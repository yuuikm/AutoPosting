import os
from dotenv import load_dotenv

load_dotenv()

EXCLUSIVE_TELEGRAM_BOT_TOKEN = os.getenv("EXCLUSIVE_TELEGRAM_BOT_TOKEN")
EXCLUSIVE_TELEGRAM_CHANNEL_ID = os.getenv("EXCLUSIVE_TELEGRAM_CHANNEL_ID")
USER_AGENT = "Mozilla/5.0"
