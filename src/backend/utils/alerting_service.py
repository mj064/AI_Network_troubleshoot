"""
Webhook Alerting System
Send alerts to multiple platforms: Slack, Email, PagerDuty, Teams, etc.
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import asyncio


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertHandler:
    """Base class for alert handlers"""
    
    def send(self, alert_data: Dict) -> bool:
        """Send alert - override in subclasses"""
        raise NotImplementedError


class SlackAlertHandler(AlertHandler):
    """Send alerts to Slack"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send(self, alert_data: Dict) -> bool:
        """Send alert to Slack"""
        try:
            severity = alert_data.get('severity', 'warning').lower()
            color_map = {
                'critical': '#FF0000',
                'warning': '#FFA500',
                'info': '#0099FF'
            }
            
            payload = {
                'attachments': [{
                    'color': color_map.get(severity, '#0099FF'),
                    'title': alert_data.get('title', 'Network Alert'),
                    'text': alert_data.get('message', ''),
                    'fields': [
                        {'title': 'Device', 'value': alert_data.get('device_id', 'N/A'), 'short': True},
                        {'title': 'Severity', 'value': severity.upper(), 'short': True},
                        {'title': 'Metric', 'value': alert_data.get('metric_name', 'N/A'), 'short': True},
                        {'title': 'Value', 'value': str(alert_data.get('metric_value', 'N/A')), 'short': True},
                    ],
                    'timestamp': int(datetime.utcnow().timestamp())
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        
        except Exception as e:
            print(f"Slack alert failed: {e}")
            return False


class EmailAlertHandler(AlertHandler):
    """Send alerts via Email (using SendGrid)"""
    
    def __init__(self, api_key: str, from_email: str):
        self.api_key = api_key
        self.from_email = from_email
    
    def send(self, alert_data: Dict) -> bool:
        """Send alert via email"""
        try:
            to_emails = alert_data.get('recipients', [])
            if not to_emails:
                return False
            
            html_content = f"""
            <h2>{alert_data.get('title', 'Network Alert')}</h2>
            <p><strong>Severity:</strong> {alert_data.get('severity', 'Unknown').upper()}</p>
            <p><strong>Device:</strong> {alert_data.get('device_id', 'N/A')}</p>
            <p><strong>Metric:</strong> {alert_data.get('metric_name', 'N/A')}</p>
            <p><strong>Value:</strong> {alert_data.get('metric_value', 'N/A')} {alert_data.get('unit', '')}</p>
            <p><strong>Message:</strong> {alert_data.get('message', '')}</p>
            <p><strong>Timestamp:</strong> {datetime.utcnow().isoformat()}</p>
            """
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'personalizations': [{'to': [{'email': email} for email in to_emails]}],
                'from': {'email': self.from_email},
                'subject': alert_data.get('title', 'Network Alert'),
                'content': [{'type': 'text/html', 'value': html_content}]
            }
            
            response = requests.post(
                'https://api.sendgrid.com/v3/mail/send',
                headers=headers,
                json=payload,
                timeout=10
            )
            return response.status_code == 202
        
        except Exception as e:
            print(f"Email alert failed: {e}")
            return False


class PagerDutyAlertHandler(AlertHandler):
    """Send alerts to PagerDuty"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.pagerduty.com'
    
    def send(self, alert_data: Dict) -> bool:
        """Send alert to PagerDuty"""
        try:
            severity_map = {
                'critical': 'critical',
                'warning': 'warning',
                'info': 'info'
            }
            
            payload = {
                'routing_key': self.api_key,
                'event_action': 'trigger',
                'dedup_key': alert_data.get('alert_id', str(datetime.utcnow().timestamp())),
                'payload': {
                    'summary': alert_data.get('title', 'Network Alert'),
                    'severity': severity_map.get(alert_data.get('severity', 'warning'), 'warning'),
                    'source': alert_data.get('device_id', 'Network-Monitor'),
                    'component': alert_data.get('metric_name', 'Unknown'),
                    'custom_details': {
                        'message': alert_data.get('message'),
                        'value': alert_data.get('metric_value'),
                        'unit': alert_data.get('unit'),
                    }
                }
            }
            
            response = requests.post(
                'https://events.pagerduty.com/v2/enqueue',
                json=payload,
                timeout=10
            )
            return response.status_code == 202
        
        except Exception as e:
            print(f"PagerDuty alert failed: {e}")
            return False


class TeamsAlertHandler(AlertHandler):
    """Send alerts to Microsoft Teams"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send(self, alert_data: Dict) -> bool:
        """Send alert to Microsoft Teams"""
        try:
            severity = alert_data.get('severity', 'warning').lower()
            color_map = {
                'critical': 'FF0000',
                'warning': 'FFA500',
                'info': '0099FF'
            }
            
            payload = {
                '@type': 'MessageCard',
                '@context': 'https://schema.org/extensions',
                'summary': alert_data.get('title', 'Network Alert'),
                'themeColor': color_map.get(severity, '0099FF'),
                'sections': [{
                    'activityTitle': alert_data.get('title', 'Network Alert'),
                    'facts': [
                        {'name': 'Device', 'value': alert_data.get('device_id', 'N/A')},
                        {'name': 'Severity', 'value': severity.upper()},
                        {'name': 'Metric', 'value': alert_data.get('metric_name', 'N/A')},
                        {'name': 'Value', 'value': str(alert_data.get('metric_value', 'N/A'))},
                    ],
                    'text': alert_data.get('message', '')
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        
        except Exception as e:
            print(f"Teams alert failed: {e}")
            return False


class WebhookAlertingService:
    """Service to manage multiple alerting channels"""
    
    def __init__(self):
        self.handlers: Dict[str, AlertHandler] = {}
    
    def add_handler(self, name: str, handler: AlertHandler):
        """Add an alert handler"""
        self.handlers[name] = handler
    
    def remove_handler(self, name: str):
        """Remove an alert handler"""
        if name in self.handlers:
            del self.handlers[name]
    
    def send_alert(self, alert_data: Dict) -> Dict[str, bool]:
        """
        Send alert to all registered handlers
        
        Args:
            alert_data: Dictionary containing:
                - title: Alert title
                - message: Alert message
                - severity: 'critical', 'warning', or 'info'
                - device_id: Affected device
                - metric_name: Affected metric
                - metric_value: Current value
                - unit: Metric unit
        
        Returns:
            Dictionary mapping handler names to success status
        """
        results = {}
        for name, handler in self.handlers.items():
            try:
                results[name] = handler.send(alert_data)
            except Exception as e:
                print(f"Handler {name} error: {e}")
                results[name] = False
        
        return results
    
    async def send_alert_async(self, alert_data: Dict) -> Dict[str, bool]:
        """Send alert asynchronously to all handlers"""
        tasks = []
        for name, handler in self.handlers.items():
            task = asyncio.to_thread(handler.send, alert_data)
            tasks.append((name, task))
        
        results = {}
        for name, task in tasks:
            try:
                results[name] = await task
            except Exception as e:
                print(f"Handler {name} error: {e}")
                results[name] = False
        
        return results


# Alert escalation policies
ESCALATION_POLICIES = {
    'critical': {
        'handlers': ['pagerduty', 'slack', 'email'],
        'wait_before_next_level': 15  # minutes
    },
    'warning': {
        'handlers': ['slack', 'email'],
        'wait_before_next_level': 30
    },
    'info': {
        'handlers': ['slack'],
        'wait_before_next_level': 60
    }
}
