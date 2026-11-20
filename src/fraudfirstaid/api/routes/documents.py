"""Document retrieval endpoints."""

from fastapi import APIRouter, HTTPException, Query, Request

from fraudfirstaid.api.deps import DocumentRepositoryDep
from fraudfirstaid.db.repository import FILTER_KEY

router = APIRouter(prefix="/v1/documents", tags=["documents"])


@router.get("")
async def list_documents(
    request: Request,
    repository: DocumentRepositoryDep,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    q: str | None = Query(default=None, min_length=1),
) -> dict[str, object]:
    """Return documents with optional search, filters, and pagination."""

    reserved_parameters = {"limit", "offset", "q"}
    filters: dict[str, str] = {}

    for key, value in request.query_params.items():
        if key in reserved_parameters:
            continue

        if not FILTER_KEY.fullmatch(key):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid filter name: '{key}'.",
            )

        filters[key] = value

    total, items = await repository.list(
        q=q,
        filters=filters,
        limit=limit,
        offset=offset,
    )

    return {
        "total": total,
        "items": items,
        "count": len(items),
        "documents": items,
        "filters": filters,
    }


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    repository: DocumentRepositoryDep,
) -> dict[str, object]:
    """Return one document by its ID."""

    record = await repository.get(document_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No document with id '{document_id}'.",
        )

    return record
