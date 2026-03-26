# Network Incident/Alert Data Structure Analysis

## 1. INCIDENT DATA STRUCTURE

### Database Model (NetworkIncident)
**Location:** [src/backend/app/production_models.py](src/backend/app/production_models.py)

```python
class NetworkIncident(Base):
    __tablename__ = 'network_incidents'
    
    id = Column(Integer, primary_key=True)
    ticket_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    severity = Column(String(10), nullable=False)  # P1, P2, P3, P4
    status = Column(String(20), default='OPEN')  # OPEN, IN_PROGRESS, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)
    symptom_summary = Column(Text)
    root_cause = Column(Text)
    resolution_steps = Column(JSON)  # List of resolution steps
    alerts_triggered = Column(JSON)  # List of related alerts
    related_tickets = Column(JSON)  # List of related ticket IDs
    
    # Many-to-many relationship with devices
    devices = relationship('NetworkDevice', secondary=incident_devices, back_populates='incidents')
```

### JSON Response Format
Incidents are returned with these fields:
```json
{
    "ticket_id": "INC-001",
    "title": "High CPU Usage on Router-A",
    "severity": "P1",
    "status": "OPEN",
    "created_at": "2026-03-26T10:30:00",
    "description": "Router-A experiencing sustained 95% CPU",
    "symptom_summary": "Device unresponsive, packet loss detected",
    "time_open": "02:15:30"
}
```

---

## 2. INCIDENT FIELDS & ATTRIBUTES

### Core Fields
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `ticket_id` | String | Unique incident identifier | INC-001, INC-12345 |
| `title` | String(200) | Brief incident description | "High CPU Usage on Router-A" |
| `description` | Text | Detailed incident information | Full narrative description |
| `severity` | String | Priority level | P1 (Critical), P2, P3, P4 |
| `status` | String | Current state | OPEN, IN_PROGRESS, RESOLVED |

### Timestamp Fields
| Field | Type | Purpose |
|-------|------|---------|
| `created_at` | DateTime | When incident was opened |
| `resolved_at` | DateTime | When incident was closed (NULL if still open) |

### Analysis & Resolution Fields
| Field | Type | Description |
|-------|------|-------------|
| `symptom_summary` | Text | Initial symptoms observed |
| `root_cause` | Text | Identified root cause analysis |
| `resolution_steps` | JSON Array | List of steps taken to resolve |
| `alerts_triggered` | JSON Array | Related alert IDs that triggered |
| `related_tickets` | JSON Array | IDs of related incidents |

### Relationships
- **Affected Devices**: Many-to-many relationship with `NetworkDevice`
  - Indicates which network devices are affected
  - Example: incident may affect multiple routers, switches, firewalls

---

## 3. FRONTEND INCIDENT DISPLAY

### Dashboard HTML Structure
**Location:** [src/frontend/dashboard.html](src/frontend/dashboard.html)

#### Recent Incidents Table (Dashboard View)
```html
<!-- Stats Cards Section -->
<div class="stat-card">
    <div class="stat-label">Open Incidents</div>
    <div class="stat-value" id="open-incidents">0</div>
    <div class="stat-change negative" id="critical-incidents">0 critical</div>
</div>

<!-- Incidents Table -->
<div class="table-section">
    <div class="table-header">Recent Incidents</div>
    <table id="incidentsTable">
        <thead>
            <tr>
                <th>Ticket ID</th>
                <th>Title</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Created</th>
            </tr>
        </thead>
        <tbody></tbody>
    </table>
</div>
```

#### Incident Timeline Chart
```javascript
// Chart.js visualization
const chart = new Chart(document.getElementById('incidentChart'), {
    type: 'line',
    data: {
        labels: incidentDates,
        datasets: [{
            label: 'Open Incidents',
            data: incidentCounts,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)'
        }]
    }
});
```

#### All Incidents Page
```html
<div id="incidents" class="page">
    <table id="allIncidentsTable">
        <thead>
            <tr>
                <th>Ticket ID</th>
                <th>Title</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Affected Devices</th>
            </tr>
        </thead>
        <tbody></tbody>
    </table>
</div>
```

#### Severity Badge Styling
```css
.badge-p1 {
    background: rgba(239, 68, 68, 0.1);  /* Red for Critical */
    color: var(--danger);  /* #ef4444 */
}

.badge-p2 {
    background: rgba(234, 179, 8, 0.1);  /* Orange for High */
    color: var(--warning);  /* #eab308 */
}
```

#### Status Indicator Colors
```javascript
const statusColors = {
    'OPEN': '#ef4444',        // Red
    'IN_PROGRESS': '#f59e0b', // Orange
    'RESOLVED': '#22c55e'     // Green
};
```

### JavaScript Display Functions
The frontend dynamically populates tables by calling API endpoints:
```javascript
// Fetch and display incidents
async function loadIncidents() {
    const response = await axios.get('/api/incidents');
    const incidents = response.data.incidents;
    
    incidents.forEach(incident => {
        // Create table row with incident details
        const row = `
            <tr onclick="showIncidentModal('${incident.ticket_id}')">
                <td><strong>${incident.ticket_id}</strong></td>
                <td>${incident.title}</td>
                <td><span class="badge badge-${incident.severity.toLowerCase()}">
                    ${incident.severity}</span></td>
                <td><span class="status-badge">${incident.status}</span></td>
                <td>${formatDate(incident.created_at)}</td>
            </tr>
        `;
        table.appendChild(row);
    });
}
```

---

## 4. ANALYTICS & ALERTING SERVICES DATA COLLECTION

### Alerting Service
**Location:** [src/backend/utils/alerting_service.py](src/backend/utils/alerting_service.py)

#### Alert Data Structure
```python
alert_data = {
    'title': 'Critical Alert',
    'message': 'CPU usage exceeded threshold',
    'severity': 'critical',  # 'critical', 'warning', 'info'
    'device_id': 'Router-A',
    'metric_name': 'cpu_usage',
    'metric_value': 95.5,
    'unit': '%',
    'alert_id': 'ALR-001',
    'timestamp': '2026-03-26T10:30:00'
}
```

#### Alert Handlers (Multi-Channel)
Supported notification channels:
- **Slack**: Color-coded attachments with fields
- **Email**: HTML formatted messages via SendGrid
- **PagerDuty**: Event-based incident creation
- **Microsoft Teams**: MessageCard format

#### Alert Escalation Policies
```python
ESCALATION_POLICIES = {
    'critical': {
        'handlers': ['pagerduty', 'slack', 'email'],
        'wait_before_next_level': 15  # minutes
    },
    'warning': {
        'handlers': ['slack', 'email'],
        'wait_before_next_level': 30
    },
    'info': {
        'handlers': ['slack'],
        'wait_before_next_level': 60
    }
}
```

### Analytics Service
**Location:** [src/backend/utils/analytics_service.py](src/backend/utils/analytics_service.py)

#### Data Collected & Analyzed

1. **Trend Analysis**
   - Linear regression slope calculation
   - Direction: increasing, decreasing, stable
   - Data points examined: 7-30 days typical

2. **Anomaly Detection**
   - Z-score analysis (2-sigma threshold)
   - Isolation Forest algorithm (ML-powered)
   - Standard deviation-based outliers

3. **Capacity Forecasting**
   - Predict when metrics exceed threshold
   - Days until capacity breach
   - Confidence levels

4. **Baseline Calculation**
   ```python
   baseline = {
       'baseline_min': min_value,
       'baseline_max': max_value,
       'baseline_mean': average_value,
       'baseline_stdev': standard_deviation
   }
   ```

5. **Deviation Detection**
   - Compare current value vs baseline
   - Percentage deviation calculation
   - Anomaly flag based on 2-sigma threshold

6. **Metric Correlation**
   - Identify correlated metrics (Pearson coefficient > 0.7)
   - Shows which metrics move together
   - Example: CPU load correlated with Memory usage

7. **Health Score Calculation**
   ```
   Score = 100
   Score -= (critical_count × 20)  # -20 per critical
   Score -= (warning_count × 5)    # -5 per warning
   Range: 0-100 (higher = healthier)
   ```

8. **MTTR (Mean Time To Recovery)**
   - Average time from incident creation to resolution
   - Calculated from resolved incidents only
   - Unit: hours and minutes

9. **Availability Percentage**
   - Formula: (uptime_hours / total_hours) × 100
   - Calculated from incident downtime records

---

## 5. BACKEND API ENDPOINTS FOR ALERTS/INCIDENTS

### Core Incident Endpoints

#### List All Incidents
```
GET /api/incidents
Query Parameters:
  - status: OPEN, IN_PROGRESS, RESOLVED
  - severity: P1, P2, P3, P4
  
Response:
{
    "count": 5,
    "incidents": [
        {
            "ticket_id": "INC-001",
            "title": "High CPU Usage",
            "severity": "P1",
            "status": "OPEN",
            "created_at": "2026-03-26T10:30:00"
        }
    ]
}
```

#### Get Incident Details
```
GET /api/incidents/{ticket_id}

Response:
{
    "ticket_id": "INC-001",
    "title": "High CPU Usage on Router-A",
    "severity": "P1",
    "status": "OPEN",
    "description": "Router-A experiencing sustained 95% CPU usage",
    "symptom_summary": "Device unresponsive, packet loss detected",
    "root_cause": "BGP update loop causing CPU spike",
    "affected_devices": [
        {
            "device_id": "Router-A",
            "device_name": "Core Router 1",
            "status": "DEGRADED"
        }
    ],
    "time_open": "02:15:30",
    "alerts_triggered": [
        "ALR-CPU-001",
        "ALR-LATENCY-002"
    ]
}
```

#### Get AI-Powered Incident Analysis
```
GET /api/incidents/{ticket_id}/analysis

Response:
{
    "ticket_id": "INC-001",
    "title": "High CPU Usage on Router-A",
    "root_cause": "BGP update loop detected",
    "affected_devices": ["Router-A", "Switch-B"],
    "recent_alerts": [
        {
            "device": "Router-A",
            "metric": "cpu_usage",
            "value": 95.5,
            "status": "CRITICAL"
        }
    ],
    "recommended_actions": [
        "Check device CPU and memory usage",
        "Verify network connectivity",
        "Review recent configuration changes",
        "Check system logs for errors"
    ],
    "estimated_resolution_time": "30-60 minutes"
}
```

### Analytics Endpoints

#### Anomaly Detection
```
GET /api/analytics/anomalies
Query Parameters:
  - device_id: specific device
  - metric_name: cpu_usage, memory, etc.
  - hours: lookback period (default: 24)

Response:
{
    "metric_name": "cpu_usage",
    "period_hours": 24,
    "total_points": 288,
    "anomalies_detected": 5,
    "anomaly_percentage": 1.74,
    "anomalies": [
        {
            "device": "Router-A",
            "metric": "cpu_usage",
            "value": 92.3,
            "timestamp": "2026-03-26T14:32:00",
            "z_score": 3.2
        }
    ]
}
```

#### Trend Analysis
```
GET /api/analytics/trends
Query Parameters:
  - device_id: optional device filter
  - metric_name: metric to analyze
  - days: lookback period (default: 7)

Response:
{
    "metric": "cpu_usage",
    "period_days": 7,
    "data_points": 168,
    "trend": {
        "direction": "increasing",
        "slope": 0.3456,
        "current_value": 75.2,
        "average": 68.5
    },
    "baseline": {
        "min": 45.0,
        "max": 80.0,
        "mean": 65.5,
        "std_dev": 8.2
    },
    "health_status": "normal"
}
```

#### Forecasting
```
GET /api/analytics/forecast
Query Parameters:
  - device_id: device to forecast
  - metric_name: metric name
  - forecast_days: days ahead (default: 7)
  - threshold: alert threshold (default: 90)

Response:
{
    "device_id": "Router-A",
    "metric": "cpu_usage",
    "forecast_days": 7,
    "threshold": 90,
    "forecast": [72.1, 74.5, 76.8, 78.2, 79.5, 80.1, 81.3],
    "risk_assessment": {
        "failure_risk": "moderate",
        "days_until_failure": 3.5,
        "recommendation": "Upgrade capacity within 3 days"
    }
}
```

### Metrics Endpoints

#### Get Critical Metrics
```
GET /api/metrics/critical
Query Parameters:
  - hours: lookback period (default: 24)

Response:
{
    "count": 12,
    "period_hours": 24,
    "metrics": [
        {
            "device": "Router-A",
            "metric": "cpu_usage",
            "value": 95.5,
            "unit": "%",
            "timestamp": "2026-03-26T14:32:00"
        }
    ]
}
```

#### Get Metrics with Filtering
```
GET /api/metrics
Query Parameters:
  - device_id: filter by device
  - metric_name: filter by metric type
  - hours: lookback period (default: 240)
  - status: OK, WARNING, CRITICAL
  - limit: max results (default: 1000)

Response:
{
    "count": 500,
    "period_hours": 240,
    "metrics": [
        {
            "device_id": "Router-A",
            "device_name": "Core Router 1",
            "metric_name": "cpu_usage",
            "metric_value": 75.5,
            "unit": "%",
            "status": "OK",
            "threshold_warn": 80,
            "threshold_crit": 90,
            "timestamp": "2026-03-26T14:32:00"
        }
    ]
}
```

#### Get Metrics Statistics
```
GET /api/metrics/statistics
Query Parameters:
  - hours: lookback period (default: 24)

Response:
{
    "period_hours": 24,
    "total_metrics": 1200,
    "status_distribution": {
        "ok": 1100,
        "warning": 75,
        "critical": 25
    }
}
```

### Health & Status Endpoint

#### Network Health Overview
```
GET /api/health

Response:
{
    "status": "degraded",
    "health_percentage": 75.5,
    "devices": {
        "total": 20,
        "healthy": 15,
        "unhealthy": 5
    },
    "incidents": {
        "open": 3,
        "critical": 1
    },
    "metrics": {
        "critical_alerts": 8
    },
    "timestamp": "2026-03-26T14:32:00"
}
```

---

## 6. DATA FLOW SUMMARY

```
Network Events
    ↓
[Metrics Collection] → NetworkMetric table
    ↓
[Alert Rules Evaluation] → Threshold breaches detected
    ↓
[Alert Triggers] → Webhook notifications (Slack/Email/PagerDuty/Teams)
    ↓
[Incident Creation] → NetworkIncident table
    ↓
[ML Analytics Service]
    ├─ Anomaly Detection (Z-score, Isolation Forest)
    ├─ Trend Analysis (Linear regression)
    ├─ Forecasting (Capacity prediction)
    ├─ Correlation Analysis
    └─ Health Score Calculation
    ↓
[Frontend Display]
    ├─ Dashboard Stats & Charts
    ├─ Incident Tables
    ├─ Analytics Visualizations
    └─ Real-time Status Indicators
    ↓
[Reporting & MTTR Tracking]
    ├─ PDF Reports
    ├─ Availability Calculations
    └─ Resolution Metrics
```

---

## 7. KEY METRICS MONITORED

- CPU Usage (%)
- Memory Usage (%)
- Disk Usage (%)
- Network Bandwidth (bps)
- Latency (ms)
- Packet Loss (%)
- Device Status (UP, DOWN, DEGRADED, ERROR)
- Interface Status
- Temperature (°C)
- Power Consumption (W)

---

## 8. SEVERITY LEVELS

| Level | Priority | Response Time | Escalation |
|-------|----------|----------------|-----------|
| P1 | Critical | <15 min | PagerDuty + Slack + Email |
| P2 | High | <60 min | Slack + Email |
| P3 | Medium | <4 hours | Slack |
| P4 | Low | <24 hours | Slack only |

