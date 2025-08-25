from _typeshed import Incomplete
from bosa_cli.constants import EXIT_GENERAL_ERROR as EXIT_GENERAL_ERROR, EXIT_SUCCESS as EXIT_SUCCESS
from datetime import datetime
from typing import Any

class Colors:
    """ANSI color codes for terminal output."""
    GREEN: str
    RED: str
    YELLOW: str
    BLUE: str
    BOLD: str
    RESET: str

class CLIError(Exception):
    """Custom exception for CLI errors."""
    data: Incomplete
    def __init__(self, message: str, data: dict[str, Any] | None = None) -> None:
        """Initialize CLIError.

        Args:
            message: Error message
            data: Optional error data

        """

def print_success(message: str) -> None:
    """Print success message in green.

    Args:
        message: Success message to print

    """
def print_error(message: str) -> None:
    """Print error message in red.

    Args:
        message: Error message to print

    """
def print_warning(message: str) -> None:
    """Print warning message in yellow.

    Args:
        message: Warning message to print

    """
def print_info(message: str) -> None:
    """Print info message in blue.

    Args:
        message: Info message to print

    """
def print_header(title: str) -> None:
    """Print section header.

    Args:
        title: Header title

    """
def print_table(headers: list[str], rows: list[list[str]], title: str | None = None) -> None:
    """Print a formatted table.

    Args:
        headers: Table headers
        rows: Table rows
        title: Optional table title

    """
def prompt_for_input(prompt: str, default: str | None = None, hide: bool = False, required: bool = True) -> str:
    """Prompt user for input.

    Args:
        prompt (str): Input prompt
        default (Optional[str]): Default value
        hide (bool): Whether to hide input
        required (bool): Whether input is required

    Returns:
        str: User input

    Raises:
        CLIError: If required input is not provided

    """
def confirm_action(message: str, default: bool = False) -> bool:
    """Confirm user action.

    Args:
        message: Confirmation message
        default: Default response

    Returns:
        True if user confirms

    """
def mask_string(api_key: str, visible_rear: int = 4, visible_front: int = 0, preserve_prefix: str = None, min_mask_length: int = 12) -> str:
    '''Mask API key for display with flexible front/rear visibility.

    Args:
        api_key: API key to mask
        visible_rear: Number of characters to show at the end (default: 4)
        visible_front: Number of characters to show at the front (default: 0)
        preserve_prefix: If provided, preserve this prefix if key starts with it (e.g., "sk-client-")
        min_mask_length: Minimum length before masking is applied (default: 12)

    Returns:
        Masked API key in various formats:
        - With prefix: "sk-client-...XXXX"
        - Front+rear: "XXXX...YYYY"
        - Rear only: "...XXXX"

    Examples:
        mask_api_key("sk-client-abc123def456", preserve_prefix="sk-client-") -> "sk-client-...f456"
        mask_api_key("jwt.token.here", visible_front=4, visible_rear=4) -> "jwt....here"
        mask_api_key("longtoken123456", visible_rear=4) -> "...3456"

    '''
def mask_client_key(api_key: str, visible_rear: int = 4) -> str:
    """Mask BOSA client keys (sk-client-...).

    Args:
        api_key: Client key to mask
        visible_rear: Number of characters to show at the end

    Returns:
        Masked key in format: sk-client-...XXXX

    """
def mask_token(token: str, visible_front: int = 4, visible_rear: int = 4) -> str:
    """Mask JWT tokens showing front and rear.

    Args:
        token: JWT token to mask
        visible_front: Number of characters to show at the front
        visible_rear: Number of characters to show at the rear

    Returns:
        Masked token in format: XXXX...YYYY

    """
def format_datetime(dt: datetime) -> str:
    """Format datetime for display.

    Args:
        dt: Datetime to format

    Returns:
        Formatted datetime string

    """
def format_connector_status(has_integration: bool) -> str:
    """Format connector status for display.

    Args:
        has_integration: Whether connector has integration

    Returns:
        Formatted status string

    """
def fail(message: str, exit_code: int = ...) -> int:
    """Print error and return with specified code.

    Args:
        message: Error message to display
        exit_code: Exit code to use (auto-detects if None)

    """
def succeed(message: str | None = None) -> int:
    """Print success message and return with code 0.

    Args:
        message: Optional success message to display

    """
