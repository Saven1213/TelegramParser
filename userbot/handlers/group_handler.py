#
from pyrogram import filters
from pyrogram.types import Message

from db.crud.log import create_log

import logging
from collections import defaultdict
import asyncio
from datetime import datetime, timedelta

from db.crud.post import create_post
from userbot.client import app


from userbot.list_group_id import GROUPS, get_channel_info

logger = logging.getLogger(__name__)








# class AlbumCollector:
#     """Собирает части альбомов и обрабатывает целиком"""
#
#     def __init__(self, wait_time: int = 5):
#         self.wait_time = wait_time  # секунд ожидания
#         self.albums: dict = defaultdict(list)  # media_group_id -> список сообщений
#         self.lock = asyncio.Lock()
#
#     async def add_message(self, message):
#         """Добавляет сообщение в альбом"""
#         async with self.lock:
#             media_group_id = message.media_group_id
#             self.albums[media_group_id].append(message)
#
#             # Запускаем обработку через wait_time секунд
#             asyncio.create_task(self._process_album_after_delay(media_group_id))
#
#     async def _process_album_after_delay(self, media_group_id):
#         """Обрабатывает альбом после задержки"""
#         await asyncio.sleep(self.wait_time)
#
#         async with self.lock:
#             if media_group_id not in self.albums:
#                 return
#
#             messages = self.albums.pop(media_group_id)
#             await self._process_full_album(messages)
#
#     async def _process_full_album(self, messages):
#         """Обрабатывает собранный альбом"""
#         if not messages:
#             return
#
#
#         messages.sort(key=lambda m: m.id)
#
#
#         first_msg = messages[0]
#         caption = first_msg.caption or ""
#
#
#         photos = []
#         videos = []
#         documents = []
#
#         for msg in messages:
#             if msg.photo:
#                 photos.append(msg.photo)
#             elif msg.video:
#                 videos.append(msg.video)
#             elif msg.document:
#                 documents.append(msg.document)
#
#
#         print(f"\n📦 СОБРАН АЛЬБОМ ({len(messages)} частей):")
#         print(f"   media_group_id: {first_msg.media_group_id}")
#         print(f"   Подпись: {caption[:100]}..." if caption else "   Без подписи")
#         print(f"   Фото: {len(photos)} шт")
#         print(f"   Видео: {len(videos)} шт")
#         print(f"   Документы: {len(documents)} шт")
#
#         # TODO: Здесь будет сохранение в БД

group_ids = list(GROUPS.keys())
groups_filter = filters.chat(group_ids)




# @app.on_message(groups_filter)
# async def debug_all(client, message):
#     print("DEBUG:", message.chat.id, message.chat.type, message.text)

albums_cache = {}  # media_group_id -> {"messages": [], "first_msg_date": datetime}

async def save_album_after_delay(media_group_id, msg_link, delay=1):
    await asyncio.sleep(delay)

    cache = albums_cache.get(media_group_id)
    if not cache:
        return

    # собираем media
    media_list = []
    for msg in cache["messages"]:
        if msg.photo:
            media_list.append(msg.photo.file_id)
        if msg.video:
            media_list.append(msg.video.file_id)
        if msg.document:
            media_list.append(msg.document.file_id)

    media_str = ",".join(media_list)
    text = cache["messages"][0].caption or cache["messages"][0].text or ""

    post_data = {
        "text": text,
        "media": media_str,
        "source_url": msg_link,
        "published_at": datetime.now(),
        "is_published": True
    }

    print(post_data)
    await create_post(**post_data)

    # очищаем кеш
    del albums_cache[media_group_id]


@app.on_message(groups_filter)
async def handle_group_message(client, message: Message):
    try:
        msg_link = f"https://t.me/{message.chat.username}/{message.id}"


        print(f"   ID сообщения: {message.id}")
        print(f"   Дата: {message.date}")
        print(f"   Ссылка на сообщение {msg_link}")

        if message.from_user:
            logger.info(f"   Автор: {message.from_user.id}")

        # -------------------------------
        # 1) Сбор данных
        # -------------------------------
        text = None
        media_list = []

        if message.caption:
            text = message.caption

        if message.text and not text:
            text = message.text

        # -------------------------------
        # 2) Альбом
        # -------------------------------
        if message.media_group_id:
            if message.media_group_id not in albums_cache:
                albums_cache[message.media_group_id] = {
                    "messages": [],
                    "saving": False
                }

            albums_cache[message.media_group_id]["messages"].append(message)


            if not albums_cache[message.media_group_id]["saving"]:
                albums_cache[message.media_group_id]["saving"] = True
                asyncio.create_task(
                    save_album_after_delay(message.media_group_id, msg_link, delay=3)
                )


        elif message.photo:
            print(f"   Тип: ФОТО")
            print(f"   file_id: {message.photo.file_id}")
            if message.caption:
                print(f"   Подпись: {message.caption[:100]}...")

            media_list = [message.photo.file_id]

        elif message.video:
            print(f"   Тип: ВИДЕО")
            print(f"   file_id: {message.video.file_id}")
            print(f"   Длительность: {message.video.duration} сек")
            if message.caption:
                print(f"   Подпись: {message.caption[:100]}...")

            media_list = [message.video.file_id]

        elif message.document:
            print(f"   Тип: ДОКУМЕНТ")
            print(f"   Имя файла: {message.document.file_name}")
            print(f"   MIME тип: {message.document.mime_type}")

            media_list = [message.document.file_id]

        elif message.text:
            print(f"   Тип: ТЕКСТ")
            print(f"   Текст: {message.text[:100]}...")
            media_list = []

        else:
            print(f"   Тип: ДРУГОЙ (не обрабатывается)")

        # -------------------------------
        # 4) Вставка в БД (для всех типов кроме альбома)
        # -------------------------------
        if not message.media_group_id:
            media_str = ",".join(media_list) if media_list else None
            text = text or ""
            post_data = {
                "text": text,
                "media": media_str,
                "source_url": msg_link,
                "published_at": datetime.now(),
                "is_published": True
            }


            await create_post(**post_data)

        print("-" * 50)

    except Exception as e:
        error_msg = f"Ошибка обработки сообщения {message.id}: {e}"
        await create_log('error', error_msg)
        print(error_msg)
        print("ошибка, но тоже сработало")


logger.info(f"✅ Групповой хэндлер настроен для {len(GROUPS)} групп")
