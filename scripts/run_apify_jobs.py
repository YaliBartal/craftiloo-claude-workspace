"""
Daily Market Intel - Parallel Apify Job Launcher (Job 4A + 4B)
Launches 20 keyword scans + 1 BSR scan concurrently, polls until done, outputs JSON.
"""

import json
import time
import urllib.request
import urllib.error
import sys

APIFY_TOKEN = "YOUR_APIFY_TOKEN_HERE"
BASE_URL = "https://api.apify.com/v2"

KEYWORDS = [
    "embroidery kit for kids",
    "cross stitch kits for kids",
    "cross stitch for kids",
    "kids embroidery kit",
    "embroidery kit for beginners",
    "sewing kit for kids",
    "kids sewing kit",
    "latch hook kits for kids",
    "latch hook pillow kit",
    "mini perler beads",
    "perler beads",
    "mini fuse beads",
    "loom knitting kit",
    "loom knitting",
    "knitting kit for kids",
    "knitting kit for beginners",
    "lacing cards",
    "lacing cards for kids ages 3-5",
    "lacing cards for kids ages 4-8",
    "needlepoint kits for kids",
]

BSR_ASINS = [
    "B08T5QC9FS","B0B7JHN4F1","B0CM9JKNCC","B0DFHN42QB","B087DYHMZ2",
    "B0D8171TF1","B08TC7423N","B0DP654CSV","B0CZHKSSL4","B0DMHY2HF3",
    "B0BB9N74SG","B0B762JW55","B0C3ZVKB46","B091GXM2Y6","B0C2XYP6L3",
    "B0CXY8JMTK","B0CTTMWXYP","B06XRRN4VL","B0CX9H8YGR","B07PPD8Q8V",
    "B004JIFCXO","B0B8W4FK4Q","B0DS23C1YX","B0182IQHYE","B0C5WQD914",
    "B0FN4CT867","B08QV9CMFQ","B0D5LF666P","B00JM5G05I","B0BRYRD91V",
    "B0D178S25M","B0CG9FN2CH","B0CWLTTZ2G","B0DJQPGDMQ"
]

HERO_ASINS = {
    "B08DDJCQKF","B0F6YTG1CH","B09X55KL2C","B0DC69M3YD","B09WQSBZY7",
    "B096MYBLS1","B08FYH13CL","B0F8R652FX","B0F8DG32H5","B09THLVFZK",
    "B07D6D95NG","B0FQC7YFX6","B09HVSLBS6"
}

TRACKED_COMPETITOR_ASINS = {
    "B08T5QC9FS","B0B7JHN4F1","B0CM9JKNCC","B0DFHN42QB","B087DYHMZ2",
    "B0D8171TF1","B08TC7423N","B0DP654CSV","B0CZHKSSL4","B0DMHY2HF3",
    "B0BB9N74SG","B0B762JW55","B0C3ZVKB46","B091GXM2Y6","B0C2XYP6L3",
    "B0CXY8JMTK","B0CTTMWXYP","B06XRRN4VL","B0CX9H8YGR","B07PPD8Q8V",
    "B004JIFCXO","B0B8W4FK4Q","B0DS23C1YX","B0182IQHYE","B0C5WQD914",
    "B0FN4CT867","B08QV9CMFQ","B0D5LF666P","B00JM5G05I","B0BRYRD91V",
    "B0D178S25M","B0CG9FN2CH","B0CWLTTZ2G","B0DJQPGDMQ",
    "B0CV1F5CFS","B0CYNNT2ZT"
}

KEYWORD_HERO_MAP = {
    "embroidery kit for kids": {"heroes": ["B08DDJCQKF","B0F6YTG1CH","B09X55KL2C"], "competitors": ["B08T5QC9FS","B0B7JHN4F1","B0CM9JKNCC","B0DFHN42QB"]},
    "cross stitch kits for kids": {"heroes": ["B08DDJCQKF","B0F6YTG1CH"], "competitors": ["B08T5QC9FS","B0B7JHN4F1","B0CM9JKNCC"]},
    "cross stitch for kids": {"heroes": ["B08DDJCQKF","B0F6YTG1CH"], "competitors": ["B08T5QC9FS","B0B7JHN4F1","B0CM9JKNCC"]},
    "kids embroidery kit": {"heroes": ["B09X55KL2C"], "competitors": ["B087DYHMZ2","B0D8171TF1","B08TC7423N","B0DP654CSV"]},
    "embroidery kit for beginners": {"heroes": ["B0DC69M3YD"], "competitors": ["B0CZHKSSL4","B0DMHY2HF3","B0BB9N74SG","B0B762JW55","B0C3ZVKB46"]},
    "sewing kit for kids": {"heroes": ["B09WQSBZY7","B096MYBLS1"], "competitors": ["B091GXM2Y6","B0C2XYP6L3","B0CV1F5CFS","B0CXY8JMTK","B0CYNNT2ZT","B0CTTMWXYP"]},
    "kids sewing kit": {"heroes": ["B09WQSBZY7","B096MYBLS1"], "competitors": ["B091GXM2Y6","B0CXY8JMTK","B0CTTMWXYP"]},
    "latch hook kits for kids": {"heroes": ["B08FYH13CL","B0F8R652FX"], "competitors": ["B06XRRN4VL","B0CX9H8YGR","B07PPD8Q8V","B0DJQPGDMQ"]},
    "latch hook pillow kit": {"heroes": ["B0F8R652FX"], "competitors": ["B06XRRN4VL","B0CX9H8YGR"]},
    "mini perler beads": {"heroes": ["B09THLVFZK","B07D6D95NG"], "competitors": ["B0C5WQD914","B0FN4CT867","B08QV9CMFQ","B0D5LF666P"]},
    "perler beads": {"heroes": ["B09THLVFZK","B07D6D95NG"], "competitors": ["B0C5WQD914","B08QV9CMFQ","B0D5LF666P"]},
    "mini fuse beads": {"heroes": ["B09THLVFZK"], "competitors": ["B0C5WQD914","B08QV9CMFQ","B0D5LF666P"]},
    "loom knitting kit": {"heroes": ["B0F8DG32H5"], "competitors": ["B004JIFCXO","B0B8W4FK4Q","B0DS23C1YX"]},
    "loom knitting": {"heroes": ["B0F8DG32H5"], "competitors": ["B0DS23C1YX","B0182IQHYE"]},
    "knitting kit for kids": {"heroes": ["B0F8DG32H5"], "competitors": ["B0B8W4FK4Q","B004JIFCXO"]},
    "knitting kit for beginners": {"heroes": ["B0F8DG32H5"], "competitors": ["B0DS23C1YX","B0B8W4FK4Q"]},
    "lacing cards": {"heroes": ["B0FQC7YFX6"], "competitors": ["B00JM5G05I","B0BRYRD91V","B0D178S25M"]},
    "lacing cards for kids ages 3-5": {"heroes": ["B0FQC7YFX6"], "competitors": ["B00JM5G05I","B0BRYRD91V","B0D178S25M"]},
    "lacing cards for kids ages 4-8": {"heroes": ["B0FQC7YFX6"], "competitors": ["B00JM5G05I","B0BRYRD91V"]},
    "needlepoint kits for kids": {"heroes": ["B09HVSLBS6"], "competitors": ["B0CG9FN2CH"]},
}

CATEGORY_MAP = {
    "embroidery kit for kids": "Cross Stitch / Embroidery Kids",
    "cross stitch kits for kids": "Cross Stitch / Embroidery Kids",
    "cross stitch for kids": "Cross Stitch / Embroidery Kids",
    "kids embroidery kit": "Cross Stitch / Embroidery Kids",
    "embroidery kit for beginners": "Cross Stitch / Embroidery Beginners",
    "sewing kit for kids": "Sewing Kids",
    "kids sewing kit": "Sewing Kids",
    "latch hook kits for kids": "Latch Hook Kids",
    "latch hook pillow kit": "Latch Hook Pillow",
    "mini perler beads": "Perler / Fuse Beads",
    "perler beads": "Perler / Fuse Beads",
    "mini fuse beads": "Perler / Fuse Beads",
    "loom knitting kit": "Loom Knitting",
    "loom knitting": "Loom Knitting",
    "knitting kit for kids": "Loom Knitting Kids",
    "knitting kit for beginners": "Loom Knitting Beginners",
    "lacing cards": "Lacing Cards",
    "lacing cards for kids ages 3-5": "Lacing Cards",
    "lacing cards for kids ages 4-8": "Lacing Cards",
    "needlepoint kits for kids": "Needlepoint Kids",
}


def apify_post(path, body):
    url = f"{BASE_URL}{path}?token={APIFY_TOKEN}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def apify_get(path):
    url = f"{BASE_URL}{path}?token={APIFY_TOKEN}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def launch_keyword_run(keyword):
    body = {"input": [{"keyword": keyword, "country": "US"}]}
    resp = apify_post("/acts/axesso_data~amazon-search-scraper/runs", body)
    run_id = resp["data"]["id"]
    dataset_id = resp["data"]["defaultDatasetId"]
    return run_id, dataset_id


def launch_bsr_run():
    body = {"asins": BSR_ASINS, "amazon_domain": "www.amazon.com"}
    resp = apify_post("/acts/saswave~amazon-product-scraper/runs", body)
    run_id = resp["data"]["id"]
    dataset_id = resp["data"]["defaultDatasetId"]
    return run_id, dataset_id


def get_run_status(run_id):
    resp = apify_get(f"/actor-runs/{run_id}")
    return resp["data"]["status"]


def get_dataset_items(dataset_id):
    url = f"{BASE_URL}/datasets/{dataset_id}/items?token={APIFY_TOKEN}&limit=200"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = json.loads(resp.read())
    # Apify returns items as a list directly or nested
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return raw.get("items", raw.get("data", []))
    return []


def poll_all(runs, max_wait=600, interval=15):
    statuses = {r: "RUNNING" for r in runs}
    elapsed = 0
    while elapsed < max_wait:
        pending = [r for r, s in statuses.items() if s not in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT")]
        if not pending:
            break
        for run_id in pending:
            try:
                s = get_run_status(run_id)
                statuses[run_id] = s
            except Exception as e:
                pass  # keep as RUNNING, retry next cycle
        still_pending = [r for r, s in statuses.items() if s not in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT")]
        done_count = len(runs) - len(still_pending)
        print(f"  [poll +{elapsed}s] {done_count}/{len(runs)} done, {len(still_pending)} pending", flush=True)
        if not still_pending:
            break
        time.sleep(interval)
        elapsed += interval
    return statuses


def extract_brand(item):
    for field in ("brand", "brandName", "sellerName", "manufacturer"):
        v = item.get(field)
        if v and isinstance(v, str) and v.strip():
            return v.strip()
    return "unknown"


def extract_badge(item):
    # Check common badge fields
    for field in ("badgeName", "productBadge", "amazonBadge", "badge", "badgeText"):
        v = item.get(field)
        if v and isinstance(v, str) and v.strip() and v.lower() not in ("false","none",""):
            return v.strip()
    # Boolean flags
    if item.get("isBestSeller") or item.get("bestSeller"):
        return "Best Seller"
    if item.get("amazonChoice") or item.get("isAmazonChoice"):
        return "Amazon's Choice"
    if item.get("overallPick") or item.get("isOverallPick"):
        return "Overall Pick"
    return None


def process_keyword_results(keyword, items):
    positions = []
    badges_found = []
    new_competitors = []

    lookup = KEYWORD_HERO_MAP.get(keyword, {"heroes": [], "competitors": []})
    tracked_heroes = set(lookup["heroes"])
    tracked_competitors = set(lookup["competitors"])
    all_tracked = tracked_heroes | tracked_competitors | HERO_ASINS

    top5_unknown = []

    for item in items:
        asin = (item.get("asin") or item.get("productAsin") or item.get("ASIN") or "").strip()
        if not asin:
            continue

        pos_raw = item.get("searchResultPosition")
        if pos_raw is None:
            pos_raw = item.get("position", 9999)
        try:
            pos = int(pos_raw) + 1  # 0-indexed to 1-indexed
        except (ValueError, TypeError):
            pos = 9999

        brand = extract_brand(item)
        badge = extract_badge(item)
        is_hero = asin in HERO_ASINS

        if asin in all_tracked:
            entry = {"asin": asin, "brand": brand, "position": pos, "is_hero": is_hero}
            if badge:
                entry["badge"] = badge
            positions.append(entry)
            if badge:
                badges_found.append({"asin": asin, "keyword": keyword, "badge": badge})
        elif pos <= 5 and asin not in TRACKED_COMPETITOR_ASINS and asin not in HERO_ASINS:
            top5_unknown.append({"asin": asin, "brand": brand, "keyword": keyword, "position": pos})

    positions.sort(key=lambda x: x["position"])
    new_competitors = top5_unknown[:5]
    return positions, badges_found, new_competitors


def process_bsr_results(items):
    result = {}
    for item in items:
        asin = (item.get("asin") or item.get("ASIN") or "").strip()
        if not asin:
            continue

        # BSR extraction
        bsr = None
        bsr_raw = item.get("bsr") or item.get("bestSellerRank") or item.get("salesRank") or item.get("rankingInCategory")
        if isinstance(bsr_raw, int):
            bsr = bsr_raw
        elif isinstance(bsr_raw, list) and bsr_raw:
            first = bsr_raw[0]
            if isinstance(first, dict):
                bsr = first.get("rank") or first.get("value") or first.get("Rank")
            elif isinstance(first, int):
                bsr = first
        elif isinstance(bsr_raw, str) and bsr_raw:
            try:
                bsr = int(bsr_raw.replace(",","").split()[0].replace("#",""))
            except:
                pass

        # Rating
        rating = None
        for field in ("rating", "stars", "productRating", "averageRating"):
            v = item.get(field)
            if v is not None:
                try:
                    rating = float(str(v).split()[0])
                    break
                except:
                    pass

        # Reviews
        reviews = None
        for field in ("reviews", "countReview", "reviewCount", "ratingsTotal", "numberOfRatings"):
            v = item.get(field)
            if v is not None:
                try:
                    reviews = int(str(v).replace(",","").split()[0])
                    break
                except:
                    pass

        result[asin] = {"bsr": bsr, "rating": rating, "reviews": reviews}
    return result


def main():
    notes = []

    # --- Launch phase ---
    print("=== Launching 20 keyword runs (Job 4A) ===", flush=True)
    keyword_runs = {}
    for kw in KEYWORDS:
        try:
            run_id, ds_id = launch_keyword_run(kw)
            keyword_runs[kw] = (run_id, ds_id)
            print(f"  OK: {kw[:45]!r} -> {run_id}", flush=True)
            time.sleep(0.3)
        except Exception as e:
            notes.append(f"Launch failed for keyword '{kw}': {e}")
            print(f"  FAIL: {kw}: {e}", flush=True)

    print("\n=== Launching BSR scan (Job 4B) ===", flush=True)
    bsr_run_id = None
    bsr_ds_id = None
    try:
        bsr_run_id, bsr_ds_id = launch_bsr_run()
        print(f"  OK: BSR scan -> {bsr_run_id}", flush=True)
    except Exception as e:
        notes.append(f"BSR run launch failed: {e}")
        print(f"  FAIL: BSR: {e}", flush=True)

    # --- Collect all run IDs for polling ---
    all_run_ids = [v[0] for v in keyword_runs.values()]
    if bsr_run_id:
        all_run_ids.append(bsr_run_id)

    print(f"\n=== Polling {len(all_run_ids)} runs (15s intervals, max 10min) ===", flush=True)
    statuses = poll_all(all_run_ids, max_wait=600, interval=15)
    print("All runs resolved.", flush=True)

    # --- Process keyword results ---
    all_keyword_battleground = []
    all_badges = []
    all_new_competitors = []
    keywords_with_data = 0

    for kw in KEYWORDS:
        if kw not in keyword_runs:
            notes.append(f"No run for: {kw}")
            all_keyword_battleground.append({"keyword": kw, "category": CATEGORY_MAP.get(kw, ""), "positions": [], "data_status": "no_run"})
            continue

        run_id, ds_id = keyword_runs[kw]
        status = statuses.get(run_id, "UNKNOWN")

        if status != "SUCCEEDED":
            notes.append(f"Keyword '{kw}' run status: {status}")
            all_keyword_battleground.append({"keyword": kw, "category": CATEGORY_MAP.get(kw, ""), "positions": [], "data_status": status.lower()})
            continue

        try:
            items = get_dataset_items(ds_id)
            if not items:
                notes.append(f"Empty results for: {kw}")
                all_keyword_battleground.append({"keyword": kw, "category": CATEGORY_MAP.get(kw, ""), "positions": [], "data_status": "empty"})
                continue

            positions, badges, new_comps = process_keyword_results(kw, items)
            keywords_with_data += 1
            all_keyword_battleground.append({
                "keyword": kw,
                "category": CATEGORY_MAP.get(kw, ""),
                "positions": positions,
                "data_status": "live"
            })
            all_badges.extend(badges)
            all_new_competitors.extend(new_comps)

        except Exception as e:
            notes.append(f"Processing error for '{kw}': {e}")
            all_keyword_battleground.append({"keyword": kw, "category": CATEGORY_MAP.get(kw, ""), "positions": [], "data_status": "error"})

    # --- Process BSR results ---
    competitor_bsr = {}
    bsr_asins_returned = 0

    if bsr_run_id:
        bsr_status = statuses.get(bsr_run_id, "UNKNOWN")
        if bsr_status == "SUCCEEDED":
            try:
                bsr_items = get_dataset_items(bsr_ds_id)
                competitor_bsr = process_bsr_results(bsr_items)
                bsr_asins_returned = len(competitor_bsr)
            except Exception as e:
                notes.append(f"BSR processing error: {e}")
        else:
            notes.append(f"BSR run status: {bsr_status}")

    # --- Deduplicate new competitors ---
    seen_nc = set()
    unique_new_competitors = []
    for nc in all_new_competitors:
        key = (nc["asin"], nc["keyword"])
        if key not in seen_nc:
            seen_nc.add(key)
            unique_new_competitors.append(nc)

    # --- Build final output ---
    output = {
        "keyword_battleground": all_keyword_battleground,
        "badges_found": all_badges,
        "new_competitors": unique_new_competitors,
        "competitor_bsr": competitor_bsr,
        "scan_summary": {
            "keywords_returned_data": keywords_with_data,
            "keywords_total": len(KEYWORDS),
            "bsr_asins_returned": bsr_asins_returned,
            "bsr_asins_total": len(BSR_ASINS),
        },
        "notes": notes
    }

    print("\n=== OUTPUT_JSON_START ===")
    print(json.dumps(output, indent=2))
    print("=== OUTPUT_JSON_END ===")


if __name__ == "__main__":
    main()
