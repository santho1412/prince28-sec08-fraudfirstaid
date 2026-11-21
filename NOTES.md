
# FraudFirstAid — Project Notes

## Day 6 Notes

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

## Day 4 — Dockerization

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
- Runtime user: uid 999 (app), non-root.
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
## D05 · CI/CD and going live

### 1. Live deployment

- Live URL: https://fraudfirstaid-api.onrender.com
- API documentation: https://fraudfirstaid-api.onrender.com/docs
- Health endpoint: https://fraudfirstaid-api.onrender.com/health
- Readiness endpoint: https://fraudfirstaid-api.onrender.com/ready
- Hosting: Render
- Database: Neon PostgreSQL
- Container registry: GitHub Container Registry (GHCR)

### 2. Continuous integration

- PR #5: CI workflow merged successfully.
- CI checks: lint and test; build image.
- Both required CI checks passed.
- Docker image published to GHCR with commit-specific SHA tags.
- GHCR package made public for Render image deployment.

### 3. Continuous deployment

- PR #6: CD workflow merged successfully.
- PR #7: README live URL and badges merged successfully.
- Automatic deployment after merging to main: successful.
- Deployment migrations: successful.
- Live smoke test: passed.

### 4. Smoke test evidence

```text
ok   /health -> 200
ok   /ready -> 200
ok   /v1/documents?limit=1 -> 200
Smoke test passed
```

### 5. Rollback drill

- Rollback target (PR #5 merge): bd4c436c62970c4a6a189a2ae5d1e5dbb2aa0c4f
- Rollback CD workflow: successful.
- Migration step: skipped as expected.
- Rollback smoke test: passed.

### 6. Roll-forward drill

- Latest main commit: 3f76fe7cc649029a2b06fbb6f64a7d315a4eb1f8
- Roll-forward CD workflow: successful.
- Smoke test: passed.
- Production restored to the latest application version.

### 7. Why was rollback safe for the database?

The rollback changed the application image, not the database schema. No incompatible database migration was introduced between the rollback target and the latest deployment. Therefore, the older application version could continue using the existing database schema.

### 8. Where my secrets live

- Neon database connection string: GitHub Secret DATABASE_URL and Render environment variables.
- Render deploy hook: GitHub Secret RENDER_DEPLOY_HOOK.
- Live URL: GitHub Actions variable LIVE_URL.
- Secrets are not committed to Git or included in the Docker image.

### 9. Monitoring

- Monitoring service: UptimeRobot.
- Monitor: FraudFirstAid API.
- Endpoint: https://fraudfirstaid-api.onrender.com/health
- Check interval: every 5 minutes.
- Email alerts: configured.
- README includes CI, Live API and Uptime badges.

### 10. Day 5 completion

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

Three successful CD runs were reviewed:

| CD run | Associated PR | Result | Total duration |
|---|---:|---|---:|
| CD #1 | #6 | Smoke test passed | 1m 6s |
| CD #3 | #7 | Smoke test passed | 59s |
| CD #8 | #9 | Smoke test passed | 1m 4s |

- Average CD workflow duration: approximately 1m 3s.
- Slowest identified step: smoke test, taking 44 seconds in CD #8.
- All three deployments completed successfully.
- The GitHub relative timestamps were rounded (for example, "2 hours ago"), so exact merge-to-smoke-test lead times and their average have not yet been established.
- Exact timestamps are needed to calculate change lead time accurately.
