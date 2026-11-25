"""Compare two parsers on the 10 largest PDF and HTML files.

Writes a comparison table into NOTES.md. Fill in the final
"Better, why" column after inspecting the results.
"""

import json
import re
import sys
import time
from pathlib import Path

from fraudfirstaid.ingest.parse import (
    ParseError,
    finish,
    headings_in,
    parse_file,
    split_pages,
)

MANIFEST = Path("data/manifest.jsonl")
NOTES = Path("NOTES.md")

START = "<!-- parsers:start -->"
END = "<!-- parsers:end -->"


def strip_tags(path: Path):
    """Naive HTML parser: remove tags and retain visible text."""
    html = path.read_text(encoding="utf-8", errors="replace")

    html = re.sub(
        r"(?is)<(script|style)\b.*?</\1\s*>",
        " ",
        html,
    )

    text = re.sub(r"(?s)<[^>]+>", " ", html)

    return finish(
        "strip-tags",
        "html",
        "",
        split_pages(text),
    )


def measure(parser, path: Path) -> dict:
    """Measure parser output, quality indicators, and execution time."""
    started = time.perf_counter()

    try:
        doc = parser(path)
    except ParseError as error:
        return {
            "ok": False,
            "note": error.reason,
            "seconds": time.perf_counter() - started,
        }

    text = "\n".join(page.text for page in doc.pages)

    return {
        "ok": True,
        "pages": len(doc.pages),
        "chars": len(text),
        "headings": len(headings_in(text)[0]),
        "tables": sum(page.tables for page in doc.pages),
        "seconds": time.perf_counter() - started,
    }


def pick_files() -> list[Path]:
    """Choose the 10 largest downloaded PDF and HTML files."""
    if not MANIFEST.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST}")

    records = [
        json.loads(line)
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    files = {
        record["path"]: record.get("bytes", 0)
        for record in records
        if record.get("status") == "downloaded" and record.get("path")
    }

    by_size = sorted(
        (path for path in files if Path(path).is_file()),
        key=lambda path: -files[path],
    )

    rich = [path for path in by_size if Path(path).suffix.lower() in {".pdf", ".html", ".htm"}]

    return [Path(path) for path in (rich or by_size)[:10]]


def cells(result: dict | None) -> str:
    """Format one parser result for the Markdown table."""
    if result is None:
        return "-"

    if not result["ok"]:
        return f"FAILED: {result['note']}"

    return f"{result['chars']:,} chars, {result['headings']} headings, {result['tables']} tables"


def main() -> int:
    """Compare selected files and update the NOTES.md table."""
    sys.stdout.reconfigure(errors="replace")

    try:
        files = [Path(arg) for arg in sys.argv[1:]] or pick_files()
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not select files: {error}")
        return 1

    if not files:
        print("No downloaded files found to compare.")
        return 1

    rows = []

    for path in files:
        if not path.is_file():
            print(f"Skipping missing file: {path}")
            continue

        suffix = path.suffix.lower()

        if suffix == ".pdf":
            first = measure(parse_file, path)
            second = measure(
                lambda p: parse_file(p, pdf_parser="pypdf"),
                path,
            )
            names = "PyMuPDF / pypdf"

        elif suffix in {".html", ".htm"}:
            first = measure(parse_file, path)
            second = measure(strip_tags, path)
            names = "trafilatura / strip tags"

        else:
            first = measure(parse_file, path)
            second = None
            names = "plain (check headings by eye)"

        pages = first.get("pages", "-")

        speed = f"{first['seconds']:.2f} s"
        if second is not None:
            speed += f" / {second['seconds']:.2f} s"

        row = (
            f"| {path.name[:48]} | {names} | {pages} | "
            f"{cells(first)} | {cells(second)} | {speed} | |"
        )

        rows.append(row)
        print(row)

    if not rows:
        print("No files could be compared.")
        return 1

    table = "\n".join(
        [
            START,
            "",
            "| File | Parsers (A / B) | Pages | A found | B found | Time (A / B) | Better, why |",
            "|---|---|---|---|---|---|---|",
            *rows,
            "",
            END,
        ]
    )

    text = NOTES.read_text(encoding="utf-8") if NOTES.exists() else "# Notes\n"

    if START in text and END in text:
        start_index = text.index(START)
        end_index = text.index(END) + len(END)

        text = text[:start_index] + table + text[end_index:]
    else:
        text = text.rstrip() + "\n\n## D07 — Parser comparison\n\n" + table + "\n"

    NOTES.write_text(text, encoding="utf-8")

    print(f"compared {len(rows)} files -> table written to NOTES.md (fill in the last column)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
