from sqlalchemy import String, Integer, Boolean, Float, DateTime
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from typing import Optional
from datetime import datetime

engine = create_async_engine(url='sqlite+aiosqlite:///tg_parser.db')

async_session = async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = "posts"


    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    media: Mapped[Optional[str]] = mapped_column(String)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)


class Category(Base):
    __tablename__ = "categories"


    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    keywords: Mapped[str] = mapped_column(String, nullable=False)


class Log(Base):
    __tablename__ = "logs"


    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # parsing, publishing, error
    message: Mapped[str] = mapped_column(String, nullable=False)



async def create_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)