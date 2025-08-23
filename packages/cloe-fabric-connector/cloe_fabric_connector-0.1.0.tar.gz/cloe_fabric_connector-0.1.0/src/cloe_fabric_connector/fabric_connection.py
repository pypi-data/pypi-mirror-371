import os
import time

import httpx
from cloe_logging import LoggerFactory
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from cloe_fabric_connector.lakehouse_client import LakehouseClient
from cloe_fabric_connector.token_provider import TokenProvider

logger = LoggerFactory.get_logger(handler_types=["console"], filename="fabric_connector.log")


class FabricConnectionError(Exception):
    """Custom exception for Fabric connection errors."""

    pass


class FabricConnector(BaseModel):
    """
    Handles authentication and connection to Microsoft Fabric.
    Supports Service Principal authentication for secure access to Fabric resources.
    """

    client_id: str | None = Field(default=None, description="Azure AD application client ID")
    client_secret: str | None = Field(default=None, description="Azure AD application client secret")
    tenant_id: str | None = Field(default=None, description="Azure AD tenant ID")
    workspace_id: str | None = Field(default=None, description="Fabric workspace ID")
    lakehouse_id: str | None = Field(default=None, description="Fabric lakehouse ID")
    api_base_url: str = Field(default="https://api.fabric.microsoft.com/v1", description="Fabric API base URL")
    session_timeout: int = Field(default=300, description="Session creation timeout in seconds")
    poll_interval: int = Field(default=5, description="Polling interval for session status in seconds")

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    @field_validator("client_id", "client_secret", "tenant_id", mode="before")
    @classmethod
    def validate_required_auth_fields(cls, v, info: ValidationInfo):
        """Validate that authentication fields are not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v

    @classmethod
    def from_env(cls) -> "FabricConnector":
        """
        Factory method to create an instance from environment variables.

        Required environment variables:
        - CLOE_FABRIC_TENANT_ID: Azure AD tenant ID
        - CLOE_FABRIC_CLIENT_ID: Azure AD application client ID
        - CLOE_FABRIC_CLIENT_SECRET: Azure AD application client secret

        Optional environment variables:
        - CLOE_FABRIC_WORKSPACE_ID: Fabric workspace ID
        - CLOE_FABRIC_LAKEHOUSE_ID: Fabric lakehouse ID

        Returns:
            FabricConnector: Configured connector instance

        Raises:
            ValueError: If required environment variables are missing
        """
        load_dotenv(override=True)  # Load environment variables from .env file if present

        tenant_id = os.getenv("CLOE_FABRIC_TENANT_ID")
        client_id = os.getenv("CLOE_FABRIC_CLIENT_ID")
        client_secret = os.getenv("CLOE_FABRIC_CLIENT_SECRET")
        workspace_id = os.getenv("CLOE_FABRIC_WORKSPACE_ID")
        lakehouse_id = os.getenv("CLOE_FABRIC_LAKEHOUSE_ID")

        if not all([tenant_id, client_id, client_secret]):
            missing_vars = [
                var
                for var, val in [
                    ("CLOE_FABRIC_TENANT_ID", tenant_id),
                    ("CLOE_FABRIC_CLIENT_ID", client_id),
                    ("CLOE_FABRIC_CLIENT_SECRET", client_secret),
                ]
                if not val
            ]
            raise ValueError(
                f"Missing required environment variables for service principal authentication: "
                f"{', '.join(missing_vars)}"
            )

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            lakehouse_id=lakehouse_id,
        )

    def _validate_lakehouse_config(self) -> tuple[str, str]:
        """
        Validate that workspace and lakehouse IDs are available.

        Returns:
            tuple[str, str]: workspace_id and lakehouse_id

        Raises:
            FabricConnectionError: If required IDs are missing
        """
        workspace_id = self.workspace_id or os.getenv("CLOE_FABRIC_WORKSPACE_ID")
        lakehouse_id = self.lakehouse_id or os.getenv("CLOE_FABRIC_LAKEHOUSE_ID")

        if not workspace_id:
            raise FabricConnectionError(
                "Workspace ID is required. Set workspace_id or CLOE_FABRIC_WORKSPACE_ID environment variable."
            )

        if not lakehouse_id:
            raise FabricConnectionError(
                "Lakehouse ID is required. Set lakehouse_id or CLOE_FABRIC_LAKEHOUSE_ID environment variable."
            )

        return workspace_id, lakehouse_id

    def _create_token_provider(self) -> TokenProvider:
        """
        Create and return a configured TokenProvider instance.

        Returns:
            TokenProvider: Configured token provider

        Raises:
            FabricConnectionError: If authentication configuration is invalid
        """
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise FabricConnectionError(
                "Missing authentication configuration. Ensure tenant_id, client_id, and client_secret are set."
            )

        return TokenProvider(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

    def _wait_for_session_ready(self, session_url: str, headers: dict, timeout: int | None = None) -> None:
        """
        Wait for the Livy session to be ready.

        Args:
            session_url: URL of the Livy session
            headers: HTTP headers for authentication
            timeout: Maximum time to wait in seconds

        Raises:
            FabricConnectionError: If session doesn't become ready within timeout
        """
        timeout = timeout or self.session_timeout
        start_time = time.time()

        with httpx.Client() as client:
            while True:
                if time.time() - start_time > timeout:
                    raise FabricConnectionError(f"Session did not become ready within {timeout} seconds")

                try:
                    response = client.get(session_url, headers=headers)
                    response.raise_for_status()
                    session_state = response.json().get("state")

                    if session_state == "idle":
                        logger.info("Livy session is ready")
                        return
                    if session_state in ["error", "dead"]:
                        raise FabricConnectionError(f"Session failed with state: {session_state}")

                    logger.info(f"Waiting for session to be ready. Current state: {session_state}")
                    time.sleep(self.poll_interval)

                except httpx.HTTPError as e:
                    raise FabricConnectionError(f"Failed to check session status: {e}") from e

    def get_lakehouse_client(self) -> LakehouseClient:
        """
        Create a LakehouseClient instance with an active Livy session.

        This method:
        1. Validates the required configuration
        2. Creates a token provider for authentication
        3. Creates a new Livy session
        4. Waits for the session to be ready
        5. Returns a configured LakehouseClient

        Returns:
            LakehouseClient: Configured client for lakehouse operations

        Raises:
            FabricConnectionError: If connection setup fails
        """
        try:
            # Validate configuration
            workspace_id, lakehouse_id = self._validate_lakehouse_config()

            # Create token provider
            token_provider = self._create_token_provider()

            # Build session URL
            livy_base_url = (
                f"{self.api_base_url}/workspaces/{workspace_id}/"
                f"lakehouses/{lakehouse_id}/livyApi/versions/2023-12-01/sessions"
            )

            # Prepare headers
            headers = {"Authorization": f"Bearer {token_provider.access_token}"}

            logger.info(f"Creating new Livy session for workspace {workspace_id}, lakehouse {lakehouse_id}")

            # Create Livy session
            with httpx.Client() as client:
                try:
                    response = client.post(livy_base_url, headers=headers, json={})
                    response.raise_for_status()
                    session_data = response.json()
                    session_id = session_data["id"]
                    session_url = f"{livy_base_url}/{session_id}"

                    logger.info(f"Created Livy session with ID: {session_id}")

                except httpx.HTTPError as e:
                    raise FabricConnectionError(f"Failed to create Livy session: {e}") from e

            # Wait for session to be ready
            self._wait_for_session_ready(session_url, headers)

            # Create and return lakehouse client
            client_params = {
                "session_url": session_url,
                "headers": headers,
            }

            logger.info("Successfully created lakehouse client")
            return LakehouseClient(client_params)

        except Exception as e:
            if isinstance(e, FabricConnectionError):
                raise
            logger.error(f"Unexpected error creating lakehouse client: {e}")
            raise FabricConnectionError(f"Failed to create lakehouse client: {e}") from e


def main() -> LakehouseClient:
    """
    Example usage of the FabricConnector.

    This function demonstrates how to create a connector from environment variables
    and obtain a lakehouse client for data operations.
    """
    try:
        logger.info("Creating Fabric connector from environment variables")
        connector = FabricConnector.from_env()

        logger.info("Getting lakehouse client")
        lakehouse_client = connector.get_lakehouse_client()

        logger.info("Fabric connector setup completed successfully")

        return lakehouse_client

    except Exception as e:
        logger.error(f"Failed to setup Fabric connector: {e}")
        raise


if __name__ == "__main__":
    main()
