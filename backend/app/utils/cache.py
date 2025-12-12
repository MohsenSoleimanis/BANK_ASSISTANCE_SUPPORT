"""
Caching utilities using Redis
"""
import json
import hashlib
from functools import wraps
from typing import Optional, Any, Callable
import redis
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Redis client
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis not available: {e}. Caching disabled.")
    redis_client = None


def cache_result(ttl: int = 3600):
    """
    Decorator to cache function results in Redis
    
    Args:
        ttl: Time to live in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not redis_client:
                return await func(*args, **kwargs)
            
            # Create cache key from function name and arguments
            key_data = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            try:
                # Try to get from cache
                cached = redis_client.get(cache_key)
                if cached:
                    logger.info(f"Cache hit for {func.__name__}")
                    return json.loads(cached)
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Store in cache
                redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(result)
                )
                
                return result
                
            except Exception as e:
                logger.error(f"Cache error: {e}")
                # If caching fails, still return result
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def clear_cache(pattern: str = "*"):
    """Clear cache entries matching pattern"""
    if redis_client:
        for key in redis_client.scan_iter(pattern):
            redis_client.delete(key)
