"""
Competitor Price & SERP Tracker - Baseline Processing Script
First run: 2026-03-08
Fetches Apify datasets, processes product + SERP data, generates all output files.
"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import httpx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "-q"])
    import httpx

# === CONFIG ===
APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
BASE_URL = "https://api.apify.com/v2"
TODAY = "2026-03-08"

# Dataset IDs from our runs
PRODUCT_DATASETS = {
    "categorized": "t1VeXg6h18eb9O5Jw",
    "uncategorized_1": "yesQVZqWSWGOaaE0l",
    "uncategorized_2": "PEdo9amxPY3JVmLx2",
}
SERP_DATASETS = {
    "cross-stitch-embroidery-kids": "MQtRlq094o43Y18oE",
    "embroidery-adults-sewing-kids": "X2JKb88DRNr6pL4xd",
    "latch-hook-loom-knitting": "ncUMgDxZo63ecRtlh",
    "fuse-beads": "z2w8OZXwvNI7QiYOG",
    "lacing-needlepoint-gem": "d0FZxhCMXVPVLPpgv",
}

# Paths
WORKSPACE = Path(__file__).resolve().parent.parent.parent.parent.parent
TRACKER_DIR = WORKSPACE / "outputs" / "research" / "competitor-tracker"
CONFIG_PATH = WORKSPACE / "context" / "competitor-config.json"

# Load config
with open(CONFIG_PATH) as f:
    config = json.load(f)

def safe_float(val):
    if val is None:
        return None
    try:
        return float(str(val).replace(chr(36), '').replace(',', '').strip())
    except (ValueError, TypeError):
        return None

def safe_int(val):
    if val is None:
        return None
    try:
        return int(float(str(val).replace(',', '').strip()))
    except (ValueError, TypeError):
        return None



# Build ASIN lookup maps
our_asins = set()
competitor_asins = set()
asin_to_categories = {}  # ASIN -> list of category keys
asin_to_brand = {}  # competitor ASIN -> brand name

for cat_key, cat_data in config["categories"].items():
    for asin in cat_data.get("our_asins", []):
        our_asins.add(asin)
        asin_to_categories.setdefault(asin, []).append(cat_key)
    for comp in cat_data.get("competitor_asins", []):
        asin = comp["asin"]
        competitor_asins.add(asin)
        asin_to_categories.setdefault(asin, []).append(cat_key)
        asin_to_brand[asin] = comp.get("brand", "Unknown")

uncategorized_asins = set(config.get("uncategorized_asins", {}).get("asins", []))

# Keyword -> categories mapping
keyword_to_categories = {}
for cat_key, cat_data in config["categories"].items():
    for kw in cat_data.get("keywords", []):
        keyword_to_categories.setdefault(kw, []).append(cat_key)


def fetch_dataset(dataset_id, limit=1000):
    """Fetch all items from an Apify dataset."""
    url = f"{BASE_URL}/datasets/{dataset_id}/items"
    params = {"token": APIFY_TOKEN, "limit": limit, "format": "json"}
    items = []
    offset = 0
    while True:
        params["offset"] = offset
        resp = httpx.get(url, params=params, timeout=60)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        items.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
        time.sleep(0.5)
    return items


def extract_product_data(item):
    """Extract key fields from saswave product scraper result."""
    asin = item.get("asin", "")

    # BSR extraction
    bsr_main = None
    bsr_sub = None
    ranks = item.get("bestsellerRanks", []) or []
    if isinstance(ranks, list) and len(ranks) > 0:
        bsr_main = safe_int(ranks[0].get("rank")) if isinstance(ranks[0], dict) else None
        if len(ranks) > 1:
            bsr_sub = safe_int(ranks[1].get("rank")) if isinstance(ranks[1], dict) else None

    # Price extraction
    price = item.get("price")
    if isinstance(price, dict):
        price = price.get("value") or price.get("current")
    if price is None:
        price = item.get("priceDetail", {}).get("price") if isinstance(item.get("priceDetail"), dict) else None
    # Ensure price is float or None
    if price is not None:
        try:
            price = float(str(price).replace(chr(36), "").replace(",", "").strip())
        except (ValueError, TypeError):
            price = None

    return {
        "asin": asin,
        "title": item.get("title", ""),
        "price": price,
        "bsr_main": bsr_main,
        "bsr_sub": bsr_sub,
        "bsr_categories": [r.get("category", "") for r in ranks if isinstance(r, dict)],
        "rating": safe_float(item.get("stars")),
        "reviews_count": safe_int(item.get("reviewsCount")),
        "availability": item.get("availability", "Unknown"),
        "brand": item.get("brand", asin_to_brand.get(asin, "Unknown")),
        "categories": asin_to_categories.get(asin, ["uncategorized"]),
        "is_our_asin": asin in our_asins,
        "is_competitor": asin in competitor_asins,
        "is_uncategorized": asin in uncategorized_asins,
        "deal_badge": bool(item.get("deal") or item.get("coupon")),
        "image_url": item.get("thumbnailImage", ""),
    }


def extract_serp_data(item):
    """Extract key fields from axesso SERP scraper result."""
    asin = item.get("asin", "")
    keyword = item.get("keyword", "")

    # Classify ASIN
    if asin in our_asins:
        asin_type = "our_product"
    elif asin in competitor_asins:
        asin_type = "tracked_competitor"
    else:
        asin_type = "unknown"

    return {
        "keyword": keyword,
        "asin": asin,
        "position": item.get("searchResultPosition", -1),  # 0-indexed
        "title": item.get("productDescription", ""),
        "price": item.get("price"),
        "rating": item.get("productRating"),
        "reviews_count": item.get("countReview"),
        "sponsored": item.get("sponsored", False),
        "sales_volume": item.get("salesVolume", ""),
        "asin_type": asin_type,
        "categories": keyword_to_categories.get(keyword, []) + asin_to_categories.get(asin, []),
    }


print("=== Fetching Product Data ===")
all_products = {}
for batch_name, dataset_id in PRODUCT_DATASETS.items():
    print(f"  Fetching {batch_name} ({dataset_id})...")
    items = fetch_dataset(dataset_id)
    print(f"    Got {len(items)} items")
    for item in items:
        pd = extract_product_data(item)
        if pd["asin"]:
            all_products[pd["asin"]] = pd

print(f"\nTotal unique products: {len(all_products)}")
print(f"  Our ASINs found: {sum(1 for p in all_products.values() if p['is_our_asin'])}")
print(f"  Competitor ASINs found: {sum(1 for p in all_products.values() if p['is_competitor'])}")
print(f"  Uncategorized ASINs found: {sum(1 for p in all_products.values() if p['is_uncategorized'])}")

print("\n=== Fetching SERP Data ===")
all_serp = {}  # keyword -> list of results
new_asins_detected = {}  # ASIN -> {keywords, positions}
for batch_name, dataset_id in SERP_DATASETS.items():
    print(f"  Fetching {batch_name} ({dataset_id})...")
    items = fetch_dataset(dataset_id)
    print(f"    Got {len(items)} items")
    for item in items:
        sd = extract_serp_data(item)
        if sd["keyword"] and sd["asin"]:
            all_serp.setdefault(sd["keyword"], []).append(sd)
            # Flag unknown ASINs in top 10
            if sd["asin_type"] == "unknown" and sd["position"] < 10 and not sd["sponsored"]:
                entry = new_asins_detected.setdefault(sd["asin"], {"keywords": [], "positions": [], "title": sd.get("title") or "", "price": sd["price"]})
                if sd["keyword"] not in entry["keywords"]:
                    entry["keywords"].append(sd["keyword"])
                    entry["positions"].append(sd["position"])

print(f"\nTotal keywords with results: {len(all_serp)}")
print(f"Total SERP results: {sum(len(v) for v in all_serp.values())}")
print(f"New unknown ASINs in top 10: {len(new_asins_detected)}")

# === BUILD SNAPSHOT ===
print("\n=== Building Snapshot ===")
snapshot = {
    "scrape_date": TODAY,
    "scrape_metadata": {
        "product_runs": list(PRODUCT_DATASETS.keys()),
        "serp_runs": list(SERP_DATASETS.keys()),
        "total_asins_scraped": len(all_products),
        "total_keywords_scraped": len(all_serp),
        "total_serp_results": sum(len(v) for v in all_serp.values()),
        "is_baseline": True,
    },
    "products": all_products,
    "wow_deltas": {},  # Empty for baseline
    "alerts": [],  # Empty for baseline
    "new_asins_detected": new_asins_detected,
}

snapshot_path = TRACKER_DIR / "snapshots" / f"{TODAY}-snapshot.json"
with open(snapshot_path, "w") as f:
    json.dump(snapshot, f, indent=2, default=str)
print(f"  Wrote snapshot: {snapshot_path}")

# === BUILD SERP FILE ===
print("\n=== Building SERP Data ===")

# Per-keyword summary
keyword_summaries = {}
for kw, results in all_serp.items():
    # Sort by position
    sorted_results = sorted(results, key=lambda x: x["position"])

    our_positions = []
    competitor_positions = {}
    unknown_top10 = []

    for r in sorted_results:
        if r["asin_type"] == "our_product":
            our_positions.append({"asin": r["asin"], "position": r["position"], "sponsored": r["sponsored"]})
        elif r["asin_type"] == "tracked_competitor":
            competitor_positions.setdefault(r["asin"], []).append({"position": r["position"], "sponsored": r["sponsored"]})
        elif r["position"] < 10 and not r["sponsored"]:
            unknown_top10.append({"asin": r["asin"], "position": r["position"], "title": (r.get('title') or '')[:80]})

    keyword_summaries[kw] = {
        "keyword": kw,
        "categories": keyword_to_categories.get(kw, []),
        "total_results": len(results),
        "our_positions": our_positions,
        "competitor_positions": competitor_positions,
        "unknown_top10": unknown_top10,
    }

serp_data = {
    "scrape_date": TODAY,
    "is_baseline": True,
    "keyword_results": keyword_summaries,
}

serp_path = TRACKER_DIR / "serp" / f"{TODAY}-serp.json"
with open(serp_path, "w") as f:
    json.dump(serp_data, f, indent=2, default=str)
print(f"  Wrote SERP data: {serp_path}")

# === BUILD TRENDS ===
print("\n=== Building Initial Trends ===")

# Category-level summaries
category_summaries = {}
for cat_key, cat_data in config["categories"].items():
    cat_comp_asins = [c["asin"] for c in cat_data.get("competitor_asins", [])]
    cat_our_asins = cat_data.get("our_asins", [])

    # Price stats
    comp_prices = [all_products[a]["price"] for a in cat_comp_asins if a in all_products and all_products[a]["price"] is not None]
    our_prices = [all_products[a]["price"] for a in cat_our_asins if a in all_products and all_products[a]["price"] is not None]

    # BSR stats
    comp_bsrs = [all_products[a]["bsr_main"] for a in cat_comp_asins if a in all_products and all_products[a]["bsr_main"] is not None]
    our_bsrs = [all_products[a]["bsr_main"] for a in cat_our_asins if a in all_products and all_products[a]["bsr_main"] is not None]

    # SERP position stats (average organic position across category keywords)
    cat_keywords = cat_data.get("keywords", [])
    our_serp_positions = []
    comp_serp_positions = []
    for kw in cat_keywords:
        if kw in keyword_summaries:
            ks = keyword_summaries[kw]
            for op in ks["our_positions"]:
                if not op["sponsored"]:
                    our_serp_positions.append(op["position"])
            for asin, positions in ks["competitor_positions"].items():
                for p in positions:
                    if not p["sponsored"]:
                        comp_serp_positions.append(p["position"])

    category_summaries[cat_key] = {
        "display_name": cat_data["display_name"],
        "week": TODAY,
        "competitor_count": len(cat_comp_asins),
        "our_asin_count": len(cat_our_asins),
        "price": {
            "our_avg": round(sum(our_prices) / len(our_prices), 2) if our_prices else None,
            "our_min": min(our_prices) if our_prices else None,
            "our_max": max(our_prices) if our_prices else None,
            "comp_avg": round(sum(comp_prices) / len(comp_prices), 2) if comp_prices else None,
            "comp_min": min(comp_prices) if comp_prices else None,
            "comp_max": max(comp_prices) if comp_prices else None,
        },
        "bsr": {
            "our_avg": round(sum(our_bsrs) / len(our_bsrs)) if our_bsrs else None,
            "comp_avg": round(sum(comp_bsrs) / len(comp_bsrs)) if comp_bsrs else None,
        },
        "serp": {
            "our_avg_position": round(sum(our_serp_positions) / len(our_serp_positions), 1) if our_serp_positions else None,
            "comp_avg_position": round(sum(comp_serp_positions) / len(comp_serp_positions), 1) if comp_serp_positions else None,
            "keywords_tracked": len(cat_keywords),
            "keywords_with_our_presence": sum(1 for kw in cat_keywords if kw in keyword_summaries and keyword_summaries[kw]["our_positions"]),
        },
    }

# Per-ASIN time series (just one data point for baseline)
asin_timeseries = {}
for asin, pd in all_products.items():
    if pd["is_competitor"] or pd["is_our_asin"]:
        asin_timeseries[asin] = {
            "brand": pd["brand"],
            "categories": pd["categories"],
            "is_ours": pd["is_our_asin"],
            "weekly_data": [{
                "week": TODAY,
                "price": pd["price"],
                "bsr_main": pd["bsr_main"],
                "reviews": pd["reviews_count"],
                "rating": pd["rating"],
                "availability": pd["availability"],
                "deal_badge": pd["deal_badge"],
            }],
        }

trends = {
    "last_updated": TODAY,
    "weeks_tracked": 1,
    "category_summaries": {TODAY: category_summaries},
    "asin_timeseries": asin_timeseries,
}

trends_path = TRACKER_DIR / "trends.json"
with open(trends_path, "w") as f:
    json.dump(trends, f, indent=2, default=str)
print(f"  Wrote trends: {trends_path}")

# === GENERATE BRIEF ===
print("\n=== Generating Baseline Brief ===")

brief_lines = []
brief_lines.append(f"# Competitor Price & SERP Tracker — Baseline Brief")
brief_lines.append(f"**Date:** {TODAY}  ")
brief_lines.append(f"**Type:** BASELINE (first run — alerts begin next week)  ")
brief_lines.append(f"**Categories:** {len(config['categories'])}  ")
brief_lines.append(f"**Competitor ASINs tracked:** {sum(1 for p in all_products.values() if p['is_competitor'])} of {len(competitor_asins)} configured  ")
brief_lines.append(f"**Keywords tracked:** {len(all_serp)} unique  ")
brief_lines.append("")
brief_lines.append("---")
brief_lines.append("")

# Price Landscape
brief_lines.append("## Price Landscape by Category")
brief_lines.append("")
brief_lines.append("| Category | Our Avg | Comp Avg | Comp Min | Comp Max | Gap |")
brief_lines.append("|----------|---------|----------|----------|----------|-----|")
for cat_key, cs in category_summaries.items():
    our_avg = cs["price"]["our_avg"]
    comp_avg = cs["price"]["comp_avg"]
    comp_min = cs["price"]["comp_min"]
    comp_max = cs["price"]["comp_max"]
    gap = ""
    if our_avg and comp_avg:
        gap_pct = round((our_avg - comp_avg) / comp_avg * 100, 1)
        gap = f"{'+' if gap_pct > 0 else ''}{gap_pct}%"
    brief_lines.append(f"| {cs['display_name']} | {'$'+str(our_avg) if our_avg else 'N/A'} | {'$'+str(comp_avg) if comp_avg else 'N/A'} | {'$'+str(comp_min) if comp_min else 'N/A'} | {'$'+str(comp_max) if comp_max else 'N/A'} | {gap} |")
brief_lines.append("")

# SERP Position Summary
brief_lines.append("## SERP Position Summary")
brief_lines.append("")
brief_lines.append("| Category | Keywords | Our Presence | Our Avg Pos | Comp Avg Pos |")
brief_lines.append("|----------|----------|--------------|-------------|--------------|")
for cat_key, cs in category_summaries.items():
    brief_lines.append(f"| {cs['display_name']} | {cs['serp']['keywords_tracked']} | {cs['serp']['keywords_with_our_presence']}/{cs['serp']['keywords_tracked']} | {cs['serp']['our_avg_position'] or 'N/A'} | {cs['serp']['comp_avg_position'] or 'N/A'} |")
brief_lines.append("")

# Top Competitors by Category
brief_lines.append("## Top Competitors by Category")
brief_lines.append("")
for cat_key, cat_data in config["categories"].items():
    if not cat_data.get("competitor_asins"):
        continue
    brief_lines.append(f"### {cat_data['display_name']}")
    brief_lines.append("")
    brief_lines.append("| ASIN | Brand | Price | BSR | Rating | Reviews |")
    brief_lines.append("|------|-------|-------|-----|--------|---------|")
    for comp in cat_data["competitor_asins"]:
        asin = comp["asin"]
        if asin in all_products:
            p = all_products[asin]
            price_str = f"${p['price']}" if p["price"] else "N/A"
            bsr_str = f"{p['bsr_main']:,}" if p["bsr_main"] else "N/A"
            rating_str = str(p["rating"]) if p["rating"] else "N/A"
            reviews_str = f"{p['reviews_count']:,}" if p["reviews_count"] else "N/A"
            brief_lines.append(f"| {asin} | {comp['brand']} | {price_str} | {bsr_str} | {rating_str} | {reviews_str} |")
        else:
            brief_lines.append(f"| {asin} | {comp['brand']} | scrape failed | — | — | — |")
    brief_lines.append("")

# New ASINs Detected
if new_asins_detected:
    brief_lines.append("## New ASINs Detected in SERP Top 10")
    brief_lines.append("")
    brief_lines.append(f"**{len(new_asins_detected)} unknown ASINs** found ranking in top 10 organic positions.")
    brief_lines.append("")
    # Show top 20 by keyword count
    sorted_new = sorted(new_asins_detected.items(), key=lambda x: len(x[1]["keywords"]), reverse=True)[:20]
    brief_lines.append("| ASIN | Title | Keywords | Best Pos |")
    brief_lines.append("|------|-------|----------|----------|")
    for asin, data in sorted_new:
        title = data.get("title") or ""[:50] + "..." if len(data.get("title", "")) > 50 else data.get("title", "")
        best_pos = min(data["positions"]) + 1 if data["positions"] else "?"
        brief_lines.append(f"| {asin} | {title} | {len(data['keywords'])} | #{best_pos} |")
    brief_lines.append("")

# Our Products Baseline
brief_lines.append("## Our Products — Baseline Snapshot")
brief_lines.append("")
brief_lines.append("| ASIN | Category | Price | BSR | Rating | Reviews |")
brief_lines.append("|------|----------|-------|-----|--------|---------|")
for asin in sorted(our_asins):
    if asin in all_products:
        p = all_products[asin]
        cats = ", ".join(p["categories"][:2])
        price_str = f"${p['price']}" if p["price"] else "N/A"
        bsr_str = f"{p['bsr_main']:,}" if p["bsr_main"] else "N/A"
        rating_str = str(p["rating"]) if p["rating"] else "N/A"
        reviews_str = f"{p['reviews_count']:,}" if p["reviews_count"] else "N/A"
        brief_lines.append(f"| {asin} | {cats} | {price_str} | {bsr_str} | {rating_str} | {reviews_str} |")
brief_lines.append("")

# Uncategorized ASINs summary
uncat_found = {a: all_products[a] for a in uncategorized_asins if a in all_products}
if uncat_found:
    brief_lines.append("## Uncategorized ASINs — Summary")
    brief_lines.append("")
    brief_lines.append(f"**{len(uncat_found)} of {len(uncategorized_asins)}** uncategorized ASINs successfully scraped.")
    brief_lines.append("These need to be mapped to categories for future tracking.")
    brief_lines.append("")

# Footer
brief_lines.append("---")
brief_lines.append("")
brief_lines.append("## Run Metadata")
brief_lines.append("")
brief_lines.append(f"- **Apify product runs:** 3 (97 ASINs)")
brief_lines.append(f"- **Apify SERP runs:** 5 (~103 keywords)")
brief_lines.append(f"- **Total Apify runs:** 8")
brief_lines.append(f"- **Products scraped:** {len(all_products)}")
brief_lines.append(f"- **SERP keywords scraped:** {len(all_serp)}")
brief_lines.append(f"- **SERP results total:** {sum(len(v) for v in all_serp.values())}")
brief_lines.append(f"- **New unknown ASINs in top 10:** {len(new_asins_detected)}")
brief_lines.append("")
brief_lines.append("**Baseline captured — alerts begin next week.**")

brief_text = "\n".join(brief_lines)
brief_path = TRACKER_DIR / "briefs" / f"{TODAY}-weekly-brief.md"
with open(brief_path, "w") as f:
    f.write(brief_text)
print(f"  Wrote brief: {brief_path}")

# === PRINT SUMMARY FOR CLAUDE ===
print("\n" + "=" * 60)
print("PROCESSING COMPLETE")
print("=" * 60)
print(f"\nFiles written:")
print(f"  1. {snapshot_path}")
print(f"  2. {serp_path}")
print(f"  3. {trends_path}")
print(f"  4. {brief_path}")
print(f"\nKey stats:")
print(f"  Products scraped: {len(all_products)}")
print(f"  - Our ASINs: {sum(1 for p in all_products.values() if p['is_our_asin'])}")
print(f"  - Competitors: {sum(1 for p in all_products.values() if p['is_competitor'])}")
print(f"  - Uncategorized: {sum(1 for p in all_products.values() if p['is_uncategorized'])}")
print(f"  Keywords with SERP data: {len(all_serp)}")
print(f"  Unknown ASINs in top 10: {len(new_asins_detected)}")
print()

# Category price/SERP summary for Claude
print("Category Summary:")
for cat_key, cs in category_summaries.items():
    print(f"  {cs['display_name']}:")
    our_avg = cs["price"]["our_avg"]
    comp_avg = cs["price"]["comp_avg"]
    if our_avg and comp_avg:
        gap = round((our_avg - comp_avg) / comp_avg * 100, 1)
        print(f"    Price: Our ${our_avg} vs Comp ${comp_avg} ({'+' if gap > 0 else ''}{gap}%)")
    elif comp_avg:
        print(f"    Price: Comp avg ${comp_avg} (no our data)")
    else:
        print(f"    Price: insufficient data")
    serp = cs["serp"]
    print(f"    SERP: {serp['keywords_with_our_presence']}/{serp['keywords_tracked']} kw presence, our avg pos {serp['our_avg_position'] or 'N/A'}, comp avg pos {serp['comp_avg_position'] or 'N/A'}")
