"""Tests for document retrieval endpoints."""

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException

from fraudfirstaid.api.errors import http_exception_handler
from fraudfirstaid.api.routes.documents import router as documents_router

SAMPLE_RECORDS = [
    {"id": "DOC001", "title": "UPI Fraud"},
    {"id": "DOC002", "title": "Phishing"},
    {"id": "DOC003", "title": "Identity Theft"},
]


def create_test_client() -> TestClient:
    """Create a test client with sample document records."""
    app = FastAPI()

    app.state.store = SimpleNamespace(
        records=SAMPLE_RECORDS,
        list_records=lambda limit=100: SAMPLE_RECORDS[:limit],
        get_record=lambda record_id: next(
            (record for record in SAMPLE_RECORDS if record["id"] == record_id),
            None,
        ),
    )

    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )
    app.include_router(documents_router)

    return TestClient(app)


def test_list_documents() -> None:
    """Document listing should return all sample records."""
    client = create_test_client()

    response = client.get("/v1/documents")
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 3
    assert len(body["items"]) == 3
    assert body["count"] == 3
    assert len(body["documents"]) == 3


def test_list_documents_with_limit() -> None:
    """Document listing should respect the requested limit."""
    client = create_test_client()

    response = client.get("/v1/documents?limit=2")
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["count"] == 2


def test_search_documents() -> None:
    """Document search should filter records by text."""
    client = create_test_client()

    response = client.get("/v1/documents?q=phishing")

    assert response.status_code == 200
    assert [record["id"] for record in response.json()["items"]] == ["DOC002"]


def test_get_existing_document() -> None:
    """An existing document should be returned successfully."""
    client = create_test_client()

    response = client.get("/v1/documents/DOC001")

    assert response.status_code == 200
    assert response.json() == SAMPLE_RECORDS[0]


def test_get_missing_document() -> None:
    """A missing document should return a Problem Details response."""
    client = create_test_client()

    response = client.get("/v1/documents/UNKNOWN")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")

    body = response.json()

    assert body["status"] == 404
    assert body["title"] == "Not Found"
    assert body["detail"] == "No document with id 'UNKNOWN'."
    assert body["instance"] == "/v1/documents/UNKNOWN"
