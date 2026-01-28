import asyncio
import logging

from aiogram.client.default import DefaultBotProperties
from pyrogram.enums import ParseMode

from bot.routers import router

from aiogram import Bot, Dispatcher

import os
from dotenv import load_dotenv

from db.models import create_session

load_dotenv()

TOKEN = str(os.getenv("BOT_TOKEN"))






bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode='html')
)
dp = Dispatcher()





async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    dp.include_router(router)


    await create_session()


    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

        await asyncio.sleep(0.1)








if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
