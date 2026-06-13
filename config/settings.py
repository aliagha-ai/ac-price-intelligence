import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

AMAZON_URL = (
    "https://www.amazon.in/s?k=1.5+ton+split+ac"
)