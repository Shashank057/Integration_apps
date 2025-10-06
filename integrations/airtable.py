import httpx
import uuid
import base64
import hashlib
from urllib.parse import urlencode
from typing import Dict, List
import config

# In-memory storage for demo (use database in production)
credentials_store: Dict[str, dict] = {}

def get_authorization_url() -> str:
    """Generate Airtable OAuth authorization URL with PKCE"""
    state = str(uuid.uuid4())
    
    # Generate PKCE code challenge
    code_verifier = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    # Store code verifier for later use
    credentials_store[f"code_verifier_{state}"] = code_verifier
    
    params = {
        "client_id": config.AIRTABLE_CLIENT_ID,
        "redirect_uri": config.AIRTABLE_REDIRECT_URI,
        "response_type": "code",
        "state": state,
        "scope": "data.records:read data.recordComments:read schema.bases:read",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    
    auth_url = f"https://airtable.com/oauth2/v1/authorize?{urlencode(params)}"
    return auth_url

async def exchange_code_for_token(code: str, state: str) -> dict:
    """Exchange authorization code for access token with PKCE"""
    token_url = "https://airtable.com/oauth2/v1/token"
    
    # Get the code verifier for this state
    code_verifier = credentials_store.get(f"code_verifier_{state}")
    if not code_verifier:
        raise ValueError("Code verifier not found for state")
    
    data = {
        "client_id": config.AIRTABLE_CLIENT_ID,
        "code": code,
        "code_verifier": code_verifier,
        "grant_type": "authorization_code",
        "redirect_uri": config.AIRTABLE_REDIRECT_URI
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        response.raise_for_status()
        return response.json()

def store_credentials(state: str, credentials: dict):
    """Store credentials for later retrieval"""
    credentials_store[state] = credentials

def get_credentials(state: str) -> dict:
    """Retrieve stored credentials"""
    return credentials_store.get(state)

async def get_items(credentials: dict) -> List[dict]:
    """Fetch bases and tables from Airtable"""
    access_token = credentials.get("access_token")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    items = []
    
    async with httpx.AsyncClient() as client:
        # Get bases (meta API)
        bases_response = await client.get(
            "https://api.airtable.com/v0/meta/bases",
            headers=headers
        )
        
        if bases_response.status_code == 200:
            bases_data = bases_response.json()
            bases = bases_data.get("bases", [])
            
            for base in bases[:5]:  # Limit to 5 bases for demo
                items.append({
                    "id": base.get("id"),
                    "name": base.get("name"),
                    "type": "base",
                    "url": f"https://airtable.com/{base.get('id')}",
                    "created_time": None
                })
                
                # Get tables for this base
                try:
                    tables_response = await client.get(
                        f"https://api.airtable.com/v0/meta/bases/{base.get('id')}/tables",
                        headers=headers
                    )
                    
                    if tables_response.status_code == 200:
                        tables_data = tables_response.json()
                        tables = tables_data.get("tables", [])
                        
                        for table in tables[:3]:  # Limit to 3 tables per base
                            items.append({
                                "id": table.get("id"),
                                "name": table.get("name"),
                                "type": "table",
                                "parent_name": base.get("name"),
                                "url": f"https://airtable.com/{base.get('id')}/{table.get('id')}",
                                "created_time": None
                            })
                except Exception as e:
                    print(f"Error fetching tables for base {base.get('id')}: {e}")
        
    return items



