"""Integration tests against a freshly migrated PostgreSQL database."""

import asyncio
import json
import os
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fraudfirstaid.api.deps import get_db
from fraudfirstaid.api.main import create_app
from fraudfirstaid.config import Settings
from fraudfirstaid.db.models import Document
from fraudfirstaid.db.repository import DocumentRepository
from fraudfirstaid.db.url import to_asyncpg_url

ROWS = [
    {
        "id": "001",
        "title": "Alpha",
        "kind": "circular",
        "year": 2024,
        "tags": ["a", "b"],
    },
    {
        "id": "002",
        "title": "Beta",
        "kind": "guideline",
        "year": 2025,
        "tags": ["b"],
    },
    {
        "id": "003",
        "title": "Gamma",
        "kind": "circular",
        "year": 2025,
        "tags": [],
    },
]


@pytest.fixture
def settings(database_url):
    """Provide settings pointing at the temporary integration database."""
    return Settings(
        app_env="ci",
        database_url=database_url,
        _env_file=None,
    )


@pytest.fixture
async def seeded(settings):
    """Replace the documents with predictable test rows for each test."""
    engine = create_async_engine(to_asyncpg_url(settings.database_url))
    try:
        async with async_sessionmaker(engine)() as session, session.begin():
            await session.execute(text("DELETE FROM documents"))

            for record in ROWS:
                metadata = {
                    key: value for key, value in record.items() if key not in ("id", "title")
                }
                session.add(
                    Document(
                        external_id=record["id"],
                        title=record["title"],
                        sha256=(record["id"] * 22)[:64],
                        metadata_=metadata,
                    )
                )
    finally:
        await engine.dispose()

    return settings


async def test_migrations_created_the_tables(settings):
    engine = create_async_engine(to_asyncpg_url(settings.database_url))
    try:
        async with engine.connect() as connection:
            tables = set(
                await connection.scalars(
                    text(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = 'public'"
                    )
                )
            )
            version = await connection.scalar(text("SELECT version_num FROM alembic_version"))
    finally:
        await engine.dispose()

    assert {"documents", "pages", "alembic_version"} <= tables
    assert version


@pytest.mark.parametrize(
    ("filters", "expected"),
    [
        ({"kind": "circular"}, ["001", "003"]),
        ({"year": "2025"}, ["002", "003"]),
        ({"tags": "b"}, ["001", "002"]),
        ({"kind": "circular", "year": "2025"}, ["003"]),
    ],
)
async def test_repository_filters(seeded, filters, expected):
    engine = create_async_engine(to_asyncpg_url(seeded.database_url))
    try:
        async with async_sessionmaker(engine)() as session:
            total, items = await DocumentRepository(session).list(
                q=None,
                filters=filters,
                limit=10,
                offset=0,
            )
    finally:
        await engine.dispose()

    assert [item["id"] for item in items] == expected
    assert total == len(expected)


def test_api_against_real_database(seeded):
    engine = create_async_engine(to_asyncpg_url(seeded.database_url))
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app = create_app(seeded)
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            assert client.get("/ready").json()["checks"]["database"] is True
            assert client.get("/v1/documents/002").json()["title"] == "Beta"
            assert client.get("/v1/documents", params={"q": "gamm"}).json()["total"] == 1
    finally:
        app.dependency_overrides.clear()
        asyncio.run(engine.dispose())


def test_loader_is_idempotent(database_url, tmp_path):
    data = tmp_path / "records.json"
    data.write_text(
        json.dumps(
            [
                {"id": "L1", "title": "Loader Alpha", "x": 1},
                {"id": "L2", "title": "Loader Beta", "x": 2},
            ]
        ),
        encoding="utf-8",
    )

    env = {
        **os.environ,
        "APP_ENV": "ci",
        "DATABASE_URL": database_url,
        "DATA_FILE": str(data),
    }

    def run():
        result = subprocess.run(
            [sys.executable, "scripts/load_db.py"],
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout

    assert "inserted=2" in run()
    assert "inserted=0 updated=0 unchanged=2" in run()
