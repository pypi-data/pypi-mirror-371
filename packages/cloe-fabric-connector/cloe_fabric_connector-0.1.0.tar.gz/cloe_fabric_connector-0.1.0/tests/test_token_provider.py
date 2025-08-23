import time
from unittest.mock import Mock, patch

import pytest
from cloe_fabric_connector.token_provider import AuthTokenError, TokenProvider
from pydantic import SecretStr


class TestTokenProvider:
    """Test cases for TokenProvider class."""

    def test_initialization(self):
        """Test TokenProvider initialization with valid parameters."""
        provider = TokenProvider(
            tenant_id="test-tenant",
            client_id="test-client",
            client_secret=SecretStr("test-secret"),
        )

        assert provider.tenant_id == "test-tenant"
        assert provider.client_id == "test-client"
        assert provider.client_secret is not None
        assert provider.client_secret.get_secret_value() == "test-secret"
        assert provider.audience == "https://api.fabric.microsoft.com/.default"
        assert provider._access_token == ""
        assert provider._expires_at == 0.0

    def test_authority_property(self):
        """Test authority URL generation."""
        provider = TokenProvider(tenant_id="test-tenant-123")
        expected_authority = "https://login.microsoftonline.com/test-tenant-123"
        assert provider.authority == expected_authority

    @patch("cloe_fabric_connector.token_provider.ConfidentialClientApplication")
    def test_app_property_creates_application(self, mock_app_class):
        """Test that app property creates ConfidentialClientApplication instance."""
        mock_app_instance = Mock()
        mock_app_class.return_value = mock_app_instance

        provider = TokenProvider(
            tenant_id="test-tenant",
            client_id="test-client",
            client_secret=SecretStr("test-secret"),
        )

        # First access creates the app
        app = provider.app
        assert app is mock_app_instance

        # Second access returns cached app
        app2 = provider.app
        assert app2 is mock_app_instance

        # Verify app was created only once
        mock_app_class.assert_called_once_with(
            client_id="test-client",
            client_credential="test-secret",
            authority="https://login.microsoftonline.com/test-tenant",
        )

    def test_is_token_expired_when_expired(self):
        """Test token expiry detection when token is expired."""
        provider = TokenProvider()
        provider._expires_at = time.time() - 100  # 100 seconds ago
        assert provider._is_token_expired() is True

    def test_is_token_expired_when_valid(self):
        """Test token expiry detection when token is still valid."""
        provider = TokenProvider()
        provider._expires_at = time.time() + 100  # 100 seconds from now
        assert provider._is_token_expired() is False

    @patch.object(TokenProvider, "_acquire_token")
    def test_renew_token(self, mock_acquire):
        """Test token renewal."""
        mock_acquire.return_value = "new-token"
        provider = TokenProvider()

        provider._renew_token()

        assert provider._access_token == "new-token"
        mock_acquire.assert_called_once()

    @patch.object(TokenProvider, "_is_token_expired")
    @patch.object(TokenProvider, "_renew_token")
    def test_access_token_renews_when_expired(self, mock_renew, mock_expired):
        """Test that access_token property renews token when expired."""
        mock_expired.return_value = True
        provider = TokenProvider()
        provider._access_token = "current-token"

        token = provider.access_token

        mock_expired.assert_called_once()
        mock_renew.assert_called_once()
        assert token == "current-token"

    @patch.object(TokenProvider, "_is_token_expired")
    @patch.object(TokenProvider, "_renew_token")
    def test_access_token_returns_cached_when_valid(self, mock_renew, mock_expired):
        """Test that access_token property returns cached token when valid."""
        mock_expired.return_value = False
        provider = TokenProvider()
        provider._access_token = "cached-token"

        token = provider.access_token

        mock_expired.assert_called_once()
        mock_renew.assert_not_called()
        assert token == "cached-token"

    @patch.object(TokenProvider, "app")
    def test_acquire_token_success(self, mock_app):
        """Test successful token acquisition."""
        # Mock successful response
        mock_app.acquire_token_for_client.return_value = {"access_token": "test-token-123", "expires_in": 3600}

        provider = TokenProvider(
            tenant_id="test-tenant",
            client_id="test-client",
            client_secret=SecretStr("test-secret"),
        )

        # Mock time to control expiry calculation
        with patch("time.time", return_value=1000):
            token = provider._acquire_token()

        assert token == "test-token-123"
        assert provider._expires_at == 1000 + 3600 - 300  # 5 min buffer
        mock_app.acquire_token_for_client.assert_called_once_with(scopes=["https://api.fabric.microsoft.com/.default"])

    @patch.object(TokenProvider, "app")
    def test_acquire_token_failure(self, mock_app):
        """Test token acquisition failure."""
        # Mock error response
        mock_app.acquire_token_for_client.return_value = {
            "error": "invalid_client",
            "error_description": "Invalid client credentials",
        }

        provider = TokenProvider(
            tenant_id="test-tenant",
            client_id="test-client",
            client_secret=SecretStr("test-secret"),
        )

        with pytest.raises(AuthTokenError) as exc_info:
            provider._acquire_token()

        assert "Failed to retrieve token: Invalid client credentials" in str(exc_info.value)
        assert exc_info.value.error_code == "invalid_client"

    def test_custom_audience(self):
        """Test TokenProvider with custom audience."""
        custom_audience = "https://custom.api.com/.default"
        provider = TokenProvider(audience=custom_audience)
        assert provider.audience == custom_audience


class TestAuthTokenError:
    """Test cases for AuthTokenError exception."""

    def test_basic_error(self):
        """Test basic AuthTokenError creation."""
        error = AuthTokenError("Test error message")
        assert str(error) == "Test error message"
        assert error.error_code is None
        assert error.raw_response is None

    def test_error_with_code_and_response(self):
        """Test AuthTokenError with error code and raw response."""
        raw_response = {"error": "test_error", "details": "test details"}
        error = AuthTokenError("Test error", error_code="test_error", raw_response=raw_response)

        assert str(error) == "Test error"
        assert error.error_code == "test_error"
        assert error.raw_response == raw_response
