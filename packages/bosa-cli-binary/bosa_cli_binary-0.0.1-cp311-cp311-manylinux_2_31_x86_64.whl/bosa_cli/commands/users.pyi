from _typeshed import Incomplete
from bosa_cli.api import UsersAPIClient as UsersAPIClient
from bosa_cli.commands.base import BaseCommands as BaseCommands
from bosa_cli.config import CLIConfig as CLIConfig
from bosa_cli.constants import EXIT_AUTH_ERROR as EXIT_AUTH_ERROR, EXIT_INVALID_SUBCOMMAND as EXIT_INVALID_SUBCOMMAND, EXIT_REQUEST_ERROR as EXIT_REQUEST_ERROR, USERS_CREATE_EPILOG as USERS_CREATE_EPILOG, USERS_MAIN_EPILOG as USERS_MAIN_EPILOG
from bosa_cli.utils import CLIError as CLIError, fail as fail, print_header as print_header, print_info as print_info, print_success as print_success, print_warning as print_warning, succeed as succeed

class UsersCommands(BaseCommands):
    """User management command handlers."""
    api_client: Incomplete
    def __init__(self, config: CLIConfig | None = None) -> None:
        """Initialize user commands.

        Args:
            config: CLI configuration (optional for parser setup)

        """
    @classmethod
    def add_subparser(cls, subparsers):
        """Add command-specific subparser and arguments (class method).

        Args:
            subparsers: Parent subparsers object

        Returns:
            The users parser for help display

        """
    @classmethod
    def users_error_handler(cls, message: str) -> None:
        """Handle user command errors.

        Args:
            message: Error message

        """
    def handle(self, args):
        """Handle user commands.

        Args:
            args: Parsed command line arguments

        Returns:
            Exit code (0 for success, 1 for error)

        """
    def create_user(self, username: str) -> int:
        """Create a new user.

        Args:
            username: Username for the new user

        Returns:
            Exit code (0 for success, 1 for error)

        """
