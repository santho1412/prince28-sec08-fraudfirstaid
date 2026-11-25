"""Parse downloaded corpus files into Postgres.

Safe to rerun: already-parsed documents are skipped.
"""

import argparse
import asyncio
import json
import sys
import time
from collections import Counter
from pathlib import Path

from fraudfirstaid.db.session import AsyncSessionLocal, engine
from fraudfirstaid.ingest.parse import (
    ParsedDoc,
    ParseError,
    parse_file,
    parse_pdf_ocr,
)
from fraudfirstaid.ingest.store import (
    document_id,
    failed_paths,
    parsed_ids,
    save_document,
    save_failure,
)

MANIFEST = Path("data/manifest.jsonl")


def load_records() -> list[dict]:
    """Load the newest manifest record per URL for downloaded files on disk."""
    latest: dict[str, dict] = {}

    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        if "url" in record:
            latest[record["url"]] = record

    return [
        record
        for record in latest.values()
        if record.get("status") == "downloaded"
        and record.get("path")
        and record.get("sha256")
        and Path(record["path"]).is_file()
    ]


def parse_one(path: Path, ocr_language: str) -> ParsedDoc:
    """Parse normally, using OCR only for scanned PDFs when requested."""
    try:
        return parse_file(path)
    except ParseError as error:
        if error.reason != "no_text_layer" or not ocr_language:
            raise

        return parse_pdf_ocr(path, ocr_language)


async def run(args: argparse.Namespace) -> int:
    records = load_records()
    counts: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    pages = 0
    started = time.perf_counter()

    async with AsyncSessionLocal() as session:
        already_parsed = await parsed_ids(session)
        previously_failed = await failed_paths(session)

        todo = []

        for record in records:
            identifier = document_id(record["sha256"])

            if identifier in already_parsed:
                counts["already_parsed"] += 1
            elif record["path"] in previously_failed and not args.retry_failed:
                counts["failed_before"] += 1
            else:
                # Avoid parsing duplicate content from different URLs.
                already_parsed.add(identifier)
                todo.append(record)

        selected = todo[: args.limit] if args.limit else todo

        for number, record in enumerate(selected, start=1):
            try:
                parsed = await asyncio.to_thread(
                    parse_one,
                    Path(record["path"]),
                    args.ocr,
                )

                await save_document(session, record, parsed)

                counts["parsed"] += 1
                pages += len(parsed.pages)

            except ParseError as error:
                await session.rollback()
                await save_failure(session, record, error)

                counts["failed"] += 1
                reasons[error.reason] += 1

                print(
                    f"failed  {error.reason:<16} {record['path']}",
                    flush=True,
                )

            if number % 50 == 0:
                print(
                    f"... {number} of {len(selected)} files",
                    flush=True,
                )

    await engine.dispose()

    elapsed = time.perf_counter() - started
    summary = " ".join(f"{name}={count}" for name, count in sorted(counts.items()))

    print(f"files={len(records)} {summary} pages={pages} seconds={elapsed:.1f}")

    if reasons:
        print(
            "failure reasons: "
            + ", ".join(f"{reason}={count}" for reason, count in reasons.most_common())
        )

    return 0


def main() -> int:
    sys.stdout.reconfigure(errors="replace")

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="parse at most N new files",
    )
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="retry files recorded in parse_failures",
    )
    parser.add_argument(
        "--ocr",
        default="",
        metavar="LANG",
        help="OCR scanned PDFs, e.g. eng",
    )

    args = parser.parse_args()

    if args.limit < 0:
        parser.error("--limit must be zero or greater")

    if not MANIFEST.exists():
        print("data/manifest.jsonl not found: collect your corpus first (Day 6)")
        return 1

    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
