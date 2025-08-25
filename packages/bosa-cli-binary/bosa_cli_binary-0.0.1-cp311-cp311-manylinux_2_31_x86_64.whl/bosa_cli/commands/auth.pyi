from _typeshed import Incomplete
from bosa_cli.api import AuthAPIClient as AuthAPIClient
from bosa_cli.commands.base import BaseCommands as BaseCommands
from bosa_cli.config import CLIConfig as CLIConfig
from bosa_cli.constants import AUTH_LOGIN_EPILOG as AUTH_LOGIN_EPILOG, AUTH_MAIN_EPILOG as AUTH_MAIN_EPILOG, DEFAULT_API_URL as DEFAULT_API_URL, EXIT_AUTH_ERROR as EXIT_AUTH_ERROR, EXIT_GENERAL_ERROR as EXIT_GENERAL_ERROR, EXIT_INVALID_SUBCOMMAND as EXIT_INVALID_SUBCOMMAND
from bosa_cli.utils import CLIError as CLIError, fail as fail, mask_client_key as mask_client_key, mask_token as mask_token, print_header as print_header, print_info as print_info, print_success as print_success, prompt_for_input as prompt_for_input, succeed as succeed

class AuthCommands(BaseCommands):
    """Authentication command handlers."""
    api_client: Incomplete
    def __init__(self, config: CLIConfig | None = None) -> None:
        """Initialize auth commands.

        Args:
            config: CLI configuration (optional for parser setup)

        """
    @classmethod
    def add_subparser(cls, subparsers):
        """Add command-specific subparser and arguments (class method).

        Args:
            subparsers: Parent subparsers object

        Returns:
            The auth parser for help display

        """
    @classmethod
    def auth_error_handler(cls, message):
        """Handle authentication errors.

        Args:
            message: Error message

        Returns:
            Exit code (0 for success, 3 for invalid subcommand)

        """
    def handle(self, args):
        """Handle auth commands.

        Args:
            args: Parsed command line arguments

        Returns:
            Exit code (0 for success, 1 for error)

        """
    def login(self, client_api_key: str | None = None, username: str | None = None, user_secret: str | None = None, api_url: str = ...) -> int:
        """Login with client API key and user credentials.

        Args:
            client_api_key: Client API key (sk-client-...)
            username: User identifier
            user_secret: User secret
            api_url: BOSA API base URL

        Returns:
            Exit code (0 for success, 1 for error)

        """
    def logout(self) -> int:
        """Logout and clear session.

        Returns:
            Exit code (0 for success, 1 for error)

        """
    def status(self) -> int:
        """Show authentication status.

        Returns:
            Exit code (0 for success, 1 for error)

        """
