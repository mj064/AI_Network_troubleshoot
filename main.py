#!/usr/bin/env python
"""
Network Troubleshooting Assistant - Entry Point
Run this script to start the Flask development server
"""
import sys
from src.backend.app import app

if __name__ == '__main__':
    print("Starting Network Troubleshooting Assistant...")
    print("Visit http://localhost:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=True)
