#!/usr/bin/env python3
"""
Generate Daily Market Intel Report for 2026-02-23
Merges Apify product data, DataDive competitor/rank radar data, keyword search results,
yesterday's snapshot, and baseline data into a comprehensive markdown report.
"""

import json
import math
import os
from datetime import datetime, date

# === CONFIGURATION ===
BASE_DIR = r"C:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE"
SNAPSHOT_DIR = os.path.join(BASE_DIR, "outputs", "research", "market-intel", "snapshots")
BRIEF_DIR = os.path.join(BASE_DIR, "outputs", "research", "market-intel", "briefs")

REPORT_DATE = "2026-02-23"
BASELINE_DATE = "2026-02-11"

# Input files
APIFY_PRODUCTS_FILE = os.path.join(SNAPSHOT_DIR, "apify-products-2026-02-23.json")
DATADIVE_COMPETITORS_FILE = os.path.join(SNAPSHOT_DIR, "datadive-competitors-2026-02-23.json")
DATADIVE_RANKRADAR_FILE = os.path.join(SNAPSHOT_DIR, "datadive-rankradar-2026-02-23.json")
APIFY_KEYWORDS_FILE = os.path.join(SNAPSHOT_DIR, "apify-keywords-2026-02-23.json")
YESTERDAY_SNAPSHOT_FILE = os.path.join(SNAPSHOT_DIR, "2026-02-22.json")
BASELINE_FILE = os.path.join(SNAPSHOT_DIR, "baseline.json")

# Output files
REPORT_OUTPUT = os.path.join(BRIEF_DIR, "2026-02-23.md")
SNAPSHOT_OUTPUT = os.path.join(SNAPSHOT_DIR, "2026-02-23.json")

# Hero products
HERO_PRODUCTS = {
    "B08DDJCQKF": "Cross Stitch Girls",
    "B0F6YTG1CH": "My First Cross Stitch",
    "B09X55KL2C": "10 Embroidery Patterns",
    "B0DC69M3YD": "4 Embroidery Flowers",
    "B09WQSBZY7": "Fairy Sewing Kit",
    "B096MYBLS1": "Dessert Sewing Kit",
    "B08FYH13CL": "Latch Hook Pencil Cases",
    "B0F8R652FX": "Latch Hook Rainbow Heart",
    "B0F8DG32H5": "Knitting Cat & Hat",
    "B09THLVFZK": "Mini Fuse Beads 48",
    "B07D6D95NG": "10mm Big Fuse Beads",
    "B0FQC7YFX6": "Princess Lacing Card",
    "B09HVSLBS6": "Needlepoint Cat Wallet",
}

# Category mapping
TOYS_AND_GAMES_ASINS = {"B09WQSBZY7", "B096MYBLS1"}

# BSR-to-sales conversion tables (BSR -> daily sales)
ACS_TABLE = [
    (1000, 1700), (5000, 680), (10000, 390), (25000, 170), (50000, 90), (100000, 45)
]
TG_TABLE = [
    (1000, 2500), (5000, 1000), (10000, 570), (25000, 250), (50000, 130), (100000, 65)
]

# Seller Board data
SELLER_BOARD = {
    "latest_date": "Feb 21",
    "latest": {
        "revenue": 4275.49,
        "units": 176,
        "profit": 928.30,
        "margin": 21.7,
        "ad_spend": 880.66,
        "tacos": 20.6,
    },
    "avg_7day": {
        "revenue": 4009.54,
        "units": 167,
        "profit": 834.87,
        "margin": 20.6,
        "ad_spend": 800.29,
        "tacos": 20.0,
    },
    "trend": {
        "revenue": 18.7,
        "profit": 80.7,
    }
}


def load_json(filepath):
    """Load JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def bsr_to_daily_sales(bsr, category="Arts, Crafts & Sewing"):
    """
    Convert BSR to estimated daily sales using logarithmic interpolation.
    """
    if bsr is None or bsr <= 0:
        return 0

    table = TG_TABLE if category == "Toys & Games" else ACS_TABLE

    # If BSR is below lowest in table
    if bsr <= table[0][0]:
        # Extrapolate using first two points
        b1, s1 = table[0]
        b2, s2 = table[1]
        log_ratio = math.log(bsr / b1) / math.log(b2 / b1)
        log_sales = math.log(s1) + log_ratio * (math.log(s2) - math.log(s1))
        return round(math.exp(log_sales))

    # If BSR is above highest in table
    if bsr >= table[-1][0]:
        b1, s1 = table[-2]
        b2, s2 = table[-1]
        log_ratio = math.log(bsr / b1) / math.log(b2 / b1)
        log_sales = math.log(s1) + log_ratio * (math.log(s2) - math.log(s1))
        return max(1, round(math.exp(log_sales)))

    # Interpolate between two points
    for i in range(len(table) - 1):
        b1, s1 = table[i]
        b2, s2 = table[i + 1]
        if b1 <= bsr <= b2:
            log_ratio = math.log(bsr / b1) / math.log(b2 / b1)
            log_sales = math.log(s1) + log_ratio * (math.log(s2) - math.log(s1))
            return round(math.exp(log_sales))

    return 0


def parse_bsr(bestseller_ranks):
    """
    Parse bestsellerRanks array from Apify data.
    Returns (main_bsr, main_category, subcategory_rank, subcategory_name).
    """
    if not bestseller_ranks:
        return None, None, None, None

    main_bsr = None
    main_category = None
    subcategory_rank = None
    subcategory_name = None

    for entry in bestseller_ranks:
        rank_str = entry.get("rank", "").replace(",", "")
        try:
            rank = int(rank_str)
        except (ValueError, TypeError):
            continue

        text = entry.get("text", "")
        href = entry.get("href", "")

        # Main category is typically the first entry or has top-level category URL
        if "toys-and-games/ref=pd_zg_ts" in href or "arts-crafts/ref=pd_zg_ts" in href:
            main_bsr = rank
            if "toys-and-games" in href:
                main_category = "Toys & Games"
            else:
                main_category = "Arts, Crafts & Sewing"
        else:
            # Subcategory
            subcategory_rank = rank
            # Extract subcategory name from text: "#X in Category Name"
            if " in " in text:
                subcategory_name = text.split(" in ", 1)[1].strip()

    return main_bsr, main_category, subcategory_rank, subcategory_name


def format_bsr_change(today_bsr, compare_bsr):
    """
    Format BSR change. Lower BSR = better.
    Returns string like "up_arrow -500" (improved) or "down_arrow +500" (declined).
    """
    if today_bsr is None or compare_bsr is None:
        return "N/A"

    diff = today_bsr - compare_bsr
    if diff < 0:
        # BSR went down = improved
        return f"↑ {diff:,}"
    elif diff > 0:
        # BSR went up = declined
        return f"↓ +{diff:,}"
    else:
        return "→ 0"


def get_dd_monthly_sales(asin, dd_data):
    """Get DataDive monthly sales for an ASIN across all niches."""
    total_sales = 0
    found = False
    for niche in dd_data.get("niches", []):
        for comp in niche.get("competitors", []):
            if comp.get("asin") == asin:
                sales = comp.get("sales")
                if sales is not None and sales > total_sales:
                    total_sales = sales
                    found = True
    return total_sales if found else None


def get_category_for_asin(asin):
    """Get category for an ASIN."""
    if asin in TOYS_AND_GAMES_ASINS:
        return "Toys & Games"
    return "Arts, Crafts & Sewing"


def build_niche_category_map():
    """Map hero ASINs to niche categories for competitor comparison."""
    return {
        "Cross Stitch": {
            "hero_asins": ["B08DDJCQKF", "B0F6YTG1CH"],
            "dd_niche_label": "Cross Stitch Kits for Kids",
        },
        "Embroidery Kids": {
            "hero_asins": ["B09X55KL2C"],
            "dd_niche_label": "Embroidery Stitch Practice Kit",
        },
        "Embroidery Adults": {
            "hero_asins": ["B0DC69M3YD"],
            "dd_niche_label": "Beginners Embroidery Kit for Kids",
        },
        "Sewing Kids": {
            "hero_asins": ["B09WQSBZY7", "B096MYBLS1"],
            "dd_niche_label": "Sewing Kit for Kids (New)",
        },
        "Latch Hook": {
            "hero_asins": ["B08FYH13CL", "B0F8R652FX"],
            "dd_niche_label": "Latch Hook Kit for Kids",
        },
        "Fuse Beads": {
            "hero_asins": ["B09THLVFZK", "B07D6D95NG"],
            "dd_niche_label": "Mini Perler Beads",
        },
        "Knitting": {
            "hero_asins": ["B0F8DG32H5"],
            "dd_niche_label": "Loom Knitting",
        },
        "Lacing Cards": {
            "hero_asins": ["B0FQC7YFX6"],
            "dd_niche_label": "Lacing Cards for Kids Ages 3-5",
        },
    }


def main():
    print(f"Loading data files for {REPORT_DATE}...")

    # Load all data sources
    apify_products = load_json(APIFY_PRODUCTS_FILE)
    dd_competitors = load_json(DATADIVE_COMPETITORS_FILE)
    dd_rankradar = load_json(DATADIVE_RANKRADAR_FILE)
    apify_keywords = load_json(APIFY_KEYWORDS_FILE)
    yesterday = load_json(YESTERDAY_SNAPSHOT_FILE)
    baseline = load_json(BASELINE_FILE)

    print(f"  Apify products: {len(apify_products.get('hero_products', {}))} heroes, {len(apify_products.get('competitors', {}))} competitors")
    print(f"  DataDive: {dd_competitors.get('nicheCount', 0)} niches, {dd_competitors.get('totalCompetitors', 0)} competitors")
    print(f"  Rank Radar: {dd_rankradar.get('radarCount', 0)} radars")
    print(f"  Keywords: {len(apify_keywords.get('keyword_rankings', {}))} keywords searched")
    print(f"  Yesterday snapshot: {yesterday.get('date', 'N/A')}")
    print(f"  Baseline: {baseline.get('baseline_date', 'N/A')}")

    # === BUILD HERO PRODUCT TABLE ===
    hero_data = []
    for asin, name in HERO_PRODUCTS.items():
        apify = apify_products.get("hero_products", {}).get(asin, {})
        bsr_ranks = apify.get("bestsellerRanks", [])
        main_bsr, main_cat, subcat_rank, subcat_name = parse_bsr(bsr_ranks)

        # Use known category mapping
        category = get_category_for_asin(asin)

        # Estimate daily sales
        daily_sales = bsr_to_daily_sales(main_bsr, category) if main_bsr else 0

        # DataDive monthly sales
        dd_sales = get_dd_monthly_sales(asin, dd_competitors)

        # Reviews and rating
        reviews = apify.get("reviewsCount", "N/A")
        rating = apify.get("stars", "N/A")
        availability = apify.get("availability", True)

        # Yesterday comparison
        yest = yesterday.get("hero_products", {}).get(asin, {})
        yest_bsr = yest.get("bsr")
        vs_yesterday = format_bsr_change(main_bsr, yest_bsr)

        # Baseline comparison
        base = baseline.get("hero_products", {}).get(asin, {})
        base_bsr = base.get("bsr")
        vs_baseline = format_bsr_change(main_bsr, base_bsr)

        hero_data.append({
            "asin": asin,
            "name": name,
            "category": category,
            "bsr": main_bsr,
            "daily_sales": daily_sales,
            "dd_monthly_sales": dd_sales,
            "subcat_rank": subcat_rank,
            "subcat_name": subcat_name,
            "reviews": reviews,
            "rating": rating,
            "availability": availability,
            "vs_yesterday": vs_yesterday,
            "vs_baseline": vs_baseline,
            "yest_bsr": yest_bsr,
            "base_bsr": base_bsr,
        })

    # Sort by daily sales descending
    hero_data.sort(key=lambda x: x["daily_sales"], reverse=True)

    # Count improving/declining/stable
    improving = sum(1 for h in hero_data if h["bsr"] and h["yest_bsr"] and h["bsr"] < h["yest_bsr"])
    declining = sum(1 for h in hero_data if h["bsr"] and h["yest_bsr"] and h["bsr"] > h["yest_bsr"])
    stable = sum(1 for h in hero_data if h["bsr"] and h["yest_bsr"] and h["bsr"] == h["yest_bsr"])

    # Days since baseline
    d1 = datetime.strptime(REPORT_DATE, "%Y-%m-%d").date()
    d2 = datetime.strptime(BASELINE_DATE, "%Y-%m-%d").date()
    days_since = (d1 - d2).days

    # === BUILD RANK RADAR SECTION ===
    # Map ASIN to radar summary
    radar_by_asin = {}
    for rs in dd_rankradar.get("radarSummaries", []):
        radar_by_asin[rs["asin"]] = rs

    # Collect all movers for hero products
    all_movers = []
    for rs in dd_rankradar.get("radarSummaries", []):
        asin = rs.get("asin")
        product_name = HERO_PRODUCTS.get(asin, asin)
        for m in rs.get("movers", []):
            all_movers.append({
                "asin": asin,
                "product": product_name,
                "keyword": m["keyword"],
                "search_volume": m.get("searchVolume", 0),
                "previous_rank": m["previousRank"],
                "current_rank": m["currentRank"],
                "change": m["change"],
                "direction": m["direction"],
                "abs_change": abs(m["change"]),
            })

    # Sort by absolute change * search_volume (impact score) descending
    all_movers.sort(key=lambda x: x["abs_change"] * max(x["search_volume"], 1), reverse=True)
    top_movers = all_movers[:20]

    # === BUILD COMPETITOR COMPARISON ===
    niche_map = build_niche_category_map()

    # Build competitor data from Apify + DataDive
    def get_apify_competitor(asin):
        """Get competitor data from Apify products."""
        comp = apify_products.get("competitors", {}).get(asin, {})
        if comp:
            main_bsr, main_cat, subcat_rank, subcat_name = parse_bsr(comp.get("bestsellerRanks", []))
            return {
                "bsr": main_bsr,
                "subcat_rank": subcat_rank,
                "reviews": comp.get("reviewsCount", "N/A"),
                "rating": comp.get("stars", "N/A"),
                "title": comp.get("title", ""),
            }
        return None

    # === BUILD KEYWORD RANKINGS SECTION ===
    kw_data = apify_keywords.get("keyword_rankings", {})
    yesterday_kw = yesterday.get("keyword_rankings", {})

    # Organize keyword rankings by category
    keyword_categories = {
        "Cross Stitch": ["kids cross stitch kit", "beginner cross stitch kits for kids", "cross stitch kit for beginners"],
        "Embroidery": ["embroidery kit for kids", "kids embroidery kit", "embroidery kit for beginners"],
        "Sewing": ["sewing kit for kids", "kids sewing kit", "sewing kits for kids ages 8-12"],
        "Latch Hook": ["latch hook kit for kids", "latch hook kit"],
        "Fuse Beads": ["fuse beads", "perler beads", "mini fuse beads"],
        "Knitting": ["knitting kit for kids", "kids knitting kit"],
        "Lacing Cards": ["lacing cards for kids", "lacing cards"],
        "Needlepoint": ["needlepoint kits for beginners"],
    }

    # Get best positions by category
    best_positions = []
    for cat, keywords in keyword_categories.items():
        for kw in keywords:
            if kw in kw_data:
                our_prods = kw_data[kw].get("our_products", [])
                if our_prods:
                    best = our_prods[0]
                    # Find top competitor
                    comps = kw_data[kw].get("competitors", [])
                    top_comp = comps[0] if comps else None
                    top_comp_unknown = kw_data[kw].get("unknown_top10", [])
                    # Get the best non-us competitor
                    if top_comp:
                        best_positions.append({
                            "category": cat,
                            "keyword": kw,
                            "our_position": best["position"],
                            "our_asin": best["asin"],
                            "top_competitor": top_comp.get("title", "")[:50] if top_comp else "N/A",
                            "their_position": top_comp.get("position", "N/A") if top_comp else "N/A",
                        })

    # Position changes vs yesterday
    position_changes = []
    for kw in kw_data:
        if kw in yesterday_kw:
            today_our = {p["asin"]: p["position"] for p in kw_data[kw].get("our_products", [])}
            yest_our = {p["asin"]: p["position"] for p in yesterday_kw[kw].get("our_products", [])}
            for asin in today_our:
                if asin in yest_our:
                    today_pos = today_our[asin]
                    yest_pos = yest_our[asin]
                    if today_pos != yest_pos:
                        position_changes.append({
                            "keyword": kw,
                            "asin": asin,
                            "product": HERO_PRODUCTS.get(asin, asin),
                            "yesterday": yest_pos,
                            "today": today_pos,
                            "change": yest_pos - today_pos,  # positive = improved
                        })

    position_changes.sort(key=lambda x: abs(x["change"]), reverse=True)

    # === NEW/RISING COMPETITORS ===
    new_competitors = []
    for kw in kw_data:
        unknowns = kw_data[kw].get("unknown_top10", [])
        for unk in unknowns:
            pos = unk.get("position", 999)
            if pos <= 10:
                new_competitors.append({
                    "keyword": kw,
                    "asin": unk.get("asin", ""),
                    "title": (unk.get("title", "") or "")[:60],
                    "position": pos,
                    "rating": unk.get("rating", ""),
                    "num_ratings": unk.get("num_ratings", ""),
                })

    # Deduplicate by ASIN, keeping lowest position
    seen_asins = {}
    for nc in new_competitors:
        asin = nc["asin"]
        if asin not in seen_asins or nc["position"] < seen_asins[asin]["position"]:
            seen_asins[asin] = nc
    new_competitors = sorted(seen_asins.values(), key=lambda x: x["position"])[:20]

    # === ALERTS ===
    alerts = []

    # BSR spike alerts (>20% increase vs yesterday)
    for h in hero_data:
        if h["bsr"] and h["yest_bsr"]:
            pct_change = (h["bsr"] - h["yest_bsr"]) / h["yest_bsr"] * 100
            if pct_change > 20:
                alerts.append({
                    "type": "🔴 BSR SPIKE",
                    "product": h["name"],
                    "details": f"BSR {h['yest_bsr']:,} → {h['bsr']:,} ({pct_change:+.0f}% vs yesterday)",
                })
            elif pct_change < -20:
                alerts.append({
                    "type": "🟢 WIN",
                    "product": h["name"],
                    "details": f"BSR improved significantly: {h['yest_bsr']:,} → {h['bsr']:,} ({pct_change:+.0f}%)",
                })

    # OOS alerts
    for h in hero_data:
        if not h["availability"]:
            alerts.append({
                "type": "⚠️ OOS",
                "product": h["name"],
                "details": f"Product appears OUT OF STOCK on Amazon",
            })

    # Review gains
    for h in hero_data:
        base = baseline.get("hero_products", {}).get(h["asin"], {})
        base_reviews = base.get("reviews", 0)
        try:
            current_reviews = int(str(h["reviews"]).replace(",", ""))
            base_reviews_int = int(str(base_reviews).replace(",", ""))
            review_gain = current_reviews - base_reviews_int
            if review_gain >= 10:
                alerts.append({
                    "type": "🟢 WIN",
                    "product": h["name"],
                    "details": f"+{review_gain} reviews since baseline ({base_reviews_int} → {current_reviews})",
                })
        except (ValueError, TypeError):
            pass

    # New competitor alerts
    for nc in new_competitors[:5]:
        alerts.append({
            "type": "🆕 NEW COMPETITOR",
            "product": nc["title"][:40],
            "details": f"ASIN {nc['asin']} at position #{nc['position']} for '{nc['keyword']}'",
        })

    # Rank drop alerts for hero products
    for m in all_movers:
        if m["asin"] in HERO_PRODUCTS and m["direction"] == "DOWN" and m["abs_change"] >= 20 and m["search_volume"] >= 1000:
            alerts.append({
                "type": "🟡 WATCH",
                "product": m["product"],
                "details": f"Rank dropped for '{m['keyword']}' (SV:{m['search_volume']:,}): {m['previous_rank']} → {m['current_rank']}",
            })

    # === GENERATE REPORT ===
    lines = []
    lines.append(f"# Market Intel - {REPORT_DATE}")
    lines.append("")
    lines.append(f"**Baseline:** {BASELINE_DATE} | **Days Since Baseline:** {days_since}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Account Snapshot
    sb = SELLER_BOARD
    lines.append("## Account Snapshot (from Seller Board)")
    lines.append("")
    lines.append(f"| Metric | Latest ({sb['latest_date']}) | 7-Day Avg | Trend |")
    lines.append("|--------|----------|-----------|-------|")
    lines.append(f"| Total Revenue | ${sb['latest']['revenue']:,.2f} | ${sb['avg_7day']['revenue']:,.2f}/day | +{sb['trend']['revenue']}% |")
    lines.append(f"| Total Units | {sb['latest']['units']} | {sb['avg_7day']['units']}/day | — |")
    lines.append(f"| Net Profit | ${sb['latest']['profit']:,.2f} | ${sb['avg_7day']['profit']:,.2f}/day | +{sb['trend']['profit']}% |")
    lines.append(f"| Profit Margin | {sb['latest']['margin']}% | {sb['avg_7day']['margin']}% | +{sb['latest']['margin'] - sb['avg_7day']['margin']:.1f} pp |")
    lines.append(f"| Ad Spend | ${sb['latest']['ad_spend']:,.2f} | ${sb['avg_7day']['ad_spend']:,.2f}/day | — |")
    lines.append(f"| TACoS | {sb['latest']['tacos']}% | {sb['avg_7day']['tacos']}% | +{sb['latest']['tacos'] - sb['avg_7day']['tacos']:.1f} pp |")
    lines.append("")
    lines.append("> **Note:** Seller Board data lags ~2 days. Feb 21 is most recent.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count | vs Baseline |")
    lines.append("|--------|-------|-------------|")

    # vs baseline counts
    base_improving = sum(1 for h in hero_data if h["bsr"] and h["base_bsr"] and h["bsr"] < h["base_bsr"])
    base_declining = sum(1 for h in hero_data if h["bsr"] and h["base_bsr"] and h["bsr"] > h["base_bsr"])
    base_stable = sum(1 for h in hero_data if h["bsr"] and h["base_bsr"] and h["bsr"] == h["base_bsr"])

    lines.append(f"| Products Improving (BSR down) | {improving} | {base_improving} vs baseline |")
    lines.append(f"| Products Declining (BSR up) | {declining} | {base_declining} vs baseline |")
    lines.append(f"| Products Stable | {stable} | {base_stable} vs baseline |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Our Products Table
    lines.append("## Our Products (Unified by Sales Velocity)")
    lines.append("")
    lines.append("| # | Product | ASIN | Category | BSR | Est. Daily Sales | DataDive Mo Sales | Subcat Rank | Reviews | Rating | vs Yesterday | vs Baseline |")
    lines.append("|---|---------|------|----------|-----|-----------------|------------------|-------------|---------|--------|-------------|-------------|")

    for i, h in enumerate(hero_data, 1):
        bsr_str = f"{h['bsr']:,}" if h["bsr"] else "N/A"
        daily_str = f"~{h['daily_sales']}" if h["daily_sales"] else "N/A"
        dd_str = f"{h['dd_monthly_sales']:,}/mo" if h["dd_monthly_sales"] else "—"
        subcat_str = f"#{h['subcat_rank']} {h['subcat_name']}" if h["subcat_rank"] else "N/A"
        avail_marker = " ⚠️OOS" if not h["availability"] else ""

        lines.append(
            f"| {i} | {h['name']}{avail_marker} | {h['asin']} | {h['category']} | {bsr_str} | {daily_str} | {dd_str} | {subcat_str} | {h['reviews']} | {h['rating']} | {h['vs_yesterday']} | {h['vs_baseline']} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")

    # Keyword Rank Snapshot
    lines.append("## Keyword Rank Snapshot (from DataDive Rank Radar)")
    lines.append("")
    lines.append("### Our Hero Products — Top Keyword Positions")
    lines.append("")
    lines.append("| Product | ASIN | Top 10 KWs | Top 50 KWs | Sig. Movers | Trend |")
    lines.append("|---------|------|-----------|-----------|-------------|-------|")

    for asin, name in HERO_PRODUCTS.items():
        radar = radar_by_asin.get(asin)
        if radar:
            top10 = radar.get("keywordsInTop10", 0)
            top50 = radar.get("keywordsInTop50", 0)
            total = radar.get("totalKeywords", 0)
            sig = radar.get("significantMovers", 0)
            movers = radar.get("movers", [])
            up_count = sum(1 for m in movers if m["direction"] == "UP")
            down_count = sum(1 for m in movers if m["direction"] == "DOWN")
            trend = f"↑{up_count} ↓{down_count}" if movers else "—"
            lines.append(f"| {name} | {asin} | {top10}/{total} | {top50}/{total} | {sig} | {trend} |")

    lines.append("")
    lines.append("### Key Rank Movements Today")
    lines.append("")
    lines.append("| Keyword | Product | Search Vol | Yesterday | Today | Change | Alert |")
    lines.append("|---------|---------|-----------|-----------|-------|--------|-------|")

    for m in top_movers:
        if m["direction"] == "UP":
            alert = "🟢" if m["abs_change"] >= 10 else "↑"
            change_str = f"+{m['change']}"
        else:
            alert = "🔴" if m["abs_change"] >= 10 else "↓"
            change_str = f"{m['change']}"

        lines.append(
            f"| {m['keyword']} | {m['product']} | {m['search_volume']:,} | {m['previous_rank']} | {m['current_rank']} | {change_str} | {alert} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")

    # Competitor Comparison
    lines.append("## Competitor Comparison")
    lines.append("")

    for cat_name, cat_info in niche_map.items():
        dd_label = cat_info["dd_niche_label"]
        hero_asins = cat_info["hero_asins"]

        # Find matching DD niche
        dd_niche = None
        for niche in dd_competitors.get("niches", []):
            if niche.get("nicheLabel") == dd_label:
                dd_niche = niche
                break

        lines.append(f"### {cat_name}")
        lines.append("")

        if dd_niche:
            lines.append("| Rank | Brand/ASIN | BSR (Apify) | Subcat Rank | Reviews | DD Sales/mo | vs Us |")
            lines.append("|------|-----------|-------------|-------------|---------|-------------|-------|")

            comps = dd_niche.get("competitors", [])
            # Sort by sales descending
            comps_sorted = sorted(comps, key=lambda x: x.get("sales", 0) or 0, reverse=True)

            our_position = None
            for rank, comp in enumerate(comps_sorted, 1):
                asin = comp.get("asin", "")
                is_ours = asin in hero_asins
                sales = comp.get("sales", 0) or 0
                reviews = comp.get("reviewCount", 0)
                rating = comp.get("rating", 0)

                # Try to get Apify BSR
                apify_comp = get_apify_competitor(asin)
                if not apify_comp:
                    # Check hero products
                    apify_hero = apify_products.get("hero_products", {}).get(asin, {})
                    if apify_hero:
                        bsr_data = parse_bsr(apify_hero.get("bestsellerRanks", []))
                        apify_comp = {
                            "bsr": bsr_data[0],
                            "subcat_rank": bsr_data[2],
                            "reviews": apify_hero.get("reviewsCount", "N/A"),
                            "rating": apify_hero.get("stars", "N/A"),
                        }

                bsr_str = f"{apify_comp['bsr']:,}" if apify_comp and apify_comp.get("bsr") else "—"
                subcat_str = f"#{apify_comp['subcat_rank']}" if apify_comp and apify_comp.get("subcat_rank") else "—"

                marker = "**🟦 US**" if is_ours else ""
                name_str = f"{HERO_PRODUCTS.get(asin, asin)} {marker}" if is_ours else asin

                if is_ours:
                    our_position = rank

                lines.append(
                    f"| {rank} | {name_str} | {bsr_str} | {subcat_str} | {reviews:,} | {sales:,}/mo | {marker} |"
                )

            if our_position:
                lines.append(f"\n**Our Position:** #{our_position} of {len(comps_sorted)}")
            else:
                lines.append(f"\n**Our Position:** Not in this niche's DD data")
        else:
            lines.append("*No DataDive niche data available for this category.*")

        lines.append("")

    lines.append("---")
    lines.append("")

    # Keyword Search Rankings
    lines.append("## Keyword Search Rankings (from Apify)")
    lines.append("")
    lines.append("### Our Best Positions by Category")
    lines.append("")
    lines.append("| Category | Keyword | Our Best Position | Our ASIN | Top Competitor | Their Position |")
    lines.append("|----------|---------|-------------------|----------|----------------|----------------|")

    # Deduplicate - show best position per category
    seen_cats = {}
    for bp in best_positions:
        cat = bp["category"]
        if cat not in seen_cats or bp["our_position"] < seen_cats[cat]["our_position"]:
            seen_cats[cat] = bp

    for cat in sorted(seen_cats.keys()):
        bp = seen_cats[cat]
        comp_name = bp["top_competitor"][:40] if bp["top_competitor"] else "N/A"
        lines.append(f"| {bp['category']} | {bp['keyword']} | #{bp['our_position']} | {bp['our_asin']} | {comp_name} | #{bp['their_position']} |")

    # Also show all positions where we're in top 3
    lines.append("")
    lines.append("### All Top 3 Positions")
    lines.append("")
    lines.append("| Keyword | Our ASIN | Product | Position | Badge |")
    lines.append("|---------|----------|---------|----------|-------|")

    for kw in sorted(kw_data.keys()):
        for prod in kw_data[kw].get("our_products", []):
            if prod["position"] <= 3:
                badge = prod.get("badge", "") or "—"
                name = HERO_PRODUCTS.get(prod["asin"], prod["asin"])
                lines.append(f"| {kw} | {prod['asin']} | {name} | #{prod['position']} | {badge} |")

    lines.append("")

    # Position changes vs yesterday
    lines.append("### Position Changes vs Yesterday")
    lines.append("")
    if position_changes:
        lines.append("| Keyword | Product | Yesterday | Today | Change |")
        lines.append("|---------|---------|-----------|-------|--------|")
        for pc in position_changes[:30]:
            direction = "🟢" if pc["change"] > 0 else "🔴"
            change_str = f"+{pc['change']}" if pc["change"] > 0 else str(pc["change"])
            lines.append(f"| {pc['keyword']} | {pc['product']} | #{pc['yesterday']} | #{pc['today']} | {direction} {change_str} |")
    else:
        lines.append("*No position changes detected vs yesterday.*")

    lines.append("")
    lines.append("---")
    lines.append("")

    # New/Rising Competitors
    lines.append("## New / Rising Competitors")
    lines.append("")
    if new_competitors:
        lines.append("| Niche | Brand/Title | ASIN | Found On Keyword | Position | Alert |")
        lines.append("|-------|------------|------|-----------------|----------|-------|")
        for nc in new_competitors:
            lines.append(f"| — | {nc['title']} | {nc['asin']} | {nc['keyword']} | #{nc['position']} | 🆕 |")
    else:
        lines.append("*No new competitors detected in top 10 positions.*")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Alerts
    lines.append("## Alerts")
    lines.append("")
    if alerts:
        lines.append("| Type | Product | Details |")
        lines.append("|------|---------|---------|")
        for a in alerts:
            lines.append(f"| {a['type']} | {a['product']} | {a['details']} |")
    else:
        lines.append("*No alerts today.*")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Data Notes
    lines.append("## Data Notes")
    lines.append("")
    lines.append(f"- **Report Date:** {REPORT_DATE}")
    lines.append(f"- **Baseline Date:** {BASELINE_DATE} ({days_since} days)")
    lines.append(f"- **Apify Products Scraped:** {len(apify_products.get('hero_products', {}))} hero + {len(apify_products.get('competitors', {}))} competitors")
    lines.append(f"- **DataDive Niches:** {dd_competitors.get('nicheCount', 0)} niches, {dd_competitors.get('totalCompetitors', 0)} competitor records")
    lines.append(f"- **Rank Radars Active:** {dd_rankradar.get('radarCount', 0)}")
    lines.append(f"- **Keywords Searched (Apify):** {len(kw_data)}")
    lines.append(f"- **Seller Board Data:** Feb 15-21 (lags ~2 days)")
    lines.append(f"- **BSR Conversion:** Logarithmic interpolation from reference tables")
    lines.append(f"- **Sources:** Apify (Amazon scraper), DataDive API, Seller Board CSV reports")

    failed = apify_products.get("failed_batches", [])
    if failed:
        lines.append(f"- **Failed Batches:** {len(failed)} Apify scrape batches failed")

    lines.append("")

    # Write report
    os.makedirs(BRIEF_DIR, exist_ok=True)
    report_content = "\n".join(lines)
    with open(REPORT_OUTPUT, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"\nReport written to: {REPORT_OUTPUT}")

    # === GENERATE SNAPSHOT JSON ===
    snapshot = {
        "date": REPORT_DATE,
        "source": "saswave/amazon-product-scraper",
        "notes": f"Automated daily market intel. {len(apify_products.get('hero_products', {}))} heroes, {len(apify_products.get('competitors', {}))} competitors, {len(kw_data)} keyword searches, {dd_rankradar.get('radarCount', 0)} rank radars.",
        "hero_products": {},
        "competitors": {},
        "keyword_rankings": {},
    }

    # Hero products snapshot
    for asin, name in HERO_PRODUCTS.items():
        apify = apify_products.get("hero_products", {}).get(asin, {})
        main_bsr, main_cat, subcat_rank, subcat_name = parse_bsr(apify.get("bestsellerRanks", []))

        snapshot["hero_products"][asin] = {
            "name": name,
            "bsr": main_bsr,
            "subcategory_rank": subcat_rank,
            "subcategory": subcat_name,
            "reviews": apify.get("reviewsCount", "N/A"),
            "rating": apify.get("stars", "N/A"),
            "availability": apify.get("availability", True),
        }

        if not apify.get("availability", True):
            snapshot["hero_products"][asin]["note"] = "OUT OF STOCK"

    # Competitors snapshot
    for asin, comp in apify_products.get("competitors", {}).items():
        main_bsr, main_cat, subcat_rank, subcat_name = parse_bsr(comp.get("bestsellerRanks", []))

        # Try to determine niche from yesterday's data
        yest_comp = yesterday.get("competitors", {}).get(asin, {})
        brand = yest_comp.get("brand", "")
        niche = yest_comp.get("niche", "")
        comp_name = yest_comp.get("name", comp.get("title", "")[:40])

        snapshot["competitors"][asin] = {
            "name": comp_name,
            "brand": brand,
            "niche": niche,
            "bsr": main_bsr,
            "subcategory_rank": subcat_rank,
            "reviews": comp.get("reviewsCount", "N/A"),
            "rating": comp.get("stars", "N/A"),
        }

    # Keyword rankings snapshot (simplified)
    for kw, kw_info in kw_data.items():
        snapshot["keyword_rankings"][kw] = {
            "our_products": [
                {"asin": p["asin"], "position": p["position"], "title": "", "badge": ""}
                for p in kw_info.get("our_products", [])
            ],
            "competitors": [
                {"asin": p["asin"], "position": p["position"], "title": "", "badge": ""}
                for p in kw_info.get("competitors", [])
            ],
            "total_results": kw_info.get("total_results", 0),
        }

    with open(SNAPSHOT_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    print(f"Snapshot written to: {SNAPSHOT_OUTPUT}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"DAILY MARKET INTEL REPORT - {REPORT_DATE}")
    print(f"{'='*60}")
    print(f"  Hero Products: {len(hero_data)}")
    print(f"    Improving (BSR down vs yesterday): {improving}")
    print(f"    Declining (BSR up vs yesterday): {declining}")
    print(f"    Stable: {stable}")
    print(f"  Top performer: {hero_data[0]['name']} (BSR {hero_data[0]['bsr']:,}, ~{hero_data[0]['daily_sales']} sales/day)")
    print(f"  Rank Radar: {len(all_movers)} significant keyword movements")
    print(f"  New competitors in top 10: {len(new_competitors)}")
    print(f"  Alerts: {len(alerts)}")
    print(f"  Keywords tracked: {len(kw_data)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
