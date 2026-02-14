"""
Business logic services for accounts app.

This module contains service classes that handle business logic,
separating concerns from serializers and views.
"""

from typing import Dict, Tuple
import logging
from django.contrib.auth import get_user_model
from firebase_admin import auth as firebase_auth
from django.conf import settings
from rest_framework.exceptions import ValidationError

User = get_user_model()
logger = logging.getLogger(__name__)


class GoogleOAuthService:
    """
    Service for handling Google OAuth operations.

    Responsibilities:
    - Verify Google ID tokens
    - Extract user information from tokens
    """

    VALID_ISSUERS = ['accounts.google.com', 'https://accounts.google.com']

    def __init__(self, client_id: str = None):
        """
        Initialize the Google OAuth service.

        Args:
            client_id: Google OAuth client ID. Defaults to settings.GOOGLE_OAUTH_CLIENT_ID
        """
        self.client_id = client_id or settings.GOOGLE_OAUTH_CLIENT_ID

        if not self.client_id:
            raise ValueError("Google OAuth client ID is not configured")

    def verify_token(self, token: str) -> Dict[str, any]:
        """
        Verify Google ID token using Firebase Admin SDK.

        Args:
            token: Google ID token string

        Returns:
            Dictionary containing verified user information

        Raises:
            ValidationError: If token is invalid or verification fails
        """
        try:
            # Verify the token with Firebase Admin SDK
            decoded_token = firebase_auth.verify_id_token(token)

            # Extract user information
            return self._extract_user_info(decoded_token)

        except firebase_auth.InvalidIdTokenError as e:
            logger.error(f"Invalid Firebase token: {str(e)}")
            raise ValidationError(f'Invalid Google token: {str(e)}')
        except firebase_auth.ExpiredIdTokenError as e:
            logger.error(f"Expired Firebase token: {str(e)}")
            raise ValidationError('Token has expired')
        except firebase_auth.RevokedIdTokenError as e:
            logger.error(f"Revoked Firebase token: {str(e)}")
            raise ValidationError('Token has been revoked')
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {str(e)}")
            raise ValidationError('Token verification failed')

    def _extract_user_info(self, decoded_token: Dict) -> Dict[str, any]:
        """
        Extract and normalize user information from verified Firebase token.

        Args:
            decoded_token: Verified token information from Firebase

        Returns:
            Dictionary with normalized user information
        """
        # Split name into first and last name if available
        name = decoded_token.get('name', '')
        name_parts = name.split(' ', 1) if name else ['', '']
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        return {
            'email': decoded_token.get('email', '').lower(),
            'email_verified': decoded_token.get('email_verified', False),
            'first_name': first_name,
            'last_name': last_name,
            'avatar': decoded_token.get('picture', ''),
            'google_id': decoded_token.get('uid', ''),
        }


class UserService:
    """
    Service for user-related operations.

    Responsibilities:
    - User creation and updates
    - Username generation
    """

    @staticmethod
    def generate_unique_username(base_username: str, exclude_user_id: int = None) -> str:
        """
        Generate a unique username based on a base string.

        Args:
            base_username: The base username to use
            exclude_user_id: Optional user ID to exclude from uniqueness check

        Returns:
            A unique username string
        """
        username = base_username
        counter = 1

        queryset = User.objects.filter(username=username)
        if exclude_user_id:
            queryset = queryset.exclude(id=exclude_user_id)

        while queryset.exists():
            username = f"{base_username}{counter}"
            counter += 1
            queryset = User.objects.filter(username=username)
            if exclude_user_id:
                queryset = queryset.exclude(id=exclude_user_id)

        return username

    @staticmethod
    def create_or_update_from_google(google_data: Dict) -> Tuple[User, bool]:
        """
        Create or update user from Google OAuth data.

        Args:
            google_data: Dictionary containing Google user information

        Returns:
            Tuple of (User instance, created boolean)
        """
        email = google_data['email']

        # Check if user exists
        try:
            user = User.objects.get(email=email)
            created = False

            # Update existing user
            user.first_name = google_data.get('first_name', user.first_name)
            user.last_name = google_data.get('last_name', user.last_name)
            user.avatar = google_data.get('avatar', user.avatar)

            # Mark as verified if Google confirms email
            if google_data.get('email_verified'):
                user.is_verified = True

            user.save()
            logger.info(f"Updated existing user from Google OAuth: {email}")

        except User.DoesNotExist:
            # Create new user
            base_username = email.split('@')[0]
            username = UserService.generate_unique_username(base_username)

            user = User.objects.create(
                email=email,
                username=username,
                first_name=google_data.get('first_name', ''),
                last_name=google_data.get('last_name', ''),
                avatar=google_data.get('avatar', ''),
                is_verified=google_data.get('email_verified', False),
            )
            created = True
            logger.info(f"Created new user from Google OAuth: {email}")

        return user, created
