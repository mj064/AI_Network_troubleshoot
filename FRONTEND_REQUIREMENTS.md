# Frontend Developer Requirements
## Enterprise Network Monitoring Platform

**Project:** Network Troubleshooting Assistant - Enterprise Edition  
**Version:** 2.0.0  
**Date:** March 26, 2026

---

## 1. TECH STACK & LIBRARIES

### Required Technologies
- **HTML5/CSS3/JavaScript** (Vanilla - no framework required)
- **Chart.js 3.9.1** - Data visualization library (via CDN)
- **Axios** - HTTP client for API calls (via CDN)
- **Font Awesome 6.4.0** - Icon library (via CDN)
- **Google Fonts (Inter)** - Typography

### CDN Links
```html
<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>

<!-- Axios -->
<script src="https://cdn.jsdelivr.net/npm/axios@0.27.2/dist/axios.min.js"></script>

<!-- Font Awesome -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

---

## 2. API CONFIGURATION

### Base URL
```
http://localhost:5000/api
```

### CORS Configuration
- ✅ CORS enabled for all origins
- All API responses in **JSON format**
- File upload max size: **16MB**
- Supported formats: CSV, JSON

---

## 3. API ENDPOINTS (30 Total)

### Core Endpoints (5)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/health` | GET | System health overview | - |
| `/api/status` | GET | Device & incident status | - |
| `/api/devices` | GET | List all devices | status, network, type |
| `/api/devices/<device_id>` | GET | Single device details | - |
| `/api/devices/<device_id>/metrics` | GET | Device-specific metrics | - |

### Incidents (3)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/incidents` | GET | List all incidents | status, severity |
| `/api/incidents/<ticket_id>` | GET | Single incident details | - |
| `/api/incidents/<ticket_id>/analysis` | GET | AI analysis of incident | - |

### Metrics (3)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/metrics` | GET | All metrics data | device_id, metric_name |
| `/api/metrics/critical` | GET | Critical metrics only | - |
| `/api/metrics/statistics` | GET | Aggregated metric stats | - |

### Data Import (4)

| Endpoint | Method | Purpose | Body |
|----------|--------|---------|------|
| `/api/import/devices` | POST | Upload device CSV | file (multipart) |
| `/api/import/metrics` | POST | Upload metrics CSV | file (multipart) |
| `/api/import/incidents` | POST | Upload incidents JSON | file (multipart) |
| `/api/import/status` | GET | Check import status | - |

### ML Analytics (3)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/analytics/anomalies` | GET | Detect anomalies with ML | device_id, metric_name, hours |
| `/api/analytics/trends` | GET | Trend analysis | device_id, metric_name, days |
| `/api/analytics/forecast` | GET | Predictive forecasting | device_id, metric_name, forecast_days, threshold |

### Network Topology (1)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/topology/graph` | GET | Network topology graph | - |

### Authentication & RBAC (2)

| Endpoint | Method | Purpose | Body/Parameters |
|----------|--------|---------|-----------------|
| `/api/auth/login` | POST | JWT login | username, password |
| `/api/rbac/permissions/<user_id>` | GET | User permissions | - |

### Alerting (2)

| Endpoint | Method | Purpose | Body |
|----------|--------|---------|------|
| `/api/alerts/send` | POST | Send alert (Slack/Email/Teams) | title, severity, description, device, metric |
| `/api/alerts/history` | GET | Alert history | hours |

### Reporting (1)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/reports/generate` | POST | PDF report generation | type |

### Integrations (2)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/netbox/sync` | POST | Sync from NetBox DCIM | url, token |
| `/api/cache/stats` | GET | Redis cache stats | - |

### Multi-Tenancy (2)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/tenants/list` | GET | List all tenants | - |
| `/api/tenants/billing` | GET | Billing info | tenant_id |

### Documentation (1)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/docs` | GET | API documentation |

---

## 4. FRONTEND FEATURES (11 Modules)

### Core Features (4)
1. **Dashboard** - Overview with KPIs, health status, real-time charts
2. **Device Management** - List, filter, search devices with status indicators
3. **Incident Tracking** - View/manage network incidents, search by severity
4. **Metrics Monitoring** - Real-time metric visualization with threshold indicators

### Enterprise Features (7)
5. **ML Analytics**
   - Anomaly detection with visualizations
   - Trend analysis (7, 30, 90 days)
   - Predictive forecasting charts

6. **Network Topology** - Visual network graph with device relationships

7. **Smart Alerts** - Alert management, notification history, routing

8. **Advanced Reporting** - PDF generation, KPI reports, data export

9. **System Configuration** - Settings, preferences, system info

10. **Authentication** - Login page, JWT token handling, session management

11. **RBAC** - Role-based access control, permission display

---

## 5. DESIGN SYSTEM

### Color Tokens
```css
:root {
    --primary: #1e40af;           /* Blue */
    --primary-dark: #1e3a8a;      /* Darker Blue */
    --secondary: #7c3aed;         /* Purple */
    --accent: #f97316;            /* Orange */
    --success: #22c55e;           /* Green */
    --warning: #eab308;           /* Yellow */
    --danger: #ef4444;            /* Red */
    --dark: #0f172a;              /* Background */
    --dark-2: #1e293b;            /* Panel */
    --light: #f8fafc;             /* Light text */
    --gray: #64748b;              /* Gray */
    --border: #e2e8f0;            /* Border color */
    
    --spacing: 1rem;
    --radius: 12px;
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    --shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 20px 45px rgba(0, 0, 0, 0.15);
}
```

### Layout Structure
```
┌─────────────────────────────────────────┐
│         HEADER (Sticky, 70px)           │
├─────────┬──────────────────────────────┤
│         │                              │
│ SIDEBAR │      MAIN CONTENT AREA       │
│ (260px) │      (Scrollable)            │
│         │                              │
│         │                              │
└─────────┴──────────────────────────────┘
```

### Typography
- **Font Family:** Inter
- **Weights:** 300, 400, 500, 600, 700
- **Headings:** Inter 600-700
- **Body:** Inter 400

---

## 6. DATA MODELS

### Device Object
```json
{
  "device_id": "DEV001",
  "device_name": "Router-01",
  "device_type": "Router",
  "ip_address": "192.168.1.1",
  "status": "UP|DOWN|DEGRADED",
  "uptime_hours": 720,
  "vendor": "Cisco",
  "model": "ASR1000",
  "location": "Data Center 1",
  "lab_network": "Production",
  "mac_address": "00:1A:2B:3C:4D:5E"
}
```

### Metric Object
```json
{
  "device_id": "DEV001",
  "metric_name": "cpu_usage|memory_usage|bandwidth_usage|error_rate",
  "metric_value": 65.5,
  "unit": "%|Mbps|errors/s",
  "status": "OK|WARNING|CRITICAL",
  "threshold_warn": 80,
  "threshold_critical": 95,
  "timestamp": "2026-03-26T10:30:00Z"
}
```

### Incident Object
```json
{
  "ticket_id": "INC001",
  "title": "High CPU on Router-01",
  "severity": "P1|P2|P3|P4|P5",
  "status": "OPEN|RESOLVED",
  "description": "CPU utilization exceeded critical threshold",
  "affected_devices": ["DEV001", "DEV002"],
  "created_at": "2026-03-26T10:00:00Z",
  "created_by": "Network Admin",
  "tags": ["cpu", "critical"]
}
```

### Analytics Response (Anomalies)
```json
{
  "device_id": "DEV001",
  "metric_name": "cpu_usage",
  "anomalies": [
    {
      "timestamp": "2026-03-26T10:00:00Z",
      "value": 95.2,
      "is_anomaly": true,
      "z_score": 3.5,
      "severity": "HIGH"
    }
  ],
  "summary": {
    "total_points": 100,
    "anomaly_count": 5,
    "anomaly_percentage": 5.0
  }
}
```

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

---

## 7. KEY JAVASCRIPT FUNCTIONS TO IMPLEMENT

### Navigation & Page Management
```javascript
// Navigate to different pages
function showPage(page, event) {
    // Hide all pages, show selected page
    // Update navigation highlight
    // Call appropriate load function
}
```

### Dashboard
```javascript
async function loadDashboard() {
    // Fetch: /api/health
    // Display KPIs, charts, status overview
}
```

### Devices
```javascript
async function loadDevices() {
    // Fetch: /api/devices
    // Display device list/table with filters
    // Show status badges
}
```

### Incidents
```javascript
async function loadIncidents() {
    // Fetch: /api/incidents
    // Display incident list with severity
    // Enable filtering and search
}
```

### Metrics
```javascript
async function loadMetrics() {
    // Fetch: /api/metrics/critical
    // Display metric cards with charts
    // Use Chart.js for visualization
}
```

### ML Analytics
```javascript
async function loadAnalytics() {
    // Fetch: /api/analytics/anomalies
    // Fetch: /api/analytics/trends
    // Fetch: /api/analytics/forecast
    // Display ML-powered charts and insights
}
```

### Network Topology
```javascript
async function loadTopology() {
    // Fetch: /api/topology/graph
    // Parse D3.js format network data
    // Render interactive network visualization
}
```

### Smart Alerts
```javascript
async function loadAlerts() {
    // Fetch: /api/alerts/history
    // Display alert timeline/list
}

async function sendAlert(alertData) {
    // POST: /api/alerts/send
    // Trigger alert to Slack/Email/Teams
}
```

### Reports
```javascript
async function generateReport(reportType) {
    // POST: /api/reports/generate
    // Download PDF file
}
```

### Authentication
```javascript
async function login(username, password) {
    // POST: /api/auth/login
    // Store JWT token
    // Redirect to dashboard
}

async function logout() {
    // Clear token
    // Redirect to login
}
```

### File Upload
```javascript
async function uploadDevices(file) {
    // POST: /api/import/devices (multipart/form-data)
    // Show progress
}

async function uploadMetrics(file) {
    // POST: /api/import/metrics
}

async function uploadIncidents(file) {
    // POST: /api/import/incidents
}
```

---

## 8. UI COMPONENTS CHECKLIST

### Navigation
- [ ] Sidebar with 11 navigation items
- [ ] Active page highlighting
- [ ] Collapsible menu (mobile)

### Header
- [ ] Dashboard title
- [ ] Search/filter controls
- [ ] User menu
- [ ] Logout button

### Content Areas
- [ ] Device list/table
- [ ] Incident list/table
- [ ] Metric cards with status
- [ ] Chart containers
- [ ] Alert notifications
- [ ] Modal dialogs

### Status Indicators
- [ ] UP (Green #22c55e)
- [ ] DOWN (Red #ef4444)
- [ ] DEGRADED (Yellow #eab308)
- [ ] OK/WARNING/CRITICAL badges

### Charts (Chart.js)
- [ ] Line charts (trends, metrics)
- [ ] Bar charts (comparisons)
- [ ] Pie/Doughnut charts (distribution)
- [ ] Gauge charts (percentages)

### Forms
- [ ] Login form
- [ ] File upload inputs
- [ ] Filter/search inputs
- [ ] Alert configuration forms

### Feedback
- [ ] Loading spinners
- [ ] Success messages
- [ ] Error notifications
- [ ] Progress indicators

---

## 9. DEVELOPMENT SETUP

### Prerequisites
- Node.js or Python (backend runs on Python)
- Code editor (VS Code recommended)
- Browser (Chrome, Firefox, Safari, or Edge)

### Running the Project
```bash
# 1. Navigate to project root
cd c:\Users\HP\Coding\TRYOUT

# 2. Start the backend server
python main.py
# Server runs on http://localhost:5000

# 3. Open in browser
# http://localhost:5000
```

### Frontend Files Location
```
src/
└── frontend/
    ├── dashboard.html        (Main UI - 11 features)
    └── index.html           (Alternative entry point)
```

### Development Tips
- No build step required (vanilla JS)
- Open DevTools (F12) to debug
- Check Network tab for API calls
- Use Console for JavaScript errors
- Reload page (Ctrl+R) to see changes

---

## 10. BUILD & DEPLOYMENT

### Production Build
```bash
# No build step needed - files are already production-ready

# Using Docker (provided in deployment/Dockerfile):
docker build -f deployment/Dockerfile -t network-monitoring:latest .
docker run -p 5000:5000 network-monitoring:latest
```

### Docker Compose (Full Stack)
```bash
docker-compose up
# Runs Flask, PostgreSQL, Nginx
```

---

## 11. DEVELOPMENT CHECKLIST

### Phase 1: Setup
- [ ] Clone/access project files
- [ ] Review this requirements document
- [ ] Start backend server (python main.py)
- [ ] Test API endpoints in Postman/browser

### Phase 2: Core Features
- [ ] Implement Dashboard page
- [ ] Implement Device Management
- [ ] Implement Incident Tracking
- [ ] Implement Metrics Monitoring
- [ ] Test all endpoints

### Phase 3: Enterprise Features
- [ ] Implement ML Analytics pages
- [ ] Implement Network Topology
- [ ] Implement Smart Alerts
- [ ] Implement Reporting
- [ ] Implement System Configuration

### Phase 4: Auth & Polish
- [ ] Implement Login/Authentication
- [ ] Implement RBAC checks
- [ ] Add loading states
- [ ] Add error handling
- [ ] Responsive design
- [ ] Performance optimization

### Phase 5: Testing & Deployment
- [ ] Test all features in browser
- [ ] Mobile responsiveness
- [ ] API error handling
- [ ] Cross-browser testing
- [ ] Deploy to production

---

## 12. API USAGE EXAMPLES

### Fetch Devices
```javascript
axios.get('http://localhost:5000/api/devices')
    .then(response => {
        const devices = response.data.devices;
        console.log(devices);
    })
    .catch(error => console.error(error));
```

### Fetch Critical Metrics
```javascript
axios.get('http://localhost:5000/api/metrics/critical')
    .then(response => {
        const metrics = response.data.metrics;
        // Render with Chart.js
    })
    .catch(error => console.error(error));
```

### Login
```javascript
axios.post('http://localhost:5000/api/auth/login', {
    username: 'admin',
    password: 'password'
})
    .then(response => {
        const token = response.data.token;
        localStorage.setItem('authToken', token);
    })
    .catch(error => console.error('Login failed:', error));
```

### Upload Devices
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

axios.post('http://localhost:5000/api/import/devices', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
})
    .then(response => console.log('Upload success:', response.data))
    .catch(error => console.error('Upload failed:', error));
```

### Get Anomalies
```javascript
axios.get('http://localhost:5000/api/analytics/anomalies', {
    params: {
        device_id: 'DEV001',
        metric_name: 'cpu_usage',
        hours: 24
    }
})
    .then(response => {
        const anomalies = response.data.anomalies;
        // Create anomaly chart
    })
    .catch(error => console.error(error));
```

---

## 13. ERROR HANDLING

### Common HTTP Status Codes
| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK | Success |
| 400 | Bad Request | Check parameters |
| 401 | Unauthorized | Login required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Backend issue |

### Error Response Format
```json
{
  "error": "Error message",
  "status": 400
}
```

### Recommended Error Handling
```javascript
axios.get('/api/endpoint')
    .then(response => {
        // Handle success
        console.log(response.data);
    })
    .catch(error => {
        if (error.response) {
            // Server responded with error status
            console.error('Error:', error.response.data.error);
            showErrorMessage(error.response.data.error);
        } else if (error.request) {
            // Request made but no response
            console.error('No response from server');
            showErrorMessage('Server not responding');
        } else {
            // Error in request setup
            console.error('Request error:', error.message);
        }
    });
```

---

## 14. PERFORMANCE CONSIDERATIONS

### Optimization Tips
- Use pagination for large lists (devices, incidents)
- Cache API responses when appropriate
- Lazy load images and charts
- Minify CSS/JavaScript for production
- Use Chart.js efficiently (limit datasets)
- Implement virtual scrolling for large tables
- Debounce search/filter inputs

### Caching Strategy
```javascript
// Simple cache implementation
const apiCache = {};

async function getCachedData(url, ttl = 60000) {
    if (apiCache[url] && Date.now() - apiCache[url].time < ttl) {
        return apiCache[url].data;
    }
    const response = await axios.get(url);
    apiCache[url] = { data: response.data, time: Date.now() };
    return response.data;
}
```

---

## 15. SECURITY CONSIDERATIONS

### Authentication
- Store JWT tokens in localStorage or sessionStorage
- Include token in Authorization header: `Authorization: Bearer <token>`
- Clear token on logout
- Handle token expiration gracefully

### Input Validation
- Validate file types before upload
- Sanitize user inputs
- Use htmlspecialchars/escaping for display

### CORS Handling
- API supports CORS
- No additional CORS configuration needed
- All cross-origin requests will work

### Data Protection
- Never log sensitive data (passwords, tokens)
- Use HTTPS in production
- Validate API responses
- Implement rate limiting if needed

---

## 16. RESPONSIVE DESIGN

### Breakpoints
```css
/* Mobile */
@media (max-width: 768px) {
    .sidebar { width: 100%; height: auto; }
    .main-content { padding: 1rem; }
}

/* Tablet */
@media (768px < width <= 1024px) {
    .sidebar { width: 200px; }
}

/* Desktop */
@media (width > 1024px) {
    .sidebar { width: 260px; }
}
```

---

## 17. TESTING CHECKLIST

### Functional Testing
- [ ] All 11 pages load correctly
- [ ] All API endpoints respond with data
- [ ] Navigation works between pages
- [ ] Charts render properly
- [ ] Forms submit correctly
- [ ] Upload functionality works
- [ ] Filters/search work

### API Testing
- [ ] GET endpoints return data
- [ ] POST endpoints accept data
- [ ] Error responses are handled
- [ ] File uploads work (CSV, JSON)
- [ ] Pagination works (if implemented)

### Browser Testing
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile browsers

### Performance Testing
- [ ] Page load time < 3 seconds
- [ ] API response time < 1 second
- [ ] Chart rendering smooth
- [ ] No memory leaks
- [ ] Handles 1000+ devices gracefully

---

## 18. COMMON ISSUES & SOLUTIONS

### Issue: "Cannot connect to API"
**Solution:** 
- Ensure backend server is running (`python main.py`)
- Check API base URL is correct
- Verify CORS is enabled
- Check browser console for errors

### Issue: "Charts not displaying"
**Solution:**
- Ensure Chart.js library is loaded
- Check data format matches Chart.js requirements
- Verify canvas element exists in HTML
- Check browser console for errors

### Issue: "Login not working"
**Solution:**
- Verify credentials are correct
- Ensure `/api/auth/login` endpoint is working
- Check token is being stored correctly
- Verify JWT token is included in subsequent requests

### Issue: "File upload fails"
**Solution:**
- Check file size (max 16MB)
- Verify file format (CSV or JSON)
- Ensure multipart/form-data header is set
- Check file encoding (UTF-8)

---

## 19. SUPPORT & DOCUMENTATION

### API Documentation Live
```
http://localhost:5000/api/docs
```
Visit this URL while backend is running to see full API documentation.

### Backend Code Structure
```
src/backend/
├── app/
│   ├── production_app.py      (Flask API - 30 endpoints)
│   ├── production_models.py   (Database ORM models)
│   └── data_importer.py       (CSV/JSON import)
├── utils/
│   ├── ml_service.py          (Anomaly detection, forecasting)
│   ├── topology_service.py    (Network graph, visualization)
│   ├── alerting_service.py    (Alert management)
│   ├── auth_service.py        (JWT authentication)
│   ├── rbac_service.py        (Role-based access control)
│   ├── reporting_service.py   (PDF generation)
│   ├── snmp_service.py        (SNMP device polling)
│   ├── caching_service.py     (Redis caching)
│   └── multi_tenancy_service.py (SaaS support)
```

### Frontend File Locations
```
src/frontend/
├── dashboard.html      (Main UI)
└── index.html         (Alternative UI)
```

---

## 20. QUICK START GUIDE FOR NEW DEVELOPER

1. **Read this document** - Understand architecture and requirements
2. **Start backend** - `python main.py` (runs on localhost:5000)
3. **Test APIs** - Visit `http://localhost:5000/api/docs`
4. **Open frontend** - Edit `src/frontend/dashboard.html`
5. **Use DevTools** - F12 to debug JavaScript and API calls
6. **Check examples** - Review API usage examples in section 12
7. **Build UI** - Create pages for 11 features
8. **Connect API** - Use Axios to fetch data from endpoints
9. **Test thoroughly** - Use checklist in section 17
10. **Deploy** - Follow build instructions in section 10

---

## 21. HELPFUL RESOURCES

### JavaScript Fetch Examples
```javascript
// Simple GET
const data = await axios.get('/api/endpoint');

// With query parameters
await axios.get('/api/devices?status=UP&network=Production');

// POST with data
await axios.post('/api/auth/login', {
    username: 'admin',
    password: 'password'
});

// File upload
const formData = new FormData();
formData.append('file', file);
await axios.post('/api/import/devices', formData);
```

### Chart.js Quick Start
```javascript
const ctx = document.getElementById('myChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar'],
        datasets: [{
            label: 'CPU Usage',
            data: [65, 59, 80],
            borderColor: '#1e40af',
            backgroundColor: 'rgba(30, 64, 175, 0.1)'
        }]
    }
});
```

### Status Badge HTML
```html
<!-- UP Status -->
<span style="color: #22c55e;">● UP</span>

<!-- DOWN Status -->
<span style="color: #ef4444;">● DOWN</span>

<!-- DEGRADED Status -->
<span style="color: #eab308;">● DEGRADED</span>
```

---

## 22. PROJECT COMPLETION STATUS

### Already Completed by Backend Team ✅
- [x] Flask API with 30 working endpoints
- [x] Database schema (SQLite/PostgreSQL)
- [x] All 11 backend services implemented
- [x] Authentication & RBAC system
- [x] ML analytics engine (anomaly detection, forecasting)
- [x] Network topology service
- [x] Alert management system
- [x] PDF report generation
- [x] Data import system (CSV/JSON)
- [x] Multi-tenancy support
- [x] Caching layer (Redis)
- [x] Docker deployment ready

### Frontend Developer Tasks 📋
1. Build responsive HTML/CSS layout
2. Implement 11 page sections
3. Connect Axios to 30 API endpoints
4. Create data visualizations (Chart.js)
5. Implement form validations
6. Add loading/error states
7. Handle authentication flow
8. Test all features
9. Deploy to production

---

**Generated:** March 26, 2026  
**Project:** Enterprise Network Monitoring Platform v2.0.0
