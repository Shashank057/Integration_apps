import os
from dotenv import load_dotenv

# Load .env file from the same directory as this config file
load_dotenv()

# Airtable Configuration
AIRTABLE_CLIENT_ID = os.getenv("AIRTABLE_CLIENT_ID", "your_airtable_client_id_here")
AIRTABLE_CLIENT_SECRET = os.getenv("AIRTABLE_CLIENT_SECRET", "your_airtable_client_secret_here")
AIRTABLE_REDIRECT_URI = os.getenv("AIRTABLE_REDIRECT_URI", "http://localhost:8000/integrations/airtable/callback")

# Debug: Print to verify loading
print(f"🔍 DEBUG: AIRTABLE_CLIENT_ID loaded: {AIRTABLE_CLIENT_ID[:20]}..." if AIRTABLE_CLIENT_ID else "❌ AIRTABLE_CLIENT_ID is empty!")

# Notion Configuration
NOTION_CLIENT_ID = os.getenv("NOTION_CLIENT_ID", "")
NOTION_CLIENT_SECRET = os.getenv("NOTION_CLIENT_SECRET", "")
NOTION_REDIRECT_URI = os.getenv("NOTION_REDIRECT_URI", "http://localhost:8000/integrations/notion/callback")

# HubSpot Configuration
HUBSPOT_CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID", "")
HUBSPOT_CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET", "")
HUBSPOT_REDIRECT_URI = os.getenv("HUBSPOT_REDIRECT_URI", "http://localhost:8000/integrations/hubspot/callback")

# Frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")



