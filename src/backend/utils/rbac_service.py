"""
Role-Based Access Control (RBAC) Module
Manages permissions for different user roles
"""

from functools import wraps
from flask import request, jsonify, jsonify as flask_jsonify
from typing import List

# Define roles and their permissions
ROLE_PERMISSIONS = {
    'admin': [
        'read:devices', 'write:devices', 'delete:devices',
        'read:metrics', 'write:metrics', 'delete:metrics',
        'read:incidents', 'write:incidents', 'delete:incidents',
        'manage:users', 'manage:roles', 'view:audit_logs',
        'manage:alerts', 'manage:webhooks', 'manage:integrations',
        'manage:reports', 'manage:settings'
    ],
    'engineer': [
        'read:devices', 'write:devices',
        'read:metrics', 'write:metrics',
        'read:incidents', 'write:incidents',
        'view:audit_logs', 'manage:alerts'
    ],
    'viewer': [
        'read:devices',
        'read:metrics',
        'read:incidents',
        'view:audit_logs'
    ]
}


class RBACService:
    """Handle role-based access control"""
    
    @staticmethod
    def get_role_permissions(role: str) -> List[str]:
        """Get all permissions for a role"""
        return ROLE_PERMISSIONS.get(role, [])
    
    @staticmethod
    def has_permission(role: str, permission: str) -> bool:
        """Check if role has specific permission"""
        return permission in RBACService.get_role_permissions(role)
    
    @staticmethod
    def has_any_permission(role: str, permissions: List[str]) -> bool:
        """Check if role has any of the listed permissions"""
        role_perms = RBACService.get_role_permissions(role)
        return any(perm in role_perms for perm in permissions)
    
    @staticmethod
    def has_all_permissions(role: str, permissions: List[str]) -> bool:
        """Check if role has all listed permissions"""
        role_perms = RBACService.get_role_permissions(role)
        return all(perm in role_perms for perm in permissions)


def require_permission(*permissions):
    """
    Decorator: Require user to have specific permission(s)
    Usage: @require_permission('read:devices', 'write:devices')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated (should be chained with @require_login)
            if not hasattr(request, 'user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = request.user.get('role')
            
            # Check if user has any of the required permissions
            if not RBACService.has_any_permission(user_role, list(permissions)):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required': list(permissions),
                    'user_role': user_role
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_role(*allowed_roles):
    """
    Decorator: Require user to have specific role
    Usage: @require_role('admin', 'engineer')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = request.user.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient role privileges',
                    'required_roles': list(allowed_roles),
                    'user_role': user_role
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
