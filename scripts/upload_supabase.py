"""Upload verified corpus files to private Supabase Storage."""

import argparse
import hashlib
import os
import sys
from pathlib import Path
from urllib.parse import quote

import httpx

from fraudfirstaid.ingest.fetch import Manifest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "manifest.jsonl"
RAW = ROOT / "data" / "raw"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_files() -> list[dict]:
    manifest = Manifest(MANIFEST_PATH)
    records = []
    seen = set()

    for record in manifest.records.values():
        if record.get("status") != "downloaded":
            continue

        path = (ROOT / record["path"]).resolve()

        if not path.is_relative_to(RAW.resolve()):
            raise ValueError(f"File outside data/raw: {record['path']}")

        if not path.is_file():
            print(f"SKIP missing: {record['path']}")
            continue

        if path in seen:
            continue
        seen.add(path)

        if path.stat().st_size != record["bytes"]:
            raise ValueError(f"Size mismatch: {record['path']}")

        if sha256_file(path) != record["sha256"]:
            raise ValueError(f"SHA-256 mismatch: {record['path']}")

        item = record.copy()
        item["_local_path"] = path
        item["_object_key"] = path.relative_to(RAW.resolve()).as_posix()
        records.append(item)

    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    try:
        records = load_files()
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"Verified files: {len(records)}")

    if not args.execute:
        print("\nDRY RUN — no files uploaded.")
        for record in records:
            print(f"{record['bytes']:>10} bytes  {record['_object_key']}")
        return 0

    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_SECRET_KEY")
    bucket = "fraudfirstaid-corpus"

    if not url or not key:
        print("Missing SUPABASE_URL or SUPABASE_SECRET_KEY in .env")
        return 1

    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
    }

    uploaded = 0

    with httpx.Client(timeout=120.0) as client:
        for record in records:
            object_key = quote(record["_object_key"], safe="/")
            endpoint = f"{url}/storage/v1/object/{bucket}/{object_key}"

            content_type = record.get("content_type") or "application/octet-stream"
            upload_headers = headers | {
                "Content-Type": content_type,
                "x-upsert": "true",
            }

            try:
                with record["_local_path"].open("rb") as handle:
                    response = client.post(
                        endpoint,
                        headers=upload_headers,
                        content=handle,
                    )
                response.raise_for_status()
            except (httpx.HTTPError, OSError) as exc:
                print(f"FAILED {record['_object_key']}: {exc}")
                return 1

            uploaded += 1
            print(f"UPLOADED {record['_object_key']}")

    print(f"\nUpload complete: {uploaded} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
