#
from pyrogram import filters
from pyrogram.types import Message

from db.crud.categories import get_categories
from db.crud.groups import get_group_ids, get_group
from db.crud.lavanda_groups import get_target_group
from db.crud.log import create_log

import logging
from collections import defaultdict
import asyncio
from datetime import datetime, timedelta

from db.crud.post import create_post
from userbot.client import app
from userbot.config import STOP_WORDS

from userbot.list_group_id import GROUPS
from userbot.utils.error_proccesing import error
from userbot.utils.post_sender import send_post_to_channel, send_post_channel, detect_category
import os
from dotenv import load_dotenv

load_dotenv()

error_chat = int(os.getenv("ERROR_CHAT"))

logger = logging.getLogger(__name__)


from dotenv import load_dotenv
import os

load_dotenv()

chat_id = int(os.getenv("MAIN_CHAT"))

group_ids = list(GROUPS.keys())
groups_filter = filters.chat(group_ids)


albums_cache = {}


def extract_text(message: Message) -> str:
    caption = message.caption.html if message.caption and message.caption.html else message.caption
    text = message.text.html if message.text and message.text.html else message.text

    print(  #ЛОГ
        f"🧾 extract_text | msg_id={message.id} | "
        f"caption={'YES' if caption else 'NO'} | "
        f"text={'YES' if text else 'NO'}"
    )

    return caption or text or ""




async def save_album_after_delay(media_group_id, msg_link, delay=1): #Устаревшая функция
    await asyncio.sleep(delay)

    cache = albums_cache.get(media_group_id)
    if not cache:
        return

    media_files = []
    text = ""

    for i, msg in enumerate(cache["messages"]):

        if i == 0:
            text = msg.caption or msg.text or ""
            text += f'\n\n<a href="{msg_link}">Источник</a>'

        file = await msg.download(in_memory=True)

        media_files.append({
            "type": (
                "photo" if msg.photo else
                "video" if msg.video else
                "document"
            ),
            "file": file
        })

    post_data = {
        "text": text,
        "media": media_files
    }

    await send_post_channel(app, chat_id, post_data)

    del albums_cache[media_group_id]

from pyrogram.types import (
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaDocument
)

async def save_album_delay(media_group_id, msg_link, delay=3, group_id = 0):
    await asyncio.sleep(delay)

    cache = albums_cache.get(media_group_id)
    if not cache:
        return

    print("\n" + "=" * 40)
    print(f"📚 SAVE ALBUM {media_group_id}")
    print(f"📦 messages count = {len(cache['messages'])}")

    media = []
    text = ""


    for msg in cache["messages"]:
        candidate_text = extract_text(msg)
        print(
            f"🧾 extract_text | msg_id={msg.id} | "
            f"caption={'YES' if msg.caption else 'NO'} | "
            f"text={'YES' if msg.text else 'NO'}"
        )
        if candidate_text:
            text = candidate_text
            print(f"📝 album TEXT FOUND len={len(text)}")
            break


    if text and any(word in text.lower() for word in STOP_WORDS):
        print("⛔ album filtered by STOP_WORDS")
        del albums_cache[media_group_id]
        return


    print(f"🧠 text before category:\n{text[:300]}")

    # categories = await get_categories()
    # print(f"📚 categories loaded = {len(categories)}")
    #
    # category = detect_category(text, categories)
    # print(f"🏷 detect_category RESULT = {category}")
    #
    # if category != "Другое":
    #     text = f"<b>[{category}]</b>\n\n" + text
    #     print("✅ category prepended")


    if text:
        text += f'\n\n{msg_link}'

    print(f"🧾 FINAL caption len={len(text)}")


    for idx, msg in enumerate(cache["messages"]):
        caption = text if idx == 0 else None

        if msg.photo:
            file = await msg.download(in_memory=True)
            media.append(InputMediaPhoto(file, caption=caption))
            print(f"📸 add PHOTO idx={idx} caption={'YES' if caption else 'NO'}")

        elif msg.video:
            file = await msg.download(in_memory=True)
            media.append(InputMediaVideo(file, caption=caption))
            print(f"🎥 add VIDEO idx={idx} caption={'YES' if caption else 'NO'}")

        elif msg.document:
            file = await msg.download(in_memory=True)
            media.append(InputMediaDocument(file, caption=caption))
            print(f"📄 add DOC idx={idx} caption={'YES' if caption else 'NO'}")


    if media:
        await app.send_media_group(chat_id=group_id, media=media)
        print("🚀 MEDIA GROUP SENT")

    del albums_cache[media_group_id]
    print(f"✅ album {media_group_id} DONE")
    print("=" * 40)









# @app.on_message(groups_filter)
# async def handle_group_message(client, message: Message):
#     try:
#
#         is_forum = message.chat.is_forum
#         topic_id = message.message_thread_id
#         print(is_forum)
#
#
#         if message.chat.username:
#
#             if is_forum and topic_id:
#                 msg_link = (
#                     f"https://t.me/{message.chat.username}/"
#                     f"{topic_id}/{message.id}"
#                 )
#             else:
#                 msg_link = f"https://t.me/{message.chat.username}/{message.id}"
#
#         else:
#
#             chat_id_abs = str(abs(message.chat.id))
#
#             if is_forum and topic_id:
#                 msg_link = (
#                     f"https://t.me/c/{chat_id_abs}/"
#                     f"{topic_id}/{message.id}"
#                 )
#             else:
#                 msg_link = f"https://t.me/c/{chat_id_abs}/{message.id}"
#
#         # ----------------------------
#         print(f"   ID сообщения: {message.id}")
#         print(f"   Дата: {message.date}")
#         print(f"   Форум: {is_forum}")
#         print(f"   Topic ID: {topic_id}")
#         print(f"   Ссылка: {msg_link}")
#
#         if message.from_user:
#             logger.info(f"   Автор: {message.from_user.id}")
#
#         text = None
#         media_list = []
#
#         if message.caption:
#             text = message.caption
#
#         if message.text and not text:
#             text = message.text
#
#
#         if message.media_group_id:
#             if message.media_group_id not in albums_cache:
#                 albums_cache[message.media_group_id] = {
#                     "messages": [],
#                     "saving": False
#                 }
#
#             albums_cache[message.media_group_id]["messages"].append(message)
#
#             if not albums_cache[message.media_group_id]["saving"]:
#                 albums_cache[message.media_group_id]["saving"] = True
#                 asyncio.create_task(
#                     save_album_after_delay(
#                         message.media_group_id,
#                         msg_link,
#                         delay=3
#                     )
#                 )
#
#
#         elif message.photo:
#             media_list = [message.photo.file_id]
#
#         elif message.video:
#             media_list = [message.video.file_id]
#
#         elif message.document:
#             media_list = [message.document.file_id]
#
#         elif message.text:
#             media_list = []
#
#         else:
#             print("   Тип не поддерживается")
#
#
#         if not message.media_group_id:
#             media_str = ",".join(media_list) if media_list else None
#             text = text or ""
#
#             post_data = {
#                 "text": text,
#                 "media": media_str,
#                 "source_url": msg_link,
#                 "published_at": datetime.now(),
#                 "is_published": True
#             }
#
#             await create_post(**post_data)
#             await send_post_to_channel(app, chat_id, post_data)
#
#         print("-" * 50)
#
#     except Exception as e:
#         error_msg = f"Ошибка обработки сообщения {message.id}: {e}"
#         await create_log("error", error_msg)
#         print(error_msg)

@app.on_message()
async def parse_handler(client, message: Message):
    groups_ids = await get_group_ids()
    print(groups_ids)
    print(message.chat.id)
    if message.chat.id not in groups_ids:
        return


    try:
        print("\n================ NEW MESSAGE ================") # ЛОГ
        print(f"📩 msg_id={message.id}")
        print(f"📦 media_group_id={message.media_group_id}")
        print(f"🖼 photo={bool(message.photo)} video={bool(message.video)} doc={bool(message.document)}")
        print(f"📝 caption={bool(message.caption)} text={bool(message.text)}")

        is_forum = message.chat.is_forum
        topic_id = message.message_thread_id

        # -------- ссылка --------
        if message.chat.username:
            msg_link = (
                f"https://t.me/{message.chat.username}/{topic_id}/{message.id}"
                if is_forum and topic_id
                else f"https://t.me/{message.chat.username}/{message.id}"
            )
        else:
            chat_id_abs = abs(message.chat.id)
            msg_link = (
                f"https://t.me/c/{chat_id_abs}/{topic_id}/{message.id}"
                if is_forum and topic_id
                else f"https://t.me/c/{chat_id_abs}/{message.id}"
            )

        print(f"🔗 link={msg_link}") # ЛОГ




        # -------- MEDIA GROUP --------

        group = await get_group(message.chat.id)

        target_group = await get_target_group(group.city)

        if target_group:
            if message.media_group_id:
                print("📚 MESSAGE IS PART OF MEDIA GROUP") # ЛОГ

                if message.media_group_id not in albums_cache:
                    print("🆕 new album created") # ЛОГ
                    albums_cache[message.media_group_id] = {
                        "messages": [],
                        "saving": False
                    }

                albums_cache[message.media_group_id]["messages"].append(message)
                print(  # ЛОГ
                    f"➕ added to album | total={len(albums_cache[message.media_group_id]['messages'])}"
                )

                if not albums_cache[message.media_group_id]["saving"]:
                    print("⏳ scheduling album save")
                    albums_cache[message.media_group_id]["saving"] = True
                    asyncio.create_task(
                        save_album_delay(
                            message.media_group_id,
                            msg_link,
                            delay=3,
                            group_id=target_group.group_id
                        )
                    )
                return

            # -------- ОДИНОЧНОЕ --------
            print("📄 SINGLE MESSAGE") # ЛОГ

            text = extract_text(message)
            print(f"📝 extracted_text_len={len(text)}") # ЛОГ

            # categories = await get_categories()
            # print(f"📚 categories loaded = {len(categories)}")
            #
            # category = detect_category(text, categories)
            # print(f"🏷 detect_category RESULT = {category}")
            #
            # if category != "Другое":
            #     text = f"<b>[{category}]</b>\n\n" + text
            #     print("✅ category prepended (single)")

            if text and any(word in text.lower() for word in STOP_WORDS):
                print("⛔ STOP WORD MATCH (single message)")     # ЛОГ
                return

            text += f'\n\n{msg_link}'





            if message.photo:
                print("🚀 send PHOTO")   # ЛОГ
                file = await message.download(in_memory=True)

                await app.send_photo(chat_id=target_group.group_id, photo=file, caption=text)
                return

            if message.video:
                print("🚀 send VIDEO")   # ЛОГ
                file = await message.download(in_memory=True)
                await app.send_video(chat_id=target_group.group_id, video=file, caption=text)
                return

            if message.document:
                print("🚀 send DOCUMENT")    # ЛОГ
                file = await message.download(in_memory=True)
                await app.send_document(chat_id=target_group.group_id, document=file, caption=text)
                return

            if text:
                print("🚀 send TEXT")    # ЛОГ
                await app.send_message(chat_id=target_group.group_id, text=text)
                return

            print("⚠️ FALLBACK triggered")  # ЛОГ
            await error(
                f"❌ неподдерживаемый тип сообщения\n\n<a href='{msg_link}'>Сообщение</a>",
                error_chat
            )

    except Exception as e:
        print("🔥 EXCEPTION:", e)
        await error(str(e), error_chat)



# @app.on_message([-1002370374751])
# async def test(client, message: Message):
#     print("=" * 50)
#     print(f"Message ID: {message.id}")
#     print("Raw message object:")
#     print(message)
#     print("Attributes available in message:")
#     print(dir(message))
#     print("=" * 50)
#     print(message.text)







# @app.on_message(groups_filter)
# async def handle_group_message(client, message: Message):
#     try:
#         if message.chat.username:
#             msg_link = f"https://t.me/{message.chat.username}/{message.id}"
#         else:
#             msg_link = f"https://t.me/c/{str(abs(message.chat.id))}/{message.id}"
#
#         print(f"   ID сообщения: {message.id}")
#         print(f"   Дата: {message.date}")
#         print(f"   Ссылка на сообщение {msg_link}")
#
#         if message.from_user:
#             logger.info(f"   Автор: {message.from_user.id}")
#
#         text = None
#         media_list = []
#
#         if message.caption:
#             text = message.caption
#
#         if message.text and not text:
#             text = message.text
#
#
#         if message.media_group_id:
#             if message.media_group_id not in albums_cache:
#                 albums_cache[message.media_group_id] = {
#                     "messages": [],
#                     "saving": False
#                 }
#
#             albums_cache[message.media_group_id]["messages"].append(message)
#
#
#             if not albums_cache[message.media_group_id]["saving"]:
#                 albums_cache[message.media_group_id]["saving"] = True
#                 asyncio.create_task(
#                     save_album_after_delay(message.media_group_id, msg_link, delay=3)
#                 )
#
#
#         elif message.photo:
#             print(f"   Тип: ФОТО")
#             print(f"   file_id: {message.photo.file_id}")
#             if message.caption:
#                 print(f"   Подпись: {message.caption[:100]}...")
#
#             media_list = [message.photo.file_id]
#
#         elif message.video:
#             print(f"   Тип: ВИДЕО")
#             print(f"   file_id: {message.video.file_id}")
#             print(f"   Длительность: {message.video.duration} сек")
#             if message.caption:
#                 print(f"   Подпись: {message.caption[:100]}...")
#
#             media_list = [message.video.file_id]
#
#         elif message.document:
#             print(f"   Тип: ДОКУМЕНТ")
#             print(f"   Имя файла: {message.document.file_name}")
#             print(f"   MIME тип: {message.document.mime_type}")
#
#             media_list = [message.document.file_id]
#
#         elif message.text:
#             print(f"   Тип: ТЕКСТ")
#             print(f"   Текст: {message.text[:100]}...")
#             media_list = []
#
#         else:
#             print(f"   Тип: ДРУГОЙ (не обрабатывается)")
#
#
#         if not message.media_group_id:
#             media_str = ",".join(media_list) if media_list else None
#             text = text or ""
#             post_data = {
#                 "text": text,
#                 "media": media_str,
#                 "source_url": msg_link,
#                 "published_at": datetime.now(),
#                 "is_published": True
#             }
#
#
#             await create_post(**post_data)
#             await send_post_to_channel(app, chat_id, post_data)
#
#         print("-" * 50)
#
#     except Exception as e:
#         error_msg = f"Ошибка обработки сообщения {message.id}: {e}"
#         await create_log('error', error_msg)
#         print(error_msg)
#         print("ошибка, но тоже сработало")




# @app.on_message(filters.all)
# async def kskd(client, message: Message):
#     if message.chat.id in groups_filter:
#         print(f"Сообщение из {message.chat.username}, {message.text}")


