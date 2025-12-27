"""
Serializers for accounts app - REST API and JWT authentication.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that adds additional user claims to JWT.
    """
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        
        # Add profile info if exists
        if hasattr(user, 'profile'):
            token['is_premium'] = user.profile.is_premium
            token['unique_tag'] = user.profile.unique_tag
        
        return token


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration and profile display.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'password_confirm', 'date_joined']
        read_only_fields = ['id', 'date_joined']
    
    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for authenticated user profile.
    """
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_active', 'date_joined', 'profile']
        read_only_fields = ['id', 'email', 'date_joined']
    
    def get_profile(self, obj):
        if hasattr(obj, 'profile'):
            return {
                'sex': obj.profile.sex,
                'weight_kg': obj.profile.weight_kg,
                'is_premium': obj.profile.is_premium,
                'unique_tag': obj.profile.unique_tag,
                'language': obj.profile.language,
                'is_adult_confirmed': obj.profile.is_adult_confirmed,
                'gdpr_consent': obj.profile.gdpr_consent,
            }
        return None


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        return data
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value
