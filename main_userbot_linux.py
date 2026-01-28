import asyncio
from logging import Logger

from pyrogram import filters, idle
import logging

from userbot.handlers.group_handler import chat_id
from userbot.list_group_id import GROUPS
from db.models import create_session
from pyrogram import filters



import asyncio
from pyrogram import filters
from userbot.list_group_id import GROUPS
from db.models import create_session
from userbot.handlers import group_handler
from userbot.list_group_id import GROUPS, SUPERGROUPS
from userbot.client import app

group_ids = list(GROUPS.keys())


async def main():

    await app.start()
    print("Userbot started")


    await create_session()
    print("DB initialized")


    await idle()


    await app.stop()
    print("Userbot stopped")

if __name__ == "__main__":
    asyncio.run(main())