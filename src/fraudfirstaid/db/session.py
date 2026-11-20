"""Asynchronous SQLAlchemy database engine and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from fraudfirstaid.config import get_settings
from fraudfirstaid.db.url import to_asyncpg_url

settings = get_settings()

if not settings.database_url:
    raise RuntimeError("DATABASE_URL is not configured.")

DATABASE_URL = to_asyncpg_url(settings.database_url)

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session and close it after use."""
    async with AsyncSessionLocal() as session:
        yield session
