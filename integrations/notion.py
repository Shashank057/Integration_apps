import httpx
from fastapi import HTTPException
from typing import List
import redis
import json
from config import NOTION_CLIENT_ID, NOTION_CLIENT_SECRET, NOTION_REDIRECT_URI, REDIS_HOST, REDIS_PORT
from models import IntegrationItem, Credentials

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)


def authorize_notion(state: str) -> str:
    auth_url = (
        f"https://api.notion.com/v1/oauth/authorize"
        f"?client_id={NOTION_CLIENT_ID}"
        f"&redirect_uri={NOTION_REDIRECT_URI}"
        f"&response_type=code"
        f"&owner=user"
        f"&state={state}"
    )
    return auth_url


async def oauth2callback_notion(code: str, state: str) -> dict:
    token_url = "https://api.notion.com/v1/oauth/token"
    
    import base64
    auth_string = f"{NOTION_CLIENT_ID}:{NOTION_CLIENT_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json"
    }
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": NOTION_REDIRECT_URI
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, json=data, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")
        
        token_data = response.json()
        
        redis_client.setex(
            f"notion_credentials:{state}",
            3600,
            json.dumps(token_data)
        )
        
        return token_data


def get_notion_credentials(state: str) -> Credentials:
    creds_json = redis_client.get(f"notion_credentials:{state}")
    
    if not creds_json:
        raise HTTPException(status_code=404, detail="Credentials not found")
    
    creds_data = json.loads(creds_json)
    return Credentials(
        access_token=creds_data.get("access_token"),
        refresh_token=creds_data.get("refresh_token"),
        expires_in=creds_data.get("expires_in"),
        token_type=creds_data.get("token_type", "Bearer")
    )


async def get_items_notion(credentials: Credentials) -> List[IntegrationItem]:
    items = []
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    async with httpx.AsyncClient() as client:
        search_response = await client.post(
            "https://api.notion.com/v1/search",
            headers=headers,
            json={"page_size": 100}
        )
        
        if search_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to search Notion")
        
        search_data = search_response.json()
        results = search_data.get("results", [])
        
        for result in results:
            item_id = result.get("id")
            item_type = result.get("object")
            
            title = ""
            if item_type == "database":
                title_list = result.get("title", [])
                if title_list:
                    title = title_list[0].get("plain_text", "")
            elif item_type == "page":
                properties = result.get("properties", {})
                title_prop = properties.get("title", {})
                title_list = title_prop.get("title", [])
                if title_list:
                    title = title_list[0].get("plain_text", "")
            
            created_time = result.get("created_time")
            last_edited_time = result.get("last_edited_time")
            url = result.get("url")
            parent = result.get("parent", {})
            parent_type = parent.get("type")
            
            items.append(IntegrationItem(
                id=item_id,
                name=title or f"Untitled {item_type}",
                type=item_type,
                created_time=created_time,
                updated_time=last_edited_time,
                url=url,
                properties={"parent_type": parent_type}
            ))
    
    return items