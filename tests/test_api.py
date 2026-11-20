"""Unit tests for the Fraud First Aid API."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from fraudfirstaid.config import Settings


def test_health_is_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_when_database_is_available(client: TestClient) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"database": True},
    }


def test_ready_when_database_is_unavailable(
    client: TestClient,
    db_state: dict[str, bool],
) -> None:
    db_state["available"] = False

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "checks": {"database": False},
    }


def test_list_documents(client: TestClient) -> None:
    response = client.get("/v1/documents")
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 3
    assert body["count"] == 3
    assert len(body["items"]) == 3
    assert body["documents"] == body["items"]


def test_list_documents_with_limit(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"limit": 2})
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["count"] == 2


def test_list_documents_with_offset(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"offset": 2})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == ["003"]


def test_search_documents(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"q": "beta"})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == ["002"]


def test_filter_documents(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"issuer": "RBI"})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == [
        "001",
        "003",
    ]
    assert response.json()["filters"] == {"issuer": "RBI"}


def test_invalid_filter_name(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"Bad-Name": "1"})

    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")


def test_get_existing_document(client: TestClient) -> None:
    response = client.get("/v1/documents/001")

    assert response.status_code == 200
    assert response.json()["title"] == "Alpha guideline"


def test_get_missing_document(client: TestClient) -> None:
    response = client.get("/v1/documents/UNKNOWN")
    body = response.json()

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert body["status"] == 404
    assert body["title"] == "Not Found"
    assert body["detail"] == "No document with id 'UNKNOWN'."
    assert body["instance"] == "/v1/documents/UNKNOWN"


def test_bad_limit_is_422(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"limit": 0})

    assert response.status_code == 422
    assert response.json()["errors"][0]["field"] == "query.limit"


def test_bad_offset_is_422(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"offset": -1})

    assert response.status_code == 422
    assert response.json()["errors"][0]["field"] == "query.offset"


def test_request_id_is_echoed(client: TestClient) -> None:
    response = client.get(
        "/health",
        headers={"X-Request-ID": "abc123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "abc123"


def test_request_id_is_generated(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_app_requires_app_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
