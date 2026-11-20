"""FastAPI dependencies shared across API routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fraudfirstaid.db.repository import DocumentRepository
from fraudfirstaid.db.session import get_db

DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_document_repository(
    session: DbSessionDep,
) -> DocumentRepository:
    """Create a document repository for the current request."""
    return DocumentRepository(session)


DocumentRepositoryDep = Annotated[
    DocumentRepository,
    Depends(get_document_repository),
]
