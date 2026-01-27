"""
Custom authentication backend for email-based login
"""
from django.contrib.auth.backends import ModelBackend
from core.models import User


class EmailBackend(ModelBackend):
    """Authenticate using email instead of username"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate user by email and password"""
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None
        
        # Check password and is_active
        if user.check_password(password) and user.is_active:
            return user
        return None
    
    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
