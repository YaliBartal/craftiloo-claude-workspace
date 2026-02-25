"""
DataDive MCP Server
Exposes DataDive API endpoints as MCP tools for keyword research,
competitor intelligence, rank tracking, and niche analysis.

Base URL: https://api.datadive.tools
Auth: x-api-key header
"""

import os
import time
import asyncio
import json
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

mcp = FastMCP("datadive")

# --- Constants ---

BASE_URL = "https://api.datadive.tools"
RATE_LIMIT_DELAY = 1.0  # seconds between requests

_last_request_time = 0.0
_rate_lock = asyncio.Lock()


# --- Helper Functions ---

async def _rate_limit():
    """Enforce 1 request/second rate limit."""
    global _last_request_time
    async with _rate_lock:
        now = time.time()
        elapsed = now - _last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            await asyncio.sleep(RATE_LIMIT_DELAY - elapsed)
        _last_request_time = time.time()


def _get_headers():
    """Build request headers with API key."""
    api_key = os.environ.get("DATADIVE_API_KEY")
    if not api_key:
        return None
    return {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


async def api_get(path: str, params: dict = None) -> dict | list | str:
    """GET request to DataDive API with auth, rate limiting, and error handling."""
    headers = _get_headers()
    if headers is None:
        return "Error: DATADIVE_API_KEY not set. Add it to your .env file."

    await _rate_limit()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BASE_URL}{path}", headers=headers, params=params
            )
    except httpx.TimeoutException:
        return f"Error: Request timed out (30s). Path: {path}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code != 200:
        try:
            err_body = response.text[:500]
        except Exception:
            err_body = ""
        return f"Error: HTTP {response.status_code} from DataDive API. Path: {path}. Response: {err_body}"

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


async def api_post(path: str, body: dict = None) -> dict | list | str:
    """POST request to DataDive API with auth, rate limiting, and error handling."""
    headers = _get_headers()
    if headers is None:
        return "Error: DATADIVE_API_KEY not set. Add it to your .env file."

    await _rate_limit()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BASE_URL}{path}", headers=headers, json=body or {}
            )
    except httpx.TimeoutException:
        return f"Error: Request timed out (60s). Path: {path}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code not in (200, 201):
        try:
            err_body = response.text[:500]
        except Exception:
            err_body = ""
        return f"Error: HTTP {response.status_code} from DataDive API. Path: {path}. Response: {err_body}"

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
                    row_vals = []
                    for k in keys:
                        val = item.get(k, "")
                        row_vals.append(_serialize_value(val, max_len=200))
                    output += "| " + " | ".join(row_vals) + " |\n"

            if total > max_items:
                output += f"\n*... {total - max_items} more items truncated*\n"
        else:
            for item in data[:max_items]:
                output += f"- {item}\n"
            if total > max_items:
                output += f"\n*... {total - max_items} more items truncated*\n"

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


def _extract_items(data, *keys):
    """Extract list items from response, trying multiple possible keys."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in keys:
            if key in data and isinstance(data[key], list):
                return data[key]
        # If there's a 'data' key, try that
        if "data" in data:
            return data["data"] if isinstance(data["data"], list) else [data["data"]]
    return [data] if isinstance(data, dict) else []


# --- Tools ---


@mcp.tool()
async def list_niches(page_size: int = 50) -> str:
    """List all DataDive niches.
    Returns nicheId, nicheLabel, heroKeyword per niche. Use the nicheId in other tools."""
    data = await api_get("/v1/niches", params={"pageSize": page_size})
    if isinstance(data, str):
        return data
    items = _extract_items(data, "niches", "items")
    return format_json(items, title="DataDive Niches")


@mcp.tool()
async def get_niche_keywords(niche_id: str, page_size: int = 200) -> str:
    """Fetch the Master Keyword List for a niche.
    Returns keyword, searchVolume, relevancy (Core/Related/Outlier), organic ranks, sponsored ranks.
    Use list_niches first to find the niche_id."""
    data = await api_get(
        f"/v1/niches/{niche_id}/keywords", params={"pageSize": page_size}
    )
    if isinstance(data, str):
        return data
    items = _extract_items(data, "keywords", "items")
    return format_json(items, title=f"Master Keyword List (niche: {niche_id})", max_items=200)


@mcp.tool()
async def get_niche_competitors(niche_id: str, page_size: int = 50) -> str:
    """Fetch competitor data for a niche from DataDive (Jungle Scout powered).
    Returns ASIN, BSR, sales/revenue estimates, price, rating, reviews, P1 keywords, advertised keywords.
    Use list_niches first to find the niche_id."""
    data = await api_get(
        f"/v1/niches/{niche_id}/competitors", params={"pageSize": page_size}
    )
    if isinstance(data, str):
        return data
    items = _extract_items(data, "competitors", "items")
    return format_json(items, title=f"Competitors (niche: {niche_id})")


@mcp.tool()
async def get_niche_ranking_juices(niche_id: str, page_size: int = 50) -> str:
    """Fetch Ranking Juice scores for a niche.
    Returns listing optimization scores for title, bullets, description per competitor ASIN.
    Use list_niches first to find the niche_id."""
    data = await api_get(
        f"/v1/niches/{niche_id}/ranking-juices", params={"pageSize": page_size}
    )
    if isinstance(data, str):
        return data
    items = _extract_items(data, "rankingJuices", "items")
    return format_json(items, title=f"Ranking Juice (niche: {niche_id})")


@mcp.tool()
async def get_niche_roots(niche_id: str, page_size: int = 100) -> str:
    """Fetch keyword roots for a niche.
    Returns root words with frequency and broadSearchVolume.
    Use list_niches first to find the niche_id."""
    data = await api_get(
        f"/v1/niches/{niche_id}/roots", params={"pageSize": page_size}
    )
    if isinstance(data, str):
        return data
    items = _extract_items(data, "roots", "items")
    return format_json(items, title=f"Keyword Roots (niche: {niche_id})", max_items=100)


@mcp.tool()
async def run_ai_copywriter(
    niche_id: str,
    mode: str,
    product_name: str = "",
    product_description: str = "",
) -> str:
    """Run DataDive AI Copywriter for a niche.
    Modes: 'cosmo', 'ranking-juice', 'nlp', 'cosmo-rufus'.
    Returns optimized listing copy (title, bullets, description).
    Use list_niches first to find the niche_id."""
    valid_modes = ["cosmo", "ranking-juice", "nlp", "cosmo-rufus"]
    if mode not in valid_modes:
        return f"Error: Invalid mode '{mode}'. Must be one of: {', '.join(valid_modes)}"

    body = {"mode": mode}
    if product_name:
        body["productName"] = product_name
    if product_description:
        body["productDescription"] = product_description

    data = await api_post(f"/v1/niches/{niche_id}/ai-copywriter", body=body)
    if isinstance(data, str):
        return data
    return format_json(data, title=f"AI Copywriter ({mode})")


@mcp.tool()
async def list_rank_radars(page_size: int = 50) -> str:
    """List all active DataDive Rank Radars.
    Returns rankRadarId, asin, keywordCount, top10KW, top10SV, top50KW, top50SV.
    Use the rankRadarId in get_rank_radar_data."""
    data = await api_get("/v1/niches/rank-radars", params={"pageSize": page_size})
    if isinstance(data, str):
        return data
    items = _extract_items(data, "rankRadars", "items")
    return format_json(items, title="Rank Radars")


@mcp.tool()
async def get_rank_radar_data(
    rank_radar_id: str, start_date: str = "", end_date: str = ""
) -> str:
    """Fetch daily keyword rankings from a DataDive Rank Radar.
    Returns keyword, searchVolume, and daily ranks (organicRank + impressionRank).
    Dates in YYYY-MM-DD format. Use list_rank_radars first to find the rank_radar_id."""
    params = {}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date

    data = await api_get(f"/v1/niches/rank-radars/{rank_radar_id}", params=params)
    if isinstance(data, str):
        return data
    return format_json(data, title=f"Rank Radar ({rank_radar_id})")


@mcp.tool()
async def create_niche_dive(seed_asin: str, marketplace: str = "com", number_of_competitors: int = 10) -> str:
    """Create a new Niche Dive from a seed ASIN.
    WARNING: This consumes DataDive tokens.
    Discovers competitors and keywords automatically. Returns a dive ID to track with get_niche_dive_status.
    marketplace: Amazon marketplace (com, ca, co.uk, com.mx, in, fr, de, es, it, co.jp). Default: com.
    number_of_competitors: Number of competitors to discover (min 2). Default: 10."""
    body = {
        "asin": seed_asin,
        "marketplace": marketplace,
        "numberOfCompetitors": number_of_competitors,
    }

    data = await api_post("/v1/niches/dives", body=body)
    if isinstance(data, str):
        return data

    dive_id = ""
    estimated = ""
    if isinstance(data, dict):
        inner = data.get("data", data)
        dive_id = inner.get("diveId", inner.get("id", ""))
        estimated = inner.get("estimatedCompletionDate", "")

    output = f"## Niche Dive Created\n\n"
    output += f"- **Seed ASIN:** {seed_asin}\n"
    output += f"- **Marketplace:** {marketplace}\n"
    output += f"- **Competitors requested:** {number_of_competitors}\n"
    if dive_id:
        output += f"- **Dive ID:** {dive_id}\n"
    if estimated:
        output += f"- **Estimated completion:** {estimated}\n"
    if dive_id:
        output += f"\nUse `get_niche_dive_status(dive_id='{dive_id}')` to check progress.\n"
    else:
        output += "\n" + format_json(data)

    return output


@mcp.tool()
async def get_niche_dive_status(dive_id: str) -> str:
    """Check the status of a DataDive Niche Dive.
    Returns status (in_progress/success/error) and results when complete."""
    data = await api_get(f"/v1/niches/dives/{dive_id}")
    if isinstance(data, str):
        return data
    return format_json(data, title=f"Niche Dive ({dive_id})")


@mcp.tool()
async def get_niche_overview(niche_id: str) -> str:
    """Fetch a combined overview of a niche: competitors, top keywords, and roots.
    Useful for a quick niche snapshot. Use list_niches first to find the niche_id."""
    results = []

    sections = [
        ("Competitors", f"/v1/niches/{niche_id}/competitors", {"pageSize": 20}, "competitors"),
        ("Top Keywords", f"/v1/niches/{niche_id}/keywords", {"pageSize": 50}, "keywords"),
        ("Keyword Roots", f"/v1/niches/{niche_id}/roots", {"pageSize": 30}, "roots"),
    ]

    for title, path, params, item_key in sections:
        results.append(f"\n{'=' * 60}\n## {title}\n{'=' * 60}")
        data = await api_get(path, params=params)
        if isinstance(data, str):
            results.append(data)
        else:
            items = _extract_items(data, item_key, "items")
            results.append(format_json(items, max_items=20))

    return "\n".join(results)


# --- Main ---

if __name__ == "__main__":
    mcp.run(transport="stdio")
