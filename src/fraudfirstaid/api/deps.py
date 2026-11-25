"""Dependencies: endpoints ask for these instead of building them."""

import asyncio
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from fraudfirstaid.config import Settings
from fraudfirstaid.db.llm_calls import UsageRepository
from fraudfirstaid.db.repository import DocumentRepository
from fraudfirstaid.db.session import get_db
from fraudfirstaid.llm.gateway import LLMGateway

DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """One session per request, closed automatically afterwards."""
    async with request.app.state.sessionmaker() as session:
        yield session


def get_document_repository(
    session: DbSessionDep,
) -> DocumentRepository:
    """Create a document repository for the current request."""
    return DocumentRepository(session)


async def check_db(request: Request) -> bool:
    """Can we run SELECT 1 within 2 seconds?"""
    try:
        async with request.app.state.engine.connect() as connection:
            await asyncio.wait_for(
                connection.execute(text("SELECT 1")),
                timeout=2,
            )
        return True
    except Exception:
        return False


def get_gateway(request: Request) -> LLMGateway:
    return request.app.state.gateway


async def get_usage_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UsageRepository:
    return UsageRepository(session)


SettingsDep = Annotated[Settings, Depends(get_app_settings)]
GatewayDep = Annotated[LLMGateway, Depends(get_gateway)]
UsageDep = Annotated[UsageRepository, Depends(get_usage_repo)]
DocumentRepositoryDep = Annotated[
    DocumentRepository,
    Depends(get_document_repository),
]
DbCheckDep = Annotated[bool, Depends(check_db)]
