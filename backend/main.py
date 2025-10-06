from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv
import httpx
import json
from integrations.notion import NotionIntegration
from integrations.hubspot import HubSpotIntegration
from integrations.airtable import AirtableIntegration

# Load environment variables
load_dotenv()

app = FastAPI(title="Integration Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize integrations
notion_integration = NotionIntegration()
hubspot_integration = HubSpotIntegration()
airtable_integration = AirtableIntegration()

@app.get("/")
async def root():
    return {"message": "Integration Backend API", "status": "running"}

@app.get("/integrations/notion/auth")
async def notion_auth():
    """Initiate Notion OAuth flow"""
    try:
        auth_url = notion_integration.get_auth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/integrations/notion/authorize")
async def notion_authorize():
    """Initiate Notion OAuth flow (alias for frontend compatibility)"""
    try:
        auth_url = notion_integration.get_auth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/integrations/notion/oauth2callback")
async def notion_callback(code: str, state: str = None):
    """Handle Notion OAuth callback"""
    try:
        # Exchange code for access token
        token_data = await notion_integration.exchange_code_for_token(code)
        
        # Store the token (you might want to store this in a database)
        # For now, we'll just return success
        
        return {
            "status": "success",
            "message": "Notion integration successful",
            "access_token": token_data.get("access_token"),
            "workspace_id": token_data.get("workspace_id")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth callback failed: {str(e)}")

@app.get("/integrations/notion/status")
async def notion_status():
    """Check Notion integration status"""
    return {"status": "connected", "integration": "notion"}

@app.get("/integrations/notion/credentials/{state}")
async def notion_credentials(state: str):
    """Get Notion credentials by state"""
    # In a real implementation, you'd store and retrieve credentials by state
    # For now, we'll return a placeholder
    return {
        "access_token": "placeholder_token",
        "workspace_id": "placeholder_workspace",
        "state": state
    }

@app.post("/integrations/notion/items")
async def notion_items(credentials: dict):
    """Get Notion items using credentials"""
    try:
        # In a real implementation, you'd use the actual access token
        # to fetch items from Notion API
        return {
            "items": [
                {
                    "id": "sample-page-1",
                    "name": "Sample Notion Page",
                    "type": "page",
                    "url": "https://notion.so/sample-page-1",
                    "created_time": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "sample-database-1", 
                    "name": "Sample Database",
                    "type": "database",
                    "url": "https://notion.so/sample-database-1",
                    "created_time": "2024-01-01T00:00:00Z"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# HubSpot Integration Endpoints
@app.get("/integrations/hubspot/authorize")
async def hubspot_authorize():
    """Initiate HubSpot OAuth flow"""
    try:
        auth_url = hubspot_integration.get_auth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/integrations/hubspot/oauth2callback")
async def hubspot_callback(code: str, state: str = None):
    """Handle HubSpot OAuth callback"""
    try:
        token_data = await hubspot_integration.exchange_code_for_token(code)
        return {
            "status": "success",
            "message": "HubSpot integration successful",
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth callback failed: {str(e)}")

@app.get("/integrations/hubspot/credentials/{state}")
async def hubspot_credentials(state: str):
    """Get HubSpot credentials by state"""
    return {
        "access_token": "placeholder_hubspot_token",
        "refresh_token": "placeholder_refresh_token",
        "state": state
    }

@app.post("/integrations/hubspot/items")
async def hubspot_items(credentials: dict):
    """Get HubSpot items using credentials"""
    try:
        return {
            "items": [
                {
                    "id": "contact-1",
                    "name": "John Doe",
                    "type": "contact",
                    "email": "john@example.com",
                    "created_time": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "company-1",
                    "name": "Acme Corp",
                    "type": "company",
                    "domain": "acme.com",
                    "created_time": "2024-01-01T00:00:00Z"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Airtable Integration Endpoints
@app.get("/integrations/airtable/authorize")
async def airtable_authorize():
    """Initiate Airtable OAuth flow"""
    try:
        auth_url = airtable_integration.get_auth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/integrations/airtable/oauth2callback")
async def airtable_callback(code: str, state: str = None):
    """Handle Airtable OAuth callback"""
    try:
        token_data = await airtable_integration.exchange_code_for_token(code)
        return {
            "status": "success",
            "message": "Airtable integration successful",
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth callback failed: {str(e)}")

@app.get("/integrations/airtable/credentials/{state}")
async def airtable_credentials(state: str):
    """Get Airtable credentials by state"""
    return {
        "access_token": "placeholder_airtable_token",
        "refresh_token": "placeholder_refresh_token",
        "state": state
    }

@app.post("/integrations/airtable/items")
async def airtable_items(credentials: dict):
    """Get Airtable items using credentials"""
    try:
        return {
            "items": [
                {
                    "id": "base-1",
                    "name": "Project Management",
                    "type": "base",
                    "url": "https://airtable.com/app1234567890",
                    "created_time": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "table-1",
                    "name": "Tasks",
                    "type": "table",
                    "parent_name": "Project Management",
                    "created_time": "2024-01-01T00:00:00Z"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)