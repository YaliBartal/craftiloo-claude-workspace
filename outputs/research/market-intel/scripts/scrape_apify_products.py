"""
Apify Amazon Product Scraper
Scrapes hero products and competitor ASINs using saswave/amazon-product-scraper.
Batches of 5 ASINs max. Saves structured JSON output.
"""

import json
import os
import time
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

try:
    from dotenv import load_dotenv
except ImportError:
    print("Installing python-dotenv...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv", "-q"])
    from dotenv import load_dotenv

# ── Configuration ──────────────────────────────────────────────────────────

ENV_PATH = Path(r"c:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE\.env")
OUTPUT_DIR = Path(r"c:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE\outputs\research\market-intel\snapshots")
OUTPUT_FILE = OUTPUT_DIR / "apify-products-2026-02-23.json"

ACTOR_ID = "saswave~amazon-product-scraper"
BASE_URL = "https://api.apify.com/v2"
POLL_INTERVAL = 10  # seconds
BATCH_TIMEOUT = 120  # seconds
BATCH_DELAY = 2  # seconds between batches

# ── ASINs ──────────────────────────────────────────────────────────────────

HERO_ASINS = [
    "B08DDJCQKF", "B0F6YTG1CH", "B09X55KL2C", "B0DC69M3YD", "B09WQSBZY7",
    "B096MYBLS1", "B08FYH13CL", "B0F8R652FX", "B0F8DG32H5", "B09THLVFZK",
    "B07D6D95NG", "B0FQC7YFX6", "B09HVSLBS6",
]

COMPETITOR_ASINS = [
    "B08T5QC9FS", "B0B7JHN4F1", "B0CM9JKNCC", "B0DFHN42QB", "B087DYHMZ2",
    "B0D8171TF1", "B08TC7423N", "B0DP654CSV", "B0CZHKSSL4", "B0DMHY2HF3",
    "B0B762JW55", "B0C3ZVKB46", "B0BB9N74SG", "B091GXM2Y6", "B0C2XYP6L3",
    "B0CV1F5CFS", "B0CXY8JMTK", "B0CYNNT2ZT", "B0CTTMWXYP", "B06XRRN4VL",
    "B0CX9H8YGR", "B004JIFCXO", "B0B8W4FK4Q", "B0C5WQD914", "B0FN4CT867",
    "B08QV9CMFQ", "B0D5LF666P", "B00JM5G05I", "B0BRYRD91V", "B0D178S25M",
    "B0CWLTTZ2G",
]

ALL_HERO_SET = set(HERO_ASINS)

# ── Batch definitions (max 5 per batch) ────────────────────────────────────

def chunk_list(lst, size=5):
    """Split list into chunks of given size."""
    return [lst[i:i + size] for i in range(0, len(lst), size)]

HERO_BATCHES = chunk_list(HERO_ASINS, 5)
COMPETITOR_BATCHES = chunk_list(COMPETITOR_ASINS, 5)

ALL_BATCHES = []
for i, batch in enumerate(HERO_BATCHES):
    ALL_BATCHES.append({"label": f"Hero Batch {i+1}", "asins": batch, "type": "hero"})
for i, batch in enumerate(COMPETITOR_BATCHES):
    ALL_BATCHES.append({"label": f"Competitor Batch {i+1}", "asins": batch, "type": "competitor"})


# ── Helper functions ───────────────────────────────────────────────────────

def start_actor_run(api_token, asins):
    """Start an Apify actor run with given ASINs."""
    url = f"{BASE_URL}/acts/{ACTOR_ID}/runs?token={api_token}"
    payload = {
        "asins": asins,
        "amazon_domain": "www.amazon.com"
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()["data"]
    return data["id"], data.get("defaultDatasetId")


def poll_run_status(api_token, run_id, timeout=BATCH_TIMEOUT):
    """Poll until run completes or timeout. Returns (status, defaultDatasetId)."""
    url = f"{BASE_URL}/actor-runs/{run_id}?token={api_token}"
    start = time.time()
    while True:
        elapsed = time.time() - start
        if elapsed > timeout:
            return "TIMED_OUT", None
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()["data"]
        status = data.get("status")
        dataset_id = data.get("defaultDatasetId")
        if status in ("SUCCEEDED", "FAILED", "ABORTED"):
            return status, dataset_id
        time.sleep(POLL_INTERVAL)


def fetch_dataset_items(api_token, dataset_id):
    """Fetch all items from a dataset."""
    url = f"{BASE_URL}/datasets/{dataset_id}/items?token={api_token}"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return resp.json()


def extract_product_data(item):
    """Extract the fields we care about from an Apify result item."""
    return {
        "asin": item.get("asin", ""),
        "title": item.get("title", ""),
        "bestsellerRanks": item.get("bestsellerRanks", []),
        "stars": item.get("stars"),
        "reviewsCount": item.get("reviewsCount"),
        "price": item.get("price"),
        "availability": item.get("availability", ""),
    }


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    # Load API token
    load_dotenv(ENV_PATH)
    api_token = os.getenv("APIFY_API_TOKEN")
    if not api_token:
        print("ERROR: APIFY_API_TOKEN not found in .env")
        sys.exit(1)
    print(f"API token loaded: {api_token[:10]}...")

    start_time = datetime.now()
    results = {
        "date": "2026-02-23",
        "hero_products": {},
        "competitors": {},
        "failed_batches": [],
        "scrape_time": "",
    }

    total_batches = len(ALL_BATCHES)
    print(f"\n{'='*60}")
    print(f"  Apify Amazon Product Scraper")
    print(f"  {total_batches} batches | {len(HERO_ASINS)} hero + {len(COMPETITOR_ASINS)} competitor ASINs")
    print(f"{'='*60}\n")

    for idx, batch_info in enumerate(ALL_BATCHES):
        label = batch_info["label"]
        asins = batch_info["asins"]
        batch_type = batch_info["type"]

        print(f"[{idx+1}/{total_batches}] {label}: {', '.join(asins)}")

        try:
            # Start the run
            run_id, dataset_id = start_actor_run(api_token, asins)
            print(f"  -> Run started: {run_id}")

            # Poll for completion
            status, final_dataset_id = poll_run_status(api_token, run_id)
            dataset_id = final_dataset_id or dataset_id

            if status == "SUCCEEDED":
                # Fetch results
                items = fetch_dataset_items(api_token, dataset_id)
                print(f"  -> SUCCEEDED: {len(items)} products returned")

                for item in items:
                    product = extract_product_data(item)
                    asin = product["asin"]
                    if not asin:
                        continue
                    # Determine if hero or competitor based on the ASIN
                    if asin in ALL_HERO_SET:
                        results["hero_products"][asin] = product
                    else:
                        results["competitors"][asin] = product
            else:
                print(f"  -> {status}: batch failed")
                results["failed_batches"].append({
                    "label": label,
                    "asins": asins,
                    "status": status,
                    "run_id": run_id,
                })

        except Exception as e:
            print(f"  -> ERROR: {e}")
            results["failed_batches"].append({
                "label": label,
                "asins": asins,
                "status": "ERROR",
                "error": str(e),
            })

        # Wait between batches (skip after last)
        if idx < total_batches - 1:
            print(f"  -> Waiting {BATCH_DELAY}s before next batch...")
            time.sleep(BATCH_DELAY)

    # Calculate scrape time
    elapsed = datetime.now() - start_time
    results["scrape_time"] = str(elapsed)

    # Save output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {OUTPUT_FILE}")

    # ── Summary ────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  SCRAPE SUMMARY")
    print(f"{'='*60}")
    print(f"  Total hero products scraped:      {len(results['hero_products'])}/{len(HERO_ASINS)}")
    print(f"  Total competitors scraped:        {len(results['competitors'])}/{len(COMPETITOR_ASINS)}")
    print(f"  Failed batches:                   {len(results['failed_batches'])}")
    print(f"  Total time:                       {results['scrape_time']}")

    if results["failed_batches"]:
        print(f"\n  FAILED BATCHES:")
        for fb in results["failed_batches"]:
            print(f"    - {fb['label']}: {fb.get('status', 'UNKNOWN')} | ASINs: {', '.join(fb['asins'])}")

    # Hero product details
    print(f"\n{'='*60}")
    print(f"  HERO PRODUCT DETAILS")
    print(f"{'='*60}")
    print(f"  {'ASIN':<14} {'BSR':>8} {'Sub-Rank':>10} {'Reviews':>8} {'Rating':>7} {'Availability'}")
    print(f"  {'-'*14} {'-'*8} {'-'*10} {'-'*8} {'-'*7} {'-'*20}")

    for asin in HERO_ASINS:
        if asin in results["hero_products"]:
            p = results["hero_products"][asin]
            bsr = ""
            sub_rank = ""
            ranks = p.get("bestsellerRanks", [])
            if ranks:
                # First rank entry is typically the main category BSR
                bsr = str(ranks[0].get("rank", "")) if len(ranks) > 0 else ""
                sub_rank = str(ranks[1].get("rank", "")) if len(ranks) > 1 else ""
            reviews = str(p.get("reviewsCount", "")) if p.get("reviewsCount") is not None else ""
            stars = str(p.get("stars", "")) if p.get("stars") is not None else ""
            avail_raw = p.get("availability", "")
            if isinstance(avail_raw, bool):
                avail = "In Stock" if avail_raw else "Out of Stock"
            elif avail_raw:
                avail = str(avail_raw)[:30]
            else:
                avail = ""
            print(f"  {asin:<14} {bsr:>8} {sub_rank:>10} {reviews:>8} {stars:>7} {avail}")
        else:
            print(f"  {asin:<14} {'--- NOT SCRAPED ---':>50}")

    print(f"\nDone.")


if __name__ == "__main__":
    main()
