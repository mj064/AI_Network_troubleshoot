# Network Troubleshooting Assistant - Production Deployment Guide

## Overview

A complete production-ready network troubleshooting system with enterprise-grade features:
- **Real Data Support**: Import your own network data (devices, metrics, incidents)
- **Professional Frontend**: Modern, responsive dashboard with real-time updates
- **Scalable Backend**: RESTful API with database persistence
- **Cloud Ready**: Docker & Docker Compose support for easy deployment
- **Secure**: CORS, rate limiting, SSL/TLS support via Nginx

**Status**: ✅ **PRODUCTION READY** - Fully deployable with real-world data

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.8+
- pip or conda

### 1. Install Dependencies
```bash
pip install -r production_requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Initialize Database
```bash
python -c "from production_models import DatabaseManager; DatabaseManager().create_tables()"
```

### 4. Run Application
```bash
python production_app.py
```

### 5. Open Dashboard
```
http://localhost:5000
```

---

## 📦 Docker Deployment (Recommended for Production)

### Prerequisites
- Docker
- Docker Compose

### 1. Build and Start Services
```bash
docker-compose up -d
```

This starts:
- **Web App**: Port 5000
- **PostgreSQL Database**: Port 5432
- **Nginx Reverse Proxy**: Port 80/443

### 2. Access Dashboard
```
http://localhost
```

### 3. View Logs
```bash
docker-compose logs -f web
```

### 4. Stop Services
```bash
docker-compose down
```

### 5. Persist Data
```bash
docker-compose down -v  # Warning: removes volumes
```

---

## 📊 Data Import Guide

### Importing Your Own Network Data

The system accepts data in these formats:

#### 1. **Device Inventory (CSV)**

**File**: `devices.csv`

```csv
device_id,device_name,device_type,vendor,model,software_version,ip_address,mac_address,location,lab_network,status,uptime_hours
R001,ROUTER-PROD-01,Core Router,Cisco,ASR 9000,IOS-XE 17.6.1,192.168.1.1,AA:BB:CC:DD:EE:01,Rack-A,Production,UP,720
S001,SWITCH-PROD-01,Aggregation Switch,Juniper,EX4300,JunOS 22.2R1,192.168.1.2,AA:BB:CC:DD:EE:02,Rack-B,Production,UP,480
```

**Column Details:**
- `device_id`: Unique identifier (required)
- `device_name`: Friendly name
- `device_type`: Router, Switch, Firewall, Load Balancer, etc.
- `vendor`: Device manufacturer
- `model`: Device model number
- `software_version`: Firmware/OS version
- `ip_address`: Management IP (required)
- `mac_address`: MAC address
- `location`: Physical location
- `lab_network`: Network segment name
- `status`: UP, DOWN, DEGRADED, ERROR
- `uptime_hours`: Uptime in hours

#### 2. **Metrics Data (CSV)**

**File**: `metrics.csv`

```csv
timestamp,device_id,metric_name,metric_value,unit,threshold_warn,threshold_crit,status
2024-03-25T10:00:00Z,R001,cpu_utilization,45,percent,75,90,OK
2024-03-25T10:00:00Z,R001,memory_utilization,60,percent,80,95,OK
2024-03-25T10:05:00Z,R001,cpu_utilization,78,percent,75,90,WARNING
```

**Metric Types:**
- `cpu_utilization`: Percentage
- `memory_utilization`: Percentage
- `interface_utilization_In`: Bits per second
- `interface_utilization_Out`: Bits per second
- `packet_loss`: Percentage
- `bgp_session_count`: Count
- `route_table_size`: Routes

#### 3. **Incidents (JSON)**

**File**: `incidents.json`

```json
{
  "incidents": [
    {
      "ticket_id": "INC-2024-001",
      "title": "Router CPU High",
      "description": "CPU utilization exceeded 90%",
      "severity": "P1",
      "status": "OPEN",
      "created_at": "2024-03-25T10:00:00Z",
      "symptom_summary": "High CPU on Router R001",
      "affected_devices": ["R001", "S001"],
      "alerts_triggered": [
        "CPU_HIGH_THRESHOLD_BREACH",
        "BGP_SESSION_DROP"
      ]
    }
  ]
}
```

### Upload via Dashboard

1. Click **"Import Data"** button in dashboard
2. Select data type (Devices/Metrics/Incidents)
3. Choose CSV or JSON file
4. Click **"Import"**
5. Check import status in "Data Import Status" section

### Upload via API

```bash
# Import devices
curl -X POST http://localhost:5000/api/import/devices \
  -F "file=@devices.csv"

# Import metrics
curl -X POST http://localhost:5000/api/import/metrics \
  -F "file=@metrics.csv"

# Import incidents
curl -X POST http://localhost:5000/api/import/incidents \
  -F "file=@incidents.json"
```

---

## 🔌 API Endpoints Reference

### Health & Status

```
GET /api/health
GET /api/status
GET /api/docs
```

### Devices

```
GET /api/devices                    # List all devices
GET /api/devices?status=UP          # Filter by status
GET /api/devices?network=Production # Filter by network
GET /api/devices/<device_id>        # Get device details
GET /api/devices/<device_id>/metrics # Get device metrics
```

### Incidents

```
GET /api/incidents                          # List all incidents
GET /api/incidents?severity=P1              # Filter by severity
GET /api/incidents?status=OPEN              # Filter by status
GET /api/incidents/<ticket_id>              # Get incident details
GET /api/incidents/<ticket_id>/analysis     # Get AI analysis
```

### Metrics

```
GET /api/metrics/critical
GET /api/metrics/statistics?hours=24
```

### Data Import

```
POST /api/import/devices    # Upload device CSV
POST /api/import/metrics    # Upload metrics CSV
POST /api/import/incidents  # Upload incidents JSON
GET /api/import/status      # Check import statistics
```

---

## 🔐 Security Configuration

### Production Security Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure SSL certificates for Nginx
- [ ] Update database password in `docker-compose.yml`
- [ ] Set up proper firewall rules
- [ ] Enable CORS selectively (not `*`)
- [ ] Implement API authentication
- [ ] Use strong database passwords
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging

### Environment Variables

```bash
# .env (Production)
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://user:password@db:5432/network_troubleshoot
SECRET_KEY=your-256-character-secret-key-here
API_KEY=your-secure-api-key-here
UPLOAD_FOLDER=./uploads
MAX_UPLOAD_SIZE=16777216  # 16MB
```

---

## 📈 Performance Tuning

### For High-Traffic Systems

#### 1. Database Optimization
```bash
# Use PostgreSQL instead of SQLite
DATABASE_URL=postgresql://user:password@host:5432/db
```

#### 2. Gunicorn Workers
```bash
# In docker-compose.yml, increase workers
gunicorn --workers 8 --worker-class sync --threads 4
```

#### 3. Nginx Caching
```nginx
# Add to nginx.conf
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api:10m;
proxy_cache api;
proxy_cache_valid 60s;
```

#### 4. Database Connection Pooling
```python
# In production_models.py
from sqlalchemy.pool import QueuePool
engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40
)
```

---

## 🚨 Monitoring & Alerting

### Health Check
```bash
curl http://localhost:5000/api/health
```

Expected Response:
```json
{
  "status": "healthy",
  "health_percentage": 95.0,
  "devices": {
    "total": 20,
    "healthy": 19,
    "unhealthy": 1
  },
  "incidents": {
    "open": 2,
    "critical": 1
  }
}
```

### Log Monitoring
```bash
# Docker logs
docker-compose logs -f web

# Application logs
tail -f logs/app.log

# Database logs
docker-compose logs -f db
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

#### 2. Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose ps

# Check database logs
docker-compose logs db
```

#### 3. Import Fails
- Check file format (CSV/JSON)
- Verify required columns exist
- Check file size (max 16MB)
- Check device IDs match between files

#### 4. Slow Queries
- Add database indexes
- Use `EXPLAIN ANALYZE` for slow queries
- Archive old data to separate tables

---

## 📊 Backup & Restore

### Docker PostgreSQL Backup

```bash
# Backup database
docker-compose exec db pg_dump -U network_admin -d network_troubleshoot > backup.sql

# Restore database
docker-compose exec -T db psql -U network_admin -d network_troubleshoot < backup.sql
```

### Volume Backup
```bash
# Backup entire volume
docker run -v network-troubleshoot-app_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/db_backup.tar.gz /data
```

---

## 🌍 Cloud Deployment

### AWS EC2 Deployment

```bash
# 1. SSH into EC2 instance
ssh -i key.pem ubuntu@your-instance.com

# 2. Install Docker & Docker Compose
sudo apt update && sudo apt install -y docker.io docker-compose

# 3. Clone repository
git clone your-repo.git
cd your-repo

# 4. Configure environment
cp .env.example .env
nano .env  # Edit with your configuration

# 5. Start services
docker-compose -f docker-compose.yml up -d

# 6. Configure Nginx with SSL
# Use Let's Encrypt for free certificates
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: network-troubleshoot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: network-troubleshoot
  template:
    metadata:
      labels:
        app: network-troubleshoot
    spec:
      containers:
      - name: web
        image: network-troubleshoot:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: connection-string
```

---

## 📞 Support & Documentation

### API Documentation
```
http://localhost:5000/api/docs
```

### Additional Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## 📋 File Structure

```
project/
├── production_app.py           # Flask application
├── production_models.py        # Database models
├── production_frontend.html    # Web dashboard
├── data_importer.py           # Data import functionality
├── production_requirements.txt # Dependencies
├── Dockerfile                 # Docker image
├── docker-compose.yml         # Multi-container setup
├── nginx.conf                 # Reverse proxy config
├── .env.example              # Environment template
├── setup.sh                  # Setup script
└── README.md                 # This file
```

---

## ✅ Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Docker & Docker Compose installed (for containerized deployment)
- [ ] Database configured (.env)
- [ ] Dependencies installed (`pip install -r production_requirements.txt`)
- [ ] Database initialized
- [ ] Frontend accessible
- [ ] API endpoints tested
- [ ] Sample data imported
- [ ] Nginx configured (if using reverse proxy)
- [ ] SSL certificates installed (for HTTPS)
- [ ] Monitoring configured
- [ ] Backups scheduled
- [ ] Documentation reviewed

---

## 🎯 Next Steps

1. **Import Real Data**: Use the dashboard or API to import your network data
2. **Configure Alerts**: Set up notification rules for critical events
3. **Monitor Dashboard**: Track incidents and device health in real-time
4. **Analyze Trends**: Use metrics to identify patterns and optimize network
5. **Scale System**: Add more workers/database capacity as needed

---

**Version**: 2.0.0 (Production Ready)
**Last Updated**: March 25, 2024
**Status**: ✅ Enterprise Grade - Ready for Deployment
