from datetime import datetime
from db.models import async_session, Log
from sqlalchemy import insert

async def create_log(event_type: str, message: str) -> None:
    """Создает запись в логах"""
    async with async_session() as session:
        log = Log(
            event_type=event_type,
            message=message,
            timestamp=datetime.now()
        )
        session.add(log)
        await session.commit()