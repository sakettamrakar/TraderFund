"""Angel One SmartAPI Authentication Manager.

This module handles SmartAPI login, token management, and provides
an authenticated client instance for API calls.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Optional

import pyotp
from SmartApi import SmartConnect

from .config import config

logger = logging.getLogger(__name__)


class AngelAuthManager:
    """Manages authentication with Angel One SmartAPI.

    Handles login, token refresh, and provides authenticated client instances.
    Tokens are cached to avoid repeated logins within the validity period.
    """

    # Token validity period (Angel tokens typically valid for ~6 hours)
    TOKEN_VALIDITY_HOURS = 5  # Refresh before actual expiry

    def __init__(self, cfg: Optional[object] = None, use_historical: bool = False):
        """Initialize the auth manager.

        Args:
            cfg: Configuration object. Uses default config if not provided.
            use_historical: Whether to use historical data credentials.
        """
        self._config = cfg or config
        self._use_historical = use_historical
        self._client: Optional[SmartConnect] = None
        self._auth_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._feed_token: Optional[str] = None
        self._token_timestamp: Optional[datetime] = None

    def _generate_totp(self) -> str:
        """Generate current TOTP code from secret."""
        secret = self._config.hist_totp_secret if self._use_historical else self._config.totp_secret
        totp = pyotp.TOTP(secret)
        return totp.now()

    def login(self) -> bool:
        """Authenticate with Angel One SmartAPI.

        Returns:
            True if login successful, False otherwise.
        """
        valid = self._config.validate_historical() if self._use_historical else self._config.validate()
        if not valid:
            mode = "historical" if self._use_historical else "live"
            missing = self._config.get_missing_credentials(mode=mode)
            logger.error(f"Missing {mode} credentials: {missing}")
            return False

        try:
            api_key = self._config.hist_api_key if self._use_historical else self._config.api_key
            client_id = self._config.hist_client_id if self._use_historical else self._config.client_id
            pin = self._config.hist_pin if self._use_historical else self._config.pin
            
            self._client = SmartConnect(api_key=api_key)

            totp_code = self._generate_totp()

            data = self._client.generateSession(
                clientCode=client_id,
                password=pin,
                totp=totp_code,
            )

            if data.get("status"):
                self._auth_token = data["data"]["jwtToken"]
                self._refresh_token = data["data"]["refreshToken"]
                self._feed_token = self._client.getfeedToken()
                self._token_timestamp = datetime.now()

                logger.info(
                    f"Login successful for {('historical' if self._use_historical else 'live')} client {client_id}"
                )
                return True
            else:
                logger.error(f"Login failed: {data.get('message', 'Unknown error')}")
                return False

        except Exception as exc:
            logger.exception(f"Login exception: {exc}")
            return False

    def refresh_token(self) -> bool:
        """Refresh the authentication token.

        Returns:
            True if refresh successful, False otherwise.
        """
        if not self._client or not self._refresh_token:
            logger.warning("No existing session to refresh. Performing fresh login.")
            return self.login()

        try:
            data = self._client.generateToken(self._refresh_token)

            if data.get("status"):
                self._auth_token = data["data"]["jwtToken"]
                self._refresh_token = data["data"]["refreshToken"]
                self._token_timestamp = datetime.now()

                logger.info("Token refresh successful")
                return True
            else:
                logger.warning(
                    f"Token refresh failed: {data.get('message')}. Performing fresh login."
                )
                return self.login()

        except Exception as exc:
            logger.exception(f"Token refresh exception: {exc}")
            return self.login()

    def is_token_valid(self) -> bool:
        """Check if the current token is still valid.

        Returns:
            True if token exists and is within validity period.
        """
        if not self._token_timestamp or not self._auth_token:
            return False

        elapsed = datetime.now() - self._token_timestamp
        return elapsed < timedelta(hours=self.TOKEN_VALIDITY_HOURS)

    def ensure_authenticated(self) -> bool:
        """Ensure we have a valid authentication.

        Refreshes token if expired, or performs fresh login if needed.

        Returns:
            True if authenticated, False otherwise.
        """
        if self.is_token_valid():
            return True

        if self._refresh_token:
            logger.info("Token expired. Attempting refresh.")
            return self.refresh_token()

        logger.info("No valid session. Performing login.")
        return self.login()

    def get_client(self) -> Optional[SmartConnect]:
        """Get authenticated SmartConnect client.

        Ensures authentication is valid before returning client.

        Returns:
            Authenticated SmartConnect instance, or None if auth fails.
        """
        if not self.ensure_authenticated():
            return None
        return self._client

    def logout(self) -> bool:
        """Logout and invalidate the session.

        Returns:
            True if logout successful or no session exists.
        """
        if not self._client:
            return True

        try:
            client_id = self._config.hist_client_id if self._use_historical else self._config.client_id
            self._client.terminateSession(client_id)
            logger.info("Logout successful")
        except Exception as exc:
            logger.warning(f"Logout exception (non-critical): {exc}")

        self._client = None
        self._auth_token = None
        self._refresh_token = None
        self._feed_token = None
        self._token_timestamp = None
        return True
