"""Document retrieval endpoints."""

from fastapi import APIRouter, HTTPException, Query

from fraudfirstaid.api.deps import StoreDep

router = APIRouter(prefix="/v1/documents", tags=["documents"])


@router.get("")
async def list_documents(
    store: StoreDep,
    limit: int = Query(default=100, ge=1, le=500),
) -> dict[str, object]:
    """Return a limited list of documents."""

    records = store.list_records(limit=limit)

    return {
        "count": len(records),
        "documents": records,
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
