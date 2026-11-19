"""Tests for JSON-based record storage."""

import json

import pytest

from fraudfirstaid.store import RecordStore

SAMPLE_RECORDS = [
    {"id": "001", "title": "UPI Payment Fraud"},
    {"id": "002", "title": "Phishing Link Fraud"},
    {"id": "003", "title": "Online Shopping Fraud"},
]


def create_store(tmp_path):
    """Create a store backed by a temporary JSON file."""
    data_file = tmp_path / "records.json"
    data_file.write_text(
        json.dumps(SAMPLE_RECORDS),
        encoding="utf-8",
    )

    store = RecordStore(data_file)
    store.load()

    return store


def test_load_records(tmp_path):
    """Records should load successfully from JSON."""
    store = create_store(tmp_path)

    assert len(store.records) == 3


def test_list_all_records(tmp_path):
    """All records should be returned by default."""
    store = create_store(tmp_path)

    assert store.list_records() == SAMPLE_RECORDS


def test_list_records_with_limit(tmp_path):
    """The requested record limit should be respected."""
    store = create_store(tmp_path)

    assert store.list_records(limit=2) == SAMPLE_RECORDS[:2]


def test_get_existing_record(tmp_path):
    """An existing record should be returned by ID."""
    store = create_store(tmp_path)

    assert store.get_record("001") == SAMPLE_RECORDS[0]


def test_get_missing_record(tmp_path):
    """A missing record should return None."""
    store = create_store(tmp_path)

    assert store.get_record("999") is None


def test_list_records_rejects_invalid_limit(tmp_path):
    """A limit below one should raise ValueError."""
    store = create_store(tmp_path)

    with pytest.raises(ValueError):
        store.list_records(limit=0)
