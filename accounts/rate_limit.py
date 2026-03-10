"""
Simple rate limiting utilities using Django's cache.
No external dependencies required.
"""
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponse
import time


def get_client_ip(request):
    """Extract client IP from request, considering proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip


def rate_limit(key_prefix, limit=5, period=60, block_time=300):
    """
    Rate limiting decorator using Django's cache.
    
    Args:
        key_prefix: Prefix for cache key (e.g., 'login', 'payment')
        limit: Maximum number of requests allowed in period
        period: Time window in seconds
        block_time: How long to block after limit exceeded (seconds)
    
    Returns:
        429 Too Many Requests if limit exceeded
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            # Create unique key based on IP and optional user
            ip = get_client_ip(request)
            user_id = request.user.id if request.user.is_authenticated else 'anon'
            cache_key = f'ratelimit:{key_prefix}:{ip}:{user_id}'
            block_key = f'ratelimit:blocked:{key_prefix}:{ip}:{user_id}'
            
            # Check if user is currently blocked
            if cache.get(block_key):
                return HttpResponse(
                    "Забагато спроб. Спробуйте пізніше.",
                    content_type="text/plain; charset=utf-8",
                    status=429
                )
            
            # Get current request count
            current = cache.get(cache_key, {'count': 0, 'start': time.time()})
            
            # Reset if period expired
            if time.time() - current['start'] > period:
                current = {'count': 0, 'start': time.time()}
            
            current['count'] += 1
            
            # Check if limit exceeded
            if current['count'] > limit:
                # Block the user/IP for block_time
                cache.set(block_key, True, block_time)
                cache.delete(cache_key)
                return HttpResponse(
                    f"Забагато спроб. Спробуйте через {block_time // 60} хвилин.",
                    content_type="text/plain; charset=utf-8",
                    status=429
                )
            
            # Update counter
            cache.set(cache_key, current, period + 1)
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped
    return decorator


# Convenient pre-configured decorators for common use cases
def rate_limit_login(view_func):
    """Rate limit for login attempts: 5 per minute, 5 min block."""
    return rate_limit('login', limit=5, period=60, block_time=300)(view_func)


def rate_limit_payment(view_func):
    """Rate limit for payment attempts: 3 per minute, 10 min block."""
    return rate_limit('payment', limit=3, period=60, block_time=600)(view_func)


def rate_limit_sensitive(view_func):
    """Rate limit for sensitive operations: 3 per 5 minutes, 15 min block."""
    return rate_limit('sensitive', limit=3, period=300, block_time=900)(view_func)


def rate_limit_api(view_func):
    """Rate limit for API calls: 60 per minute, 1 min block."""
    return rate_limit('api', limit=60, period=60, block_time=60)(view_func)
