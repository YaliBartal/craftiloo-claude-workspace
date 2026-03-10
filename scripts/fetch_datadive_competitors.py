"""
Fetch DataDive competitor data for 11 niches.
Returns compact structured JSON suitable for daily market intel report.
Structure: raw["data"]["competitors"] is the list.
"""

import urllib.request
import urllib.parse
import json
import time
import ssl

API_KEY = "pDbBQZJBAd6rome2KvVWN2jxDxGRdSHWazx1KLF9"
BASE_URL = "https://api.datadive.tools"

NICHES = [
    {"id": "u1y83aQfmK", "label": "Kids Cross Stitch Kit",           "heroes": ["B08DDJCQKF", "B0F6YTG1CH"]},
    {"id": "gfot2FZUBU", "label": "Embroidery Stitch Practice Kit",  "heroes": ["B0DC69M3YD", "B09X55KL2C"]},
    {"id": "Er21lin0KC", "label": "Beginners Embroidery Kit for Kids","heroes": ["B09X55KL2C"]},
    {"id": "RmbSD3OH6t", "label": "Sewing Kit for Kids",             "heroes": ["B09WQSBZY7", "B096MYBLS1"]},
    {"id": "3qbggwOhO2", "label": "Latch Hook Kits for Kids",        "heroes": ["B08FYH13CL", "B0F8R652FX"]},
    {"id": "AY4AlnSj9g", "label": "Mini Perler Beads",               "heroes": ["B09THLVFZK"]},
    {"id": "O6b4XATpTj", "label": "Loom Knitting",                   "heroes": ["B0F8DG32H5"]},
    {"id": "Aw4EQhG6bP", "label": "Lacing Cards for Kids",           "heroes": ["B0FQC7YFX6"]},
    {"id": "5IGkCmOM0h", "label": "Needlepoint Pouch Kit",           "heroes": ["B09HVSLBS6"]},
    {"id": "kZRreyE7kJ", "label": "Cross Stitch Kits (broad)",       "heroes": ["B08DDJCQKF", "B09X55KL2C"]},
    {"id": "WFV3TE3beK", "label": "Fuse Beads",                      "heroes": ["B07D6D95NG"]},
]

ALL_HEROES = [
    "B08DDJCQKF", "B0F6YTG1CH", "B09X55KL2C", "B0DC69M3YD",
    "B09WQSBZY7", "B096MYBLS1", "B08FYH13CL", "B0F8R652FX",
    "B0F8DG32H5", "B09THLVFZK", "B07D6D95NG", "B0FQC7YFX6",
    "B09HVSLBS6"
]

ctx = ssl.create_default_context()

def api_get(path, params=None):
    url = BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "x-api-key": API_KEY,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except Exception as e:
        return {"error": str(e)}

def extract_competitors(raw):
    """Extract competitors list from raw["data"]["competitors"]."""
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        # Standard structure: {"data": {"competitors": [...]}}
        data_inner = raw.get("data", {})
        if isinstance(data_inner, dict):
            competitors = data_inner.get("competitors")
            if isinstance(competitors, list):
                return competitors
        # Fallback: try top-level
        for key in ("competitors", "items"):
            val = raw.get(key)
            if isinstance(val, list):
                return val
    return []

def compact_competitor(item):
    """Extract only the needed fields, omit nulls/zeros."""
    out = {}
    asin = item.get("asin") or item.get("ASIN")
    if asin:
        out["asin"] = asin
    brand = item.get("brand") or item.get("brandName") or ""
    if not brand:
        # Fall back to first 30 chars of a title if brand empty
        title = item.get("title", "")
        brand = title[:30] if title else ""
    if brand:
        out["brand"] = str(brand)[:30]
    bsr = item.get("bsr") or item.get("salesRank") or item.get("bestSellerRank")
    if bsr:
        out["bsr"] = bsr
    sales = item.get("sales") or item.get("monthlySales") or item.get("salesEstimate")
    if sales:
        out["sales"] = sales
    revenue = item.get("revenue") or item.get("monthlyRevenue") or item.get("revenueEstimate")
    if revenue:
        out["revenue"] = round(revenue, 2)
    price = item.get("price") or item.get("currentPrice")
    if price:
        out["price"] = price
    rating = item.get("rating") or item.get("starRating")
    if rating:
        out["rating"] = rating
    reviews = item.get("reviewCount") or item.get("reviews") or item.get("numberOfReviews")
    if reviews:
        out["reviews"] = reviews
    kw_p1 = item.get("kwRankedOnP1") or item.get("keywordsRankedOnPage1") or item.get("p1Keywords")
    if kw_p1:
        out["kwRankedOnP1"] = kw_p1
    return out

# --- Main fetch loop ---
result = {
    "fetch_date": "2026-03-02",
    "niches": {},
    "hero_ratings": {},
    "notes": []
}

hero_found = {h: False for h in ALL_HEROES}

for i, niche in enumerate(NICHES):
    nid = niche["id"]
    label = niche["label"]
    heroes = niche["heroes"]

    print(f"[{i+1}/11] Fetching {label} ({nid})...", flush=True)
    raw = api_get(f"/v1/niches/{nid}/competitors", params={"pageSize": 4})

    if "error" in raw:
        result["notes"].append(f"FAILED {nid} ({label}): {raw['error']}")
        print(f"  ERROR: {raw['error']}")
        if i < len(NICHES) - 1:
            time.sleep(1.1)
        continue

    items = extract_competitors(raw)
    print(f"  Got {len(items)} competitor items", flush=True)

    # Sort by sales descending, take top 4
    try:
        items_sorted = sorted(items, key=lambda x: (x.get("sales") or 0), reverse=True)
    except Exception:
        items_sorted = items
    top4 = items_sorted[:4]

    competitors = []
    hero_in_results = {}

    for pos, item in enumerate(top4):
        asin = item.get("asin") or item.get("ASIN", "")
        comp = compact_competitor(item)
        if comp:
            competitors.append(comp)

        # Check if this ASIN is a hero
        if asin in ALL_HEROES:
            rating = item.get("rating") or item.get("starRating")
            reviews = item.get("reviewCount") or item.get("reviews") or item.get("numberOfReviews")
            sales = item.get("sales") or item.get("monthlySales") or 0

            if asin in heroes:
                entry = {"position": pos + 1}
                if rating: entry["rating"] = rating
                if reviews: entry["reviews"] = reviews
                if sales: entry["sales"] = sales
                hero_in_results[asin] = entry

            # hero_ratings: first occurrence across all niches
            if not hero_found[asin]:
                hero_found[asin] = True
                hr = {}
                if rating: hr["rating"] = rating
                if reviews: hr["reviews"] = reviews
                result["hero_ratings"][asin] = hr

    # Also scan ALL items (not just top4) for heroes not in top4
    for item in items:
        asin = item.get("asin") or item.get("ASIN", "")
        if asin in ALL_HEROES and not hero_found[asin]:
            rating = item.get("rating") or item.get("starRating")
            reviews = item.get("reviewCount") or item.get("reviews") or item.get("numberOfReviews")
            hero_found[asin] = True
            hr = {}
            if rating: hr["rating"] = rating
            if reviews: hr["reviews"] = reviews
            result["hero_ratings"][asin] = hr

    niche_entry = {"label": label, "competitors": competitors}
    if hero_in_results:
        niche_entry["hero_in_results"] = hero_in_results

    result["niches"][nid] = niche_entry

    if i < len(NICHES) - 1:
        time.sleep(1.1)

# Note any heroes not found in any niche
for h in ALL_HEROES:
    if not hero_found[h]:
        result["notes"].append(f"Hero ASIN {h} not found in any niche results")

print("\n=== RESULT ===", flush=True)
print(json.dumps(result, indent=2))
