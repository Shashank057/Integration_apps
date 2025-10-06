from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class IntegrationItem(BaseModel):
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    parent_id: Optional[str] = None
    parent_name: Optional[str] = None
    created_time: Optional[str] = None
    updated_time: Optional[str] = None
    url: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123",
                "name": "Example Item",
                "type": "page",
                "created_time": "2023-01-01T00:00:00.000Z"
            }
        }


class Credentials(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    token_type: Optional[str] = "Bearer"