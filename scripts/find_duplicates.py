import json
from collections import defaultdict
from pathlib import Path

groups = defaultdict(list)

for line in Path("data/manifest.jsonl").read_text(encoding="utf-8").splitlines():
    row = json.loads(line)
    if row.get("status") == "downloaded" and row.get("sha256"):
        groups[row["sha256"]].append(row)

duplicates = {sha: rows for sha, rows in groups.items() if len({row["url"] for row in rows}) > 1}

for sha, rows in duplicates.items():
    print(f"\nSHA256: {sha}")
    for row in rows:
        print(f"  {row['url']} -> {row['path']}")

print(f"\nDuplicate groups: {len(duplicates)}")

extra_downloads = sum(len({row["url"] for row in rows}) - 1 for rows in duplicates.values())
print(f"Extra downloads under different URLs: {extra_downloads}")
