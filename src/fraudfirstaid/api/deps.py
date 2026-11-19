"""FastAPI dependency injection."""

from fastapi import Request

from fraudfirstaid.config import Settings, get_settings
from fraudfirstaid.store import RecordStore


def get_app_settings() -> Settings:
    """Return cached application settings."""
    return get_settings()


def get_record_store(request: Request) -> RecordStore:
    """Return the application's record store."""
    return request.app.state.record_store
