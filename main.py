from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn
from integrations import airtable, notion, hubspot
import config

app = FastAPI(title="VectorShift Integrations API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Airtable Routes
@app.get("/integrations/airtable/authorize")
async def airtable_authorize():
    """Initiate Airtable OAuth flow"""
    auth_url = airtable.get_authorization_url()
    return {"auth_url": auth_url}

@app.get("/integrations/airtable/callback")
async def airtable_callback(code: str, state: str):
    """Handle Airtable OAuth callback"""
    try:
        credentials = await airtable.exchange_code_for_token(code, state)
        airtable.store_credentials(state, credentials)
        return RedirectResponse(url=f"{config.FRONTEND_URL}/airtable/success?state={state}")
    except Exception as e:
        return RedirectResponse(url=f"{config.FRONTEND_URL}/airtable/error?message={str(e)}")

@app.get("/integrations/airtable/credentials/{state}")
async def get_airtable_credentials(state: str):
    """Retrieve Airtable credentials by state"""
    credentials = airtable.get_credentials(state)
    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")
    return credentials

@app.post("/integrations/airtable/items")
async def get_airtable_items(credentials: dict):
    """Fetch items from Airtable"""
    try:
        items = await airtable.get_items(credentials)
        return {"items": items, "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Notion Routes
@app.get("/integrations/notion/authorize")
async def notion_authorize():
    """Initiate Notion OAuth flow"""
    auth_url = notion.get_authorization_url()
    return {"auth_url": auth_url}

@app.get("/integrations/notion/callback")
async def notion_callback(code: str, state: str):
    """Handle Notion OAuth callback"""
    try:
        credentials = await notion.exchange_code_for_token(code)
        notion.store_credentials(state, credentials)
        return RedirectResponse(url=f"{config.FRONTEND_URL}/notion/success?state={state}")
    except Exception as e:
        return RedirectResponse(url=f"{config.FRONTEND_URL}/notion/error?message={str(e)}")

@app.get("/integrations/notion/credentials/{state}")
async def get_notion_credentials(state: str):
    """Retrieve Notion credentials by state"""
    credentials = notion.get_credentials(state)
    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")
    return credentials

@app.post("/integrations/notion/items")
async def get_notion_items(credentials: dict):
    """Fetch items from Notion"""
    try:
        items = await notion.get_items(credentials)
        return {"items": items, "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# HubSpot Routes
@app.get("/integrations/hubspot/authorize")
async def hubspot_authorize():
    """Initiate HubSpot OAuth flow"""
    auth_url = hubspot.get_authorization_url()
    return {"auth_url": auth_url}

@app.get("/integrations/hubspot/callback")
async def hubspot_callback(code: str, state: str):
    """Handle HubSpot OAuth callback"""
    try:
        credentials = await hubspot.exchange_code_for_token(code)
        hubspot.store_credentials(state, credentials)
        return RedirectResponse(url=f"{config.FRONTEND_URL}/hubspot/success?state={state}")
    except Exception as e:
        return RedirectResponse(url=f"{config.FRONTEND_URL}/hubspot/error?message={str(e)}")

@app.get("/integrations/hubspot/credentials/{state}")
async def get_hubspot_credentials(state: str):
    """Retrieve HubSpot credentials by state"""
    credentials = hubspot.get_credentials(state)
    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")
    return credentials

@app.post("/integrations/hubspot/items")
async def get_hubspot_items(credentials: dict):
    """Fetch items from HubSpot"""
    try:
        items = await hubspot.get_items(credentials)
        return {"items": items, "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "VectorShift Integrations API",
        "version": "1.0.0",
        "integrations": ["airtable", "notion", "hubspot"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



