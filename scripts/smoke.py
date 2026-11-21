"""Smoke-test the live FraudFirstAid API."""

import argparse
import sys

import httpx


def check_health(client: httpx.Client, expected_version: str | None) -> None:
    """Check application liveness and, optionally, its deployed version."""

    response = client.get("/health")
    response.raise_for_status()

    data = response.json()

    if data.get("status") != "ok":
        raise RuntimeError(f"Health check failed: {data}")

    version = data.get("version")

    if not version:
        raise RuntimeError("Health response does not contain a version.")

    if expected_version and version != expected_version:
        raise RuntimeError(f"Version mismatch: expected {expected_version}, got {version}")

    print(f"Health check passed (version: {version})")


def check_readiness(client: httpx.Client) -> None:
    """Check that the application and its database are ready."""

    response = client.get("/ready")
    response.raise_for_status()

    data = response.json()

    if data.get("status") != "ready":
        raise RuntimeError(f"Readiness check failed: {data}")

    if data.get("checks", {}).get("database") is not True:
        raise RuntimeError(f"Database readiness check failed: {data}")

    print("Readiness check passed (database: connected)")


def check_documents(client: httpx.Client) -> None:
    """Check that the document listing endpoint responds correctly."""

    response = client.get("/v1/documents", params={"limit": 1})
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict):
        raise RuntimeError("Documents response must be a JSON object.")

    if not isinstance(data.get("items"), list):
        raise RuntimeError("Documents response does not contain an items list.")

    if not isinstance(data.get("count"), int):
        raise RuntimeError("Documents response does not contain a valid count.")

    if data["count"] != len(data["items"]):
        raise RuntimeError("Documents count does not match the returned items.")

    print("Documents endpoint passed")


def main() -> None:
    """Run all live API smoke tests."""

    parser = argparse.ArgumentParser(description="Smoke-test the live API.")
    parser.add_argument("base_url", help="Base URL of the deployed API")
    parser.add_argument(
        "--expect-version",
        help="Expected Git commit SHA reported by /health",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    try:
        with httpx.Client(base_url=base_url, timeout=20.0) as client:
            check_health(client, args.expect_version)
            check_readiness(client)
            check_documents(client)

    except (httpx.HTTPError, ValueError, RuntimeError) as exc:
        print(f"Smoke test failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print("Smoke test passed")


if __name__ == "__main__":
    main()
