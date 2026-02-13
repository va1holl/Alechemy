"""
Request logging middleware for monitoring and debugging.
Production optimized: logs only errors and slow requests.
"""
import logging
import secrets
import time
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

request_logger = logging.getLogger('django.request')
security_logger = logging.getLogger('django.security')

# Threshold for slow request logging (in seconds)
SLOW_REQUEST_THRESHOLD = float(getattr(settings, 'SLOW_REQUEST_THRESHOLD', 1.0))


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log requests.
    In production: only errors (4xx/5xx) and slow requests.
    In development: all requests.
    """
    
    def process_request(self, request):
        """Store the start time when request comes in."""
        request._start_time = time.time()
        
        # Only log all requests in DEBUG mode
        if settings.DEBUG:
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
            request_logger.debug(
                f"Request: {request.method} {request.path} | User: {user} | IP: {self.get_client_ip(request)}"
            )
    
    def process_response(self, request, response):
        """Log the response - only errors and slow requests in production."""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            duration_ms = round(duration * 1000, 2)
            
            # Always log server errors (5xx)
            if response.status_code >= 500:
                request_logger.error(
                    f"Response: {response.status_code} | Duration: {duration_ms}ms | "
                    f"Path: {request.path} | IP: {self.get_client_ip(request)}"
                )
            # Log client errors (4xx) at warning level
            elif response.status_code >= 400:
                request_logger.warning(
                    f"Response: {response.status_code} | Duration: {duration_ms}ms | Path: {request.path}"
                )
            # In debug mode, log all requests
            elif settings.DEBUG:
                request_logger.debug(
                    f"Response: {response.status_code} | Duration: {duration_ms}ms | Path: {request.path}"
                )
            
            # Always log slow requests
            if duration > SLOW_REQUEST_THRESHOLD:
                request_logger.warning(
                    f"Slow request: {request.method} {request.path} took {duration_ms}ms | "
                    f"IP: {self.get_client_ip(request)}"
                )
        
        return response
    
    def process_exception(self, request, exception):
        """Log unhandled exceptions."""
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
        request_logger.exception(
            f"Unhandled exception: {type(exception).__name__} | "
            f"Path: {request.path} | User: {user} | IP: {self.get_client_ip(request)}"
        )
    
    @staticmethod
    def get_client_ip(request):
        """Get the client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip


class ContentSecurityPolicyMiddleware(MiddlewareMixin):
    """
    Middleware to add Content-Security-Policy headers with nonce support.
    Uses nonce-based CSP for better security without unsafe-inline.
    """
    
    def process_request(self, request):
        """Generate a unique nonce for this request."""
        # Generate a cryptographically secure random nonce
        request.csp_nonce = secrets.token_urlsafe(32)
    
    def process_response(self, request, response):
        """Add CSP headers to response with nonce."""
        from django.conf import settings
        
        # Skip CSP for admin (may break some functionality)
        if request.path.startswith('/admin/'):
            return response
        
        # Get the nonce (generated in process_request)
        nonce = getattr(request, 'csp_nonce', secrets.token_urlsafe(32))
        
        if settings.DEBUG:
            # Development: more permissive for easier debugging
            # Still include nonce but keep unsafe-inline as fallback for hot reload etc
            csp_directives = [
                "default-src 'self'",
                f"script-src 'self' 'nonce-{nonce}' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com https://cdnjs.cloudflare.com",
                f"style-src 'self' 'nonce-{nonce}' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://unpkg.com",
                "font-src 'self' https://fonts.gstatic.com data:",
                "img-src 'self' data: https: blob:",
                "connect-src 'self' https://unpkg.com https://api.openstreetmap.org https://*.tile.openstreetmap.org https://tile.openstreetmap.org",
                "frame-src 'self' https://www.google.com https://hcaptcha.com https://*.hcaptcha.com",
                "frame-ancestors 'self'",
                "form-action 'self'",
                "base-uri 'self'",
                "object-src 'none'",
            ]
        else:
            # Production: strict nonce-based CSP (no unsafe-inline!)
            csp_directives = [
                "default-src 'self'",
                # Nonce-based: allows only scripts/styles with matching nonce
                f"script-src 'self' 'nonce-{nonce}' 'strict-dynamic' https://cdn.jsdelivr.net https://unpkg.com https://cdnjs.cloudflare.com",
                f"style-src 'self' 'nonce-{nonce}' https://fonts.googleapis.com https://cdn.jsdelivr.net https://unpkg.com",
                "font-src 'self' https://fonts.gstatic.com data:",
                "img-src 'self' data: https: blob:",
                "connect-src 'self' https://unpkg.com https://api.openstreetmap.org https://*.tile.openstreetmap.org https://tile.openstreetmap.org",
                "frame-src 'self' https://www.google.com https://hcaptcha.com https://*.hcaptcha.com",
                "frame-ancestors 'self'",
                "form-action 'self'",
                "base-uri 'self'",
                "object-src 'none'",
                "upgrade-insecure-requests",
            ]
        
        csp_header = "; ".join(csp_directives)
        response['Content-Security-Policy'] = csp_header
        
        # Also add X-Content-Type-Options if not already set
        if 'X-Content-Type-Options' not in response:
            response['X-Content-Type-Options'] = 'nosniff'
        
        # Add Permissions-Policy (formerly Feature-Policy)
        response['Permissions-Policy'] = (
            "accelerometer=(), camera=(), geolocation=(self), "
            "gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
        )
        
        return response


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log security-related events.
    """
    
    SENSITIVE_PATHS = [
        '/accounts/login/',
        '/accounts/signup/',
        '/accounts/password_reset/',
        '/admin/',
        '/api/',
    ]
    
    def process_request(self, request):
        """Log access to sensitive paths."""
        if any(request.path.startswith(path) for path in self.SENSITIVE_PATHS):
            security_logger.info(
                f"Sensitive path access: {request.method} {request.path} | "
                f"IP: {self.get_client_ip(request)} | "
                f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'unknown')[:100]}"
            )
    
    def process_response(self, request, response):
        """Log failed authentication attempts."""
        # Log failed login attempts
        if request.path == '/accounts/login/' and request.method == 'POST':
            if response.status_code == 200 and 'form' in str(response.content):
                # Failed login (form re-rendered with errors)
                security_logger.warning(
                    f"Failed login attempt | IP: {self.get_client_ip(request)} | "
                    f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'unknown')[:100]}"
                )
        
        # Log 403 and 401 responses
        if response.status_code in (401, 403):
            security_logger.warning(
                f"Access denied: {response.status_code} | Path: {request.path} | "
                f"IP: {self.get_client_ip(request)}"
            )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Get the client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
