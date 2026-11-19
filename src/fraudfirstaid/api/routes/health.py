"""Application health and readiness endpoints."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Return a simple liveness response."""
    return {"status": "ok"}


@router.get("/ready", response_model=None)
async def ready(request: Request) -> JSONResponse | dict[str, object]:
    """Check whether the application is ready to serve requests."""
    store = getattr(request.app.state, "store", None)
    records_loaded = store is not None and bool(store.records)

    if not records_loaded:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "checks": {"records_loaded": False},
            },
        )

    return {
        "status": "ready",
        "checks": {"records_loaded": True},
    }
