"""Polite, resumable downloader with conditional ETag refresh support."""

import asyncio
import csv
import hashlib
import json
import random
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit

import httpx
from protego import Protego

CONTACT = "https://github.com/santho1412/prince28-sec08-fraudfirstaid"
ROBOTS_TOKEN = "examate-student-bot"
USER_AGENT = f"{ROBOTS_TOKEN}/0.1 (student project; +{CONTACT})"

RETRYABLE = {408, 425, 429, 500, 502, 503, 504}
MAX_WAIT = 120.0
MAX_BYTES = 200 * 1024 * 1024
ATTEMPT_TIMEOUT = 300.0

KNOWN_EXT = {
    ".pdf",
    ".html",
    ".htm",
    ".json",
    ".txt",
    ".md",
    ".mdx",
    ".rst",
    ".adoc",
    ".csv",
    ".xml",
    ".yaml",
    ".yml",
    ".zip",
    ".docx",
    ".xlsx",
    ".xls",
}

EXT_BY_TYPE = {
    "application/pdf": ".pdf",
    "text/html": ".html",
    "application/xhtml+xml": ".html",
    "application/json": ".json",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/csv": ".csv",
    "application/xml": ".xml",
    "text/xml": ".xml",
    "application/zip": ".zip",
    "application/yaml": ".yaml",
}

Sleep = Callable[[float], Awaitable[None]]


@dataclass(frozen=True)
class Source:
    url: str
    source: str
    licence: str
    title: str = ""


class DownloadError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: int | None = None,
        retry_after: float | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.retry_after = retry_after


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def slug(text: str, limit: int = 60) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:limit] or "file"


def file_stem(url: str) -> str:
    parts = urlsplit(url)
    last = unquote(parts.path.rstrip("/").rsplit("/", 1)[-1]) or parts.netloc
    name = last.rsplit(".", 1)[0] if "." in last else last
    suffix = hashlib.sha256(url.encode()).hexdigest()[:8]
    return f"{slug(name)}-{suffix}"


def _content_extension(
    url: str,
    content_type: str,
    content_prefix: bytes = b"",
) -> str:
    """Choose an extension using file signatures before server metadata or URL."""

    prefix = content_prefix.lstrip(b"\xef\xbb\xbf \t\r\n").lower()

    if prefix.startswith(b"%pdf-"):
        return ".pdf"

    if (
        prefix.startswith(b"<!doctype html")
        or prefix.startswith(b"<html")
        or prefix.startswith(b"<head")
        or prefix.startswith(b"<body")
        or b"<html" in prefix[:512]
    ):
        return ".html"

    media_type = content_type.split(";")[0].strip().lower()
    detected = EXT_BY_TYPE.get(media_type)
    if detected:
        return detected

    suffix = Path(urlsplit(url).path).suffix.lower()
    if suffix in KNOWN_EXT:
        return suffix

    return ".bin"


def pick_ext(
    url: str,
    content_type: str,
    content_prefix: bytes = b"",
) -> str:
    """Return the best extension based on content, response type, and URL."""
    return _content_extension(url, content_type, content_prefix)


def backoff_delay(attempt: int, *, base: float = 1.0, cap: float = 60.0) -> float:
    return random.uniform(0, min(cap, base * 2**attempt))


def retry_after_seconds(value: str | None) -> float | None:
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return float(value)
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)
    return max(0.0, (when - datetime.now(UTC)).total_seconds())


def read_sources(path: Path) -> list[Source]:
    sources: list[Source] = []
    seen: set[str] = set()

    with path.open(encoding="utf-8-sig", newline="") as handle:
        lines = (line for line in handle if line.strip() and not line.lstrip().startswith("#"))
        for number, row in enumerate(csv.DictReader(lines), start=1):
            url = (row.get("url") or "").strip()
            name = (row.get("source") or "").strip()
            licence = (row.get("licence") or "").strip()

            if urlsplit(url).scheme not in {"http", "https"}:
                raise ValueError(f"sources row {number}: not an http(s) URL: {url!r}")
            if not name or not licence:
                raise ValueError(f"sources row {number}: source and licence are required: {url}")
            if url not in seen:
                seen.add(url)
                sources.append(Source(url, name, licence, (row.get("title") or "").strip()))

    return sources


class Manifest:
    """Append-only log: the newest record for a URL wins."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.records: dict[str, dict] = {}

        if path.exists():
            content = path.read_text(encoding="utf-8")
            for line in content.splitlines():
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "url" in record:
                    self.records[record["url"]] = record

            if content and not content.endswith("\n"):
                with path.open("a", encoding="utf-8") as handle:
                    handle.write("\n")

    def done(self, url: str, root: Path) -> bool:
        record = self.records.get(url)
        return bool(
            record
            and record.get("status") == "downloaded"
            and record.get("path")
            and (root / record["path"]).is_file()
        )

    def add(self, record: dict) -> None:
        self.records[record["url"]] = record
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


class Robots:
    """Fetch robots.txt once per site and apply its rules."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client
        self._rules: dict[str, Protego | None] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def _load(self, origin: str) -> Protego | None:
        try:
            response = await self._client.get(origin + "/robots.txt")
        except httpx.HTTPError:
            return None

        if response.status_code == 429 or response.status_code >= 500:
            return None
        if response.status_code >= 400:
            return Protego.parse("")
        return Protego.parse(response.text)

    async def check(self, url: str) -> tuple[bool, float]:
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"

        async with self._locks.setdefault(origin, asyncio.Lock()):
            if origin not in self._rules:
                self._rules[origin] = await self._load(origin)

        rules = self._rules[origin]
        if rules is None:
            return False, 0.0

        return (
            rules.can_fetch(url, ROBOTS_TOKEN),
            float(rules.crawl_delay(ROBOTS_TOKEN) or 0.0),
        )


class HostGate:
    """Leave a gap between requests to the same host."""

    def __init__(self, delay: float, sleep: Sleep) -> None:
        self._delay = delay
        self._sleep = sleep
        self._next_ok: dict[str, float] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def wait(self, host: str, crawl_delay: float = 0.0) -> None:
        async with self._locks.setdefault(host, asyncio.Lock()):
            pause = self._next_ok.get(host, 0.0) - time.monotonic()
            if pause > 0:
                await self._sleep(pause)
            self._next_ok[host] = time.monotonic() + max(self._delay, crawl_delay)


def make_client(max_concurrency: int = 4) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT},
        timeout=httpx.Timeout(30.0, connect=10.0),
        limits=httpx.Limits(max_connections=max_concurrency),
        follow_redirects=True,
    )


async def _download(
    client: httpx.AsyncClient,
    src: Source,
    root: Path,
    raw_dir: Path,
    previous: dict | None = None,
) -> dict:
    """Download a file, or reuse it when the server returns HTTP 304."""

    headers = {}
    if previous and previous.get("etag"):
        headers["If-None-Match"] = previous["etag"]

    async with client.stream("GET", src.url, headers=headers) as response:
        if response.status_code == 304:
            if not previous or not previous.get("path"):
                raise DownloadError("HTTP 304 received without an existing file")

            return {
                "not_modified": True,
                "path": previous["path"],
                "bytes": previous.get("bytes", 0),
                "sha256": previous.get("sha256", ""),
                "content_type": previous.get("content_type", ""),
                "http_status": 304,
                "etag": response.headers.get("ETag") or previous.get("etag"),
            }

        if response.status_code != 200:
            raise DownloadError(
                f"HTTP {response.status_code}",
                code=response.status_code,
                retry_after=retry_after_seconds(response.headers.get("Retry-After")),
            )

        content_type = response.headers.get("Content-Type", "")
        etag = response.headers.get("ETag")

        directory = raw_dir / slug(src.source)
        directory.mkdir(parents=True, exist_ok=True)

        stem = file_stem(src.url)
        part = directory / f"{stem}.part"
        digest = hashlib.sha256()
        size = 0
        prefix = bytearray()

        try:
            with part.open("wb") as handle:
                async for chunk in response.aiter_bytes():
                    if len(prefix) < 1024:
                        prefix.extend(chunk[: 1024 - len(prefix)])

                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise DownloadError(f"larger than {MAX_BYTES // 2**20} MB")

                    digest.update(chunk)
                    handle.write(chunk)

            extension = pick_ext(src.url, content_type, bytes(prefix))
            target = directory / f"{stem}{extension}"
            part.replace(target)

        finally:
            part.unlink(missing_ok=True)

    return {
        "path": target.relative_to(root).as_posix(),
        "bytes": size,
        "sha256": digest.hexdigest(),
        "content_type": content_type.split(";")[0].strip(),
        "http_status": 200,
        "etag": etag,
    }


async def fetch_one(
    client: httpx.AsyncClient,
    src: Source,
    *,
    root: Path,
    raw_dir: Path,
    robots: Robots,
    gate: HostGate,
    slots: asyncio.Semaphore,
    max_attempts: int,
    sleep: Sleep,
    previous: dict | None = None,
) -> dict:
    record = {
        "url": src.url,
        "source": src.source,
        "licence": src.licence,
        "title": src.title,
        "via": "http",
    }

    allowed, crawl_delay = await robots.check(src.url)
    if not allowed:
        return record | {
            "status": "blocked",
            "error": "robots.txt",
            "fetched_at": now_iso(),
        }

    host = urlsplit(src.url).netloc
    error, code, attempt = "", None, 0

    for attempt in range(1, max_attempts + 1):
        wait = backoff_delay(attempt - 1)

        async with slots:
            await gate.wait(host, crawl_delay)
            try:
                async with asyncio.timeout(ATTEMPT_TIMEOUT):
                    started = time.monotonic()
                    fields = await _download(client, src, root, raw_dir, previous)
                    fields["elapsed_seconds"] = max(
                        time.monotonic() - started,
                        1e-9,
                    )

                if fields.pop("not_modified", False):
                    return (
                        record
                        | fields
                        | {
                            "status": "not_modified",
                            "attempts": attempt,
                            "fetched_at": now_iso(),
                        }
                    )

                return (
                    record
                    | fields
                    | {
                        "status": "downloaded",
                        "attempts": attempt,
                        "fetched_at": now_iso(),
                    }
                )

            except DownloadError as exc:
                error, code = str(exc), exc.code
                if code not in RETRYABLE:
                    break
                if exc.retry_after is not None:
                    if exc.retry_after > MAX_WAIT:
                        error = f"{error}: asked to wait {exc.retry_after:.0f} s, run again later"
                        break
                    wait = max(wait, exc.retry_after)

            except (httpx.TransportError, TimeoutError) as exc:
                error, code = type(exc).__name__, None

            except httpx.HTTPError as exc:
                error, code = type(exc).__name__, None
                break

        if attempt < max_attempts:
            await sleep(min(wait, MAX_WAIT))

    return record | {
        "status": "failed",
        "http_status": code,
        "error": error,
        "attempts": attempt,
        "fetched_at": now_iso(),
    }


async def fetch_all(
    sources: list[Source],
    *,
    root: Path = Path("."),
    max_concurrency: int = 4,
    per_host_delay: float = 0.5,
    max_attempts: int = 4,
    client: httpx.AsyncClient | None = None,
    sleep: Sleep = asyncio.sleep,
    on_result: Callable[[dict], None] | None = None,
    refresh: bool = False,
) -> dict[str, int]:
    """Fetch missing files; with refresh=True, conditionally revalidate completed files."""

    raw_dir = root / "data" / "raw"
    manifest = Manifest(root / "data" / "manifest.jsonl")

    todo = [src for src in sources if refresh or not manifest.done(src.url, root)]

    counts = {
        "downloaded": 0,
        "skipped": len(sources) - len(todo),
        "blocked": 0,
        "failed": 0,
    }

    own_client = client is None
    client = client or make_client(max_concurrency)
    robots = Robots(client)
    gate = HostGate(per_host_delay, sleep)
    slots = asyncio.Semaphore(max_concurrency)

    try:
        tasks = [
            asyncio.create_task(
                fetch_one(
                    client,
                    src,
                    root=root,
                    raw_dir=raw_dir,
                    robots=robots,
                    gate=gate,
                    slots=slots,
                    max_attempts=max_attempts,
                    sleep=sleep,
                    previous=manifest.records.get(src.url),
                )
            )
            for src in todo
        ]

        for finished in asyncio.as_completed(tasks):
            result = await finished
            status = result["status"]

            if status == "not_modified":
                counts["skipped"] += 1
                saved_record = result | {"status": "downloaded"}
                manifest.add(saved_record)
            else:
                counts[status] += 1
                before = manifest.records.get(result["url"], {})
                same_problem = (
                    before.get("status"),
                    before.get("error"),
                ) == (
                    result["status"],
                    result.get("error"),
                )

                if result["status"] == "downloaded" or not same_problem:
                    manifest.add(result)

            if on_result:
                on_result(result)

    finally:
        if own_client:
            await client.aclose()

    return counts
