"""
Standalone SP-API data collector for 13 hero ASINs.
Collects BSR, pricing, FBA inventory, and yesterday's orders.
Returns a single JSON object.
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

import httpx

# ── Load .env ────────────────────────────────────────────────────────────────
for d in [Path.cwd(), Path(__file__).resolve().parent.parent]:
    env_file = d / ".env"
    if env_file.exists():
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    if key and not os.environ.get(key):
                        os.environ[key] = value
        break

# ── Constants ─────────────────────────────────────────────────────────────────
BASE_URL = "https://sellingpartnerapi-na.amazon.com"
LWA_TOKEN_URL = "https://api.amazon.com/auth/o2/token"
MARKETPLACE_US = os.environ.get("SP_API_MARKETPLACE_US", "ATVPDKIKX0DER")

HERO_ASINS = [
    "B08DDJCQKF", "B0F6YTG1CH", "B09X55KL2C", "B0DC69M3YD",
    "B09WQSBZY7", "B096MYBLS1", "B08FYH13CL", "B0F8R652FX",
    "B0F8DG32H5", "B09THLVFZK", "B07D6D95NG", "B0FQC7YFX6",
    "B09HVSLBS6",
]

_access_token = None
_token_expires_at = 0.0


# ── Auth ──────────────────────────────────────────────────────────────────────
async def get_token(client: httpx.AsyncClient) -> str:
    global _access_token, _token_expires_at
    if _access_token and time.time() < _token_expires_at - 60:
        return _access_token

    resp = await client.post(LWA_TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": os.environ["SP_API_REFRESH_TOKEN"],
        "client_id": os.environ["SP_API_CLIENT_ID"],
        "client_secret": os.environ["SP_API_CLIENT_SECRET"],
    }, timeout=15.0)
    resp.raise_for_status()
    data = resp.json()
    _access_token = data["access_token"]
    _token_expires_at = time.time() + data.get("expires_in", 3600)
    return _access_token


async def sp_get(client: httpx.AsyncClient, path: str, params: dict = None) -> dict | str:
    token = await get_token(client)
    headers = {"x-amz-access-token": token, "Content-Type": "application/json"}
    resp = await client.get(f"{BASE_URL}{path}", headers=headers, params=params or {}, timeout=30.0)
    if resp.status_code == 429:
        return "429"
    if resp.status_code != 200:
        return f"ERR:{resp.status_code}:{resp.text[:200]}"
    return resp.json()


# ── STEP 1: Catalog (BSR) ──────────────────────────────────────────────────────
async def fetch_catalog_item(client: httpx.AsyncClient, asin: str) -> dict:
    params = {
        "marketplaceIds": MARKETPLACE_US,
        "includedData": "salesRanks",
    }
    data = await sp_get(client, f"/catalog/2022-04-01/items/{asin}", params=params)
    result = {"asin": asin, "bsr": None, "bsr_category": "", "subcategory_rank": None, "subcategory": ""}
    if isinstance(data, str):
        result["catalog_error"] = data
        return result

    try:
        ranks = data.get("salesRanks", [])
        if ranks:
            display = ranks[0].get("displayGroupRanks", [])
            if display:
                result["bsr"] = display[0].get("rank")
                result["bsr_category"] = display[0].get("title", "")
            classif = ranks[0].get("classificationRanks", [])
            if classif:
                result["subcategory_rank"] = classif[0].get("rank")
                result["subcategory"] = classif[0].get("title", "")
    except Exception as e:
        result["catalog_error"] = str(e)
    return result


# ── STEP 2: Pricing (serialized) ───────────────────────────────────────────────
async def fetch_pricing(client: httpx.AsyncClient, asin: str) -> dict:
    params = {
        "MarketplaceId": MARKETPLACE_US,
        "Asins": asin,
        "ItemType": "Asin",
    }
    data = await sp_get(client, "/products/pricing/v0/competitivePrice", params=params)
    result = {"asin": asin, "price": None}

    if data == "429":
        await asyncio.sleep(2)
        data = await sp_get(client, "/products/pricing/v0/competitivePrice", params=params)

    if isinstance(data, str):
        result["pricing_error"] = data
        return result

    try:
        payload = data.get("payload", [])
        for item in payload:
            if item.get("ASIN") == asin:
                cp = item.get("Product", {}).get("CompetitivePricing", {})
                prices = cp.get("CompetitivePrices", [])
                for p in prices:
                    if p.get("condition") == "New":
                        result["price"] = p.get("Price", {}).get("LandedPrice", {}).get("Amount")
                        break
                if result["price"] is None and prices:
                    # Try first price if no "New" match
                    result["price"] = prices[0].get("Price", {}).get("LandedPrice", {}).get("Amount")
    except Exception as e:
        result["pricing_error"] = str(e)
    return result


# ── STEP 3: FBA Inventory ──────────────────────────────────────────────────────
async def fetch_fba_inventory(client: httpx.AsyncClient) -> dict:
    params = {
        "details": "true",
        "granularityType": "Marketplace",
        "granularityId": MARKETPLACE_US,
        "marketplaceIds": MARKETPLACE_US,
    }
    asin_set = set(HERO_ASINS)
    asin_totals = {}
    pages = 0

    while pages < 20:
        data = await sp_get(client, "/fba/inventory/v1/summaries", params=params)
        if isinstance(data, str):
            return {"error": data}
        summaries = data.get("payload", {}).get("inventorySummaries", [])
        for s in summaries:
            asin = s.get("asin", "")
            if asin not in asin_set:
                continue
            qty = s.get("totalQuantity", 0)
            if asin not in asin_totals:
                asin_totals[asin] = 0
            asin_totals[asin] += qty
        pages += 1
        next_token = data.get("pagination", {}).get("nextToken")
        if not next_token:
            break
        params = {
            "details": "true",
            "granularityType": "Marketplace",
            "granularityId": MARKETPLACE_US,
            "marketplaceIds": MARKETPLACE_US,
            "nextToken": next_token,
        }

    # Fill missing ASINs with 0
    for asin in HERO_ASINS:
        if asin not in asin_totals:
            asin_totals[asin] = 0

    return asin_totals


# ── STEP 4: Orders (yesterday) ─────────────────────────────────────────────────
async def fetch_orders_yesterday(client: httpx.AsyncClient) -> dict:
    date = "2026-02-28"
    params = {
        "MarketplaceIds": MARKETPLACE_US,
        "CreatedAfter": f"{date}T00:00:00Z",
        "CreatedBefore": f"{date}T23:59:59Z",
        "MaxResultsPerPage": 100,
    }
    all_orders = []
    pages = 0
    while pages < 10:
        data = await sp_get(client, "/orders/v0/orders", params=params)
        if isinstance(data, str):
            return {"error": data}
        payload = data.get("payload", {})
        orders = payload.get("Orders", [])
        all_orders.extend(orders)
        pages += 1
        next_token = payload.get("NextToken")
        if not next_token:
            break
        params = {
            "MarketplaceIds": MARKETPLACE_US,
            "NextToken": next_token,
        }

    shipped = [o for o in all_orders if o.get("OrderStatus") == "Shipped"]
    pending = [o for o in all_orders if o.get("OrderStatus") == "Pending"]
    canceled = [o for o in all_orders if o.get("OrderStatus") == "Canceled"]

    total_units = sum(
        o.get("NumberOfItemsShipped", 0) + o.get("NumberOfItemsUnshipped", 0)
        for o in all_orders
    )
    shipped_revenue = 0.0
    for o in shipped:
        tot = o.get("OrderTotal", {})
        try:
            shipped_revenue += float(tot.get("Amount", 0))
        except (ValueError, TypeError):
            pass

    return {
        "date": date,
        "total_orders": len(all_orders),
        "total_units": total_units,
        "shipped_orders": len(shipped),
        "pending_orders": len(pending),
        "canceled_orders": len(canceled),
        "shipped_revenue_incl_tax": round(shipped_revenue, 2),
    }


# ── MAIN ───────────────────────────────────────────────────────────────────────
async def main():
    async with httpx.AsyncClient() as client:
        # STEP 1: Catalog — parallel
        catalog_tasks = [fetch_catalog_item(client, asin) for asin in HERO_ASINS]
        catalog_results = await asyncio.gather(*catalog_tasks)
        catalog_map = {r["asin"]: r for r in catalog_results}

        # STEP 2: Pricing — serialized, 0.5s apart
        pricing_map = {}
        for asin in HERO_ASINS:
            pr = await fetch_pricing(client, asin)
            pricing_map[asin] = pr
            await asyncio.sleep(0.5)

        # STEP 3: FBA Inventory
        inventory = await fetch_fba_inventory(client)

        # STEP 4: Orders yesterday
        orders = await fetch_orders_yesterday(client)

    # ── Assemble output ────────────────────────────────────────────────────────
    hero_products = {}
    oos_alerts = []
    low_stock_alerts = []
    pricing_errors = []

    for asin in HERO_ASINS:
        cat = catalog_map.get(asin, {})
        pri = pricing_map.get(asin, {})
        stock = inventory.get(asin, 0) if not isinstance(inventory, dict) or "error" not in inventory else 0
        if isinstance(inventory, dict) and "error" not in inventory:
            stock = inventory.get(asin, 0)

        price = pri.get("price")
        if pri.get("pricing_error"):
            pricing_errors.append(asin)

        hero_products[asin] = {
            "bsr": cat.get("bsr"),
            "bsr_category": cat.get("bsr_category", ""),
            "subcategory_rank": cat.get("subcategory_rank"),
            "subcategory": cat.get("subcategory", ""),
            "price": price,
            "stock": stock,
        }

        if stock == 0:
            oos_alerts.append(asin)
        elif stock < 30:
            low_stock_alerts.append(asin)

    output = {
        "hero_products": hero_products,
        "oos_alerts": oos_alerts,
        "low_stock_alerts": low_stock_alerts,
        "pricing_errors": pricing_errors,
        "orders_yesterday": orders,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
