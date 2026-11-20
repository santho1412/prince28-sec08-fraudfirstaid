"""Shared fixtures for API tests."""

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from fraudfirstaid.api.deps import get_document_repository
from fraudfirstaid.api.main import create_app
from fraudfirstaid.config import Settings
from fraudfirstaid.db.session import get_db

SAMPLE_DOCUMENTS: list[dict[str, Any]] = [
    {
        "id": "001",
        "title": "Alpha guideline",
        "year": 2023,
        "issuer": "RBI",
    },
    {
        "id": "002",
        "title": "Beta circular",
        "year": 2024,
        "issuer": "CERT-In",
    },
    {
        "id": "003",
        "title": "Gamma notice",
        "year": 2025,
        "issuer": "RBI",
    },
]


class FakeDatabaseSession:
    """Fake database session for readiness tests."""

    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    async def execute(self, statement: object) -> None:
        if self.should_fail:
            raise SQLAlchemyError("Database unavailable")


class FakeDocumentRepository:
    """In-memory document repository for API unit tests."""

    def __init__(self) -> None:
        self.records = [record.copy() for record in SAMPLE_DOCUMENTS]

    async def list(
        self,
        *,
        q: str | None,
        filters: dict[str, str],
        limit: int,
        offset: int,
    ) -> tuple[int, list[dict[str, Any]]]:
        records = self.records.copy()

        if q:
            records = [
                record
                for record in records
                if any(q.casefold() in str(value).casefold() for value in record.values())
            ]

        for key, value in filters.items():
            records = [
                record
                for record in records
                if str(record.get(key, "")).casefold() == value.casefold()
            ]

        total = len(records)
        return total, records[offset : offset + limit]

    async def get(self, external_id: str) -> dict[str, Any] | None:
        return next(
            (record for record in self.records if record["id"] == external_id),
            None,
        )


@pytest.fixture
def settings() -> Settings:
    """Provide isolated test settings."""
    return Settings(
        app_env="ci",
        database_url="postgresql://localhost:5432/unused",
        _env_file=None,
    )


@pytest.fixture
def db_state() -> dict[str, bool]:
    """Control whether the fake database is available."""
    return {"available": True}


@pytest.fixture
def client(
    settings: Settings,
    db_state: dict[str, bool],
) -> Iterator[TestClient]:
    """Create an API client with fake database dependencies."""
    app = create_app(settings)

    async def override_get_db():
        yield FakeDatabaseSession(
            should_fail=not db_state["available"],
        )

    def override_get_document_repository() -> FakeDocumentRepository:
        return FakeDocumentRepository()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_document_repository] = override_get_document_repository

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
