"""
DataDive Competitor Data Fetcher
Fetches competitor data for key niches via the DataDive API.
Saves combined JSON snapshot and prints a summary.

Date: 2026-02-23
"""

import json
import os
import sys
import time
import requests
from pathlib import Path


# --- Configuration ---

WORKSPACE_ROOT = Path(r"c:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE")
ENV_FILE = WORKSPACE_ROOT / ".env"
OUTPUT_FILE = WORKSPACE_ROOT / "outputs" / "research" / "market-intel" / "snapshots" / "datadive-competitors-2026-02-23.json"

BASE_URL = "https://api.datadive.tools"
RATE_LIMIT_SECONDS = 1.0

NICHES = [
    {"id": "b4Nisjv3xy", "label": "Cross Stitch Kits for Kids"},
    {"id": "Er21lin0KC", "label": "Beginners Embroidery Kit for Kids"},
    {"id": "gfot2FZUBU", "label": "Embroidery Stitch Practice Kit"},
    {"id": "RmbSD3OH6t", "label": "Sewing Kit for Kids (New)"},
    {"id": "VqBgB5QQ07", "label": "Latch Hook Kit for Kids"},
    {"id": "AY4AlnSj9g", "label": "Mini Perler Beads"},
    {"id": "O6b4XATpTj", "label": "Loom Knitting"},
    {"id": "Aw4EQhG6bP", "label": "Lacing Cards for Kids Ages 3-5"},
]

# Fields to extract per competitor
COMPETITOR_FIELDS = [
    "asin", "bsr", "sales", "salesLowerRange", "salesHigherRange",
    "revenue", "revenueLowerRange", "revenueHigherRange",
    "price", "rating", "reviewCount", "kwRankedOnP1",
    "advertisedKws", "title", "name",
]


# --- Functions ---

def load_api_key(env_path: Path) -> str:
    """Read DATADIVE_API_KEY from .env file."""
    if not env_path.exists():
        print(f"ERROR: .env file not found at {env_path}")
        sys.exit(1)

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("DATADIVE_API_KEY="):
                return line.split("=", 1)[1].strip()

    print("ERROR: DATADIVE_API_KEY not found in .env file")
    sys.exit(1)


def get_headers(api_key: str) -> dict:
    return {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def extract_competitors(response_data) -> list[dict]:
    """
    Extract competitor records from the API response.
    The API may nest data in various structures — try multiple approaches.
    """
    # If it's already a list, check if items are competitor dicts
    if isinstance(response_data, list):
        if len(response_data) > 0 and isinstance(response_data[0], dict):
            # Could be a list of competitor dicts directly
            if "asin" in response_data[0]:
                return response_data
            # Could be a list where first item contains competitors
            if "competitors" in response_data[0]:
                return response_data[0]["competitors"]
        return response_data

    # If it's a dict, try known keys
    if isinstance(response_data, dict):
        # Direct competitors key
        if "competitors" in response_data:
            return response_data["competitors"]
        # Nested under data
        if "data" in response_data:
            data = response_data["data"]
            if isinstance(data, list):
                if len(data) > 0 and isinstance(data[0], dict):
                    if "competitors" in data[0]:
                        return data[0]["competitors"]
                    if "asin" in data[0]:
                        return data
                return data
            if isinstance(data, dict) and "competitors" in data:
                return data["competitors"]
        # Items key
        if "items" in response_data:
            return response_data["items"]

    return []


def extract_competitor_fields(competitor: dict) -> dict:
    """Extract only the fields we care about from a competitor record."""
    result = {}
    for field in COMPETITOR_FIELDS:
        if field in competitor:
            result[field] = competitor[field]

    # Ensure we have a display name — use title or name
    if "title" not in result and "name" in result:
        result["title"] = result.pop("name")
    elif "name" in result and "title" in result:
        # Keep both, but prefer title for display
        pass

    return result


def fetch_niche_competitors(niche_id: str, api_key: str) -> dict:
    """Fetch competitors for a single niche. Returns raw response JSON."""
    url = f"{BASE_URL}/v1/niches/{niche_id}/competitors"
    params = {"pageSize": 50}
    headers = get_headers(api_key)

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  ERROR fetching niche {niche_id}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"  ERROR decoding response for niche {niche_id}: {e}")
        return None


def print_summary(all_results: list[dict]):
    """Print a formatted summary of competitor data by niche."""
    print("\n" + "=" * 100)
    print("DATADIVE COMPETITOR SNAPSHOT - 2026-02-23")
    print("=" * 100)

    for niche_data in all_results:
        label = niche_data["nicheLabel"]
        niche_id = niche_data["nicheId"]
        competitors = niche_data["competitors"]
        count = len(competitors)

        print(f"\n{'-' * 100}")
        print(f"  {label}  (ID: {niche_id})  -  {count} competitors")
        print(f"{'-' * 100}")

        if count == 0:
            print("  No competitor data found.")
            continue

        # Sort by sales descending, handle None values
        sorted_comps = sorted(
            competitors,
            key=lambda c: c.get("sales") or 0,
            reverse=True
        )

        # Top 5 by sales
        top5 = sorted_comps[:5]
        print(f"  {'ASIN':<14} {'BSR':>8} {'Sales/mo':>10} {'Revenue':>12} {'Price':>8} {'Rating':>7} {'Reviews':>8}  Title")
        print(f"  {'-'*14} {'-'*8} {'-'*10} {'-'*12} {'-'*8} {'-'*7} {'-'*8}  {'-'*40}")

        for c in top5:
            asin = c.get("asin", "N/A")
            bsr = c.get("bsr")
            sales = c.get("sales")
            revenue = c.get("revenue")
            price = c.get("price")
            rating = c.get("rating")
            reviews = c.get("reviewCount")
            title = c.get("title") or c.get("name") or "N/A"

            bsr_str = f"{bsr:,}" if bsr else "N/A"
            sales_str = f"{sales:,}" if sales else "N/A"
            revenue_str = f"${revenue:,.0f}" if revenue else "N/A"
            price_str = f"${price:.2f}" if price else "N/A"
            rating_str = f"{rating:.1f}" if rating else "N/A"
            reviews_str = f"{reviews:,}" if reviews else "N/A"
            title_short = title[:50] + "..." if len(str(title)) > 50 else title

            print(f"  {asin:<14} {bsr_str:>8} {sales_str:>10} {revenue_str:>12} {price_str:>8} {rating_str:>7} {reviews_str:>8}  {title_short}")

    print(f"\n{'=' * 100}")
    total_competitors = sum(len(n["competitors"]) for n in all_results)
    print(f"TOTAL: {len(all_results)} niches, {total_competitors} competitors")
    print(f"Output saved to: {OUTPUT_FILE}")
    print("=" * 100)


# --- Main ---

def main():
    print("DataDive Competitor Fetcher")
    print("-" * 40)

    # Load API key
    api_key = load_api_key(ENV_FILE)
    print(f"API key loaded: {api_key[:8]}...{api_key[-4:]}")

    all_results = []

    for i, niche in enumerate(NICHES):
        niche_id = niche["id"]
        label = niche["label"]

        print(f"\n[{i+1}/{len(NICHES)}] Fetching: {label} ({niche_id})...")

        # Rate limit — wait between requests (skip for first)
        if i > 0:
            time.sleep(RATE_LIMIT_SECONDS)

        raw_response = fetch_niche_competitors(niche_id, api_key)

        if raw_response is None:
            all_results.append({
                "nicheId": niche_id,
                "nicheLabel": label,
                "competitors": [],
                "error": "API request failed",
            })
            continue

        # Debug: show response structure for first niche
        if i == 0:
            print(f"  Response type: {type(raw_response).__name__}")
            if isinstance(raw_response, dict):
                print(f"  Top-level keys: {list(raw_response.keys())}")
                for k, v in raw_response.items():
                    if isinstance(v, list):
                        print(f"    '{k}': list with {len(v)} items")
                        if len(v) > 0:
                            print(f"      First item type: {type(v[0]).__name__}")
                            if isinstance(v[0], dict):
                                print(f"      First item keys: {list(v[0].keys())[:15]}...")
                    elif isinstance(v, dict):
                        print(f"    '{k}': dict with keys {list(v.keys())[:10]}")
                    else:
                        print(f"    '{k}': {type(v).__name__} = {str(v)[:80]}")
            elif isinstance(raw_response, list):
                print(f"  List with {len(raw_response)} items")
                if len(raw_response) > 0:
                    first = raw_response[0]
                    print(f"  First item type: {type(first).__name__}")
                    if isinstance(first, dict):
                        print(f"  First item keys: {list(first.keys())[:15]}...")

        # Extract competitor records
        competitors_raw = extract_competitors(raw_response)
        print(f"  Found {len(competitors_raw)} competitors")

        # Extract only the fields we want
        competitors_clean = [extract_competitor_fields(c) for c in competitors_raw]

        all_results.append({
            "nicheId": niche_id,
            "nicheLabel": label,
            "competitorCount": len(competitors_clean),
            "competitors": competitors_clean,
        })

    # Save to JSON
    output = {
        "fetchDate": "2026-02-23",
        "nicheCount": len(all_results),
        "totalCompetitors": sum(len(n["competitors"]) for n in all_results),
        "niches": all_results,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nJSON saved to: {OUTPUT_FILE}")

    # Print summary
    print_summary(all_results)


if __name__ == "__main__":
    main()
