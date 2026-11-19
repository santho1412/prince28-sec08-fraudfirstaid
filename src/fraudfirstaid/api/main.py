"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from fraudfirstaid.api.deps import get_app_settings
from fraudfirstaid.api.errors import install_error_handlers
from fraudfirstaid.api.middleware import RequestMiddleware
from fraudfirstaid.api.routes import documents, health
from fraudfirstaid.logging_setup import setup_logging
from fraudfirstaid.store import RecordStore


def create_app(settings=None) -> FastAPI:
    """Create and configure the FastAPI application."""
    if settings is None:
        settings = get_app_settings()

    setup_logging(settings.log_level)

    store = RecordStore(settings.data_file)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if store.data_file.exists():
            store.load()
        app.state.record_store = store
        yield

    app = FastAPI(
        title="FraudFirstAid",
        description="Evidence-based cyber fraud emergency response API for India.",
        version="0.1.0",
        lifespan=lifespan,
    )

    install_error_handlers(app)

    app.add_middleware(RequestMiddleware)

    app.include_router(health.router)
    app.include_router(documents.router)

    return app
