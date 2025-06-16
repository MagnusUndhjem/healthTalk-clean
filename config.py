# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Hvis du bruker .env-fil lokalt
load_dotenv()

# --- API-nøkler --------------------------------------------------
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")     # (kommer senere)
IMAGE_API_KEY     = os.getenv("IMAGE_API_KEY")         # (kommer senere)

# --- Google Drive service-konto ----------------------------------
# Hvis du bruker en service account JSON i secrets / på disk
SERVICE_JSON = os.getenv("GOOGLE_SERVICE_ACC_JSON")    # for Streamlit Cloud
SERVICE_JSON_PATH = (
    Path(__file__).parent / "service_account.json"
    if not SERVICE_JSON
    else None
)
