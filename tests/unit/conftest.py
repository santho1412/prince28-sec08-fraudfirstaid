"""Shared fixtures for API unit tests."""

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from fraudfirstaid.api.deps import (
    check_db,
    get_gateway,
    get_ingest_repo,
    get_manifest,
    get_queue,
    get_repo,
    get_session,
    get_usage_repo,
)
from fraudfirstaid.api.main import create_app
from fraudfirstaid.config import Settings
from fraudfirstaid.llm.gateway import FakeLLM, LLMGateway

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


class FakeUsage:
    """Fake usage repository for API unit tests."""

    async def by_day(self, days: int = 7) -> list[dict[str, Any]]:
        return [
            {
                "day": "2026-11-25",
                "calls": 3,
                "errors": 1,
                "fallbacks": 1,
                "tokens_in": 300,
                "tokens_out": 120,
                "cost_inr": 0.0642,
            }
        ]


@pytest.fixture
def settings() -> Settings:
    """Provide isolated test settings."""
    return Settings(
        app_env="ci",
        database_url="postgresql://localhost:5432/unused",
        admin_token="test-token",  # pragma: allowlist secret
        _env_file=None,
    )


@pytest.fixture
def db_state() -> dict[str, bool]:
    """Control whether the fake database is available."""
    return {"available": True}


@pytest.fixture
def manifest() -> list[dict[str, Any]]:
    """Provide an in-memory ingestion manifest."""
    return [
        {
            "url": f"https://x.test/{number}.pdf",
            "source": "x",
            "licence": "CC BY 4.0",
            "path": f"data/raw/x/{number}.pdf",
            "sha256": str(number) * 64,
            "status": "downloaded",
        }
        for number in (1, 2)
    ] + [
        {
            "url": "https://x.test/3.pdf",
            "source": "x",
            "licence": "CC BY 4.0",
            "path": "data/raw/x/3.pdf",
            "sha256": "a" * 64,
            "status": "downloaded",
        },
        {
            "url": "https://x.test/4.pdf",
            "source": "x",
            "licence": "CC BY 4.0",
            "path": "data/raw/x/4.pdf",
            "sha256": "4" * 64,
            "status": "failed",
        },
    ]


@pytest.fixture
def client(
    settings: Settings,
    db_state: dict[str, bool],
    llm: FakeLLM,
    queue: Any,
    ingest_repo: Any,
    manifest: list[dict[str, Any]],
) -> Iterator[TestClient]:
    """Create an API client with fake dependencies."""

    app = create_app(settings)

    async def override_get_session():
        yield FakeDatabaseSession(
            should_fail=not db_state["available"],
        )

    def override_get_repo() -> FakeDocumentRepository:
        return FakeDocumentRepository()

    def override_get_gateway() -> LLMGateway:
        return LLMGateway([llm])

    def override_get_usage_repo() -> FakeUsage:
        return FakeUsage()

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_repo] = override_get_repo
    app.dependency_overrides[get_gateway] = override_get_gateway
    app.dependency_overrides[get_usage_repo] = override_get_usage_repo
    app.dependency_overrides[get_queue] = lambda: queue
    app.dependency_overrides[get_ingest_repo] = lambda: ingest_repo
    app.dependency_overrides[get_manifest] = lambda: manifest
    app.dependency_overrides[check_db] = lambda: db_state["available"]

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
