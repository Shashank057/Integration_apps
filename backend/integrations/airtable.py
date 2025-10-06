import os
import httpx
import secrets
import urllib.parse
import base64
import hashlib
from typing import Dict, Any

class AirtableIntegration:
    def __init__(self):
        self.client_id = os.getenv("AIRTABLE_CLIENT_ID")
        self.client_secret = os.getenv("AIRTABLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("BACKEND_URL", "http://localhost:8000") + "/integrations/airtable/oauth2callback"
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Airtable client ID and secret must be set in environment variables")
    
    def get_auth_url(self) -> str:
        """Generate Airtable OAuth authorization URL with PKCE"""
        state = secrets.token_urlsafe(32)
        
        # Generate PKCE parameters
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": "data.records:read data.records:write schema.bases:read",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        
        base_url = "https://airtable.com/oauth2/v1/authorize"
        query_string = urllib.parse.urlencode(params)
        
        return f"{base_url}?{query_string}"
    
    async def exchange_code_for_token(self, code: str, code_verifier: str = None) -> Dict[str, Any]:
        """Exchange authorization code for access token with PKCE"""
        token_url = "https://airtable.com/oauth2/v1/token"
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
            "code_verifier": code_verifier or secrets.token_urlsafe(32)  # Fallback if not provided
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
    
    async def get_bases(self, access_token: str) -> Dict[str, Any]:
        """Get Airtable bases"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.airtable.com/v0/meta/bases",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get bases: {response.text}")
            
            return response.json()