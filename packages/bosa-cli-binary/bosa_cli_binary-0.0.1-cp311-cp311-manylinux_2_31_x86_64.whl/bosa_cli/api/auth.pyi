from bosa_cli.api.base import BaseAPIClient as BaseAPIClient
from bosa_cli.api.models import BosaToken as BosaToken
from bosa_cli.constants import API_KEY_HEADER as API_KEY_HEADER, HTTP_POST as HTTP_POST
from bosa_cli.utils import CLIError as CLIError

class AuthAPIClient(BaseAPIClient):
    """Authentication API client."""
    def authenticate_user(self, client_key: str, identifier: str, secret: str) -> BosaToken:
        """Authenticate user and get JWT token.

        Args:
            client_key: Client API key
            identifier: User identifier
            secret: User secret

        Returns:
            Authentication token information

        Raises:
            CLIError: If authentication fails

        """
