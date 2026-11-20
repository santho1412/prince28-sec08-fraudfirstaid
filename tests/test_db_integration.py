"""Optional read-only integration tests for PostgreSQL."""

import asyncio
import os
from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from fraudfirstaid.db.models import Document
from fraudfirstaid.db.repository import DocumentRepository
from fraudfirstaid.db.url import to_asyncpg_url

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL is not configured",
)


def run_database_test(
    operation: Callable[[AsyncEngine], Awaitable[Any]],
) -> Any:
    """Run a read-only database test using a separate test engine."""

    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL is not configured")

    async def run() -> Any:
        engine = create_async_engine(
            to_asyncpg_url(TEST_DATABASE_URL),
            pool_pre_ping=True,
        )

        try:
            return await operation(engine)
        finally:
            await engine.dispose()

    return asyncio.run(run())


def test_database_connection() -> None:
    """Verify that the test PostgreSQL database is reachable."""

    async def check(engine: AsyncEngine) -> None:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            assert result.scalar_one() == 1

    run_database_test(check)


def test_documents_table_is_accessible() -> None:
    """Verify that the migrated documents table can be queried."""

    async def check(engine: AsyncEngine) -> None:
        async with engine.connect() as connection:
            result = await connection.execute(select(func.count()).select_from(Document))
            assert result.scalar_one() >= 0

    run_database_test(check)


def test_document_repository_reads_database() -> None:
    """Verify that the repository can list and retrieve documents."""

    async def check(engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            repository = DocumentRepository(session)

            total, items = await repository.list(
                q=None,
                filters={},
                limit=1,
                offset=0,
            )

            assert total >= 0
            assert len(items) <= 1

            if items:
                document = await repository.get(items[0]["id"])
                assert document == items[0]

    run_database_test(check)
