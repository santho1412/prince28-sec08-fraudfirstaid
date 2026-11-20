"""Tests for application health and readiness endpoints."""

from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from fraudfirstaid.api.routes.health import router as health_router
from fraudfirstaid.db.session import get_db


class FakeDatabaseSession:
    """Fake database session for readiness tests."""

    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    async def execute(self, statement: object) -> None:
        if self.should_fail:
            raise SQLAlchemyError("Database unavailable")


def create_test_client(database_available: bool = True) -> TestClient:
    """Create a test client with a controlled database session."""

    async def override_get_db() -> AsyncGenerator[FakeDatabaseSession, None]:
        yield FakeDatabaseSession(should_fail=not database_available)

    app = FastAPI()
    app.dependency_overrides[get_db] = override_get_db
    app.include_router(health_router)

    return TestClient(app)


def test_health_returns_ok() -> None:
    client = create_test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_ready_when_database_is_available() -> None:
    client = create_test_client()

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"database": True},
    }


def test_ready_returns_503_when_database_is_unavailable() -> None:
    client = create_test_client(database_available=False)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "checks": {"database": False},
    }
