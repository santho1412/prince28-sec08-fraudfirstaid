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
