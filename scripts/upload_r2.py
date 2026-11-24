"""Upload verified corpus files to a private Cloudflare R2 bucket."""

import argparse
import hashlib
import os
import sys
from pathlib import Path

import boto3

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

        relative = Path(record["path"])
        path = (ROOT / relative).resolve()

        if not path.is_relative_to(RAW.resolve()):
            raise ValueError(f"File is outside data/raw: {record['path']}")

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

        record = record.copy()
        record["_local_path"] = path
        record["_object_key"] = "raw/" + path.relative_to(RAW.resolve()).as_posix()
        records.append(record)

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
        print("\nRun with --execute when your private R2 bucket is ready.")
        return 0

    account_id = os.getenv("CLOUDFLARE_R2_ACCOUNT_ID")
    access_key = os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID")
    secret_key = os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY")
    bucket = os.getenv("CLOUDFLARE_R2_BUCKET_NAME")

    missing = [
        name
        for name, value in {
            "CLOUDFLARE_R2_ACCOUNT_ID": account_id,
            "CLOUDFLARE_R2_ACCESS_KEY_ID": access_key,
            "CLOUDFLARE_R2_SECRET_ACCESS_KEY": secret_key,
            "CLOUDFLARE_R2_BUCKET_NAME": bucket,
        }.items()
        if not value
    ]

    if missing:
        print("Missing environment variables: " + ", ".join(missing))
        return 1

    client = boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )

    for record in records:
        extra_args = {"Metadata": {"sha256": record["sha256"]}}
        if record.get("content_type"):
            extra_args["ContentType"] = record["content_type"]

        try:
            client.upload_file(
                str(record["_local_path"]),
                bucket,
                record["_object_key"],
                ExtraArgs=extra_args,
            )
        except Exception as exc:
            print(f"FAILED {record['_object_key']}: {type(exc).__name__}: {exc}")
            return 1

        print(f"UPLOADED {record['_object_key']}")

    print(f"\nUpload complete: {len(records)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
