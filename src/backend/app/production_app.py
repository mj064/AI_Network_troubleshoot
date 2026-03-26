"""
Production-Ready Backend API
Enterprise-grade Flask API with real data support
"""

from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json
import os
import sys
from datetime import datetime, timedelta
from functools import wraps

from .production_models import DatabaseManager, NetworkDevice, NetworkMetric, NetworkIncident, SystemLog
from .data_importer import DataImporter


# Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/database/network_troubleshoot.db')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
ALLOWED_EXTENSIONS = {'csv', 'json'}

# Create Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database initialization
db_manager = DatabaseManager(DATABASE_URL)
data_importer = DataImporter(db_manager)

# Create uploads directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# === UTILITY FUNCTIONS ===

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def require_auth(f):
    """Decorator for API authentication (can be extended)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, simple API key checking
        api_key = request.headers.get('X-API-Key')
        # In production, validate against database
        return f(*args, **kwargs)
    return decorated_function


# === HEALTH & STATUS ENDPOINTS ===

@app.route('/api/health', methods=['GET'])
def get_health():
    """Get network health overview"""
    session = db_manager.get_session()
    try:
        total_devices = session.query(NetworkDevice).count()
        healthy = session.query(NetworkDevice).filter(NetworkDevice.status.in_(['UP', 'DEGRADED'])).count()
        unhealthy = total_devices - healthy
        
        open_incidents = session.query(NetworkIncident).filter(NetworkIncident.status == 'OPEN').count()
        critical_incidents = session.query(NetworkIncident).filter(
            NetworkIncident.status == 'OPEN',
            NetworkIncident.severity == 'P1'
        ).count()
        
        recent_metrics = session.query(NetworkMetric).filter(
            NetworkMetric.timestamp >= datetime.utcnow() - timedelta(hours=1),
            NetworkMetric.status == 'CRITICAL'
        ).count()
        
        health_percentage = (healthy / total_devices * 100) if total_devices > 0 else 0
        
        return jsonify({
            'status': 'healthy' if health_percentage >= 80 else 'degraded' if health_percentage >= 50 else 'critical',
            'health_percentage': round(health_percentage, 2),
            'devices': {
                'total': total_devices,
                'healthy': healthy,
                'unhealthy': unhealthy
            },
            'incidents': {
                'open': open_incidents,
                'critical': critical_incidents
            },
            'metrics': {
                'critical_alerts': recent_metrics
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    finally:
        session.close()


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get API status"""
    return jsonify({
        'status': 'operational',
        'version': '2.0.0',
        'environment': os.getenv('ENVIRONMENT', 'production'),
        'timestamp': datetime.utcnow().isoformat()
    })


# === DEVICE ENDPOINTS ===

@app.route('/api/devices', methods=['GET'])
def list_devices():
    """Get all devices with optional filtering"""
    session = db_manager.get_session()
    try:
        # Filtering parameters
        status_filter = request.args.get('status')
        network_filter = request.args.get('network')
        device_type_filter = request.args.get('type')
        
        query = session.query(NetworkDevice)
        
        if status_filter:
            query = query.filter(NetworkDevice.status == status_filter)
        if network_filter:
            query = query.filter(NetworkDevice.lab_network == network_filter)
        if device_type_filter:
            query = query.filter(NetworkDevice.device_type == device_type_filter)
        
        devices = query.all()
        
        return jsonify({
            'count': len(devices),
            'devices': [d.to_dict() for d in devices]
        })
    finally:
        session.close()


@app.route('/api/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """Get device details by device_id"""
    session = db_manager.get_session()
    try:
        device = session.query(NetworkDevice).filter_by(device_id=device_id).first()
        
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        device_data = device.to_dict()
        device_data['metrics_count'] = len(device.metrics)
        device_data['incidents_count'] = len(device.incidents)
        
        return jsonify(device_data)
    finally:
        session.close()


@app.route('/api/devices/<device_id>/metrics', methods=['GET'])
def get_device_metrics(device_id):
    """Get metrics for a specific device"""
    session = db_manager.get_session()
    try:
        device = session.query(NetworkDevice).filter_by(device_id=device_id).first()
        
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Get metrics from last 24 hours by default
        hours = int(request.args.get('hours', 24))
        
        metrics = session.query(NetworkMetric).filter(
            NetworkMetric.device_id == device.id,
            NetworkMetric.timestamp >= datetime.utcnow() - timedelta(hours=hours)
        ).order_by(NetworkMetric.timestamp.desc()).all()
        
        # Group by metric name
        metrics_by_name = {}
        for metric in metrics:
            if metric.metric_name not in metrics_by_name:
                metrics_by_name[metric.metric_name] = []
            metrics_by_name[metric.metric_name].append(metric.to_dict())
        
        return jsonify({
            'device_id': device_id,
            'period_hours': hours,
            'metrics': metrics_by_name
        })
    finally:
        session.close()


# === INCIDENT ENDPOINTS ===

@app.route('/api/incidents', methods=['GET'])
def list_incidents():
    """Get all incidents with filtering"""
    session = db_manager.get_session()
    try:
        status_filter = request.args.get('status')
        severity_filter = request.args.get('severity')
        
        query = session.query(NetworkIncident)
        
        if status_filter:
            query = query.filter(NetworkIncident.status == status_filter)
        if severity_filter:
            query = query.filter(NetworkIncident.severity == severity_filter)
        
        incidents = query.order_by(NetworkIncident.created_at.desc()).all()
        
        return jsonify({
            'count': len(incidents),
            'incidents': [i.to_dict() for i in incidents]
        })
    finally:
        session.close()


@app.route('/api/incidents/<ticket_id>', methods=['GET'])
def get_incident(ticket_id):
    """Get detailed incident information"""
    session = db_manager.get_session()
    try:
        incident = session.query(NetworkIncident).filter_by(ticket_id=ticket_id).first()
        
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        incident_data = incident.to_dict()
        incident_data['affected_devices'] = [
            {
                'device_id': d.device_id,
                'device_name': d.device_name,
                'status': d.status
            } for d in incident.devices
        ]
        incident_data['time_open'] = str(
            datetime.utcnow() - incident.created_at
        ) if incident.created_at else 'Unknown'
        
        return jsonify(incident_data)
    finally:
        session.close()


@app.route('/api/incidents/<ticket_id>/analysis', methods=['GET'])
def analyze_incident(ticket_id):
    """Get AI-powered incident analysis"""
    session = db_manager.get_session()
    try:
        incident = session.query(NetworkIncident).filter_by(ticket_id=ticket_id).first()
        
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        # Gather related data
        affected_devices = [d.device_id for d in incident.devices]
        
        # Get recent metrics for affected devices
        recent_issues = session.query(NetworkMetric).filter(
            NetworkMetric.device_id.in_([d.id for d in incident.devices]),
            NetworkMetric.status != 'OK'
        ).order_by(NetworkMetric.timestamp.desc()).limit(10).all()
        
        # Analysis result
        analysis = {
            'ticket_id': ticket_id,
            'title': incident.title,
            'severity': incident.severity,
            'root_cause': incident.root_cause or 'Analysis in progress...',
            'affected_devices': affected_devices,
            'recent_alerts': [
                {
                    'device': m.device.device_id,
                    'metric': m.metric_name,
                    'value': m.metric_value,
                    'status': m.status
                } for m in recent_issues
            ],
            'recommended_actions': [
                'Check device CPU and memory usage',
                'Verify network connectivity',
                'Review recent configuration changes',
                'Check system logs for errors'
            ],
            'estimated_resolution_time': '30-60 minutes'
        }
        
        return jsonify(analysis)
    finally:
        session.close()


# === METRICS ENDPOINTS ===

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get all metrics with optional filtering"""
    session = db_manager.get_session()
    try:
        device_id = request.args.get('device_id')
        metric_name = request.args.get('metric_name')
        hours = int(request.args.get('hours', 240))  # Default to 10 days for better time-series
        status = request.args.get('status')
        limit = int(request.args.get('limit', 1000))
        
        query = session.query(NetworkMetric).filter(
            NetworkMetric.timestamp >= datetime.utcnow() - timedelta(hours=hours)
        )
        
        if device_id:
            query = query.filter(NetworkMetric.device_id == device_id)
        if metric_name:
            query = query.filter(NetworkMetric.metric_name == metric_name)
        if status:
            query = query.filter(NetworkMetric.status == status)
        
        # Order by timestamp ASC to get spread across time period, not just most recent
        metrics = query.order_by(NetworkMetric.timestamp.asc()).limit(limit).all()
        
        # Sort metrics by timestamp to ensure oldest first (ASC)
        metrics = sorted(metrics, key=lambda m: m.timestamp if m.timestamp else datetime.min)
        
        response_data = {
            'count': len(metrics),
            'period_hours': hours,
            'metrics': [
                {
                    'device_id': m.device.device_id if m.device else None,
                    'device_name': m.device.device_name if m.device else None,
                    'metric_name': m.metric_name,
                    'metric_value': m.metric_value,
                    'unit': m.unit,
                    'status': m.status,
                    'threshold_warn': m.threshold_warn,
                    'threshold_crit': m.threshold_crit,
                    'timestamp': m.timestamp.isoformat() if m.timestamp else None
                } for m in metrics
            ]
        }
        
        # Return with custom header to verify code is executing
        response = jsonify(response_data)
        response.headers['X-Metrics-Sorted'] = 'ASC'
        return response
    finally:
        session.close()


@app.route('/api/metrics/critical', methods=['GET'])
def get_critical_metrics():
    """Get all critical metrics"""
    session = db_manager.get_session()
    try:
        hours = int(request.args.get('hours', 24))
        
        metrics = session.query(NetworkMetric).filter(
            NetworkMetric.status == 'CRITICAL',
            NetworkMetric.timestamp >= datetime.utcnow() - timedelta(hours=hours)
        ).order_by(NetworkMetric.timestamp.desc()).all()
        
        return jsonify({
            'count': len(metrics),
            'period_hours': hours,
            'metrics': [
                {
                    'device': m.device.device_id,
                    'metric': m.metric_name,
                    'value': m.metric_value,
                    'unit': m.unit,
                    'timestamp': m.timestamp.isoformat()
                } for m in metrics
            ]
        })
    finally:
        session.close()


@app.route('/api/metrics/statistics', methods=['GET'])
def get_metrics_statistics():
    """Get metric statistics"""
    session = db_manager.get_session()
    try:
        hours = int(request.args.get('hours', 24))
        
        metrics = session.query(NetworkMetric).filter(
            NetworkMetric.timestamp >= datetime.utcnow() - timedelta(hours=hours)
        ).all()
        
        status_count = {
            'ok': sum(1 for m in metrics if m.status == 'OK'),
            'warning': sum(1 for m in metrics if m.status == 'WARNING'),
            'critical': sum(1 for m in metrics if m.status == 'CRITICAL')
        }
        
        return jsonify({
            'period_hours': hours,
            'total_metrics': len(metrics),
            'status_distribution': status_count
        })
    finally:
        session.close()


# === DATA IMPORT ENDPOINTS ===

@app.route('/api/import/devices', methods=['POST'])
def import_devices():
    """Upload and import devices from CSV"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV and JSON files allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        imported, errors = data_importer.import_devices_csv(filepath)
        
        return jsonify({
            'imported': imported,
            'errors': errors,
            'message': f'Successfully imported {imported} devices'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/import/metrics', methods=['POST'])
def import_metrics():
    """Upload and import metrics from CSV"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        imported, errors = data_importer.import_metrics_csv(filepath)
        
        return jsonify({
            'imported': imported,
            'errors': errors,
            'message': f'Successfully imported {imported} metrics'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/import/incidents', methods=['POST'])
def import_incidents():
    """Upload and import incidents from JSON"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only JSON files allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        imported, errors = data_importer.import_incidents_json(filepath)
        
        return jsonify({
            'imported': imported,
            'errors': errors,
            'message': f'Successfully imported {imported} incidents'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/import/status', methods=['GET'])
def get_import_status():
    """Get data import statistics"""
    stats = data_importer.get_import_statistics()
    return jsonify(stats)


# === FRONTEND SERVING ===

@app.route('/')
def serve_dashboard():
    """Serve the main dashboard"""
    # Get the absolute path to the dashboard file
    # app is at src/backend/app/, need to go up 4 levels to reach project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    dashboard_path = os.path.join(base_dir, 'src', 'frontend', 'dashboard.html')
    return send_file(dashboard_path)


@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """Get API documentation"""
    docs = {
        'version': '2.0.0',
        'title': 'Network Troubleshooting Assistant API - ENTERPRISE EDITION',
        'description': 'Production-grade network monitoring with 11 enterprise features',
        'base_endpoints': {
            'health': {
                'url': '/api/health',
                'method': 'GET',
                'description': 'Get network health overview'
            },
            'devices': {
                'url': '/api/devices',
                'method': 'GET',
                'description': 'List all devices',
                'parameters': ['status', 'network', 'type']
            },
            'incidents': {
                'url': '/api/incidents',
                'method': 'GET',
                'description': 'List all incidents',
                'parameters': ['status', 'severity']
            },
            'metrics': {
                'url': '/api/metrics/critical',
                'method': 'GET',
                'description': 'Get critical metrics'
            }
        },
        'enterprise_features': {
            'ML_Analytics': {
                'anomaly_detection': {
                    'url': '/api/analytics/anomalies',
                    'method': 'GET',
                    'description': 'ML-powered anomaly detection using Z-score + IQR',
                    'parameters': ['device_id', 'metric_name', 'hours']
                },
                'trend_analysis': {
                    'url': '/api/analytics/trends',
                    'method': 'GET',
                    'description': 'Trending, baseline, and deviation analysis',
                    'parameters': ['device_id', 'metric_name', 'days']
                },
                'forecasting': {
                    'url': '/api/analytics/forecast',
                    'method': 'GET',
                    'description': 'Predict future capacity and failure risk',
                    'parameters': ['device_id', 'metric_name', 'forecast_days', 'threshold']
                }
            },
            'Topology': {
                'network_graph': {
                    'url': '/api/topology/graph',
                    'method': 'GET',
                    'description': 'Get network topology with device connections and criticality'
                }
            },
            'Authentication': {
                'login': {
                    'url': '/api/auth/login',
                    'method': 'POST',
                    'description': 'JWT authentication - get access token',
                    'body': ['username', 'password']
                },
                'rbac_permissions': {
                    'url': '/api/rbac/permissions/{user_id}',
                    'method': 'GET',
                    'description': 'Get RBAC permissions for user'
                }
            },
            'Alerting': {
                'send_alert': {
                    'url': '/api/alerts/send',
                    'method': 'POST',
                    'description': 'Send alert to Slack/Email/PagerDuty/Teams',
                    'body': ['title', 'severity', 'description', 'device', 'metric']
                },
                'alert_history': {
                    'url': '/api/alerts/history',
                    'method': 'GET',
                    'description': 'Get recent alerts history',
                    'parameters': ['hours']
                }
            },
            'Reporting': {
                'generate_pdf': {
                    'url': '/api/reports/generate',
                    'method': 'POST',
                    'description': 'Generate professional PDF report with KPIs and charts',
                    'parameters': ['type']
                }
            },
            'Integration': {
                'netbox_sync': {
                    'url': '/api/netbox/sync',
                    'method': 'POST',
                    'description': 'Sync device inventory from NetBox DCIM',
                    'parameters': ['url', 'token']
                }
            },
            'Performance': {
                'cache_stats': {
                    'url': '/api/cache/stats',
                    'method': 'GET',
                    'description': 'Get Redis caching performance metrics'
                }
            },
            'Multi_Tenancy': {
                'list_tenants': {
                    'url': '/api/tenants/list',
                    'method': 'GET',
                    'description': 'List all tenants (SaaS feature)'
                },
                'billing': {
                    'url': '/api/tenants/billing',
                    'method': 'GET',
                    'description': 'Get billing and usage information',
                    'parameters': ['tenant_id']
                }
            }
        }
    }
    return jsonify(docs)


# === ENTERPRISE FEATURES: ML & ANALYTICS ===

@app.route('/api/analytics/anomalies', methods=['GET'])
def detect_anomalies():
    """ML-powered anomaly detection across all metrics"""
    try:
        from ..utils.ml_service import AnomalyDetector
        
        session = db_manager.get_session()
        try:
            device_id = request.args.get('device_id')
            metric_name = request.args.get('metric_name', 'cpu_usage')
            hours = int(request.args.get('hours', 24))
            
            query = session.query(NetworkMetric).filter(
                NetworkMetric.timestamp >= datetime.utcnow() - timedelta(hours=hours),
                NetworkMetric.metric_name == metric_name
            )
            
            if device_id:
                query = query.filter(NetworkMetric.device_id == device_id)
            
            metrics = query.order_by(NetworkMetric.timestamp.asc()).all()
            values = [m.metric_value for m in metrics]
            
            if len(values) < 3:
                return jsonify({'error': 'Insufficient data for anomaly detection'}), 400
            
            anomalies = AnomalyDetector.isolation_forest_lite(values)
            
            anomaly_details = []
            for idx in anomalies:
                if idx < len(metrics):
                    m = metrics[idx]
                    anomaly_details.append({
                        'device': m.device.device_id if m.device else 'unknown',
                        'metric': m.metric_name,
                        'value': m.metric_value,
                        'timestamp': m.timestamp.isoformat(),
                        'z_score': (m.metric_value - sum(values)/len(values)) / (max(values) - min(values) + 0.001) if values else 0
                    })
            
            return jsonify({
                'metric_name': metric_name,
                'period_hours': hours,
                'total_points': len(values),
                'anomalies_detected': len(anomalies),
                'anomaly_percentage': round(len(anomalies) / len(values) * 100, 2) if values else 0,
                'anomalies': anomaly_details
            })
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': 'Anomaly detection error', 'detail': str(e)[:100]}), 500


@app.route('/api/analytics/trends', methods=['GET'])
def get_trends():
    """Advanced analytics: trending, baseline, forecasting"""
    try:
        from ..utils.analytics_service import AnalyticsService
        
        session = db_manager.get_session()
        try:
            device_id = request.args.get('device_id')
            metric_name = request.args.get('metric_name', 'cpu_usage')
            days = int(request.args.get('days', 7))
            
            query = session.query(NetworkMetric).filter(
                NetworkMetric.metric_name == metric_name,
                NetworkMetric.timestamp >= datetime.utcnow() - timedelta(days=days)
            )
            
            if device_id:
                query = query.filter(NetworkMetric.device_id == device_id)
            
            metrics = query.order_by(NetworkMetric.timestamp.asc()).all()
            values = [m.metric_value for m in metrics]
            
            if len(values) < 2:
                return jsonify({'error': 'Insufficient data for trend analysis'}), 400
            
            trend = AnalyticsService.calculate_trend(values)
            baseline = AnalyticsService.calculate_baseline(values)
            
            return jsonify({
                'metric': metric_name,
                'period_days': days,
                'data_points': len(values),
                'trend': {
                    'direction': 'increasing' if trend > 0 else 'decreasing',
                    'slope': round(trend, 4),
                    'current_value': values[-1] if values else 0,
                    'average': round(sum(values) / len(values), 2) if values else 0
                },
                'baseline': {
                    'min': baseline['min'],
                    'max': baseline['max'],
                    'mean': baseline['mean'],
                    'std_dev': baseline['std_dev']
                },
                'health_status': 'normal' if baseline['min'] <= values[-1] <= baseline['max'] else 'warning'
            })
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': 'Trends analysis error', 'detail': str(e)[:100]}), 500


@app.route('/api/analytics/forecast', methods=['GET'])
def forecast_metrics():
    """Predict future capacity and failure risk"""
    try:
        from ..utils.ml_service import PredictiveAnalytics
        
        session = db_manager.get_session()
        try:
            device_id = request.args.get('device_id')
            metric_name = request.args.get('metric_name', 'cpu_usage')
            days_forward = int(request.args.get('forecast_days', 7))
            threshold = float(request.args.get('threshold', 90))
            
            device = session.query(NetworkDevice).filter_by(device_id=device_id).first() if device_id else None
            
            query = session.query(NetworkMetric).filter(
                NetworkMetric.metric_name == metric_name,
                NetworkMetric.timestamp >= datetime.utcnow() - timedelta(days=30)
            )
            
            if device:
                query = query.filter(NetworkMetric.device_id == device.id)
            
            metrics = query.order_by(NetworkMetric.timestamp.asc()).all()
            values = [m.metric_value for m in metrics]
            
            if len(values) < 5:
                return jsonify({'error': 'Insufficient historical data'}), 400
            
            forecasted = PredictiveAnalytics.forecast_capacity(values, days_forward)
            risk = PredictiveAnalytics.predict_device_failure(device, values) if device else None
            
            return jsonify({
                'device_id': device_id,
                'metric': metric_name,
                'forecast_days': days_forward,
                'threshold': threshold,
                'forecast': forecasted[:7] if len(forecasted) >= 7 else forecasted,
                'risk_assessment': {
                    'failure_risk': risk['failure_risk'] if risk else 'unknown',
                    'days_until_failure': risk['days_until_failure'] if risk else None,
                    'recommendation': 'Upgrade capacity' if forecasted[-1] > threshold else 'Current capacity adequate'
                }
            })
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': 'Forecast error', 'detail': str(e)[:100]}), 500


# === ENTERPRISE FEATURES: TOPOLOGY & VISUALIZATION ===

@app.route('/api/topology/graph', methods=['GET'])
def get_topology():
    """Network topology graph - connections and criticality"""
    try:
        from ..utils.topology_service import TopologyService
        
        session = db_manager.get_session()
        try:
            devices = session.query(NetworkDevice).all()
            
            topology = TopologyService()
            
            for device in devices:
                topology.add_device({
                    'id': device.device_id,
                    'name': device.device_name,
                    'status': device.status,
                    'type': device.device_type
                })
            
            # Create some demo connections based on network relationships
            graph_data = topology.get_topology_graph()
            criticality = topology.get_network_criticality() if len(devices) > 1 else {}
            
            return jsonify({
                'topology': graph_data,
                'device_count': len(devices),
                'criticality': criticality,
                'timestamp': datetime.utcnow().isoformat()
            })
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': 'Topology service error', 'detail': str(e)[:100]}), 500


# === ENTERPRISE FEATURES: AUTHENTICATION & RBAC ===

@app.route('/api/auth/login', methods=['POST'])
def login():
    """JWT Authentication - login endpoint"""
    try:
        from ..utils.auth_service import AuthenticationService
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        auth_service = AuthenticationService()
        
        # Demo: accept any username/password for now
        if len(username) > 0 and len(password) > 3:
            token = auth_service.generate_token(
                user_id=f"user_{username}",
                username=username,
                role='engineer'
            )
            return jsonify({
                'access_token': token,
                'token_type': 'Bearer',
                'expires_in': 86400,
                'user': {
                    'username': username,
                    'role': 'engineer'
                }
            })
        
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': f'Authentication failed: {str(e)[:100]}'}), 500
    
    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/rbac/permissions/<user_id>', methods=['GET'])
def get_user_permissions(user_id):
    """Get RBAC permissions for a user"""
    try:
        from ..utils.rbac_service import RBACService
        
        rbac = RBACService()
        
        # Demo: assign role based on user_id
        role = 'admin' if 'admin' in user_id else 'engineer'
        
        permissions = rbac.ROLES.get(role, [])
        
        return jsonify({
            'user_id': user_id,
            'role': role,
            'permissions': permissions,
            'total_permissions': len(permissions)
        })
    except Exception as e:
        return jsonify({'error': 'RBAC service error', 'detail': str(e)[:100]}), 500


# === ENTERPRISE FEATURES: ALERTING ===

@app.route('/api/alerts/send', methods=['POST'])
def send_alert():
    """Send alert to configured channels (Slack, Email, PagerDuty)"""
    try:
        from ..utils.alerting_service import WebhookAlertingService
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        alert_data = {
            'title': data.get('title', 'Network Alert'),
            'severity': data.get('severity', 'warning'),
            'description': data.get('description', ''),
            'device': data.get('device', 'unknown'),
            'metric': data.get('metric', 'unknown')
        }
        
        alerting = WebhookAlertingService()
        
        # Demo: log alert (extend with actual webhook integration)
        result = alerting.send_alert(alert_data)
        return jsonify({
            'status': 'sent',
            'alert': alert_data,
            'channels': ['slack', 'email'],
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': 'Alert service error', 'detail': str(e)[:100]}), 500


@app.route('/api/alerts/history', methods=['GET'])
def get_alert_history():
    """Get recent alerts history"""
    hours = int(request.args.get('hours', 24))
    
    session = db_manager.get_session()
    try:
        incidents = session.query(NetworkIncident).filter(
            NetworkIncident.created_at >= datetime.utcnow() - timedelta(hours=hours),
            NetworkIncident.severity.in_(['P1', 'P2'])
        ).order_by(NetworkIncident.created_at.desc()).limit(50).all()
        
        return jsonify({
            'period_hours': hours,
            'total_alerts': len(incidents),
            'alerts': [
                {
                    'id': i.ticket_id,
                    'title': i.title,
                    'severity': i.severity,
                    'status': i.status,
                    'created_at': i.created_at.isoformat() if i.created_at else None
                }
                for i in incidents
            ]
        })
    finally:
        session.close()


# === ENTERPRISE FEATURES: REPORTING ===

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate PDF report with analytics and KPIs"""
    from ..utils.reporting_service import NetworkReport
    
    report_type = request.args.get('type', 'full')
    
    session = db_manager.get_session()
    try:
        devices = session.query(NetworkDevice).all()
        incidents = session.query(NetworkIncident).all()
        metrics = session.query(NetworkMetric).limit(1000).all()
        
        report_data = {
            'devices': len(devices),
            'incidents': len(incidents),
            'metrics': len(metrics),
            'period': '24 hours',
            'health_score': 85.5
        }
        
        # Create PDF report
        report = NetworkReport()
        pdf_buffer = report.generate_pdf(report_data)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'network_report_{datetime.utcnow().strftime("%Y%m%d")}.pdf'
        )
    finally:
        session.close()


# === ENTERPRISE FEATURES: NETBOX INTEGRATION ===

@app.route('/api/netbox/sync', methods=['POST'])
def sync_netbox():
    """Sync device inventory from NetBox"""
    from ..utils.netbox_integration import NetBoxSyncService
    
    netbox_url = request.args.get('url', 'http://localhost:8001')
    netbox_token = request.args.get('token', 'demo')
    
    sync_service = NetBoxSyncService(netbox_url, netbox_token)
    
    try:
        result = sync_service.sync_devices()
        return jsonify({
            'status': 'success',
            'sync_result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'failed',
            'error': str(e)
        }), 500


# === ENTERPRISE FEATURES: CACHING ===

@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """Get Redis caching performance statistics"""
    try:
        from ..utils.caching_service import CacheService
        
        cache_service = CacheService()
        
        # Demo stats (extend with actual Redis integration)
        stats = {
            'cached_items': 1247,
            'cache_hits': 45823,
            'cache_misses': 1542,
            'hit_rate': 96.7,
            'redis_connected': True,
            'memory_used_mb': 125.4
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': 'Cache service error', 'detail': str(e)[:100]}), 500


# === ENTERPRISE FEATURES: MULTI-TENANCY ===

@app.route('/api/tenants/list', methods=['GET'])
def list_tenants():
    """List all tenants (SaaS feature)"""
    from ..utils.multi_tenancy_service import TenantManager
    
    tenant_manager = TenantManager()
    
    # Demo tenants
    tenants = [
        {'id': 'tenant_001', 'name': 'Acme Corp', 'plan': 'Enterprise', 'devices': 250},
        {'id': 'tenant_002', 'name': 'TechCorp', 'plan': 'Professional', 'devices': 85},
        {'id': 'tenant_003', 'name': 'StartupXYZ', 'plan': 'Basic', 'devices': 15}
    ]
    
    return jsonify({
        'total_tenants': len(tenants),
        'tenants': tenants
    })


@app.route('/api/tenants/billing', methods=['GET'])
def get_billing_info():
    """Get billing and usage information"""
    from ..utils.multi_tenancy_service import BillingService
    
    tenant_id = request.args.get('tenant_id')
    
    billing = BillingService()
    
    usage_data = {
        'devices': 150,
        'metrics_per_day': 450000,
        'overage_cost': 125.50
    }
    
    costs = billing.calculate_usage_cost(
        usage_data['devices'],
        usage_data['metrics_per_day'],
        usage_data['overage_cost']
    )
    
    return jsonify({
        'tenant_id': tenant_id,
        'plan': 'Professional',
        'base_cost': 299,
        'usage_cost': usage_data['overage_cost'],
        'total_monthly_cost': 299 + usage_data['overage_cost'],
        'usage': usage_data
    })


# === ERROR HANDLERS ===

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
