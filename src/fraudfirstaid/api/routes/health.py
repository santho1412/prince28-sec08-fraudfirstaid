"""Application health and readiness endpoints."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from fraudfirstaid.api.deps import DbSessionDep

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(request: Request) -> dict[str, str]:
    """Return application liveness and the deployed Git commit."""
    settings = request.app.state.settings

    return {
        "status": "ok",
        "version": settings.git_sha,
    }


@router.get("/ready", response_model=None)
async def ready(session: DbSessionDep) -> JSONResponse | dict[str, object]:
    """Check whether PostgreSQL is reachable."""
    try:
        await session.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError):
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "checks": {"database": False},
            },
        )

    return {
        "status": "ready",
        "checks": {"database": True},
    }
