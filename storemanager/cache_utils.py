from django.core.cache import cache
from django.utils.encoding import force_str
from functools import wraps
import logging

# Set up logger
logger = logging.getLogger(__name__)

def cache_result(timeout=300, key_prefix=None, key_generator=None):
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
                
                # Handle args, including class methods where the first arg is 'self' or 'cls'
                actual_args = args
                if args:
                    # Check if the function is a method of a class
                    # This is a heuristic; might need refinement for complex cases
                    first_arg_is_instance_or_class = hasattr(args[0], func.__name__) and callable(getattr(args[0], func.__name__))
                    if first_arg_is_instance_or_class and (force_str(func.__module__) in str(type(args[0]))):
                         actual_args = args[1:] # Skip 'self' or 'cls'

                for arg in actual_args:
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
            # Ensure pattern is a string for Redis and other backends
            search_pattern = f"*{pattern}*" if "*" not in pattern else pattern

            keys_iterable = backend.keys(search_pattern)
            
            keys_to_delete = []
            for key in keys_iterable:
                if isinstance(key, bytes):
                    try:
                        keys_to_delete.append(key.decode('utf-8'))
                    except UnicodeDecodeError:
                        logger.warning(f"Could not decode cache key: {key}")
                        continue 
                else:
                    keys_to_delete.append(str(key))

            if keys_to_delete:
                cache.delete_many(keys_to_delete)
                keys_deleted = len(keys_to_delete)
            
            logger.debug(f"Invalidated {keys_deleted} keys matching pattern '{pattern}'")
        else:
            logger.warning(f"Cache backend does not support key iteration or 'keys' with pattern. Pattern invalidation for '{pattern}' skipped.")
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
        cache_data = {}
        keys_to_index = []
        for key, value in data.items():
            full_key = f"{prefix}:{key}"
            cache_data[full_key] = value
            keys_to_index.append(key)
        
        cache.set_many(cache_data, timeout)
        
        prefix_index_key = f"{prefix}:_index"
        cache.set(prefix_index_key, keys_to_index, timeout)
        
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
        
    This is more efficient than pattern matching for structured keys if an index exists.
    """
    try:
        prefix_index_key = f"{prefix}:_index"
        keys_in_index = cache.get(prefix_index_key, [])
        keys_deleted_count = 0
        
        if keys_in_index:
            full_keys_to_delete = [f"{prefix}:{key}" for key in keys_in_index]
            cache.delete_many(full_keys_to_delete)
            keys_deleted_count = len(full_keys_to_delete)
            
            cache.delete(prefix_index_key)
            logger.debug(f"Invalidated {keys_deleted_count} keys with prefix '{prefix}' using index")
            return

        backend = getattr(cache, '_cache', None)
        if hasattr(backend, 'keys'):
            pattern = f"{prefix}:*" 
            
            keys_iterable = backend.keys(pattern)
            keys_to_delete = []
            for key in keys_iterable:
                if isinstance(key, bytes):
                    try:
                        keys_to_delete.append(key.decode('utf-8'))
                    except UnicodeDecodeError:
                        logger.warning(f"Could not decode cache key for prefix invalidation: {key}")
                        continue
                else:
                    keys_to_delete.append(str(key))
            
            if keys_to_delete:
                cache.delete_many(keys_to_delete)
                keys_deleted_count = len(keys_to_delete)
                
            logger.debug(f"Invalidated {keys_deleted_count} keys with prefix '{prefix}' using pattern matching")
        else:
            logger.warning(f"Cache backend doesn't support key iteration for prefix invalidation and no index found for '{prefix}'")
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
        
    result = value_func()
    
    try:
        cache.set(key, result, timeout)
        logger.debug(f"Cached result for {key}, expires in {timeout}s")
    except Exception as e:
        logger.warning(f"Failed to cache result for {key}: {e}")
    
    return result
