"""
Apify Amazon Keyword Search Script
Searches 27 keywords across 9 categories using igview-owner/amazon-search-scraper
Tracks hero products, competitors, and unknown ASINs in search results.
"""

import json
import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# --- Configuration ---
ENV_PATH = r"C:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE\.env"
OUTPUT_PATH = r"C:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE\outputs\research\market-intel\snapshots\apify-keywords-2026-02-23.json"

load_dotenv(ENV_PATH)
API_TOKEN = os.getenv("APIFY_API_TOKEN")
if not API_TOKEN:
    raise ValueError("APIFY_API_TOKEN not found in .env file")

ACTOR_ID = "igview-owner~amazon-search-scraper"
BASE_URL = f"https://api.apify.com/v2/acts/{ACTOR_ID}"

# Hero product ASINs
HERO_ASINS = {
    "B08DDJCQKF", "B0F6YTG1CH", "B09X55KL2C", "B0DC69M3YD", "B09WQSBZY7",
    "B096MYBLS1", "B08FYH13CL", "B0F8R652FX", "B0F8DG32H5", "B09THLVFZK",
    "B07D6D95NG", "B0FQC7YFX6", "B09HVSLBS6"
}

# Tracked competitor ASINs
COMPETITOR_ASINS = {
    "B08T5QC9FS", "B0B7JHN4F1", "B0CM9JKNCC", "B0DFHN42QB", "B087DYHMZ2",
    "B0D8171TF1", "B08TC7423N", "B0DP654CSV", "B0CZHKSSL4", "B0DMHY2HF3",
    "B0B762JW55", "B0C3ZVKB46", "B0BB9N74SG", "B091GXM2Y6", "B0C2XYP6L3",
    "B0CV1F5CFS", "B0CXY8JMTK", "B0CYNNT2ZT", "B0CTTMWXYP", "B06XRRN4VL",
    "B0CX9H8YGR", "B004JIFCXO", "B0B8W4FK4Q", "B0C5WQD914", "B0FN4CT867",
    "B08QV9CMFQ", "B0D5LF666P", "B00JM5G05I", "B0BRYRD91V", "B0D178S25M",
    "B0CWLTTZ2G"
}

# Keywords grouped by category
KEYWORDS_BY_CATEGORY = {
    "Cross Stitch": [
        "embroidery kit for kids",
        "kids cross stitch kit",
        "beginner cross stitch kits for kids"
    ],
    "Embroidery Kids": [
        "kids embroidery kit",
        "embroidery kit for beginners kids",
        "kids embroidery kits ages 8-12"
    ],
    "Embroidery Adults": [
        "embroidery kit for beginners",
        "embroidery kits for adults",
        "needle point kits adults"
    ],
    "Sewing Kids": [
        "sewing kit for kids",
        "kids sewing kit",
        "sewing kits for kids 8-12"
    ],
    "Latch Hook": [
        "latch hook kits for kids",
        "hook rug kits for kids",
        "latch kits"
    ],
    "Fuse Beads": [
        "mini perler beads",
        "mini beads",
        "mini fuse beads"
    ],
    "Knitting": [
        "loom knitting kit",
        "knitting loom kit",
        "knitting kit for kids"
    ],
    "Lacing Cards": [
        "lacing cards",
        "lacing cards for kids ages 3-5",
        "lacing cards for kids ages 4-8"
    ],
    "Needlepoint": [
        "needlepoint kits for kids",
        "kids needlepoint kit",
        "beginner cross stitch kits for kids"
    ]
}

# Flatten keywords (preserving order, deduplicating)
ALL_KEYWORDS = []
seen = set()
for category, kws in KEYWORDS_BY_CATEGORY.items():
    for kw in kws:
        if kw not in seen:
            ALL_KEYWORDS.append(kw)
            seen.add(kw)

POLL_INTERVAL = 8  # seconds
TIMEOUT = 90  # seconds per keyword
DELAY_BETWEEN = 3  # seconds between launching searches


def categorize_asin(asin):
    """Categorize an ASIN as hero, competitor, or unknown."""
    if asin in HERO_ASINS:
        return "hero"
    elif asin in COMPETITOR_ASINS:
        return "competitor"
    return "unknown"


def start_run(keyword):
    """Start an Apify actor run for a keyword search."""
    url = f"{BASE_URL}/runs?token={API_TOKEN}"
    payload = {
        "query": keyword,
        "maxPages": 1,
        "country": "US",
        "language": "en_US",
        "sortBy": "RELEVANCE"
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    run_id = data["data"]["id"]
    return run_id


def poll_run(run_id, timeout=TIMEOUT):
    """Poll an Apify run until it completes or times out."""
    url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={API_TOKEN}"
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        status = resp.json()["data"]["status"]
        if status == "SUCCEEDED":
            return True
        elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
            return False
        time.sleep(POLL_INTERVAL)
    return False  # timed out


def fetch_results(run_id):
    """Fetch dataset items from a completed run."""
    url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items?token={API_TOKEN}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def process_keyword(keyword, attempt=1):
    """Run a full keyword search: start, poll, fetch, parse."""
    print(f"  [{attempt}] Starting search for: '{keyword}'")
    try:
        run_id = start_run(keyword)
        print(f"      Run ID: {run_id} - polling...")
        success = poll_run(run_id)
        if not success:
            print(f"      FAILED or timed out for '{keyword}'")
            return None

        items = fetch_results(run_id)
        print(f"      Got {len(items)} results")

        our_products = []
        competitors = []
        unknown_top10 = []

        for item in items:
            asin = item.get("asin", "")
            if not asin:
                continue

            position = item.get("position", 0)

            # Build badge string from available fields
            badges = []
            if item.get("product_badge"):
                badges.append(item["product_badge"])
            if item.get("is_amazon_choice"):
                badges.append("Amazon's Choice")
            if item.get("is_best_seller"):
                badges.append("Best Seller")
            badge_str = ", ".join(badges)

            product_info = {
                "asin": asin,
                "position": position,
                "title": item.get("product_title", ""),
                "badge": badge_str,
                "price": item.get("product_price", ""),
                "rating": item.get("product_star_rating", ""),
                "num_ratings": item.get("product_num_ratings", 0),
                "sales_volume": item.get("sales_volume", ""),
                "is_prime": item.get("is_prime", False)
            }

            cat = categorize_asin(asin)
            if cat == "hero":
                our_products.append(product_info)
            elif cat == "competitor":
                competitors.append(product_info)
            elif position <= 10:  # top 10 only for unknowns
                unknown_top10.append(product_info)

        return {
            "our_products": our_products,
            "competitors": competitors,
            "unknown_top10": unknown_top10,
            "total_results": len(items)
        }
    except Exception as e:
        print(f"      ERROR: {e}")
        return None


def main():
    print(f"=" * 70)
    print(f"APIFY AMAZON KEYWORD SEARCH")
    print(f"Date: 2026-02-23")
    print(f"Keywords: {len(ALL_KEYWORDS)} unique (27 total, some may overlap)")
    print(f"Hero ASINs: {len(HERO_ASINS)} | Competitor ASINs: {len(COMPETITOR_ASINS)}")
    print(f"=" * 70)

    results = {
        "date": "2026-02-23",
        "keyword_rankings": {},
        "new_competitors_detected": [],
        "failed_keywords": []
    }

    for i, keyword in enumerate(ALL_KEYWORDS):
        print(f"\n[{i+1}/{len(ALL_KEYWORDS)}] Processing: '{keyword}'")

        result = process_keyword(keyword, attempt=1)

        # Retry once if failed
        if result is None:
            print(f"  Retrying '{keyword}'...")
            time.sleep(3)
            result = process_keyword(keyword, attempt=2)

        if result is None:
            results["failed_keywords"].append(keyword)
            print(f"  FAILED after retry: '{keyword}'")
        else:
            results["keyword_rankings"][keyword] = result

            # Track unknown top-10 ASINs as potential new competitors
            for prod in result.get("unknown_top10", []):
                results["new_competitors_detected"].append({
                    "asin": prod["asin"],
                    "keyword": keyword,
                    "position": prod["position"],
                    "title": prod["title"]
                })

        # Wait between keywords (except after last)
        if i < len(ALL_KEYWORDS) - 1:
            time.sleep(DELAY_BETWEEN)

    # Save results
    output_path = Path(OUTPUT_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"RESULTS SAVED TO: {OUTPUT_PATH}")
    print(f"{'=' * 70}")

    # --- SUMMARY ---
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Keywords searched: {len(ALL_KEYWORDS)}")
    print(f"Successful: {len(results['keyword_rankings'])}")
    print(f"Failed: {len(results['failed_keywords'])}")

    if results["failed_keywords"]:
        print(f"\nFailed keywords:")
        for kw in results["failed_keywords"]:
            print(f"  - {kw}")

    print(f"\n{'=' * 70}")
    print("PER-KEYWORD RANKINGS")
    print(f"{'=' * 70}")
    print(f"{'Keyword':<45} {'Our Best':>10} {'Top Comp':>10} {'Results':>8}")
    print("-" * 75)

    for kw, data in results["keyword_rankings"].items():
        our_best = min([p["position"] for p in data["our_products"]], default="-")
        comp_best = min([p["position"] for p in data["competitors"]], default="-")
        total = data["total_results"]
        print(f"{kw:<45} {str(our_best):>10} {str(comp_best):>10} {total:>8}")

    # Unknown ASINs summary (deduplicated)
    unknown_asins = {}
    for entry in results["new_competitors_detected"]:
        asin = entry["asin"]
        if asin not in unknown_asins:
            unknown_asins[asin] = {
                "asin": asin,
                "title": entry["title"],
                "keywords": [],
                "best_position": entry["position"]
            }
        unknown_asins[asin]["keywords"].append(f"{entry['keyword']} (#{entry['position']})")
        unknown_asins[asin]["best_position"] = min(unknown_asins[asin]["best_position"], entry["position"])

    # Sort by frequency (most keyword appearances first)
    sorted_unknowns = sorted(unknown_asins.values(), key=lambda x: (-len(x["keywords"]), x["best_position"]))

    print(f"\n{'=' * 70}")
    print(f"UNKNOWN ASINs IN TOP 10 (Potential New Competitors): {len(sorted_unknowns)}")
    print(f"{'=' * 70}")

    for u in sorted_unknowns[:30]:  # Show top 30
        print(f"\n  ASIN: {u['asin']}")
        print(f"  Title: {u['title'][:80]}")
        print(f"  Best Position: #{u['best_position']}")
        print(f"  Found in {len(u['keywords'])} keywords: {', '.join(u['keywords'][:5])}")

    print(f"\n{'=' * 70}")
    print("DONE")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
