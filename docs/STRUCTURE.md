# Project Structure

## Overview
```
network-troubleshooting-assistant/
├── src/                        # Source code
│   ├── backend/               # Backend Python application
│   │   ├── app/              # Main Flask application
│   │   │   ├── production_app.py       # Flask app and API routes
│   │   │   ├── production_models.py    # Database models (SQLAlchemy)
│   │   │   └── data_importer.py        # CSV/JSON data import utilities
│   │   └── utils/            # Utility modules
│   │       ├── analytics.py   # Analytics and metrics processing
│   │       ├── api.py         # API helpers
│   │       └── utils.py       # General utilities
│   └── frontend/              # Frontend UI
│       ├── index.html         # Main dashboard page
│       └── dashboard.html     # Enhanced dashboard (alternative view)
│
├── config/                    # Configuration files
│   ├── .env                   # Environment variables (local, git-ignored)
│   ├── .env.example          # Example environment file
│   ├── config.json           # Application configuration
│   ├── nginx.conf            # Nginx reverse proxy config
│   └── production_requirements.txt  # Python dependencies
│
├── data/                      # Data and databases
│   ├── test-data/           # Test data files
│   │   ├── test_devices.csv      # Device inventory test data
│   │   ├── test_metrics.csv      # Metrics test data
│   │   └── test_incidents.json   # Incidents test data
│   └── database/            # SQLite database file
│       └── network_troubleshoot.db
│
├── deployment/               # Docker and deployment
│   ├── Dockerfile           # Docker image configuration
│   ├── docker-compose.yml   # Docker Compose configuration
│   └── setup.sh             # Setup script
│
├── scripts/                  # Utility scripts
│   ├── generate_test_data.py    # Generate synthetic test data
│   └── test_suite.py            # Test suite
│
├── docs/                     # Documentation
│   ├── README.md             # Main project documentation
│   ├── DEPLOYMENT_GUIDE.md   # Deployment instructions
│   └── STRUCTURE.md          # This file
│
├── archive/                  # Old projects and archived files
│   ├── AI Powered Network.../  # Original project folder
│   ├── AI_Network_Troubleshooting_Complete/
│   ├── network_troubleshoot_assistant.py # Old backend
│   └── requirements-old.txt   # Old dependencies
│
├── uploads/                  # User uploaded files (git-ignored)
├── .venv/                    # Virtual environment (git-ignored)
├── __pycache__/             # Python cache (git-ignored)
├── .gitignore               # Git ignore rules
├── main.py                  # Application entry point
└── production_requirements.txt # Current Python dependencies
```

## Directory Descriptions

### src/backend/app/
Contains the core Flask application, database models, and data import logic.
- **production_app.py**: Main Flask app with all API routes
- **production_models.py**: SQLAlchemy ORM models for database tables
- **data_importer.py**: Functions to import data from CSV/JSON files

### src/backend/utils/
Utility modules used throughout the application.
- **analytics.py**: Metrics analysis and processing
- **api.py**: API helper functions
- **utils.py**: General utility functions

### src/frontend/
HTML/CSS/JavaScript frontend files.
- **index.html**: Basic dashboard (deprecated)
- **dashboard.html**: Enhanced professional dashboard

### config/
All configuration files including environment variables and infrastructure configs.
- **.env**: Local environment (NOT in git)
- **.env.example**: Template for environment variables
- **config.json**: Application settings
- **nginx.conf**: Web server configuration
- **production_requirements.txt**: Python package dependencies

### data/
Data storage for databases, test data, and imports.
- **test-data/**: Sample CSV/JSON files for testing data import
- **database/**: SQLite database file (auto-created on first run)

### deployment/
Docker and deployment-related files.
- **Dockerfile**: Container definition
- **docker-compose.yml**: Multi-container orchestration
- **setup.sh**: Initialization script

### scripts/
Standalone scripts for testing and data generation.
- **generate_test_data.py**: Creates synthetic test data
- **test_suite.py**: Automated tests

### docs/
Project documentation.
- **README.md**: Getting started and overview
- **DEPLOYMENT_GUIDE.md**: Production deployment instructions
- **STRUCTURE.md**: This file

### archive/
Legacy code and previous versions (not used in current project).

## Running the Application

### Development
```bash
cd network-troubleshooting-assistant
python main.py
```

### Docker
```bash
cd deployment/
docker-compose up -d
```

## Database

The SQLite database is stored in `data/database/network_troubleshoot.db` and is automatically created on first run.

To import test data:
1. Place CSV files in `data/test-data/`
2. Use the import endpoints in the API to load data

## Dependencies

All Python dependencies are listed in `config/production_requirements.txt`. Install with:
```bash
pip install -r config/production_requirements.txt
```

## Environment Configuration

Copy `config/.env.example` to `config/.env` and customize settings:
```bash
cp config/.env.example config/.env
```

Always keep `.env` in `.gitignore` to avoid committing secrets.
