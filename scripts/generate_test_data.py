"""
Generate realistic network test data
Supports generating CSV/JSON for devices, metrics, incidents
"""

import csv
import json
from datetime import datetime, timedelta
import random

def generate_devices(count=50):
    """Generate realistic network devices"""
    vendors = [
        ("Cisco", ["ASR 9000", "Nexus 9000", "IOS XE 17"]),
        ("Juniper", ["EX4300", "QFX5100", "JunOS"]),
        ("Palo Alto", ["PA-5220", "PA-3260"]),
        ("F5", ["BIG-IP i7000", "BIG-IP i4800"]),
        ("Arista", ["DCS-7050", "EOS"]),
    ]
    
    device_types = ["Core Router", "Aggregation Switch", "Firewall", "Load Balancer", "Edge Router"]
    networks = ["NET-PROD", "NET-BACKUP", "NET-DMZ", "NET-5G", "NET-MANAGEMENT"]
    locations = [f"Rack-{chr(65+i)} Slot-{j+1}" for i in range(5) for j in range(3)]
    
    devices = []
    for i in range(count):
        vendor, models = random.choice(vendors)
        model = random.choice(models)
        devices.append({
            'device_id': f'D{i+1:04d}',
            'device_name': f'{random.choice(device_types).split()[0]}-{i+1:03d}',
            'device_type': random.choice(device_types),
            'vendor': vendor,
            'model': model,
            'software_version': f'{random.randint(15,23)}.{random.randint(1,9)}.{random.randint(0,5)}',
            'ip_address': f'{random.randint(10,192)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}',
            'location': random.choice(locations),
            'lab_network': random.choice(networks),
            'status': random.choices(['UP', 'DEGRADED', 'DOWN', 'ERROR'], weights=[60, 20, 15, 5])[0],
            'last_seen': (datetime.utcnow() - timedelta(hours=random.randint(0, 24))).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'uptime_hours': random.randint(0, 8760)
        })
    
    return devices


def generate_metrics(devices, samples_per_device=1000):
    """Generate historical metrics for devices with proper time series data across multiple days"""
    metrics_list = [
        ('cpu_utilization', 'percent', 75, 90),
        ('memory_utilization', 'percent', 80, 95),
        ('interface_in_bps', 'bps', 800000000, 950000000),
        ('interface_out_bps', 'bps', 800000000, 950000000),
        ('packet_loss', 'percent', 1, 5),
        ('bgp_sessions', 'count', 10, 15),
        ('latency', 'ms', 100, 200),
    ]
    
    metrics = []
    
    # Create time series data: 10 days of metrics, sampled every minute
    # Total samples_per_device per device, spread across 10 days
    base_time = datetime.utcnow() - timedelta(days=10)
    minutes_per_sample = (10 * 24 * 60) // samples_per_device  # Distribute samples across 10 days
    
    for idx, device in enumerate(devices):
        current_time = base_time + timedelta(hours=idx)  # Offset each device by hour to spread data
        for sample in range(samples_per_device):
            for metric_name, unit, warn_threshold, crit_threshold in metrics_list:
                # Create realistic time series data with trends
                value = 30 + random.randint(-10, 50)  # Base value with variation
                
                # Add some realistic patterns
                hour = current_time.hour
                if 8 <= hour <= 18:  # Business hours - higher load
                    value += random.randint(10, 30)
                
                status = 'OK'
                if value >= crit_threshold:
                    status = 'CRITICAL'
                elif value >= warn_threshold:
                    status = 'WARNING'
                
                metrics.append({
                    'timestamp': current_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'device_id': device['device_id'],
                    'device_name': device['device_name'],
                    'metric_name': metric_name,
                    'metric_value': value,
                    'unit': unit,
                    'threshold_warn': warn_threshold,
                    'threshold_crit': crit_threshold,
                    'status': status
                })
            
            # Move to next sample time
            current_time += timedelta(minutes=max(1, minutes_per_sample))
    
    return metrics


def generate_incidents(devices, count=20):
    """Generate realistic incidents"""
    severities = ['P1', 'P2', 'P3', 'P4']
    statuses = ['OPEN', 'IN_PROGRESS', 'RESOLVED']
    
    incidents = []
    for i in range(count):
        affected_count = random.randint(1, 3)
        affected_devices = random.sample([d['device_id'] for d in devices], affected_count)
        
        created_time = datetime.utcnow() - timedelta(hours=random.randint(0, 72))
        
        incidents.append({
            'ticket_id': f'INC-2024-{1000+i}',
            'title': random.choice([
                'High CPU Usage on Core Router',
                'Interface Down - Packet Loss Detected',
                'Memory Utilization Critical',
                'BGP Session Flapping',
                'Network Latency Spike',
                'Device Unreachable',
                'Configuration Sync Failed',
            ]),
            'severity': random.choice(severities),
            'status': random.choice(statuses),
            'created_at': created_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'reported_by': random.choice(['auto-monitor', 'john.doe@company.com', 'jane.smith@company.com']),
            'affected_devices': affected_devices,
            'symptom_summary': f'{len(affected_devices)} device(s) showing degraded performance',
            'user_reported_description': 'System alert triggered by monitoring',
        })
    
    return incidents


def save_devices_csv(devices, filename='test_devices.csv'):
    """Save devices to CSV"""
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=devices[0].keys())
        writer.writeheader()
        writer.writerows(devices)
    print(f"Saved {len(devices)} devices to {filename}")


def save_metrics_csv(metrics, filename='test_metrics.csv'):
    """Save metrics to CSV"""
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=metrics[0].keys())
        writer.writeheader()
        writer.writerows(metrics)
    print(f"Saved {len(metrics)} metrics to {filename}")


def save_incidents_json(incidents, filename='test_incidents.json'):
    """Save incidents to JSON"""
    with open(filename, 'w') as f:
        json.dump({'incidents': incidents}, f, indent=2)
    print(f"Saved {len(incidents)} incidents to {filename}")


if __name__ == '__main__':
    print("Generating test data...")
    print("-" * 60)
    
    # Generate 50 devices with 50 time-series samples each (10 days of data, 5-min intervals)
    devices = generate_devices(count=50)
    metrics = generate_metrics(devices, samples_per_device=50)
    incidents = generate_incidents(devices, count=20)
    
    # Save files
    save_devices_csv(devices)
    save_metrics_csv(metrics)
    save_incidents_json(incidents)
    
    print("-" * 60)
    print("Test data generated successfully!")
    print("\nNext steps:")
    print("1. Upload test_devices.csv via dashboard")
    print("2. Upload test_metrics.csv via dashboard")
    print("3. Upload test_incidents.json via dashboard")
    print("\nYour dashboard will populate with realistic data!")
