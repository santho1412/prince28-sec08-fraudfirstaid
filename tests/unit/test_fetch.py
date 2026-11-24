"""The downloader, tested without the internet: httpx.MockTransport plays the website."""

import asyncio
import json
from pathlib import Path

import httpx
import pytest

from fraudfirstaid.ingest import fetch
from fraudfirstaid.ingest.fetch import Source, fetch_all

SITE = "https://docs.example.org"


def make_sources(count: int) -> list[Source]:
    licence = "CC BY 4.0"
    return [Source(f"{SITE}/guide/page-{i}.html", "Example Docs", licence) for i in range(count)]


class FakeSite:
    """A tiny website. `plan` lists the status codes a path answers with before it says 200."""

    def __init__(self, robots: str | int = 404, plan: dict[str, list[int]] | None = None) -> None:
        self.robots = robots
        self.plan = plan or {}
        self.error_headers: dict[str, str] = {}
        self.hits: list[str] = []
        self.busy = 0
        self.max_busy = 0
        self.slept: list[float] = []

    async def handler(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/robots.txt":
            if isinstance(self.robots, int):
                return httpx.Response(self.robots)
            return httpx.Response(200, text=self.robots)

        self.hits.append(path)
        self.busy += 1
        self.max_busy = max(self.max_busy, self.busy)
        await asyncio.sleep(0.005)
        self.busy -= 1

        queue = self.plan.get(path)
        status = queue.pop(0) if queue else 200
        if status != 200:
            return httpx.Response(status, headers=self.error_headers)
        return httpx.Response(200, html=f"<h1>{path}</h1>")

    async def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)

    async def run(self, sources: list[Source], root: Path, **options) -> dict[str, int]:
        transport = httpx.MockTransport(self.handler)
        async with httpx.AsyncClient(transport=transport, follow_redirects=True) as client:
            return await fetch_all(
                sources,
                root=root,
                client=client,
                sleep=self.sleep,
                per_host_delay=0,
                **options,
            )


def manifest(root: Path) -> list[dict]:
    lines = (root / "data" / "manifest.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines]


def raw_files(root: Path) -> list[Path]:
    return [p for p in (root / "data" / "raw").rglob("*") if p.is_file()]


async def test_downloads_files_and_records_where_they_came_from(tmp_path):
    counts = await FakeSite().run(make_sources(3), tmp_path)
    assert counts == {"downloaded": 3, "skipped": 0, "blocked": 0, "failed": 0}

    record = manifest(tmp_path)[0]
    assert record["status"] == "downloaded" and record["licence"] == "CC BY 4.0"

    saved = tmp_path / record["path"]
    assert saved.parent == tmp_path / "data" / "raw" / "example-docs"
    assert saved.suffix == ".html" and saved.stat().st_size == record["bytes"]
    assert len(record["sha256"]) == 64


async def test_second_run_downloads_nothing(tmp_path):
    site = FakeSite()
    await site.run(make_sources(5), tmp_path)
    counts = await site.run(make_sources(5), tmp_path)

    assert counts["skipped"] == 5 and counts["downloaded"] == 0
    assert len(site.hits) == 5


async def test_resume_fetches_only_what_is_missing(tmp_path):
    site = FakeSite()
    await site.run(make_sources(3), tmp_path)
    counts = await site.run(make_sources(8), tmp_path)

    assert counts == {"downloaded": 5, "skipped": 3, "blocked": 0, "failed": 0}
    assert len(site.hits) == 8 and len(set(site.hits)) == 8


async def test_deleted_file_is_downloaded_again(tmp_path):
    site = FakeSite()
    await site.run(make_sources(2), tmp_path)
    raw_files(tmp_path)[0].unlink()
    counts = await site.run(make_sources(2), tmp_path)

    assert counts["downloaded"] == 1 and counts["skipped"] == 1


async def test_retries_a_503_and_then_succeeds(tmp_path):
    site = FakeSite(plan={"/guide/page-0.html": [503, 503]})
    counts = await site.run(make_sources(1), tmp_path)

    assert counts["downloaded"] == 1
    assert manifest(tmp_path)[0]["attempts"] == 3
    assert len(site.slept) == 2


async def test_obeys_retry_after_on_429(tmp_path):
    site = FakeSite(plan={"/guide/page-0.html": [429]})
    site.error_headers = {"Retry-After": "7"}
    counts = await site.run(make_sources(1), tmp_path)

    assert counts["downloaded"] == 1
    assert site.slept and site.slept[0] >= 7


async def test_gives_up_after_max_attempts_and_leaves_no_file(tmp_path):
    site = FakeSite(plan={"/guide/page-0.html": [500] * 10})
    counts = await site.run(make_sources(1), tmp_path, max_attempts=3)

    assert counts["failed"] == 1 and len(site.hits) == 3
    record = manifest(tmp_path)[0]
    assert record["status"] == "failed" and record["http_status"] == 500
    assert raw_files(tmp_path) == []


async def test_404_is_not_retried(tmp_path):
    site = FakeSite(plan={"/guide/page-0.html": [404]})
    counts = await site.run(make_sources(1), tmp_path)

    assert counts["failed"] == 1
    assert len(site.hits) == 1 and site.slept == []


async def test_a_failed_file_is_tried_again_on_the_next_run(tmp_path):
    site = FakeSite(plan={"/guide/page-0.html": [404]})
    await site.run(make_sources(1), tmp_path)
    counts = await site.run(make_sources(1), tmp_path)

    assert counts["downloaded"] == 1


async def test_robots_disallow_means_never_requested(tmp_path):
    site = FakeSite(robots="User-agent: *\nDisallow: /guide/\n")
    counts = await site.run(make_sources(3), tmp_path)

    assert counts["blocked"] == 3 and site.hits == []


async def test_robots_longest_match_wins(tmp_path):
    site = FakeSite(robots="User-agent: *\nDisallow: /guide/\nAllow: /guide/page-1\n")
    counts = await site.run(make_sources(3), tmp_path)

    assert counts["blocked"] == 2
    assert site.hits == ["/guide/page-1.html"]


async def test_robots_server_error_blocks_the_whole_site(tmp_path):
    counts = await FakeSite(robots=503).run(make_sources(2), tmp_path)

    assert counts["blocked"] == 2


async def test_never_more_than_max_concurrency_at_once(tmp_path):
    site = FakeSite()
    await site.run(make_sources(20), tmp_path, max_concurrency=4)

    assert 1 < site.max_busy <= 4


async def test_broken_connection_leaves_no_half_file(tmp_path):
    async def body():
        yield b"<h1>first half"
        raise httpx.ReadError("connection lost")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(
            200,
            content=body(),
            headers={"Content-Type": "text/html"},
        )

    async def no_sleep(seconds: float) -> None:
        return None

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        counts = await fetch_all(
            make_sources(1),
            root=tmp_path,
            client=client,
            sleep=no_sleep,
            max_attempts=2,
        )

    assert counts["failed"] == 1
    assert manifest(tmp_path)[0]["error"] == "ReadError"
    assert raw_files(tmp_path) == []


async def test_interrupted_download_cleans_partial_file_and_resumes(tmp_path):
    started = asyncio.Event()

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404)

        async def slow_body():
            yield b"<h1>incomplete"
            started.set()
            await asyncio.Event().wait()

        return httpx.Response(
            200,
            content=slow_body(),
            headers={"Content-Type": "text/html"},
        )

    sources = make_sources(2)
    site = FakeSite()

    first_counts = await site.run(sources[:1], tmp_path)
    assert first_counts["downloaded"] == 1

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        run = asyncio.create_task(
            fetch_all(
                sources[1:],
                root=tmp_path,
                client=client,
                per_host_delay=0,
                max_concurrency=1,
            )
        )

        await asyncio.wait_for(started.wait(), timeout=3)

        pending = [
            task
            for task in asyncio.all_tasks()
            if task is not asyncio.current_task() and task is not run and not task.done()
        ]
        for task in pending:
            task.cancel()

        await asyncio.gather(*pending, return_exceptions=True)
        run.cancel()

        with pytest.raises(asyncio.CancelledError):
            await run

    records = manifest(tmp_path)
    assert len(records) == 1
    assert records[0]["status"] == "downloaded"
    assert len(raw_files(tmp_path)) == 1
    assert not list((tmp_path / "data" / "raw").rglob("*.part"))

    counts = await site.run(sources, tmp_path)

    assert counts == {"downloaded": 1, "skipped": 1, "blocked": 0, "failed": 0}
    assert len(manifest(tmp_path)) == 2
    assert not list((tmp_path / "data" / "raw").rglob("*.part"))


async def test_etag_refresh_uses_if_none_match_and_handles_304(tmp_path):
    requests: list[httpx.Request] = []
    etag = '"v1"'
    body = b"<h1>original content</h1>"

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404)

        requests.append(request)

        if request.headers.get("If-None-Match") == etag:
            return httpx.Response(304, headers={"ETag": etag})

        return httpx.Response(
            200,
            content=body,
            headers={
                "Content-Type": "text/html",
                "ETag": etag,
            },
        )

    async def no_sleep(seconds: float) -> None:
        return None

    source = make_sources(1)[0]

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        follow_redirects=True,
    ) as client:
        first_counts = await fetch_all(
            [source],
            root=tmp_path,
            client=client,
            sleep=no_sleep,
            per_host_delay=0,
        )

        first_record = manifest(tmp_path)[-1]
        saved_path = tmp_path / first_record["path"]
        original_hash = first_record["sha256"]

        second_counts = await fetch_all(
            [source],
            root=tmp_path,
            client=client,
            sleep=no_sleep,
            per_host_delay=0,
            refresh=True,
        )

    assert first_counts["downloaded"] == 1
    assert first_record["etag"] == etag
    assert requests[0].headers.get("If-None-Match") is None

    assert second_counts == {
        "downloaded": 0,
        "skipped": 1,
        "blocked": 0,
        "failed": 0,
    }
    assert requests[1].headers.get("If-None-Match") == etag

    latest_record = manifest(tmp_path)[-1]
    assert latest_record["status"] == "downloaded"
    assert latest_record["etag"] == etag
    assert latest_record["sha256"] == original_hash
    assert latest_record["path"] == first_record["path"]
    assert saved_path.read_bytes() == body
    assert len(raw_files(tmp_path)) == 1


def test_backoff_grows_but_stays_inside_its_limits():
    for attempt in range(12):
        ceiling = min(60.0, 2.0**attempt)
        assert all(0 <= fetch.backoff_delay(attempt) <= ceiling for _ in range(50))


def test_retry_after_understands_seconds_and_dates():
    assert fetch.retry_after_seconds("120") == 120.0
    assert fetch.retry_after_seconds("Wed, 21 Oct 2015 07:28:00 GMT") == 0.0
    assert fetch.retry_after_seconds("soon") is None
    assert fetch.retry_after_seconds(None) is None


def test_file_names_are_stable_and_safe():
    url = "https://example.org/files/Annual Report (2024): Final?.PDF"
    stem = fetch.file_stem(url)

    assert stem == fetch.file_stem(url)
    assert stem != fetch.file_stem(url + "x")
    assert all(ch.isalnum() or ch == "-" for ch in stem)
    assert fetch.pick_ext("https://example.org/a/b.PDF", "text/html") == ".pdf"
    assert fetch.pick_ext("https://example.org/view.aspx?id=7", "application/pdf") == ".pdf"
    assert fetch.pick_ext("https://example.org/thing", "weird/type") == ".bin"


def test_read_sources_skips_notes_and_duplicates(tmp_path):
    path = tmp_path / "sources.csv"
    path.write_text(
        "# my notes\n"
        "url,source,licence,title\n"
        "https://example.org/a.pdf,example,CC BY 4.0,Report A\n"
        "\n"
        "https://example.org/a.pdf,example,CC BY 4.0,Report A again\n"
        'https://example.org/b.pdf,example,"Public, cite the page",\n',
        encoding="utf-8",
    )

    sources = fetch.read_sources(path)

    assert [s.url for s in sources] == [
        "https://example.org/a.pdf",
        "https://example.org/b.pdf",
    ]
    assert sources[1].licence == "Public, cite the page"


def test_a_source_without_a_licence_is_refused(tmp_path):
    path = tmp_path / "sources.csv"
    path.write_text("url,source,licence,title\nhttps://example.org/a.pdf,example,,\n")

    with pytest.raises(ValueError, match="licence"):
        fetch.read_sources(path)
