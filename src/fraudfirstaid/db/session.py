"""Asynchronous SQLAlchemy database engine and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from fraudfirstaid.config import Settings, get_settings
from fraudfirstaid.db.url import to_asyncpg_url


def make_engine(settings: Settings | None = None) -> AsyncEngine:
    """Create an asynchronous database engine from application settings."""
    config = settings or get_settings()

    if not config.database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    database_url = to_asyncpg_url(config.database_url)

    return create_async_engine(
        database_url,
        pool_pre_ping=True,
    )


def make_sessionmaker(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create an asynchronous session factory for the given engine."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


settings = get_settings()
engine = make_engine(settings)
AsyncSessionLocal = make_sessionmaker(engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session and close it after use."""
    async with AsyncSessionLocal() as session:
        yield session
