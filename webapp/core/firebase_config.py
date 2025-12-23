"""
Firebase Admin SDK Configuration

This module initializes Firebase Admin SDK and provides utility functions
for Firebase token verification and user management.
"""

import firebase_admin
from firebase_admin import credentials, auth
from decouple import config
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
_firebase_app = None

def initialize_firebase():
    """
    Initialize Firebase Admin SDK with service account credentials.
    
    This function should be called once during application startup.
    It reads the Firebase credentials from the path specified in environment variables.
    
    Raises:
        FileNotFoundError: If the Firebase credentials file is not found.
        ValueError: If the Firebase credentials are invalid.
    """
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    try:
        # Get the credentials path from environment variable
        cred_path = config('FIREBASE_CREDENTIALS_PATH', default=None)
        
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            _firebase_app = firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully")
        else:
            # In production, credentials are required
            if config('DEBUG', default=True, cast=bool) is False:
                raise ValueError("Firebase credentials are required in production. Set FIREBASE_CREDENTIALS_PATH.")
            
            # For development/testing only, use default credentials
            logger.warning("Firebase credentials not found. Using default initialization (development only).")
            _firebase_app = firebase_admin.initialize_app()
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        raise
    
    return _firebase_app


def verify_firebase_token(id_token: str) -> dict:
    """
    Verify a Firebase ID token and return the decoded token data.
    
    Args:
        id_token: The Firebase ID token to verify.
        
    Returns:
        dict: Decoded token data containing user information including:
            - uid: Firebase user ID
            - email: User email address
            - name: User display name (if available)
            - picture: User profile picture URL (if available)
            - email_verified: Boolean indicating if email is verified
            
    Raises:
        auth.InvalidIdTokenError: If the token is invalid or expired.
        auth.ExpiredIdTokenError: If the token has expired.
        ValueError: If the token is None or empty.
    
    Example:
        >>> token_data = verify_firebase_token(firebase_id_token)
        >>> user_email = token_data['email']
    """
    if not id_token:
        raise ValueError("ID token is required")
    
    try:
        # Initialize Firebase if not already done
        if _firebase_app is None:
            initialize_firebase()
        
        # Verify the ID token and get decoded token data
        decoded_token = auth.verify_id_token(id_token)
        logger.info(f"Successfully verified token for user: {decoded_token.get('uid')}")
        return decoded_token
    except auth.ExpiredIdTokenError:
        logger.warning("Firebase token has expired")
        raise
    except auth.InvalidIdTokenError as e:
        logger.warning(f"Invalid Firebase token: {e}")
        raise
    except Exception as e:
        logger.error(f"Error verifying Firebase token: {e}")
        raise


def get_firebase_user(uid: str) -> dict:
    """
    Fetch user details from Firebase using their UID.
    
    Args:
        uid: The Firebase user ID.
        
    Returns:
        dict: User data from Firebase containing:
            - uid: Firebase user ID
            - email: User email address
            - displayName: User display name
            - photoURL: User profile picture URL
            - emailVerified: Boolean indicating if email is verified
            
    Raises:
        auth.UserNotFoundError: If the user does not exist.
        ValueError: If uid is None or empty.
    
    Example:
        >>> user_data = get_firebase_user('firebase_uid_123')
        >>> email = user_data.email
    """
    if not uid:
        raise ValueError("User UID is required")
    
    try:
        # Initialize Firebase if not already done
        if _firebase_app is None:
            initialize_firebase()
        
        # Get user data from Firebase
        user = auth.get_user(uid)
        logger.info(f"Successfully fetched user data for UID: {uid}")
        
        return {
            'uid': user.uid,
            'email': user.email,
            'displayName': user.display_name,
            'photoURL': user.photo_url,
            'emailVerified': user.email_verified,
        }
    except auth.UserNotFoundError:
        logger.warning(f"User not found with UID: {uid}")
        raise
    except Exception as e:
        logger.error(f"Error fetching Firebase user: {e}")
        raise
