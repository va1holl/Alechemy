"""
API URL configuration for accounts app - JWT authentication endpoints.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .api_views import (
    CustomTokenObtainPairView,
    RegisterAPIView,
    UserProfileAPIView,
    PasswordChangeAPIView,
    LogoutAPIView,
    verify_token,
)

app_name = 'accounts_api'

urlpatterns = [
    # JWT Token endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Authentication endpoints
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    
    # User endpoints
    path('me/', UserProfileAPIView.as_view(), name='profile'),
    path('password/change/', PasswordChangeAPIView.as_view(), name='password_change'),
    path('verify/', verify_token, name='verify'),
]
