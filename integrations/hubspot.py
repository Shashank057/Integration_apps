import httpx
from fastapi import HTTPException
from typing import List
import redis
import json
from config import HUBSPOT_CLIENT_ID, HUBSPOT_CLIENT_SECRET, HUBSPOT_REDIRECT_URI, REDIS_HOST, REDIS_PORT
from models import IntegrationItem, Credentials

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)


def authorize_hubspot(state: str) -> str:
    scope = "crm.objects.contacts.read crm.objects.companies.read crm.objects.deals.read crm.schemas.contacts.read crm.schemas.companies.read crm.schemas.deals.read"
    
    auth_url = (
        f"https://app.hubspot.com/oauth/authorize"
        f"?client_id={HUBSPOT_CLIENT_ID}"
        f"&redirect_uri={HUBSPOT_REDIRECT_URI}"
        f"&scope={scope}"
        f"&state={state}"
    )
    return auth_url


async def oauth2callback_hubspot(code: str, state: str) -> dict:
    token_url = "https://api.hubapi.com/oauth/v1/token"
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": HUBSPOT_REDIRECT_URI,
        "client_id": HUBSPOT_CLIENT_ID,
        "client_secret": HUBSPOT_CLIENT_SECRET,
    }
    
    headers = {
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
            f"hubspot_credentials:{state}",
            3600,
            json.dumps(token_data)
        )
        
        return token_data


def get_hubspot_credentials(state: str) -> Credentials:
    creds_json = redis_client.get(f"hubspot_credentials:{state}")
    
    if not creds_json:
        raise HTTPException(status_code=404, detail="Credentials not found")
    
    creds_data = json.loads(creds_json)
    return Credentials(
        access_token=creds_data.get("access_token"),
        refresh_token=creds_data.get("refresh_token"),
        expires_in=creds_data.get("expires_in"),
        token_type=creds_data.get("token_type", "Bearer")
    )


async def get_items_hubspot(credentials: Credentials) -> List[IntegrationItem]:
    items = []
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            contacts_response = await client.get(
                "https://api.hubapi.com/crm/v3/objects/contacts",
                headers=headers,
                params={"limit": 100, "properties": "firstname,lastname,email,createdate,lastmodifieddate"}
            )
            
            if contacts_response.status_code == 200:
                contacts_data = contacts_response.json()
                results = contacts_data.get("results", [])
                
                for contact in results:
                    contact_id = contact.get("id")
                    properties = contact.get("properties", {})
                    firstname = properties.get("firstname", "")
                    lastname = properties.get("lastname", "")
                    email = properties.get("email", "")
                    created_time = properties.get("createdate")
                    updated_time = properties.get("lastmodifieddate")
                    
                    name = f"{firstname} {lastname}".strip() or email or f"Contact {contact_id}"
                    
                    items.append(IntegrationItem(
                        id=contact_id,
                        name=name,
                        type="contact",
                        created_time=created_time,
                        updated_time=updated_time,
                        url=f"https://app.hubspot.com/contacts/{contact_id}",
                        properties=properties
                    ))
        except Exception as e:
            print(f"Error fetching contacts: {str(e)}")
        
        try:
            companies_response = await client.get(
                "https://api.hubapi.com/crm/v3/objects/companies",
                headers=headers,
                params={"limit": 100, "properties": "name,domain,createdate,hs_lastmodifieddate"}
            )
            
            if companies_response.status_code == 200:
                companies_data = companies_response.json()
                results = companies_data.get("results", [])
                
                for company in results:
                    company_id = company.get("id")
                    properties = company.get("properties", {})
                    name = properties.get("name", f"Company {company_id}")
                    domain = properties.get("domain", "")
                    created_time = properties.get("createdate")
                    updated_time = properties.get("hs_lastmodifieddate")
                    
                    items.append(IntegrationItem(
                        id=company_id,
                        name=name,
                        type="company",
                        created_time=created_time,
                        updated_time=updated_time,
                        url=f"https://app.hubspot.com/contacts/{company_id}/company/{company_id}",
                        properties=properties
                    ))
        except Exception as e:
            print(f"Error fetching companies: {str(e)}")
        
        try:
            deals_response = await client.get(
                "https://api.hubapi.com/crm/v3/objects/deals",
                headers=headers,
                params={"limit": 100, "properties": "dealname,amount,dealstage,createdate,hs_lastmodifieddate,closedate"}
            )
            
            if deals_response.status_code == 200:
                deals_data = deals_response.json()
                results = deals_data.get("results", [])
                
                for deal in results:
                    deal_id = deal.get("id")
                    properties = deal.get("properties", {})
                    name = properties.get("dealname", f"Deal {deal_id}")
                    created_time = properties.get("createdate")
                    updated_time = properties.get("hs_lastmodifieddate")
                    
                    items.append(IntegrationItem(
                        id=deal_id,
                        name=name,
                        type="deal",
                        created_time=created_time,
                        updated_time=updated_time,
                        url=f"https://app.hubspot.com/contacts/{deal_id}/deal/{deal_id}",
                        properties=properties
                    ))
        except Exception as e:
            print(f"Error fetching deals: {str(e)}")
    
    return items