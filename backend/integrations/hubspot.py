import os
import httpx
import secrets
import urllib.parse
from typing import Dict, Any

class HubSpotIntegration:
    def __init__(self):
        self.client_id = os.getenv("HUBSPOT_CLIENT_ID")
        self.client_secret = os.getenv("HUBSPOT_CLIENT_SECRET")
        self.redirect_uri = os.getenv("BACKEND_URL", "http://localhost:8000") + "/integrations/hubspot/oauth2callback"
        
        if not self.client_id or not self.client_secret:
            raise ValueError("HubSpot client ID and secret must be set in environment variables")
    
    def get_auth_url(self) -> str:
        """Generate HubSpot OAuth authorization URL"""
        state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "crm.objects.contacts.read crm.objects.companies.read crm.objects.deals.read crm.schemas.contacts.read crm.schemas.companies.read crm.schemas.deals.read oauth",
            "state": state
        }
        
        base_url = "https://app.hubspot.com/oauth/authorize"
        query_string = urllib.parse.urlencode(params)
        
        return f"{base_url}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        token_url = "https://api.hubapi.com/oauth/v1/token"
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Token exchange failed: {response.text}")
            
            return response.json()
    
    async def get_contacts(self, access_token: str) -> Dict[str, Any]:
        """Get contacts from HubSpot"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.hubapi.com/crm/v3/objects/contacts",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get contacts: {response.text}")
            
            return response.json()
