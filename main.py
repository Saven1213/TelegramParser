import asyncio


from pyrogram import Client


import os
from dotenv import load_dotenv

from db.models import create_session

load_dotenv()


API_ID = int(os.getenv('API_ID'))
API_HASH = str(os.getenv("API_HASH"))
SESSION_NAME = str(os.getenv("SESSION_NAME"))


app = Client(
    name=SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    workdir="sessions"
)






async def main():
    from pyrogram import idle
    print("Юзербот запущен")
    await app.start()

    await create_session()

    await idle()


if __name__ == "__main__":
    from pyrogram import idle
    asyncio.run(main())
