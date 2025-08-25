from bosa_cli.api.base import BaseAPIClient as BaseAPIClient
from bosa_cli.api.models import BosaUser as BosaUser, CreatedBosaUser as CreatedBosaUser
from bosa_cli.constants import API_KEY_HEADER as API_KEY_HEADER, AUTHORIZATION_HEADER as AUTHORIZATION_HEADER, BEARER_PREFIX as BEARER_PREFIX, HTTP_GET as HTTP_GET, HTTP_POST as HTTP_POST
from bosa_cli.utils import CLIError as CLIError

class UsersAPIClient(BaseAPIClient):
    """Users API client."""
    def create_user(self, client_key: str, username: str) -> CreatedBosaUser:
        """Create a new user.

        Args:
            client_key: Client API key
            username: Username for the new user

        Returns:
            BosaUser: User creation response data

        Raises:
            CLIError: If user creation fails

        """
    def get_user_info(self, client_key: str, token: str) -> BosaUser:
        """Get current user information.

        Args:
            client_key: Client API key
            token: User JWT token

        Returns:
            BosaUser: User information

        Raises:
            CLIError: If request fails

        """
