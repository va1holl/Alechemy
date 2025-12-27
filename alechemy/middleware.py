"""
Request logging middleware for monitoring and debugging.
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin

request_logger = logging.getLogger('django.request')
security_logger = logging.getLogger('django.security')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all incoming requests and their response times.
    """
    
    def process_request(self, request):
        """Store the start time when request comes in."""
        request._start_time = time.time()
        
        # Log request details
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
        request_logger.info(
            f"Request: {request.method} {request.path} | User: {user} | IP: {self.get_client_ip(request)}"
        )
    
    def process_response(self, request, response):
        """Log the response with duration."""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            duration_ms = round(duration * 1000, 2)
            
            # Log based on response status
            if response.status_code >= 500:
                request_logger.error(
                    f"Response: {response.status_code} | Duration: {duration_ms}ms | Path: {request.path}"
                )
            elif response.status_code >= 400:
                request_logger.warning(
                    f"Response: {response.status_code} | Duration: {duration_ms}ms | Path: {request.path}"
                )
            else:
                request_logger.info(
                    f"Response: {response.status_code} | Duration: {duration_ms}ms | Path: {request.path}"
                )
            
            # Log slow requests (> 1 second)
            if duration > 1.0:
                request_logger.warning(
                    f"Slow request detected: {request.method} {request.path} took {duration_ms}ms"
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
    Middleware to add Content-Security-Policy headers.
    Helps prevent XSS, clickjacking, and other code injection attacks.
    """
    
    def process_response(self, request, response):
        """Add CSP headers to response."""
        from django.conf import settings
        
        # Skip CSP for admin (may break some functionality)
        if request.path.startswith('/admin/'):
            return response
        
        # Build CSP directives
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://unpkg.com",
            "font-src 'self' https://fonts.gstatic.com data:",
            "img-src 'self' data: https: blob:",
            "connect-src 'self' https://unpkg.com https://api.openstreetmap.org https://*.tile.openstreetmap.org https://tile.openstreetmap.org",
            "frame-src 'self' https://www.google.com https://hcaptcha.com https://*.hcaptcha.com",
            "frame-ancestors 'self'",
            "form-action 'self'",
            "base-uri 'self'",
            "object-src 'none'",
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
        '/accounts/register/',
        '/accounts/password-reset/',
        '/admin/',
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
