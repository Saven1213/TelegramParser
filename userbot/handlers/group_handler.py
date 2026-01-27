
from pyrogram import filters
from pyrogram.types import Message

from db.crud.log import create_log
from userbot.client import app as client
import logging


from userbot.list_group_id import GROUPS, get_channel_info

logger = logging.getLogger(__name__)

# userbot/utils/album_collector.py
from collections import defaultdict
import asyncio
from datetime import datetime, timedelta


class AlbumCollector:
    """Собирает части альбомов и обрабатывает целиком"""

    def __init__(self, wait_time: int = 5):
        self.wait_time = wait_time  # секунд ожидания
        self.albums: dict = defaultdict(list)  # media_group_id -> список сообщений
        self.lock = asyncio.Lock()

    async def add_message(self, message):
        """Добавляет сообщение в альбом"""
        async with self.lock:
            media_group_id = message.media_group_id
            self.albums[media_group_id].append(message)

            # Запускаем обработку через wait_time секунд
            asyncio.create_task(self._process_album_after_delay(media_group_id))

    async def _process_album_after_delay(self, media_group_id):
        """Обрабатывает альбом после задержки"""
        await asyncio.sleep(self.wait_time)

        async with self.lock:
            if media_group_id not in self.albums:
                return

            messages = self.albums.pop(media_group_id)
            await self._process_full_album(messages)

    async def _process_full_album(self, messages):
        """Обрабатывает собранный альбом"""
        if not messages:
            return


        messages.sort(key=lambda m: m.id)


        first_msg = messages[0]
        caption = first_msg.caption or ""


        photos = []
        videos = []
        documents = []

        for msg in messages:
            if msg.photo:
                photos.append(msg.photo)
            elif msg.video:
                videos.append(msg.video)
            elif msg.document:
                documents.append(msg.document)


        print(f"\n📦 СОБРАН АЛЬБОМ ({len(messages)} частей):")
        print(f"   media_group_id: {first_msg.media_group_id}")
        print(f"   Подпись: {caption[:100]}..." if caption else "   Без подписи")
        print(f"   Фото: {len(photos)} шт")
        print(f"   Видео: {len(videos)} шт")
        print(f"   Документы: {len(documents)} шт")

        # TODO: Здесь будет сохранение в БД

group_ids = list(GROUPS.keys())
groups_filter = filters.chat(group_ids) if group_ids else None


@client.on_message(groups_filter)
async def handle_group_message(client, message: Message):
    try:
        # channel_info = get_channel_info(message.chat.id)
        # await create_log('parsing', f'Парсинг из группы {channel_info["name"]}')

        # logger.info(f"📥 ГРУППА: '{channel_info['name']}'")
        logger.info(f"   ID сообщения: {message.id}")
        logger.info(f"   Дата: {message.date}")

        if message.from_user:
            logger.info(f"   Автор: {message.from_user.id}")

        # Проверяем тип контента
        if message.media_group_id:
            # Альбом медиа
            logger.info(f"   Тип: АЛЬБОМ (media_group_id: {message.media_group_id})")

            if message.caption:
                logger.info(f"   Подпись альбома: {message.caption[:100]}...")

            if message.photo:
                logger.info(f"   📸 Фото в альбоме: {message.photo.file_id}")
            if message.video:
                logger.info(f"   🎥 Видео в альбоме: {message.video.file_id}")
            if message.document:
                logger.info(f"   📎 Документ в альбоме: {message.document.file_name}")

        elif message.photo:
            # Одно фото
            logger.info(f"   Тип: ФОТО")
            logger.info(f"   file_id: {message.photo.file_id}")

            if message.caption:
                logger.info(f"   Подпись: {message.caption[:100]}...")

        elif message.video:
            # Видео
            logger.info(f"   Тип: ВИДЕО")
            logger.info(f"   file_id: {message.video.file_id}")
            logger.info(f"   Длительность: {message.video.duration} сек")

            if message.caption:
                logger.info(f"   Подпись: {message.caption[:100]}...")

        elif message.document:
            # Документ
            logger.info(f"   Тип: ДОКУМЕНТ")
            logger.info(f"   Имя файла: {message.document.file_name}")
            logger.info(f"   MIME тип: {message.document.mime_type}")

        elif message.text:
            # Только текст
            logger.info(f"   Тип: ТЕКСТ")
            logger.info(f"   Текст: {message.text[:100]}...")

        else:
            # Другой тип
            logger.info(f"   Тип: ДРУГОЙ (не обрабатывается)")

        logger.info("-" * 50)

    except Exception as e:
        error_msg = f"Ошибка обработки сообщения {message.id}: {e}"
        await create_log('error', error_msg)
        logger.error(error_msg)


logger.info(f"✅ Групповой хэндлер настроен для {len(GROUPS)} групп")
