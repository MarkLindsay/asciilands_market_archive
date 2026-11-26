#!/usr/bin/env python3
"""Asciilands market archiver.

Fetches the public market API for each realm and saves the raw JSON response:

    data/v1/na/market/2026-11-26_175642.json
    data/v1/eu/market/2026-11-26_175642.json

Usage:
    python archive.py            # normal run
    python archive.py --dry-run  # print what would be saved, don't write files
"""

import argparse
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

API = {
    "eu": "https://api.asciilands.io/v1/public/market",
    "na": "https://api-na.asciilands.io/v1/public/market",
}

OUT_DIR = Path("data")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "asciilands-market-archive/1.0 (GitHub Actions)"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def save(realm: str, body: bytes, dry_run: bool) -> Path:
    now = datetime.now(UTC)
    stamp = now.strftime("%Y-%m-%d_%H%M%S")
    
    path = OUT_DIR / "v1" / realm / "market" / f"{stamp}.json"

    if dry_run:
        print(f"[dry-run] would write {path} ({len(body)} bytes)")
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    print(f"saved {path} ({len(body)} bytes)")
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    errors = 0
    for realm, url in API.items():
        try:
            body = fetch(url)
            save(realm, body, args.dry_run)
        except Exception as e:
            print(f"[{realm}] fetch failed: {e}", file=sys.stderr)
            errors += 1

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
