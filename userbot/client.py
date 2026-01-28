from msilib.text import dirname

from pyrogram import Client

import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION_NAME = os.getenv('SESSION_NAME', 'parser_session')

app = Client(
    name=SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    workdir="sessions"
)





