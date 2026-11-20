"""Shared fixtures for API tests."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from fraudfirstaid.api.deps import get_document_repository
from fraudfirstaid.api.main import create_app
from fraudfirstaid.config import Settings
from fraudfirstaid.db.session import get_db

SAMPLE = [
    {"id": "001", "title": "Alpha guideline", "year": 2023},
    {"id": "002", "title": "Beta circular", "year": 2024},
    {"id": "003", "title": "Gamma notice", "year": 2025},
]


class FakeDatabaseSession:
    """Fake database session for readiness tests."""

    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    async def execute(self, statement: object) -> None:
        if self.should_fail:
            raise SQLAlchemyError("Database unavailable")


class FakeDocumentRepository:
    """Fake document repository for API tests."""

    async def list(
        self,
        *,
        q: str | None,
        filters: dict[str, str],
        limit: int,
        offset: int,
    ) -> tuple[int, list[dict]]:
        records = SAMPLE.copy()

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

    async def get(self, external_id: str) -> dict | None:
        return next(
            (record for record in SAMPLE if record["id"] == external_id),
            None,
        )


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Create an API test client with fake database dependencies."""
    app = create_app(Settings(app_env="ci"))

    async def override_get_db():
        yield FakeDatabaseSession()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_document_repository] = FakeDocumentRepository

    with TestClient(app) as test_client:
        yield test_client
