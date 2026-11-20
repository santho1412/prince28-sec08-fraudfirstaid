"""Integration tests: a real Postgres database, created fresh for each test run.

Set TEST_DATABASE_URL to a PostgreSQL database where the app user can
create and drop databases. With Docker Compose running, the Poe task
provides the local test_db URL automatically.
Without TEST_DATABASE_URL, integration tests are skipped.
"""

import asyncio
import os
import uuid

import pytest
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import command
from fraudfirstaid.config import get_settings
from fraudfirstaid.db.url import to_asyncpg_url

BASE_URL = os.getenv("TEST_DATABASE_URL")


def pytest_collection_modifyitems(config, items):
    """Skip integration tests when no test database URL is configured."""
    if BASE_URL:
        return

    skip = pytest.mark.skip(reason="set TEST_DATABASE_URL to run integration tests")
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(skip)


async def _admin(sql: str) -> None:
    """Execute a database administration statement."""
    if not BASE_URL:
        raise RuntimeError("TEST_DATABASE_URL is not configured.")

    engine = create_async_engine(
        to_asyncpg_url(BASE_URL),
        isolation_level="AUTOCOMMIT",
    )
    try:
        async with engine.connect() as connection:
            await connection.execute(text(sql))
    finally:
        await engine.dispose()


@pytest.fixture(scope="session")
def database_url():
    """Create a temporary database, migrate it, and drop it after the run."""
    if not BASE_URL:
        pytest.skip("set TEST_DATABASE_URL to run integration tests")

    name = f"test_{uuid.uuid4().hex[:8]}"

    asyncio.run(_admin(f'CREATE DATABASE "{name}"'))

    url = make_url(to_asyncpg_url(BASE_URL)).set(database=name)
    url_string = url.render_as_string(hide_password=False)

    patch = pytest.MonkeyPatch()
    patch.setenv("APP_ENV", "ci")
    patch.setenv("DATABASE_URL", url_string)
    get_settings.cache_clear()

    try:
        command.upgrade(Config("alembic.ini"), "head")
        yield url_string
    finally:
        get_settings.cache_clear()
        patch.undo()
        get_settings.cache_clear()
        asyncio.run(_admin(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
