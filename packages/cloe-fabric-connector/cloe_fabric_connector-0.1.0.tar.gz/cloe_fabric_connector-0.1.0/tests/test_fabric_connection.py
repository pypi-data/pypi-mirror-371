from unittest.mock import Mock, patch

import httpx
import pytest
from cloe_fabric_connector.fabric_connection import FabricConnectionError, FabricConnector
from cloe_fabric_connector.lakehouse_client import LakehouseClient
from cloe_fabric_connector.token_provider import TokenProvider


class TestFabricConnector:
    """Test cases for FabricConnector class."""

    def test_initialization_with_defaults(self):
        """Test FabricConnector initialization with default values."""
        connector = FabricConnector()

        assert connector.client_id is None
        assert connector.client_secret is None
        assert connector.tenant_id is None
        assert connector.workspace_id is None
        assert connector.lakehouse_id is None
        assert connector.api_base_url == "https://api.fabric.microsoft.com/v1"
        assert connector.session_timeout == 300
        assert connector.poll_interval == 5

    def test_initialization_with_custom_values(self):
        """Test FabricConnector initialization with custom values."""
        connector = FabricConnector(
            client_id="test-client",
            client_secret="test-secret",
            tenant_id="test-tenant",
            workspace_id="test-workspace",
            lakehouse_id="test-lakehouse",
            api_base_url="https://custom.api.com",
            session_timeout=600,
            poll_interval=10,
        )

        assert connector.client_id == "test-client"
        assert connector.client_secret == "test-secret"
        assert connector.tenant_id == "test-tenant"
        assert connector.workspace_id == "test-workspace"
        assert connector.lakehouse_id == "test-lakehouse"
        assert connector.api_base_url == "https://custom.api.com"
        assert connector.session_timeout == 600
        assert connector.poll_interval == 10

    def test_validate_required_auth_fields_empty_string(self, monkeypatch):
        """Test validation of empty string auth fields."""
        # Clear all environment variables to avoid interference
        monkeypatch.delenv("CLOE_FABRIC_CLIENT_ID", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_CLIENT_SECRET", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_TENANT_ID", raising=False)

        with pytest.raises(ValueError, match="client_id cannot be empty"):
            FabricConnector(client_id="   ")

    def test_validate_required_auth_fields_none_allowed(self):
        """Test that None values are allowed for auth fields."""
        connector = FabricConnector(client_id=None, client_secret=None, tenant_id=None)
        assert connector.client_id is None
        assert connector.client_secret is None
        assert connector.tenant_id is None

    @patch("cloe_fabric_connector.fabric_connection.load_dotenv")
    def test_env_variable_loading(self, mock_load_dotenv, monkeypatch) -> None:
        """Ensure that credentials are correctly loaded from the environment and passed to Client"""
        # Clear existing env vars first
        monkeypatch.delenv("CLOE_FABRIC_CLIENT_ID", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_CLIENT_SECRET", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_TENANT_ID", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_WORKSPACE_ID", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_LAKEHOUSE_ID", raising=False)

        # Set test values
        monkeypatch.setenv("CLOE_FABRIC_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("CLOE_FABRIC_CLIENT_SECRET", "test_client_secret")
        monkeypatch.setenv("CLOE_FABRIC_TENANT_ID", "test_tenant_id")

        connector = FabricConnector.from_env()
        assert connector.client_id == "test_client_id"
        assert connector.client_secret == "test_client_secret"
        assert connector.tenant_id == "test_tenant_id"
        mock_load_dotenv.assert_called_once_with(override=True)

    @patch("cloe_fabric_connector.fabric_connection.load_dotenv")
    def test_from_env_with_optional_variables(self, mock_load_dotenv, monkeypatch):
        """Test from_env with optional workspace and lakehouse IDs."""
        # Clear existing env vars first
        monkeypatch.delenv("CLOE_FABRIC_CLIENT_ID", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_CLIENT_SECRET", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_TENANT_ID", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_WORKSPACE_ID", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_LAKEHOUSE_ID", raising=False)

        # Set test values
        monkeypatch.setenv("CLOE_FABRIC_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("CLOE_FABRIC_CLIENT_SECRET", "test_client_secret")
        monkeypatch.setenv("CLOE_FABRIC_TENANT_ID", "test_tenant_id")
        monkeypatch.setenv("CLOE_FABRIC_WORKSPACE_ID", "test_workspace_id")
        monkeypatch.setenv("CLOE_FABRIC_LAKEHOUSE_ID", "test_lakehouse_id")

        connector = FabricConnector.from_env()
        assert connector.workspace_id == "test_workspace_id"
        assert connector.lakehouse_id == "test_lakehouse_id"
        mock_load_dotenv.assert_called_once_with(override=True)

    @patch("cloe_fabric_connector.fabric_connection.load_dotenv")
    def test_missing_credentials_token_and_client_secret(self, mock_load_dotenv, monkeypatch):
        # Clear all env vars first
        monkeypatch.delenv("CLOE_FABRIC_CLIENT_ID", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_CLIENT_SECRET", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_TENANT_ID", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_WORKSPACE_ID", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_LAKEHOUSE_ID", raising=False)

        # Set partial values
        monkeypatch.setenv("CLOE_FABRIC_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("CLOE_FABRIC_TENANT_ID", "test_tenant_id")

        with pytest.raises(
            ValueError,
            match="Missing required environment variables for service principal authentication.*",
        ):
            FabricConnector.from_env()
        mock_load_dotenv.assert_called_once_with(override=True)

    @patch("cloe_fabric_connector.fabric_connection.load_dotenv")
    def test_missing_all_required_credentials(self, mock_load_dotenv, monkeypatch):
        """Test from_env when all required credentials are missing."""
        monkeypatch.delenv("CLOE_FABRIC_CLIENT_ID", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_CLIENT_SECRET", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_TENANT_ID", raising=False)

        with pytest.raises(ValueError) as exc_info:
            FabricConnector.from_env()

        error_msg = str(exc_info.value)
        assert "Missing required environment variables" in error_msg
        assert "CLOE_FABRIC_TENANT_ID" in error_msg
        assert "CLOE_FABRIC_CLIENT_ID" in error_msg
        assert "CLOE_FABRIC_CLIENT_SECRET" in error_msg
        mock_load_dotenv.assert_called_once_with(override=True)

    def test_validate_lakehouse_config_success(self):
        """Test successful lakehouse configuration validation."""
        connector = FabricConnector(workspace_id="test-workspace", lakehouse_id="test-lakehouse")

        workspace_id, lakehouse_id = connector._validate_lakehouse_config()
        assert workspace_id == "test-workspace"
        assert lakehouse_id == "test-lakehouse"

    def test_validate_lakehouse_config_from_env(self, monkeypatch):
        """Test lakehouse configuration validation using environment variables."""
        monkeypatch.setenv("CLOE_FABRIC_WORKSPACE_ID", "env-workspace")
        monkeypatch.setenv("CLOE_FABRIC_LAKEHOUSE_ID", "env-lakehouse")

        connector = FabricConnector()
        workspace_id, lakehouse_id = connector._validate_lakehouse_config()
        assert workspace_id == "env-workspace"
        assert lakehouse_id == "env-lakehouse"

    def test_validate_lakehouse_config_missing_workspace(self, monkeypatch):
        """Test lakehouse configuration validation with missing workspace ID."""
        # Clear env vars to ensure no fallback
        monkeypatch.delenv("CLOE_FABRIC_WORKSPACE_ID", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_LAKEHOUSE_ID", raising=False)

        connector = FabricConnector(lakehouse_id="test-lakehouse")

        with pytest.raises(FabricConnectionError, match="Workspace ID is required"):
            connector._validate_lakehouse_config()

    def test_validate_lakehouse_config_missing_lakehouse(self, monkeypatch):
        """Test lakehouse configuration validation with missing lakehouse ID."""
        # Clear env vars to ensure no fallback
        monkeypatch.delenv("CLOE_FABRIC_WORKSPACE_ID", raising=False)
        monkeypatch.delenv("CLOE_FABRIC_LAKEHOUSE_ID", raising=False)

        connector = FabricConnector(workspace_id="test-workspace")

        with pytest.raises(FabricConnectionError, match="Lakehouse ID is required"):
            connector._validate_lakehouse_config()

    def test_create_token_provider_success(self):
        """Test successful token provider creation."""
        connector = FabricConnector(tenant_id="test-tenant", client_id="test-client", client_secret="test-secret")

        token_provider = connector._create_token_provider()

        assert isinstance(token_provider, TokenProvider)
        assert token_provider.tenant_id == "test-tenant"
        assert token_provider.client_id == "test-client"
        assert token_provider.client_secret is not None
        assert token_provider.client_secret.get_secret_value() == "test-secret"

    def test_create_token_provider_missing_credentials(self):
        """Test token provider creation with missing credentials."""
        connector = FabricConnector(tenant_id="test-tenant")

        with pytest.raises(FabricConnectionError, match="Missing authentication configuration"):
            connector._create_token_provider()

    def test_wait_for_session_ready_success(self):
        """Test successful session ready waiting."""
        connector = FabricConnector()
        session_url = "https://api.fabric.microsoft.com/sessions/123"
        headers = {"Authorization": "Bearer token"}

        # Mock successful response with idle state
        mock_response = Mock()
        mock_response.json.return_value = {"state": "idle"}

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.get.return_value = mock_response

            # Should not raise any exception
            connector._wait_for_session_ready(session_url, headers, timeout=30)

    def test_wait_for_session_ready_timeout(self):
        """Test session ready waiting with timeout."""
        connector = FabricConnector()
        session_url = "https://api.fabric.microsoft.com/sessions/123"
        headers = {"Authorization": "Bearer token"}

        # Mock response that never becomes idle
        mock_response = Mock()
        mock_response.json.return_value = {"state": "starting"}

        with patch("httpx.Client") as mock_client_class, patch("time.sleep"):  # Speed up the test
            mock_client = Mock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.get.return_value = mock_response

            with pytest.raises(FabricConnectionError, match="Session did not become ready within 1 seconds"):
                connector._wait_for_session_ready(session_url, headers, timeout=1)

    def test_wait_for_session_ready_error_state(self):
        """Test session ready waiting when session enters error state."""
        connector = FabricConnector()
        session_url = "https://api.fabric.microsoft.com/sessions/123"
        headers = {"Authorization": "Bearer token"}

        # Mock response with error state
        mock_response = Mock()
        mock_response.json.return_value = {"state": "error"}

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.get.return_value = mock_response

            with pytest.raises(FabricConnectionError, match="Session failed with state: error"):
                connector._wait_for_session_ready(session_url, headers, timeout=30)

    def test_wait_for_session_ready_http_error(self):
        """Test session ready waiting with HTTP error."""
        connector = FabricConnector()
        session_url = "https://api.fabric.microsoft.com/sessions/123"
        headers = {"Authorization": "Bearer token"}

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.get.side_effect = httpx.HTTPError("Network error")

            with pytest.raises(FabricConnectionError, match="Failed to check session status"):
                connector._wait_for_session_ready(session_url, headers, timeout=30)

    @patch.object(FabricConnector, "_wait_for_session_ready")
    @patch.object(FabricConnector, "_create_token_provider")
    @patch.object(FabricConnector, "_validate_lakehouse_config")
    @patch("httpx.Client")
    def test_get_lakehouse_client_success(self, mock_client_class, mock_validate, mock_token_provider, mock_wait):
        """Test successful lakehouse client creation."""
        # Setup mocks
        mock_validate.return_value = ("workspace123", "lakehouse456")

        mock_token_provider_instance = Mock()
        mock_token_provider_instance.access_token = "test-token"
        mock_token_provider.return_value = mock_token_provider_instance

        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        mock_response = Mock()
        mock_response.json.return_value = {"id": "session789"}
        mock_client.post.return_value = mock_response

        connector = FabricConnector()

        # Test the method
        lakehouse_client = connector.get_lakehouse_client()

        # Verify calls
        mock_validate.assert_called_once()
        mock_token_provider.assert_called_once()
        mock_wait.assert_called_once()

        # Verify lakehouse client
        assert isinstance(lakehouse_client, LakehouseClient)

    @patch.object(FabricConnector, "_validate_lakehouse_config")
    def test_get_lakehouse_client_validation_error(self, mock_validate):
        """Test lakehouse client creation with validation error."""
        mock_validate.side_effect = FabricConnectionError("Validation failed")

        connector = FabricConnector()

        with pytest.raises(FabricConnectionError, match="Validation failed"):
            connector.get_lakehouse_client()

    @patch.object(FabricConnector, "_create_token_provider")
    @patch.object(FabricConnector, "_validate_lakehouse_config")
    @patch("httpx.Client")
    def test_get_lakehouse_client_session_creation_error(
        self,
        mock_client_class,
        mock_validate,
        mock_token_provider,
    ):
        """Test lakehouse client creation with session creation error."""
        # Setup mocks
        mock_validate.return_value = ("workspace123", "lakehouse456")

        mock_token_provider_instance = Mock()
        mock_token_provider_instance.access_token = "test-token"
        mock_token_provider.return_value = mock_token_provider_instance

        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        mock_client.post.side_effect = httpx.HTTPError("Session creation failed")

        connector = FabricConnector()

        with pytest.raises(FabricConnectionError, match="Failed to create Livy session"):
            connector.get_lakehouse_client()

    @patch.object(FabricConnector, "from_env")
    def test_main_function_success(self, mock_from_env):
        """Test successful main function execution."""
        from cloe_fabric_connector.fabric_connection import main

        mock_connector = Mock()
        mock_from_env.return_value = mock_connector

        mock_client = Mock()
        mock_connector.get_lakehouse_client.return_value = mock_client

        result = main()

        assert result is mock_client
        mock_from_env.assert_called_once()
        mock_connector.get_lakehouse_client.assert_called_once()

    @patch.object(FabricConnector, "from_env")
    def test_main_function_failure(self, mock_from_env):
        """Test main function with failure."""
        from cloe_fabric_connector.fabric_connection import main

        mock_from_env.side_effect = ValueError("Environment error")

        with pytest.raises(ValueError, match="Environment error"):
            main()


class TestFabricConnectionError:
    """Test cases for FabricConnectionError exception."""

    def test_fabric_connection_error(self):
        """Test FabricConnectionError creation."""
        error = FabricConnectionError("Test connection error")
        assert str(error) == "Test connection error"
        assert isinstance(error, Exception)
