"""
Business logic services for accounts app.

This module contains service classes that handle business logic,
separating concerns from serializers and views.
"""

from typing import Dict, Tuple
import logging
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests
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
        Verify Google ID token and extract user information.

        Args:
            token: Google ID token string

        Returns:
            Dictionary containing verified user information

        Raises:
            ValidationError: If token is invalid or verification fails
        """
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                self.client_id
            )

            # Verify the token audience
            if idinfo.get('aud') != self.client_id:
                raise ValidationError('Invalid token audience')

            # Verify the token issuer
            if idinfo.get('iss') not in self.VALID_ISSUERS:
                raise ValidationError('Invalid token issuer')

            return self._extract_user_info(idinfo)

        except ValueError as e:
            logger.error(f"Google token verification failed: {str(e)}")
            raise ValidationError(f'Invalid Google token: {str(e)}')
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {str(e)}")
            raise ValidationError('Token verification failed')

    def _extract_user_info(self, idinfo: Dict) -> Dict[str, any]:
        """
        Extract and normalize user information from verified token.

        Args:
            idinfo: Verified token information from Google

        Returns:
            Dictionary with normalized user information
        """
        return {
            'email': idinfo.get('email', '').lower(),
            'email_verified': idinfo.get('email_verified', False),
            'first_name': idinfo.get('given_name', ''),
            'last_name': idinfo.get('family_name', ''),
            'avatar': idinfo.get('picture', ''),
            'google_id': idinfo.get('sub', ''),
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
