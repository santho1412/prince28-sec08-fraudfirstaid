"""FastAPI application factory."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from fraudfirstaid.api.errors import (
    http_exception_handler,
    validation_exception_handler,
)
from fraudfirstaid.api.middleware import RequestContextMiddleware
from fraudfirstaid.api.routes.documents import router as documents_router
from fraudfirstaid.api.routes.health import router as health_router
from fraudfirstaid.config import Settings, get_settings
from fraudfirstaid.db.session import engine
from fraudfirstaid.logging_setup import setup_logging

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""

    if settings is None:
        settings = get_settings()

    setup_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Manage the database engine lifecycle."""
        logger.info("Starting application")
        yield
        await engine.dispose()
        logger.info("Database engine disposed")

    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )

    app.state.settings = settings

    app.add_middleware(RequestContextMiddleware)

    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )

    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )

    app.include_router(health_router)
    app.include_router(documents_router)

    return app
