"""Load and provide access to sample records."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RecordStore:
    """Simple JSON-based record storage."""

    def __init__(self, data_file: Path) -> None:
        self.data_file = data_file
        self.records: list[dict[str, Any]] = []

    def load(self) -> None:
        """Load records from the configured JSON file."""

        if not self.data_file.exists():
            raise FileNotFoundError(f"Records file not found: {self.data_file}")

        with self.data_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("Records file must contain a JSON list.")

        self.records = data

        logger.info(
            "records loaded",
            extra={"records": len(self.records)},
        )

    def list_records(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return a limited list of records."""

        if limit < 1:
            raise ValueError("Limit must be greater than zero.")

        return self.records[:limit]

    def get_record(self, record_id: str) -> dict[str, Any] | None:
        """Find one record by its ID."""

        for record in self.records:
            if record.get("id") == record_id:
                return record

        return None
