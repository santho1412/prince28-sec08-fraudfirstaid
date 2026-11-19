"""FastAPI dependencies shared across API routes."""

from typing import Annotated

from fastapi import Depends, Request

from fraudfirstaid.store import RecordStore


def get_store(request: Request) -> RecordStore:
    """Return the application record store."""
    return request.app.state.store


StoreDep = Annotated[RecordStore, Depends(get_store)]
