from datetime import datetime
from typing import Optional

from db.models import async_session, Post
from sqlalchemy import insert

async def create_post(
    text: str,
    media: Optional[str],
    source_url: str,
    published_at: datetime,
    is_published: bool
):
    async with async_session() as session:
        post = Post(
            text=text,
            media=media,
            source_url=source_url,
            published_at=published_at,
            is_published=is_published
        )
        session.add(post)
        await session.commit()