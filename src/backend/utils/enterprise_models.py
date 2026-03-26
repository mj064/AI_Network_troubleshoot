"""
PostgreSQL Database Models - Extended Enterprise Version
Includes User Management, Audit Logging, Webhooks, SNMP Devices, etc.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, Enum, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()


# Association tables
snmp_device_metrics = Table(
    'snmp_device_metrics',
    Base.metadata,
    Column('snmp_device_id', Integer, ForeignKey('snmp_devices.id')),
    Column('metric_id', Integer, ForeignKey('network_metrics.id'))
)


# ============ MULTI-TENANCY ============

class Tenant(Base):
    """Organization/SaaS tenant"""
    __tablename__ = 'tenants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    type = Column(String(50), default='network')  # network, service_provider, enterprise
    api_key = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============ USER MANAGEMENT ============

class User(Base):
    """User account for system access"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default='viewer')  # admin, engineer, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    audit_logs = relationship('AuditLog', back_populates='user')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


# ============ AUDIT LOGGING ============

class AuditLog(Base):
    """Track all user actions for compliance"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(100), nullable=False)  # create, read, update, delete
    resource_type = Column(String(50), nullable=False)  # device, metric, incident
    resource_id = Column(String(100))
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(50))
    
    user = relationship('User', back_populates='audit_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address
        }


# ============ SNMP DEVICE MANAGEMENT ============

class SNMPDevice(Base):
    """SNMP-enabled network device for real monitoring"""
    __tablename__ = 'snmp_devices'
    
    id = Column(Integer, primary_key=True)
    ip_address = Column(String(50), unique=True, nullable=False)
    hostname = Column(String(255))
    community_string = Column(String(255), nullable=False)
    snmp_version = Column(String(10), default='2c')  # 2c, 3
    vendor = Column(String(100))
    location = Column(String(255))
    is_active = Column(Boolean, default=True)
    last_poll = Column(DateTime)
    poll_interval_minutes = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'hostname': self.hostname,
            'vendor': self.vendor,
            'location': self.location,
            'is_active': self.is_active,
            'last_poll': self.last_poll.isoformat() if self.last_poll else None,
            'poll_interval_minutes': self.poll_interval_minutes
        }


# ============ WEBHOOK MANAGEMENT ============

class Webhook(Base):
    """Webhook endpoint for alert routing"""
    __tablename__ = 'webhooks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    url = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # slack, email, pagerduty, teams, custom
    is_active = Column(Boolean, default=True)
    alert_severity = Column(String(50))  # critical, warning, info, or all
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'type': self.type,
            'is_active': self.is_active,
            'alert_severity': self.alert_severity
        }


# ============ ALERT CONFIGURATION ============

class AlertRule(Base):
    """Configuration for metric alerting"""
    __tablename__ = 'alert_rules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    metric_name = Column(String(100), nullable=False)
    condition = Column(String(50), nullable=False)  # greater_than, less_than, equals
    threshold_value = Column(Float, nullable=False)
    severity = Column(String(50), nullable=False)  # critical, warning, info
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'metric_name': self.metric_name,
            'condition': self.condition,
            'threshold_value': self.threshold_value,
            'severity': self.severity,
            'enabled': self.enabled
        }


# ============ EXTENDED NETWORK MODELS ============

class NetworkDevice(Base):
    """Network device (updated for extended data)"""
    __tablename__ = 'network_devices'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(50), unique=True, nullable=False)
    device_name = Column(String(255), nullable=False)
    device_type = Column(String(100))  # Router, Switch, Firewall, etc.
    ip_address = Column(String(50))
    vendor = Column(String(100))
    location = Column(String(255))
    lab_network = Column(String(100))
    status = Column(String(50), default='UP')
    uptime_hours = Column(Integer, default=0)
    last_seen = Column(DateTime)
    snmp_enabled = Column(Boolean, default=False)
    snmp_device_id = Column(Integer, ForeignKey('snmp_devices.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    metrics = relationship('NetworkMetric', back_populates='device')
    incidents = relationship('NetworkIncident', secondary='incident_devices', back_populates='devices')
    snmp_device = relationship('SNMPDevice')
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'ip_address': self.ip_address,
            'vendor': self.vendor,
            'location': self.location,
            'lab_network': self.lab_network,
            'status': self.status,
            'uptime_hours': self.uptime_hours,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'snmp_enabled': self.snmp_enabled
        }


class NetworkMetric(Base):
    """Network performance metric"""
    __tablename__ = 'network_metrics'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('network_devices.id'))
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    unit = Column(String(50))
    status = Column(String(50))  # OK, WARNING, CRITICAL
    threshold_warn = Column(Float)
    threshold_crit = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    device = relationship('NetworkDevice', back_populates='metrics')
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'unit': self.unit,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class NetworkIncident(Base):
    """Network incident/ticket"""
    __tablename__ = 'network_incidents'
    
    id = Column(Integer, primary_key=True)
    ticket_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(String(50))  # P1, P2, P3, P4, P5
    status = Column(String(50), default='OPEN')  # OPEN, CLOSED, RESOLVED
    root_cause = Column(Text)
    symptom_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    devices = relationship('NetworkDevice', secondary='incident_devices', back_populates='incidents')
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'title': self.title,
            'severity': self.severity,
            'status': self.status,
            'symptom_summary': self.symptom_summary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


# Association table for incident-device relationship
incident_devices = Table(
    'incident_devices',
    Base.metadata,
    Column('incident_id', Integer, ForeignKey('network_incidents.id')),
    Column('device_id', Integer, ForeignKey('network_devices.id'))
)


class SystemLog(Base):
    """System operation logs"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True)
    level = Column(String(20))  # INFO, WARNING, ERROR, CRITICAL
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class NetworkTopology(Base):
    """Network topology/connections between devices"""
    __tablename__ = 'network_topology'
    
    id = Column(Integer, primary_key=True)
    source_device_id = Column(String(50))
    destination_device_id = Column(String(50))
    connection_type = Column(String(50))  # ethernet, bgp, mpls, etc.
    bandwidth_mbps = Column(Float)
    status = Column(String(50), default='UP')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_device_id': self.source_device_id,
            'destination_device_id': self.destination_device_id,
            'connection_type': self.connection_type,
            'bandwidth_mbps': self.bandwidth_mbps,
            'status': self.status
        }


# Database Manager
class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        # Create all tables
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        return self.Session()
    
    def init_db(self):
        """Initialize database with all tables"""
        Base.metadata.create_all(self.engine)
    
    def drop_all(self):
        """Drop all tables (development only)"""
        Base.metadata.drop_all(self.engine)
