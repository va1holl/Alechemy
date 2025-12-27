"""
REST API views for accounts app.
"""
import logging
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
)

User = get_user_model()
logger = logging.getLogger('accounts')


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view with additional logging.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Log successful login
            email = request.data.get('email', 'unknown')
            logger.info(f"JWT login successful for: {email}")
        else:
            # Log failed login
            email = request.data.get('email', 'unknown')
            logger.warning(f"JWT login failed for: {email}")
        
        return response


class RegisterAPIView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"New user registered via API: {user.email}")
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating user profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class PasswordChangeAPIView(APIView):
    """
    API endpoint for changing password.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            
            logger.info(f"Password changed via API for: {request.user.email}")
            
            return Response({
                'message': 'Password changed successfully.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """
    API endpoint for logout (blacklist refresh token).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                
                logger.info(f"User logged out via API: {request.user.email}")
                
                return Response({
                    'message': 'Logged out successfully.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Refresh token is required.'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Logout error for {request.user.email}: {str(e)}")
            return Response({
                'error': 'Invalid token.'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verify_token(request):
    """
    Verify that the token is valid and return user info.
    """
    user = request.user
    return Response({
        'valid': True,
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
        }
    })
