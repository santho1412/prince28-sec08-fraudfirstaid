# FraudFirstAid — Day 6 Notes

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

## 4. Loader pruning evidence

The loader now detects database documents that no longer exist in `data/sample_records.json`.

### Safe mode — original dataset

Command:

```powershell
uv run python scripts/load_db.py
```

Output:

```text
records=20 inserted=0 updated=0 unchanged=20 missing=0 deleted=0
```

### Missing document detection

A temporary test document (`__prune_test__`) was inserted directly into PostgreSQL.

Running the loader without `--prune`:

```text
records=20 inserted=0 updated=0 unchanged=20 missing=1 deleted=0
```

The missing document was detected but not deleted.

### Prune mode

Command:

```powershell
uv run python scripts/load_db.py --prune
```

Output:

```text
records=20 inserted=0 updated=0 unchanged=20 missing=1 deleted=1
```

The temporary test document was deleted successfully.

### Final verification

Running the loader again without `--prune`:

```text
records=20 inserted=0 updated=0 unchanged=20 missing=0 deleted=0
```

The temporary record was removed, and all 20 original JSON documents remain in the database.

**Conclusion:** Deletion is disabled by default. Documents missing from the JSON file are deleted only when the loader is explicitly run with `--prune`.
