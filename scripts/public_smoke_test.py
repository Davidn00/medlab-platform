from __future__ import annotations

import sys
import time
import urllib.error
import urllib.request

ENDPOINTS = [
    "/",
    "/health",
    "/health/live",
    "/health/db",
    "/health/redis",
    "/health/ready",
    "/openapi.json",
]


def request(
    base_url: str,
    path: str,
) -> tuple[int, str]:
    url = f"{base_url.rstrip('/')}{path}"

    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": "MedLab-Public-Smoke-Test/1.0",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=20,
    ) as response:
        body = response.read().decode(
            "utf-8",
            errors="replace",
        )

        return response.status, body


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: python scripts/public_smoke_test.py "
            "https://your-service.onrender.com"
        )
        return 2

    base_url = sys.argv[1].rstrip("/")

    print("=" * 60)
    print("MedLab Platform — Public Smoke Test")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print()

    max_attempts = 12

    for attempt in range(1, max_attempts + 1):
        try:
            status, _ = request(
                base_url,
                "/health/live",
            )

            if status == 200:
                print(f"[OK] /health/live -> {status}")
                break

            print(f"[WAIT] /health/live -> {status}")

        except Exception as exc:
            print(f"[WAIT] attempt {attempt}/{max_attempts}: {exc}")

        if attempt < max_attempts:
            time.sleep(10)

    else:
        print()
        print("Public service did not become ready.")
        return 1

    print()
    print("Running endpoint checks...")
    print()

    failures = 0

    for endpoint in ENDPOINTS:
        try:
            status, body = request(
                base_url,
                endpoint,
            )

            if 200 <= status < 300:
                print(f"[OK]   {endpoint:<20} HTTP {status}")

            else:
                print(f"[FAIL] {endpoint:<20} HTTP {status}")
                failures += 1

        except urllib.error.HTTPError as exc:
            print(f"[FAIL] {endpoint:<20} HTTP {exc.code}")
            failures += 1

        except Exception as exc:
            print(f"[FAIL] {endpoint:<20} {exc}")
            failures += 1

    print()
    print("=" * 60)

    if failures:
        print(f"Public smoke test FAILED: {failures} endpoint(s)")
        return 1

    print("Public smoke test PASSED.")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
