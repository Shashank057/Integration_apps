from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class OAuthCredentials(BaseModel):
    access_token: str
    token_type: Optional[str] = "Bearer"
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None

class AirtableCredentials(OAuthCredentials):
    pass

class NotionCredentials(OAuthCredentials):
    workspace_id: Optional[str] = None
    workspace_name: Optional[str] = None
    bot_id: Optional[str] = None

class HubSpotCredentials(OAuthCredentials):
    pass

class Item(BaseModel):
    id: str
    name: Optional[str] = None
    type: str
    url: Optional[str] = None
    created_time: Optional[str] = None
    parent_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ItemsResponse(BaseModel):
    items: List[Item]
    count: int



