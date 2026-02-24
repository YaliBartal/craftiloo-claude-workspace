"""
Fetch raw DataDive API data and save as JSON.
Bypasses MCP server's format_json which collapses nested data.
"""

import json
import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from workspace root
WORKSPACE = Path(__file__).resolve().parents[4]
load_dotenv(WORKSPACE / ".env")

API_KEY = os.getenv("DATADIVE_API_KEY")
if not API_KEY:
    raise RuntimeError("DATADIVE_API_KEY not found in .env")

BASE_URL = "https://api.datadive.tools/v1"
NICHE_ID = "b4Nisjv3xy"

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

SNAPSHOT_DIR = WORKSPACE / "outputs" / "research" / "listing-optimizer" / "snapshots"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

DATE = "2026-02-23"

REQUESTS = [
    {
        "name": "Ranking Juices",
        "url": f"{BASE_URL}/niches/{NICHE_ID}/ranking-juices?pageSize=50",
        "file": f"datadive-ranking-juices-{DATE}.json",
    },
    {
        "name": "Master Keyword List",
        "url": f"{BASE_URL}/niches/{NICHE_ID}/keywords?pageSize=200",
        "file": f"datadive-mkl-{DATE}.json",
    },
    {
        "name": "Keyword Roots",
        "url": f"{BASE_URL}/niches/{NICHE_ID}/roots?pageSize=100",
        "file": f"datadive-roots-{DATE}.json",
    },
    {
        "name": "Rank Radars",
        "url": f"{BASE_URL}/niches/rank-radars?pageSize=50",
        "file": f"datadive-rank-radars-{DATE}.json",
    },
]


def main():
    saved_files = []

    for i, req in enumerate(REQUESTS):
        print(f"[{i+1}/{len(REQUESTS)}] Fetching {req['name']}...")
        resp = requests.get(req["url"], headers=HEADERS, timeout=30)
        resp.raise_for_status()

        data = resp.json()
        out_path = SNAPSHOT_DIR / req["file"]
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        size_kb = out_path.stat().st_size / 1024
        print(f"    Saved: {out_path.name} ({size_kb:.1f} KB)")
        saved_files.append(str(out_path))

        # Rate limit: 1 second between requests
        if i < len(REQUESTS) - 1:
            time.sleep(1)

    print(f"\nDone. {len(saved_files)} files saved to {SNAPSHOT_DIR}")
    for f in saved_files:
        print(f"  {f}")


if __name__ == "__main__":
    main()
