"""Health and readiness endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from fraudfirstaid.api.deps import get_record_store
from fraudfirstaid.store import RecordStore

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    """Check whether the application is running."""
    return {"status": "ok"}


@router.get("/ready")
def readiness(
    store: RecordStore = Depends(get_record_store),  # noqa: B008
):
    """Check whether the application can serve records."""
    if not store.records:
        raise HTTPException(
            status_code=503,
            detail="Record store is not ready.",
        )

    return {
        "status": "ready",
        "checks": {
            "records_loaded": True,
        },
    }
