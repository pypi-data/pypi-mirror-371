import time

from cloe_logging import LoggerFactory
from msal import ConfidentialClientApplication
from pydantic import BaseModel, Field, SecretStr

logger = LoggerFactory.get_logger(handler_types=["console"], filename="fabric_connector.log")


class AuthTokenError(Exception):
    def __init__(self, message, error_code=None, raw_response=None):
        super().__init__(message)
        self.error_code = error_code
        self.raw_response = raw_response


class TokenProvider(BaseModel):
    """
    Azure access token provider using client credentials flow.
    Handles token renewal and caching.
    """

    tenant_id: str | None = Field(default=None)
    client_id: str | None = Field(default=None)
    client_secret: SecretStr | None = Field(default=None)
    audience: str = Field(default="https://api.fabric.microsoft.com/.default")

    def __init__(self, **data):
        super().__init__(**data)
        self._access_token: str = ""
        self._expires_at: float = 0.0
        self._app: ConfidentialClientApplication | None = None

    @property
    def authority(self) -> str:
        """Return the Azure AD authority URL."""
        return f"https://login.microsoftonline.com/{self.tenant_id}"

    @property
    def app(self) -> ConfidentialClientApplication:
        """Return or create the MSAL ConfidentialClientApplication instance."""
        if self._app is None:
            self._app = ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret.get_secret_value() if self.client_secret else None,
                authority=self.authority,
            )
        return self._app

    @property
    def access_token(self) -> str:
        """Return a valid access token, renewing if expired."""
        if self._is_token_expired():
            self._renew_token()
        return self._access_token

    def _is_token_expired(self) -> bool:
        """Check if the cached token is expired."""
        return time.time() >= self._expires_at

    def _renew_token(self) -> None:
        """Renew the access token and update expiry."""
        self._access_token = self._acquire_token()

    def _acquire_token(self) -> str:
        """Acquire a new access token from Azure AD."""
        logger.info("Requesting new access token...")
        result = self.app.acquire_token_for_client(scopes=[self.audience])

        if "access_token" in result:
            token = result["access_token"]
            expires_in = result.get("expires_in", 3600)
            self._expires_at = time.time() + expires_in - 300  # Renew 5 min before expiry
            logger.info("Access token acquired successfully.")
            return str(token)
        error_code = result.get("error")
        error_desc = result.get("error_description", "Unknown error")
        raise AuthTokenError(f"Failed to retrieve token: {error_desc}", error_code=error_code, raw_response=result)
