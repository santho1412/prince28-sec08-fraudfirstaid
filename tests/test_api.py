"""Integration tests for the Fraud First Aid API."""

import pytest
from fastapi.testclient import TestClient

from fraudfirstaid.api.main import create_app
from fraudfirstaid.config import Settings


def test_health_is_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_when_records_loaded(client: TestClient) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


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
    assert ready_response.json() == {"status": "not_ready"}


def test_list_documents_returns_records(client: TestClient) -> None:
    response = client.get("/v1/documents")

    assert response.status_code == 200
    assert response.json()["count"] == 3
    assert len(response.json()["documents"]) == 3


def test_list_documents_respects_limit(client: TestClient) -> None:
    response = client.get("/v1/documents?limit=2")

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert len(response.json()["documents"]) == 2


def test_get_document_found(client: TestClient) -> None:
    response = client.get("/v1/documents/002")

    assert response.status_code == 200
    assert response.json()["id"] == "002"
    assert response.json()["title"] == "Beta circular"


def test_missing_document_is_problem_details(client: TestClient) -> None:
    response = client.get("/v1/documents/999")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["status"] == 404
    assert response.json()["title"] == "Not Found"
    assert response.json()["instance"] == "/v1/documents/999"


def test_bad_limit_is_422_problem(client: TestClient) -> None:
    response = client.get("/v1/documents?limit=0")

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["status"] == 422
    assert response.json()["title"] == "Unprocessable Entity"


def test_request_id_is_returned(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("x-request-id")


def test_app_refuses_to_start_without_app_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)

    with pytest.raises(ValueError):
        Settings(_env_file=None)
