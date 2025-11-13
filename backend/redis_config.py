"""
Redis Configuration for Caching and Session Management
Handles ML model caching, session storage, and real-time data
"""

import os
import redis
import json
from dotenv import load_dotenv

load_dotenv()

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_URL = os.getenv('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}')

# Redis Client
redis_client = None

def init_redis():
    """Initialize Redis client"""
    global redis_client
    
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD if REDIS_PASSWORD else None,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Test connection
        redis_client.ping()
        print(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        
        return redis_client
    except Exception as e:
        print(f"Redis initialization error: {e}")
        print("Redis features will be disabled")
        return None


def get_redis_client():
    """Get Redis client instance"""
    return redis_client


def is_redis_available():
    """Check if Redis is available"""
    if not redis_client:
        return False
    try:
        redis_client.ping()
        return True
    except:
        return False


# Cache Management Functions

def cache_set(key, value, ttl=3600):
    """
    Set a value in cache with TTL
    
    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized)
        ttl: Time to live in seconds (default 1 hour)
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not redis_client:
        return False
    
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        redis_client.setex(key, ttl, value)
        return True
    except Exception as e:
        print(f"Error setting cache: {e}")
        return False


def cache_get(key):
    """
    Get a value from cache
    
    Args:
        key: Cache key
        
    Returns:
        Cached value or None if not found
    """
    if not redis_client:
        return None
    
    try:
        value = redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None
    except Exception as e:
        print(f"Error getting cache: {e}")
        return None


def cache_delete(key):
    """
    Delete a value from cache
    
    Args:
        key: Cache key
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not redis_client:
        return False
    
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Error deleting cache: {e}")
        return False


def cache_exists(key):
    """
    Check if a key exists in cache
    
    Args:
        key: Cache key
        
    Returns:
        bool: True if exists, False otherwise
    """
    if not redis_client:
        return False
    
    try:
        return redis_client.exists(key) > 0
    except Exception as e:
        print(f"Error checking cache: {e}")
        return False


# Session Management Functions

def session_set(session_id, session_data, ttl=3600):
    """
    Store session data
    
    Args:
        session_id: Session identifier
        session_data: Session data dictionary
        ttl: Time to live in seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    key = f"session:{session_id}"
    return cache_set(key, session_data, ttl)


def session_get(session_id):
    """
    Retrieve session data
    
    Args:
        session_id: Session identifier
        
    Returns:
        dict: Session data or None if not found
    """
    key = f"session:{session_id}"
    return cache_get(key)


def session_delete(session_id):
    """
    Delete session data
    
    Args:
        session_id: Session identifier
        
    Returns:
        bool: True if successful, False otherwise
    """
    key = f"session:{session_id}"
    return cache_delete(key)


def session_update_ttl(session_id, ttl=3600):
    """
    Update session TTL
    
    Args:
        session_id: Session identifier
        ttl: New time to live in seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not redis_client:
        return False
    
    try:
        key = f"session:{session_id}"
        redis_client.expire(key, ttl)
        return True
    except Exception as e:
        print(f"Error updating session TTL: {e}")
        return False


# ML Model Cache Functions

def cache_model(model_id, model_data, ttl=3600):
    """
    Cache ML model data
    
    Args:
        model_id: Model identifier
        model_data: Model data (weights, parameters)
        ttl: Time to live in seconds (default 1 hour)
        
    Returns:
        bool: True if successful, False otherwise
    """
    key = f"ml_model:{model_id}"
    return cache_set(key, model_data, ttl)


def get_cached_model(model_id):
    """
    Retrieve cached ML model
    
    Args:
        model_id: Model identifier
        
    Returns:
        Model data or None if not found
    """
    key = f"ml_model:{model_id}"
    return cache_get(key)


# Behavioral Data Cache Functions

def cache_behavioral_profile(user_id, profile_data, ttl=3600):
    """
    Cache user behavioral profile
    
    Args:
        user_id: User identifier
        profile_data: Behavioral profile data
        ttl: Time to live in seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    key = f"behavioral_profile:{user_id}"
    return cache_set(key, profile_data, ttl)


def get_cached_behavioral_profile(user_id):
    """
    Retrieve cached behavioral profile
    
    Args:
        user_id: User identifier
        
    Returns:
        Behavioral profile data or None if not found
    """
    key = f"behavioral_profile:{user_id}"
    return cache_get(key)


# Context Score Cache Functions

def cache_context_score(request_id, context_data, ttl=300):
    """
    Cache contextual intelligence score
    
    Args:
        request_id: Request identifier
        context_data: Context evaluation data
        ttl: Time to live in seconds (default 5 minutes)
        
    Returns:
        bool: True if successful, False otherwise
    """
    key = f"context_score:{request_id}"
    return cache_set(key, context_data, ttl)


def get_cached_context_score(request_id):
    """
    Retrieve cached context score
    
    Args:
        request_id: Request identifier
        
    Returns:
        Context data or None if not found
    """
    key = f"context_score:{request_id}"
    return cache_get(key)


# Threat Prediction Cache Functions

def cache_threat_predictions(predictions, ttl=1800):
    """
    Cache threat predictions
    
    Args:
        predictions: List of threat predictions
        ttl: Time to live in seconds (default 30 minutes)
        
    Returns:
        bool: True if successful, False otherwise
    """
    key = "threat_predictions:latest"
    return cache_set(key, predictions, ttl)


def get_cached_threat_predictions():
    """
    Retrieve cached threat predictions
    
    Returns:
        List of predictions or None if not found
    """
    key = "threat_predictions:latest"
    return cache_get(key)


# Statistics Functions

def get_redis_stats():
    """
    Get Redis statistics
    
    Returns:
        dict: Redis statistics or None if failed
    """
    if not redis_client:
        return None
    
    try:
        info = redis_client.info()
        return {
            'version': info.get('redis_version'),
            'uptime_seconds': info.get('uptime_in_seconds'),
            'connected_clients': info.get('connected_clients'),
            'used_memory': info.get('used_memory_human'),
            'total_keys': redis_client.dbsize(),
            'hits': info.get('keyspace_hits', 0),
            'misses': info.get('keyspace_misses', 0)
        }
    except Exception as e:
        print(f"Error getting Redis stats: {e}")
        return None
