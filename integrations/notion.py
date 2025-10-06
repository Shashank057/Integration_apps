import httpx
import uuid
from urllib.parse import urlencode
from typing import Dict, List
import config

# In-memory storage for demo (use database in production)
credentials_store: Dict[str, dict] = {}

def get_authorization_url() -> str:
    """Generate Notion OAuth authorization URL"""
    state = str(uuid.uuid4())
    
    params = {
        "client_id": config.NOTION_CLIENT_ID,
        "redirect_uri": config.NOTION_REDIRECT_URI,
        "response_type": "code",
        "owner": "user",
        "state": state
    }
    
    auth_url = f"https://api.notion.com/v1/oauth/authorize?{urlencode(params)}"
    return auth_url

async def exchange_code_for_token(code: str) -> dict:
    """Exchange authorization code for access token"""
    token_url = "https://api.notion.com/v1/oauth/token"
    
    auth = (config.NOTION_CLIENT_ID, config.NOTION_CLIENT_SECRET)
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.NOTION_REDIRECT_URI
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, auth=auth, json=data)
        response.raise_for_status()
        return response.json()

def store_credentials(state: str, credentials: dict):
    """Store credentials for later retrieval"""
    credentials_store[state] = credentials

def get_credentials(state: str) -> dict:
    """Retrieve stored credentials"""
    return credentials_store.get(state)

async def get_items(credentials: dict) -> List[dict]:
    """Fetch pages and databases from Notion"""
    access_token = credentials.get("access_token")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    items = []
    
    async with httpx.AsyncClient() as client:
        # Search for pages and databases
        search_response = await client.post(
            "https://api.notion.com/v1/search",
            headers=headers,
            json={
                "page_size": 20
            }
        )
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            results = search_data.get("results", [])
            
            for result in results:
                item_type = result.get("object")
                item_id = result.get("id")
                
                # Get title
                title = "Untitled"
                if item_type == "page":
                    properties = result.get("properties", {})
                    title_prop = properties.get("title", {})
                    if title_prop and "title" in title_prop:
                        title_array = title_prop.get("title", [])
                        if title_array and len(title_array) > 0:
                            title = title_array[0].get("plain_text", "Untitled")
                elif item_type == "database":
                    title_array = result.get("title", [])
                    if title_array and len(title_array) > 0:
                        title = title_array[0].get("plain_text", "Untitled")
                
                items.append({
                    "id": item_id,
                    "name": title,
                    "type": item_type,
                    "url": result.get("url"),
                    "created_time": result.get("created_time")
                })
    
    return items


