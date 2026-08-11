import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

DATABASE_URL = os.getenv("DATABASE_URL", "")

SMM_API_URL = os.getenv("SMM_API_URL", "")
SMM_API_KEY = os.getenv("SMM_API_KEY", "")
