import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from bosa_cli.config import CLIConfig as CLIConfig
from bosa_cli.constants import AUTH_LOGIN_HELP as AUTH_LOGIN_HELP
from bosa_cli.utils import print_error as print_error, print_info as print_info

class BaseCommands(ABC, metaclass=abc.ABCMeta):
    """Base class for all CLI commands."""
    config: Incomplete
    def __init__(self, config: CLIConfig | None = None) -> None:
        """Initialize the base commands.

        Args:
            config: CLI configuration

        """
    @classmethod
    @abstractmethod
    def add_subparser(cls, subparsers) -> None:
        """Add command-specific subparser and arguments.

        Args:
            subparsers: Parent subparsers object

        Returns:
            The command parser for help display (optional)

        """
    @abstractmethod
    def handle(self, args) -> int:
        """Handle the command execution.

        Returns:
            Exit code (0 for success, non-zero for error)

        """
