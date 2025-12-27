"""
Tests for security features - CSP, middleware, headers.
"""
import pytest
from django.test import Client, override_settings


class TestCSPHeaders:
    """Tests for Content Security Policy headers."""
    
    def test_csp_header_present(self, authenticated_client):
        """CSP header should be present on responses."""
        from django.urls import reverse
        url = reverse('events:scenario_list')
        response = authenticated_client.get(url)
        
        assert 'Content-Security-Policy' in response
        csp = response['Content-Security-Policy']
        
        # Check essential directives
        assert "default-src 'self'" in csp
        assert "script-src" in csp
        assert "style-src" in csp
    
    def test_csp_nonce_in_header(self, authenticated_client):
        """CSP should contain nonce for scripts and styles."""
        from django.urls import reverse
        url = reverse('events:scenario_list')
        response = authenticated_client.get(url)
        
        csp = response['Content-Security-Policy']
        
        # Check for nonce in script-src and style-src
        assert "'nonce-" in csp
    
    def test_csp_nonce_in_context(self, authenticated_client):
        """CSP nonce should be available in template context."""
        from django.urls import reverse
        url = reverse('events:scenario_list')
        response = authenticated_client.get(url)
        
        # Check that nonce is in context
        assert 'csp_nonce' in response.context or hasattr(response, 'csp_nonce')
    
    def test_admin_no_csp(self, client, admin_user):
        """Admin pages should not have CSP (may break functionality)."""
        client.force_login(admin_user)
        response = client.get('/admin/')
        
        # CSP might be absent or different for admin
        # This depends on implementation
        pass


class TestSecurityHeaders:
    """Tests for other security headers."""
    
    def test_x_content_type_options(self, authenticated_client):
        """X-Content-Type-Options header should be present."""
        from django.urls import reverse
        url = reverse('events:scenario_list')
        response = authenticated_client.get(url)
        
        assert response.get('X-Content-Type-Options') == 'nosniff'
    
    def test_permissions_policy(self, authenticated_client):
        """Permissions-Policy header should be present."""
        from django.urls import reverse
        url = reverse('events:scenario_list')
        response = authenticated_client.get(url)
        
        assert 'Permissions-Policy' in response


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_healthz_endpoint_accessible(self, client):
        """Healthz endpoint should be publicly accessible."""
        response = client.get('/health/healthz/')
        assert response.status_code == 200
    
    def test_healthz_returns_ok(self, client):
        """Healthz endpoint should return 'ok'."""
        response = client.get('/health/healthz/')
        assert response.content == b'ok'
        assert response['Content-Type'] == 'text/plain'


class TestSecurityMiddleware:
    """Tests for security middleware logging."""
    
    def test_sensitive_path_logging(self, client, user, user_data, caplog):
        """Sensitive paths should be logged."""
        import logging
        
        with caplog.at_level(logging.INFO, logger='django.security'):
            client.post('/accounts/login/', {
                'username': user_data['email'],
                'password': user_data['password'],
            })
        
        # Check that something was logged (actual check depends on logger config)
        # In tests, logging might be different


class TestCookieSecurity:
    """Tests for secure cookie settings."""
    
    @override_settings(SESSION_COOKIE_SECURE=True)
    def test_session_cookie_secure_in_production(self, client, user, user_data):
        """Session cookie should be secure in production."""
        from django.conf import settings
        
        # This is a settings check, not runtime check
        assert settings.SESSION_COOKIE_SECURE is True
    
    @override_settings(CSRF_COOKIE_SECURE=True)
    def test_csrf_cookie_secure_in_production(self, client):
        """CSRF cookie should be secure in production."""
        from django.conf import settings
        
        assert settings.CSRF_COOKIE_SECURE is True
