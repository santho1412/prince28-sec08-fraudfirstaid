"""Integration tests for parser storage against real PostgreSQL."""

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fraudfirstaid.db.models import Document, Page, ParseFailure
from fraudfirstaid.db.url import to_asyncpg_url
from fraudfirstaid.ingest.parse import ParsedDoc, ParsedPage, ParseError
from fraudfirstaid.ingest.store import (
    document_id,
    failed_paths,
    parsed_ids,
    save_document,
    save_failure,
)


def make_record():
    sha256 = uuid.uuid4().hex * 2
    return {
        "sha256": sha256,
        "path": f"data/raw/test/{sha256}.md",
        "url": "https://example.org/fever.pdf",
        "source": "test",
        "licence": "Test licence",
    }


def make_parsed():
    return ParsedDoc(
        parser="markdown",
        kind="markdown",
        title="Fever Guidance",
        pages=[
            ParsedPage(
                page_no=1,
                text="Recognising fever symptoms and seeking help.",
                headings=["Fever", "Symptoms"],
            ),
            ParsedPage(
                page_no=2,
                text="Contact a healthcare professional for advice.",
                headings=["Fever", "Next steps"],
            ),
        ],
    )


@pytest.mark.asyncio
async def test_save_document_persists_document_and_pages(database_url):
    engine = create_async_engine(to_asyncpg_url(database_url))
    try:
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            record = make_record()
            parsed = make_parsed()

            await save_document(session, record, parsed)

            document = await session.scalar(
                select(Document).where(Document.external_id == document_id(record["sha256"]))
            )
            assert document is not None
            assert document.title == "Fever Guidance"
            assert document.doc_type == "markdown"
            assert document.metadata_["pages"] == 2

            pages = list(
                await session.scalars(
                    select(Page).where(Page.document_id == document.id).order_by(Page.page_no)
                )
            )
            assert len(pages) == 2
            assert pages[0].headings == ["Fever", "Symptoms"]
            assert pages[1].headings == ["Fever", "Next steps"]
            assert document.external_id in await parsed_ids(session)
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_save_failure_increments_attempts(database_url):
    engine = create_async_engine(to_asyncpg_url(database_url))
    try:
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            record = make_record()
            error = ParseError("invalid_file", "Unable to read source file")

            await save_failure(session, record, error)
            await save_failure(
                session,
                record,
                ParseError("invalid_file", "Retry failed"),
            )

            failure = await session.scalar(
                select(ParseFailure).where(ParseFailure.path == record["path"])
            )
            assert failure is not None
            assert failure.attempts == 2
            assert failure.reason == "invalid_file"
            assert failure.detail == "Retry failed"
            assert await failed_paths(session) == {record["path"]}
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_save_document_clears_previous_failure(database_url):
    engine = create_async_engine(to_asyncpg_url(database_url))
    try:
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            record = make_record()

            await save_failure(
                session,
                record,
                ParseError("invalid_file", "Initial parsing failed"),
            )
            assert record["path"] in await failed_paths(session)

            await save_document(session, record, make_parsed())

            assert record["path"] not in await failed_paths(session)
            assert document_id(record["sha256"]) in await parsed_ids(session)
    finally:
        await engine.dispose()
