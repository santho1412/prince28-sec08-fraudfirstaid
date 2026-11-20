"""Tests for document retrieval endpoints."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException

from fraudfirstaid.api.deps import get_document_repository
from fraudfirstaid.api.errors import http_exception_handler
from fraudfirstaid.api.routes.documents import router as documents_router

SAMPLE_RECORDS = [
    {"id": "DOC001", "title": "UPI Fraud", "issuer": "RBI"},
    {"id": "DOC002", "title": "Phishing", "issuer": "CERT-In"},
    {"id": "DOC003", "title": "Identity Theft", "issuer": "RBI"},
]


class FakeDocumentRepository:
    """In-memory repository for endpoint tests."""

    async def list(
        self,
        *,
        q: str | None,
        filters: dict[str, str],
        limit: int,
        offset: int,
    ) -> tuple[int, list[dict]]:
        records = SAMPLE_RECORDS.copy()

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
            (record for record in SAMPLE_RECORDS if record["id"] == external_id),
            None,
        )


def create_test_client() -> TestClient:
    """Create a test client with a fake repository."""
    app = FastAPI()

    app.dependency_overrides[get_document_repository] = FakeDocumentRepository

    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )
    app.include_router(documents_router)

    return TestClient(app)


def test_list_documents() -> None:
    client = create_test_client()

    response = client.get("/v1/documents")
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 3
    assert len(body["items"]) == 3
    assert body["count"] == 3
    assert len(body["documents"]) == 3


def test_list_documents_with_limit() -> None:
    client = create_test_client()

    response = client.get("/v1/documents?limit=2")
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["count"] == 2


def test_search_documents() -> None:
    client = create_test_client()

    response = client.get("/v1/documents?q=phishing")

    assert response.status_code == 200
    assert [record["id"] for record in response.json()["items"]] == ["DOC002"]


def test_filter_documents() -> None:
    client = create_test_client()

    response = client.get("/v1/documents?issuer=RBI")

    assert response.status_code == 200
    assert [record["id"] for record in response.json()["items"]] == [
        "DOC001",
        "DOC003",
    ]
    assert response.json()["filters"] == {"issuer": "RBI"}


def test_invalid_filter_name() -> None:
    client = create_test_client()

    response = client.get("/v1/documents?Bad-Name=1")

    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")


def test_get_existing_document() -> None:
    client = create_test_client()

    response = client.get("/v1/documents/DOC001")

    assert response.status_code == 200
    assert response.json() == SAMPLE_RECORDS[0]


def test_get_missing_document() -> None:
    client = create_test_client()

    response = client.get("/v1/documents/UNKNOWN")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")

    body = response.json()

    assert body["status"] == 404
    assert body["title"] == "Not Found"
    assert body["detail"] == "No document with id 'UNKNOWN'."
    assert body["instance"] == "/v1/documents/UNKNOWN"
