import os
import httpx
import secrets
import urllib.parse
from typing import Dict, Any

class NotionIntegration:
    def __init__(self):
        self.client_id = os.getenv("NOTION_CLIENT_ID")
        self.client_secret = os.getenv("NOTION_CLIENT_SECRET")
        self.redirect_uri = os.getenv("BACKEND_URL", "http://localhost:8000") + "/integrations/notion/oauth2callback"
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Notion client ID and secret must be set in environment variables")
    
    def get_auth_url(self) -> str:
        """Generate Notion OAuth authorization URL"""
        state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "owner": "user",
            "state": state
        }
        
        base_url = "https://api.notion.com/v1/oauth/authorize"
        query_string = urllib.parse.urlencode(params)
        
        return f"{base_url}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        token_url = "https://api.notion.com/v1/oauth/token"
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        auth = (self.client_id, self.client_secret)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data=data,
                auth=auth,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Token exchange failed: {response.text}")
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Notion"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Notion-Version": "2022-06-28"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.notion.com/v1/users/me",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get user info: {response.text}")
            
            return response.json()
