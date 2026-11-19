"""FastAPI application factory."""

from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException

from fraudfirstaid.api.errors import http_exception_handler
from fraudfirstaid.api.middleware import RequestContextMiddleware
from fraudfirstaid.api.routes.documents import router as documents_router
from fraudfirstaid.api.routes.health import router as health_router
from fraudfirstaid.config import get_settings
from fraudfirstaid.logging_setup import setup_logging
from fraudfirstaid.store import RecordStore


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = get_settings()

    setup_logging(settings.log_level)

    store = RecordStore(settings.data_file)
    store.load()

    app = FastAPI(title=settings.app_name)

    app.state.store = store

    app.add_middleware(RequestContextMiddleware)

    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )

    app.include_router(health_router)
    app.include_router(documents_router)

    return app
