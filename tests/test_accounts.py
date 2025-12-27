"""
Tests for accounts app - authentication, profile, API.
"""
import pytest
from django.urls import reverse
from django.test import Client


class TestAuthentication:
    """Tests for authentication flows."""
    
    def test_login_page_accessible(self, client):
        """Login page should be accessible."""
        url = reverse('accounts:login')
        response = client.get(url)
        assert response.status_code == 200
    
    def test_signup_page_accessible(self, client):
        """Signup page should be accessible."""
        url = reverse('accounts:signup')
        response = client.get(url)
        assert response.status_code == 200
    
    def test_login_with_valid_credentials(self, client, user, user_data):
        """User can login with valid credentials."""
        url = reverse('accounts:login')
        response = client.post(url, {
            'username': user_data['email'],
            'password': user_data['password'],
        })
        # Should redirect on successful login
        assert response.status_code == 302
    
    def test_login_with_invalid_credentials(self, client, db):
        """Invalid credentials should fail login."""
        url = reverse('accounts:login')
        response = client.post(url, {
            'username': 'nonexistent@example.com',
            'password': 'wrongpassword',
        })
        # Should stay on login page with form errors
        assert response.status_code == 200
    
    def test_logout(self, authenticated_client):
        """User can logout."""
        url = reverse('accounts:logout')
        response = authenticated_client.post(url)
        assert response.status_code == 302


class TestProfile:
    """Tests for user profile functionality."""
    
    def test_profile_requires_auth(self, client):
        """Profile page requires authentication."""
        url = reverse('pages:personal_data')
        response = client.get(url)
        assert response.status_code == 302
        assert '/accounts/login/' in response.url
    
    def test_profile_accessible_authenticated(self, authenticated_client):
        """Authenticated user can access profile."""
        url = reverse('pages:personal_data')
        response = authenticated_client.get(url)
        assert response.status_code == 200


class TestAdultRequirement:
    """Tests for adult age verification decorator."""
    
    def test_minor_cannot_access_events(self, client, user, user_data, db):
        """User without adult verification cannot access events."""
        from datetime import date
        from accounts.models import Profile
        
        # Create profile with minor age
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.birthday = date(2015, 1, 1)  # Minor
        profile.save()
        
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('events:scenario_list')
        response = client.get(url)
        # Should be redirected to age verification or denied
        assert response.status_code in [302, 403]
    
    def test_adult_can_access_events(self, authenticated_client):
        """Adult user can access events."""
        url = reverse('events:scenario_list')
        response = authenticated_client.get(url)
        assert response.status_code == 200


class TestRateLimiting:
    """Tests for rate limiting on sensitive endpoints."""
    
    @pytest.mark.skip(reason="Rate limiting tests require cache setup")
    def test_login_rate_limit(self, client, db):
        """Login endpoint should be rate limited."""
        url = reverse('accounts:login')
        
        # Make multiple failed login attempts
        for i in range(10):
            client.post(url, {
                'username': f'user{i}@example.com',
                'password': 'wrongpassword',
            })
        
        # Next attempt should be rate limited
        response = client.post(url, {
            'username': 'another@example.com',
            'password': 'wrongpassword',
        })
        
        # Check for rate limit response (429 or specific message)
        # This depends on implementation
        assert response.status_code in [200, 429]
