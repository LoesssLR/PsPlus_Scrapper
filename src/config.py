import os
from dotenv import load_dotenv

# variables from .env file
load_dotenv()

# preparing email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# url to extract PS Plus information
PS_PLUS_URL = os.getenv("PS_PLUS_URL", "https://www.playstation.com/es-cr/ps-plus/#subscriptions")