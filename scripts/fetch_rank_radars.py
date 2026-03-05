"""
Fetch DataDive Rank Radar data for 9 hero ASINs.
Outputs compact JSON summary for daily market intel report.
Run with: python scripts/fetch_rank_radars.py
"""

import os
import sys
import asyncio
import json
import time
from pathlib import Path

import httpx

# ── Load .env ────────────────────────────────────────────────────────────────
for d in [Path(__file__).resolve().parent.parent]:
    env_file = d / ".env"
    if env_file.exists():
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

API_KEY = os.environ.get("DATADIVE_API_KEY", "")
if not API_KEY:
    print("ERROR: DATADIVE_API_KEY not set", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://api.datadive.tools"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# ── Hero ASINs to match ───────────────────────────────────────────────────────
HERO_ASINS = {
    "B09X55KL2C": "Embroidery Kids",
    "B0DC69M3YD": "Embroidery Adults",
    "B09WQSBZY7": "Fairy Sewing Kit",
    "B096MYBLS1": "Dessert Sewing Kit",
    "B08FYH13CL": "Latch Hook Pencil Cases",
    "B0F8DG32H5": "Knitting Cat & Hat",
    "B09THLVFZK": "Mini Fuse Beads",
    "B07D6D95NG": "10mm Big Fuse Beads",
    "B0FQC7YFX6": "Princess Lacing Card",
}

SKIP_ASINS = {
    "B092SW839H", "B0F8QZZQQM", "B09HVDNFMR",
    "B0B1927HCG", "B0FHMRQWRX", "B0DKD2S3JT"
}

START_DATE = "2026-03-01"
END_DATE   = "2026-03-02"
TODAY      = "2026-03-02"
YESTERDAY  = "2026-03-01"

RATE_LIMIT = 1.1  # seconds between calls


async def api_get(client: httpx.AsyncClient, path: str, params: dict = None):
    url = f"{BASE_URL}{path}"
    resp = await client.get(url, headers=HEADERS, params=params or {})
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}: {resp.text[:300]}"}
    return resp.json()


async def main():
    notes = []
    products = {}

    async with httpx.AsyncClient(timeout=30.0) as client:
        # ── Step 1: list rank radars ──────────────────────────────────────────
        print("Fetching rank radar list...", flush=True)
        raw = await api_get(client, "/v1/niches/rank-radars", {"pageSize": 50})
        await asyncio.sleep(RATE_LIMIT)

        if "error" in raw:
            print(f"ERROR listing radars: {raw['error']}", file=sys.stderr)
            sys.exit(1)

        # Extract list — API wraps response as: {data: {data: [...], ...}}
        def extract_radar_list(obj):
            """Recursively unwrap nested dicts to find the list of radar objects."""
            if isinstance(obj, list):
                return obj
            if isinstance(obj, dict):
                # Check for direct list keys
                for key in ("rankRadars", "items"):
                    if key in obj and isinstance(obj[key], list):
                        return obj[key]
                # 'data' can be either the pagination wrapper or the final list
                if "data" in obj:
                    return extract_radar_list(obj["data"])
            return []

        radars = extract_radar_list(raw)
        print(f"Found {len(radars)} radars total", flush=True)

        # ── Step 2: match radars to hero ASINs ───────────────────────────────
        matched = {}  # asin -> radar dict
        for r in radars:
            # ASIN may be a nested object: {"asin": {"asin": "B0...", ...}}
            asin_field = r.get("asin")
            if isinstance(asin_field, dict):
                asin = (asin_field.get("asin") or "").strip().upper()
            else:
                asin = (asin_field or "").strip().upper()

            if asin in HERO_ASINS:
                matched[asin] = r
            elif asin in SKIP_ASINS:
                pass  # silently skip

        print(f"Matched {len(matched)}/{len(HERO_ASINS)} hero ASINs", flush=True)

        for asin in HERO_ASINS:
            if asin not in matched:
                notes.append(f"No rank radar found for {asin} ({HERO_ASINS[asin]})")
                print(f"  MISSING radar: {asin}", flush=True)

        # ── Step 3: fetch rank data for each matched radar ────────────────────
        for asin, radar in matched.items():
            radar_id = radar.get("id") or radar.get("rankRadarId") or radar.get("_id") or ""
            name = HERO_ASINS[asin]
            print(f"Fetching radar data for {asin} ({name}) [id={radar_id}]...", flush=True)

            if not radar_id:
                notes.append(f"Radar for {asin} has no ID field. Keys: {list(radar.keys())}")
                products[asin] = None
                continue

            raw2 = await api_get(
                client,
                f"/v1/niches/rank-radars/{radar_id}",
                {"startDate": START_DATE, "endDate": END_DATE}
            )
            await asyncio.sleep(RATE_LIMIT)

            if "error" in raw2:
                notes.append(f"Error fetching radar {radar_id} for {asin}: {raw2['error']}")
                products[asin] = None
                continue

            # ── Parse keywords + rank data ────────────────────────────────────
            # DataDive response structure: list of keyword objects or dict with keywords key
            if isinstance(raw2, list):
                kw_list = raw2
            elif isinstance(raw2, dict):
                for key in ("keywords", "items", "data", "rankRadarData"):
                    if key in raw2 and isinstance(raw2[key], list):
                        kw_list = raw2[key]
                        break
                else:
                    # Maybe the whole dict is keyword data
                    kw_list = [raw2] if raw2 else []
            else:
                kw_list = []

            if not kw_list:
                notes.append(f"No keyword data returned for {asin} ({name})")
                products[asin] = None
                continue

                # Print sample keyword structure (for debugging)
            print(f"  Sample kw keys: {list(kw_list[0].keys())}", flush=True)

            # ── Compute metrics ────────────────────────────────────────────────
            total_kws = len(kw_list)
            top10_today = 0
            top50_today = 0
            top10_yesterday = 0

            movers = []   # (score, kw, sv, y_rank, t_rank, change)
            losers = []

            for kw_obj in kw_list:
                kw_name = kw_obj.get("keyword") or kw_obj.get("name") or kw_obj.get("keywordText") or ""
                sv      = kw_obj.get("searchVolume") or kw_obj.get("sv") or 0

                # Ranks may be embedded in a "ranks" list or as direct fields
                today_rank = None
                yest_rank  = None

                # Try "ranks" list: [{date, organicRank, impressionRank}, ...]
                ranks_list = kw_obj.get("ranks") or kw_obj.get("dailyRanks") or []
                if isinstance(ranks_list, list):
                    for r in ranks_list:
                        d = r.get("date", "")[:10]
                        if d == TODAY:
                            today_rank = r.get("organicRank")
                        elif d == YESTERDAY:
                            yest_rank = r.get("organicRank")

                # Fallback: direct fields
                if today_rank is None:
                    today_rank = kw_obj.get("organicRank") or kw_obj.get("rank")
                if yest_rank is None:
                    yest_rank = kw_obj.get("previousRank") or kw_obj.get("prevRank")

                # Convert to int, skip if missing/0
                def to_int(v):
                    try:
                        return int(v) if v not in (None, "", 0) else None
                    except (ValueError, TypeError):
                        return None

                t_rank = to_int(today_rank)
                y_rank = to_int(yest_rank)

                # Counts for today
                if t_rank is not None:
                    if t_rank <= 10:
                        top10_today += 1
                    if t_rank <= 50:
                        top50_today += 1

                # Counts for yesterday (for trend)
                if y_rank is not None:
                    if y_rank <= 10:
                        top10_yesterday += 1

                # Mover scoring
                if t_rank is not None and y_rank is not None:
                    change = y_rank - t_rank  # positive = improvement (rank number went down)
                    score  = abs(sv) * abs(change)
                    if change > 0:
                        movers.append((score, kw_name, sv, y_rank, t_rank, change))
                    elif change < 0:
                        losers.append((score, kw_name, sv, y_rank, t_rank, change))

            # Sort
            movers.sort(key=lambda x: x[0], reverse=True)
            losers.sort(key=lambda x: x[0], reverse=True)

            # Trend
            delta = top10_today - top10_yesterday
            if top10_today == 0 and top50_today == 0:
                trend = "collapsed"
            elif top10_today == 0:
                trend = "critical"
            elif delta >= 2:
                trend = "improving"
            elif delta <= -2:
                trend = "declining"
            else:
                trend = "stable"

            products[asin] = {
                "top10": top10_today,
                "top50": top50_today,
                "total": total_kws,
                "trend": trend,
                "significant_movers": [
                    {"keyword": m[1], "sv": m[2], "yesterday": m[3], "today": m[4], "change": m[5]}
                    for m in movers[:10]
                ],
                "big_losers": [
                    {"keyword": l[1], "sv": l[2], "yesterday": l[3], "today": l[4], "change": l[5]}
                    for l in losers[:5]
                ],
            }

            print(f"  Done: top10={top10_today}, top50={top50_today}, total={total_kws}, trend={trend}", flush=True)

    # Fill missing products with null
    for asin in HERO_ASINS:
        if asin not in products:
            products[asin] = None

    result = {
        "fetch_date": "2026-03-02",
        "date_range": f"{START_DATE} to {END_DATE}",
        "products": products,
        "notes": notes,
    }

    print("\n\n=== FINAL JSON OUTPUT ===\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
