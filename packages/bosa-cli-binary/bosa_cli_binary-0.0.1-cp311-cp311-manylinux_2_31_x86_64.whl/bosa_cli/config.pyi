from _typeshed import Incomplete
from bosa_cli.constants import AUTH_NOT_AUTHENTICATED as AUTH_NOT_AUTHENTICATED, DEFAULT_API_URL as DEFAULT_API_URL
from bosa_cli.utils import CLIError as CLIError
from dataclasses import dataclass
from typing import Any

@dataclass
class CLISession:
    """CLI authentication session storage."""
    client_api_key: str
    api_url: str
    username: str
    token: str
    token_type: str
    expires_at: str
    user_id: str
    is_revoked: bool
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CLISession:
        """Create from dictionary."""

class CLIConfig:
    """Configuration management for BOSA CLI."""
    DEFAULT_CONFIG_DIR: Incomplete
    DEFAULT_CONFIG_FILE: str
    config_path: Incomplete
    config_dir: Incomplete
    api_url: Incomplete
    def __init__(self) -> None:
        """Initialize CLI configuration."""
    def save_session(self, client_api_key: str, api_url: str, username: str, token: str, token_type: str, expires_at: str, user_id: str, is_revoked: bool) -> None:
        '''Save authentication session.

        Args:
            client_api_key: Client API key
            api_url: BOSA API base URL
            username: User identifier
            token: JWT token
            token_type: Token type (usually "Bearer")
            expires_at: Token expiration time
            user_id: User ID
            is_revoked: Is revoked

        '''
    def get_session(self) -> CLISession | None:
        """Get stored session.

        Returns:
            Stored session or None if not found

        """
    def clear_session(self) -> None:
        """Clear stored session."""
    def is_authenticated(self) -> bool:
        """Check if user is authenticated.

        Returns:
            True if session is stored

        """
    def get_client_key(self) -> str:
        """Get client API key.

        Returns:
            Client API key

        Raises:
            CLIError: If not authenticated

        """
    def get_username(self) -> str:
        """Get username.

        Returns:
            Username

        Raises:
            CLIError: If not authenticated

        """
    def get_token(self) -> str:
        """Get JWT token.

        Returns:
            JWT token

        Raises:
            CLIError: If not authenticated

        """
    def get_api_url(self) -> str:
        """Get API URL.

        Returns:
            API base URL (uses stored session URL or default)

        """
