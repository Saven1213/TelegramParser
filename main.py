import asyncio


from userbot.client import app

from db.models import create_session
from userbot.list_group_id import GROUPS


async def main():
    from pyrogram import idle
    print("Юзербот запущен")
    await app.start()

    await create_session()

    for group_id in GROUPS.keys():
        try:
            chat = await app.get_chat(group_id)
            print(f"   ✅ {chat.title} (ID: {group_id})")
        except Exception as e:
            print(f"   ❌ Ошибка группы {group_id}: {e}")

    await idle()


if __name__ == "__main__":
    from pyrogram import idle
    asyncio.run(main())
