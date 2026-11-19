"""Load and retrieve sample records."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RecordStore:
    """Simple JSON-backed document store."""

    def __init__(self, data_file: Path) -> None:
        self.data_file = data_file
        self.records: list[dict[str, Any]] = []

    def load(self) -> None:
        """Load records from the configured JSON file."""
        if not self.data_file.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_file}")

        with self.data_file.open(encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("Sample records must be a JSON list.")

        if not all(isinstance(record, dict) for record in data):
            raise ValueError("Every sample record must be a JSON object.")

        self.records = data

        logger.info(
            "records loaded",
            extra={"records": len(self.records)},
        )

    def list_records(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return up to the requested number of records."""
        return self.records[:limit]

    def get_record(self, record_id: str) -> dict[str, Any] | None:
        """Find a record by its ID."""
        return next(
            (record for record in self.records if str(record.get("id")) == record_id),
            None,
        )
