"""Document retrieval endpoints."""

from fastapi import APIRouter, HTTPException, Query

from fraudfirstaid.api.deps import StoreDep

router = APIRouter(prefix="/v1/documents", tags=["documents"])


@router.get("")
async def list_documents(
    store: StoreDep,
    limit: int = Query(default=100, ge=1, le=500),
    q: str | None = Query(default=None, min_length=1),
) -> dict[str, object]:
    """Return documents with optional search and pagination."""

    records = store.list_records(limit=500)

    if q:
        search_term = q.casefold()
        records = [
            record
            for record in records
            if any(search_term in str(value).casefold() for value in record.values())
        ]

    total = len(records)
    items = records[:limit]

    return {
        "total": total,
        "items": items,
        # Keep the existing response keys for compatibility.
        "count": len(items),
        "documents": items,
    }


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    store: StoreDep,
) -> dict[str, object]:
    """Return one document by its ID."""
    record = store.get_record(document_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No document with id '{document_id}'.",
        )

    return record
