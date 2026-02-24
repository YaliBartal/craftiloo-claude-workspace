"""
Apify MCP Server
Exposes Apify Platform API endpoints as MCP tools for running actors,
checking status, and retrieving scraping results.

Base URL: https://api.apify.com/v2
Auth: Bearer token via Authorization header
Env: APIFY_API_TOKEN in .env
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

mcp = FastMCP("apify")

# --- Constants ---

BASE_URL = "https://api.apify.com/v2"
RATE_LIMIT_DELAY = 0.5  # seconds between requests
SYNC_RUN_TIMEOUT = 300.0  # max wait for synchronous actor runs
DEFAULT_DATASET_LIMIT = 100

_last_request_time = 0.0
_rate_lock = asyncio.Lock()


# --- Helper Functions ---

async def _rate_limit():
    """Enforce rate limiting between requests."""
    global _last_request_time
    async with _rate_lock:
        now = time.time()
        elapsed = now - _last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            await asyncio.sleep(RATE_LIMIT_DELAY - elapsed)
        _last_request_time = time.time()


def _get_headers():
    """Build request headers with Apify API token."""
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        return None
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


async def api_get(path: str, params: dict = None) -> dict | list | str:
    """GET request to Apify API with auth, rate limiting, and error handling."""
    headers = _get_headers()
    if headers is None:
        return "Error: APIFY_API_TOKEN not set. Add it to your .env file."

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

    if response.status_code == 429:
        return "Error: Rate limit exceeded (429). Wait a moment and try again."
    if response.status_code == 401:
        return "Error: Invalid API token (401). Check APIFY_API_TOKEN in .env."
    if response.status_code == 404:
        return f"Error: Not found (404). Check that the ID exists. Path: {path}"
    if response.status_code != 200:
        body = response.text[:500]
        return f"Error: HTTP {response.status_code} from Apify API. Path: {path}. Response: {body}"

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


async def api_post(path: str, body: dict = None, timeout: float = 60.0) -> dict | list | str:
    """POST request to Apify API with auth, rate limiting, and error handling."""
    headers = _get_headers()
    if headers is None:
        return "Error: APIFY_API_TOKEN not set. Add it to your .env file."

    await _rate_limit()

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{BASE_URL}{path}", headers=headers, json=body or {}
            )
    except httpx.TimeoutException:
        return f"Error: Request timed out ({timeout}s). Path: {path}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code == 429:
        return "Error: Rate limit exceeded (429). Wait a moment and try again."
    if response.status_code == 401:
        return "Error: Invalid API token (401). Check APIFY_API_TOKEN in .env."
    if response.status_code == 404:
        return f"Error: Not found (404). Path: {path}"
    if response.status_code not in (200, 201, 202):
        body_text = response.text[:500]
        return f"Error: HTTP {response.status_code} from Apify API. Path: {path}. Response: {body_text}"

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


def _extract_items(data, *keys):
    """Extract list items from response, trying multiple possible keys.
    Handles Apify's nested data.items pattern: {"data": {"items": [...]}}."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in keys:
            if key in data and isinstance(data[key], list):
                return data[key]
        # Handle nested data wrapper: {"data": {"items": [...]}}
        if "data" in data and isinstance(data["data"], dict):
            inner = data["data"]
            for key in keys:
                if key in inner and isinstance(inner[key], list):
                    return inner[key]
            if "items" in inner and isinstance(inner["items"], list):
                return inner["items"]
        if "data" in data:
            return data["data"] if isinstance(data["data"], list) else [data["data"]]
    return [data] if isinstance(data, dict) else []


# --- Tools ---


@mcp.tool()
async def search_store_actors(
    search: str,
    limit: int = 20,
) -> str:
    """Search the Apify Store for actors (scrapers/tools).
    Find actors for any scraping use case — Amazon products, reviews, search results, etc.
    Returns actor ID (use in run_actor), name, description, run count, and user rating."""
    params = {
        "search": search,
        "limit": min(limit, 50),
        "sortBy": "popularity",
    }
    data = await api_get("/store", params=params)
    if isinstance(data, str):
        return data

    items = _extract_items(data, "data", "items")
    results = []
    for item in items[:limit]:
        actor_id = item.get("id", "")
        username = item.get("username", "")
        name = item.get("name", "")
        if username and name:
            actor_id = f"{username}/{name}"

        results.append({
            "actorId": actor_id,
            "title": item.get("title", ""),
            "description": (item.get("description", "") or "")[:150],
            "totalRuns": item.get("stats", {}).get("totalRuns", 0),
            "totalUsers": item.get("stats", {}).get("totalUsers", 0),
        })
    return format_json(results, title=f"Apify Store: '{search}'")


@mcp.tool()
async def run_actor(
    actor_id: str,
    input_json: str = "{}",
    memory_mb: int = 0,
    timeout_secs: int = 0,
) -> str:
    """Run an Apify actor asynchronously. Returns immediately with a run ID.
    Use get_run_status to check progress, then get_run_dataset to retrieve results.

    actor_id: Actor identifier like 'saswave~amazon-product-scraper' or 'username/actor-name'.
    input_json: JSON string of actor input (e.g. '{"asins": ["B08DDJCQKF"], "amazon_domain": "www.amazon.com"}').
    memory_mb: Memory allocation in MB (0 = actor default). Common: 256, 512, 1024, 2048, 4096.
    timeout_secs: Max run time in seconds (0 = actor default)."""
    try:
        input_data = json.loads(input_json) if input_json else {}
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON input — {e}"

    params = {}
    if memory_mb > 0:
        params["memory"] = memory_mb
    if timeout_secs > 0:
        params["timeout"] = timeout_secs

    path = f"/acts/{actor_id}/runs"
    data = await api_post(path, body=input_data)
    if isinstance(data, str):
        return data

    run_data = data.get("data", data)
    run_id = run_data.get("id", "")
    dataset_id = run_data.get("defaultDatasetId", "")
    status = run_data.get("status", "")

    output = f"## Actor Run Started\n\n"
    output += f"- **Actor:** {actor_id}\n"
    output += f"- **Run ID:** {run_id}\n"
    output += f"- **Status:** {status}\n"
    output += f"- **Dataset ID:** {dataset_id}\n"
    if memory_mb:
        output += f"- **Memory:** {memory_mb} MB\n"
    output += f"\nUse `get_run_status(run_id='{run_id}')` to check progress."
    output += f"\nWhen SUCCEEDED, use `get_run_dataset(dataset_id='{dataset_id}')` to get results."
    return output


@mcp.tool()
async def run_actor_sync(
    actor_id: str,
    input_json: str = "{}",
    memory_mb: int = 0,
    timeout_secs: int = 300,
    max_items: int = 100,
) -> str:
    """Run an Apify actor and wait for results (synchronous, blocks up to 300s).
    Best for quick actors that complete in under 5 minutes. For longer runs, use run_actor instead.

    actor_id: Actor identifier like 'saswave~amazon-product-scraper'.
    input_json: JSON string of actor input.
    timeout_secs: Max wait time in seconds (default 300, max 300).
    max_items: Max dataset items to return (default 100)."""
    try:
        input_data = json.loads(input_json) if input_json else {}
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON input — {e}"

    effective_timeout = min(timeout_secs, 300)

    params = {"timeout": effective_timeout}
    if memory_mb > 0:
        params["memory"] = memory_mb

    path = f"/acts/{actor_id}/run-sync"
    param_str = "&".join(f"{k}={v}" for k, v in params.items())
    path = f"{path}?{param_str}"

    data = await api_post(path, body=input_data, timeout=effective_timeout + 30)
    if isinstance(data, str):
        return data

    # Sync endpoint returns the run object
    run_data = data.get("data", data)
    status = run_data.get("status", "")
    dataset_id = run_data.get("defaultDatasetId", "")

    if status != "SUCCEEDED":
        output = f"## Actor Run Completed (non-success)\n\n"
        output += f"- **Actor:** {actor_id}\n"
        output += f"- **Status:** {status}\n"
        output += f"- **Run ID:** {run_data.get('id', '')}\n"
        return output

    if not dataset_id:
        return f"## Actor Run Completed\n\n- **Status:** {status}\n- No dataset ID returned."

    # Fetch dataset items
    items_data = await api_get(
        f"/datasets/{dataset_id}/items", params={"limit": max_items}
    )
    if isinstance(items_data, str):
        return f"## Actor run SUCCEEDED but dataset fetch failed\n\n{items_data}"

    items = items_data if isinstance(items_data, list) else _extract_items(items_data, "data", "items")
    return format_json(items, title=f"Results: {actor_id} ({len(items)} items)")


@mcp.tool()
async def get_run_status(run_id: str) -> str:
    """Check the status of an Apify actor run.
    Returns status (READY/RUNNING/SUCCEEDED/FAILED/ABORTED/TIMED-OUT), timing, and usage stats.
    When SUCCEEDED, provides the dataset ID for get_run_dataset."""
    data = await api_get(f"/actor-runs/{run_id}")
    if isinstance(data, str):
        return data

    run_data = data.get("data", data)
    status = run_data.get("status", "UNKNOWN")
    actor_id = run_data.get("actId", run_data.get("actorId", ""))
    dataset_id = run_data.get("defaultDatasetId", "")
    started = run_data.get("startedAt", "")
    finished = run_data.get("finishedAt", "")
    usage = run_data.get("usage", {})

    output = f"## Run Status\n\n"
    output += f"- **Run ID:** {run_id}\n"
    output += f"- **Actor:** {actor_id}\n"
    output += f"- **Status:** {status}\n"
    if started:
        output += f"- **Started:** {started}\n"
    if finished:
        output += f"- **Finished:** {finished}\n"
    if dataset_id:
        output += f"- **Dataset ID:** {dataset_id}\n"
    if usage:
        compute = usage.get("ACTOR_COMPUTE_UNITS", 0)
        if compute:
            output += f"- **Compute Units:** {compute}\n"

    if status == "SUCCEEDED" and dataset_id:
        output += f"\nUse `get_run_dataset(dataset_id='{dataset_id}')` to get results."
    elif status in ("RUNNING", "READY"):
        output += f"\nStill running. Check again shortly."
    elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
        output += f"\nRun did not succeed. Consider re-running or checking actor logs."

    return output


@mcp.tool()
async def get_run_dataset(
    dataset_id: str,
    limit: int = 100,
    offset: int = 0,
) -> str:
    """Fetch results from a completed actor run's dataset.
    Returns the scraped data items. Use after get_run_status shows SUCCEEDED.

    dataset_id: The defaultDatasetId from the run status.
    limit: Max items to return (default 100, max 1000).
    offset: Skip first N items (for pagination)."""
    params = {
        "limit": min(limit, 1000),
        "offset": offset,
    }
    data = await api_get(f"/datasets/{dataset_id}/items", params=params)
    if isinstance(data, str):
        return data

    items = data if isinstance(data, list) else _extract_items(data, "data", "items")

    title = f"Dataset Results ({dataset_id[:12]}...)"
    if offset > 0:
        title += f" [offset: {offset}]"

    return format_json(items, title=title, max_items=min(limit, 100))


@mcp.tool()
async def list_recent_runs(
    actor_id: str = "",
    limit: int = 20,
) -> str:
    """List recent actor runs with status and timing.
    Optionally filter by actor_id. Shows run ID, status, actor, start time, and dataset ID.

    actor_id: Optional — filter to a specific actor (e.g. 'saswave~amazon-product-scraper').
    limit: Number of runs to return (default 20, max 100)."""
    params = {
        "limit": min(limit, 100),
        "desc": "true",
    }

    if actor_id:
        path = f"/acts/{actor_id}/runs"
    else:
        path = "/actor-runs"

    data = await api_get(path, params=params)
    if isinstance(data, str):
        return data

    items = _extract_items(data, "data", "items")
    results = []
    for run in items[:limit]:
        results.append({
            "runId": run.get("id", ""),
            "actorId": run.get("actId", run.get("actorId", "")),
            "status": run.get("status", ""),
            "startedAt": (run.get("startedAt", "") or "")[:19],
            "finishedAt": (run.get("finishedAt", "") or "")[:19],
            "datasetId": run.get("defaultDatasetId", ""),
        })

    title = "Recent Runs"
    if actor_id:
        title += f" ({actor_id})"
    return format_json(results, title=title)


@mcp.tool()
async def abort_run(run_id: str) -> str:
    """Abort (cancel) a running actor. Use if a run is stuck or no longer needed.
    Only works on runs with status READY or RUNNING."""
    data = await api_post(f"/actor-runs/{run_id}/abort")
    if isinstance(data, str):
        return data

    run_data = data.get("data", data)
    status = run_data.get("status", "")

    output = f"## Run Aborted\n\n"
    output += f"- **Run ID:** {run_id}\n"
    output += f"- **Status:** {status}\n"
    return output


# --- Main ---

if __name__ == "__main__":
    mcp.run(transport="stdio")
