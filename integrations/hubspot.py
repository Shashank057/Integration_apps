import httpx
import uuid
from urllib.parse import urlencode
from typing import Dict, List
import config

# In-memory storage for demo (use database in production)
credentials_store: Dict[str, dict] = {}

def get_authorization_url() -> str:
    """Generate HubSpot OAuth authorization URL"""
    state = str(uuid.uuid4())
    
    params = {
        "client_id": config.HUBSPOT_CLIENT_ID,
        "redirect_uri": config.HUBSPOT_REDIRECT_URI,
        "scope": "crm.objects.contacts.read crm.objects.companies.read crm.objects.deals.read",
        "state": state
    }
    
    auth_url = f"https://app.hubspot.com/oauth/authorize?{urlencode(params)}"
    return auth_url

async def exchange_code_for_token(code: str) -> dict:
    """Exchange authorization code for access token"""
    token_url = "https://api.hubapi.com/oauth/v1/token"
    
    data = {
        "grant_type": "authorization_code",
        "client_id": config.HUBSPOT_CLIENT_ID,
        "client_secret": config.HUBSPOT_CLIENT_SECRET,
        "redirect_uri": config.HUBSPOT_REDIRECT_URI,
        "code": code
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
    """Fetch contacts, companies, and deals from HubSpot"""
    access_token = credentials.get("access_token")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    items = []
    
    async with httpx.AsyncClient() as client:
        # Fetch contacts
        try:
            contacts_response = await client.get(
                "https://api.hubapi.com/crm/v3/objects/contacts",
                headers=headers,
                params={"limit": 10}
            )
            
            if contacts_response.status_code == 200:
                contacts_data = contacts_response.json()
                contacts = contacts_data.get("results", [])
                
                for contact in contacts:
                    properties = contact.get("properties", {})
                    name = f"{properties.get('firstname', '')} {properties.get('lastname', '')}".strip() or "Unnamed Contact"
                    
                    items.append({
                        "id": contact.get("id"),
                        "name": name,
                        "type": "contact",
                        "url": f"https://app.hubspot.com/contacts/{contact.get('id')}",
                        "created_time": contact.get("createdAt")
                    })
        except Exception as e:
            print(f"Error fetching contacts: {e}")
        
        # Fetch companies
        try:
            companies_response = await client.get(
                "https://api.hubapi.com/crm/v3/objects/companies",
                headers=headers,
                params={"limit": 10}
            )
            
            if companies_response.status_code == 200:
                companies_data = companies_response.json()
                companies = companies_data.get("results", [])
                
                for company in companies:
                    properties = company.get("properties", {})
                    
                    items.append({
                        "id": company.get("id"),
                        "name": properties.get("name", "Unnamed Company"),
                        "type": "company",
                        "url": f"https://app.hubspot.com/contacts/{company.get('id')}/company/{company.get('id')}",
                        "created_time": company.get("createdAt")
                    })
        except Exception as e:
            print(f"Error fetching companies: {e}")
        
        # Fetch deals
        try:
            deals_response = await client.get(
                "https://api.hubapi.com/crm/v3/objects/deals",
                headers=headers,
                params={"limit": 10}
            )
            
            if deals_response.status_code == 200:
                deals_data = deals_response.json()
                deals = deals_data.get("results", [])
                
                for deal in deals:
                    properties = deal.get("properties", {})
                    
                    items.append({
                        "id": deal.get("id"),
                        "name": properties.get("dealname", "Unnamed Deal"),
                        "type": "deal",
                        "url": f"https://app.hubspot.com/contacts/{deal.get('id')}/deal/{deal.get('id')}",
                        "created_time": deal.get("createdAt")
                    })
        except Exception as e:
            print(f"Error fetching deals: {e}")
    
    return items


