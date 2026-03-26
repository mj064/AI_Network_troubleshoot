"""
Data import system for real network data
Supports CSV uploads, JSON imports, and API data ingestion
"""

import csv
import json
from typing import List, Dict, Tuple
from datetime import datetime
from .production_models import DatabaseManager, NetworkDevice, NetworkMetric, NetworkIncident, SystemLog, NetworkTopology


def parse_iso_timestamp(timestamp_str):
    """Parse ISO format timestamp, handling 'Z' suffix for UTC"""
    if not timestamp_str:
        return datetime.utcnow()
    
    # Remove 'Z' suffix if present for compatibility with fromisoformat
    if timestamp_str.endswith('Z'):
        timestamp_str = timestamp_str[:-1]
    
    try:
        return datetime.fromisoformat(timestamp_str)
    except:
        return datetime.utcnow()


class DataImporter:
    """Import real network data from various sources"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize importer with database connection"""
        self.db = db_manager
        self.session = db_manager.get_session()
        self.import_log = []
    
    def import_devices_csv(self, csv_file_path: str) -> Tuple[int, List[str]]:
        """
        Import devices from CSV file
        Expected columns: device_id, device_name, device_type, vendor, model, 
                        software_version, ip_address, mac_address, location, lab_network, status, uptime_hours
        """
        imported = 0
        errors = []
        
        try:
            with open(csv_file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        device = NetworkDevice(
                            device_id=row.get('device_id'),
                            device_name=row.get('device_name'),
                            device_type=row.get('device_type'),
                            vendor=row.get('vendor'),
                            model=row.get('model'),
                            software_version=row.get('software_version'),
                            ip_address=row.get('ip_address'),
                            mac_address=row.get('mac_address'),
                            location=row.get('location'),
                            lab_network=row.get('lab_network'),
                            status=row.get('status', 'UP'),
                            uptime_hours=int(row.get('uptime_hours', 0))
                        )
                        self.session.add(device)
                        imported += 1
                    except Exception as e:
                        errors.append(f"Row error: {str(e)}")
                
                self.session.commit()
        except Exception as e:
            errors.append(f"File read error: {str(e)}")
            self.session.rollback()
        
        self.import_log.append(f"Imported {imported} devices from {csv_file_path}")
        return imported, errors
    
    def import_metrics_csv(self, csv_file_path: str) -> Tuple[int, List[str]]:
        """
        Import metrics from CSV file
        Expected columns: timestamp, device_id, metric_name, metric_value, unit, 
                        threshold_warn, threshold_crit, status
        """
        imported = 0
        errors = []
        
        try:
            with open(csv_file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Find device by device_id
                        device = self.session.query(NetworkDevice).filter_by(
                            device_id=row.get('device_id')
                        ).first()
                        
                        if not device:
                            errors.append(f"Device {row.get('device_id')} not found")
                            continue
                        
                        metric = NetworkMetric(
                            device_id=device.id,
                            metric_name=row.get('metric_name'),
                            metric_value=float(row.get('metric_value', 0)),
                            unit=row.get('unit'),
                            threshold_warn=float(row.get('threshold_warn', 0)),
                            threshold_crit=float(row.get('threshold_crit', 0)),
                            status=row.get('status', 'OK'),
                            timestamp=parse_iso_timestamp(row.get('timestamp'))
                        )
                        self.session.add(metric)
                        imported += 1
                    except Exception as e:
                        errors.append(f"Row error: {str(e)}")
                
                self.session.commit()
        except Exception as e:
            errors.append(f"File read error: {str(e)}")
            self.session.rollback()
        
        self.import_log.append(f"Imported {imported} metrics from {csv_file_path}")
        return imported, errors
    
    def import_incidents_json(self, json_file_path: str) -> Tuple[int, List[str]]:
        """
        Import incidents from JSON file
        Expected structure: { "incidents": [...] }
        """
        imported = 0
        errors = []
        
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
                
                for incident_data in data.get('incidents', []):
                    try:
                        incident = NetworkIncident(
                            ticket_id=incident_data.get('ticket_id'),
                            title=incident_data.get('title'),
                            description=incident_data.get('description'),
                            severity=incident_data.get('severity'),
                            status=incident_data.get('status', 'OPEN'),
                            symptom_summary=incident_data.get('symptom_summary'),
                            root_cause=incident_data.get('root_cause'),
                            alerts_triggered=incident_data.get('alerts_triggered', []),
                            related_tickets=incident_data.get('related_tickets', [])
                        )
                        
                        # Add affected devices
                        for device_id in incident_data.get('affected_devices', []):
                            device = self.session.query(NetworkDevice).filter_by(
                                device_id=device_id
                            ).first()
                            if device:
                                incident.devices.append(device)
                        
                        self.session.add(incident)
                        imported += 1
                    except Exception as e:
                        errors.append(f"Incident error: {str(e)}")
                
                self.session.commit()
        except Exception as e:
            errors.append(f"File read error: {str(e)}")
            self.session.rollback()
        
        self.import_log.append(f"Imported {imported} incidents from {json_file_path}")
        return imported, errors
    
    def import_logs_csv(self, csv_file_path: str) -> Tuple[int, List[str]]:
        """
        Import system logs from CSV file
        Expected columns: timestamp, device_id, log_level, message, source
        """
        imported = 0
        errors = []
        
        try:
            with open(csv_file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        device = self.session.query(NetworkDevice).filter_by(
                            device_id=row.get('device_id')
                        ).first()
                        
                        if not device:
                            errors.append(f"Device {row.get('device_id')} not found")
                            continue
                        
                        log = SystemLog(
                            device_id=device.id,
                            log_level=row.get('log_level', 'INFO'),
                            message=row.get('message'),
                            source=row.get('source'),
                            timestamp=parse_iso_timestamp(row.get('timestamp'))
                        )
                        self.session.add(log)
                        imported += 1
                    except Exception as e:
                        errors.append(f"Row error: {str(e)}")
                
                self.session.commit()
        except Exception as e:
            errors.append(f"File read error: {str(e)}")
            self.session.rollback()
        
        self.import_log.append(f"Imported {imported} logs from {csv_file_path}")
        return imported, errors
    
    def import_topology_json(self, json_file_path: str) -> Tuple[int, List[str]]:
        """Import network topology from JSON file"""
        imported = 0
        errors = []
        
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
                
                for link in data.get('topology', {}).get('links', []):
                    try:
                        topology = NetworkTopology(
                            from_device_id=link.get('from'),
                            to_device_id=link.get('to'),
                            link_type=link.get('type'),
                            protocol=link.get('protocol'),
                            bandwidth=link.get('bandwidth'),
                            status=link.get('status', 'UP'),
                            vlan=link.get('vlan')
                        )
                        self.session.add(topology)
                        imported += 1
                    except Exception as e:
                        errors.append(f"Topology error: {str(e)}")
                
                self.session.commit()
        except Exception as e:
            errors.append(f"File read error: {str(e)}")
            self.session.rollback()
        
        self.import_log.append(f"Imported {imported} topology links from {json_file_path}")
        return imported, errors
    
    def get_import_statistics(self) -> Dict:
        """Get statistics about imported data"""
        return {
            'total_devices': self.session.query(NetworkDevice).count(),
            'total_metrics': self.session.query(NetworkMetric).count(),
            'total_incidents': self.session.query(NetworkIncident).count(),
            'total_logs': self.session.query(SystemLog).count(),
            'total_links': self.session.query(NetworkTopology).count(),
            'import_log': self.import_log
        }
    
    def clear_all_data(self):
        """Clear all imported data - use with caution"""
        try:
            self.session.query(SystemLog).delete()
            self.session.query(NetworkMetric).delete()
            self.session.query(NetworkIncident).delete()
            self.session.query(NetworkTopology).delete()
            self.session.query(NetworkDevice).delete()
            self.session.commit()
            self.import_log.append("All data cleared")
        except Exception as e:
            self.session.rollback()
            self.import_log.append(f"Error clearing data: {str(e)}")
