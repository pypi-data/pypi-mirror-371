from _typeshed import Incomplete
from bosa_cli.api import IntegrationsAPIClient as IntegrationsAPIClient, UsersAPIClient as UsersAPIClient
from bosa_cli.api.models import BosaUser as BosaUser
from bosa_cli.commands.base import BaseCommands as BaseCommands
from bosa_cli.config import CLIConfig as CLIConfig
from bosa_cli.constants import CONNECTOR_FIELD as CONNECTOR_FIELD, EXIT_AUTH_ERROR as EXIT_AUTH_ERROR, EXIT_GENERAL_ERROR as EXIT_GENERAL_ERROR, EXIT_INVALID_SUBCOMMAND as EXIT_INVALID_SUBCOMMAND, EXIT_REQUEST_ERROR as EXIT_REQUEST_ERROR, HELP_CONNECTOR as HELP_CONNECTOR, HELP_IDENTIFIER as HELP_IDENTIFIER, INTEGRATIONS_ADD_EPILOG as INTEGRATIONS_ADD_EPILOG, INTEGRATIONS_COUNT_FIELD as INTEGRATIONS_COUNT_FIELD, INTEGRATIONS_MAIN_EPILOG as INTEGRATIONS_MAIN_EPILOG, INTEGRATIONS_REMOVE_EPILOG as INTEGRATIONS_REMOVE_EPILOG, INTEGRATIONS_SHOW_EPILOG as INTEGRATIONS_SHOW_EPILOG, METAVAR_ACCOUNT as METAVAR_ACCOUNT, METAVAR_CONNECTOR as METAVAR_CONNECTOR, USER_IDENTIFIER_FIELD as USER_IDENTIFIER_FIELD
from bosa_cli.utils import CLIError as CLIError, confirm_action as confirm_action, fail as fail, print_error as print_error, print_header as print_header, print_info as print_info, print_success as print_success, print_table as print_table, print_warning as print_warning, succeed as succeed

class IntegrationsCommands(BaseCommands):
    """Integration management command handlers."""
    integrations_api_client: Incomplete
    users_api_client: Incomplete
    def __init__(self, config: CLIConfig | None = None) -> None:
        """Initialize integration commands.

        Args:
            config: CLI configuration (optional for parser setup)

        """
    @classmethod
    def add_subparser(cls, subparsers):
        """Add command-specific subparser and arguments (class method).

        Args:
            subparsers: Parent subparsers object

        Returns:
            The integrations parser for help display

        """
    @classmethod
    def integrations_error_handler(cls, message: str) -> None:
        """Handle integration command errors.

        Args:
            message: Error message

        """
    def handle(self, args):
        """Handle integration commands.

        Args:
            args: Parsed command line arguments

        Returns:
            Exit code (0 for success, 1 for error)

        """
    def list_integrations(self) -> int:
        """List all integrations (like the dashboard).

        Returns:
            Exit code (0 for success, 1 for error)

        """
    def add_integration(self, connector: str) -> int:
        """Add a new integration.

        Args:
            connector: Connector name

        Returns:
            Exit code (0 for success, 1 for error)

        """
    def remove_integration(self, connector: str, account: str) -> int:
        """Remove an integration.

        Args:
            connector: Connector name
            account: Account identifier

        Returns:
            Exit code (0 for success, 1 for error)

        """
    def show_integration(self, connector: str, identifier: str = None) -> int:
        """Show integration details for a connector.

        Args:
            connector: Connector name
            identifier: Optional user identifier for specific integration

        Returns:
            Exit code (0 for success, 1 for error)

        """
    def select_integration(self, connector: str, account: str) -> int:
        """Select or unselect an integration.

        Args:
            connector: Connector name
            account: Account identifier

        Returns:
            Exit code (0 for success, 1 for error)

        """
