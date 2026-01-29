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


def main():

    app.start()
    print("Userbot started")
    # history = []
    # for msg in app.get_chat_history(-1002370374751, limit=10):
    #     history.append(msg.caption)
    #
    # print(history)
    asyncio.get_event_loop().run_until_complete(create_session())

    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()

