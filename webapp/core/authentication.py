"""
Custom Firebase Authentication Backend for Django REST Framework

This module provides a custom authentication class that verifies Firebase ID tokens
and authenticates users in Django.
"""

from rest_framework import authentication, exceptions
from firebase_admin import auth as firebase_auth
from .firebase_config import verify_firebase_token
from .models import User
import logging

logger = logging.getLogger(__name__)


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Custom DRF authentication class that verifies Firebase ID tokens.
    
    This authentication class:
    1. Extracts the Firebase ID token from the Authorization header
    2. Verifies the token using Firebase Admin SDK
    3. Gets or creates a Django User from the token data
    4. Returns the authenticated user
    
    The Authorization header should be in the format:
        Authorization: Bearer <firebase_id_token>
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using Firebase ID token.
        
        Args:
            request: The HTTP request object.
            
        Returns:
            tuple: (user, token_data) if authentication is successful.
            None: If no authentication credentials were provided.
            
        Raises:
            AuthenticationFailed: If authentication fails.
        """
        # Get the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        # Parse the Bearer token
        try:
            auth_type, token = auth_header.split(' ', 1)
            if auth_type.lower() != 'bearer':
                return None
        except ValueError:
            return None
        
        # Verify the Firebase token
        try:
            decoded_token = verify_firebase_token(token)
        except firebase_auth.ExpiredIdTokenError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except firebase_auth.InvalidIdTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise exceptions.AuthenticationFailed('Authentication failed')
        
        # Get or create the user
        try:
            user = self.get_or_create_user(decoded_token)
        except Exception as e:
            logger.error(f"Error getting or creating user: {e}")
            raise exceptions.AuthenticationFailed('User creation failed')
        
        return (user, decoded_token)
    
    def get_or_create_user(self, token_data: dict):
        """
        Get or create a Django User from Firebase token data.
        
        Args:
            token_data: Decoded Firebase token containing user information.
            
        Returns:
            User: The Django User object.
            
        Raises:
            ValueError: If required user data is missing.
        """
        firebase_uid = token_data.get('uid')
        email = token_data.get('email')
        name = token_data.get('name', '')
        
        if not email:
            raise ValueError("Email is required")
        
        # Try to get existing user by email
        try:
            user = User.objects.get(email=email)
            logger.info(f"Found existing user: {email}")
            return user
        except User.DoesNotExist:
            # Create a new user
            # Parse the name into first and last name
            name_parts = name.split(' ', 1) if name else ['', '']
            firstname = name_parts[0] if len(name_parts) > 0 else email.split('@')[0]
            lastname = name_parts[1] if len(name_parts) > 1 else ''
            
            # Default role for new users is 'student'
            # Admins can change this later through the admin panel
            user = User.objects.create(
                email=email,
                firstname=firstname,
                lastname=lastname,
                role='student',  # Default role
            )
            logger.info(f"Created new user: {email}")
            return user
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the WWW-Authenticate
        header in a 401 Unauthenticated response.
        """
        return 'Bearer realm="api"'
