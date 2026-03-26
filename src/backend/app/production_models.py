"""
Database models for Network Troubleshooting Assistant
Production-ready models for real-world network data
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Text, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os

Base = declarative_base()

# Association table for many-to-many relationship between incidents and devices
incident_devices = Table(
    'incident_devices',
    Base.metadata,
    Column('incident_id', Integer, ForeignKey('network_incidents.id')),
    Column('device_id', Integer, ForeignKey('network_devices.id'))
)


class NetworkDevice(Base):
    """Database model for network devices"""
    __tablename__ = 'network_devices'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(50), unique=True, nullable=False, index=True)
    device_name = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)
    vendor = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    software_version = Column(String(50))
    ip_address = Column(String(15), nullable=False, index=True)
    mac_address = Column(String(17))
    location = Column(String(100))
    lab_network = Column(String(50), index=True)
    status = Column(String(20), default='UP')  # UP, DOWN, DEGRADED, ERROR
    uptime_hours = Column(Integer, default=0)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    metrics = relationship('NetworkMetric', back_populates='device', cascade='all, delete-orphan')
    incidents = relationship('NetworkIncident', secondary='incident_devices', back_populates='devices')
    logs = relationship('SystemLog', back_populates='device', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'vendor': self.vendor,
            'status': self.status,
            'ip_address': self.ip_address,
            'location': self.location,
            'lab_network': self.lab_network,
            'uptime_hours': self.uptime_hours,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }


class NetworkMetric(Base):
    """Database model for network metrics"""
    __tablename__ = 'network_metrics'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('network_devices.id'), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    unit = Column(String(20))
    threshold_warn = Column(Float)
    threshold_crit = Column(Float)
    status = Column(String(20), default='OK')  # OK, WARNING, CRITICAL
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    device = relationship('NetworkDevice', back_populates='metrics')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'device_id': self.device.device_id if self.device else None,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'unit': self.unit,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class NetworkIncident(Base):
    """Database model for network incidents"""
    __tablename__ = 'network_incidents'
    
    id = Column(Integer, primary_key=True)
    ticket_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    severity = Column(String(10), nullable=False)  # P1, P2, P3, P4
    status = Column(String(20), default='OPEN')  # OPEN, IN_PROGRESS, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)
    symptom_summary = Column(Text)
    root_cause = Column(Text)
    resolution_steps = Column(JSON)
    alerts_triggered = Column(JSON)  # List of alerts
    related_tickets = Column(JSON)  # List of related ticket IDs
    
    # Relationships
    devices = relationship('NetworkDevice', secondary=incident_devices, back_populates='incidents')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'ticket_id': self.ticket_id,
            'title': self.title,
            'severity': self.severity,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'description': self.description,
            'symptom_summary': self.symptom_summary
        }


class SystemLog(Base):
    """Database model for system logs"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('network_devices.id'), nullable=False)
    log_level = Column(String(10), nullable=False)  # INFO, WARN, ERROR, CRIT
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String(50))
    
    # Relationship
    device = relationship('NetworkDevice', back_populates='logs')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'device_id': self.device.device_id if self.device else None,
            'log_level': self.log_level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class NetworkTopology(Base):
    """Database model for network topology/links"""
    __tablename__ = 'network_topology'
    
    id = Column(Integer, primary_key=True)
    from_device_id = Column(String(50), ForeignKey('network_devices.device_id'), nullable=False)
    to_device_id = Column(String(50), ForeignKey('network_devices.device_id'), nullable=False)
    link_type = Column(String(50))  # BGP, OSPF, MPLS, Ethernet, etc.
    protocol = Column(String(50))
    bandwidth = Column(String(50))
    status = Column(String(20), default='UP')
    vlan = Column(JSON)


class AlertRule(Base):
    """Database model for custom alert rules"""
    __tablename__ = 'alert_rules'
    
    id = Column(Integer, primary_key=True)
    rule_name = Column(String(100), nullable=False)
    metric_name = Column(String(100), nullable=False)
    condition = Column(String(50))  # GREATER_THAN, LESS_THAN, EQUAL
    threshold_value = Column(Float, nullable=False)
    severity = Column(String(10))  # P1, P2, P3, P4
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self, database_url: str = None):
        """Initialize database connection"""
        if database_url is None:
            # Default to SQLite for development
            db_path = os.getenv('DATABASE_URL', 'sqlite:///network_troubleshoot.db')
        else:
            db_path = database_url
        
        self.engine = create_engine(db_path, echo=False)
        self.create_tables()
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Get database session"""
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=self.engine)
        return Session()
    
    def drop_all(self):
        """Drop all tables - use for testing only"""
        Base.metadata.drop_all(self.engine)
