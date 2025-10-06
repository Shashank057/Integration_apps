import os
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_CLIENT_ID = os.getenv("AIRTABLE_CLIENT_ID", "")
AIRTABLE_CLIENT_SECRET = os.getenv("AIRTABLE_CLIENT_SECRET", "")
AIRTABLE_REDIRECT_URI = os.getenv("BACKEND_URL", "http://localhost:8000") + "/integrations/airtable/oauth2callback"

NOTION_CLIENT_ID = os.getenv("NOTION_CLIENT_ID", "")
NOTION_CLIENT_SECRET = os.getenv("NOTION_CLIENT_SECRET", "")
NOTION_REDIRECT_URI = os.getenv("BACKEND_URL", "http://localhost:8000") + "/integrations/notion/oauth2callback"

HUBSPOT_CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID", "")
HUBSPOT_CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET", "")
HUBSPOT_REDIRECT_URI = os.getenv("BACKEND_URL", "http://localhost:8000") + "/integrations/hubspot/oauth2callback"

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))