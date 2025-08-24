"""
Authentication management for the Trading Platform SDK
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional, cast

from .exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class AuthManager:
    """
    Manages authentication and JWT tokens for the trading platform
    """

    def __init__(self, client):
        self.client = client
        self.jwt_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self._refresh_token: Optional[str] = None

    def set_jwt_token(self, token: str, expires_in: Optional[int] = None):
        """
        Set the JWT token and optional expiration
        Args:
            token: JWT token string
            expires_in: Token expiration in seconds from now
        """
        self.jwt_token = token
        if expires_in:
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        else:
            # Default to 1 hour if no expiration provided
            self.token_expires_at = datetime.utcnow() + timedelta(hours=1)

        logger.info("JWT token set successfully")

    def is_token_expired(self) -> bool:
        """Check if the current token is expired"""
        if not self.jwt_token or not self.token_expires_at:
            return True

        # Add 5 minute buffer before actual expiration
        return datetime.utcnow() > (self.token_expires_at - timedelta(minutes=5))

    async def login_with_google(self, redirect_uri: str) -> str:
        """
        Initiate Google OAuth2 login flow
        Args:
            redirect_uri: URI to redirect to after authentication
        Returns:
            Google OAuth2 authorization URL
        """
        try:
            response = await self.client.request(
                'POST',
                'auth',
                'auth/login',
                auth_required=False,
                json={'redirect_uri': redirect_uri}
            )

            auth_url = response['auth_url']
            return cast(str, auth_url)

        except Exception as e:
            raise AuthenticationError(
                f"Failed to initiate Google login: {e}"
            ) from e

    async def handle_oauth_callback(self, authorization_code: str, state: str) -> dict[str, Any]:
        """
        Handle OAuth2 callback and exchange code for JWT token
        Args:
            authorization_code: Authorization code from OAuth2 callback
            state: State parameter for CSRF protection
        Returns:
            User profile and token information
        """
        try:
            response = await self.client.request(
                'POST',
                'auth',
                'auth/callback',
                auth_required=False,
                json={
                    'code': authorization_code,
                    'state': state
                }
            )

            # Extract token information
            jwt_token = response.get('jwt_token')
            expires_in = response.get('expires_in')
            refresh_token = response.get('refresh_token')

            if jwt_token:
                self.set_jwt_token(jwt_token, expires_in)
                if refresh_token:
                    self._refresh_token = refresh_token

            return cast(dict[str, Any], response)

        except Exception as e:
            raise AuthenticationError(f"OAuth callback failed: {e}") from e

    async def refresh_token(self) -> bool:
        """
        Refresh the JWT token using the refresh token
        Returns:
            True if refresh was successful
        """
        if not self._refresh_token:
            logger.warning("No refresh token available")
            return False

        try:
            response = await self.client.request(
                'POST',
                'auth',
                'auth/refresh',
                auth_required=False,
                json={'refresh_token': self._refresh_token}
            )

            jwt_token = response.get('jwt_token')
            expires_in = response.get('expires_in')

            if jwt_token:
                self.set_jwt_token(jwt_token, expires_in)
                logger.info("JWT token refreshed successfully")
                return True

            return False

        except Exception as e:
            logger.error("Token refresh failed: %s", e)
            return False

    async def validate_token(self) -> bool:
        """
        Validate the current JWT token with the server
        Returns:
            True if token is valid
        """
        if not self.jwt_token:
            return False

        try:
            response = await self.client.request(
                'POST',
                'auth',
                'auth/validate',
                auth_required=True
            )

            valid = response.get('valid', False)
            return bool(valid)

        except Exception as e:
            logger.error("Token validation failed: %s", e)
            return False

    async def get_profile(self) -> dict[str, Any]:
        """
        Get the current user's profile information
        Returns:
            User profile data
        """
        try:
            response = await self.client.request(
                'GET',
                'auth',
                'auth/profile',
                auth_required=True
            )

            return cast(dict[str, Any], response)

        except Exception as e:
            raise AuthenticationError(f"Failed to get user profile: {e}") from e

    async def logout(self):
        """Logout and clear authentication state"""
        try:
            if self.jwt_token:
                await self.client.request(
                    'POST',
                    'auth',
                    'auth/logout',
                    auth_required=True
                )
        except Exception as e:
            logger.warning("Logout request failed: %s", e)
        finally:
            # Clear local auth state regardless of server response
            self.jwt_token = None
            self.token_expires_at = None
            self._refresh_token = None
            logger.info("Logged out successfully")
