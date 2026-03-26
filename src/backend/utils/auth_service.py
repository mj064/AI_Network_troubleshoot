"""
JWT Authentication Module
Handles user authentication, token generation, and validation
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from typing import Dict, Tuple, Optional
import os

# Default secret key (should be set in environment)
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-super-secret-key-change-in-production')
TOKEN_EXPIRY_HOURS = int(os.getenv('TOKEN_EXPIRY_HOURS', 24))


class AuthenticationService:
    """Handle user authentication and JWT tokens"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_token(user_id: str, username: str, role: str) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token
    
    @staticmethod
    def get_token_from_request() -> Optional[str]:
        """Extract token from Authorization header"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        return None


def require_login(f):
    """Decorator: Require valid JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = AuthenticationService.get_token_from_request()
        
        if not token:
            return jsonify({'error': 'Missing authentication token'}), 401
        
        payload = AuthenticationService.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Store user info in request context
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function


def login_route(db_session):
    """Login endpoint factory - returns Flask route function"""
    def route():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Query user from database (requires User model in production)
        # For now, return sample token
        user_id = 'user_001'
        role = 'admin'
        
        token = AuthenticationService.generate_token(user_id, username, role)
        return jsonify({
            'token': token,
            'user_id': user_id,
            'username': username,
            'role': role,
            'expires_in_hours': TOKEN_EXPIRY_HOURS
        })
    
    return route
