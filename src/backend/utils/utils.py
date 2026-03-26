"""
Utility functions for network troubleshooting assistant
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json


class DateTimeUtils:
    """Utilities for timestamp and time-based calculations"""
    
    @staticmethod
    def parse_iso_timestamp(timestamp: str) -> datetime:
        """Parse ISO 8601 timestamp"""
        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    @staticmethod
    def format_iso_timestamp(dt: datetime) -> str:
        """Format datetime to ISO 8601"""
        return dt.isoformat() + 'Z'
    
    @staticmethod
    def get_time_diff_minutes(start: str, end: str) -> float:
        """Calculate time difference in minutes between two ISO timestamps"""
        start_dt = DateTimeUtils.parse_iso_timestamp(start)
        end_dt = DateTimeUtils.parse_iso_timestamp(end)
        diff = end_dt - start_dt
        return diff.total_seconds() / 60
    
    @staticmethod
    def is_within_timeframe(timestamp: str, hours: int) -> bool:
        """Check if timestamp is within the last N hours"""
        ts = DateTimeUtils.parse_iso_timestamp(timestamp)
        now = datetime.now(ts.tzinfo) if ts.tzinfo else datetime.now()
        diff = now - ts
        return diff < timedelta(hours=hours)


class AlertCorrelation:
    """Correlates multiple alerts to identify root causes"""
    
    ALERT_SEVERITY_MAP = {
        "CPU_HIGH_THRESHOLD_BREACH": 85,
        "MEMORY_LOW_WARNING": 80,
        "INTERFACE_DOWN": 90,
        "BGP_SESSION_DROP": 85,
        "PACKET_LOSS_HIGH": 75,
        "DEVICE_UNREACHABLE": 95,
        "POWER_SUPPLY_FAILURE": 95,
        "TEMPERATURE_CRITICAL": 90,
        "ROUTE_FLAPPING": 70,
        "NTP_SYNC_LOST": 60
    }
    
    @staticmethod
    def get_alert_severity(alert_type: str) -> int:
        """Get severity score for an alert type (0-100)"""
        return AlertCorrelation.ALERT_SEVERITY_MAP.get(alert_type, 50)
    
    @staticmethod
    def correlate_alerts(alerts: List[str]) -> Dict:
        """Correlate multiple alerts to find patterns"""
        if not alerts:
            return {}
        
        correlation = {
            "total_alerts": len(alerts),
            "avg_severity": sum(AlertCorrelation.get_alert_severity(a) for a in alerts) / len(alerts),
            "critical_alerts": [a for a in alerts if AlertCorrelation.get_alert_severity(a) >= 90],
            "alert_categories": AlertCorrelation._categorize_alerts(alerts),
            "likely_root_cause": AlertCorrelation._determine_root_cause(alerts)
        }
        return correlation
    
    @staticmethod
    def _categorize_alerts(alerts: List[str]) -> Dict[str, List]:
        """Categorize alerts by type"""
        categories = {
            "performance": [],
            "availability": [],
            "connectivity": [],
            "configuration": []
        }
        
        for alert in alerts:
            if "CPU" in alert or "MEMORY" in alert or "TEMPERATURE" in alert:
                categories["performance"].append(alert)
            elif "DOWN" in alert or "UNREACHABLE" in alert:
                categories["availability"].append(alert)
            elif "BGP" in alert or "OSPF" in alert or "ROUTE" in alert:
                categories["connectivity"].append(alert)
            else:
                categories["configuration"].append(alert)
        
        return {k: v for k, v in categories.items() if v}
    
    @staticmethod
    def _determine_root_cause(alerts: List[str]) -> str:
        """Determine likely root cause from alert pattern"""
        if any("CPU" in a or "MEMORY" in a for a in alerts):
            return "Resource exhaustion (CPU/Memory)"
        elif any("INTERFACE_DOWN" in a or "PACKET_LOSS" in a for a in alerts):
            return "Physical link failure or degradation"
        elif any("BGP" in a or "OSPF" in a or "ROUTE" in a for a in alerts):
            return "Routing protocol instability"
        elif any("DOWN" in a or "UNREACHABLE" in a for a in alerts):
            return "Device or service availability issue"
        else:
            return "Configuration or operational issue"


class NetworkAnalytics:
    """Analyzes network health trends and patterns"""
    
    @staticmethod
    def calculate_mttr(incidents: List[Dict]) -> Dict[str, float]:
        """Calculate Mean Time To Resolution for different severity levels"""
        mttr_data = {}
        
        for severity in ["P1", "P2", "P3", "P4"]:
            matching_incidents = [i for i in incidents if i.get("severity") == severity]
            if matching_incidents:
                resolution_times = []
                for incident in matching_incidents:
                    if incident.get("resolved_at") and incident.get("created_at"):
                        time_minutes = DateTimeUtils.get_time_diff_minutes(
                            incident["created_at"],
                            incident["resolved_at"]
                        )
                        resolution_times.append(time_minutes)
                
                if resolution_times:
                    mttr_data[severity] = sum(resolution_times) / len(resolution_times)
        
        return mttr_data
    
    @staticmethod
    def identify_problem_devices(devices: List[Dict], incidents: List[Dict]) -> List[Dict]:
        """Identify devices involved in recurring issues"""
        device_incident_count = {}
        
        for incident in incidents:
            for device_id in incident.get("affected_devices", []):
                device_incident_count[device_id] = device_incident_count.get(device_id, 0) + 1
        
        problem_devices = [
            {
                "device_id": device_id,
                "incident_count": count,
                "severity": "HIGH" if count >= 3 else "MEDIUM" if count >= 2 else "LOW"
            }
            for device_id, count in sorted(device_incident_count.items(), 
                                          key=lambda x: x[1], reverse=True)
        ]
        
        return problem_devices
    
    @staticmethod
    def calculate_network_availability(devices: List[Dict]) -> float:
        """Calculate overall network availability percentage"""
        if not devices:
            return 0.0
        
        available = sum(1 for d in devices if d.get("status") in ["UP", "DEGRADED"])
        return (available / len(devices)) * 100


class ReportGenerator:
    """Generates formatted reports"""
    
    @staticmethod
    def generate_json_report(data: Dict) -> str:
        """Generate JSON formatted report"""
        return json.dumps(data, indent=2, default=str)
    
    @staticmethod
    def generate_text_report(title: str, sections: Dict[str, List[str]]) -> str:
        """Generate text formatted report"""
        report = f"\n{'='*60}\n{title}\n{'='*60}\n"
        
        for section_title, items in sections.items():
            report += f"\n{section_title}:\n{'-'*40}\n"
            for item in items:
                report += f"  • {item}\n"
        
        return report
    
    @staticmethod
    def generate_summary_table(headers: List[str], rows: List[List]) -> str:
        """Generate simple ASCII table"""
        col_widths = [max(len(str(h)), 
                         max((len(str(row[i])) for row in rows), default=0))
                     for i, h in enumerate(headers)]
        
        # Header
        table = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + "\n"
        table += "-" * (sum(col_widths) + len(headers) * 3 - 1) + "\n"
        
        # Rows
        for row in rows:
            table += " | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)) + "\n"
        
        return table


class ValidationUtils:
    """Data validation utilities"""
    
    @staticmethod
    def validate_device_data(device: Dict) -> Tuple[bool, List[str]]:
        """Validate device data completeness"""
        required_fields = ['device_id', 'device_name', 'ip_address', 'status']
        errors = [f"Missing field: {field}" for field in required_fields 
                 if field not in device]
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_incident_data(incident: Dict) -> Tuple[bool, List[str]]:
        """Validate incident data completeness"""
        required_fields = ['ticket_id', 'title', 'severity', 'affected_devices']
        errors = [f"Missing field: {field}" for field in required_fields 
                 if field not in incident]
        
        if incident.get('severity') not in ['P1', 'P2', 'P3', 'P4']:
            errors.append(f"Invalid severity: {incident.get('severity')}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_metric_data(metric: Dict) -> Tuple[bool, List[str]]:
        """Validate metric data"""
        required_fields = ['device_id', 'metric_name', 'metric_value']
        errors = [f"Missing field: {field}" for field in required_fields 
                 if field not in metric]
        
        try:
            float(metric.get('metric_value', 0))
        except (ValueError, TypeError):
            errors.append(f"Invalid metric value: {metric.get('metric_value')}")
        
        return len(errors) == 0, errors
