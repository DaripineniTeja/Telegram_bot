import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
JSON_FILE_PATH = os.getenv('JSON_FILE_PATH', 'tools.json')

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')