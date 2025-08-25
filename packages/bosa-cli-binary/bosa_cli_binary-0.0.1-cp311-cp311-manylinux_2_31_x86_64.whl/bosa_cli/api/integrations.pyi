from bosa_cli.api.base import BaseAPIClient as BaseAPIClient
from bosa_cli.api.models import IntegrationDetail as IntegrationDetail
from bosa_cli.constants import API_KEY_HEADER as API_KEY_HEADER, AUTHORIZATION_HEADER as AUTHORIZATION_HEADER, BEARER_PREFIX as BEARER_PREFIX, HTTP_DELETE as HTTP_DELETE, HTTP_GET as HTTP_GET, HTTP_POST as HTTP_POST
from bosa_cli.utils import CLIError as CLIError
from typing import Any

class IntegrationsAPIClient(BaseAPIClient):
    """Integrations API client."""
    def get_connectors(self, client_key: str) -> list[str]:
        """Get all available connectors.

        Args:
            client_key: Client API key

        Returns:
            List of available connectors

        Raises:
            CLIError: If request fails

        """
    def check_integration_status(self, client_key: str, connector_name: str, token: str) -> bool:
        """Check if integration exists for a connector.

        Args:
            client_key: Client API key
            connector_name: Name of the connector
            token: User JWT token

        Returns:
            Integration status information (True if integration exists, False otherwise)

        Raises:
            CLIError: If request fails

        """
    def initiate_integration(self, client_key: str, connector_name: str, token: str) -> str:
        """Initiate OAuth integration for a connector.

        Args:
            client_key: Client API key
            connector_name: Name of the connector
            token: User JWT token

        Returns:
            str: Integration initiation response (contains OAuth URL)

        Raises:
            CLIError: If request fails

        """
    def remove_integration(self, client_key: str, connector_name: str, user_identifier: str, token: str) -> dict[str, Any]:
        """Remove integration for a connector and specific user identifier.

        Args:
            client_key: Client API key
            connector_name: Name of the connector
            user_identifier: User identifier to specify which integration to remove
            token: User JWT token

        Returns:
            Removal response

        Raises:
            CLIError: If request fails

        """
    def get_integration_details_by_identifier(self, client_key: str, connector: str, user_identifier: str, token: str) -> IntegrationDetail:
        """Get a specific integration by user identifier.

        Args:
            client_key: Client API key
            connector: Connector name
            user_identifier: The third-party service user identifier (e.g., GitHub username, Google email)
            token: User token

        Returns:
            Integration details including access token

        Raises:
            CLIError: If request fails or integration not found

        """
    def set_selected_integration(self, client_key: str, connector_name: str, user_identifier: str, token: str) -> dict[str, Any]:
        """Set integration as selected/unselected.

        Args:
            client_key: Client API key
            connector_name: Name of the connector
            user_identifier: User identifier for the integration
            token: User JWT token

        Returns:
            Update response

        Raises:
            CLIError: If request fails

        """
