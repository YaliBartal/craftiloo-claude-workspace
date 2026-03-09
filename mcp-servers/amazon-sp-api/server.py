"""
Amazon SP-API MCP Server
Exposes Amazon Selling Partner API endpoints as MCP tools.
Auth: LWA OAuth2 (Client ID + Client Secret + Refresh Token).
No AWS credentials required.

Base URL: https://sellingpartnerapi-na.amazon.com
"""

import os
import time
import asyncio
import gzip
import json
from datetime import datetime, timedelta
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import httpx


def _load_dotenv():
    """Load .env file from workspace root as fallback if env vars aren't set."""
    for d in [Path.cwd(), Path(__file__).resolve().parent.parent.parent]:
        env_file = d / ".env"
        if env_file.exists():
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip()
                        current = os.environ.get(key, "")
                        if key and (not current or current.startswith("${")):
                            os.environ[key] = value
            return


_load_dotenv()

mcp = FastMCP("amazon-sp-api")

# --- Constants ---

BASE_URL = "https://sellingpartnerapi-na.amazon.com"
LWA_TOKEN_URL = "https://api.amazon.com/auth/o2/token"
RATE_LIMIT_DELAY = 0.5  # seconds between requests (conservative)

_last_request_time = 0.0
_rate_lock = asyncio.Lock()

# Token cache
_access_token = None
_token_expires_at = 0.0


# --- Auth ---

async def _get_access_token() -> str:
    """Get a valid access token, refreshing if expired."""
    global _access_token, _token_expires_at

    if _access_token and time.time() < _token_expires_at - 60:
        return _access_token

    client_id = os.environ.get("SP_API_CLIENT_ID")
    client_secret = os.environ.get("SP_API_CLIENT_SECRET")
    refresh_token = os.environ.get("SP_API_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        return None

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(LWA_TOKEN_URL, data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        })

    if resp.status_code != 200:
        _access_token = None
        return None

    data = resp.json()
    _access_token = data["access_token"]
    _token_expires_at = time.time() + data.get("expires_in", 3600)
    return _access_token


# --- Helpers ---

async def _rate_limit():
    """Enforce rate limiting between requests."""
    global _last_request_time
    async with _rate_lock:
        now = time.time()
        elapsed = now - _last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            await asyncio.sleep(RATE_LIMIT_DELAY - elapsed)
        _last_request_time = time.time()


def _marketplace_id(marketplace: str = "US") -> str:
    """Get marketplace ID from env or default."""
    mp = marketplace.upper()
    env_key = f"SP_API_MARKETPLACE_{mp}"
    return os.environ.get(env_key, "ATVPDKIKX0DER")


async def api_get(path: str, params: dict = None) -> dict | list | str:
    """GET request to SP-API with auth and rate limiting."""
    token = await _get_access_token()
    if not token:
        return "Error: SP-API credentials not set. Check SP_API_CLIENT_ID, SP_API_CLIENT_SECRET, SP_API_REFRESH_TOKEN in .env."

    await _rate_limit()

    headers = {
        "x-amz-access-token": token,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}{path}", headers=headers, params=params)
    except httpx.TimeoutException:
        return f"Error: Request timed out (30s). Path: {path}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code == 429:
        return "Error: Rate limit exceeded (429). Wait and try again."
    if response.status_code == 403:
        return f"Error: Forbidden (403). Your app may not have the required role for this endpoint. Path: {path}"
    if response.status_code == 404:
        return f"Error: Not found (404). Path: {path}"
    if response.status_code != 200:
        body = response.text[:500]
        return f"Error: HTTP {response.status_code}. Path: {path}. Response: {body}"

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


async def api_post(path: str, body: dict = None) -> dict | list | str:
    """POST request to SP-API with auth and rate limiting."""
    token = await _get_access_token()
    if not token:
        return "Error: SP-API credentials not set. Check .env."

    await _rate_limit()

    headers = {
        "x-amz-access-token": token,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{BASE_URL}{path}", headers=headers, json=body or {})
    except httpx.TimeoutException:
        return f"Error: Request timed out (60s). Path: {path}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code == 429:
        return "Error: Rate limit exceeded (429). Wait and try again."
    if response.status_code == 403:
        return f"Error: Forbidden (403). Path: {path}"
    if response.status_code not in (200, 201, 202):
        body = response.text[:500]
        return f"Error: HTTP {response.status_code}. Path: {path}. Response: {body}"

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


async def api_patch(path: str, body: dict = None, params: dict = None) -> dict | list | str:
    """PATCH request to SP-API with auth and rate limiting."""
    token = await _get_access_token()
    if not token:
        return "Error: SP-API credentials not set. Check .env."

    await _rate_limit()

    headers = {
        "x-amz-access-token": token,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.patch(
                f"{BASE_URL}{path}", headers=headers, json=body or {}, params=params
            )
    except httpx.TimeoutException:
        return f"Error: Request timed out (60s). Path: {path}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code == 429:
        return "Error: Rate limit exceeded (429). Wait and try again."
    if response.status_code == 403:
        return f"Error: Forbidden (403). Your app may not have the Listings role. Path: {path}"
    if response.status_code not in (200, 201):
        resp_body = response.text[:500]
        return f"Error: HTTP {response.status_code}. Path: {path}. Response: {resp_body}"

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


def _seller_id() -> str:
    """Get seller ID from env."""
    return os.environ.get("SP_API_SELLER_ID", "")


def _serialize_value(val, max_len: int = 2000) -> str:
    """Serialize values for display. Returns compact JSON for nested structures."""
    if val is None:
        return ""
    if isinstance(val, (str, int, float, bool)):
        s = str(val)
        return s[:max_len] + "..." if len(s) > max_len else s
    # For lists and dicts, serialize as compact JSON to preserve full data
    try:
        s = json.dumps(val, separators=(",", ":"))
        return s[:max_len] + "..." if len(s) > max_len else s
    except (TypeError, ValueError):
        s = str(val)
        return s[:max_len] + "..." if len(s) > max_len else s


def format_json(data, title: str = "", max_items: int = 50) -> str:
    """Format JSON response as readable markdown with full nested data preserved."""
    if isinstance(data, str):
        return data

    output = ""
    if title:
        output += f"## {title}\n\n"

    if isinstance(data, list):
        total = len(data)
        output += f"**Total items:** {total}\n\n"
        if total == 0:
            return output + "No data returned.\n"

        if isinstance(data[0], dict):
            keys = list(data[0].keys())
            has_nested = any(
                isinstance(data[0].get(k), (dict, list)) for k in keys
            )

            if has_nested:
                # Data has nested structures — use JSON blocks to preserve full data
                for i, item in enumerate(data[:max_items]):
                    output += f"### Item {i + 1}\n```json\n"
                    output += json.dumps(item, indent=2)
                    output += "\n```\n\n"
            else:
                # Flat data — use markdown table for readability
                header = "| " + " | ".join(keys) + " |"
                separator = "| " + " | ".join(["---"] * len(keys)) + " |"
                output += header + "\n" + separator + "\n"
                for item in data[:max_items]:
                    row = "| " + " | ".join(_serialize_value(item.get(k, ""), max_len=200) for k in keys) + " |"
                    output += row + "\n"

            if total > max_items:
                output += f"\n*... {total - max_items} more items truncated*\n"
        else:
            for item in data[:max_items]:
                output += f"- {item}\n"

    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                # Nested list of objects — render as sub-section
                output += f"\n### {key}\n"
                output += format_json(value, max_items=max_items)
            elif isinstance(value, (dict, list)):
                # Nested dict or simple list — render as JSON block
                try:
                    s = json.dumps(value, indent=2)
                    if len(s) > 5000:
                        s = s[:5000] + "\n... truncated"
                    output += f"- **{key}:**\n```json\n{s}\n```\n"
                except (TypeError, ValueError):
                    output += f"- **{key}:** {value}\n"
            else:
                output += f"- **{key}:** {value}\n"

    return output


# ============================================================
# TOOLS
# ============================================================


@mcp.tool()
async def get_marketplace_participations() -> str:
    """List all marketplaces your seller account is registered in.
    Returns marketplace names, IDs, and country codes."""
    data = await api_get("/sellers/v1/marketplaceParticipations")
    if isinstance(data, str):
        return data

    payload = data.get("payload", data)
    results = []
    for p in payload:
        mp = p.get("marketplace", {})
        part = p.get("participation", {})
        results.append({
            "name": mp.get("name", ""),
            "id": mp.get("id", ""),
            "country": mp.get("countryCode", ""),
            "isParticipating": part.get("isParticipating", ""),
        })
    return format_json(results, title="Marketplace Participations")


@mcp.tool()
async def get_orders(
    days_back: int = 7,
    date: str = "",
    marketplace: str = "US",
    max_results: int = 500,
) -> str:
    """Fetch recent orders from Amazon with full pagination.
    Returns order IDs, status, dates, totals (note: totals include tax).

    Args:
        days_back: Number of days to look back (default 7). Ignored if date is set.
        date: Specific date in YYYY-MM-DD format (e.g. '2026-02-23'). Fetches only that day.
        marketplace: US, CA, or MX.
        max_results: Max orders to return (default 500, auto-paginates).
    """
    if date:
        after = f"{date}T00:00:00Z"
        before = f"{date}T23:59:59Z"
    else:
        after = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")
        before = None

    params = {
        "MarketplaceIds": _marketplace_id(marketplace),
        "CreatedAfter": after,
        "MaxResultsPerPage": 100,
    }
    if before:
        params["CreatedBefore"] = before

    all_orders = []
    pages = 0
    max_pages = (max_results // 100) + 1

    while pages < max_pages:
        data = await api_get("/orders/v0/orders", params=params)
        if isinstance(data, str):
            if all_orders:
                break  # return what we have
            return data

        payload = data.get("payload", {})
        orders = payload.get("Orders", [])
        all_orders.extend(orders)
        pages += 1

        next_token = payload.get("NextToken")
        if not next_token or len(all_orders) >= max_results:
            break

        # Use NextToken for next page (replaces other params)
        params = {
            "MarketplaceIds": _marketplace_id(marketplace),
            "NextToken": next_token,
        }

    results = []
    for o in all_orders[:max_results]:
        total = o.get("OrderTotal", {})
        results.append({
            "OrderId": o.get("AmazonOrderId", ""),
            "Status": o.get("OrderStatus", ""),
            "Date": o.get("PurchaseDate", "")[:10],
            "Total": f"{total.get('Amount', '')} {total.get('CurrencyCode', '')}",
            "Items": o.get("NumberOfItemsShipped", 0) + o.get("NumberOfItemsUnshipped", 0),
            "Channel": o.get("SalesChannel", ""),
            "FulfillmentChannel": o.get("FulfillmentChannel", ""),
        })

    label = f"Orders for {date}" if date else f"Orders (last {days_back} days)"
    summary = f"**Fetched {len(results)} orders across {pages} page(s).**\n\n"

    # Add quick stats
    shipped = [r for r in results if r["Status"] == "Shipped"]
    pending = [r for r in results if r["Status"] == "Pending"]
    canceled = [r for r in results if r["Status"] == "Canceled"]
    total_units = sum(r["Items"] for r in results)
    shipped_totals = []
    for r in shipped:
        try:
            amt = float(r["Total"].replace(" USD", "").strip())
            shipped_totals.append(amt)
        except (ValueError, AttributeError):
            pass

    summary += f"| Metric | Value |\n| --- | --- |\n"
    summary += f"| Total orders | {len(results)} |\n"
    summary += f"| Shipped | {len(shipped)} |\n"
    summary += f"| Pending | {len(pending)} |\n"
    summary += f"| Canceled | {len(canceled)} |\n"
    summary += f"| Total units | {total_units} |\n"
    if shipped_totals:
        summary += f"| Shipped revenue (incl. tax) | ${sum(shipped_totals):,.2f} |\n"
        summary += f"| Avg order value (incl. tax) | ${sum(shipped_totals)/len(shipped_totals):,.2f} |\n"
    summary += f"\n*Note: Order totals include sales tax. For pre-tax prices, use get_order_items on individual orders.*\n\n"

    return f"## {label}\n\n{summary}" + format_json(results)


@mcp.tool()
async def get_order_items(order_id: str) -> str:
    """Get line items for a specific order.
    Returns ASINs, quantities, prices, SKUs for each item in the order."""
    data = await api_get(f"/orders/v0/orders/{order_id}/orderItems")
    if isinstance(data, str):
        return data

    items = data.get("payload", {}).get("OrderItems", [])
    results = []
    for item in items:
        price = item.get("ItemPrice", {})
        results.append({
            "ASIN": item.get("ASIN", ""),
            "SKU": item.get("SellerSKU", ""),
            "Title": item.get("Title", "")[:80],
            "Qty": item.get("QuantityOrdered", 0),
            "Price": f"{price.get('Amount', '')} {price.get('CurrencyCode', '')}",
        })
    return format_json(results, title=f"Order Items ({order_id})")


@mcp.tool()
async def get_catalog_item(
    asin: str,
    marketplace: str = "US",
) -> str:
    """Get product details for an ASIN from Amazon catalog.
    Returns title, brand, category, images, dimensions, sales rank."""
    params = {
        "marketplaceIds": _marketplace_id(marketplace),
        "includedData": "summaries,salesRanks,images,dimensions,identifiers",
    }
    data = await api_get(f"/catalog/2022-04-01/items/{asin}", params=params)
    if isinstance(data, str):
        return data
    return format_json(data, title=f"Catalog Item: {asin}")


@mcp.tool()
async def search_catalog(
    keywords: str,
    marketplace: str = "US",
    max_results: int = 20,
) -> str:
    """Search Amazon catalog by keywords.
    Returns matching ASINs with titles, brands, and classifications."""
    params = {
        "marketplaceIds": _marketplace_id(marketplace),
        "keywords": keywords,
        "includedData": "summaries",
        "pageSize": min(max_results, 20),
    }
    data = await api_get("/catalog/2022-04-01/items", params=params)
    if isinstance(data, str):
        return data

    items = data.get("items", [])
    results = []
    for item in items:
        summaries = item.get("summaries", [{}])
        s = summaries[0] if summaries else {}
        results.append({
            "ASIN": item.get("asin", ""),
            "Title": s.get("itemName", "")[:80],
            "Brand": s.get("brand", ""),
            "Classification": s.get("classificationId", ""),
        })
    return format_json(results, title=f"Catalog Search: '{keywords}'")


@mcp.tool()
async def get_competitive_pricing(
    asin: str,
    marketplace: str = "US",
) -> str:
    """Get competitive pricing for an ASIN.
    Returns landed price, listing price, and shipping for Buy Box and other offers."""
    params = {
        "MarketplaceId": _marketplace_id(marketplace),
        "Asins": asin,
        "ItemType": "Asin",
    }
    data = await api_get("/products/pricing/v0/competitivePrice", params=params)
    if isinstance(data, str):
        return data
    return format_json(data, title=f"Competitive Pricing: {asin}")


@mcp.tool()
async def get_item_offers(
    asin: str,
    marketplace: str = "US",
    item_condition: str = "New",
) -> str:
    """Get current offers/prices for an ASIN on Amazon.
    Returns all active offers with prices, shipping, seller info, Buy Box status."""
    params = {
        "MarketplaceId": _marketplace_id(marketplace),
        "ItemCondition": item_condition,
    }
    data = await api_get(f"/products/pricing/v0/items/{asin}/offers", params=params)
    if isinstance(data, str):
        return data
    return format_json(data, title=f"Offers: {asin}")


@mcp.tool()
async def get_fba_inventory(
    marketplace: str = "US",
    asin_filter: str = "",
) -> str:
    """Get FBA inventory summaries with full pagination.
    Returns SKUs with ASIN, fulfillable quantity, inbound, reserved stock levels.

    Args:
        marketplace: US, CA, or MX.
        asin_filter: Optional comma-separated ASINs to filter results (e.g. 'B08DDJCQKF,B09X55KL2C').
                     If provided, only returns inventory for those ASINs (aggregated across SKUs).
                     If empty, returns all SKUs (truncated at 50 in output).
    """
    mp_id = _marketplace_id(marketplace)
    params = {
        "details": "true",
        "granularityType": "Marketplace",
        "granularityId": mp_id,
        "marketplaceIds": mp_id,
    }

    # Parse ASIN filter
    filter_asins = set()
    if asin_filter:
        filter_asins = {a.strip() for a in asin_filter.split(",") if a.strip()}

    all_summaries = []
    pages = 0
    max_pages = 20  # safety cap (~1000 SKUs)

    while pages < max_pages:
        data = await api_get("/fba/inventory/v1/summaries", params=params)
        if isinstance(data, str):
            if all_summaries:
                break
            return data

        summaries = data.get("payload", {}).get("inventorySummaries", [])
        all_summaries.extend(summaries)
        pages += 1

        next_token = data.get("pagination", {}).get("nextToken")
        if not next_token:
            break

        params = {
            "details": "true",
            "granularityType": "Marketplace",
            "granularityId": mp_id,
            "marketplaceIds": mp_id,
            "nextToken": next_token,
        }

    # Build per-SKU results
    results = []
    for s in all_summaries:
        asin = s.get("asin", "")
        if filter_asins and asin not in filter_asins:
            continue
        inv = s.get("inventoryDetails", {})
        results.append({
            "ASIN": asin,
            "SKU": s.get("sellerSku", ""),
            "FNSKU": s.get("fnSku", ""),
            "Name": s.get("productName", "")[:60],
            "Fulfillable": s.get("totalQuantity", 0),
            "Inbound": inv.get("inboundWorkingQuantity", 0) + inv.get("inboundShippedQuantity", 0) + inv.get("inboundReceivingQuantity", 0),
            "Reserved": inv.get("reservedQuantity", {}).get("totalReservedQuantity", 0),
        })

    if filter_asins:
        # Aggregate multiple SKUs per ASIN into a single row
        asin_totals = {}
        for r in results:
            asin = r["ASIN"]
            if asin not in asin_totals:
                asin_totals[asin] = {
                    "ASIN": asin,
                    "Name": r["Name"],
                    "SKU_Count": 0,
                    "Fulfillable": 0,
                    "Inbound": 0,
                    "Reserved": 0,
                }
            asin_totals[asin]["SKU_Count"] += 1
            asin_totals[asin]["Fulfillable"] += r["Fulfillable"]
            asin_totals[asin]["Inbound"] += r["Inbound"]
            asin_totals[asin]["Reserved"] += r["Reserved"]

        # Flag missing ASINs
        aggregated = list(asin_totals.values())
        found_asins = set(asin_totals.keys())
        missing = filter_asins - found_asins
        for m in sorted(missing):
            aggregated.append({
                "ASIN": m,
                "Name": "NOT FOUND IN FBA INVENTORY",
                "SKU_Count": 0,
                "Fulfillable": 0,
                "Inbound": 0,
                "Reserved": 0,
            })

        title = f"FBA Inventory — {len(found_asins)}/{len(filter_asins)} ASINs found ({len(results)} SKUs, {pages} pages fetched)"
        return format_json(aggregated, title=title, max_items=len(aggregated))

    return format_json(results, title=f"FBA Inventory ({len(results)} SKUs, {pages} pages)")


@mcp.tool()
async def create_report(
    report_type: str,
    marketplace: str = "US",
    days_back: int = 30,
) -> str:
    """Request a report from Amazon. Returns a reportId to check with get_report_status.

    Common report types:
    - GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL (all orders)
    - GET_SALES_AND_TRAFFIC_REPORT (business report - sessions, conversions)
    - GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA (FBA inventory)
    - GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA (FBA returns)
    - GET_MERCHANT_LISTINGS_ALL_DATA (all active listings)
    - GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT (Brand Analytics search terms)
    """
    start = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")
    end = datetime.utcnow().strftime("%Y-%m-%dT23:59:59Z")

    body = {
        "reportType": report_type,
        "marketplaceIds": [_marketplace_id(marketplace)],
        "dataStartTime": start,
        "dataEndTime": end,
    }
    data = await api_post("/reports/2021-06-30/reports", body=body)
    if isinstance(data, str):
        return data

    report_id = data.get("reportId", "")
    return f"## Report Requested\n\n- **Report Type:** {report_type}\n- **Report ID:** {report_id}\n- **Period:** last {days_back} days\n\nUse `get_report_status(report_id='{report_id}')` to check when it's ready."



@mcp.tool()
async def create_brand_analytics_report(
    report_name: str,
    period: str = "WEEK",
    periods_back: int = 1,
    marketplace: str = "US",
    asins: str = "",
) -> str:
    """Request a Brand Analytics report with proper calendar-aligned dates.

    report_name options:
    - search_terms: Top search keywords + most-clicked ASINs + click/conversion share
    - market_basket: Items frequently bought together with your products
    - repeat_purchase: Repeat vs one-time purchase quantities per ASIN
    - sqp: Search Query Performance -- impressions, clicks, cart adds, purchases by query (REQUIRES asins)
    - scp: Search Catalog Performance -- same metrics organized by ASIN

    period: WEEK, MONTH, or QUARTER (default WEEK)
    periods_back: How many periods back (default 1 = last completed period)
    asins: Space-separated ASINs (REQUIRED for sqp, max 200 chars). Example: "B08DDJCQKF B09WQSBZY7"
    """
    report_map = {
        "search_terms": "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT",
        "market_basket": "GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT",
        "repeat_purchase": "GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT",
        "sqp": "GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT",
        "scp": "GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT",
    }

    report_type = report_map.get(report_name.lower())
    if not report_type:
        opts = ', '.join(report_map.keys())
        return f"Error: Unknown report_name '{report_name}'. Options: {opts}"

    now = datetime.utcnow()
    period = period.upper()

    if period == "WEEK":
        # Find last COMPLETED week (Sun-Sat).
        # Saturday=7 (go to prev Sat), Sun=1, Mon=2, Tue=3, etc.
        days_back_to_sat = (now.weekday() - 5) % 7 or 7
        last_saturday = now - timedelta(days=days_back_to_sat)
        last_saturday = last_saturday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = last_saturday - timedelta(weeks=periods_back - 1)
        start = end - timedelta(days=6)
        end_str = end.strftime("%Y-%m-%dT23:59:59Z")
        start_str = start.strftime("%Y-%m-%dT00:00:00Z")
    elif period == "MONTH":
        first_of_current = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        for _ in range(periods_back):
            first_of_current = (first_of_current - timedelta(days=1)).replace(day=1)
        start = first_of_current
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
        start_str = start.strftime("%Y-%m-%dT00:00:00Z")
        end_str = end.strftime("%Y-%m-%dT23:59:59Z")
    elif period == "QUARTER":
        current_q = (now.month - 1) // 3
        for _ in range(periods_back):
            current_q -= 1
        year = now.year + (current_q // 4)
        q = current_q % 4
        start_month = q * 3 + 1
        start = datetime(year, start_month, 1)
        end_month = start_month + 2
        if end_month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = datetime(year, end_month + 1, 1) - timedelta(days=1)
        start_str = start.strftime("%Y-%m-%dT00:00:00Z")
        end_str = end.strftime("%Y-%m-%dT23:59:59Z")
    else:
        return f"Error: period must be WEEK, MONTH, or QUARTER (got '{period}')"

    report_options = {"reportPeriod": period}

    # SQP requires asin parameter
    if report_name.lower() == "sqp":
        if not asins:
            return "Error: SQP report requires 'asins' parameter (space-separated, max 200 chars). Example: asins='B08DDJCQKF B09WQSBZY7'"
        if len(asins) > 200:
            return f"Error: asins string is {len(asins)} chars (max 200). Reduce the number of ASINs."
        report_options["asin"] = asins

    body = {
        "reportType": report_type,
        "marketplaceIds": [_marketplace_id(marketplace)],
        "dataStartTime": start_str,
        "dataEndTime": end_str,
        "reportOptions": report_options,
    }
    data = await api_post("/reports/2021-06-30/reports", body=body)
    if isinstance(data, str):
        return data

    report_id = data.get("reportId", "")
    parts = [
        "## Brand Analytics Report Requested",
        "",
        f"- **Report:** {report_name} ({report_type})",
        f"- **Report ID:** {report_id}",
        f"- **Period:** {period} ({start_str[:10]} to {end_str[:10]})",
        f"- **Marketplace:** {marketplace}",
    ]
    if asins:
        asin_count = len(asins.split())
        parts.append(f"- **ASINs:** {asin_count} provided")
    parts.append("")
    parts.append(f"Use `get_report_status(report_id='{report_id}')` to check when it's ready.")
    return chr(10).join(parts)


@mcp.tool()
async def get_report_status(report_id: str) -> str:
    """Check the status of a requested report.
    Returns DONE, IN_PROGRESS, IN_QUEUE, CANCELLED, or FATAL.
    When DONE, returns the document ID to download with get_report_document."""
    data = await api_get(f"/reports/2021-06-30/reports/{report_id}")
    if isinstance(data, str):
        return data

    status = data.get("processingStatus", "UNKNOWN")
    output = f"## Report Status\n\n"
    output += f"- **Report ID:** {report_id}\n"
    output += f"- **Type:** {data.get('reportType', '')}\n"
    output += f"- **Status:** {status}\n"

    if status == "DONE":
        doc_id = data.get("reportDocumentId", "")
        output += f"- **Document ID:** {doc_id}\n"
        output += f"\nUse `get_report_document(document_id='{doc_id}')` to download."
    elif status == "FATAL":
        output += f"\nReport failed. Try requesting again."

    return output


@mcp.tool()
async def get_report_document(document_id: str) -> str:
    """Download a completed report document.
    Returns the report data (CSV/TSV/JSON depending on report type)."""
    data = await api_get(f"/reports/2021-06-30/documents/{document_id}")
    if isinstance(data, str):
        return data

    url = data.get("url", "")
    if not url:
        return "Error: No download URL in report document."

    is_gzip = data.get("compressionAlgorithm", "").upper() == "GZIP"

    # Download the actual report content
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return f"Error: HTTP {resp.status_code} downloading report."

            if is_gzip:
                content = gzip.decompress(resp.content).decode("utf-8", errors="replace")
            else:
                content = resp.text

            # Cap output to avoid huge responses
            if len(content) > 50000:
                content = content[:50000] + f"\n\n... truncated ({len(content)} total chars)"
            return f"## Report Document ({document_id})\n\n```\n{content}\n```"
    except Exception as e:
        return f"Error downloading report: {e}"


@mcp.tool()
async def get_my_listings(
    marketplace: str = "US",
) -> str:
    """Get all your active listings via report.
    Requests GET_MERCHANT_LISTINGS_ALL_DATA report and returns the report ID.
    Use get_report_status and get_report_document to retrieve the data."""
    return await create_report("GET_MERCHANT_LISTINGS_ALL_DATA", marketplace, days_back=1)


@mcp.tool()
async def get_listing(
    sku: str,
    marketplace: str = "US",
) -> str:
    """Get current listing data for a SKU.
    Returns product type, attributes (title, bullets, description, keywords), issues, and offers.
    Use this before update_listing to find the required product_type.

    Args:
        sku: The seller SKU of the product (e.g. 'EK17').
        marketplace: US, CA, or MX.
    """
    seller_id = _seller_id()
    if not seller_id:
        return "Error: SP_API_SELLER_ID not set in .env. Find your Merchant ID in Seller Central → Account Info → Merchant Token."

    params = {
        "marketplaceIds": _marketplace_id(marketplace),
        "includedData": "attributes,issues,offers,fulfillmentAvailability",
    }
    data = await api_get(f"/listings/2021-08-01/items/{seller_id}/{sku}", params=params)
    if isinstance(data, str):
        return data

    # Extract key info for easy reading
    output = f"## Listing: {sku}\n\n"
    output += f"- **Product Type:** {data.get('productType', 'UNKNOWN')}\n"
    output += f"- **SKU:** {sku}\n\n"

    attrs = data.get("attributes", {})
    if attrs:
        # Title
        item_name = attrs.get("item_name", [])
        if item_name:
            title_val = item_name[0].get("value", "") if isinstance(item_name, list) else item_name
            output += f"### Current Title\n{title_val}\n\n"

        # Bullets
        bullets = attrs.get("bullet_point", [])
        if bullets:
            output += "### Current Bullet Points\n"
            for i, b in enumerate(bullets, 1):
                val = b.get("value", "") if isinstance(b, dict) else b
                output += f"{i}. {val}\n"
            output += "\n"

        # Description
        desc = attrs.get("product_description", [])
        if desc:
            desc_val = desc[0].get("value", "") if isinstance(desc, list) else desc
            output += f"### Current Description\n{desc_val}\n\n"

        # Backend keywords
        keywords = attrs.get("generic_keyword", [])
        if keywords:
            kw_val = keywords[0].get("value", "") if isinstance(keywords, list) else keywords
            output += f"### Current Backend Keywords\n{kw_val}\n\n"

    # Issues
    issues = data.get("issues", [])
    if issues:
        output += f"### Issues ({len(issues)})\n"
        for issue in issues:
            severity = issue.get("severity", "")
            msg = issue.get("message", "")
            output += f"- **[{severity}]** {msg}\n"

    # Also include raw attributes for full inspection
    output += "\n### All Attributes (raw)\n```json\n"
    output += json.dumps(attrs, indent=2)[:8000]
    output += "\n```\n"

    return output


@mcp.tool()
async def update_listing(
    sku: str,
    product_type: str,
    marketplace: str = "US",
    title: str = "",
    bullet_points: str = "",
    description: str = "",
    generic_keywords: str = "",
) -> str:
    """Update an Amazon listing's text content. Uses PATCH — only updates fields you provide.

    IMPORTANT: Run get_listing(sku) first to find the required product_type.

    Args:
        sku: The seller SKU (e.g. 'EK17').
        product_type: Amazon product type from get_listing (e.g. 'HOME_BED_AND_BATH'). Required.
        marketplace: US, CA, or MX.
        title: New product title. Leave blank to skip.
        bullet_points: New bullet points separated by ||| (triple pipe). Leave blank to skip.
                       Example: "First bullet|||Second bullet|||Third bullet"
        description: New product description. Leave blank to skip.
        generic_keywords: New backend keywords (space-separated, 249 bytes max). Leave blank to skip.
    """
    seller_id = _seller_id()
    if not seller_id:
        return "Error: SP_API_SELLER_ID not set in .env. Find your Merchant ID in Seller Central → Account Info → Merchant Token."

    mp_id = _marketplace_id(marketplace)
    patches = []

    if title:
        patches.append({
            "op": "replace",
            "path": "/attributes/item_name",
            "value": [{"value": title, "marketplace_id": mp_id}],
        })

    if bullet_points:
        bullets = [b.strip() for b in bullet_points.split("|||") if b.strip()]
        patches.append({
            "op": "replace",
            "path": "/attributes/bullet_point",
            "value": [{"value": b, "marketplace_id": mp_id} for b in bullets],
        })

    if description:
        patches.append({
            "op": "replace",
            "path": "/attributes/product_description",
            "value": [{"value": description, "marketplace_id": mp_id}],
        })

    if generic_keywords:
        # Validate byte count
        kw_bytes = len(generic_keywords.encode("utf-8"))
        if kw_bytes > 249:
            return f"Error: Backend keywords are {kw_bytes} bytes (max 249). Shorten them and try again."
        patches.append({
            "op": "replace",
            "path": "/attributes/generic_keyword",
            "value": [{"value": generic_keywords, "marketplace_id": mp_id}],
        })

    if not patches:
        return "Error: No fields to update. Provide at least one of: title, bullet_points, description, generic_keywords."

    body = {
        "productType": product_type,
        "patches": patches,
    }

    query_params = {"marketplaceIds": mp_id}

    data = await api_patch(
        f"/listings/2021-08-01/items/{seller_id}/{sku}",
        body=body,
        params=query_params,
    )
    if isinstance(data, str):
        return data

    # Format response
    status = data.get("status", "UNKNOWN")
    submission_id = data.get("submissionId", "N/A")
    output = f"## Listing Update: {sku}\n\n"
    output += f"- **Status:** {status}\n"
    output += f"- **Submission ID:** {submission_id}\n"
    output += f"- **Product Type:** {product_type}\n"

    # Show what was updated
    fields = []
    if title:
        fields.append("Title")
    if bullet_points:
        count = len([b for b in bullet_points.split("|||") if b.strip()])
        fields.append(f"Bullet Points ({count})")
    if description:
        fields.append("Description")
    if generic_keywords:
        fields.append(f"Backend Keywords ({len(generic_keywords.encode('utf-8'))}/249 bytes)")
    output += f"- **Fields submitted:** {', '.join(fields)}\n"

    if status == "ACCEPTED":
        output += "\nChanges accepted and queued for processing. They typically appear on the listing within 15 minutes to a few hours.\n"
    elif status == "INVALID":
        output += "\n**Submission was rejected.** Check the issues below and fix before retrying.\n"

    # Show issues if any
    issues = data.get("issues", [])
    if issues:
        output += f"\n### Issues ({len(issues)})\n"
        for issue in issues:
            severity = issue.get("severity", "")
            msg = issue.get("message", "")
            code = issue.get("code", "")
            attr_names = issue.get("attributeNames", [])
            output += f"- **[{severity}]** {msg}"
            if code:
                output += f" (code: {code})"
            if attr_names:
                output += f" — attributes: {', '.join(attr_names)}"
            output += "\n"

    return output


# --- Main ---

if __name__ == "__main__":
    mcp.run(transport="stdio")
