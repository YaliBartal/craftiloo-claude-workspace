"""
Amazon Ads API MCP Server
Exposes Amazon Advertising API endpoints as MCP tools.
Auth: LWA OAuth2 (Client ID + Client Secret + Refresh Token).
Supports Sponsored Products, Sponsored Brands, Sponsored Display, and Reporting.

Base URL: https://advertising-api.amazon.com
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

mcp = FastMCP("amazon-ads-api")

# --- Constants ---

BASE_URL = "https://advertising-api.amazon.com"
LWA_TOKEN_URL = "https://api.amazon.com/auth/o2/token"
RATE_LIMIT_DELAY = 0.5  # seconds between requests (conservative)

_last_request_time = 0.0
_rate_lock = asyncio.Lock()

# Token cache
_access_token = None
_token_expires_at = 0.0

# v3 versioned Content-Type headers per resource type
V3_HEADERS = {
    "campaigns": "application/vnd.spCampaign.v3+json",
    "adGroups": "application/vnd.spAdGroup.v3+json",
    "keywords": "application/vnd.spKeyword.v3+json",
    "negativeKeywords": "application/vnd.spNegativeKeyword.v3+json",
    "campaignNegativeKeywords": "application/vnd.spCampaignNegativeKeyword.v3+json",
    "targets": "application/vnd.spTargetingClause.v3+json",
    "negativeTargets": "application/vnd.spNegativeTargetingClause.v3+json",
    "bidRecommendations": "application/vnd.spTargetBidRecommendation.v3+json",
    "budgetUsage": "application/vnd.spCampaignBudgetUsage.v1+json",
    "sb_campaigns": "application/vnd.sbCampaignResource.v4+json",
    "sd_campaigns": "application/vnd.sdCampaign.v3+json",
}

# Report presets with sensible default columns
REPORT_PRESETS = {
    "sp_campaigns": {
        "reportTypeId": "spCampaigns",
        "groupBy": ["campaign"],
        "columns": [
            "campaignName", "campaignId", "campaignStatus",
            "campaignBudgetAmount", "campaignBudgetType",
            "impressions", "clicks", "cost",
            "purchases7d", "sales7d", "unitsSoldClicks7d",
            "costPerClick", "clickThroughRate",
        ],
        "timeUnit": "SUMMARY",
    },
    "sp_search_terms": {
        "reportTypeId": "spSearchTerm",
        "groupBy": ["searchTerm"],
        "columns": [
            "searchTerm", "campaignName", "adGroupName", "targeting",
            "impressions", "clicks", "cost",
            "purchases7d", "sales7d", "unitsSoldClicks7d",
            "costPerClick", "clickThroughRate",
        ],
        "timeUnit": "SUMMARY",
    },
    "sp_keywords": {
        "reportTypeId": "spTargeting",
        "groupBy": ["targeting"],
        "columns": [
            "campaignName", "adGroupName", "targeting", "matchType",
            "impressions", "clicks", "cost",
            "purchases7d", "sales7d", "unitsSoldClicks7d",
            "topOfSearchImpressionShare",
        ],
        "timeUnit": "SUMMARY",
    },
    "sp_targets": {
        "reportTypeId": "spTargeting",
        "groupBy": ["targeting"],
        "columns": [
            "campaignName", "adGroupName", "targeting", "matchType",
            "impressions", "clicks", "cost",
            "purchases7d", "sales7d",
        ],
        "timeUnit": "SUMMARY",
    },
    "sp_placements": {
        "reportTypeId": "spCampaigns",
        "groupBy": ["campaign"],
        "columns": [
            "campaignName", "campaignId", "placementClassification",
            "impressions", "clicks", "cost",
            "purchases7d", "sales7d",
        ],
        "timeUnit": "SUMMARY",
    },
    "sp_purchased_products": {
        "reportTypeId": "spPurchasedProduct",
        "groupBy": ["asin"],
        "columns": [
            "campaignName", "adGroupName", "asin",
            "purchases7d", "sales7d", "unitsSoldClicks7d",
        ],
        "timeUnit": "SUMMARY",
    },
}


# --- Auth ---

async def _get_access_token() -> str:
    """Get a valid access token, refreshing if expired."""
    global _access_token, _token_expires_at

    if _access_token and time.time() < _token_expires_at - 60:
        return _access_token

    client_id = os.environ.get("ADS_API_CLIENT_ID")
    client_secret = os.environ.get("ADS_API_CLIENT_SECRET")
    refresh_token = os.environ.get("ADS_API_REFRESH_TOKEN")

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


def _profile_id(marketplace: str = "US") -> str:
    """Get advertising profile ID from env."""
    mp = marketplace.upper()
    env_key = f"ADS_API_PROFILE_{mp}"
    return os.environ.get(env_key, os.environ.get("ADS_API_PROFILE_US", ""))


def _build_headers(token: str, marketplace: str, resource: str = None) -> dict:
    """Build request headers with auth and optional v3 Content-Type."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Amazon-Advertising-API-ClientId": os.environ.get("ADS_API_CLIENT_ID", ""),
        "Amazon-Advertising-API-Scope": _profile_id(marketplace),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if resource and resource in V3_HEADERS:
        headers["Content-Type"] = V3_HEADERS[resource]
        headers["Accept"] = V3_HEADERS[resource]
    return headers


async def ads_api_get(path: str, params: dict = None, marketplace: str = "US") -> dict | list | str:
    """GET request to Ads API with auth and rate limiting."""
    token = await _get_access_token()
    if not token:
        return "Error: Ads API credentials not set. Check ADS_API_CLIENT_ID, ADS_API_CLIENT_SECRET, ADS_API_REFRESH_TOKEN in .env."

    profile = _profile_id(marketplace)
    if not profile:
        return f"Error: No profile ID for marketplace '{marketplace}'. Check ADS_API_PROFILE_{marketplace.upper()} in .env."

    await _rate_limit()

    headers = _build_headers(token, marketplace)

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
        return f"Error: Forbidden (403). Check Ads API app permissions. Path: {path}"
    if response.status_code == 404:
        return f"Error: Not found (404). Path: {path}"
    if response.status_code != 200:
        body = response.text[:500]
        return f"Error: HTTP {response.status_code}. Path: {path}. Response: {body}"

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


async def ads_api_post(path: str, body: dict = None, marketplace: str = "US",
                       resource: str = None) -> dict | list | str:
    """POST request to Ads API with auth, rate limiting, and v3 headers."""
    token = await _get_access_token()
    if not token:
        return "Error: Ads API credentials not set. Check .env."

    profile = _profile_id(marketplace)
    if not profile:
        return f"Error: No profile ID for marketplace '{marketplace}'. Check .env."

    await _rate_limit()

    headers = _build_headers(token, marketplace, resource)

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
    if response.status_code == 422:
        body_text = response.text[:500]
        return f"Error: Invalid request (422). Check filter/body syntax. Path: {path}. Response: {body_text}"
    if response.status_code not in (200, 201, 202, 207):
        body_text = response.text[:500]
        return f"Error: HTTP {response.status_code}. Path: {path}. Response: {body_text}"

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


async def ads_api_put(path: str, body: dict = None, marketplace: str = "US",
                      resource: str = None) -> dict | list | str:
    """PUT request to Ads API with auth, rate limiting, and v3 headers."""
    token = await _get_access_token()
    if not token:
        return "Error: Ads API credentials not set. Check .env."

    profile = _profile_id(marketplace)
    if not profile:
        return f"Error: No profile ID for marketplace '{marketplace}'. Check .env."

    await _rate_limit()

    headers = _build_headers(token, marketplace, resource)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.put(f"{BASE_URL}{path}", headers=headers, json=body or {})
    except httpx.TimeoutException:
        return f"Error: Request timed out (60s). Path: {path}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code == 429:
        return "Error: Rate limit exceeded (429). Wait and try again."
    if response.status_code == 403:
        return f"Error: Forbidden (403). Path: {path}"
    if response.status_code == 422:
        body_text = response.text[:500]
        return f"Error: Invalid request (422). Path: {path}. Response: {body_text}"
    if response.status_code not in (200, 201, 202, 207):
        body_text = response.text[:500]
        return f"Error: HTTP {response.status_code}. Path: {path}. Response: {body_text}"

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


async def _paginate_list(path: str, body: dict, marketplace: str = "US",
                         resource: str = None, max_items: int = 1000,
                         result_key: str = None) -> list | str:
    """Paginate through a v3 list endpoint. Returns list of items or error string."""
    all_items = []
    next_token = None
    max_pages = max(1, (max_items // 100) + 1)

    for _ in range(max_pages):
        request_body = {**body}
        if next_token:
            request_body["nextToken"] = next_token
        if "maxResults" not in request_body:
            request_body["maxResults"] = min(100, max_items - len(all_items))

        data = await ads_api_post(path, request_body, marketplace, resource)
        if isinstance(data, str):
            if all_items:
                break
            return data

        # Extract items — try provided key first, then common response keys
        items = None
        if result_key:
            items = data.get(result_key)
        if items is None:
            for key in ["campaigns", "adGroups", "keywords", "negativeKeywords",
                         "campaignNegativeKeywords", "targetingClauses",
                         "negativeTargetingClauses", "results"]:
                items = data.get(key)
                if items is not None:
                    break
        if items is None:
            items = data if isinstance(data, list) else []

        all_items.extend(items)

        next_token = data.get("nextToken")
        if not next_token or len(all_items) >= max_items:
            break

    return all_items[:max_items]


def _serialize_value(val, max_len: int = 2000) -> str:
    """Serialize values for display. Returns compact JSON for nested structures."""
    if val is None:
        return ""
    if isinstance(val, (str, int, float, bool)):
        s = str(val)
        return s[:max_len] + "..." if len(s) > max_len else s
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
                for i, item in enumerate(data[:max_items]):
                    output += f"### Item {i + 1}\n```json\n"
                    output += json.dumps(item, indent=2)
                    output += "\n```\n\n"
            else:
                header = "| " + " | ".join(keys) + " |"
                separator = "| " + " | ".join(["---"] * len(keys)) + " |"
                output += header + "\n" + separator + "\n"
                for item in data[:max_items]:
                    row = "| " + " | ".join(
                        _serialize_value(item.get(k, ""), max_len=200) for k in keys
                    ) + " |"
                    output += row + "\n"

            if total > max_items:
                output += f"\n*... {total - max_items} more items truncated*\n"
        else:
            for item in data[:max_items]:
                output += f"- {item}\n"

    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                output += f"\n### {key}\n"
                output += format_json(value, max_items=max_items)
            elif isinstance(value, (dict, list)):
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


def _parse_json_param(value: str, param_name: str) -> list | dict | str:
    """Parse a JSON string parameter. Returns parsed data or error string."""
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON in '{param_name}' parameter. {e}"


# ============================================================
# TOOLS — Profiles
# ============================================================

@mcp.tool()
async def list_profiles() -> str:
    """List all Amazon Advertising profiles (accounts).
    Returns profile IDs, marketplace, account name, type, daily budget.
    Use profile IDs to configure ADS_API_PROFILE_US/CA in .env."""
    token = await _get_access_token()
    if not token:
        return "Error: Ads API credentials not set. Check ADS_API_CLIENT_ID, ADS_API_CLIENT_SECRET, ADS_API_REFRESH_TOKEN in .env."

    await _rate_limit()

    headers = {
        "Authorization": f"Bearer {token}",
        "Amazon-Advertising-API-ClientId": os.environ.get("ADS_API_CLIENT_ID", ""),
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/v2/profiles", headers=headers)
    except httpx.TimeoutException:
        return "Error: Request timed out."
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code != 200:
        return f"Error: HTTP {response.status_code}. Response: {response.text[:500]}"

    profiles = response.json()
    results = []
    for p in profiles:
        info = p.get("accountInfo", {})
        results.append({
            "profileId": p.get("profileId"),
            "country": p.get("countryCode"),
            "currency": p.get("currencyCode"),
            "timezone": p.get("timezone"),
            "dailyBudget": p.get("dailyBudget"),
            "accountName": info.get("name"),
            "accountType": info.get("type"),
            "accountId": info.get("id"),
        })
    return format_json(results, title="Advertising Profiles")


# ============================================================
# TOOLS — Sponsored Products: Campaigns
# ============================================================

@mcp.tool()
async def list_sp_campaigns(
    state: str = "ENABLED",
    name_filter: str = "",
    portfolio_id: str = "",
    marketplace: str = "US",
    max_results: int = 200,
) -> str:
    """List Sponsored Products campaigns with filtering.

    Args:
        state: Filter by state — ENABLED, PAUSED, ARCHIVED, or ALL (default ENABLED).
        name_filter: Filter campaigns by name (contains match).
        portfolio_id: Filter by portfolio ID.
        marketplace: US or CA.
        max_results: Max campaigns to return (default 200).
    """
    body = {}
    if state.upper() != "ALL":
        body["stateFilter"] = {"include": [state.upper()]}
    if name_filter:
        body["nameFilter"] = {"queryTermMatchType": "BROAD_MATCH", "include": [name_filter]}
    if portfolio_id:
        body["portfolioIdFilter"] = {"include": [portfolio_id]}

    items = await _paginate_list("/sp/campaigns/list", body, marketplace, "campaigns", max_results)
    if isinstance(items, str):
        return items

    results = []
    for c in items:
        budget = c.get("budget", {})
        bidding = c.get("dynamicBidding", {})
        results.append({
            "campaignId": c.get("campaignId"),
            "name": c.get("name"),
            "state": c.get("state"),
            "budget": budget.get("budget"),
            "budgetType": budget.get("budgetType"),
            "biddingStrategy": bidding.get("strategy"),
            "portfolioId": c.get("portfolioId", ""),
            "startDate": c.get("startDate", ""),
        })
    return format_json(results, title=f"SP Campaigns ({marketplace})")


@mcp.tool()
async def create_sp_campaigns(campaigns: str, marketplace: str = "US") -> str:
    """Create one or more Sponsored Products campaigns.

    Args:
        campaigns: JSON array of campaign objects.
            Required: name, targetingType (MANUAL/AUTO), budget ({budget, budgetType}), startDate (YYYYMMDD).
            Example: [{"name": "Test", "targetingType": "MANUAL",
                       "budget": {"budget": 10.0, "budgetType": "DAILY"},
                       "startDate": "20260301", "state": "PAUSED"}]
        marketplace: US or CA.
    """
    parsed = _parse_json_param(campaigns, "campaigns")
    if isinstance(parsed, str):
        return parsed

    body = {"campaigns": parsed if isinstance(parsed, list) else [parsed]}
    data = await ads_api_post("/sp/campaigns", body, marketplace, "campaigns")
    if isinstance(data, str):
        return data

    results = data.get("campaigns", data) if isinstance(data, dict) else data
    return format_json(results, title="Campaign Creation Results")


@mcp.tool()
async def update_sp_campaigns(campaigns: str, marketplace: str = "US") -> str:
    """Update one or more Sponsored Products campaigns (state, budget, name, bidding).

    Args:
        campaigns: JSON array of updates. Each needs 'campaignId' plus fields to update.
            Example: [{"campaignId": "123", "state": "PAUSED"}]
            Example: [{"campaignId": "123", "budget": {"budget": 25.0, "budgetType": "DAILY"}}]
        marketplace: US or CA.
    """
    parsed = _parse_json_param(campaigns, "campaigns")
    if isinstance(parsed, str):
        return parsed

    body = {"campaigns": parsed if isinstance(parsed, list) else [parsed]}
    data = await ads_api_put("/sp/campaigns", body, marketplace, "campaigns")
    if isinstance(data, str):
        return data

    results = data.get("campaigns", data) if isinstance(data, dict) else data
    return format_json(results, title="Campaign Update Results")


# ============================================================
# TOOLS — Sponsored Products: Ad Groups
# ============================================================

@mcp.tool()
async def list_sp_ad_groups(
    campaign_id: str = "",
    state: str = "ENABLED",
    marketplace: str = "US",
    max_results: int = 200,
) -> str:
    """List Sponsored Products ad groups.

    Args:
        campaign_id: Filter by campaign ID (recommended).
        state: ENABLED, PAUSED, ARCHIVED, or ALL.
        marketplace: US or CA.
        max_results: Max results (default 200).
    """
    body = {}
    if state.upper() != "ALL":
        body["stateFilter"] = {"include": [state.upper()]}
    if campaign_id:
        body["campaignIdFilter"] = {"include": [campaign_id]}

    items = await _paginate_list("/sp/adGroups/list", body, marketplace, "adGroups", max_results)
    if isinstance(items, str):
        return items

    results = []
    for ag in items:
        results.append({
            "adGroupId": ag.get("adGroupId"),
            "name": ag.get("name"),
            "campaignId": ag.get("campaignId"),
            "state": ag.get("state"),
            "defaultBid": ag.get("defaultBid"),
        })
    return format_json(results, title=f"SP Ad Groups ({marketplace})")


@mcp.tool()
async def create_sp_ad_groups(ad_groups: str, marketplace: str = "US") -> str:
    """Create one or more SP ad groups.

    Args:
        ad_groups: JSON array. Required: name, campaignId, defaultBid.
            Example: [{"name": "Main", "campaignId": "123", "defaultBid": 1.00, "state": "ENABLED"}]
        marketplace: US or CA.
    """
    parsed = _parse_json_param(ad_groups, "ad_groups")
    if isinstance(parsed, str):
        return parsed

    body = {"adGroups": parsed if isinstance(parsed, list) else [parsed]}
    data = await ads_api_post("/sp/adGroups", body, marketplace, "adGroups")
    if isinstance(data, str):
        return data

    results = data.get("adGroups", data) if isinstance(data, dict) else data
    return format_json(results, title="Ad Group Creation Results")


@mcp.tool()
async def update_sp_ad_groups(ad_groups: str, marketplace: str = "US") -> str:
    """Update one or more SP ad groups (bid, state, name).

    Args:
        ad_groups: JSON array. Each needs 'adGroupId' plus fields to update.
            Example: [{"adGroupId": "123", "defaultBid": 1.50}]
            Example: [{"adGroupId": "123", "state": "PAUSED"}]
        marketplace: US or CA.
    """
    parsed = _parse_json_param(ad_groups, "ad_groups")
    if isinstance(parsed, str):
        return parsed

    body = {"adGroups": parsed if isinstance(parsed, list) else [parsed]}
    data = await ads_api_put("/sp/adGroups", body, marketplace, "adGroups")
    if isinstance(data, str):
        return data

    results = data.get("adGroups", data) if isinstance(data, dict) else data
    return format_json(results, title="Ad Group Update Results")


# ============================================================
# TOOLS — Sponsored Products: Keywords
# ============================================================

@mcp.tool()
async def list_sp_keywords(
    campaign_id: str = "",
    ad_group_id: str = "",
    state: str = "ENABLED",
    marketplace: str = "US",
    max_results: int = 500,
) -> str:
    """List Sponsored Products keywords (positive targeting).

    Args:
        campaign_id: Filter by campaign.
        ad_group_id: Filter by ad group.
        state: ENABLED, PAUSED, ARCHIVED, or ALL.
        marketplace: US or CA.
        max_results: Default 500.
    """
    body = {}
    if state.upper() != "ALL":
        body["stateFilter"] = {"include": [state.upper()]}
    if campaign_id:
        body["campaignIdFilter"] = {"include": [campaign_id]}
    if ad_group_id:
        body["adGroupIdFilter"] = {"include": [ad_group_id]}

    items = await _paginate_list("/sp/keywords/list", body, marketplace, "keywords", max_results)
    if isinstance(items, str):
        return items

    results = []
    for kw in items:
        results.append({
            "keywordId": kw.get("keywordId"),
            "keywordText": kw.get("keywordText"),
            "matchType": kw.get("matchType"),
            "bid": kw.get("bid"),
            "state": kw.get("state"),
            "adGroupId": kw.get("adGroupId"),
            "campaignId": kw.get("campaignId"),
        })
    return format_json(results, title=f"SP Keywords ({marketplace})")


@mcp.tool()
async def manage_sp_keywords(action: str, keywords: str, marketplace: str = "US") -> str:
    """Create or update SP keywords (positive targeting).

    Args:
        action: 'create' or 'update'.
        keywords: JSON array.
            Create: [{"campaignId": "...", "adGroupId": "...", "keywordText": "cross stitch kit",
                      "matchType": "BROAD", "bid": 1.20, "state": "ENABLED"}]
            Update: [{"keywordId": "...", "bid": 1.50}] or [{"keywordId": "...", "state": "PAUSED"}]
        marketplace: US or CA.
    """
    parsed = _parse_json_param(keywords, "keywords")
    if isinstance(parsed, str):
        return parsed

    body = {"keywords": parsed if isinstance(parsed, list) else [parsed]}
    if action.lower() == "create":
        data = await ads_api_post("/sp/keywords", body, marketplace, "keywords")
    elif action.lower() == "update":
        data = await ads_api_put("/sp/keywords", body, marketplace, "keywords")
    else:
        return f"Error: Invalid action '{action}'. Use 'create' or 'update'."

    if isinstance(data, str):
        return data
    results = data.get("keywords", data) if isinstance(data, dict) else data
    return format_json(results, title=f"Keyword {action.title()} Results")


# ============================================================
# TOOLS — Sponsored Products: Negative Keywords
# ============================================================

@mcp.tool()
async def list_sp_negative_keywords(
    campaign_id: str = "",
    ad_group_id: str = "",
    state: str = "ENABLED",
    marketplace: str = "US",
    max_results: int = 500,
) -> str:
    """List SP negative keywords (ad group level).

    Args:
        campaign_id: Filter by campaign.
        ad_group_id: Filter by ad group.
        state: ENABLED, PAUSED, ARCHIVED, or ALL.
        marketplace: US or CA.
        max_results: Default 500.
    """
    body = {}
    if state.upper() != "ALL":
        body["stateFilter"] = {"include": [state.upper()]}
    if campaign_id:
        body["campaignIdFilter"] = {"include": [campaign_id]}
    if ad_group_id:
        body["adGroupIdFilter"] = {"include": [ad_group_id]}

    items = await _paginate_list(
        "/sp/negativeKeywords/list", body, marketplace, "negativeKeywords", max_results
    )
    if isinstance(items, str):
        return items

    results = []
    for kw in items:
        results.append({
            "keywordId": kw.get("keywordId"),
            "keywordText": kw.get("keywordText"),
            "matchType": kw.get("matchType"),
            "state": kw.get("state"),
            "adGroupId": kw.get("adGroupId"),
            "campaignId": kw.get("campaignId"),
        })
    return format_json(results, title=f"SP Negative Keywords ({marketplace})")


@mcp.tool()
async def manage_sp_negative_keywords(action: str, keywords: str, marketplace: str = "US") -> str:
    """Create or update SP negative keywords (ad group level).

    Args:
        action: 'create' or 'update'.
        keywords: JSON array.
            Create: [{"campaignId": "...", "adGroupId": "...", "keywordText": "crochet",
                      "matchType": "NEGATIVE_PHRASE", "state": "ENABLED"}]
            Update: [{"keywordId": "...", "state": "ARCHIVED"}]
        marketplace: US or CA.
    """
    parsed = _parse_json_param(keywords, "keywords")
    if isinstance(parsed, str):
        return parsed

    body = {"negativeKeywords": parsed if isinstance(parsed, list) else [parsed]}
    if action.lower() == "create":
        data = await ads_api_post("/sp/negativeKeywords", body, marketplace, "negativeKeywords")
    elif action.lower() == "update":
        data = await ads_api_put("/sp/negativeKeywords", body, marketplace, "negativeKeywords")
    else:
        return f"Error: Invalid action '{action}'. Use 'create' or 'update'."

    if isinstance(data, str):
        return data
    results = data.get("negativeKeywords", data) if isinstance(data, dict) else data
    return format_json(results, title=f"Negative Keyword {action.title()} Results")


@mcp.tool()
async def list_sp_campaign_negative_keywords(
    campaign_id: str,
    marketplace: str = "US",
    max_results: int = 500,
) -> str:
    """List campaign-level negative keywords for an SP campaign.
    These apply across ALL ad groups in the campaign.

    Args:
        campaign_id: Campaign ID (required).
        marketplace: US or CA.
        max_results: Default 500.
    """
    body = {"campaignIdFilter": {"include": [campaign_id]}}

    items = await _paginate_list(
        "/sp/campaignNegativeKeywords/list", body, marketplace,
        "campaignNegativeKeywords", max_results
    )
    if isinstance(items, str):
        return items

    results = []
    for kw in items:
        results.append({
            "keywordId": kw.get("keywordId"),
            "keywordText": kw.get("keywordText"),
            "matchType": kw.get("matchType"),
            "state": kw.get("state"),
            "campaignId": kw.get("campaignId"),
        })
    return format_json(results, title=f"Campaign Negative Keywords ({marketplace})")


@mcp.tool()
async def create_sp_campaign_negative_keywords(keywords: str, marketplace: str = "US") -> str:
    """Create campaign-level negative keywords for SP campaigns.
    These apply across ALL ad groups. Cannot be updated — only created or archived.

    Args:
        keywords: JSON array.
            [{"campaignId": "...", "keywordText": "free pattern",
              "matchType": "NEGATIVE_PHRASE", "state": "ENABLED"}]
        marketplace: US or CA.
    """
    parsed = _parse_json_param(keywords, "keywords")
    if isinstance(parsed, str):
        return parsed

    body = {"campaignNegativeKeywords": parsed if isinstance(parsed, list) else [parsed]}
    data = await ads_api_post(
        "/sp/campaignNegativeKeywords", body, marketplace, "campaignNegativeKeywords"
    )
    if isinstance(data, str):
        return data

    results = data.get("campaignNegativeKeywords", data) if isinstance(data, dict) else data
    return format_json(results, title="Campaign Negative Keyword Creation Results")


# ============================================================
# TOOLS — Sponsored Products: Targeting
# ============================================================

@mcp.tool()
async def list_sp_targets(
    campaign_id: str = "",
    ad_group_id: str = "",
    state: str = "ENABLED",
    marketplace: str = "US",
    max_results: int = 500,
) -> str:
    """List SP product targeting clauses (ASIN and category targets).

    Args:
        campaign_id: Filter by campaign.
        ad_group_id: Filter by ad group.
        state: ENABLED, PAUSED, ARCHIVED, or ALL.
        marketplace: US or CA.
        max_results: Default 500.
    """
    body = {}
    if state.upper() != "ALL":
        body["stateFilter"] = {"include": [state.upper()]}
    if campaign_id:
        body["campaignIdFilter"] = {"include": [campaign_id]}
    if ad_group_id:
        body["adGroupIdFilter"] = {"include": [ad_group_id]}

    items = await _paginate_list(
        "/sp/targets/list", body, marketplace, "targets", max_results,
        result_key="targetingClauses"
    )
    if isinstance(items, str):
        return items

    results = []
    for t in items:
        results.append({
            "targetId": t.get("targetId"),
            "expression": json.dumps(t.get("expression", [])),
            "expressionType": t.get("expressionType"),
            "bid": t.get("bid"),
            "state": t.get("state"),
            "adGroupId": t.get("adGroupId"),
            "campaignId": t.get("campaignId"),
        })
    return format_json(results, title=f"SP Targets ({marketplace})")


@mcp.tool()
async def manage_sp_targets(action: str, targets: str, marketplace: str = "US") -> str:
    """Create or update SP product targets (ASIN/category targeting).

    Args:
        action: 'create' or 'update'.
        targets: JSON array.
            Create: [{"campaignId": "...", "adGroupId": "...",
                      "expression": [{"type": "asinSameAs", "value": "B08DDJCQKF"}],
                      "expressionType": "manual", "bid": 0.75, "state": "ENABLED"}]
            Update: [{"targetId": "...", "bid": 1.00}]
        marketplace: US or CA.
    """
    parsed = _parse_json_param(targets, "targets")
    if isinstance(parsed, str):
        return parsed

    body = {"targetingClauses": parsed if isinstance(parsed, list) else [parsed]}
    if action.lower() == "create":
        data = await ads_api_post("/sp/targets", body, marketplace, "targets")
    elif action.lower() == "update":
        data = await ads_api_put("/sp/targets", body, marketplace, "targets")
    else:
        return f"Error: Invalid action '{action}'. Use 'create' or 'update'."

    if isinstance(data, str):
        return data
    results = data.get("targetingClauses", data) if isinstance(data, dict) else data
    return format_json(results, title=f"Target {action.title()} Results")


@mcp.tool()
async def manage_sp_negative_targets(action: str, targets: str, marketplace: str = "US") -> str:
    """Create or list SP negative product targets.

    Args:
        action: 'create' or 'list'.
        targets: JSON data.
            Create: [{"campaignId": "...", "adGroupId": "...",
                      "expression": [{"type": "asinSameAs", "value": "B08DDJCQKF"}],
                      "state": "ENABLED"}]
            List: {"campaignIdFilter": {"include": ["..."]}}
        marketplace: US or CA.
    """
    parsed = _parse_json_param(targets, "targets")
    if isinstance(parsed, str):
        return parsed

    if action.lower() == "create":
        body = {"negativeTargetingClauses": parsed if isinstance(parsed, list) else [parsed]}
        data = await ads_api_post("/sp/negativeTargets", body, marketplace, "negativeTargets")
        if isinstance(data, str):
            return data
        results = data.get("negativeTargetingClauses", data) if isinstance(data, dict) else data
        return format_json(results, title="Negative Target Creation Results")
    elif action.lower() == "list":
        body = parsed if isinstance(parsed, dict) else {}
        items = await _paginate_list(
            "/sp/negativeTargets/list", body, marketplace, "negativeTargets", 500,
            result_key="negativeTargetingClauses"
        )
        if isinstance(items, str):
            return items
        return format_json(items, title=f"SP Negative Targets ({marketplace})")
    else:
        return f"Error: Invalid action '{action}'. Use 'create' or 'list'."


# ============================================================
# TOOLS — Sponsored Products: Bids & Budget
# ============================================================

@mcp.tool()
async def get_sp_bid_recommendations(targets: str, marketplace: str = "US") -> str:
    """Get bid recommendations for SP keyword or product targets.

    Args:
        targets: JSON array of targeting objects.
            Keywords: [{"keywordText": "cross stitch kit", "matchType": "BROAD"}]
            Products: [{"expression": [{"type": "asinSameAs", "value": "B08DDJCQKF"}]}]
        marketplace: US or CA.
    """
    parsed = _parse_json_param(targets, "targets")
    if isinstance(parsed, str):
        return parsed

    body = {"targetingExpressions": parsed if isinstance(parsed, list) else [parsed]}
    data = await ads_api_post(
        "/sp/targets/bid/recommendations", body, marketplace, "bidRecommendations"
    )
    if isinstance(data, str):
        return data

    return format_json(data, title=f"Bid Recommendations ({marketplace})")


@mcp.tool()
async def get_sp_campaign_budget_usage(campaign_ids: str, marketplace: str = "US") -> str:
    """Check budget usage and recommendations for SP campaigns.
    Shows if campaigns are budget-constrained.

    Args:
        campaign_ids: Comma-separated campaign IDs (max 100).
        marketplace: US or CA.
    """
    ids = [cid.strip() for cid in campaign_ids.split(",") if cid.strip()]
    if not ids:
        return "Error: Provide at least one campaign ID."

    body = {"campaignIds": ids}
    data = await ads_api_post(
        "/sp/campaigns/budget/usage", body, marketplace, "budgetUsage"
    )
    if isinstance(data, str):
        return data

    return format_json(data, title=f"Budget Usage ({marketplace})")


# ============================================================
# TOOLS — Reporting
# ============================================================

@mcp.tool()
async def create_ads_report(
    report_type: str,
    date_range: str = "LAST_7_DAYS",
    marketplace: str = "US",
    metrics: str = "",
) -> str:
    """Create an async Amazon Ads report.

    Args:
        report_type: Preset name — sp_campaigns, sp_search_terms, sp_keywords,
                     sp_targets, sp_placements, sp_purchased_products.
        date_range: LAST_7_DAYS, LAST_14_DAYS, LAST_30_DAYS, LAST_60_DAYS, LAST_90_DAYS,
                    or custom 'YYYYMMDD-YYYYMMDD'.
        marketplace: US or CA.
        metrics: Optional comma-separated column names to override preset defaults.
    """
    preset = REPORT_PRESETS.get(report_type)
    if not preset:
        available = ", ".join(REPORT_PRESETS.keys())
        return f"Error: Unknown report_type '{report_type}'. Available: {available}"

    columns = [m.strip() for m in metrics.split(",") if m.strip()] if metrics else preset["columns"]

    # Build date range
    today = datetime.utcnow().date()
    range_days = {
        "LAST_7_DAYS": 7, "LAST_14_DAYS": 14, "LAST_30_DAYS": 30,
        "LAST_60_DAYS": 60, "LAST_90_DAYS": 90,
    }

    if date_range.upper() in range_days:
        days = range_days[date_range.upper()]
        end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    elif "-" in date_range and len(date_range) == 17:
        # Custom: YYYYMMDD-YYYYMMDD
        start_raw, end_raw = date_range.split("-")
        start_date = f"{start_raw[:4]}-{start_raw[4:6]}-{start_raw[6:8]}"
        end_date = f"{end_raw[:4]}-{end_raw[4:6]}-{end_raw[6:8]}"
    elif "-" in date_range and len(date_range) == 21:
        # Custom: YYYY-MM-DD-YYYY-MM-DD
        start_date = date_range[:10]
        end_date = date_range[11:]
    else:
        start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")

    body = {
        "name": f"{report_type} report",
        "startDate": start_date,
        "endDate": end_date,
        "configuration": {
            "adProduct": "SPONSORED_PRODUCTS",
            "reportTypeId": preset["reportTypeId"],
            "groupBy": preset["groupBy"],
            "columns": columns,
            "timeUnit": preset["timeUnit"],
            "format": "GZIP_JSON",
        },
    }

    # Use correct Content-Type for report creation
    token = await _get_access_token()
    if not token:
        return "Error: Ads API credentials not set. Check .env."
    profile = _profile_id(marketplace)
    if not profile:
        return f"Error: No profile ID for marketplace '{marketplace}'."

    await _rate_limit()

    headers = {
        "Authorization": f"Bearer {token}",
        "Amazon-Advertising-API-ClientId": os.environ.get("ADS_API_CLIENT_ID", ""),
        "Amazon-Advertising-API-Scope": profile,
        "Content-Type": "application/vnd.createasyncreportrequest.v3+json",
        "Accept": "application/vnd.createasyncreportrequest.v3+json",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BASE_URL}/reporting/reports", headers=headers, json=body
            )
    except httpx.TimeoutException:
        return "Error: Report creation timed out."
    except httpx.RequestError as e:
        return f"Error: Report creation failed — {e}"

    if response.status_code not in (200, 201, 202):
        return f"Error: HTTP {response.status_code}. Response: {response.text[:500]}"

    data = response.json()
    report_id = data.get("reportId", "unknown")
    status = data.get("status", "unknown")
    return (
        f"## Report Requested\n\n"
        f"- **Report ID:** `{report_id}`\n"
        f"- **Status:** {status}\n"
        f"- **Type:** {report_type}\n"
        f"- **Date Range:** {start_date} to {end_date}\n\n"
        f"Use `get_ads_report_status('{report_id}')` to check progress."
    )


@mcp.tool()
async def get_ads_report_status(report_id: str, marketplace: str = "US") -> str:
    """Check status of an Ads report.

    Args:
        report_id: Report ID from create_ads_report.
        marketplace: US or CA.
    """
    data = await ads_api_get(f"/reporting/reports/{report_id}", marketplace=marketplace)
    if isinstance(data, str):
        return data

    status = data.get("status", "unknown")
    output = f"## Report Status\n\n- **Report ID:** `{report_id}`\n- **Status:** {status}\n"

    if status == "COMPLETED":
        url = data.get("url", "")
        output += f"- **Size:** {data.get('fileSize', 'unknown')} bytes\n\n"
        output += f"Report is ready. Use `download_ads_report('{report_id}')` to download."
    elif status == "FAILED":
        output += f"- **Error:** {data.get('statusDetails', 'No details available')}\n"
    else:
        output += "\nReport is still processing. Check again in a few seconds."

    return output


@mcp.tool()
async def download_ads_report(
    report_id: str,
    marketplace: str = "US",
    max_rows: int = 500,
) -> str:
    """Download a completed Ads report. Handles gzip decompression.

    Args:
        report_id: Report ID from create_ads_report.
        marketplace: US or CA.
        max_rows: Max rows to return (default 500).
    """
    # Get report status to find download URL
    data = await ads_api_get(f"/reporting/reports/{report_id}", marketplace=marketplace)
    if isinstance(data, str):
        return data

    status = data.get("status", "")
    if status != "COMPLETED":
        return f"Report is not ready. Status: {status}. Wait and check again with get_ads_report_status."

    url = data.get("url", "")
    if not url:
        return "Error: Report completed but no download URL found."

    # Download the report (pre-signed S3 URL, no auth needed)
    await _rate_limit()
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(url)
    except httpx.TimeoutException:
        return "Error: Report download timed out (120s)."
    except httpx.RequestError as e:
        return f"Error: Report download failed — {e}"

    if response.status_code != 200:
        return f"Error: Download HTTP {response.status_code}."

    # Decompress and parse
    try:
        content = gzip.decompress(response.content)
        report_data = json.loads(content)
    except (gzip.BadGzipFile, json.JSONDecodeError):
        # Try as plain JSON
        try:
            report_data = response.json()
        except json.JSONDecodeError:
            return f"Error: Could not parse report. First 500 chars: {response.text[:500]}"

    if not isinstance(report_data, list):
        return format_json(report_data, title=f"Report {report_id}")

    total = len(report_data)
    truncated = report_data[:max_rows]

    output = format_json(truncated, title=f"Report Results ({total} total rows)")
    if total > max_rows:
        output += f"\n*Showing {max_rows} of {total} rows. Increase max_rows for more.*\n"
    return output


# ============================================================
# TOOLS — Sponsored Brands
# ============================================================

@mcp.tool()
async def list_sb_campaigns(
    state: str = "ENABLED",
    marketplace: str = "US",
    max_results: int = 100,
) -> str:
    """List Sponsored Brands campaigns.

    Args:
        state: ENABLED, PAUSED, ARCHIVED, or ALL.
        marketplace: US or CA.
        max_results: Default 100.
    """
    body = {}
    if state.upper() != "ALL":
        body["stateFilter"] = {"include": [state.upper()]}

    items = await _paginate_list(
        "/sb/v4/campaigns/list", body, marketplace, "sb_campaigns", max_results
    )
    if isinstance(items, str):
        return items

    results = []
    for c in items:
        budget = c.get("budget", {})
        results.append({
            "campaignId": c.get("campaignId"),
            "name": c.get("name"),
            "state": c.get("state"),
            "budget": budget.get("budget") if isinstance(budget, dict) else budget,
            "budgetType": budget.get("budgetType") if isinstance(budget, dict) else "",
            "portfolioId": c.get("portfolioId", ""),
        })
    return format_json(results, title=f"SB Campaigns ({marketplace})")


@mcp.tool()
async def update_sb_campaigns(campaigns: str, marketplace: str = "US") -> str:
    """Update Sponsored Brands campaigns (state, budget).

    Args:
        campaigns: JSON array. Each needs 'campaignId' plus fields to update.
            Example: [{"campaignId": "123", "state": "PAUSED"}]
        marketplace: US or CA.
    """
    parsed = _parse_json_param(campaigns, "campaigns")
    if isinstance(parsed, str):
        return parsed

    body = {"campaigns": parsed if isinstance(parsed, list) else [parsed]}
    data = await ads_api_put("/sb/campaigns", body, marketplace, "sb_campaigns")
    if isinstance(data, str):
        return data

    results = data.get("campaigns", data) if isinstance(data, dict) else data
    return format_json(results, title="SB Campaign Update Results")


# ============================================================
# TOOLS — Sponsored Display
# ============================================================

@mcp.tool()
async def list_sd_campaigns(
    state: str = "ENABLED",
    marketplace: str = "US",
    max_results: int = 100,
) -> str:
    """List Sponsored Display campaigns.

    Args:
        state: ENABLED, PAUSED, ARCHIVED, or ALL.
        marketplace: US or CA.
        max_results: Default 100.
    """
    params = {}
    if state.upper() != "ALL":
        params["stateFilter"] = state.lower()
    params["count"] = min(max_results, 100)

    data = await ads_api_get("/sd/campaigns", params=params, marketplace=marketplace)
    if isinstance(data, str):
        return data

    items = data if isinstance(data, list) else data.get("campaigns", [])

    results = []
    for c in items[:max_results]:
        results.append({
            "campaignId": c.get("campaignId"),
            "name": c.get("name"),
            "state": c.get("state"),
            "budget": c.get("budget"),
            "budgetType": c.get("budgetType", ""),
            "tactic": c.get("tactic", ""),
            "costType": c.get("costType", ""),
        })
    return format_json(results, title=f"SD Campaigns ({marketplace})")


@mcp.tool()
async def update_sd_campaigns(campaigns: str, marketplace: str = "US") -> str:
    """Update Sponsored Display campaigns (state, budget).

    Args:
        campaigns: JSON array. Each needs 'campaignId' plus fields to update.
            Example: [{"campaignId": "123", "state": "PAUSED"}]
        marketplace: US or CA.
    """
    parsed = _parse_json_param(campaigns, "campaigns")
    if isinstance(parsed, str):
        return parsed

    items = parsed if isinstance(parsed, list) else [parsed]
    data = await ads_api_put("/sd/campaigns", items, marketplace)
    if isinstance(data, str):
        return data

    results = data if isinstance(data, list) else data.get("campaigns", data)
    return format_json(results, title="SD Campaign Update Results")


# ============================================================
# TOOLS — Portfolios
# ============================================================

@mcp.tool()
async def list_portfolios(marketplace: str = "US") -> str:
    """List all portfolios. Returns portfolio ID, name, state, budget.

    Args:
        marketplace: US or CA.
    """
    data = await ads_api_get("/v2/portfolios", marketplace=marketplace)
    if isinstance(data, str):
        return data

    if not isinstance(data, list):
        return format_json(data, title="Portfolios")

    results = []
    for p in data:
        budget = p.get("budget", {})
        results.append({
            "portfolioId": p.get("portfolioId"),
            "name": p.get("name"),
            "state": p.get("state"),
            "budget": budget.get("amount") if isinstance(budget, dict) else "",
            "budgetPolicy": budget.get("policy") if isinstance(budget, dict) else "",
        })
    return format_json(results, title=f"Portfolios ({marketplace})")


@mcp.tool()
async def manage_portfolios(action: str, portfolios: str, marketplace: str = "US") -> str:
    """Create or update portfolios.

    Args:
        action: 'create' or 'update'.
        portfolios: JSON array.
            Create: [{"name": "Q2 Cross Stitch", "state": "ENABLED"}]
            Update: [{"portfolioId": "123", "name": "New Name", "state": "ENABLED"}]
        marketplace: US or CA.
    """
    parsed = _parse_json_param(portfolios, "portfolios")
    if isinstance(parsed, str):
        return parsed

    items = parsed if isinstance(parsed, list) else [parsed]
    if action.lower() == "create":
        data = await ads_api_post("/v2/portfolios", items, marketplace)
    elif action.lower() == "update":
        data = await ads_api_put("/v2/portfolios", items, marketplace)
    else:
        return f"Error: Invalid action '{action}'. Use 'create' or 'update'."

    if isinstance(data, str):
        return data
    return format_json(data, title=f"Portfolio {action.title()} Results")


# --- Main ---

if __name__ == "__main__":
    mcp.run(transport="stdio")
