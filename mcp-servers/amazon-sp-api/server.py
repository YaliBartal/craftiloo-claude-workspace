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
) -> str:
    """Get FBA inventory summaries with full pagination.
    Returns ALL SKUs with ASIN, fulfillable quantity, inbound, reserved stock levels."""
    mp_id = _marketplace_id(marketplace)
    params = {
        "details": "true",
        "granularityType": "Marketplace",
        "granularityId": mp_id,
        "marketplaceIds": mp_id,
    }

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

    results = []
    for s in all_summaries:
        inv = s.get("inventoryDetails", {})
        results.append({
            "ASIN": s.get("asin", ""),
            "SKU": s.get("sellerSku", ""),
            "FNSKU": s.get("fnSku", ""),
            "Name": s.get("productName", "")[:60],
            "Fulfillable": s.get("totalQuantity", 0),
            "Inbound": inv.get("inboundWorkingQuantity", 0) + inv.get("inboundShippedQuantity", 0) + inv.get("inboundReceivingQuantity", 0),
            "Reserved": inv.get("reservedQuantity", {}).get("totalReservedQuantity", 0),
        })

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


# --- Main ---

if __name__ == "__main__":
    mcp.run(transport="stdio")
