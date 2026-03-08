"""
Daily SP-API data fetch — 2026-03-08 run (yesterday = 2026-03-07).
Fetches: catalog (BSR), pricing, inventory, yesterday orders.
Output: compact JSON matching daily market intel format.
"""

import os
import time
import asyncio
import json
from pathlib import Path

import httpx

# ---- env ----
def _load_dotenv():
    for d in [Path(__file__).resolve().parent]:
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
            return

_load_dotenv()

BASE_URL = "https://sellingpartnerapi-na.amazon.com"
LWA_TOKEN_URL = "https://api.amazon.com/auth/o2/token"

_access_token = None
_token_expires_at = 0.0

HERO_ASINS = [
    "B08DDJCQKF", "B0F6YTG1CH", "B09X55KL2C", "B0DC69M3YD",
    "B09WQSBZY7", "B096MYBLS1", "B08FYH13CL", "B0F8R652FX",
    "B0F8DG32H5", "B09THLVFZK", "B07D6D95NG", "B0FQC7YFX6",
    "B09HVSLBS6"
]

async def _get_access_token(client: httpx.AsyncClient) -> str:
    global _access_token, _token_expires_at
    if _access_token and time.time() < _token_expires_at - 60:
        return _access_token
    cid = os.environ.get("SP_API_CLIENT_ID")
    csec = os.environ.get("SP_API_CLIENT_SECRET")
    rt = os.environ.get("SP_API_REFRESH_TOKEN")
    if not all([cid, csec, rt]):
        raise RuntimeError("SP_API credentials not set in .env")
    resp = await client.post(LWA_TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": rt,
        "client_id": cid,
        "client_secret": csec,
    })
    resp.raise_for_status()
    data = resp.json()
    _access_token = data["access_token"]
    _token_expires_at = time.time() + data.get("expires_in", 3600)
    return _access_token


async def _get(client: httpx.AsyncClient, path: str, params: dict = None) -> dict:
    token = await _get_access_token(client)
    headers = {"x-amz-access-token": token, "Content-Type": "application/json"}
    url = f"{BASE_URL}{path}"
    for attempt in range(3):
        resp = await client.get(url, headers=headers, params=params)
        if resp.status_code == 429:
            await asyncio.sleep(2)
            continue
        if resp.status_code != 200:
            return {"_error": f"HTTP {resp.status_code}: {resp.text[:300]}"}
        return resp.json()
    return {"_error": "Rate limited after 3 attempts"}


# ---- Phase A: Catalog (BSR) ----

async def fetch_catalog(client: httpx.AsyncClient, asin: str) -> dict:
    mp = os.environ.get("SP_API_MARKETPLACE_US", "ATVPDKIKX0DER")
    params = {
        "marketplaceIds": mp,
        "includedData": "salesRanks",
    }
    data = await _get(client, f"/catalog/2022-04-01/items/{asin}", params=params)
    if "_error" in data:
        return {"asin": asin, "error": data["_error"]}

    result = {"asin": asin}
    sales_ranks = data.get("salesRanks", [])
    if sales_ranks:
        sr = sales_ranks[0]
        display = sr.get("displayGroupRanks", [])
        classif = sr.get("classificationRanks", [])
        if display:
            result["bsr"] = display[0].get("rank")
            result["bsr_category"] = display[0].get("title")
        if classif:
            result["subcategory_rank"] = classif[0].get("rank")
            result["subcategory"] = classif[0].get("title")
    return result


# ---- Phase B: Pricing (serial) ----

async def fetch_pricing(client: httpx.AsyncClient, asin: str) -> dict:
    mp = os.environ.get("SP_API_MARKETPLACE_US", "ATVPDKIKX0DER")
    params = {"MarketplaceId": mp, "Asins": asin, "ItemType": "Asin"}
    data = await _get(client, "/products/pricing/v0/competitivePrice", params=params)
    if "_error" in data:
        return {"asin": asin, "price": None, "error": data["_error"]}

    try:
        items = data.get("payload", [])
        for item in items:
            if item.get("ASIN") == asin:
                comp_prices = item.get("Product", {}).get("CompetitivePricing", {}).get("CompetitivePrices", [])
                for cp in comp_prices:
                    if cp.get("condition") == "New":
                        amount = cp.get("Price", {}).get("LandedPrice", {}).get("Amount")
                        return {"asin": asin, "price": amount}
                if comp_prices:
                    amount = comp_prices[0].get("Price", {}).get("LandedPrice", {}).get("Amount")
                    return {"asin": asin, "price": amount}
        return {"asin": asin, "price": None}
    except Exception as e:
        return {"asin": asin, "price": None, "error": str(e)}


# ---- Phase C: Inventory ----

async def fetch_inventory(client: httpx.AsyncClient) -> dict:
    asin_str = ",".join(HERO_ASINS)
    params = {
        "granularityType": "Marketplace",
        "granularityId": os.environ.get("SP_API_MARKETPLACE_US", "ATVPDKIKX0DER"),
        "asinFilter": asin_str,
    }
    data = await _get(client, "/fba/inventory/v1/summaries", params=params)
    if "_error" in data:
        return {"error": data["_error"]}

    result = {}
    summaries = data.get("payload", {}).get("inventorySummaries", [])
    for s in summaries:
        asin = s.get("asin")
        total = s.get("totalQuantity", 0)
        if asin:
            result[asin] = total
    for a in HERO_ASINS:
        if a not in result:
            result[a] = 0
    return result


# ---- Phase D: Orders (yesterday = 2026-03-07) ----

async def fetch_orders(client: httpx.AsyncClient) -> dict:
    mp = os.environ.get("SP_API_MARKETPLACE_US", "ATVPDKIKX0DER")
    created_after = "2026-03-07T00:00:00Z"
    created_before = "2026-03-08T00:00:00Z"
    params = {
        "MarketplaceIds": mp,
        "CreatedAfter": created_after,
        "CreatedBefore": created_before,
        "OrderStatuses": "Shipped,Unshipped,PartiallyShipped,Pending",
    }
    data = await _get(client, "/orders/v0/orders", params=params)
    if "_error" in data:
        return {"error": data["_error"]}

    orders = data.get("payload", {}).get("Orders", [])
    total_orders = len(orders)
    total_units = 0
    shipped_revenue = 0.0

    for order in orders:
        num_items = order.get("NumberOfItemsShipped", 0) + order.get("NumberOfItemsUnshipped", 0)
        total_units += num_items
        status = order.get("OrderStatus", "")
        if status in ("Shipped", "PartiallyShipped"):
            amt = order.get("OrderTotal", {}).get("Amount")
            if amt:
                try:
                    shipped_revenue += float(amt)
                except (ValueError, TypeError):
                    pass

    next_token = data.get("payload", {}).get("NextToken")
    page = 1
    while next_token and page < 10:
        page += 1
        await asyncio.sleep(0.5)
        page_data = await _get(client, "/orders/v0/orders", {"NextToken": next_token})
        if "_error" in page_data:
            break
        more_orders = page_data.get("payload", {}).get("Orders", [])
        total_orders += len(more_orders)
        for order in more_orders:
            num_items = order.get("NumberOfItemsShipped", 0) + order.get("NumberOfItemsUnshipped", 0)
            total_units += num_items
            status = order.get("OrderStatus", "")
            if status in ("Shipped", "PartiallyShipped"):
                amt = order.get("OrderTotal", {}).get("Amount")
                if amt:
                    try:
                        shipped_revenue += float(amt)
                    except (ValueError, TypeError):
                        pass
        next_token = page_data.get("payload", {}).get("NextToken")

    return {
        "total_orders": total_orders,
        "total_units": total_units,
        "shipped_revenue_incl_tax": round(shipped_revenue, 2),
    }


# ---- Main ----

async def main():
    errors = []
    catalog_out = {}
    pricing_out = {}
    inventory_out = {}
    orders_out = {}

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Phase A: Catalog — all in parallel
        catalog_tasks = [fetch_catalog(client, asin) for asin in HERO_ASINS]
        catalog_results = await asyncio.gather(*catalog_tasks, return_exceptions=True)

        for r in catalog_results:
            if isinstance(r, Exception):
                errors.append(f"Catalog exception: {r}")
                continue
            asin = r.get("asin")
            if r.get("error"):
                errors.append(f"Catalog {asin}: {r['error']}")
            else:
                entry = {}
                if r.get("bsr") is not None:
                    entry["bsr"] = r["bsr"]
                if r.get("bsr_category"):
                    entry["bsr_category"] = r["bsr_category"]
                if r.get("subcategory_rank") is not None:
                    entry["subcat_rank"] = r["subcategory_rank"]
                if r.get("subcategory"):
                    entry["subcat"] = r["subcategory"]
                catalog_out[asin] = entry

        # Phase B: Pricing — serial with delay
        for asin in HERO_ASINS:
            result = await fetch_pricing(client, asin)
            pricing_out[asin] = result.get("price")
            if result.get("error"):
                errors.append(f"Pricing {asin}: {result['error']}")
            await asyncio.sleep(0.6)

        # Phase C: Inventory
        inventory = await fetch_inventory(client)
        if "error" in inventory:
            errors.append(f"Inventory: {inventory['error']}")
        else:
            inventory_out = inventory

        # Phase D: Orders
        orders = await fetch_orders(client)
        if "error" in orders:
            errors.append(f"Orders: {orders['error']}")
        else:
            orders_out = orders

    output = {
        "catalog": catalog_out,
        "pricing": pricing_out,
        "inventory": inventory_out,
        "orders_yesterday": {
            "date": "2026-03-07",
            **orders_out
        },
        "notes": errors
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
