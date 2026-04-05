import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

ENABLE_SCREENSHOTS = os.getenv("ENABLE_SCREENSHOTS", "true").lower() == "true"
ENABLE_CLIPBOARD = os.getenv("ENABLE_CLIPBOARD", "true").lower() == "true"
ENABLE_NOTIFICATIONS = os.getenv("ENABLE_NOTIFICATIONS", "true").lower() == "true"
ENABLE_INACTIVITY_POPUP = (
    os.getenv("ENABLE_INACTIVITY_POPUP", "true").lower() == "true"
)
AI_ASSISTANT_ENABLED = os.getenv("AI_ASSISTANT_ENABLED", "true").lower() == "true"

INACTIVITY_THRESHOLD_SECONDS = int(
    os.getenv("INACTIVITY_THRESHOLD_SECONDS", "600")
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SCREENSHOT_DIR = DATA_DIR / "screenshots"

DATA_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)