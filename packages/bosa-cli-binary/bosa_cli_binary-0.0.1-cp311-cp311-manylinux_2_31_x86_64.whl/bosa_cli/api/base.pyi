from _typeshed import Incomplete
from bosa_cli.constants import HTTP_DELETE as HTTP_DELETE, HTTP_GET as HTTP_GET, HTTP_POST as HTTP_POST, HTTP_PUT as HTTP_PUT
from bosa_cli.utils import CLIError as CLIError

class BaseAPIClient:
    """Base API client with shared request functionality."""
    base_url: Incomplete
    session: Incomplete
    def __init__(self, base_url: str) -> None:
        """Initialize base API client.

        Args:
            base_url: BOSA API base URL

        """
