import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UPLOAD_DIR = "uploads"

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD")