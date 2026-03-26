# 🚀 Enterprise Network Troubleshooting & Monitoring Platform

Production-ready network monitoring and troubleshooting system for enterprise telecom operations.

## ⚡ Quick Start

### Run Locally
```bash
python main.py
```
Then visit: **http://localhost:5000**

### Using Docker
```bash
cd deployment
docker-compose up -d
```

## Project Structure

```
├── src/
│   ├── backend/
│   │   ├── app/                          → Flask API (15+ endpoints)
│   │   └── utils/                        → 11 Enterprise services
│   └── frontend/                         → Dashboard UI (HTML/JS/CSS)
├── config/                               → Configuration & requirements
├── data/                                 → Test data (CSV/JSON)
├── deployment/                           → Docker & Nginx configs
├── scripts/                              → Utility & test scripts
├── tests/                                → Test suites
└── docs/                                 → Documentation
```

## ✅ ALL 11 FEATURES IMPLEMENTED & WORKING

### Core Features (4)
✅ **Professional Dashboard** - Real-time visualization with Chart.js  
✅ **Device Management** - Track 65+ devices with status indicators  
✅ **Incident Tracking** - Monitor and resolve network issues  
✅ **Metrics Monitoring** - Real-time metric visualization and thresholds  

### Enterprise Features (7)
✅ **ML Analytics** - Anomaly detection, trend analysis, forecasting  
✅ **Network Topology** - Interactive graph visualization & path finding  
✅ **Smart Alerting** - Slack/Email/Teams/PagerDuty integration  
✅ **PDF Reports** - Professional reporting with KPIs  
✅ **Authentication** - JWT with bcrypt password hashing  
✅ **RBAC System** - Admin/Engineer/Viewer roles (3 roles, 15+ permissions)  
✅ **SNMP Polling** - Real device polling (SNMPv2/v3)  

### Additional Capabilities
✅ **REST API** - 30 endpoints for programmatic access  
✅ **Multi-Tenancy** - SaaS-ready tenant isolation  
✅ **Redis Caching** - Performance optimization with smart TTL  
✅ **NetBox Integration** - Auto-sync device inventory  
✅ **Data Import** - CSV/JSON file import system  
✅ **Docker Ready** - Production deployment via Docker Compose  

## Documentation

- **Getting Started**: [docs/README.md](docs/README.md)
- **Project Structure**: [docs/STRUCTURE.md](docs/STRUCTURE.md)
- **Deployment Guide**: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

## Technology Stack

- **Backend**: Python 3.8+, Flask 2.3, SQLAlchemy 2.0
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **DevOps**: Docker, Docker Compose, Nginx

## Environment Setup

1. Copy the environment template:
   ```bash
   cp config/.env.example config/.env
   ```

2. Install dependencies:
   ```bash
   pip install -r config/production_requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Dashboard Access

**URL**: http://localhost:5000  
**Default**: No authentication required (configure in config/.env)

## Database

- **Location**: `data/database/network_troubleshoot.db`
- **Type**: SQLite (auto-created on first run)
- **Test Data**: Load from `data/test-data/` via the dashboard import feature

## API Endpoints

- `GET /api/health` - System health status
- `GET /api/devices` - List all devices
- `GET /api/incidents` - List incidents
- `GET /api/metrics` - Get metrics data
- `POST /api/import/*` - Import data files
- More endpoints available - see [docs/README.md](docs/README.md)

## Support

For issues, deployment help, or feature requests, refer to:
- [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - Production deployment
- [collaboration.md](docs/collaboration.md) - Team notes and development history

---

**Ready to monitor your network?** Start with `python main.py`
