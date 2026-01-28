import asyncio
from logging import Logger

from pyrogram import filters, idle
import logging

from userbot.handlers.group_handler import chat_id
from userbot.list_group_id import GROUPS
from db.models import create_session
from pyrogram import filters
from userbot.client import app


import asyncio
from pyrogram import filters
from userbot.list_group_id import GROUPS
from db.models import create_session
from userbot.handlers import group_handler, supergroup_handler
from userbot.list_group_id import GROUPS, SUPERGROUPS


group_ids = list(GROUPS.keys())


def main():

    app.start()
    print("Userbot started")

    asyncio.get_event_loop().run_until_complete(create_session())

    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()

# async def diagnose():
#     await app.start()
#
#     print("🔍 ДИАГНОСТИКА КАНАЛА -1002647897800")
#     print("=" * 50)
#
#     # 1. Проверим через get_chat
#     try:
#         chat = await app.get_chat(-1002647897800)
#         print(f"1. get_chat: ✅ {chat.title}")
#     except Exception as e:
#         print(f"1. get_chat: ❌ {e}")
#
#     # 2. Проверим через get_chat_members
#     try:
#         members = await app.get_chat_members(-1002647897800, limit=1)
#         print(f"2. get_chat_members: ✅ {len(members)} участников")
#     except Exception as e:
#         print(f"2. get_chat_members: ❌ {e}")
#
#     # 3. Проверим в диалогах
#     print("3. Поиск в диалогах:")
#     found = False
#     async for dialog in app.get_dialogs():
#         if dialog.chat.id == -1002647897800:
#             print(f"   ✅ Найден: {dialog.chat.title}")
#             found = True
#             break
#
#     if not found:
#         print("   ❌ Не найден в диалогах")
#
#     # 4. Проверим через join_chat (если публичный)
#     try:
#         chat = await app.join_chat(-1002647897800)
#         print(f"4. join_chat: ✅ Успешно")
#     except Exception as e:
#         print(f"4. join_chat: ❌ {e}")
#
#     # 5. Попробуем получить историю
#     try:
#         async for msg in app.get_chat_history(-1002647897800, limit=1):
#             print(f"5. get_chat_history: ✅ Сообщение {msg.id}")
#             break
#     except Exception as e:
#         print(f"5. get_chat_history: ❌ {e}")
#
#     print("=" * 50)
#
#     # Покажи ВСЕ каналы юзербота
#     print("\n📋 ВСЕ каналы UserBot:")
#     async for dialog in app.get_dialogs(limit=20):
#         chat = dialog.chat
#         if chat.type in ["channel", "supergroup"]:
#             print(f"  {chat.id}: {chat.title}")
#
#
# asyncio.run(diagnose())