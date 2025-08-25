from datetime import datetime
from pydantic import BaseModel
from typing import Any

class BosaUser(BaseModel):
    """BOSA user information."""
    id: str
    identifier: str
    secret_preview: str
    is_active: bool
    client_id: str
    integrations: list[dict[str, Any]]

class CreatedBosaUser(BosaUser):
    """BOSA user information with secret."""
    secret: str

class BosaToken(BaseModel):
    """BOSA authentication token."""
    token: str
    token_type: str
    expires_at: datetime
    is_revoked: bool
    user_id: str

class IntegrationDetail(BaseModel):
    """Integration detail."""
    connector: str
    user_identifier: str
    auth_string: str
    auth_scopes: list[str]
    selected: bool
