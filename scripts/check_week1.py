"""Week 1 project self-check for FraudFirstAid.

Run:
    uv run python scripts/check_week1.py
    uv run python scripts/check_week1.py https://fraudfirstaid-api.onrender.com
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

passed = 0
failed = 0
warnings = 0


def report(name: str, success: bool, detail: str = "") -> None:
    global passed, failed

    if success:
        passed += 1
        mark = "PASS"
    else:
        failed += 1
        mark = "FAIL"

    suffix = f" — {detail}" if detail else ""
    print(f"[{mark}] {name}{suffix}")


def warn(name: str, detail: str) -> None:
    global warnings
    warnings += 1
    print(f"[WARN] {name} — {detail}")


def exists(relative_path: str) -> bool:
    return (ROOT / relative_path).exists()


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def run_command(
    command: list[str],
    timeout: int = 180,
) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        return result.returncode == 0, output
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)


def find_migrations() -> list[Path]:
    folders = [
        ROOT / "alembic" / "versions",
        ROOT / "migrations" / "versions",
        ROOT / "src" / "fraudfirstaid" / "migrations" / "versions",
    ]

    for folder in folders:
        if folder.is_dir():
            return [path for path in folder.glob("*.py") if path.name != "__init__.py"]

    return []


def count_sample_records() -> int:
    path = ROOT / "data" / "sample_records.json"

    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0

    if isinstance(data, list):
        return len(data)

    if isinstance(data, dict):
        for key in ("records", "data", "items"):
            value = data.get(key)
            if isinstance(value, list):
                return len(value)

    return 0


def get_live_url() -> str | None:
    if len(sys.argv) > 1:
        return sys.argv[1].rstrip("/")

    readme = read_text("README.md")
    urls = re.findall(r"https?://[^\s)>]+", readme)

    for url in urls:
        cleaned = url.rstrip(".,;")
        if "onrender.com" in cleaned:
            return cleaned.rstrip("/")

    return None


print("=" * 65)
print("FraudFirstAid — Week 1 Self-Check")
print("=" * 65)

# D01 — Project foundation

print("\nD01 — Project foundation")

foundation_files = [
    "README.md",
    "docs/QUESTIONS.md",
    "docs/REQUIREMENTS.md",
    ".pre-commit-config.yaml",
    ".env.example",
    "uv.lock",
]

for relative_path in foundation_files:
    report(
        f"Required file: {relative_path}",
        exists(relative_path),
    )

questions = read_text("docs/QUESTIONS.md")

# Supports headings such as:
# ## 1. Emergency response
# followed by the question on the next line.
question_count = len(re.findall(r"(?m)^##\s+\d+\.\s+\S", questions))

report(
    "At least 10 project questions",
    question_count >= 10,
    f"found {question_count}",
)

tracked_env, env_output = run_command(["git", "ls-files", "--error-unmatch", ".env"])

report(
    ".env is not tracked by Git",
    not tracked_env,
    "not tracked" if not tracked_env else env_output,
)

hooks_path_ok, hooks_path = run_command(["git", "config", "--get", "core.hooksPath"])

if hooks_path_ok and hooks_path:
    hook_file = Path(hooks_path.strip()) / "pre-commit"
else:
    hook_file = ROOT / ".git" / "hooks" / "pre-commit"

report(
    "Pre-commit Git hook is installed",
    hook_file.is_file(),
    str(hook_file),
)

if "TODO" in questions.upper():
    warn(
        "Questions document contains TODO text",
        "Review and resolve remaining TODO items.",
    )

# D02 — API and sample data

print("\nD02 — API and sample data")

report(
    "FastAPI main module exists",
    exists("src/fraudfirstaid/api/main.py"),
)

report(
    "Project configuration exists",
    exists("src/fraudfirstaid/config.py"),
)

report(
    "Sample records file exists",
    exists("data/sample_records.json"),
)

record_count = count_sample_records()

report(
    "At least 20 sample records",
    record_count >= 20,
    f"found {record_count}",
)

# D03 — Database and migrations

print("\nD03 — Database and migrations")

migration_files = find_migrations()

report(
    "At least 2 database migrations exist",
    len(migration_files) >= 2,
    f"found {len(migration_files)}",
)

report(
    "Database models exist",
    exists("src/fraudfirstaid/db/models.py"),
)

report(
    "Database loader exists",
    exists("scripts/load_db.py"),
)

notes = read_text("NOTES.md")

# Accept either a dedicated D03 heading or the existing
# database migration evidence and migration history sections.
has_d03_documentation = re.search(r"(?im)^##\s+D03\b", notes) is not None or (
    "Database migration evidence" in notes and "Migration history" in notes
)

report(
    "NOTES.md documents D03 database migration evidence",
    has_d03_documentation,
)

# D04 — Docker, testing and local development

print("\nD04 — Docker and local development")

d04_files = [
    "Dockerfile",
    ".dockerignore",
    "docker-compose.yml",
    "Makefile",
    "tests/unit",
    "tests/integration",
]

for relative_path in d04_files:
    report(
        f"Required file or directory: {relative_path}",
        exists(relative_path),
    )

readme = read_text("README.md")

report(
    "README documents one-command local setup",
    "Run locally in one command" in readme,
)

test_ok, test_output = run_command(
    ["uv", "run", "pytest", "tests/unit", "-q"],
    timeout=180,
)

report(
    "Unit tests pass",
    test_ok,
    "pytest completed successfully" if test_ok else test_output[-500:],
)

# D05 — CI/CD and deployment

print("\nD05 — CI/CD and deployment")

d05_files = [
    ".github/workflows/ci.yml",
    ".github/workflows/cd.yml",
    "scripts/smoke.py",
]

for relative_path in d05_files:
    report(
        f"Required file: {relative_path}",
        exists(relative_path),
    )

report(
    "README contains a CI badge",
    "github.com/" in readme and ("actions/workflows" in readme or "badge" in readme.lower()),
)

report(
    "README contains the live API URL",
    "https://fraudfirstaid-api.onrender.com" in readme,
)

tag_ok, tag_output = run_command(["git", "tag", "--list", "week-1"])

report(
    "week-1 Git tag exists",
    tag_ok and "week-1" in tag_output.splitlines(),
)

report(
    "NOTES.md documents D05",
    "## D05" in notes,
)

# Live deployment

print("\nLive deployment")

live_url = get_live_url()

if not live_url:
    warn(
        "Live API check skipped",
        "Pass the deployed API URL as a command-line argument.",
    )
else:
    try:
        request = urllib.request.Request(
            f"{live_url}/health",
            headers={"User-Agent": "FraudFirstAid-Week1-Check"},
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            status_code = response.status
            body = response.read().decode(
                "utf-8",
                errors="replace",
            )

        try:
            health_data = json.loads(body)
        except json.JSONDecodeError:
            health_data = None

        report(
            "Live /health endpoint returns HTTP 200 JSON",
            status_code == 200 and isinstance(health_data, dict),
            f"HTTP {status_code}",
        )

        if isinstance(health_data, dict):
            live_version = health_data.get("version")

            if live_version:
                main_ok, main_sha = run_command(["git", "rev-parse", "origin/main"])

                if main_ok:
                    expected = main_sha.strip()

                    if live_version != expected:
                        warn(
                            "Live version differs from origin/main",
                            f"live={live_version}, main={expected}",
                        )
                    else:
                        print("[INFO] Live version matches origin/main.")

    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
    ) as exc:
        report(
            "Live /health endpoint returns HTTP 200 JSON",
            False,
            str(exc),
        )

# Summary

print("\n" + "=" * 65)
print("SELF-CHECK SUMMARY")
print("=" * 65)
print(f"Passed:   {passed}")
print(f"Failed:   {failed}")
print(f"Warnings: {warnings}")
print(f"Total:    {passed + failed}")

if failed:
    print("\nResult: NOT COMPLETE — fix the failed checks.")
    sys.exit(1)

if warnings:
    print("\nResult: CHECK WARNINGS before declaring Week 1 complete.")
else:
    print("\nResult: ALL CHECKS PASSED.")

sys.exit(0)
