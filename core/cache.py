"""
Caching utilities for performance optimization
"""
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json


def cache_key(*args, **kwargs):
    """
    Generate cache key from arguments

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        str: Cache key
    """
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached_view(timeout=300, key_prefix="view"):
    """
    Decorator to cache view results

    Args:
        timeout: Cache timeout in seconds (default 5 minutes)
        key_prefix: Prefix for cache key

    Usage:
        @cached_view(timeout=600, key_prefix="products")
        def my_view(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Build cache key from view name, args, kwargs, and query params
            cache_key_parts = [
                key_prefix,
                func.__name__,
                str(args),
                str(kwargs),
                str(request.GET.dict())
            ]
            key = cache_key(*cache_key_parts)

            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result

            # Execute view and cache result
            result = func(request, *args, **kwargs)
            cache.set(key, result, timeout)

            return result
        return wrapper
    return decorator


class CacheManager:
    """Manager for common caching operations"""

    # Cache timeouts (in seconds)
    CACHE_SHORT = 300  # 5 minutes
    CACHE_MEDIUM = 1800  # 30 minutes
    CACHE_LONG = 3600  # 1 hour
    CACHE_VERY_LONG = 86400  # 24 hours

    @staticmethod
    def get_product_cache_key(product_id):
        """Get cache key for product"""
        return f"product:{product_id}"

    @staticmethod
    def get_category_cache_key(category_id):
        """Get cache key for category"""
        return f"category:{category_id}"

    @staticmethod
    def get_products_list_cache_key(**filters):
        """Get cache key for products list"""
        return f"products:list:{cache_key(**filters)}"

    @staticmethod
    def get_categories_list_cache_key():
        """Get cache key for categories list"""
        return "categories:list"

    @staticmethod
    def get_cart_cache_key(user_id):
        """Get cache key for user's cart"""
        return f"cart:user:{user_id}"

    @staticmethod
    def get_coupon_cache_key(code):
        """Get cache key for coupon"""
        return f"coupon:{code}"

    @staticmethod
    def invalidate_product_cache(product_id):
        """Invalidate product cache"""
        cache.delete(CacheManager.get_product_cache_key(product_id))
        # Also invalidate products list cache
        cache.delete_pattern("products:list:*")

    @staticmethod
    def invalidate_category_cache(category_id):
        """Invalidate category cache"""
        cache.delete(CacheManager.get_category_cache_key(category_id))
        cache.delete(CacheManager.get_categories_list_cache_key())

    @staticmethod
    def invalidate_cart_cache(user_id):
        """Invalidate cart cache"""
        cache.delete(CacheManager.get_cart_cache_key(user_id))

    @staticmethod
    def invalidate_coupon_cache(code):
        """Invalidate coupon cache"""
        cache.delete(CacheManager.get_coupon_cache_key(code))


def cache_product(timeout=CacheManager.CACHE_MEDIUM):
    """
    Decorator to cache product-related functions

    Args:
        timeout: Cache timeout in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(product_id, *args, **kwargs):
            key = CacheManager.get_product_cache_key(product_id)
            result = cache.get(key)

            if result is None:
                result = func(product_id, *args, **kwargs)
                cache.set(key, result, timeout)

            return result
        return wrapper
    return decorator


def cache_categories(timeout=CacheManager.CACHE_LONG):
    """
    Decorator to cache categories list

    Args:
        timeout: Cache timeout in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = CacheManager.get_categories_list_cache_key()
            result = cache.get(key)

            if result is None:
                result = func(*args, **kwargs)
                cache.set(key, result, timeout)

            return result
        return wrapper
    return decorator
