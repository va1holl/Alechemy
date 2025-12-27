"""
Tests for accounts app - User registration, authentication, and profiles.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTests(TestCase):
    """Tests for custom User model."""
    
    def test_create_user_with_email(self):
        """Test creating a user with email."""
        email = "test@example.com"
        password = "testpass123!"
        user = User.objects.create_user(username=email, email=email, password=password)
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        email = "admin@example.com"
        password = "adminpass123!"
        user = User.objects.create_superuser(username=email, email=email, password=password)
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_email_is_unique(self):
        """Test that email must be unique."""
        email = "test@example.com"
        User.objects.create_user(username="user1", email=email, password="test123!")
        
        with self.assertRaises(Exception):
            User.objects.create_user(username="user2", email=email, password="test123!")
    
    def test_user_string_representation(self):
        """Test user __str__ method."""
        email = "test@example.com"
        user = User.objects.create_user(username=email, email=email, password="test123!")
        
        self.assertEqual(str(user), email)


class UserRegistrationTests(TestCase):
    """Tests for user registration."""
    
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('accounts:signup')
    
    def test_signup_page_loads(self):
        """Test that signup page loads correctly."""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')
    
    def test_signup_with_valid_data(self):
        """Test registration with valid data."""
        data = {
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = self.client.post(self.signup_url, data)
        
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        
        # User should be created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_signup_password_mismatch(self):
        """Test registration fails with password mismatch."""
        data = {
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass123!',
        }
        response = self.client.post(self.signup_url, data)
        
        self.assertEqual(response.status_code, 200)  # Stays on page
        self.assertFalse(User.objects.filter(email='newuser@example.com').exists())
    
    def test_signup_duplicate_email(self):
        """Test registration fails with duplicate email."""
        User.objects.create_user(username='existing', email='existing@example.com', password='test123!')
        
        data = {
            'email': 'existing@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = self.client.post(self.signup_url, data)
        
        self.assertEqual(response.status_code, 200)  # Stays on page with error


class UserLoginTests(TestCase):
    """Tests for user login."""
    
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login')
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123!'
        )
    
    def test_login_page_loads(self):
        """Test that login page loads correctly."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
    
    def test_login_with_valid_credentials(self):
        """Test login with valid email and password."""
        data = {
            'username': 'test@example.com',  # Django uses 'username' field
            'password': 'testpass123!',
        }
        response = self.client.post(self.login_url, data)
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
    
    def test_login_with_invalid_password(self):
        """Test login fails with wrong password."""
        data = {
            'username': 'test@example.com',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, 200)  # Stays on page


class ProfileTests(TestCase):
    """Tests for user profile."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123!'
        )
        self.client.login(username='test@example.com', password='testpass123!')
    
    def test_profile_exists_after_user_creation(self):
        """Test that profile is created automatically with user."""
        self.assertTrue(hasattr(self.user, 'profile'))
    
    def test_profile_page_requires_login(self):
        """Test that profile page requires authentication."""
        self.client.logout()
        response = self.client.get(reverse('pages:me'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_profile_page_accessible_when_logged_in(self):
        """Test that profile page is accessible for logged in user."""
        response = self.client.get(reverse('pages:me'))
        self.assertEqual(response.status_code, 200)


class PasswordResetTests(TestCase):
    """Tests for password reset functionality."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123!'
        )
    
    def test_password_reset_page_loads(self):
        """Test that password reset page loads."""
        response = self.client.get(reverse('accounts:password_reset'))
        self.assertEqual(response.status_code, 200)
    
    def test_password_reset_with_valid_email(self):
        """Test password reset request with valid email."""
        data = {'email': 'test@example.com'}
        response = self.client.post(reverse('accounts:password_reset'), data)
        
        # Should redirect to done page
        self.assertEqual(response.status_code, 302)
