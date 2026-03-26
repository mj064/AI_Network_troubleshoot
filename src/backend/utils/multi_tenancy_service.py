"""
Multi-Tenancy Module
Support multiple organizations/networks with isolated data
"""

from typing import Dict, Optional, List
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from src.backend.app.production_models import NetworkDevice, NetworkMetric
from src.backend.utils.enterprise_models import Tenant


class TenantManager:
    """Manage multiple tenants (organizations/networks)"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def create_tenant(self, org_name: str, org_type: str = 'network') -> Optional[Dict]:
        """
        Create new tenant
        
        Args:
            org_name: Organization name
            org_type: Type of organization (network, service_provider, enterprise)
            
        Returns:
            Tenant dictionary with ID and API key
        """
        try:
            from src.backend.utils.enterprise_models import Tenant
            
            import secrets
            api_key = secrets.token_urlsafe(32)
            
            tenant = Tenant(
                name=org_name,
                type=org_type,
                api_key=api_key,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            self.db.add(tenant)
            self.db.commit()
            
            return {
                'tenant_id': tenant.id,
                'name': tenant.name,
                'api_key': api_key,
                'created_at': tenant.created_at.isoformat()
            }
        
        except Exception as e:
            self.db.rollback()
            print(f"Tenant creation failed: {e}")
            return None
    
    def get_tenant_by_api_key(self, api_key: str) -> Optional[Dict]:
        """Get tenant by API key"""
        try:
            from src.backend.utils.enterprise_models import Tenant
            
            tenant = self.db.query(Tenant).filter_by(api_key=api_key).first()
            
            if tenant:
                return {
                    'tenant_id': tenant.id,
                    'name': tenant.name,
                    'type': tenant.type,
                    'is_active': tenant.is_active
                }
        
        except Exception as e:
            print(f"Tenant lookup failed: {e}")
        
        return None
    
    def list_tenants(self) -> List[Dict]:
        """List all tenants"""
        try:
            from src.backend.utils.enterprise_models import Tenant
            
            tenants = self.db.query(Tenant).all()
            
            return [
                {
                    'tenant_id': t.id,
                    'name': t.name,
                    'type': t.type,
                    'is_active': t.is_active,
                    'device_count': len(t.devices) if hasattr(t, 'devices') else 0
                }
                for t in tenants
            ]
        
        except Exception as e:
            print(f"Tenant listing failed: {e}")
            return []
    
    def get_tenant_usage(self, tenant_id: int) -> Optional[Dict]:
        """Get usage statistics for a tenant"""
        try:
            from src.backend.utils.enterprise_models import Tenant, NetworkDevice, NetworkMetric
            
            tenant = self.db.query(Tenant).filter_by(id=tenant_id).first()
            
            if not tenant:
                return None
            
            device_count = self.db.query(NetworkDevice).filter_by(tenant_id=tenant_id).count()
            metric_count = self.db.query(NetworkMetric).join(NetworkDevice).filter(
                NetworkDevice.tenant_id == tenant_id
            ).count()
            
            return {
                'tenant_id': tenant_id,
                'name': tenant.name,
                'devices': device_count,
                'metrics_collected': metric_count,
                'users': len(tenant.users) if hasattr(tenant, 'users') else 0,
                'created_at': tenant.created_at.isoformat() if tenant.created_at else None
            }
        
        except Exception as e:
            print(f"Usage query failed: {e}")
            return None


class TenantDataIsolation:
    """Ensure data isolation between tenants"""
    
    @staticmethod
    def apply_tenant_filter(query, tenant_id: int):
        """Apply tenant filter to ORM query"""
        return query.filter_by(tenant_id=tenant_id)
    
    @staticmethod
    def scope_to_tenant(resource_dict: Dict, tenant_id: int) -> Dict:
        """Add tenant_id to resource"""
        resource_dict['tenant_id'] = tenant_id
        return resource_dict
    
    @staticmethod
    def verify_tenant_access(resource_tenant_id: int, request_tenant_id: int) -> bool:
        """Verify that requesting tenant has access to resource"""
        return resource_tenant_id == request_tenant_id


class BillingService:
    """Manage billing and usage-based pricing for SaaS model"""
    
    PRICING_TIERS = {
        'basic': {
            'monthly_cost': 99,
            'max_devices': 50,
            'max_metrics_per_day': 100000,
            'features': ['monitoring', 'basic_alerts']
        },
        'professional': {
            'monthly_cost': 299,
            'max_devices': 500,
            'max_metrics_per_day': 1000000,
            'features': ['monitoring', 'alerts', 'reporting', 'api_access']
        },
        'enterprise': {
            'monthly_cost': 999,
            'max_devices': None,  # Unlimited
            'max_metrics_per_day': None,  # Unlimited
            'features': ['*']  # All features
        }
    }
    
    def __init__(self, db_session):
        self.db = db_session
    
    def calculate_usage_cost(self, tenant_id: int, period_start: datetime, period_end: datetime) -> float:
        """Calculate overage charges for tenant"""
        try:
            from src.backend.utils.enterprise_models import Tenant, NetworkMetric
            
            tenant = self.db.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant:
                return 0
            
            # Get metrics in billing period
            metrics = self.db.query(NetworkMetric).join(NetworkDevice).filter(
                NetworkDevice.tenant_id == tenant_id,
                NetworkMetric.timestamp >= period_start,
                NetworkMetric.timestamp <= period_end
            ).count()
            
            tier = self.PRICING_TIERS.get(tenant.tier, self.PRICING_TIERS['basic'])
            base_cost = tier['monthly_cost']
            max_metrics = tier['max_metrics_per_day']
            days_in_period = (period_end - period_start).days or 1
            
            if max_metrics is None:
                return base_cost
            
            allowed_metrics = max_metrics * days_in_period
            overage_metrics = max(0, metrics - allowed_metrics)
            
            # $0.10 per 10k overage metrics
            overage_cost = (overage_metrics / 10000) * 0.10
            
            return round(base_cost + overage_cost, 2)
        
        except Exception as e:
            print(f"Cost calculation failed: {e}")
            return 0
    
    def get_tenant_quota(self, tenant_id: int) -> Dict:
        """Get current quota and usage for tenant"""
        try:
            from src.backend.utils.enterprise_models import Tenant, NetworkDevice, NetworkMetric
            
            tenant = self.db.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant:
                return {}
            
            tier = self.PRICING_TIERS.get(tenant.tier, self.PRICING_TIERS['basic'])
            
            current_devices = self.db.query(NetworkDevice).filter_by(tenant_id=tenant_id).count()
            current_metrics_month = self.db.query(NetworkMetric).join(NetworkDevice).filter(
                NetworkDevice.tenant_id == tenant_id,
                NetworkMetric.timestamp >= datetime.utcnow().replace(day=1)
            ).count()
            
            return {
                'tier': tenant.tier,
                'devices': {
                    'current': current_devices,
                    'limit': tier['max_devices']
                },
                'metrics_month': {
                    'current': current_metrics_month,
                    'limit': tier['max_metrics_per_day'] * 30
                },
                'features': tier['features']
            }
        
        except Exception as e:
            print(f"Quota check failed: {e}")
            return {}


class WhiteLabelService:
    """White-label branding and customization"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def set_branding(self, tenant_id: int, branding: Dict) -> bool:
        """Configure white-label branding for tenant"""
        try:
            from src.backend.utils.enterprise_models import Tenant
            
            tenant = self.db.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant:
                return False
            
            # Store branding configuration
            tenant.logo_url = branding.get('logo_url')
            tenant.primary_color = branding.get('primary_color', '#1e40af')
            tenant.app_name = branding.get('app_name', 'Network Operations')
            tenant.support_email = branding.get('support_email')
            
            self.db.commit()
            return True
        
        except Exception as e:
            self.db.rollback()
            print(f"Branding update failed: {e}")
            return False
    
    def get_branding(self, tenant_id: int) -> Dict:
        """Get branding configuration for tenant"""
        try:
            from src.backend.utils.enterprise_models import Tenant
            
            tenant = self.db.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant:
                return {}
            
            return {
                'logo_url': tenant.logo_url,
                'primary_color': tenant.primary_color or '#1e40af',
                'app_name': tenant.app_name or 'Network Operations',
                'support_email': tenant.support_email
            }
        
        except Exception as e:
            print(f"Branding retrieval failed: {e}")
            return {}


# Tenant model for database
class TenantModel:
    """Database model for multi-tenancy"""
    
    __tablename__ = 'tenants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    type = Column(String(50), default='network')  # network, service_provider, enterprise
    api_key = Column(String(255), unique=True, nullable=False)
    tier = Column(String(50), default='basic')  # basic, professional, enterprise
    is_active = Column(Boolean, default=True)
    
    # Branding
    logo_url = Column(String(255))
    primary_color = Column(String(20), default='#1e40af')
    app_name = Column(String(255), default='Network Operations')
    support_email = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    last_active = Column(DateTime)
    
    # Usage tracking
    monthly_cost = Column(Float, default=0)
    overage_cost = Column(Float, default=0)
