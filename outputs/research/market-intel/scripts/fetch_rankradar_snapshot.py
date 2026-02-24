"""
Fetch Rank Radar data for all active DataDive radars.
- Lists all rank radars with summary info
- Fetches last 2 days of ranking data for each radar
- Saves combined JSON snapshot
- Prints movement summary per radar
"""

import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import requests

# --- Configuration ---

WORKSPACE_ROOT = Path(r"C:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE")
ENV_FILE = WORKSPACE_ROOT / ".env"
OUTPUT_DIR = WORKSPACE_ROOT / "outputs" / "research" / "market-intel" / "snapshots"

BASE_URL = "https://api.datadive.tools"
RATE_LIMIT_SECONDS = 1.1

TODAY = date(2026, 2, 23)
YESTERDAY = TODAY - timedelta(days=1)
START_DATE = YESTERDAY.isoformat()  # 2026-02-22
END_DATE = TODAY.isoformat()        # 2026-02-23

OUTPUT_FILE = OUTPUT_DIR / f"datadive-rankradar-{TODAY.isoformat()}.json"


def load_api_key() -> str:
    """Read DATADIVE_API_KEY from .env file."""
    if not ENV_FILE.exists():
        print(f"ERROR: .env file not found at {ENV_FILE}")
        sys.exit(1)

    with open(ENV_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("DATADIVE_API_KEY="):
                key = line.split("=", 1)[1].strip()
                if key:
                    return key

    print("ERROR: DATADIVE_API_KEY not found in .env file")
    sys.exit(1)


def get_headers(api_key: str) -> dict:
    return {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def api_get(api_key: str, path: str, params: dict = None) -> dict:
    """Make a GET request to DataDive API."""
    url = f"{BASE_URL}{path}"
    headers = get_headers(api_key)

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
    except requests.exceptions.RequestException as e:
        print(f"  REQUEST ERROR: {e}")
        return {"error": str(e)}

    if resp.status_code != 200:
        print(f"  HTTP {resp.status_code} for {path}")
        try:
            return {"error": f"HTTP {resp.status_code}", "body": resp.json()}
        except Exception:
            return {"error": f"HTTP {resp.status_code}", "body": resp.text[:500]}

    try:
        return resp.json()
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response", "body": resp.text[:500]}


def extract_items(data, *keys):
    """Extract list from response, trying multiple key names.
    Handles DataDive's nested structure: { data: { data: [...] } }
    """
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # First try explicit keys at top level
        for key in keys:
            if key in data and isinstance(data[key], list):
                return data[key]
        # Handle nested data.data pattern (paginated responses)
        if "data" in data:
            inner = data["data"]
            if isinstance(inner, list):
                return inner
            if isinstance(inner, dict):
                # Try keys inside the nested data object
                for key in keys:
                    if key in inner and isinstance(inner[key], list):
                        return inner[key]
                # Try data.data.data (the actual items list)
                if "data" in inner and isinstance(inner["data"], list):
                    return inner["data"]
    return []


def main():
    api_key = load_api_key()
    print(f"API key loaded: {api_key[:8]}...{api_key[-4:]}")
    print(f"Date range: {START_DATE} to {END_DATE}")
    print()

    # -------------------------------------------------------
    # Step 1: List all rank radars
    # -------------------------------------------------------
    print("=" * 70)
    print("STEP 1: Fetching list of all active Rank Radars")
    print("=" * 70)

    radars_response = api_get(api_key, "/v1/niches/rank-radars", params={"pageSize": 50})

    if "error" in radars_response:
        print(f"ERROR fetching radars: {radars_response}")
        sys.exit(1)

    # Explore the response structure
    print(f"\nResponse type: {type(radars_response).__name__}")
    if isinstance(radars_response, dict):
        print(f"Top-level keys: {list(radars_response.keys())}")

    radars = extract_items(radars_response, "rankRadars", "items", "radars")

    if not radars:
        # Maybe the response itself is the list, or nested differently
        print("\nDEBUG: Could not extract radar list. Full response structure:")
        print(json.dumps(radars_response, indent=2, default=str)[:3000])
        sys.exit(1)

    print(f"\nFound {len(radars)} rank radars:\n")

    # Helper to extract ASIN string from radar (could be nested object or plain string)
    def get_asin(radar):
        asin_field = radar.get("asin", "N/A")
        if isinstance(asin_field, dict):
            return asin_field.get("asin", "N/A")
        return asin_field

    # Print summary table
    print(f"{'#':<4} {'Radar ID':<38} {'ASIN':<14} {'Keywords':<10} {'Top10 KW':<10} {'Top10 SV':<10} {'Top50 KW':<10} {'Top50 SV':<10}")
    print("-" * 106)
    for i, radar in enumerate(radars, 1):
        radar_id = radar.get("rankRadarId", radar.get("id", "N/A"))
        asin = get_asin(radar)
        kw_count = radar.get("keywordCount", radar.get("keywords", "N/A"))
        top10kw = radar.get("top10KW", radar.get("top10Kw", "N/A"))
        top10sv = radar.get("top10SV", radar.get("top10Sv", "N/A"))
        top50kw = radar.get("top50KW", radar.get("top50Kw", "N/A"))
        top50sv = radar.get("top50SV", radar.get("top50Sv", "N/A"))
        print(f"{i:<4} {str(radar_id):<38} {str(asin):<14} {str(kw_count):<10} {str(top10kw):<10} {str(top10sv):<10} {str(top50kw):<10} {str(top50sv):<10}")

    # -------------------------------------------------------
    # Step 2: Fetch detailed data for each radar
    # -------------------------------------------------------
    print()
    print("=" * 70)
    print("STEP 2: Fetching detailed rank data for each radar")
    print(f"        Date range: {START_DATE} to {END_DATE}")
    print("=" * 70)

    combined_results = {
        "fetchDate": TODAY.isoformat(),
        "dateRange": {"start": START_DATE, "end": END_DATE},
        "radarCount": len(radars),
        "radarSummaries": [],
        "radarDetails": [],
    }

    for i, radar in enumerate(radars):
        radar_id = radar.get("rankRadarId", radar.get("id", ""))
        asin = get_asin(radar)

        print(f"\n--- Radar {i + 1}/{len(radars)}: {asin} (ID: {radar_id}) ---")

        # Rate limit
        if i > 0:
            print(f"  Rate limiting: waiting {RATE_LIMIT_SECONDS}s...")
            time.sleep(RATE_LIMIT_SECONDS)

        # Fetch radar data
        params = {"startDate": START_DATE, "endDate": END_DATE}
        detail = api_get(api_key, f"/v1/niches/rank-radars/{radar_id}", params=params)

        if "error" in detail:
            print(f"  ERROR: {detail.get('error')}")
            combined_results["radarDetails"].append({
                "radarId": radar_id,
                "asin": asin,
                "error": detail.get("error"),
            })
            continue

        # Explore response structure for first radar
        if i == 0:
            print(f"  Response type: {type(detail).__name__}")
            if isinstance(detail, dict):
                print(f"  Top-level keys: {list(detail.keys())}")
                for k, v in detail.items():
                    if isinstance(v, list) and len(v) > 0:
                        print(f"  Key '{k}': list with {len(v)} items")
                        if isinstance(v[0], dict):
                            print(f"    First item keys: {list(v[0].keys())}")

        # Extract keywords from the response
        keywords_data = extract_items(detail, "keywords", "items", "data", "ranks")

        if not keywords_data and isinstance(detail, dict):
            # Try to find any list in the response
            for k, v in detail.items():
                if isinstance(v, list) and len(v) > 0:
                    keywords_data = v
                    print(f"  Found keyword data under key: '{k}' ({len(v)} items)")
                    break

        if not keywords_data:
            print(f"  WARNING: No keyword data found. Response keys: {list(detail.keys()) if isinstance(detail, dict) else 'N/A'}")
            combined_results["radarDetails"].append({
                "radarId": radar_id,
                "asin": asin,
                "keywords": [],
                "rawResponse": detail if not isinstance(detail, list) else {"items": detail},
            })
            continue

        # Process keywords and extract rankings
        processed_keywords = []
        top10_count = 0
        top50_count = 0
        significant_movers = []

        for kw_entry in keywords_data:
            keyword = kw_entry.get("keyword", "N/A")
            search_volume = kw_entry.get("searchVolume", kw_entry.get("sv", 0))

            # Extract daily ranks - could be in 'ranks', 'dailyRanks', or inline
            ranks_list = kw_entry.get("ranks", kw_entry.get("dailyRanks", []))

            # Build a clean keyword record
            kw_record = {
                "keyword": keyword,
                "searchVolume": search_volume,
                "ranks": [],
            }

            # If ranks are date-keyed objects
            if isinstance(ranks_list, list):
                for rank_entry in ranks_list:
                    if isinstance(rank_entry, dict):
                        kw_record["ranks"].append({
                            "date": rank_entry.get("date", rank_entry.get("d", "")),
                            "organicRank": rank_entry.get("organicRank", rank_entry.get("organic", rank_entry.get("oRank", None))),
                            "impressionRank": rank_entry.get("impressionRank", rank_entry.get("impression", rank_entry.get("iRank", None))),
                        })
            elif isinstance(ranks_list, dict):
                # Might be keyed by date
                for dt, rank_val in ranks_list.items():
                    if isinstance(rank_val, dict):
                        kw_record["ranks"].append({
                            "date": dt,
                            "organicRank": rank_val.get("organicRank", rank_val.get("organic", None)),
                            "impressionRank": rank_val.get("impressionRank", rank_val.get("impression", None)),
                        })

            # If no nested ranks found, check for flat rank fields
            if not kw_record["ranks"]:
                organic = kw_entry.get("organicRank", kw_entry.get("organic", None))
                impression = kw_entry.get("impressionRank", kw_entry.get("impression", None))
                if organic is not None or impression is not None:
                    kw_record["ranks"].append({
                        "date": END_DATE,
                        "organicRank": organic,
                        "impressionRank": impression,
                    })

            processed_keywords.append(kw_record)

            # Count top 10 and top 50
            current_organic = None
            prev_organic = None

            for rank in kw_record["ranks"]:
                org_rank = rank.get("organicRank")
                if org_rank is not None and isinstance(org_rank, (int, float)):
                    rank_date = str(rank.get("date", ""))
                    if END_DATE in rank_date or rank_date == END_DATE:
                        current_organic = org_rank
                    elif START_DATE in rank_date or rank_date == START_DATE:
                        prev_organic = org_rank

            # If we only have one rank entry, treat it as current
            if current_organic is None and len(kw_record["ranks"]) >= 1:
                last_rank = kw_record["ranks"][-1]
                org = last_rank.get("organicRank")
                if org is not None and isinstance(org, (int, float)):
                    current_organic = org
                if len(kw_record["ranks"]) >= 2:
                    first_rank = kw_record["ranks"][0]
                    org2 = first_rank.get("organicRank")
                    if org2 is not None and isinstance(org2, (int, float)):
                        prev_organic = org2

            if current_organic is not None:
                if current_organic <= 10:
                    top10_count += 1
                if current_organic <= 50:
                    top50_count += 1

            # Check for significant movement (5+ positions)
            if current_organic is not None and prev_organic is not None:
                change = prev_organic - current_organic  # positive = improvement
                if abs(change) >= 5:
                    significant_movers.append({
                        "keyword": keyword,
                        "searchVolume": search_volume,
                        "previousRank": prev_organic,
                        "currentRank": current_organic,
                        "change": change,
                        "direction": "UP" if change > 0 else "DOWN",
                    })

        # Store summary
        radar_summary = {
            "radarId": radar_id,
            "asin": asin,
            "totalKeywords": len(processed_keywords),
            "keywordsInTop10": top10_count,
            "keywordsInTop50": top50_count,
            "significantMovers": len(significant_movers),
            "movers": significant_movers,
        }
        combined_results["radarSummaries"].append(radar_summary)

        # Store full details
        combined_results["radarDetails"].append({
            "radarId": radar_id,
            "asin": asin,
            "radarMeta": radar,
            "keywords": processed_keywords,
        })

        print(f"  Keywords: {len(processed_keywords)} total | Top 10: {top10_count} | Top 50: {top50_count} | Significant movers: {len(significant_movers)}")

    # -------------------------------------------------------
    # Step 3: Save combined JSON
    # -------------------------------------------------------
    print()
    print("=" * 70)
    print("STEP 3: Saving results")
    print("=" * 70)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(combined_results, f, indent=2, default=str)

    file_size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"\nSaved to: {OUTPUT_FILE}")
    print(f"File size: {file_size_kb:.1f} KB")

    # -------------------------------------------------------
    # Step 4: Print summary
    # -------------------------------------------------------
    print()
    print("=" * 70)
    print("SUMMARY: Rank Radar Snapshot")
    print(f"Date: {TODAY.isoformat()}")
    print("=" * 70)

    for summary in combined_results["radarSummaries"]:
        print(f"\n  ASIN: {summary['asin']}")
        print(f"  Radar ID: {summary['radarId']}")
        print(f"  Total keywords tracked: {summary['totalKeywords']}")
        print(f"  Keywords in Top 10: {summary['keywordsInTop10']}")
        print(f"  Keywords in Top 50: {summary['keywordsInTop50']}")
        print(f"  Significant movers (5+ positions): {summary['significantMovers']}")

        if summary["movers"]:
            print(f"  {'Keyword':<45} {'SV':<8} {'Prev':<6} {'Now':<6} {'Change':<8} {'Dir'}")
            print(f"  {'-'*45} {'-'*7} {'-'*5} {'-'*5} {'-'*7} {'-'*5}")
            for m in sorted(summary["movers"], key=lambda x: abs(x["change"]), reverse=True):
                direction_marker = "^" if m["direction"] == "UP" else "v"
                print(f"  {m['keyword']:<45} {m['searchVolume']:<8} {m['previousRank']:<6} {m['currentRank']:<6} {m['change']:+<8} {direction_marker} {m['direction']}")

    print()
    print("Done.")


if __name__ == "__main__":
    main()
