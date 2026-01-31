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
            if kw.lower() in text:
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
        msg_error = 'Ошибка постинга'
        await create_log('error', msg_error)
        await app.send_message(chat_id=error_chat, text=msg_error)

async def send_post_channel(client, chat_id, post_data):

    print("\n" + "=" * 40)
    print("📤 send_post_channel CALLED")

    text = post_data.get("text", "") or ""
    media = post_data.get("media", [])

    print(f"📝 post_data.text len={len(text)}")
    print(f"📦 media count={len(media)}")

    # ---------- caption fallback ----------
    if not text and media:
        print("⚠️ text empty, searching caption in media")
        for i, m in enumerate(media):
            caption = m.get("caption")
            print(f"   media[{i}] caption={'YES' if caption else 'NO'}")
            if caption:
                text = caption
                print(f"✅ caption FOUND len={len(text)}")
                break

    print(f"🧾 FINAL text len={len(text)}")
    print(f"🧾 FINAL text preview:\n{text[:300]}")

    # ---------- categories ----------
    categories = await get_categories()
    print(f"📚 categories count={len(categories)}")

    # покажем первые 3 категории
    for c in categories[:3]:
        print(
            f"   ▶ category id={c.id} name={c.name} "
            f"keywords_len={len(c.keywords or '')}"
        )

    # ---------- detect ----------
    category = detect_category(text, categories)
    print(f"🏷 detect_category RESULT = {category}")

    if category != "Другое":
        text = f"<b>[{category}]</b>\n\n" + text
        print("✅ category prepended to text")
    else:
        print("⚠️ category == 'Другое', NOT prepended")

    # ---------- SEND ----------
    if not media:
        print("📤 sending TEXT message")
        await client.send_message(chat_id, text)
        return

    if len(media) == 1:
        m = media[0]
        print(f"📤 sending SINGLE media type={m['type']}")

        if m["type"] == "photo":
            await client.send_photo(chat_id, m["file"], caption=text)

        elif m["type"] == "video":
            await client.send_video(chat_id, m["file"], caption=text)

        elif m["type"] == "document":
            await client.send_document(chat_id, m["file"], caption=text)

        return

    print("📤 sending MEDIA GROUP")
    group = []

    for i, m in enumerate(media):
        caption = text if i == 0 else None
        print(f"   media[{i}] type={m['type']} caption={'YES' if caption else 'NO'}")

        if m["type"] == "photo":
            group.append(InputMediaPhoto(m["file"], caption=caption))

        elif m["type"] == "video":
            group.append(InputMediaVideo(m["file"], caption=caption))

        elif m["type"] == "document":
            group.append(InputMediaDocument(m["file"], caption=caption))

    await client.send_media_group(chat_id, group)

    print("✅ send_post_channel DONE")
    print("=" * 40)



