"""Validate the Fraud First Aid Step 5 dataset."""

import argparse
import json
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "sample_records.json"

REQUIRED_FIELDS = {
    "id",
    "issuer",
    "doc_type",
    "number",
    "date",
    "topic",
    "scam_type",
    "deadline_days",
}


def validate_records(minimum: int = 5) -> None:
    """Validate the structure and quality of sample records."""

    try:
        records = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read valid JSON: {exc}") from exc

    if not isinstance(records, list):
        raise SystemExit("Dataset must be a JSON list.")

    if len(records) < minimum:
        raise SystemExit(f"Expected at least {minimum} records; found {len(records)}.")

    seen_ids = set()

    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise SystemExit(f"Record {index} must be a JSON object.")

        actual_fields = set(record)

        if actual_fields != REQUIRED_FIELDS:
            missing = REQUIRED_FIELDS - actual_fields
            extra = actual_fields - REQUIRED_FIELDS
            raise SystemExit(f"Record {index}: missing={missing}, extra={extra}")

        for field in ("id", "issuer", "doc_type", "topic", "scam_type"):
            if not isinstance(record[field], str) or not record[field].strip():
                raise SystemExit(f"Record {index}: {field} must be non-empty text.")

        if record["id"] in seen_ids:
            raise SystemExit(f"Duplicate ID: {record['id']}")

        seen_ids.add(record["id"])

        if record["number"] is not None and not isinstance(record["number"], str):
            raise SystemExit(f"Record {index}: invalid number.")

        if record["date"] is not None:
            if not isinstance(record["date"], str):
                raise SystemExit(f"Record {index}: invalid date.")

            try:
                parsed_date = date.fromisoformat(record["date"])
            except ValueError as exc:
                raise SystemExit(f"Record {index}: date must use YYYY-MM-DD.") from exc

            if parsed_date.isoformat() != record["date"]:
                raise SystemExit(f"Record {index}: date must use YYYY-MM-DD.")

        deadline = record["deadline_days"]

        if deadline is not None and (type(deadline) is not int or deadline < 0):
            raise SystemExit(f"Record {index}: invalid deadline_days.")

    print("STEP 5 DATA VALIDATION PASSED")
    print(f"Total records: {len(records)}")
    print("All eight fields are present.")
    print("All IDs are unique.")
    print("Dates and deadline values are valid.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--minimum", type=int, default=5)
    args = parser.parse_args()

    validate_records(args.minimum)
