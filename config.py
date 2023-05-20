import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv('BOT_TOKEN')

id_alphabet = frozenset('1234567890')
ADMINS: list[str] = list(filter(lambda x: x != '' and set(x).issubset(id_alphabet), os.getenv('ADMINS').split(',')))
