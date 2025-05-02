import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", 0)) or 12345678
API_HASH = os.getenv("API_HASH", "") or "tu_api_hash_aqui"
SESSION_NAME = 'osint_session'
REPORTS_DIR = "reportes"