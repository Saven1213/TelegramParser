#
from pyrogram import filters
from pyrogram.types import Message
import traceback
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
    print(f"\n🔹 START HANDLER | Chat ID: {message.chat.id} | Message ID: {message.id}")

    try:
        # 1. Получаем список групп
        groups_ids = await get_group_ids()
        print(f"📊 Available groups IDs: {groups_ids}")
        print(f"🎯 Current chat ID: {message.chat.id}")
        print(f"✅ Chat in allowed list: {message.chat.id in groups_ids}")

        if message.chat.id not in groups_ids:
            print("⏩ Skipping - chat not in allowed list")
            return

        print("\n" + "=" * 20 + " NEW MESSAGE " + "=" * 20)
        print(f"📩 msg_id={message.id}")
        print(f"📦 media_group_id={message.media_group_id}")
        print(f"🖼 photo={bool(message.photo)} video={bool(message.video)} doc={bool(message.document)}")
        print(f"📝 caption={bool(message.caption)} text={bool(message.text)}")

        # 2. Получаем информацию о группе источника
        print(f"\n🔍 Getting source group for chat ID: {message.chat.id}")
        group = await get_group(message.chat.id)
        print(f"📌 Source group: {group}")
        if group:
            print(f"🏙️ Source city: {group.city}")
        else:
            print("❌ Source group not found!")
            return

        # 3. Получаем целевую группу
        print(f"\n🎯 Getting target group for city: {group.city}")
        target_group = await get_target_group(group.city)
        print(f"📌 Target group object: {target_group}")

        if target_group:
            print(f"✅ Target group found:")
            print(f"   Name: {target_group.name}")
            print(f"   Group ID: {target_group.group_id}")
            print(f"   City: {target_group.city}")
            print(f"   Type of group_id: {type(target_group.group_id)}")
        else:
            print("❌ Target group not found for this city!")
            return

        # 4. Проверяем валидность ID целевой группы
        print(f"\n🔎 Validating target group ID: {target_group.group_id}")
        if target_group.group_id is None:
            print("❌ ERROR: target_group.group_id is None!")
            return

        if not isinstance(target_group.group_id, int):
            print(f"❌ ERROR: group_id is not integer! Type: {type(target_group.group_id)}")
            return

        print(f"✅ Group ID is valid integer: {target_group.group_id}")

        # 5. Проверяем доступ бота к целевой группе
        print(f"\n🤖 Checking bot access to target group: {target_group.group_id}")
        try:
            chat_info = await client.get_chat(target_group.group_id)
            print(f"✅ Bot has access to target group:")
            print(f"   Title: {chat_info.title}")
            print(f"   Type: {chat_info.type}")
            print(f"   Username: {chat_info.username}")
        except Exception as access_error:
            print(f"❌ Bot has NO access to target group {target_group.group_id}: {access_error}")
            print(f"⚠️  Make sure bot is added to this group as admin/member")
            return

        # -------- Формируем ссылку --------
        is_forum = message.chat.is_forum
        topic_id = message.message_thread_id

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

        print(f"🔗 Generated link: {msg_link}")

        # -------- Обработка медиа-групп --------
        if message.media_group_id:
            print(f"\n📚 MESSAGE IS PART OF MEDIA GROUP: {message.media_group_id}")

            if message.media_group_id not in albums_cache:
                print("🆕 New album created in cache")
                albums_cache[message.media_group_id] = {
                    "messages": [],
                    "saving": False
                }

            albums_cache[message.media_group_id]["messages"].append(message)
            print(f"➕ Added to album | Total messages: {len(albums_cache[message.media_group_id]['messages'])}")

            if not albums_cache[message.media_group_id]["saving"]:
                print("⏳ Scheduling album save with delay")
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

        # -------- ОДИНОЧНОЕ СООБЩЕНИЕ --------
        print("\n📄 SINGLE MESSAGE PROCESSING")

        text = extract_text(message)
        print(f"📝 Extracted text length: {len(text)}")
        print(f"📝 Text preview: {text[:100]}{'...' if len(text) > 100 else ''}")

        # Проверка стоп-слов
        if text:
            stop_words_found = [word for word in STOP_WORDS if word in text.lower()]
            if stop_words_found:
                print(f"⛔ STOP WORD MATCH: {stop_words_found}")
                return
            else:
                print("✅ No stop words found")

        text += f'\n\n{msg_link}'

        # -------- ОТПРАВКА В ЦЕЛЕВУЮ ГРУППУ --------
        print(f"\n🚀 ATTEMPTING TO SEND TO TARGET GROUP: {target_group.group_id}")

        try:
            if message.photo:
                print("📸 Processing PHOTO")
                file = await message.download(in_memory=True)
                print(f"✅ Photo downloaded, size: {len(file.getvalue()) if hasattr(file, 'getvalue') else 'N/A'}")
                await client.send_photo(
                    chat_id=target_group.group_id,
                    photo=file,
                    caption=text
                )
                print("✅ Photo sent successfully")
                return

            elif message.video:
                print("🎬 Processing VIDEO")
                file = await message.download(in_memory=True)
                print(f"✅ Video downloaded")
                await client.send_video(
                    chat_id=target_group.group_id,
                    video=file,
                    caption=text
                )
                print("✅ Video sent successfully")
                return

            elif message.document:
                print("📄 Processing DOCUMENT")
                file = await message.download(in_memory=True)
                print(f"✅ Document downloaded")
                await client.send_document(
                    chat_id=target_group.group_id,
                    document=file,
                    caption=text
                )
                print("✅ Document sent successfully")
                return

            elif text:
                print("📝 Processing TEXT MESSAGE")
                print(f"📤 Sending text to {target_group.group_id}")
                print(f"📄 Text to send: {text[:200]}...")

                await client.send_message(
                    chat_id=target_group.group_id,
                    text=text
                )
                print("✅ Text message sent successfully")
                return

            else:
                print("⚠️ FALLBACK: Unsupported message type")
                await error(
                    f"❌ Unsupported message type\n\n<a href='{msg_link}'>Message link</a>",
                    error_chat
                )

        except Exception as send_error:
            print(f"❌ ERROR SENDING TO TARGET GROUP {target_group.group_id}:")
            print(f"   Error type: {type(send_error).__name__}")
            print(f"   Error message: {str(send_error)}")
            print(f"   Target group ID: {target_group.group_id}")
            print(f"   Target group name: {target_group.name}")
            raise send_error  # Перебрасываем ошибку в общий обработчик

    except Exception as e:
        print("\n" + "🔥" * 20 + " UNHANDLED EXCEPTION " + "🔥" * 20)
        print(f"❌ Exception type: {type(e).__name__}")
        print(f"❌ Exception message: {str(e)}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        print("🔥" * 50)

        await error(f"Handler error: {str(e)}", error_chat)



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


