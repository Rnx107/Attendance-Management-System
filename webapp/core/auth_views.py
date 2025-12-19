"""
Authentication Views for Firebase-Django Integration

This module provides API endpoints for handling Firebase authentication,
session management, and token operations.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import auth as firebase_auth
from .firebase_config import verify_firebase_token
from .models import User
from .serializers import UserSerializer
import jwt
from datetime import datetime, timedelta
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def generate_session_token(user: User) -> dict:
    """
    Generate a JWT session token for a Django user.
    
    Args:
        user: The Django User object.
        
    Returns:
        dict: Token data containing:
            - token: The JWT session token
            - expires_at: ISO formatted expiration timestamp
            - user: Serialized user data
    """
    # Token expires in 1 hour
    expiration = datetime.utcnow() + timedelta(hours=1)
    
    payload = {
        'user_id': str(user.id),
        'email': user.email,
        'role': user.role,
        'exp': expiration,
        'iat': datetime.utcnow(),
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    return {
        'token': token,
        'expires_at': expiration.isoformat(),
        'user': UserSerializer(user).data,
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def firebase_login(request):
    """
    Authenticate user with Firebase ID token and return Django session token.
    
    Request Body:
        {
            "idToken": "firebase_id_token_here"
        }
    
    Response:
        {
            "success": true,
            "token": "django_session_token",
            "expires_at": "2024-01-01T12:00:00",
            "user": {
                "id": "uuid",
                "email": "user@example.com",
                "firstname": "John",
                "lastname": "Doe",
                "role": "student"
            }
        }
    
    Error Response:
        {
            "success": false,
            "error": "error_message"
        }
    """
    id_token = request.data.get('idToken')
    
    if not id_token:
        return Response(
            {'success': False, 'error': 'Firebase ID token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Verify Firebase token
        decoded_token = verify_firebase_token(id_token)
        
        # Extract user data
        firebase_uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        name = decoded_token.get('name', '')
        
        if not email:
            return Response(
                {'success': False, 'error': 'Email not found in token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create user
        try:
            user = User.objects.get(email=email)
            logger.info(f"Existing user logged in: {email}")
        except User.DoesNotExist:
            # Create new user
            name_parts = name.split(' ', 1) if name else ['', '']
            firstname = name_parts[0] if len(name_parts) > 0 else email.split('@')[0]
            lastname = name_parts[1] if len(name_parts) > 1 else ''
            
            user = User.objects.create(
                email=email,
                firstname=firstname,
                lastname=lastname,
                role='student',  # Default role
            )
            logger.info(f"New user registered: {email}")
        
        # Generate session token
        token_data = generate_session_token(user)
        
        return Response({
            'success': True,
            **token_data
        }, status=status.HTTP_200_OK)
        
    except firebase_auth.ExpiredIdTokenError:
        return Response(
            {'success': False, 'error': 'Firebase token has expired'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except firebase_auth.InvalidIdTokenError:
        return Response(
            {'success': False, 'error': 'Invalid Firebase token'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        return Response(
            {'success': False, 'error': 'Authentication failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def firebase_logout(request):
    """
    Handle user logout.
    
    Note: Since we're using stateless JWT tokens, logout is primarily handled
    on the client side by removing the stored token. This endpoint serves as
    a confirmation and can be used for logging purposes.
    
    Response:
        {
            "success": true,
            "message": "Logged out successfully"
        }
    """
    logger.info(f"User logged out: {request.user.email}")
    
    return Response({
        'success': True,
        'message': 'Logged out successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_session(request):
    """
    Verify the current session validity and return user data.
    
    This endpoint requires authentication via session token.
    
    Response:
        {
            "success": true,
            "valid": true,
            "user": {
                "id": "uuid",
                "email": "user@example.com",
                "firstname": "John",
                "lastname": "Doe",
                "role": "student"
            }
        }
    """
    return Response({
        'success': True,
        'valid': True,
        'user': UserSerializer(request.user).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh the Django session token using a new Firebase ID token.
    
    This allows users to extend their session by providing a fresh Firebase token.
    
    Request Body:
        {
            "idToken": "new_firebase_id_token"
        }
    
    Response:
        {
            "success": true,
            "token": "new_django_session_token",
            "expires_at": "2024-01-01T12:00:00",
            "user": { ... }
        }
    """
    id_token = request.data.get('idToken')
    
    if not id_token:
        return Response(
            {'success': False, 'error': 'Firebase ID token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Verify Firebase token
        decoded_token = verify_firebase_token(id_token)
        email = decoded_token.get('email')
        
        if not email:
            return Response(
                {'success': False, 'error': 'Email not found in token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'success': False, 'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate new session token
        token_data = generate_session_token(user)
        
        return Response({
            'success': True,
            **token_data
        }, status=status.HTTP_200_OK)
        
    except firebase_auth.ExpiredIdTokenError:
        return Response(
            {'success': False, 'error': 'Firebase token has expired'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except firebase_auth.InvalidIdTokenError:
        return Response(
            {'success': False, 'error': 'Invalid Firebase token'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return Response(
            {'success': False, 'error': 'Token refresh failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
