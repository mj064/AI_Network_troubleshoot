"""
Redis Caching Module
Performance optimization with intelligent caching
"""

import redis
import json
from typing import Any, Optional, Callable
from datetime import timedelta
from functools import wraps


class CacheService:
    """Service for Redis-based caching"""
    
    def __init__(self, redis_url: str = 'redis://localhost:6379/0', ttl_seconds: int = 3600):
        """
        Initialize cache service
        
        Args:
            redis_url: Redis connection URL
            ttl_seconds: Default time-to-live in seconds
        """
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            self.available = True
        except Exception as e:
            print(f"Redis connection failed: {e}. Cache disabled.")
            self.redis_client = None
            self.available = False
        
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.available:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Set value in cache"""
        if not self.available:
            return False
        
        try:
            ttl = ttl_seconds or self.ttl_seconds
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
        
        return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.available:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
        
        return False
    
    def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.available:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Cache flush error: {e}")
        
        return 0
    
    def clear_all(self):
        """Clear entire cache"""
        if not self.available:
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
        
        return False
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        if not self.available:
            return {'status': 'offline'}
        
        try:
            info = self.redis_client.info()
            return {
                'status': 'online',
                'used_memory_mb': info.get('used_memory', 0) / (1024 * 1024),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands': info.get('total_commands_processed', 0),
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


def cache_result(ttl_seconds: int = 3600, key_prefix: str = ''):
    """
    Decorator to cache function results
    
    Usage:
        @cache_result(ttl_seconds=300, key_prefix='devices')
        def get_all_devices():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{json.dumps({
                'args': [str(a) for a in args],
                'kwargs': {k: str(v) for k, v in kwargs.items()}
            })}"
            
            # Try to get from cache
            cache = getattr(wrapper, '_cache', None)
            if cache:
                cached = cache.get(cache_key)
                if cached is not None:
                    return cached
            
            # Call original function
            result = func(*args, **kwargs)
            
            # Store in cache
            if cache:
                cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    
    return decorator


# Cache keys for common queries
CACHE_KEYS = {
    'devices_all': 'cache:devices:all',
    'devices_health': 'cache:devices:health',
    'incidents_open': 'cache:incidents:open',
    'incidents_recent': 'cache:incidents:recent',
    'metrics_critical': 'cache:metrics:critical',
    'metrics_top': 'cache:metrics:top',
    'health_score': 'cache:health:score',
    'reports': 'cache:reports:*',
}


class CachingStrategy:
    """Strategies for intelligent caching"""
    
    @staticmethod
    def get_cache_ttl(data_type: str) -> int:
        """Get appropriate TTL for different data types"""
        ttl_map = {
            'devices': 300,  # 5 minutes
            'metrics': 60,  # 1 minute (more volatile)
            'incidents': 120,  # 2 minutes
            'reports': 3600,  # 1 hour
            'analytics': 1800,  # 30 minutes
            'health_stats': 60,  # 1 minute
        }
        return ttl_map.get(data_type, 3600)
    
    @staticmethod
    def is_cache_worth_it(query_complexity: str) -> bool:
        """Determine if query is worth caching"""
        expensive_queries = ['complex_analytics', 'full_report_generation', 'large_dataset_query']
        return query_complexity in expensive_queries


# Preloading strategy for frequently accessed data
PRELOAD_STRATEGY = {
    'health_overview': {
        'ttl': 60,
        'refresh_interval': 30,
        'priority': 'high'
    },
    'device_summary': {
        'ttl': 300,
        'refresh_interval': 120,
        'priority': 'high'
    },
    'recent_incidents': {
        'ttl': 120,
        'refresh_interval': 60,
        'priority': 'medium'
    },
    'critical_metrics': {
        'ttl': 60,
        'refresh_interval': 30,
        'priority': 'high'
    }
}
