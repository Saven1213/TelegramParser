from db.crud.log import create_log
from userbot.client import app


async def error(message, error_chat):
    await create_log('error', message)
    await app.send_message(chat_id=error_chat, message=message)