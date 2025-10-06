import httpx
from fastapi import HTTPException
from typing import List
import redis
import json
import hashlib
import base64
import secrets
from config import AIRTABLE_CLIENT_ID, AIRTABLE_CLIENT_SECRET, AIRTABLE_REDIRECT_URI, REDIS_HOST, REDIS_PORT
from models import IntegrationItem, Credentials

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)


def authorize_airtable(state: str) -> str:
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    redis_client.setex(
        f"airtable_code_verifier:{state}",
        600,
        code_verifier
    )
    
    scope = "data.records:read data.records:write schema.bases:read"
    auth_url = (
        f"https://airtable.com/oauth2/v1/authorize"
        f"?client_id={AIRTABLE_CLIENT_ID}"
        f"&redirect_uri={AIRTABLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&state={state}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
    )
    return auth_url


async def oauth2callback_airtable(code: str, state: str) -> dict:
    code_verifier = redis_client.get(f"airtable_code_verifier:{state}")
    if not code_verifier:
        raise HTTPException(status_code=400, detail="Code verifier not found or expired")
    
    token_url = "https://airtable.com/oauth2/v1/token"
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": AIRTABLE_REDIRECT_URI,
        "client_id": AIRTABLE_CLIENT_ID,
        "code_verifier": code_verifier,
    }
    
    import base64 as b64
    auth_string = f"{AIRTABLE_CLIENT_ID}:{AIRTABLE_CLIENT_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = b64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to obtain access token: {response.text}"
            )
        
        token_data = response.json()
        
        redis_client.setex(
            f"airtable_credentials:{state}",
            3600,
            json.dumps(token_data)
        )
        
        redis_client.delete(f"airtable_code_verifier:{state}")
        
        return token_data


def get_airtable_credentials(state: str) -> Credentials:
    creds_json = redis_client.get(f"airtable_credentials:{state}")
    
    if not creds_json:
        raise HTTPException(status_code=404, detail="Credentials not found")
    
    creds_data = json.loads(creds_json)
    return Credentials(
        access_token=creds_data.get("access_token"),
        refresh_token=creds_data.get("refresh_token"),
        expires_in=creds_data.get("expires_in"),
        token_type=creds_data.get("token_type", "Bearer")
    )


async def get_items_airtable(credentials: Credentials) -> List[IntegrationItem]:
    items = []
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        bases_response = await client.get(
            "https://api.airtable.com/v0/meta/bases",
            headers=headers
        )
        
        if bases_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch Airtable bases")
        
        bases_data = bases_response.json()
        bases = bases_data.get("bases", [])
        
        for base in bases:
            base_id = base.get("id")
            base_name = base.get("name")
            
            items.append(IntegrationItem(
                id=base_id,
                name=base_name,
                type="base",
                url=f"https://airtable.com/{base_id}"
            ))
            
            tables_response = await client.get(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
                headers=headers
            )
            
            if tables_response.status_code == 200:
                tables_data = tables_response.json()
                tables = tables_data.get("tables", [])
                
                for table in tables:
                    table_id = table.get("id")
                    table_name = table.get("name")
                    
                    items.append(IntegrationItem(
                        id=table_id,
                        name=table_name,
                        type="table",
                        parent_id=base_id,
                        parent_name=base_name,
                        url=f"https://airtable.com/{base_id}/{table_id}",
                        properties={"fields": table.get("fields", [])}
                    ))
    
    return items