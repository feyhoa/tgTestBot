import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv('BOT_TOKEN')
ADMIN: str = os.getenv('ADMIN')
