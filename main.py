from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
import uuid
from typing import Optional

from integrations.airtable import (
    authorize_airtable,
    oauth2callback_airtable,
    get_airtable_credentials,
    get_items_airtable
)
from integrations.notion import (
    authorize_notion,
    oauth2callback_notion,
    get_notion_credentials,
    get_items_notion
)
from integrations.hubspot import (
    authorize_hubspot,
    oauth2callback_hubspot,
    get_hubspot_credentials,
    get_items_hubspot
)
from models import Credentials

app = FastAPI(title="VectorShift Integrations API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "VectorShift Integrations API", "status": "running"}


@app.get("/integrations/airtable/authorize")
async def authorize_airtable_route():
    state = str(uuid.uuid4())
    auth_url = authorize_airtable(state)
    return {"auth_url": auth_url, "state": state}


@app.get("/integrations/airtable/oauth2callback")
async def oauth2callback_airtable_route(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None)
):
    try:
        if error:
            error_msg = error_description or error
            return RedirectResponse(
                url=f"http://localhost:3000/integrations/airtable/error?message={error_msg}"
            )
        
        if not code or not state:
            return RedirectResponse(
                url=f"http://localhost:3000/integrations/airtable/error?message=Missing code or state parameter"
            )
        
        token_data = await oauth2callback_airtable(code, state)
        return RedirectResponse(
            url=f"http://localhost:3000/integrations/airtable/success?state={state}"
        )
    except Exception as e:
        return RedirectResponse(
            url=f"http://localhost:3000/integrations/airtable/error?message={str(e)}"
        )


@app.get("/integrations/airtable/credentials/{state}")
async def get_airtable_credentials_route(state: str):
    credentials = get_airtable_credentials(state)
    return credentials


@app.post("/integrations/airtable/items")
async def get_airtable_items_route(credentials: Credentials):
    items = await get_items_airtable(credentials)
    return {"items": items, "count": len(items)}


@app.get("/integrations/notion/authorize")
async def authorize_notion_route():
    state = str(uuid.uuid4())
    auth_url = authorize_notion(state)
    return {"auth_url": auth_url, "state": state}


@app.get("/integrations/notion/oauth2callback")
async def oauth2callback_notion_route(
    code: str = Query(...),
    state: str = Query(...)
):
    try:
        token_data = await oauth2callback_notion(code, state)
        return RedirectResponse(
            url=f"http://localhost:3000/integrations/notion/success?state={state}"
        )
    except Exception as e:
        return RedirectResponse(
            url=f"http://localhost:3000/integrations/notion/error?message={str(e)}"
        )


@app.get("/integrations/notion/credentials/{state}")
async def get_notion_credentials_route(state: str):
    credentials = get_notion_credentials(state)
    return credentials


@app.post("/integrations/notion/items")
async def get_notion_items_route(credentials: Credentials):
    items = await get_items_notion(credentials)
    return {"items": items, "count": len(items)}


@app.get("/integrations/hubspot/authorize")
async def authorize_hubspot_route():
    state = str(uuid.uuid4())
    auth_url = authorize_hubspot(state)
    return {"auth_url": auth_url, "state": state}


@app.get("/integrations/hubspot/oauth2callback")
async def oauth2callback_hubspot_route(
    code: str = Query(...),
    state: str = Query(...)
):
    try:
        token_data = await oauth2callback_hubspot(code, state)
        return RedirectResponse(
            url=f"http://localhost:3000/integrations/hubspot/success?state={state}"
        )
    except Exception as e:
        return RedirectResponse(
            url=f"http://localhost:3000/integrations/hubspot/error?message={str(e)}"
        )


@app.get("/integrations/hubspot/credentials/{state}")
async def get_hubspot_credentials_route(state: str):
    credentials = get_hubspot_credentials(state)
    return credentials


@app.post("/integrations/hubspot/items")
async def get_hubspot_items_route(credentials: Credentials):
    items = await get_items_hubspot(credentials)
    
    print("\n" + "="*80)
    print(f"HUBSPOT ITEMS - Total Count: {len(items)}")
    print("="*80)
    for idx, item in enumerate(items, 1):
        print(f"\n{idx}. {item.type.upper()}: {item.name}")
        print(f"   ID: {item.id}")
        if item.url:
            print(f"   URL: {item.url}")
        if item.created_time:
            print(f"   Created: {item.created_time}")
        if item.updated_time:
            print(f"   Updated: {item.updated_time}")
    print("\n" + "="*80 + "\n")
    
    return {"items": items, "count": len(items)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)