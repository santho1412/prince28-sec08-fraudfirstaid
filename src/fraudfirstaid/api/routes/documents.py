"""Document listing, searching, and retrieval endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query

from fraudfirstaid.api.deps import get_record_store
from fraudfirstaid.store import RecordStore

router = APIRouter(prefix="/v1/documents", tags=["Documents"])


@router.get("")
def list_documents(
    limit: int = Query(default=100, ge=1, le=100),
    q: str | None = Query(default=None),
    store: RecordStore = Depends(get_record_store),  # noqa: B008
):
    """List and search documents with pagination."""
    records = store.records

    if q:
        search_term = q.casefold()
        records = [
            record
            for record in records
            if search_term in " ".join(str(value) for value in record.values()).casefold()
        ]

    total = len(records)
    items = records[:limit]

    return {
        "total": total,
        "items": items,
    }


@router.get("/{document_id}")
def get_document(
    document_id: str,
    store: RecordStore = Depends(get_record_store),  # noqa: B008
):
    """Retrieve a document by ID."""
    record = store.get_record(document_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No document with id '{document_id}'.",
        )

    return record
