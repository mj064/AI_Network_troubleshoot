#!/bin/bash

# Network Troubleshooting Assistant - Setup Script
# Run this script to set up the production environment

echo "================================"
echo "Network Troubleshooting Assistant"
echo "Production Setup Script"
echo "================================"

# Check Python version
echo "Checking Python installation..."
python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r production_requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p data

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please update .env with your configuration"
fi

# Create initial database
echo "Initializing database..."
python3 -c "from production_models import DatabaseManager; DatabaseManager().create_tables()"

echo "================================"
echo "Setup Complete!"
echo "To start the application:"
echo "1. source venv/bin/activate"
echo "2. python production_app.py"
echo "3. Open http://localhost:5000 in your browser"
echo "================================"
