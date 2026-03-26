"""
Comprehensive test suite for Network Troubleshooting Assistant
"""

import unittest
from datetime import datetime
from network_troubleshoot_assistant import (
    NetworkDevice, Metric, Incident, LogEntry,
    DeviceStatus, SeverityLevel,
    NetworkDeviceManager, IncidentManager, MetricsAnalyzer,
    LogAnalyzer, TroubleShootingEngine
)
from utils import DateTimeUtils, AlertCorrelation, NetworkAnalytics, ValidationUtils


class TestDataModels(unittest.TestCase):
    """Test data model classes"""
    
    def test_device_status_enum(self):
        """Test DeviceStatus enum"""
        self.assertEqual(DeviceStatus.UP.value, "UP")
        self.assertEqual(DeviceStatus.DOWN.value, "DOWN")
        self.assertEqual(DeviceStatus.DEGRADED.value, "DEGRADED")
        self.assertEqual(DeviceStatus.ERROR.value, "ERROR")
    
    def test_severity_level_enum(self):
        """Test SeverityLevel enum"""
        self.assertEqual(SeverityLevel.P1_CRITICAL.value, "P1")
        self.assertEqual(SeverityLevel.P2_HIGH.value, "P2")
    
    def test_network_device_creation(self):
        """Test NetworkDevice instantiation"""
        device = NetworkDevice(
            device_id="D001",
            device_name="ROUTER-LAB-01",
            device_type="Core Router",
            vendor="Cisco",
            model="ASR 9000",
            software_version="IOS-XE 17.6.1",
            ip_address="10.0.0.1",
            location="Rack-A Slot-1",
            lab_network="NET-LAB-ALPHA",
            status=DeviceStatus.UP,
            last_seen="2024-03-15T08:30:00Z",
            uptime_hours=72
        )
        self.assertEqual(device.device_id, "D001")
        self.assertEqual(device.status, DeviceStatus.UP)
    
    def test_metric_creation(self):
        """Test Metric instantiation"""
        metric = Metric(
            timestamp="2024-03-15T08:00:00Z",
            device_id="D001",
            device_name="ROUTER-LAB-01",
            metric_name="cpu_utilization",
            metric_value=78,
            unit="percent",
            threshold_warn=75,
            threshold_crit=90,
            status="WARNING"
        )
        self.assertEqual(metric.metric_name, "cpu_utilization")
        self.assertEqual(metric.metric_value, 78)
        self.assertEqual(metric.status, "WARNING")


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_parse_iso_timestamp(self):
        """Test ISO timestamp parsing"""
        ts = "2024-03-15T08:30:00Z"
        dt = DateTimeUtils.parse_iso_timestamp(ts)
        self.assertIsInstance(dt, datetime)
    
    def test_alert_severity_scoring(self):
        """Test alert severity scoring"""
        cpu_severity = AlertCorrelation.get_alert_severity("CPU_HIGH_THRESHOLD_BREACH")
        self.assertEqual(cpu_severity, 85)
    
    def test_alert_correlation(self):
        """Test alert correlation"""
        alerts = ["CPU_HIGH_THRESHOLD_BREACH", "MEMORY_LOW_WARNING", "BGP_SESSION_DROP"]
        correlation = AlertCorrelation.correlate_alerts(alerts)
        
        self.assertEqual(correlation["total_alerts"], 3)
        self.assertIn("likely_root_cause", correlation)
        self.assertGreater(correlation["avg_severity"], 0)
    
    def test_device_validation(self):
        """Test device data validation"""
        valid_device = {
            'device_id': 'D001',
            'device_name': 'ROUTER-01',
            'ip_address': '10.0.0.1',
            'status': 'UP'
        }
        is_valid, errors = ValidationUtils.validate_device_data(valid_device)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_incident_validation(self):
        """Test incident data validation"""
        valid_incident = {
            'ticket_id': 'INC-001',
            'title': 'Test Issue',
            'severity': 'P1',
            'affected_devices': ['D001']
        }
        is_valid, errors = ValidationUtils.validate_incident_data(valid_incident)
        self.assertTrue(is_valid)


class TestDataManagers(unittest.TestCase):
    """Test data manager classes"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.device_manager = NetworkDeviceManager()
        self.incident_manager = IncidentManager()
        self.metrics_analyzer = MetricsAnalyzer()
        self.log_analyzer = LogAnalyzer()
    
    def test_device_manager_initialization(self):
        """Test device manager initialization"""
        self.assertIsNotNone(self.device_manager.devices)
        self.assertEqual(len(self.device_manager.devices), 0)
    
    def test_incident_manager_initialization(self):
        """Test incident manager initialization"""
        self.assertIsNotNone(self.incident_manager.incidents)
        self.assertEqual(len(self.incident_manager.incidents), 0)
    
    def test_metrics_analyzer_initialization(self):
        """Test metrics analyzer initialization"""
        self.assertIsNotNone(self.metrics_analyzer.metrics)
        self.assertEqual(len(self.metrics_analyzer.metrics), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        """Set up test fixtures with real data"""
        base_path = r"c:\Users\HP\Coding\TRYOUT\AI Powered Network Troubleshooting Assistant for Telecom Test Labs"
        
        self.device_manager = NetworkDeviceManager()
        self.incident_manager = IncidentManager()
        self.metrics_analyzer = MetricsAnalyzer()
        self.log_analyzer = LogAnalyzer()
        
        try:
            self.device_manager.load_from_csv(f"{base_path}\\device_inventory.csv")
            self.incident_manager.load_from_json(f"{base_path}\\incident_tickets.json")
            self.metrics_analyzer.load_from_csv(f"{base_path}\\snmp_metrics.csv")
            self.log_analyzer.load_from_file(f"{base_path}\\router_syslog.log")
            self.engine = TroubleShootingEngine(
                self.device_manager, self.incident_manager,
                self.metrics_analyzer, self.log_analyzer
            )
        except:
            self.skipTest("Data files not found")
    
    def test_load_all_data(self):
        """Test loading all data sources"""
        self.assertGreater(len(self.device_manager.devices), 0)
        self.assertGreater(len(self.incident_manager.incidents), 0)
        self.assertGreater(len(self.metrics_analyzer.metrics), 0)
    
    def test_get_devices_by_status(self):
        """Test filtering devices by status"""
        up_devices = self.device_manager.get_devices_by_status(DeviceStatus.UP)
        self.assertIsInstance(up_devices, list)
    
    def test_get_open_incidents(self):
        """Test getting open incidents"""
        open_incidents = self.incident_manager.get_open_incidents()
        self.assertIsInstance(open_incidents, list)
    
    def test_get_critical_metrics(self):
        """Test getting critical metrics"""
        critical = self.metrics_analyzer.get_critical_metrics()
        self.assertIsInstance(critical, list)
    
    def test_generate_health_report(self):
        """Test health report generation"""
        report = self.engine.generate_health_report()
        
        self.assertIn("timestamp", report)
        self.assertIn("network_summary", report)
        self.assertIn("incident_summary", report)
        self.assertIn("metric_summary", report)
    
    def test_analyze_incident(self):
        """Test incident analysis"""
        open_incidents = self.incident_manager.get_open_incidents()
        if open_incidents:
            incident = open_incidents[0]
            analysis = self.engine.analyze_incident(incident)
            
            self.assertIn("ticket_id", analysis)
            self.assertIn("affected_devices", analysis)
            self.assertIn("root_cause_analysis", analysis)
            self.assertIn("recommended_actions", analysis)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    run_tests()
