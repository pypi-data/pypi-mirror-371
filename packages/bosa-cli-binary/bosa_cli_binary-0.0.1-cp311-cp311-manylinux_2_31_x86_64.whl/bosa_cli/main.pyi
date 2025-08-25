from argparse import ArgumentParser
from bosa_cli.commands.base import BaseCommands as BaseCommands
from bosa_cli.config import CLIConfig as CLIConfig
from bosa_cli.constants import EXIT_GENERAL_ERROR as EXIT_GENERAL_ERROR, EXIT_INVALID_SUBCOMMAND as EXIT_INVALID_SUBCOMMAND, MAIN_EPILOG as MAIN_EPILOG
from bosa_cli.utils import fail as fail, print_error as print_error

def discover_commands() -> dict[str, BaseCommands]:
    """Discover command modules from the commands folder.

    Returns:
        Dict of command name to command class

    """
def create_parser() -> tuple[ArgumentParser, dict[str, BaseCommands]]:
    """Create argument parser for BOSA CLI.

    Returns:
        Configured argument parser

    """
def main() -> int:
    """Run the main CLI entry point.

    Returns:
        Exit code (0 for success, non-zero for error)

    """
