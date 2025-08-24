import os
from dotenv import load_dotenv

load_dotenv(override=True)

TURN_LIMIT = int(os.getenv("TURN_LIMIT", 4))
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_USER = os.getenv("PUSHOVER_USER")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
BASE_URL = os.getenv("BASE_URL")
ME = os.getenv("ME", "Someone Mysterious")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_BASE_DIR = os.path.join(ROOT_DIR, "knowledge_base")
PDF_PATH = os.path.join(KNOWLEDGE_BASE_DIR, "me.pdf")
