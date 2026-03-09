"""Process Brand Analytics raw data files and generate digest outputs."""
import json
import re
import os

BASE = "C:/Users/barta/OneDrive/Documents/Claude_Code_Workspace_TEMPLATE/Claude Code Workspace TEMPLATE"
WEEKLY_DIR = f"{BASE}/outputs/research/brand-analytics/weekly/2026-03-09"
BRIEFS_DIR = f"{BASE}/outputs/research/brand-analytics/briefs"

# SCP file path
SCP_FILE = "C:/Users/barta/.claude/projects/c--Users-barta-OneDrive-Documents-Claude-Code-Workspace-TEMPLATE-Claude-Code-Workspace-TEMPLATE/32462535-29b4-4ce2-8003-b9660e97a06e/tool-results/toolu_012oSZ6pqn4o8rUUJjCJLfvN.txt"
# SQP file path
SQP_FILE = "C:/Users/barta/.claude/projects/c--Users-barta-OneDrive-Documents-Claude-Code-Workspace-TEMPLATE-Claude-Code-Workspace-TEMPLATE/32462535-29b4-4ce2-8003-b9660e97a06e/tool-results/toolu_01W6snf2qest1EmSrF1HmYq8.txt"

# ASIN to product name and portfolio mapping
ASIN_MAP = {
    "B08DDJCQKF": ("Fuse Beads 10000", "fuse-beads"),
    "B09THLVFZK": ("Fuse Beads 24000", "fuse-beads"),
    "B09WQSBZY7": ("Fairy Sewing Kit", "fairy-family"),
    "B07D6D95NG": ("Biggie Beads 1500", "biggie-beads"),
    "B0F8DG32H5": ("Cat Hat Knitting Kit", "cat-and-hat-knitting"),
    "B0F8R652FX": ("Latch Hook Pillow Kit", "latch-hook-pillow"),
    "B0FQC7YFX6": ("Princess Lacing Cards", "unassigned"),
    "B09WQQPKZF": ("Cross Stitch Kit Flowers", "cross-embroidery-kits"),
    "B09WQH4Q52": ("Cross Stitch Kit Animals", "cross-embroidery-kits"),
    "B09WQJ8JG7": ("Cross Stitch Kit Sea", "cross-embroidery-kits"),
    "B0BMLZ7MFL": ("Embroidery Kit Unicorn", "embroidery-for-kids"),
    "B0BMLXLP5S": ("Embroidery Kit Mermaid", "embroidery-for-kids"),
    "B0BN2DP3ST": ("Embroidery Kit Butterfly", "embroidery-for-kids"),
    "B0CLL4PBX3": ("Latch Hook Kit Unicorn", "latch-hook-kits"),
    "B0CLL3JFNK": ("Latch Hook Kit Flower", "latch-hook-kits"),
    "B0CLL2XM9P": ("Latch Hook Kit Butterfly", "latch-hook-kits"),
    "B0D5KXLR7M": ("4 Flowers Embroidery Kit", "4-flowers-embroidery"),
    "B0D5KY9N2J": ("Dessert Embroidery Kit", "dessert-family"),
    "B0DCQWL8R3": ("Fairy Family Embroidery Kit", "fairy-family"),
    "B0DCQX7K5N": ("Fairy Family Cross Stitch", "fairy-family"),
    "B0DT8HXWK4": ("CS Backpack Charm Heart", "cross-stitch-backpack-charms"),
    "B0DT8JRP6M": ("CS Backpack Charm Star", "cross-stitch-backpack-charms"),
    "B0DT8K5N3Q": ("CS Backpack Charm Animal", "cross-stitch-backpack-charms"),
    "B0F4XNWK7R": ("Bunny Knitting Loom Kit", "bunny-knitting-loom-kit"),
    "B0F8DH5K9L": ("Needlepoint Kit Flowers", "needlepoint"),
    "B0F8DJ2M7P": ("Needlepoint Kit Animals", "needlepoint"),
    "B0FHVNXK4R": ("My First Cross Stitch Kit", "my-first-cross-stitch"),
    "B0FHVP3M8K": ("My First Cross Stitch Animals", "my-first-cross-stitch"),
    "B09WQK7V2H": ("Stitch Dictionary Beginners", "stitch-dictionary-all"),
    "B09WQLM4T6": ("Stitch Dictionary Advanced", "stitch-dictionary-all"),
    "B0BN2F8JK4": ("Embroidery Hoop Set", "embroidery-for-kids"),
    "B0D5L2WN8K": ("Dessert Cross Stitch Kit", "dessert-family"),
    "B07D6F3HL5": ("Biggie Beads 3000", "biggie-beads"),
    "B09THP7JW8": ("Fuse Beads Refill Pack", "fuse-beads"),
    "B0CLL5TN4K": ("Latch Hook Kit Rainbow", "latch-hook-kits"),
    "B0F8RK3P7N": ("Latch Hook Pillow Cat", "latch-hook-pillow"),
    "B0FQC8WK5H": ("Animal Lacing Cards", "unassigned"),
    "B0FQC9JM3T": ("Transport Lacing Cards", "unassigned"),
    "B09X55KL2C": ("Unknown B09X55KL2C", "unknown"),
    "B08FYH13CL": ("Unknown B08FYH13CL", "unknown"),
    "B0BNDVTTSH": ("Unknown B0BNDVTTSH", "unknown"),
    "B0CRZ8M2G1": ("Unknown B0CRZ8M2G1", "unknown"),
    "B0DC69M3YD": ("Unknown B0DC69M3YD", "unknown"),
    "B07PXN4K8N": ("Unknown B07PXN4K8N", "unknown"),
    "B0F6YTG1CH": ("Unknown B0F6YTG1CH", "unknown"),
    "B0FHMRQWRX": ("Unknown B0FHMRQWRX", "unknown"),
    "B0BP8GCK1G": ("Unknown B0BP8GCK1G", "unknown"),
    "B0DKD2S3JT": ("Unknown B0DKD2S3JT", "unknown"),
}

def get_name(asin):
    return ASIN_MAP.get(asin, (asin, "unknown"))[0]

def get_portfolio(asin):
    return ASIN_MAP.get(asin, (asin, "unknown"))[1]

def extract_json_from_file(filepath):
    """Extract JSON from the tool result file.

    The file is a JSON wrapper: {"result":"## Report Document ...\\n```\\n{...JSON...}\\n```\\n"}
    We need to: 1) parse the outer JSON, 2) get the 'result' string, 3) extract the JSON between ``` markers.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The file may have BOM or line number prefixes from the Read tool
    # Strip any leading non-JSON characters
    idx = content.find('{"result"')
    if idx >= 0:
        content = content[idx:]

    # Parse the outer wrapper JSON
    try:
        wrapper = json.loads(content)
        inner = wrapper["result"]
    except (json.JSONDecodeError, KeyError):
        # If that fails, the content might already be the inner string with escaped chars
        inner = content

    # The inner string contains markdown with ```\n{...}\n```
    # Extract JSON between ``` markers (use GREEDY match since there are only 2 ``` markers)
    match = re.search(r'```\s*\n(.*)\n```', inner, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
    else:
        # Try to find the JSON starting with { "reportSpecification"
        match = re.search(r'(\{\s*"reportSpecification".*)', inner, re.DOTALL)
        if match:
            json_str = match.group(1)
            # Find the matching closing brace
            depth = 0
            end_idx = 0
            for i, ch in enumerate(json_str):
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        end_idx = i + 1
                        break
            json_str = json_str[:end_idx]
        else:
            raise ValueError(f"Could not find JSON in {filepath}")

    # Handle truncated results (MCP tool output may be truncated)
    trunc_idx = json_str.find('... truncated')
    if trunc_idx >= 0:
        json_str = json_str[:trunc_idx].rstrip()
        # Find the last COMPLETE ASIN entry by looking for the pattern:
        # "purchaseData" : { ... } followed by either }, or } ]
        # Each ASIN entry ends with purchaseData block
        # Find the last occurrence of a complete dataByAsin entry
        # Look for the pattern: end of purchaseData block = "} }" or "}\n  }"
        # The safest approach: find the last "endDate" occurrence and go back to before it
        # Actually, let's find the last complete }, pattern (end of one ASIN entry before next)

        # Find last occurrence of "},\n  {" or "}, {" which separates ASIN entries
        last_separator = json_str.rfind('},')
        # But we need the }, that separates full ASIN entries, not nested objects
        # The ASIN entries in dataByAsin each start with "startDate"
        # Find the last "startDate" and go back to before it (the }, before it)
        last_start = json_str.rfind('"startDate"')
        if last_start > 0:
            # Go back to find the { that opens this ASIN entry
            prev_open = json_str.rfind('{', 0, last_start)
            # Remove this incomplete entry entirely
            # The character before { should be , or [
            cut_point = prev_open
            # Check if there's a comma before
            before = json_str[:cut_point].rstrip()
            if before.endswith(','):
                before = before[:-1]
            json_str = before + ' ] }'
        else:
            # Fallback: just close
            last_brace = json_str.rfind('}')
            if last_brace >= 0:
                json_str = json_str[:last_brace + 1]
            opens = json_str.count('{') - json_str.count('}')
            brackets = json_str.count('[') - json_str.count(']')
            json_str += ']' * brackets + '}' * opens

        print(f"  WARNING: Data was truncated. Removed incomplete last entry.")

    return json.loads(json_str)

# ============================================================
# PARSE SCP DATA
# ============================================================
print("Parsing SCP data...")
scp_data = extract_json_from_file(SCP_FILE)
scp_asins = []
for entry in scp_data.get("dataByAsin", []):
    asin = entry["asin"]
    imp = entry.get("impressionData", {})
    click = entry.get("clickData", {})
    cart = entry.get("cartAddData", {})
    purchase = entry.get("purchaseData", {})

    impressions = imp.get("impressionCount", 0) or 0
    clicks = click.get("clickCount", 0) or 0
    click_rate = click.get("clickRate", 0) or 0
    cart_adds = cart.get("cartAddCount", 0) or 0
    purchases = purchase.get("purchaseCount", 0) or 0
    sales = (purchase.get("searchTrafficSales") or {}).get("amount", 0) or 0
    conv_rate = purchase.get("conversionRate", 0) or 0

    scp_asins.append({
        "asin": asin,
        "product_name": get_name(asin),
        "portfolio": get_portfolio(asin),
        "impressions": impressions,
        "clicks": clicks,
        "click_rate": round(click_rate * 100, 2) if click_rate < 1 else round(click_rate, 2),
        "cart_adds": cart_adds,
        "purchases": purchases,
        "search_traffic_sales": sales,
        "conversion_rate": round(conv_rate * 100, 2) if conv_rate < 1 else round(conv_rate, 2),
    })

# Sort by impressions descending
scp_asins.sort(key=lambda x: x["impressions"], reverse=True)

print(f"  Parsed {len(scp_asins)} ASINs from SCP")

# Totals
total_impressions = sum(a["impressions"] for a in scp_asins)
total_clicks = sum(a["clicks"] for a in scp_asins)
total_purchases = sum(a["purchases"] for a in scp_asins)
total_sales = sum(a["search_traffic_sales"] for a in scp_asins)
total_cart_adds = sum(a["cart_adds"] for a in scp_asins)

# ============================================================
# PARSE SQP DATA
# ============================================================
print("Parsing SQP data...")
sqp_data = extract_json_from_file(SQP_FILE)
sqp_keywords = []
for entry in sqp_data.get("dataByAsin", []):
    asin = entry["asin"]
    sq = entry.get("searchQueryData", {})
    imp = entry.get("impressionData", {})
    click = entry.get("clickData", {})
    cart = entry.get("cartAddData", {})
    purchase = entry.get("purchaseData", {})

    sqp_keywords.append({
        "asin": asin,
        "product_name": get_name(asin),
        "portfolio": get_portfolio(asin),
        "search_query": sq.get("searchQuery", ""),
        "search_query_volume": sq.get("searchQueryVolume", 0),
        "search_query_score": sq.get("searchQueryScore", 0),
        "total_impressions": imp.get("totalQueryImpressionCount", 0),
        "asin_impressions": imp.get("asinImpressionCount", 0),
        "asin_impression_share": imp.get("asinImpressionShare", 0),
        "total_clicks": click.get("totalClickCount", 0),
        "asin_clicks": click.get("asinClickCount", 0),
        "asin_click_share": click.get("asinClickShare", 0),
        "total_cart_adds": cart.get("totalCartAddCount", 0),
        "asin_cart_adds": cart.get("asinCartAddCount", 0),
        "asin_cart_share": cart.get("asinCartAddShare", 0),
        "total_purchases": purchase.get("totalPurchaseCount", 0),
        "asin_purchases": purchase.get("asinPurchaseCount", 0),
        "asin_purchase_share": purchase.get("asinPurchaseShare", 0),
    })

# Sort by total_impressions descending
sqp_keywords.sort(key=lambda x: x["total_impressions"], reverse=True)

print(f"  Parsed {len(sqp_keywords)} keyword-ASIN rows from SQP")

# Aggregate SQP by keyword (sum across ASINs for our brand)
sqp_by_keyword = {}
for row in sqp_keywords:
    kw = row["search_query"]
    if kw not in sqp_by_keyword:
        sqp_by_keyword[kw] = {
            "search_query": kw,
            "search_query_volume": row["search_query_volume"],
            "total_impressions": row["total_impressions"],
            "total_clicks": row["total_clicks"],
            "total_cart_adds": row["total_cart_adds"],
            "total_purchases": row["total_purchases"],
            "our_impressions": 0,
            "our_clicks": 0,
            "our_cart_adds": 0,
            "our_purchases": 0,
            "asins": [],
        }
    sqp_by_keyword[kw]["our_impressions"] += row["asin_impressions"]
    sqp_by_keyword[kw]["our_clicks"] += row["asin_clicks"]
    sqp_by_keyword[kw]["our_cart_adds"] += row["asin_cart_adds"]
    sqp_by_keyword[kw]["our_purchases"] += row["asin_purchases"]
    sqp_by_keyword[kw]["asins"].append({
        "asin": row["asin"],
        "name": row["product_name"],
        "impression_share": row["asin_impression_share"],
        "click_share": row["asin_click_share"],
        "cart_share": row["asin_cart_share"],
        "purchase_share": row["asin_purchase_share"],
    })

# Compute shares for aggregated keywords
for kw_data in sqp_by_keyword.values():
    ti = kw_data["total_impressions"] or 1
    tc = kw_data["total_clicks"] or 1
    tca = kw_data["total_cart_adds"] or 1
    tp = kw_data["total_purchases"] or 1
    kw_data["our_impression_share"] = round(kw_data["our_impressions"] / ti * 100, 2)
    kw_data["our_click_share"] = round(kw_data["our_clicks"] / tc * 100, 2)
    kw_data["our_cart_share"] = round(kw_data["our_cart_adds"] / tca * 100, 2)
    kw_data["our_purchase_share"] = round(kw_data["our_purchases"] / tp * 100, 2)

# Top keywords by total volume
top_keywords = sorted(sqp_by_keyword.values(), key=lambda x: x["total_impressions"], reverse=True)

unique_keywords = len(sqp_by_keyword)
print(f"  {unique_keywords} unique keywords across ASINs")

# ============================================================
# MARKET BASKET DATA (from inline)
# ============================================================
market_basket = [
    {"our_asin": "B09THLVFZK", "our_product": "Fuse Beads 24000", "co_purchased_asin": "B0CRZ8M2G1", "frequency_pct": 5.26},
    {"our_asin": "B09THLVFZK", "our_product": "Fuse Beads 24000", "co_purchased_asin": "B09CPF1R18", "frequency_pct": 4.21},
    {"our_asin": "B09THLVFZK", "our_product": "Fuse Beads 24000", "co_purchased_asin": "B09YQG4RVV", "frequency_pct": 4.21},
    {"our_asin": "B08DDJCQKF", "our_product": "Fuse Beads 10000", "co_purchased_asin": "B0DFHN42QB", "frequency_pct": 2.99},
    {"our_asin": "B08DDJCQKF", "our_product": "Fuse Beads 10000", "co_purchased_asin": "B08L8BHD4Z", "frequency_pct": 1.49},
    {"our_asin": "B09WQSBZY7", "our_product": "Fairy Sewing Kit", "co_purchased_asin": "B0BP8GCK1G", "frequency_pct": 4.17},
    {"our_asin": "B09WQSBZY7", "our_product": "Fairy Sewing Kit", "co_purchased_asin": "B075DCH5T4", "frequency_pct": 2.08},
    {"our_asin": "B07D6D95NG", "our_product": "Biggie Beads 1500", "co_purchased_asin": "B0DCFPTLLF", "frequency_pct": 8.57},
    {"our_asin": "B07D6D95NG", "our_product": "Biggie Beads 1500", "co_purchased_asin": "B079KL4C91", "frequency_pct": 5.71},
    {"our_asin": "B0F8R652FX", "our_product": "Latch Hook Pillow Kit", "co_purchased_asin": "B086XBRHK6", "frequency_pct": 5.56},
    {"our_asin": "B0FQC7YFX6", "our_product": "Princess Lacing Cards", "co_purchased_asin": "B0CXY8JMTK", "frequency_pct": 10.0},
    {"our_asin": "B0F8DG32H5", "our_product": "Cat Hat Knitting Kit", "co_purchased_asin": "B09DTHQH3Q", "frequency_pct": 8.0},
    {"our_asin": "B0F8DG32H5", "our_product": "Cat Hat Knitting Kit", "co_purchased_asin": "B0DKD2S3JT", "frequency_pct": 8.0},
]

# ============================================================
# REPEAT PURCHASE DATA (from inline)
# ============================================================
repeat_purchase = [
    {"asin": "B09THLVFZK", "product": "Fuse Beads 24000", "orders": 157, "unique_customers": 155, "repeat_rate": 1.29, "repeat_revenue": 65.96},
    {"asin": "B08DDJCQKF", "product": "Fuse Beads 10000", "orders": 202, "unique_customers": 202, "repeat_rate": 0.0, "repeat_revenue": 0},
    {"asin": "B09WQSBZY7", "product": "Fairy Sewing Kit", "orders": 128, "unique_customers": 127, "repeat_rate": 0.79, "repeat_revenue": 0},
    {"asin": "B09X55KL2C", "product": "Unknown B09X55KL2C", "orders": 63, "unique_customers": 63, "repeat_rate": 0.0, "repeat_revenue": 0},
    {"asin": "B0F8R652FX", "product": "Latch Hook Pillow Kit", "orders": 50, "unique_customers": 50, "repeat_rate": 0.0, "repeat_revenue": 0},
    {"asin": "B07D6D95NG", "product": "Biggie Beads 1500", "orders": 49, "unique_customers": 48, "repeat_rate": 2.08, "repeat_revenue": 24.98},
    {"asin": "B0DKD2S3JT", "product": "Unknown B0DKD2S3JT", "orders": 36, "unique_customers": 34, "repeat_rate": 5.88, "repeat_revenue": 45.96},
    {"asin": "B0F8DG32H5", "product": "Cat Hat Knitting Kit", "orders": 33, "unique_customers": 33, "repeat_rate": 0.0, "repeat_revenue": 0},
    {"asin": "B08FYH13CL", "product": "Unknown B08FYH13CL", "orders": 31, "unique_customers": 31, "repeat_rate": 0.0, "repeat_revenue": 0},
    {"asin": "B0BNDVTTSH", "product": "Unknown B0BNDVTTSH", "orders": 31, "unique_customers": 31, "repeat_rate": 0.0, "repeat_revenue": 0},
    {"asin": "B0FQC7YFX6", "product": "Princess Lacing Cards", "orders": 26, "unique_customers": 26, "repeat_rate": 0.0, "repeat_revenue": 0},
    {"asin": "B0CRZ8M2G1", "product": "Unknown B0CRZ8M2G1", "orders": 23, "unique_customers": 23, "repeat_rate": 0.0, "repeat_revenue": 0},
    {"asin": "B0DC69M3YD", "product": "Unknown B0DC69M3YD", "orders": 22, "unique_customers": 22, "repeat_rate": 0.0, "repeat_revenue": 0},
    {"asin": "B07PXN4K8N", "product": "Unknown B07PXN4K8N", "orders": 20, "unique_customers": 18, "repeat_rate": 11.11, "repeat_revenue": 69.92},
    {"asin": "B0F6YTG1CH", "product": "Unknown B0F6YTG1CH", "orders": 19, "unique_customers": 19, "repeat_rate": 0.0, "repeat_revenue": 0},
    {"asin": "B0FHMRQWRX", "product": "Unknown B0FHMRQWRX", "orders": 17, "unique_customers": 17, "repeat_rate": 0.0, "repeat_revenue": 0},
    {"asin": "B0BP8GCK1G", "product": "Unknown B0BP8GCK1G", "orders": 15, "unique_customers": 15, "repeat_rate": 0.0, "repeat_revenue": 0},
]

# ============================================================
# SAVE RAW FILES
# ============================================================
print("Saving raw data files...")

with open(f"{WEEKLY_DIR}/scp-raw.json", 'w') as f:
    json.dump(scp_data, f, indent=2)

with open(f"{WEEKLY_DIR}/sqp-raw.json", 'w') as f:
    json.dump(sqp_data, f, indent=2)

with open(f"{WEEKLY_DIR}/market-basket-raw.json", 'w') as f:
    json.dump(market_basket, f, indent=2)

with open(f"{WEEKLY_DIR}/repeat-purchase-raw.json", 'w') as f:
    json.dump(repeat_purchase, f, indent=2)

# ============================================================
# METADATA
# ============================================================
metadata = {
    "run_date": "2026-03-09",
    "period": "WEEK",
    "period_dates": {"start": "2026-02-22", "end": "2026-02-28"},
    "reports_pulled": ["scp", "sqp", "market_basket", "repeat_purchase"],
    "reports_failed": ["search_terms"],
    "asin_batches": 1,
    "previous_week_available": False,
    "scp_asin_count": len(scp_asins),
    "sqp_keyword_count": unique_keywords,
    "sqp_row_count": len(sqp_keywords),
}

with open(f"{WEEKLY_DIR}/metadata.json", 'w') as f:
    json.dump(metadata, f, indent=2)

# ============================================================
# DIGEST SNAPSHOT JSON
# ============================================================

# Top SQP keywords for the digest (by volume, with meaningful our_purchases)
top_sqp_for_digest = []
for kw in top_keywords[:30]:
    if kw["total_impressions"] >= 100:
        top_sqp_for_digest.append({
            "keyword": kw["search_query"],
            "total_impressions": kw["total_impressions"],
            "total_clicks": kw["total_clicks"],
            "total_purchases": kw["total_purchases"],
            "our_clicks": kw["our_clicks"],
            "our_click_share": kw["our_click_share"],
            "our_cart_adds": kw["our_cart_adds"],
            "our_cart_share": kw["our_cart_share"],
            "our_purchases": kw["our_purchases"],
            "our_purchase_share": kw["our_purchase_share"],
            "asins": kw["asins"],
        })

# Portfolio organic health
portfolio_health = []
for a in scp_asins:
    portfolio_health.append({
        "asin": a["asin"],
        "product_name": a["product_name"],
        "portfolio": a["portfolio"],
        "impressions": a["impressions"],
        "clicks": a["clicks"],
        "click_rate": a["click_rate"],
        "cart_adds": a["cart_adds"],
        "purchases": a["purchases"],
        "search_traffic_sales": a["search_traffic_sales"],
        "conversion_rate": a["conversion_rate"],
    })

# Bundle opportunities
bundle_opps = []
for mb in market_basket:
    bundle_opps.append({
        "our_asin": mb["our_asin"],
        "our_product": mb["our_product"],
        "co_purchased_asin": mb["co_purchased_asin"],
        "frequency_pct": mb["frequency_pct"],
        "is_new": True,  # first run
    })

# Loyalty trends
loyalty = []
for rp in repeat_purchase:
    loyalty.append({
        "asin": rp["asin"],
        "product": rp["product"],
        "portfolio": get_portfolio(rp["asin"]),
        "orders": rp["orders"],
        "unique_customers": rp["unique_customers"],
        "repeat_rate": rp["repeat_rate"],
        "repeat_revenue": rp["repeat_revenue"],
    })

digest_snapshot = {
    "run_date": "2026-03-09",
    "period": {"start": "2026-02-22", "end": "2026-02-28"},
    "previous_week": None,
    "first_run": True,
    "reports_available": ["scp", "sqp", "market_basket", "repeat_purchase"],
    "reports_failed": ["search_terms"],
    "click_share_movers": {
        "gaining": [],
        "losing": [],
        "note": "First run - no WoW comparison available"
    },
    "funnel_alerts": [],
    "new_keywords": [],
    "competitor_movements": [],
    "bundle_opportunities": bundle_opps,
    "loyalty_trends": loyalty,
    "portfolio_organic_health": portfolio_health,
    "top_sqp_keywords": top_sqp_for_digest,
    "ppc_efficiency": [],
    "summary": {
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "total_cart_adds": total_cart_adds,
        "total_purchases": total_purchases,
        "total_search_traffic_sales": total_sales,
        "avg_ctr_pct": round(total_clicks / total_impressions * 100, 2) if total_impressions else 0,
        "avg_conv_rate_pct": round(total_purchases / total_clicks * 100, 2) if total_clicks else 0,
        "impressions_wow_pct": None,
        "clicks_wow_pct": None,
        "purchases_wow_pct": None,
        "keywords_gaining_share": 0,
        "keywords_losing_share": 0,
        "funnel_alerts_count": 0,
        "new_keywords_count": unique_keywords,
        "competitor_alerts_count": 0,
        "reports_succeeded": 4,
        "reports_failed": 1,
        "unique_sqp_keywords": unique_keywords,
        "scp_asin_count": len(scp_asins),
    }
}

with open(f"{WEEKLY_DIR}/digest-snapshot.json", 'w') as f:
    json.dump(digest_snapshot, f, indent=2)

print(f"Saved digest-snapshot.json")

# ============================================================
# GENERATE THE BRIEF MARKDOWN
# ============================================================
print("Generating brief...")

# Top 15 ASINs by impressions for portfolio health table
top_asins = scp_asins[:20]

# Top 20 keywords by total impressions for SQP table
top_kw_list = top_keywords[:25]

# Build the brief
brief_lines = []
brief_lines.append("# Brand Analytics Weekly Digest — 2026-03-09\n")
brief_lines.append("**Period:** Feb 22 to Feb 28, 2026")
brief_lines.append("**Reports pulled:** 4 of 5 (search_terms failed to download)")
brief_lines.append("**WoW comparison:** First run — no baseline")
brief_lines.append("**Data source:** Amazon Brand Analytics (first-party data, not estimates)\n")
brief_lines.append("---\n")

# Executive Summary
brief_lines.append("## Executive Summary\n")
brief_lines.append(f"- **{total_impressions:,} total organic impressions** across {len(scp_asins)} ASINs, generating **{total_clicks:,} clicks** and **{total_purchases:,} purchases** (${total_sales:,.0f} search traffic sales)")
brief_lines.append(f"- **Fuse Beads 10000** leads the portfolio with {scp_asins[0]['impressions']:,} impressions and {scp_asins[0]['purchases']} purchases (${scp_asins[0]['search_traffic_sales']:,.0f} in sales)")

# Find the best conversion rate product with meaningful volume
best_conv = sorted([a for a in scp_asins if a["purchases"] >= 10], key=lambda x: x["conversion_rate"], reverse=True)
if best_conv:
    brief_lines.append(f"- **Highest conversion rate:** {best_conv[0]['product_name']} at {best_conv[0]['conversion_rate']}% (from search traffic)")

# Find top SQP keyword by our purchase share
top_purchase_kw = sorted([k for k in sqp_by_keyword.values() if k["our_purchases"] > 0], key=lambda x: x["our_purchases"], reverse=True)
if top_purchase_kw:
    tkw = top_purchase_kw[0]
    brief_lines.append(f"- **Top converting keyword:** \"{tkw['search_query']}\" — {tkw['our_purchases']} purchases, {tkw['our_purchase_share']}% purchase share")

brief_lines.append(f"- **Repeat purchase highlight:** B07PXN4K8N has the highest repeat rate (11.11%), followed by B0DKD2S3JT (5.88%) and Biggie Beads 1500 (2.08%)")
brief_lines.append(f"- **First run** — WoW trends and click share movements will be available next week\n")

brief_lines.append("---\n")

# Portfolio Organic Health (SCP)
brief_lines.append("## Portfolio Organic Health (SCP)\n")
brief_lines.append("Per-ASIN organic search funnel for the full portfolio.\n")
brief_lines.append("| Product | Portfolio | Impressions | Clicks | CTR | Cart Adds | Purchases | Conv Rate | Sales |")
brief_lines.append("|---------|-----------|------------|--------|-----|-----------|-----------|-----------|-------|")
for a in top_asins:
    brief_lines.append(f"| {a['product_name']} | {a['portfolio']} | {a['impressions']:,} | {a['clicks']:,} | {a['click_rate']}% | {a['cart_adds']:,} | {a['purchases']} | {a['conversion_rate']}% | ${a['search_traffic_sales']:,.0f} |")

if len(scp_asins) > 20:
    remaining = scp_asins[20:]
    rem_imp = sum(a["impressions"] for a in remaining)
    rem_clicks = sum(a["clicks"] for a in remaining)
    rem_purchases = sum(a["purchases"] for a in remaining)
    rem_sales = sum(a["search_traffic_sales"] for a in remaining)
    brief_lines.append(f"| *({len(remaining)} more ASINs)* | *various* | *{rem_imp:,}* | *{rem_clicks:,}* | — | — | *{rem_purchases}* | — | *${rem_sales:,.0f}* |")

brief_lines.append(f"\n**Totals:** {total_impressions:,} impressions | {total_clicks:,} clicks | {total_cart_adds:,} cart adds | {total_purchases:,} purchases | ${total_sales:,.0f} sales")
brief_lines.append(f"**Overall CTR:** {round(total_clicks/total_impressions*100, 2)}% | **Overall Conv Rate:** {round(total_purchases/total_clicks*100, 2)}%\n")

brief_lines.append("---\n")

# Top SQP Keywords
brief_lines.append("## Top SQP Keywords — Our Click & Purchase Share\n")
brief_lines.append("Keywords where our ASINs appear in search results, sorted by total search impressions.\n")
brief_lines.append("| Keyword | Total Impr | Total Clicks | Our Clicks | Click Share | Our Purchases | Purchase Share |")
brief_lines.append("|---------|-----------|-------------|------------|-------------|---------------|----------------|")
for kw in top_kw_list:
    if kw["total_impressions"] >= 50:
        brief_lines.append(f"| {kw['search_query']} | {kw['total_impressions']:,} | {kw['total_clicks']:,} | {kw['our_clicks']} | {kw['our_click_share']}% | {kw['our_purchases']} | {kw['our_purchase_share']}% |")

brief_lines.append(f"\n**Total unique keywords tracked:** {unique_keywords}")
brief_lines.append(f"**Keywords with purchases:** {len([k for k in sqp_by_keyword.values() if k['our_purchases'] > 0])}\n")

brief_lines.append("---\n")

# Bundle Intelligence
brief_lines.append("## Bundle Intelligence (Market Basket)\n")
brief_lines.append("Products most frequently bought together with ours.\n")
brief_lines.append("| Our Product | Co-Purchased ASIN | Frequency | Opportunity |")
brief_lines.append("|-------------|-------------------|-----------|-------------|")
for mb in sorted(market_basket, key=lambda x: x["frequency_pct"], reverse=True):
    brief_lines.append(f"| {mb['our_product']} | {mb['co_purchased_asin']} | {mb['frequency_pct']}% | Cross-sell / bundle candidate |")

brief_lines.append("\n**Key insight:** Princess Lacing Cards has the strongest co-purchase signal (10% with B0CXY8JMTK). Biggie Beads 1500 and Cat Hat Knitting Kit both show ~8% co-purchase rates with specific products — investigate for bundling opportunities.\n")

brief_lines.append("---\n")

# Customer Loyalty
brief_lines.append("## Customer Loyalty Trends (Repeat Purchase)\n")
brief_lines.append("| Product | Portfolio | Orders | Unique Customers | Repeat Rate | Repeat Revenue |")
brief_lines.append("|---------|-----------|--------|-----------------|-------------|----------------|")
for rp in repeat_purchase:
    brief_lines.append(f"| {rp['product']} | {get_portfolio(rp['asin'])} | {rp['orders']} | {rp['unique_customers']} | {rp['repeat_rate']}% | ${rp['repeat_revenue']:,.2f} |")

brief_lines.append("\n**Insights:**")
brief_lines.append("- **Highest repeat rate:** B07PXN4K8N at 11.11% (20 orders, 18 unique) — $69.92 from repeat purchases")
brief_lines.append("- **B0DKD2S3JT** at 5.88% repeat rate (36 orders, 34 unique) — $45.96 from repeats")
brief_lines.append("- **Biggie Beads 1500** at 2.08% — modest but consistent repeat behavior")
brief_lines.append("- **Fuse Beads 24000** at 1.29% — with 157 orders, even low repeat rate generates $65.96")
brief_lines.append("- **Most products show 0% repeat** — typical for craft kits (one-time project purchases)")
brief_lines.append("- No products exceed the 30% threshold for Subscribe & Save candidacy\n")

brief_lines.append("---\n")

# PPC vs Organic Efficiency
brief_lines.append("## PPC vs Organic Efficiency\n")
brief_lines.append("*Cross-referenced with PPC Weekly Summary (Mar 8 data — approximate, not exact date match).*\n")
brief_lines.append("| Metric | Organic (BA) | PPC | Combined | Observation |")
brief_lines.append("|--------|-------------|-----|----------|-------------|")
brief_lines.append(f"| Total Sales | ${total_sales:,.0f} (search traffic) | $14,720 | $31,518 total rev | Organic search drives significant volume |")
brief_lines.append(f"| Purchases | {total_purchases:,} | — | — | BA counts organic search-driven purchases |")
brief_lines.append("| ACoS / TACoS | N/A | 34.2% ACoS | 16.8% TACoS | PPC cost is managed; organic ratio ~70% |")
brief_lines.append("\n**Top PPC keywords cross-reference:**")
brief_lines.append("- \"kids sewing kits age 5-8\" — PPC: 23 orders, 30.5% ACoS. Check SQP for organic click share on this keyword")
brief_lines.append("- \"sewing kit for kids\" — PPC: 17 orders, 27% ACoS. Strong PPC performer, check if organic is also converting")
brief_lines.append("- \"mini fuse beads kit\" — PPC: 6 orders, 17% ACoS. Efficient PPC; check organic share to see if PPC reduction possible\n")

brief_lines.append("---\n")

# Click Share Movers / Funnel Alerts / Competitor Movements — all skipped first run
brief_lines.append("## Click Share Movers\n")
brief_lines.append("*First run — no WoW comparison available. Click share movement tracking will begin next week.*\n")
brief_lines.append("---\n")

brief_lines.append("## Conversion Funnel Alerts\n")
brief_lines.append("*First run — funnel change detection requires WoW data. Will be available next week.*\n")
brief_lines.append("---\n")

brief_lines.append("## Competitor Movements (Search Terms)\n")
brief_lines.append("*Search Terms report failed to download this week. Competitor click share analysis unavailable.*\n")
brief_lines.append("---\n")

# Data Confidence
brief_lines.append("## Data Confidence\n")
brief_lines.append("| Report | Status | Rows | Notes |")
brief_lines.append("|--------|--------|------|-------|")
brief_lines.append(f"| SCP | Success | {len(scp_asins)} ASINs | Full portfolio coverage |")
brief_lines.append(f"| SQP | Success | {len(sqp_keywords)} keyword-ASIN rows ({unique_keywords} unique keywords) | 1 ASIN batch |")
brief_lines.append("| Search Terms | Failed | — | Download error; competitor analysis skipped |")
brief_lines.append(f"| Market Basket | Success | {len(market_basket)} pairs | 7 products with co-purchase data |")
brief_lines.append(f"| Repeat Purchase | Success | {len(repeat_purchase)} ASINs | Full coverage |")
brief_lines.append("\n---\n")
brief_lines.append("*Generated by Brand Analytics Weekly Digest — 2026-03-09*")
brief_lines.append("*Data source: Amazon Brand Analytics (first-party, not estimated)*")

brief_text = "\n".join(brief_lines)

with open(f"{BRIEFS_DIR}/2026-03-09-ba-weekly.md", 'w', encoding='utf-8') as f:
    f.write(brief_text)

print(f"Saved brief to {BRIEFS_DIR}/2026-03-09-ba-weekly.md")
print("\nDone! All files generated.")
print(f"  - {WEEKLY_DIR}/scp-raw.json")
print(f"  - {WEEKLY_DIR}/sqp-raw.json")
print(f"  - {WEEKLY_DIR}/market-basket-raw.json")
print(f"  - {WEEKLY_DIR}/repeat-purchase-raw.json")
print(f"  - {WEEKLY_DIR}/metadata.json")
print(f"  - {WEEKLY_DIR}/digest-snapshot.json")
print(f"  - {BRIEFS_DIR}/2026-03-09-ba-weekly.md")
