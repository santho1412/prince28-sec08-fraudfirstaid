# FraudFirstAid — Project Notes

# Day 6 Notes

## 1. Database migration evidence

### Downgrade

```text
Running downgrade f2598cbeaee3 -> afe23be4c384, add metadata gin index
```

### Current revision after downgrade

```text
afe23be4c384
```

### Upgrade

```text
Running upgrade afe23be4c384 -> f2598cbeaee3, add metadata gin index
```

### Current revision after upgrade

```text
f2598cbeaee3 (head)
```

### Migration history

```text
afe23be4c384 -> f2598cbeaee3 (head), add metadata gin index
<base> -> afe23be4c384, create documents and pages
```

## 2. Loader idempotency evidence

The loader was run multiple times using `data/sample_records.json`.

### Run 1

```text
records=20 inserted=0 updated=0 unchanged=20
```

### Run 2

```text
records=20 inserted=0 updated=0 unchanged=20
```

### Run 3 — after temporarily changing document 001

```text
records=20 inserted=0 updated=1 unchanged=19
```

### Restoration run

```text
records=20 inserted=0 updated=1 unchanged=19
```

### Final verification

```text
records=20 inserted=0 updated=0 unchanged=20
```

The loader is idempotent: unchanged records are skipped. When a record changes, the loader updates it instead of inserting a duplicate. The original JSON data was restored after the test.

## 3. EXPLAIN ANALYZE evidence

Command:

```powershell
uv run python scripts/explain.py issuer "Reserve Bank of India"
```

### Actual output

```text
-- 1) What the planner chooses on its own:
Seq Scan on documents  (cost=0.00..11.00 rows=1 width=36) (actual time=0.869..1.374 rows=13.00 loops=1)
  Filter: (metadata @> '{"issuer": "Reserve Bank of India"}'::jsonb)
  Rows Removed by Filter: 7
  Buffers: shared read=2 dirtied=2
Planning:
  Buffers: shared hit=143 read=8 dirtied=1
Planning Time: 5.336 ms
Execution Time: 1.406 ms

-- 2) Seq scan switched off, to prove the index can be used:
Bitmap Heap Scan on documents  (cost=17.23..21.25 rows=1 width=36) (actual time=1.653..1.660 rows=13.00 loops=1)
  Recheck Cond: (metadata @> '{"issuer": "Reserve Bank of India"}'::jsonb)
  Heap Blocks: exact=2
  Buffers: shared hit=4 read=2
  ->  Bitmap Index Scan on ix_documents_metadata_gin  (cost=0.00..17.23 rows=1 width=0) (actual time=1.618..1.619 rows=15.00 loops=1)
        Index Cond: (metadata @> '{"issuer": "Reserve Bank of India"}'::jsonb)
        Index Searches: 1
        Buffers: shared hit=2 read=2
Planning:
  Buffers: shared hit=1
Planning Time: 0.086 ms
Execution Time: 1.702 ms
```

### Why does PostgreSQL choose a Seq Scan?

The table currently contains only 20 documents. Reading the entire table is cheaper than using an index for this small dataset.

### When is the GIN index chosen?

As the table grows and the metadata filter becomes selective enough, PostgreSQL may choose the GIN index because it can reduce the number of rows that need to be read.

Disabling sequential scans demonstrates that the GIN index `ix_documents_metadata_gin` is available and can be used.

---

# Day 4 — Dockerization

## 4. Multi-stage Docker image

Created a root-level `Dockerfile` using:

- Python 3.12 slim as the base image.
- uv for dependency installation.
- A separate builder stage and runtime stage.
- A non-root `app` user.
- Uvicorn as the application server.
- Port 8000 exposed for the API.

The runtime image copies the Alembic migration directory from `alembic/`, along with the application runtime dependencies, scripts, and data.

## 5. Docker build evidence

Built the application image:

```powershell
docker build -t fraudfirstaid:dev .
```

Image:

```text
fraudfirstaid:dev
```

Reported Docker image size:

```text
301MB
```

The image is below the 400 MB target.

## 6. Non-root user verification

Command:

```powershell
docker run --rm fraudfirstaid:dev id
```

Expected identity:

```text
uid=999(app) gid=999(app) groups=999(app)
```

The container runs as the non-root `app` user rather than root.

## 7. Docker build cache verification

Temporarily changed the application factory docstring in:

```text
src/fraudfirstaid/api/main.py
```

Rebuilt the image after the source change.

The dependency installation layer was reported as:

```text
CACHED
```

This confirms that changing application source code does not unnecessarily reinstall dependencies.

### Cache verification rebuild time

```text
19.6 seconds
```

### Initial build timing

The successful initial build duration was not captured.

The first recorded build attempt took 30.7 seconds but failed because of an incorrect migration-directory path. This was corrected from `migrations/` to `alembic/`, and the README exclusion was also corrected before the successful build.

## 8. Docker ignore configuration

Created `.dockerignore` to exclude unnecessary files and directories, including:

- Git metadata.
- Python cache files.
- Local virtual environments.
- Environment secrets.
- Test files and coverage output.
- IDE configuration.
- Temporary files.

`README.md` is intentionally included in the Docker build context because the project build backend requires it when building the package.

## 9. Cache-test cleanup

Restored:

```text
src/fraudfirstaid/api/main.py
```

to its original application factory docstring:

```python
"""Create and configure the FastAPI application."""
```

The temporary cache-test modification was removed after verification.

## 10. Docker Compose stack

Created `docker-compose.yml` to run the complete local development stack.

Services:

- `db`: PostgreSQL 17 with pgvector.
- `redis`: Redis 7 Alpine.
- `migrate`: Runs Alembic migrations and loads sample records.
- `api`: Runs the FastAPI application.

### PostgreSQL configuration

- Database: `app`
- User: `app`
- Host port: `5433`
- Container port: `5432`
- Persistent named volume: `pgdata`

A separate test database is initialized through:

```text
docker/initdb/01-create-test-db.sql
```

The SQL initialization creates `test_db` owned by `app`.

### Health checks and startup dependencies

- PostgreSQL uses `pg_isready`.
- Redis uses `redis-cli ping`.
- API waits for PostgreSQL and Redis to become healthy.
- API waits for the migration service to complete successfully.
- Migration service waits for PostgreSQL to become healthy.

### Compose configuration validation

Command:

```powershell
docker compose config --quiet
```

Result: passed with no configuration errors.

## 11. Docker Compose startup evidence

Started the stack with:

```powershell
docker compose up --build -d
```

Initial service results:

```text
db       Healthy
redis    Healthy
migrate  Exited (0)
api      Started
```

### Migration and seed output

```text
Running upgrade -> afe23be4c384, create documents and pages
Running upgrade afe23be4c384 -> f2598cbeaee3, add metadata gin index
records=20 inserted=20 updated=0 unchanged=0
```

The migration service completed successfully, and the initial 20 sample records were inserted.

## 12. API health and readiness verification

### Initial healthy state

Command:

```powershell
curl.exe -s http://localhost:8000/health
curl.exe -s http://localhost:8000/ready
```

Actual output:

```text
{"status":"ok"}
{"status":"ready","checks":{"database":true}}
```

The API was alive and PostgreSQL was reachable.

## 13. Database failure and readiness verification

Stopped PostgreSQL:

```powershell
docker compose stop db
```

### Liveness check while database was stopped

Actual output:

```text
{"status":"ok"}
```

The API remained alive even though PostgreSQL was unavailable.

### Initial readiness failure

The first readiness test returned:

```text
Internal Server Error
```

Inspection of the API logs showed a database connection failure ending in:

```text
socket.gaierror: [Errno -2] Name or service not known
```

The readiness endpoint originally caught `SQLAlchemyError` but did not catch the operating-system connection error.

### Readiness endpoint correction

Updated:

```text
src/fraudfirstaid/api/routes/health.py
```

The readiness endpoint now catches:

```python
except (SQLAlchemyError, OSError):
```

When the database is unavailable, it returns HTTP 503 and a structured `not_ready` response.

### Successful failure test after correction

Actual HTTP response from `/health`:

```text
HTTP/1.1 200 OK

{"status":"ok"}
```

Actual HTTP response from `/ready`:

```text
HTTP/1.1 503 Service Unavailable

{"status":"not_ready","checks":{"database":false}}
```

Ruff formatting and lint checks passed after the correction.

## 14. Database recovery verification

Restarted PostgreSQL:

```powershell
docker compose start db
```

The database returned to `healthy` status. Redis and the API were also healthy.

### Readiness after database recovery

Actual HTTP response:

```text
HTTP/1.1 200 OK

{"status":"ready","checks":{"database":true}}
```

The API recovered its database connectivity without restarting the API container.

## 15. Docker Compose restart and seed idempotency

Stopped and removed the Compose containers without deleting the persistent database volume:

```powershell
docker compose down
```

Started the stack again:

```powershell
docker compose up -d
```

Checked migration logs:

```powershell
docker compose logs migrate
```

### Actual migration and seed output

```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
records=20 inserted=0 updated=0 unchanged=20
```

The existing 20 records were unchanged after the Compose restart. No duplicate records were inserted.

### Final result

- PostgreSQL and Redis health checks passed.
- The migration service completed successfully.
- The API health and readiness endpoints worked.
- The API remained alive during database failure.
- Readiness correctly returned HTTP 503 when PostgreSQL was unavailable.
- Readiness returned HTTP 200 after PostgreSQL recovered.
- The API recovered without a container restart.
- The loader remained idempotent after restarting the Compose stack.

## D04 · Docker, Compose and tests

### Clean-clone verification

- Cloned the repository into a separate directory and built the Compose stack successfully.
- API container: healthy.
- PostgreSQL container: healthy.
- Redis container: healthy.
- Migration container: exited with code 0.
- Removed the temporary clone and restarted the original project successfully.
- Verified the original stack again with `docker compose ps -a`.

### Image and build

- Image size: 301 MB (target: under 400 MB).
- Runtime user: uid 999 (`app`), non-root.
- Dependency installation layer was cached after a source-only change because dependency files had not changed.
- Source-change cache rebuild: 19.6 seconds.
- Clean-clone Compose build: approximately 30.5 seconds.

### Stack and health checks

- PostgreSQL and Redis health checks passed.
- Migration and seed service completed successfully.
- `/health` returned HTTP 200 when the database was stopped.
- `/ready` returned HTTP 503 when the database was stopped.
- `/ready` returned HTTP 200 after the database restarted.
- Re-running the seed loader left all 20 records unchanged.

### Tests and coverage

Unit-only coverage:

```text
16 passed, 7 skipped
TOTAL                                  247     28     40      6    85%
```

# D05 · CI/CD and going live

## 1. Live deployment

- Live URL: https://fraudfirstaid-api.onrender.com
- API documentation: https://fraudfirstaid-api.onrender.com/docs
- Health endpoint: https://fraudfirstaid-api.onrender.com/health
- Readiness endpoint: https://fraudfirstaid-api.onrender.com/ready
- Hosting: Render
- Database: Neon PostgreSQL
- Container registry: GitHub Container Registry (GHCR)

## 2. Continuous integration

- PR #5: CI workflow merged successfully.
- CI checks: lint and test; build image.
- Both required CI checks passed.
- Docker image published to GHCR with commit-specific SHA tags.
- GHCR package made public for Render image deployment.

## 3. Continuous deployment

- PR #6: CD workflow merged successfully.
- PR #7: README live URL and badges merged successfully.
- Automatic deployment after merging to main: successful.
- Deployment migrations: successful.
- Live smoke test: passed.

## 4. Smoke test evidence

```text
ok   /health -> 200
ok   /ready -> 200
ok   /v1/documents?limit=1 -> 200
Smoke test passed
```

## 5. Rollback drill

- Rollback target (PR #5 merge): `bd4c436c62970c4a6a189a2ae5d1e5dbb2aa0c4f`
- Rollback CD workflow: successful.
- Migration step: skipped as expected.
- Rollback smoke test: passed.

## 6. Roll-forward drill

- Latest main commit: `3f76fe7cc649029a2b06fbb6f64a7d315a4eb1f8`
- Roll-forward CD workflow: successful.
- Smoke test: passed.
- Production restored to the latest application version.

## 7. Why was rollback safe for the database?

The rollback changed the application image, not the database schema. No incompatible database migration was introduced between the rollback target and the latest deployment. Therefore, the older application version could continue using the existing database schema.

## 8. Where my secrets live

- Neon database connection string: GitHub Secret `DATABASE_URL` and Render environment variables.
- Render deploy hook: GitHub Secret `RENDER_DEPLOY_HOOK`.
- Live URL: GitHub Actions variable `LIVE_URL`.
- Secrets are not committed to Git or included in the Docker image.

## 9. Monitoring

- Monitoring service: UptimeRobot.
- Monitor: FraudFirstAid API.
- Endpoint: https://fraudfirstaid-api.onrender.com/health
- Check interval: every 5 minutes.
- Email alerts: configured.
- README includes CI, Live API and Uptime badges.

## 10. Day 5 completion

- CI on pull requests: complete.
- Main branch protection: complete.
- Render production deployment: complete.
- Automatic CD deployment: complete.
- Uptime monitoring: configured.
- README badges and live URL: complete.
- Rollback and roll-forward drills: complete.

## D05 Stretch — Production approval gate

- Configured the GitHub `production` environment with `santho1412` as a required reviewer. Self-review is allowed, and administrator bypass remains enabled.
- A manual approval delay is worthwhile for high-risk production changes because it provides an opportunity to review deployments before release. For routine, low-risk changes, the delay may slow delivery without providing much additional benefit.

## D05 Stretch — Deployment lead-time measurement

Three successful automatic deployments associated with merged pull requests were measured using the exact GitHub pull request merge timestamps and smoke-test completion timestamps.

All timestamps below are in Indian Standard Time (IST, UTC+5:30).

| CD run | Pull request | Merge time (IST) | Smoke test passed (IST) | Change lead time |
|---|---:|---|---|---:|
| CD #1 | PR #6 | 2026-11-21 15:28:22 | 2026-11-21 15:30:38 | 2m 16s |
| CD #8 | PR #9 | 2026-11-21 22:37:19 | 2026-11-21 22:39:50 | 2m 31s |
| CD #7 | PR #8 | 2026-11-21 21:56:28 | 2026-11-21 21:58:29 | 2m 1s |

### Results

- Average DORA change lead time: 136 seconds (2m 16s).
- All three deployments were automatic deployments associated with merged pull requests.
- All three production smoke tests passed.
- Smoke-test durations: 44 seconds for CD #1, 44 seconds for CD #8, and 43 seconds for CD #7.
- Slowest individual smoke-test step: 44 seconds.
- Change lead time was calculated from the exact pull request merge timestamp to the successful smoke-test completion timestamp.

### Calculation

- PR #6 / CD #1: 136 seconds (2m 16s).
- PR #9 / CD #8: 151 seconds (2m 31s).
- PR #8 / CD #7: 121 seconds (2m 1s).

Average = (136 + 151 + 121) / 3 = 136 seconds (2m 16s).

### Human approval gate verification

- Configured the GitHub `production` environment with myself as a required reviewer.
- Manually triggered CD #11 on `main` using commit `0a0a56b`.
- Verified that deployment paused while waiting for production approval.
- Approved the pending deployment through GitHub Actions.
- CD #11 completed successfully in 14m 16s.
- This confirms that the production approval gate works as intended.

# D06 · Collecting the corpus

- Start target: RBI liability circular + Ombudsman scheme + portal FAQs + 50 advisories.
- Collected today: 66 files, 224 pages, 22.7 MB (from DATASET.md).
- Doors used: URL list and by hand (manual registration).

### Licence check

| Source | Licence or terms, in my words | May I show full text in answers? |
|---|---|---|
| RBI | Caching is prohibited; downloading, storage and reproduction permissions need clarification. | No, not until permission is confirmed. |
| CERT-In | Reproduction requires prior permission by email; third-party material needs separate permission. | No, not until permission is confirmed. |
| I4C | Reproduction requires prior MHA permission; source acknowledgement is required. | No, not until permission is confirmed. |

### robots.txt

- RBI: HTTP 418; robots.txt could not be retrieved.
- CERT-In: HTTP 200 returned an HTML error page, not robots.txt rules.
- I4C: TLS/SSL connection failed; robots.txt could not be retrieved.
- No URLs were recorded as blocked by robots.txt in the collection report. However, robots rules could not be reliably verified for these sites, so permission must not be assumed.

### Kill and resume

- Run 1: I pressed Ctrl+C after 2 files.
- Run 2: downloaded=6 skipped=2.
- Run 3: downloaded=0 skipped=8.
- Verified: no `.part` files remained in the test corpus.
- Test used an isolated temporary folder and did not modify the main corpus.

### Capacity (from docs/CAPACITY.md)

- Tokens per page, measured: 525.
- Full corpus: 1.05 M tokens, 3,018 chunks, embedding about Rs 17, vectors 9 MB.
- The number that surprised me most was the estimated 1.05 million tokens for 2,000 pages. This is an approximation based on four characters per token, not an actual tokenizer measurement.

### One thing that went wrong today, and how I fixed it

The I4C FAQ's older URL returned HTTP 403. I used the current FAQ page and saved it manually. I also identified an HTML file incorrectly saved with a PDF extension and documented it as an invalid PDF in DATASET.md.

### Crawl statistics

- Unique URLs in latest manifest: 75.
- Downloaded: 74.
- Failed: 1.
- Total downloaded bytes: 22,701,893 (22.7 MB).

#### By source

- RBI: 8.
- CERT-In: 33.
- I4C: 26.
- Local test: 8.

#### By content type

- HTML: 40.
- PDF: 22.
- Unknown: 4.
- Plain text: 8.

#### Download size by source

- CERT-In: 33 files, 4.25 MiB.
- I4C: 25 files, 16.33 MiB.
- Local test: 8 files, 0.00 MiB.
- RBI: 8 files, 1.07 MiB.

#### Slowest hosts by average request time

- `www.rbi.org.in`: 0.872 seconds average (6 requests).
- `cybercrime.gov.in`: 0.777 seconds average (21 requests).
- `www.cert-in.org.in`: 0.319 seconds average (32 requests).
- `rbidocs.rbi.org.in`: 0.250 seconds average (1 request).

#### Retry statistics

- 1 URL required more than one attempt.

## Day 7 — Task 3: Parsing observations

- HTML parsing with Trafilatura extracts readable advisory content.
- Some HTML pages still contain navigation menus, accessibility links, and footer text.
- Parsed HTML pages currently have empty heading paths (`[]`).
- Two scanned PDFs failed with `no_text_layer`; OCR may be needed.
- These are known parsing-quality issues to investigate in a later improvement pass.

- Recovered the official Digital Arrest Advisory PDF from the I4C learning-corner URL; verified 2 pages and approximately 3,000 extracted characters.
- The older Digital Arrest PDF endpoint and the Fake Stock Market advisory endpoint return invalid content; the latter returns the Cybercrime Portal HTML shell instead of a PDF.
- OCR was attempted on the remaining problematic PDFs but returned empty text; these remain source-quality limitations.

## Day 7 — Task 4: Full corpus parsing and failure handling

- Full corpus parsing completed and rerun; already-parsed documents were skipped.
- Recovered the official I4C Digital Arrest Advisory from the learning-corner PDF URL.
- Verified the recovered advisory in Neon: 2 pages and 2,955 extracted characters.
- Retried failed files; 2 no_text_layer failures remain.
- Known gaps: the old Digital Arrest PDF is damaged, and the old FAQ and Fake Stock Market advisory endpoints return the portal HTML shell instead of the actual content.
- OCR was attempted on the damaged PDF but did not recover text.
- Remaining source-quality failures are documented rather than silently treated as successful parses.

## D07 — Parser comparison

<!-- parsers:start -->

| File | Parsers (A / B) | Pages | A found | B found | Time (A / B) | Better, why |
|---|---|---|---|---|---|---|
| monthly-underground-banking-report-61fa0768.pdf | PyMuPDF / pypdf | 33 | 29,058 chars, 72 headings, 12 tables | 22,912 chars, 0 headings, 0 tables | 11.16 s / 1.15 s | |
| National_Cyber_Crime_Portal_FAQ.pdf | PyMuPDF / pypdf | 3 | 28,609 chars, 0 headings, 2 tables | 2,490 chars, 0 headings, 0 tables | 1.70 s / 0.23 s | |
| faqs-on-cybersecuritydirections-may2022-5be59b6c | PyMuPDF / pypdf | 28 | 43,733 chars, 120 headings, 0 tables | 47,732 chars, 0 headings, 0 tables | 2.23 s / 0.46 s | |
| whatsapp-web-account-60b0fdfb.pdf | PyMuPDF / pypdf | 4 | 3,464 chars, 12 headings, 0 tables | 3,132 chars, 0 headings, 0 tables | 0.43 s / 0.14 s | |
| Advisory_on_digital.pdf | PyMuPDF / pypdf | - | FAILED: no_text_layer | FAILED: no_text_layer | 0.03 s / 0.15 s | |
| advisory-regarding-fake-9971fd8a.pdf | PyMuPDF / pypdf | 1 | 1,671 chars, 11 headings, 0 tables | 1,617 chars, 0 headings, 0 tables | 0.04 s / 0.06 s | |
| cybercriminals-tampering-with-b1b677ca.pdf | PyMuPDF / pypdf | 2 | 3,375 chars, 18 headings, 0 tables | 3,317 chars, 0 headings, 0 tables | 0.23 s / 0.14 s | |
| fraudsters-using-army-personnel-d2f95144.pdf | PyMuPDF / pypdf | 2 | 3,813 chars, 21 headings, 0 tables | 3,731 chars, 0 headings, 0 tables | 0.30 s / 0.17 s | |
| cybercriminals-using-caller-2628ec1b.pdf | PyMuPDF / pypdf | 2 | 3,195 chars, 18 headings, 0 tables | 3,139 chars, 0 headings, 0 tables | 0.22 s / 0.13 s | |
| advisory-on-digital-e557ee2e.pdf | PyMuPDF / pypdf | 2 | 2,956 chars, 7 headings, 0 tables | 2,992 chars, 0 headings, 0 tables | 0.26 s / 0.10 s | |

<!-- parsers:start -->

## D07 — Parser comparison

| File | Parsers (A / B) | Pages | A found | B found | Time (A / B) | Better, why |
|---|---|---:|---|---|---|---|
| monthly-underground-banking-report-61fa0768.pdf | PyMuPDF / pypdf | 33 | 29,058 chars, 72 headings, 12 tables | 22,912 chars, 0 headings, 0 tables | 11.16 s / 1.15 s | PyMuPDF — preserves 72 headings and 12 tables; pypdf finds neither. |
| National_Cyber_Crime_Portal_FAQ.pdf | PyMuPDF / pypdf | 3 | 28,609 chars, 0 headings, 2 tables | 2,490 chars, 0 headings, 0 tables | 1.70 s / 0.23 s | Neither — the source is HTML portal content saved with a PDF extension; extracted content contains duplicated FAQ text and navigation fragments. |
| faqs-on-cybersecuritydirections-may2022-5be59b6c | PyMuPDF / pypdf | 28 | 43,733 chars, 120 headings, 0 tables | 47,732 chars, 0 headings, 0 tables | 2.23 s / 0.46 s | PyMuPDF for structure — identifies 120 headings; pypdf extracts more characters but no headings. |
| whatsapp-web-account-60b0fdfb.pdf | PyMuPDF / pypdf | 4 | 3,464 chars, 12 headings, 0 tables | 3,132 chars, 0 headings, 0 tables | 0.43 s / 0.14 s | PyMuPDF — extracts more characters and identifies 12 headings. |
| Advisory_on_digital.pdf | PyMuPDF / pypdf | - | FAILED: no_text_layer | FAILED: no_text_layer | 0.03 s / 0.15 s | Neither — damaged source; both parsers fail to extract text. |
| advisory-regarding-fake-9971fd8a.pdf | PyMuPDF / pypdf | 1 | 1,671 chars, 11 headings, 0 tables | 1,617 chars, 0 headings, 0 tables | 0.04 s / 0.06 s | PyMuPDF — extracts slightly more text and identifies 11 headings. |
| cybercriminals-tampering-with-b1b677ca.pdf | PyMuPDF / pypdf | 2 | 3,375 chars, 18 headings, 0 tables | 3,317 chars, 0 headings, 0 tables | 0.23 s / 0.14 s | PyMuPDF — extracts slightly more text and identifies 18 headings. |
| fraudsters-using-army-personnel-d2f95144.pdf | PyMuPDF / pypdf | 2 | 3,813 chars, 21 headings, 0 tables | 3,731 chars, 0 headings, 0 tables | 0.30 s / 0.17 s | PyMuPDF — extracts slightly more text and identifies 21 headings. |
| cybercriminals-using-caller-2628ec1b.pdf | PyMuPDF / pypdf | 2 | 3,195 chars, 18 headings, 0 tables | 3,139 chars, 0 headings, 0 tables | 0.22 s / 0.13 s | PyMuPDF — extracts slightly more text and identifies 18 headings. |
| advisory-on-digital-e557ee2e.pdf | PyMuPDF / pypdf | 2 | 2,956 chars, 7 headings, 0 tables | 2,992 chars, 0 headings, 0 tables | 0.26 s / 0.10 s | PyMuPDF for structure — identifies 7 headings; pypdf extracts slightly more characters but no headings. |

<!-- parsers:end -->

### D07 · Parsing my corpus

- Files in the manifest: **76 URLs** · downloaded: **75** · parsed: **70** · failed: **5** · pages in Postgres: **200**
- Parsing coverage: **93.3%** of downloaded files (70 / 75)

### Failures by reason

| Reason | Files | What I did |
|---|---:|---|
| empty | 3 | Investigated the source URLs. They returned portal HTML instead of the expected document content. Documented these source-quality issues. |
| no_text_layer | 2 | Attempted OCR using Tesseract. The problematic PDFs were damaged or contained invalid content; OCR did not recover text. |

- The one I fixed: file `advisorytau-adv-003digitalarrest06-03-2025-60c6a2e6.pdf`, reason `no_text_layer`, fix: identified that the old endpoint returned an HTML portal shell instead of a valid PDF; recovered the official Digital Arrest Advisory from the I4C learning-corner PDF URL and successfully parsed it into 2 pages with 2,955 characters.

### What I saw when I read my parsed pages

- A page where the heading path is right (document, page, path): `MODUS OPERANDI`, page 2, heading path `["arrest"]`.
- Something that came out wrong (document, page, what): `Cybercrime Portal`, page 2, FAQ questions were duplicated across table columns and heading paths were empty.
- A table: `T-397 – Monthly Underground Banking Report`, page 1: extracted as a Markdown grid with table rows and columns.

### My parser choice

- For PDFs I use **PyMuPDF** because:
  - The Monthly Underground Banking Report produced 29,058 characters, 72 headings and 12 tables, compared with pypdf's 22,912 characters, 0 headings and 0 tables.
  - PyMuPDF also identified 7 headings in the recovered Digital Arrest Advisory, while pypdf identified none.
  - PyMuPDF is slower in the report comparison (11.16 seconds versus 1.15 seconds), but its structural extraction is more useful for this project.
- A kind of document in my corpus that neither parser handles well: damaged PDFs and HTML portal pages incorrectly saved or labelled as PDFs.

### One thing that went wrong today, and how I fixed it

- The Ruff formatting check failed because `scripts/compare_parsers.py` was not formatted.
- I fixed it by running `uv run ruff format scripts/compare_parsers.py` and reran the lint checks successfully.

# D08 — Task 5: Break it on purpose

## 1. English vs Tamil token comparison

| Test | Input tokens |
|---|---:|
| Baseline: Hi | 187 |
| English refund question | 195 |
| Tamil refund question | 203 |

- English message tokens: 195 - 187 = 8.
- Tamil message tokens: 203 - 187 = 16.
- Tamil-to-English token ratio: 16 / 8 = 2x.
- The Tamil message required twice as many input tokens as the English message in this test.


## 2. Ask what it can't know

| Test | Observed result |
|---|---|
| RBI customer liability | Hallucination: invented a ₹5,000–₹25,000 cap for customer negligence |
| Scammer account frozen? | Correctly admitted it did not know |
| Unrelated cricket question | Correctly declined as outside product scope |
| First-hour UPI fraud steps | Gemini stream ended early; incomplete answer |
| Evidence to preserve | Plausible answer; checked against project documentation |


## 3. Primary failure, fallback and circuit breaker

- Changed primary model to gemini-no-such-model.
- First four calls successfully used Groq with fallback=YES.
- After waiting 30 seconds, the recovery test still used Groq.
- Restored gemini-3.5-flash-lite and restarted the server.
- Final test returned Gemini with fallback=no.
- Groq fallback responses contained inconsistent RBI reporting deadlines (24, 30 and 48 hours), demonstrating factual reliability problems.


## 4. Read the bill and verify database records

Usage API for 2026-11-25:
- Calls: 21
- Errors: 5
- Fallbacks: 5
- Input tokens: 3,486
- Output tokens: 2,933
- Estimated cost: Rs 0.3781

Neon SQL verification:
- Failed Gemini attempts recorded with status=error.
- Failed calls show zero tokens and zero cost.
- Successful Groq fallback calls recorded with fallback_used=true.
- Restored Gemini call recorded with status=ok.
- Interrupted Gemini stream recorded as an error.


### D08 · LLM gateway
- Primary: gemini-3.5-flash-lite (Gemini) · fallback: openai/gpt-oss-20b (Groq)
- First question on my laptop: first words 3.87 s, total 5.88 s, tokens in 200 / out 137, cost Rs 0.038238
- Live URL: pending measurement

### Tokens: English against Tamil
| Message | tokens in |
|---|---:|
| "Hi" (baseline: mostly my system prompt) | 187 |
| English refund explanation | 195 |
| Same question in Tamil | 203 |
- Message-only comparison: English 8 tokens, Tamil 16 tokens. Tamil needs about 2 times the tokens.

### What the model does without my documents
- Question 6 ("Has the scammer's account been frozen yet?"): it admitted uncertainty: "I am not sure if the scammer's account has been frozen yet."
- A detail it got wrong or invented: RBI liability answer → it claimed OTP/PIN-sharing customer liability was capped at Rs 5,000–Rs 25,000 based on account type → this claim was inaccurate.
- Off-topic question: declined in one sentence: "This question is outside this product's subject, which is guiding victims of online financial fraud through the first hours after an incident."

### Fallback and circuit breaker
- With the primary broken: provider Groq, fallback YES, first words after 4.53 s
- Four fallback calls were tested. Exact question number when Gemini error logs stopped appearing: not recorded.

### The bill
- /v1/usage today: calls 21, errors 5, fallbacks 5, cost Rs 0.3781
- Average per answered question: Rs 0.0236 (16 successful calls)

### One thing that went wrong today, and how I fixed it
- An invalid Gemini model caused an HTTP 404. I restored the correct configured model, then verified that Gemini worked again and Groq fallback worked when the primary was unavailable.

### Live deployment verification
- Live URL: https://fraudfirstaid-api.onrender.com
- First request: first words 6.01 s, total 7.74 s, Groq fallback
- Second (awake) request: first words 2.45 s, total 3.82 s, Groq fallback
- /v1/usage: 25 calls, 7 errors, 7 fallbacks, 4,008 input tokens, 3,608 output tokens, cost Rs 0.401
- Average cost per successful call: Rs 0.0223
- Health endpoint: status ok

## D09 · Prompt versions compared

<!-- prompts:start -->

| Prompt version | Correct | Accuracy | Invalid replies | Avg tokens in |
|---|---|---|---|---|
| classify_v1 | 17/20 | 85% | 0 | 48 |
| classify_v2 | 19/20 | 95% | 0 | 277 |
| classify_v3 | 19/20 | 95% | 0 | 458 |
| classify_v4 | 20/20 | 100% | 0 | 491 |
| classify_v5 | 19/20 | 95% | 0 | 320 |

<!-- prompts:end -->

### Why v4 improved
- v3 scored 19/20. It misclassified testset line 20 because the question combined a general RBI zero-liability rule with a request to determine whether the rule meant the user's own recent loss must be refunded.
- v4 added one explicit rule: questions combining general policy with a request about the user's own fraud case are classified as personal.
- v4 scored 20/20 on the 20-question testset.
- No remaining incorrect classifications or LEAK warnings were reported.

## D09 · Metadata extraction v2 trial

- Five documents with parsed page content processed: 5 successful, 0 failed, 1 repaired.
- Years, issuers, reference numbers and summaries were generally consistent with source text.
- Quality issue: `scam_type` sometimes includes general cybersecurity threats such as DDoS and malware, even when the source is not describing financial scams. Restrict this field to explicitly described fraud or scam types.
- Empty `deadline_days` values were appropriate where no deadline expressed in days was found.
- Trial cost: Rs 0.6316.

### D09 · Prompts and structured output

- My best router prompt: classify_v4 with 20 / 20 (100%).
- What I changed in v4, and what happened to the score: Added an explicit rule that questions combining general RBI policy with a request about the user's own fraud case are classified as personal. Accuracy improved from 19/20 in v3 to 20/20 in v4.
- The question my best version still gets wrong (line, wanted, got), and why I think so: None. classify_v4 correctly classified all 20 test questions.
- A label in my test set that I changed after seeing the results: None recorded.
- Input tokens per question: v1 48, best version 491. The extra accuracy is worth it for a safety-critical fraud-support router, although the token cost is significantly higher.
### My contract (DocMeta)

- Fields I kept from my project card: doc_kind, year, language, summary, topics, issuer, number, date, scam_type and deadline_days. These support document classification, search and fraud-specific filtering.
- Fields I deleted, and why they make no sense per document: No additional project-card fields were retained in the final schema. Document-specific fields are kept only when useful across individual documents.
- The field I tightened, and how: doc_kind uses a fixed Literal list; language is restricted to en, ta, hi or other; summary is limited to 20–300 characters; topics require 1–6 entries; custom value lists are limited to 8 entries, with each string limited to 80 characters. Extra fields are forbidden.

### Extraction run

- Prompt version: extract_v2 · documents: 70 ok, 4 repaired, 0 failed (of 75 parsed)
- Not finished? Why, and how many are left: Finished; 0 remaining.
- Most common failure reason, and what I did about it: No failed documents.
- A record that was valid but wrong (document, field, what it said, what is true): No confirmed example recorded.
- Cost at list price: Rs 6.5334 in total, Rs 0.0933 per document.

### One thing that went wrong today, and how I fixed it

- Manual verification: checked 5 extract_v2 records against their official sources. Summaries and classifications were broadly accurate, but publication dates were missed in 4 of 5 records. Issuer extraction also needs review.
