"""Tests for application health and readiness endpoints."""

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fraudfirstaid.api.routes.health import router as health_router


def create_test_client(records: list | None = None) -> TestClient:
    """Create a test client with a controlled record store."""
    app = FastAPI()
    app.state.store = SimpleNamespace(records=records or [])
    app.include_router(health_router)

    return TestClient(app)


def test_health_returns_ok() -> None:
    """Health endpoint should return HTTP 200."""
    client = create_test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_ready_when_records_exist() -> None:
    """Readiness endpoint should succeed when records exist."""
    client = create_test_client(records=[{"id": "test-record"}])

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["checks"]["records_loaded"] is True


def test_ready_returns_503_when_no_records_exist() -> None:
    """Readiness endpoint should fail when no records exist."""
    client = create_test_client()

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["checks"]["records_loaded"] is False
