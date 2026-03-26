# API QUICK REFERENCE
## Network Monitoring Platform

### BASE URL: http://localhost:5000/api

---

## CORE ENDPOINTS
```
GET  /api/health                    → System health overview
GET  /api/status                    → Device & incident status
GET  /api/devices                   → List all devices
GET  /api/devices/{id}              → Single device details
GET  /api/devices/{id}/metrics      → Device metrics
```

## INCIDENTS
```
GET  /api/incidents                 → List incidents
GET  /api/incidents/{id}            → Incident details
GET  /api/incidents/{id}/analysis   → AI analysis
```

## METRICS
```
GET  /api/metrics                   → All metrics
GET  /api/metrics/critical          → Critical only
GET  /api/metrics/statistics        → Aggregated stats
```

## DATA IMPORT
```
POST /api/import/devices            → Upload device CSV
POST /api/import/metrics            → Upload metrics CSV
POST /api/import/incidents          → Upload incidents JSON
GET  /api/import/status             → Import status
```

## ML ANALYTICS
```
GET  /api/analytics/anomalies       → Anomaly detection
GET  /api/analytics/trends          → Trend analysis
GET  /api/analytics/forecast        → Predictive forecast
```

## NETWORK
```
GET  /api/topology/graph            → Network topology
```

## AUTHENTICATION
```
POST /api/auth/login                → JWT login
GET  /api/rbac/permissions/{id}     → User permissions
```

## ALERTS
```
POST /api/alerts/send               → Send alert
GET  /api/alerts/history            → Alert history
```

## REPORTS
```
POST /api/reports/generate          → Generate PDF report
```

## INTEGRATIONS
```
POST /api/netbox/sync               → Sync NetBox
GET  /api/cache/stats               → Cache performance
```

## MULTI-TENANCY
```
GET  /api/tenants/list              → List tenants
GET  /api/tenants/billing           → Billing info
```

## DOCS
```
GET  /api/docs                      → API documentation
```

---

## AXIOS REQUEST EXAMPLES

### GET Request
```javascript
axios.get('/api/devices')
    .then(response => console.log(response.data))
    .catch(error => console.error(error));
```

### GET with Parameters
```javascript
axios.get('/api/analytics/anomalies', {
    params: {
        device_id: 'DEV001',
        metric_name: 'cpu_usage',
        hours: 24
    }
})
    .then(response => console.log(response.data));
```

### POST Request
```javascript
axios.post('/api/auth/login', {
    username: 'admin',
    password: 'password'
})
    .then(response => {
        const token = response.data.token;
        localStorage.setItem('authToken', token);
    });
```

### File Upload
```javascript
const formData = new FormData();
formData.append('file', document.getElementById('file').files[0]);

axios.post('/api/import/devices', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
})
    .then(response => console.log('Success:', response.data));
```

---

## RESPONSE FORMATS

### Health Response
```json
{
  "health_percentage": 92.5,
  "status": "Healthy",
  "total_devices": 45,
  "devices_online": 42,
  "devices_degraded": 2,
  "devices_offline": 1,
  "critical_incidents": 2,
  "open_incidents": 8,
  "critical_metrics": 5
}
```

### Device Response
```json
{
  "device_id": "DEV001",
  "device_name": "Router-01",
  "device_type": "Router",
  "ip_address": "192.168.1.1",
  "status": "UP",
  "uptime_hours": 720,
  "vendor": "Cisco",
  "model": "ASR1000"
}
```

### Metric Response
```json
{
  "device_id": "DEV001",
  "metric_name": "cpu_usage",
  "metric_value": 65.5,
  "unit": "%",
  "status": "OK",
  "threshold_warn": 80,
  "threshold_critical": 95,
  "timestamp": "2026-03-26T10:30:00Z"
}
```

### Login Response
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user_id": "user123",
  "username": "admin",
  "role": "Administrator"
}
```

---

## COLOR SCHEME
```
Primary:    #1e40af (Blue)
Secondary:  #7c3aed (Purple)
Success:    #22c55e (Green)
Warning:    #eab308 (Yellow)
Danger:     #ef4444 (Red)
Dark:       #0f172a (Background)
Light:      #f8fafc (Text)
```

---

## PAGE NAVIGATION (11 Pages)
1. Dashboard
2. Devices
3. Incidents
4. Metrics
5. Analytics
6. Topology
7. Alerts
8. Reports
9. System
10. Settings
11. User Profile

---

**Quick Start:** python main.py → http://localhost:5000
