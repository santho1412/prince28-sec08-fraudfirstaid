"""Integration tests for the Fraud First Aid API."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from fraudfirstaid.api.main import create_app
from fraudfirstaid.config import Settings


def test_health_is_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_when_records_loaded(client: TestClient) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["checks"]["records_loaded"] is True


def test_ready_is_503_when_data_file_missing(tmp_path) -> None:
    settings = Settings(
        app_env="ci",
        data_file=tmp_path / "missing.json",
    )

    with TestClient(create_app(settings)) as test_client:
        health_response = test_client.get("/health")
        ready_response = test_client.get("/ready")

    assert health_response.status_code == 200
    assert ready_response.status_code == 503
    assert ready_response.json()["checks"]["records_loaded"] is False


def test_list_documents_paginates(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"limit": 2})
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 3
    assert len(body["items"]) == 2


def test_search_filters_records(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"q": "beta"})

    assert response.status_code == 200
    assert [record["id"] for record in response.json()["items"]] == ["002"]


def test_get_document_found(client: TestClient) -> None:
    response = client.get("/v1/documents/001")

    assert response.status_code == 200
    assert response.json()["title"] == "Alpha guideline"


def test_missing_document_is_problem_details(client: TestClient) -> None:
    response = client.get("/v1/documents/999")
    body = response.json()

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert body["status"] == 404
    assert body["title"] == "Not Found"
    assert body["request_id"] == response.headers["X-Request-ID"]


def test_bad_limit_is_422_problem(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"limit": 0})

    assert response.status_code == 422
    assert response.json()["errors"][0]["field"] == "query.limit"


def test_request_id_is_echoed(client: TestClient) -> None:
    response = client.get(
        "/health",
        headers={"X-Request-ID": "abc123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "abc123"


def test_request_id_is_generated_when_missing(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("x-request-id")


def test_app_refuses_to_start_without_app_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
