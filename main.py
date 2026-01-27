import asyncio
from pyrogram import filters, idle
from userbot.list_group_id import GROUPS
from db.models import create_session

from telethon import events

from pyrogram import filters
from userbot.client import app


import asyncio
from pyrogram import filters
from userbot.list_group_id import GROUPS
from db.models import create_session
from userbot.handlers import group_handler






def main():

    app.start()
    print("Userbot started")


    asyncio.get_event_loop().run_until_complete(create_session())





    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()


