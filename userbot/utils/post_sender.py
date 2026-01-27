from pyrogram.filters import caption

from db.crud.categories import get_categories
from db.crud.log import create_log
from userbot.client import app
from pyrogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from dotenv import load_dotenv
import os

load_dotenv()

error_chat = int(os.getenv("ERROR_CHAT"))

def detect_category(text: str, categories: list) -> str:
    text = text.lower()

    for cat in categories:
        for kw in cat["keywords"]:
            if kw in text:
                return cat["name"]

    return "Другое"


async def send_post_to_channel(client: app, chat_id: int, post_data: dict):
    text = post_data.get("text", "")
    media_str = post_data.get("media")
    source_url = post_data.get("source_url", "")

    categories = await get_categories()

    category = detect_category(text, categories)
    if category != "Другое":
        text = f"<b>[{category}]</b>\n\n" + text

    if source_url:
        text += f'\n\n<a href="{source_url}">Источник</a>'

    try:
        if not media_str:
            await client.send_message(chat_id=chat_id, text=text)
            return

        media_list = media_str.split(",")

        if len(media_list) == 1:
            file_id = media_list[0]

            try:
                await client.send_photo(chat_id=chat_id, photo=file_id, caption=text)
                return
            except Exception:
                pass

            try:
                await client.send_video(chat_id=chat_id, video=file_id, caption=text)
                return
            except Exception:
                pass

            try:
                await client.send_document(chat_id=chat_id, document=file_id, caption=text)
                return
            except Exception:
                pass

        else:
            media_group = []
            for idx, file_id in enumerate(media_list):
                if idx == 0 and text:
                    media_group.append(InputMediaPhoto(file_id, caption=text))
                else:
                    media_group.append(InputMediaPhoto(file_id))

            await client.send_media_group(chat_id=chat_id, media=media_group)

    except Exception as e:
        print("SEND ERROR:", e)
        message = 'Ошибка постинга'
        await create_log('error', message)
        await app.send_message(chat_id=error_chat, message=message)
