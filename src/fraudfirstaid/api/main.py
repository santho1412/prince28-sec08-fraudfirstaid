"""App factory: build a fully wired FastAPI app from settings."""

import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from fraudfirstaid.api.errors import (
    http_exception_handler,
    validation_exception_handler,
)
from fraudfirstaid.api.middleware import RequestContextMiddleware
from fraudfirstaid.api.routes import chat
from fraudfirstaid.api.routes.documents import router as documents_router
from fraudfirstaid.api.routes.health import router as health_router
from fraudfirstaid.config import Settings, get_settings
from fraudfirstaid.db.llm_calls import make_recorder
from fraudfirstaid.db.session import make_engine, make_sessionmaker
from fraudfirstaid.llm.gateway import build_gateway
from fraudfirstaid.logging_setup import setup_logging

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""

    if settings is None:
        settings = get_settings()

    setup_logging(settings.log_level)
    engine = make_engine(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Manage the database engine lifecycle."""
        logger.info("Starting application")
        yield
        await engine.dispose()
        logger.info("Database engine disposed")

    app = FastAPI(
        title=settings.app_name,
        version="0.2.0",
        lifespan=lifespan,
    )

    app.state.settings = settings
    app.state.engine = engine
    app.state.sessionmaker = make_sessionmaker(engine)
    app.state.system_prompt = chat.load_prompt(settings.prompts_dir)
    app.state.gateway = build_gateway(
        settings,
        make_recorder(app.state.sessionmaker),
    )

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

    v1 = APIRouter(prefix="/v1")
    v1.include_router(chat.router)
    app.include_router(v1)

    return app
