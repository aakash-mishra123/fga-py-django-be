from django.core.cache import cache
from django.utils.encoding import force_str
from functools import wraps
import logging

# Set up logger
logger = logging.getLogger(__name__)

def cache_result(timeout=300, key_prefix=None, key_generator=None):
    """
    Cache the result of a function for a specified time.
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Optional prefix for cache key
        key_generator: Optional function that generates custom cache key
        
    Usage:
    @cache_result(timeout=60)  # Cache for 60 seconds
    def my_function(arg1, arg2):
        ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use key generator if provided, otherwise create a default key
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                # Create a unique cache key based on the function and arguments
                key_parts = []
                
                if key_prefix:
                    key_parts.append(key_prefix)
                else:
                    key_parts = [force_str(func.__module__), force_str(func.__name__)]
                
                for arg in args:
                    if hasattr(arg, 'id'):  # Handle objects with IDs like request.user
                        key_parts.append(f"id-{arg.id}")
                    else:
                        key_parts.append(force_str(arg))
                        
                for k, v in sorted(kwargs.items()):
                    key_parts.append(f"{force_str(k)}:{force_str(v)}")
            
                cache_key = ":".join(key_parts)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return result
                
            # If not in cache, call the function
            result = func(*args, **kwargs)
            
            # Store in cache
            try:
                cache.set(cache_key, result, timeout)
                logger.debug(f"Cached result for {cache_key}, expires in {timeout}s")
            except Exception as e:
                logger.warning(f"Failed to cache result for {cache_key}: {e}")
            
            return result
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern: str):
    """
    Invalidate all cache keys containing the given pattern.
    
    Args:
        pattern: String pattern to match in cache keys
        
    WARNING: Inefficient for some backends (like Redis without KEYS permission).
    Prefer structured key prefixes with explicit keys when possible.
    """
    try:
        backend = getattr(cache, '_cache', None)
        keys_deleted = 0
        
        if hasattr(backend, 'keys'):
            keys = backend.keys('*')
            for key in keys:
                decoded_key = key.decode() if isinstance(key, bytes) else key
                if pattern in decoded_key:
                    cache.delete(decoded_key)
                    keys_deleted += 1
            
            logger.debug(f"Invalidated {keys_deleted} keys matching pattern '{pattern}'")
        else:
            logger.warning(f"Cache backend does not support key iteration. Pattern invalidation for '{pattern}' skipped.")
    except Exception as e:
        logger.error(f"Error invalidating cache pattern '{pattern}': {e}")


def cache_with_prefix(prefix: str, data: dict, timeout=300):
    """
    Store multiple key-value pairs with a common prefix in cache.
    
    Args:
        prefix: Common prefix for all cache keys
        data: Dictionary of key-value pairs to cache
        timeout: Cache timeout in seconds
        
    Useful for batch caching related items (e.g., all addresses for a user)
    """
    try:
        for key, value in data.items():
            full_key = f"{prefix}:{key}"
            cache.set(full_key, value, timeout)
        
        # Also cache a prefix index to help with later invalidation
        prefix_index_key = f"{prefix}:_index"
        cache.set(prefix_index_key, list(data.keys()), timeout)
        
        logger.debug(f"Cached {len(data)} items with prefix '{prefix}'")
        return True
    except Exception as e:
        logger.error(f"Failed to cache data with prefix '{prefix}': {e}")
        return False


def invalidate_prefix(prefix: str):
    """
    Invalidate all cache entries that start with a specific prefix.
    
    Args:
        prefix: Common prefix for cache keys to invalidate
        
    This is more efficient than pattern matching for structured keys
    """
    try:
        # First try to get the index of keys for this prefix
        prefix_index_key = f"{prefix}:_index"
        keys = cache.get(prefix_index_key, [])
        keys_deleted = 0
        
        # Delete all keys in the index
        for key in keys:
            full_key = f"{prefix}:{key}"
            cache.delete(full_key)
            keys_deleted += 1
            
        # Delete the index itself
        cache.delete(prefix_index_key)
        
        # If we had an index, we're done
        if keys_deleted > 0:
            logger.debug(f"Invalidated {keys_deleted} keys with prefix '{prefix}' using index")
            return
        
        # Fallback: Try pattern matching if backend supports it
        backend = getattr(cache, '_cache', None)
        if hasattr(backend, 'keys'):
            pattern = f"{prefix}:*"
            keys = backend.keys(pattern)
            for key in keys:
                decoded_key = key.decode() if isinstance(key, bytes) else key
                cache.delete(decoded_key)
                keys_deleted += 1
                
            logger.debug(f"Invalidated {keys_deleted} keys with prefix '{prefix}' using pattern")
        else:
            logger.warning(f"Cache backend doesn't support prefix invalidation and no index found for '{prefix}'")
    except Exception as e:
        logger.error(f"Failed to invalidate prefix '{prefix}': {e}")

def get_cached_or_set(key, value_func, timeout=300):
    """
    Get a value from the cache or compute and store it if not available
    
    Args:
        key: Cache key to look up
        value_func: Function to call to compute the value if not in cache 
        timeout: Cache timeout in seconds
        
    Returns:
        Cached value or result of value_func
    """
    result = cache.get(key)
    if result is not None:
        logger.debug(f"Cache hit for {key}")
        return result
        
    # Not in cache, compute the value
    result = value_func()
    
    # Store in cache
    try:
        cache.set(key, result, timeout)
        logger.debug(f"Cached result for {key}, expires in {timeout}s")
    except Exception as e:
        logger.warning(f"Failed to cache result for {key}: {e}")
    
    return result
