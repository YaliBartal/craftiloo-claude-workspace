"""
Notion MCP Server
Exposes Notion API endpoints as MCP tools for workspace management.
Auth: Bearer token (Internal Integration Token).

Base URL: https://api.notion.com/v1
"""

import os
import re
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

mcp = FastMCP("notion")

# --- Constants ---

BASE_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
RATE_LIMIT_DELAY = 0.33  # ~3 requests/second
MAX_BLOCKS_PER_APPEND = 100
MAX_PAGINATION_PAGES = 10
MAX_RECURSIVE_DEPTH = 3

_last_request_time = 0.0
_rate_lock = asyncio.Lock()


# --- Helper Functions ---


def _normalize_id(id_str: str) -> str:
    """Strip dashes from UUID for consistent handling."""
    return id_str.replace("-", "").strip()


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
    """Build request headers with API key and Notion version."""
    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        return None
    return {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


async def api_get(path: str, params: dict = None) -> dict | list | str:
    """GET request to Notion API with auth, rate limiting, and error handling."""
    headers = _get_headers()
    if headers is None:
        return "Error: NOTION_API_KEY not set. Add it to your .env file."

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
        return "Error: Invalid API key (401). Check NOTION_API_KEY in .env."
    if response.status_code == 403:
        return f"Error: Forbidden (403). Make sure the integration has access to this page/database. Path: {path}"
    if response.status_code == 404:
        return f"Error: Not found (404). Check that the page/database exists and is shared with the integration. Path: {path}"
    if response.status_code == 409:
        return "Error: Conflict (409). The resource was modified by another process. Try again."
    if response.status_code != 200:
        body = response.text[:500]
        return f"Error: HTTP {response.status_code}. Path: {path}. Response: {body}"

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


async def api_post(path: str, body: dict = None) -> dict | list | str:
    """POST request to Notion API with auth, rate limiting, and error handling."""
    headers = _get_headers()
    if headers is None:
        return "Error: NOTION_API_KEY not set. Add it to your .env file."

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

    if response.status_code == 429:
        return "Error: Rate limit exceeded (429). Wait a moment and try again."
    if response.status_code == 401:
        return "Error: Invalid API key (401). Check NOTION_API_KEY in .env."
    if response.status_code == 403:
        return f"Error: Forbidden (403). Make sure the integration has access. Path: {path}"
    if response.status_code == 404:
        return f"Error: Not found (404). Check that the resource exists and is shared. Path: {path}"
    if response.status_code not in (200, 201):
        body_text = response.text[:500]
        return f"Error: HTTP {response.status_code}. Path: {path}. Response: {body_text}"

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


async def api_patch(path: str, body: dict = None) -> dict | list | str:
    """PATCH request to Notion API with auth, rate limiting, and error handling."""
    headers = _get_headers()
    if headers is None:
        return "Error: NOTION_API_KEY not set. Add it to your .env file."

    await _rate_limit()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.patch(
                f"{BASE_URL}{path}", headers=headers, json=body or {}
            )
    except httpx.TimeoutException:
        return f"Error: Request timed out (60s). Path: {path}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code == 429:
        return "Error: Rate limit exceeded (429). Wait a moment and try again."
    if response.status_code == 401:
        return "Error: Invalid API key (401). Check NOTION_API_KEY in .env."
    if response.status_code == 403:
        return f"Error: Forbidden (403). Path: {path}"
    if response.status_code == 404:
        return f"Error: Not found (404). Path: {path}"
    if response.status_code != 200:
        body_text = response.text[:500]
        return f"Error: HTTP {response.status_code}. Path: {path}. Response: {body_text}"

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


async def api_delete(path: str) -> dict | list | str:
    """DELETE request to Notion API with auth, rate limiting, and error handling."""
    headers = _get_headers()
    if headers is None:
        return "Error: NOTION_API_KEY not set. Add it to your .env file."

    await _rate_limit()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{BASE_URL}{path}", headers=headers
            )
    except httpx.TimeoutException:
        return f"Error: Request timed out (30s). Path: {path}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code == 429:
        return "Error: Rate limit exceeded (429). Wait a moment and try again."
    if response.status_code == 404:
        return f"Error: Not found (404). Path: {path}"
    if response.status_code != 200:
        body_text = response.text[:500]
        return f"Error: HTTP {response.status_code}. Path: {path}. Response: {body_text}"

    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


# --- Pagination Helpers ---


async def _paginate_post(path: str, body: dict, item_key: str = "results") -> list | str:
    """Auto-paginate a POST endpoint (e.g., database query, search)."""
    all_items = []
    start_cursor = None

    for _ in range(MAX_PAGINATION_PAGES):
        req_body = dict(body)
        if start_cursor:
            req_body["start_cursor"] = start_cursor

        data = await api_post(path, req_body)
        if isinstance(data, str):
            if all_items:
                return all_items  # Return what we have so far
            return data

        items = data.get(item_key, [])
        all_items.extend(items)

        if not data.get("has_more", False):
            break
        start_cursor = data.get("next_cursor")
        if not start_cursor:
            break

    return all_items


async def _paginate_get(path: str, params: dict = None, item_key: str = "results") -> list | str:
    """Auto-paginate a GET endpoint (e.g., block children, users, comments)."""
    all_items = []
    start_cursor = None
    params = dict(params) if params else {}

    for _ in range(MAX_PAGINATION_PAGES):
        if start_cursor:
            params["start_cursor"] = start_cursor

        data = await api_get(path, params)
        if isinstance(data, str):
            if all_items:
                return all_items
            return data

        items = data.get(item_key, [])
        all_items.extend(items)

        if not data.get("has_more", False):
            break
        start_cursor = data.get("next_cursor")
        if not start_cursor:
            break

    return all_items


# --- Rich Text Helpers ---


def _rich_text(text: str, bold: bool = False, italic: bool = False,
               code: bool = False, strikethrough: bool = False,
               link: str = "") -> dict:
    """Build a single Notion rich_text object."""
    rt = {
        "type": "text",
        "text": {"content": text},
        "annotations": {
            "bold": bold,
            "italic": italic,
            "code": code,
            "strikethrough": strikethrough,
        },
    }
    if link:
        rt["text"]["link"] = {"url": link}
    return rt


def _rich_text_array(text: str) -> list:
    """Build a rich_text array from plain text, handling 2000-char Notion limit."""
    if not text:
        return [_rich_text("")]
    chunks = []
    while text:
        chunks.append(_rich_text(text[:2000]))
        text = text[2000:]
    return chunks


def _parse_inline_formatting(text: str) -> list:
    """Parse inline markdown formatting into Notion rich_text objects.

    Supports: **bold**, *italic*, `code`, ~~strikethrough~~
    """
    parts = []
    # Pattern matches: **bold**, *italic*, `code`, ~~strike~~
    pattern = r'(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|~~(.+?)~~)'
    last_end = 0

    for match in re.finditer(pattern, text):
        # Add plain text before this match
        if match.start() > last_end:
            plain = text[last_end:match.start()]
            if plain:
                parts.append(_rich_text(plain))

        if match.group(2) is not None:  # **bold**
            parts.append(_rich_text(match.group(2), bold=True))
        elif match.group(3) is not None:  # *italic*
            parts.append(_rich_text(match.group(3), italic=True))
        elif match.group(4) is not None:  # `code`
            parts.append(_rich_text(match.group(4), code=True))
        elif match.group(5) is not None:  # ~~strike~~
            parts.append(_rich_text(match.group(5), strikethrough=True))

        last_end = match.end()

    # Add remaining plain text
    if last_end < len(text):
        remaining = text[last_end:]
        if remaining:
            parts.append(_rich_text(remaining))

    if not parts:
        parts.append(_rich_text(text))

    return parts


def _extract_plain_text(rich_text_array: list) -> str:
    """Extract plain text from a Notion rich_text array."""
    if not rich_text_array:
        return ""
    parts = []
    for rt in rich_text_array:
        if isinstance(rt, dict):
            parts.append(rt.get("plain_text", rt.get("text", {}).get("content", "")))
        else:
            parts.append(str(rt))
    return "".join(parts)


# --- Block Builder Helpers ---


def _block(block_type: str, text: str = "", **kwargs) -> dict:
    """Build a Notion block object from type and text."""
    block = {"object": "block", "type": block_type}

    if block_type == "divider":
        block[block_type] = {}
    elif block_type == "code":
        block[block_type] = {
            "rich_text": _parse_inline_formatting(text),
            "language": kwargs.get("language", "plain text"),
        }
    elif block_type == "to_do":
        block[block_type] = {
            "rich_text": _parse_inline_formatting(text),
            "checked": kwargs.get("checked", False),
        }
    elif block_type in ("heading_1", "heading_2", "heading_3"):
        block[block_type] = {
            "rich_text": _parse_inline_formatting(text),
            "is_toggleable": kwargs.get("is_toggleable", False),
        }
    elif block_type == "callout":
        block[block_type] = {
            "rich_text": _parse_inline_formatting(text),
            "icon": kwargs.get("icon", {"type": "emoji", "emoji": "💡"}),
        }
    elif block_type == "table":
        block[block_type] = {
            "table_width": kwargs.get("table_width", 2),
            "has_column_header": kwargs.get("has_column_header", True),
            "has_row_header": False,
            "children": kwargs.get("children", []),
        }
    elif block_type == "table_row":
        block[block_type] = {
            "cells": kwargs.get("cells", []),
        }
    elif block_type == "toggle":
        block[block_type] = {
            "rich_text": _parse_inline_formatting(text),
            "children": kwargs.get("children", []),
        }
    elif block_type == "image":
        block[block_type] = {
            "type": "external",
            "external": {"url": kwargs.get("url", text)},
        }
        if text and kwargs.get("url"):
            block[block_type]["caption"] = _parse_inline_formatting(text)
    else:
        # paragraph, bulleted_list_item, numbered_list_item, quote
        block[block_type] = {
            "rich_text": _parse_inline_formatting(text),
        }

    return block


def _chunk_blocks(blocks: list, size: int = MAX_BLOCKS_PER_APPEND) -> list:
    """Split a block list into chunks of `size` (default 100)."""
    return [blocks[i:i + size] for i in range(0, len(blocks), size)]


# --- Markdown Parser ---


def _parse_markdown(text: str) -> list:
    """Parse simplified markdown into Notion block objects.

    Supported syntax:
    - # / ## / ### Headings
    - Regular text -> paragraph
    - - Item -> bulleted list
    - 1. Item -> numbered list
    - > Quote
    - --- -> divider
    - ```code``` -> code block
    - [ ] / [x] -> to_do
    - !callout text -> callout
    - >>>Toggle Title + indented children -> toggle
    - | A | B | pipe tables -> table
    """
    lines = text.split("\n")
    blocks = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # Code block (multi-line)
        if stripped.startswith("```"):
            language = stripped[3:].strip() or "plain text"
            code_lines = []
            i += 1
            while i < len(lines):
                if lines[i].strip().startswith("```"):
                    i += 1
                    break
                code_lines.append(lines[i])
                i += 1
            else:
                i += 1  # EOF without closing ```
            blocks.append(_block("code", "\n".join(code_lines), language=language))
            continue

        # Toggle block (>>>Title + indented children)
        if stripped.startswith(">>>"):
            title = stripped[3:].strip()
            children = []
            i += 1
            while i < len(lines):
                child_line = lines[i]
                # Children are indented (2+ spaces or tab)
                if child_line and (child_line.startswith("  ") or child_line.startswith("\t")):
                    child_text = child_line.strip()
                    if child_text:
                        # Parse child as a simple block
                        child_block = _parse_single_line(child_text)
                        if child_block:
                            children.append(child_block)
                    i += 1
                elif child_line.strip() == "":
                    i += 1  # Skip blank lines within toggle
                else:
                    break
            blocks.append(_block("toggle", title, children=children if children else [_block("paragraph", "")]))
            continue

        # Table (pipe-delimited)
        if stripped.startswith("|") and stripped.endswith("|"):
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                row_text = lines[i].strip()
                # Skip separator rows (|---|---|)
                if re.match(r'^\|[\s\-:]+\|$', row_text.replace("|", "|")):
                    i += 1
                    continue
                cells = [c.strip() for c in row_text.strip("|").split("|")]
                table_rows.append(cells)
                i += 1

            if table_rows:
                table_width = max(len(row) for row in table_rows)
                children = []
                for row_cells in table_rows:
                    # Pad rows to table_width
                    while len(row_cells) < table_width:
                        row_cells.append("")
                    notion_cells = [_parse_inline_formatting(c) for c in row_cells]
                    children.append(_block("table_row", cells=notion_cells))
                blocks.append(_block("table", table_width=table_width,
                                     has_column_header=True, children=children))
            continue

        # Divider
        if stripped == "---" or stripped == "***" or stripped == "___":
            blocks.append(_block("divider"))
            i += 1
            continue

        # Single-line blocks
        block = _parse_single_line(stripped)
        if block:
            blocks.append(block)
        i += 1

    return blocks


def _parse_single_line(stripped: str) -> dict | None:
    """Parse a single line of markdown into a Notion block."""
    if not stripped:
        return None

    # Headings
    if stripped.startswith("### "):
        return _block("heading_3", stripped[4:])
    if stripped.startswith("## "):
        return _block("heading_2", stripped[3:])
    if stripped.startswith("# "):
        return _block("heading_1", stripped[2:])

    # Callout
    if stripped.startswith("!") and not stripped.startswith("!["):
        return _block("callout", stripped[1:].strip())

    # To-do
    if stripped.startswith("[x] ") or stripped.startswith("[X] "):
        return _block("to_do", stripped[4:], checked=True)
    if stripped.startswith("[ ] "):
        return _block("to_do", stripped[4:], checked=False)

    # Bulleted list
    if stripped.startswith("- ") or stripped.startswith("* "):
        return _block("bulleted_list_item", stripped[2:])

    # Numbered list
    num_match = re.match(r'^(\d+)\.\s+(.+)', stripped)
    if num_match:
        return _block("numbered_list_item", num_match.group(2))

    # Quote
    if stripped.startswith("> "):
        return _block("quote", stripped[2:])

    # Default: paragraph
    return _block("paragraph", stripped)


# --- Output Formatting ---


def _serialize_value(val, max_len: int = 2000) -> str:
    """Serialize values for display."""
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


# --- Property Formatting ---


def _format_property_value(prop: dict) -> str:
    """Extract a human-readable value from a Notion property object."""
    prop_type = prop.get("type", "")

    if prop_type == "title":
        return _extract_plain_text(prop.get("title", []))
    elif prop_type == "rich_text":
        return _extract_plain_text(prop.get("rich_text", []))
    elif prop_type == "number":
        val = prop.get("number")
        return str(val) if val is not None else ""
    elif prop_type == "select":
        sel = prop.get("select")
        return sel.get("name", "") if sel else ""
    elif prop_type == "multi_select":
        items = prop.get("multi_select", [])
        return ", ".join(i.get("name", "") for i in items)
    elif prop_type == "date":
        d = prop.get("date")
        if not d:
            return ""
        start = d.get("start", "")
        end = d.get("end", "")
        return f"{start} → {end}" if end else start
    elif prop_type == "checkbox":
        return "Yes" if prop.get("checkbox") else "No"
    elif prop_type == "url":
        return prop.get("url", "") or ""
    elif prop_type == "email":
        return prop.get("email", "") or ""
    elif prop_type == "phone_number":
        return prop.get("phone_number", "") or ""
    elif prop_type == "status":
        s = prop.get("status")
        return s.get("name", "") if s else ""
    elif prop_type == "people":
        people = prop.get("people", [])
        return ", ".join(p.get("name", p.get("id", "")) for p in people)
    elif prop_type == "files":
        files = prop.get("files", [])
        return ", ".join(f.get("name", "") for f in files)
    elif prop_type == "relation":
        rels = prop.get("relation", [])
        return ", ".join(r.get("id", "") for r in rels)
    elif prop_type == "formula":
        formula = prop.get("formula", {})
        f_type = formula.get("type", "")
        return str(formula.get(f_type, ""))
    elif prop_type == "rollup":
        rollup = prop.get("rollup", {})
        r_type = rollup.get("type", "")
        return str(rollup.get(r_type, ""))
    elif prop_type == "created_time":
        return prop.get("created_time", "")
    elif prop_type == "last_edited_time":
        return prop.get("last_edited_time", "")
    elif prop_type == "created_by":
        cb = prop.get("created_by", {})
        return cb.get("name", cb.get("id", ""))
    elif prop_type == "last_edited_by":
        eb = prop.get("last_edited_by", {})
        return eb.get("name", eb.get("id", ""))
    elif prop_type == "unique_id":
        uid = prop.get("unique_id", {})
        prefix = uid.get("prefix", "")
        number = uid.get("number", "")
        return f"{prefix}-{number}" if prefix else str(number)
    else:
        return str(prop.get(prop_type, ""))


def _format_page_summary(page: dict) -> str:
    """Format a page object into a readable summary."""
    props = page.get("properties", {})
    page_id = page.get("id", "")
    url = page.get("url", "")
    created = page.get("created_time", "")[:10]
    edited = page.get("last_edited_time", "")[:10]

    # Find title
    title = ""
    for name, prop in props.items():
        if prop.get("type") == "title":
            title = _extract_plain_text(prop.get("title", []))
            break

    output = f"## {title or 'Untitled'}\n\n"
    output += f"- **ID:** {page_id}\n"
    output += f"- **URL:** {url}\n"
    output += f"- **Created:** {created}\n"
    output += f"- **Last edited:** {edited}\n"

    # Format all properties
    if props:
        output += "\n### Properties\n\n"
        for name, prop in props.items():
            val = _format_property_value(prop)
            if val:
                output += f"- **{name}:** {val}\n"
            else:
                output += f"- **{name}:** *(empty)*\n"

    return output


def _format_block_content(block: dict, indent: int = 0) -> str:
    """Format a single block into readable text."""
    block_type = block.get("type", "unknown")
    prefix = "  " * indent
    block_id = block.get("id", "")

    content = block.get(block_type, {})

    if block_type == "divider":
        return f"{prefix}---\n"

    if block_type == "table_row":
        cells = content.get("cells", [])
        cell_texts = [_extract_plain_text(c) for c in cells]
        return f"{prefix}| " + " | ".join(cell_texts) + " |\n"

    if block_type == "code":
        text = _extract_plain_text(content.get("rich_text", []))
        lang = content.get("language", "")
        return f"{prefix}```{lang}\n{prefix}{text}\n{prefix}```\n"

    if block_type == "image":
        img = content.get("file", content.get("external", {}))
        url = img.get("url", "")
        caption = _extract_plain_text(content.get("caption", []))
        return f"{prefix}[Image: {caption or url}]\n"

    if block_type == "child_page":
        return f"{prefix}📄 **{content.get('title', 'Untitled')}** (page: {block_id})\n"

    if block_type == "child_database":
        return f"{prefix}📊 **{content.get('title', 'Untitled')}** (database: {block_id})\n"

    # Text-based blocks
    rich_text = content.get("rich_text", [])
    text = _extract_plain_text(rich_text)

    type_prefixes = {
        "heading_1": "# ",
        "heading_2": "## ",
        "heading_3": "### ",
        "bulleted_list_item": "- ",
        "numbered_list_item": "1. ",
        "quote": "> ",
        "callout": "💡 ",
        "toggle": "▶ ",
        "to_do": "",
    }

    type_prefix = type_prefixes.get(block_type, "")

    if block_type == "to_do":
        checked = content.get("checked", False)
        type_prefix = "[x] " if checked else "[ ] "

    return f"{prefix}{type_prefix}{text}\n"


# ============================================================
# TOOLS — Group 1: Search & Discovery
# ============================================================


@mcp.tool()
async def search(
    query: str = "",
    filter_type: str = "",
    page_size: int = 20,
) -> str:
    """Search across the entire Notion workspace by title.
    Returns pages and/or databases matching the query.

    Args:
        query: Text to search in page/database titles. Empty returns recent items.
        filter_type: 'page' or 'database' to filter results. Empty returns both.
        page_size: Number of results to return (max 100).
    """
    body = {}
    if query:
        body["query"] = query
    if filter_type in ("page", "database"):
        body["filter"] = {"value": filter_type, "property": "object"}
    body["page_size"] = min(page_size, 100)

    data = await _paginate_post("/search", body)
    if isinstance(data, str):
        return data

    results = []
    for item in data:
        obj_type = item.get("object", "")
        item_id = item.get("id", "")
        edited = item.get("last_edited_time", "")[:10]

        # Get title
        title = ""
        if obj_type == "page":
            for prop in item.get("properties", {}).values():
                if prop.get("type") == "title":
                    title = _extract_plain_text(prop.get("title", []))
                    break
        elif obj_type == "database":
            title_arr = item.get("title", [])
            title = _extract_plain_text(title_arr)

        # Get parent info
        parent = item.get("parent", {})
        parent_type = parent.get("type", "")
        parent_info = parent.get(parent_type, "")
        if isinstance(parent_info, bool):
            parent_info = "workspace"

        results.append({
            "Type": obj_type,
            "Title": title or "(untitled)",
            "ID": item_id,
            "Last Edited": edited,
            "Parent": f"{parent_type}: {parent_info}",
        })

    return format_json(results, title=f"Search Results{' for: ' + query if query else ''}")


@mcp.tool()
async def get_self() -> str:
    """Get the integration bot's user info. Use to verify the connection works."""
    data = await api_get("/users/me")
    if isinstance(data, str):
        return data

    output = "## Bot User Info\n\n"
    output += f"- **Name:** {data.get('name', '')}\n"
    output += f"- **ID:** {data.get('id', '')}\n"
    output += f"- **Type:** {data.get('type', '')}\n"
    bot = data.get("bot", {})
    if bot:
        owner = bot.get("owner", {})
        output += f"- **Owner type:** {owner.get('type', '')}\n"
    return output


# ============================================================
# TOOLS — Group 2: Pages
# ============================================================


@mcp.tool()
async def get_page(page_id: str) -> str:
    """Get page metadata and all properties.
    Does NOT return page content (blocks) — use get_blocks or get_page_tree for that.

    Args:
        page_id: Page UUID (with or without dashes).
    """
    pid = _normalize_id(page_id)
    data = await api_get(f"/pages/{pid}")
    if isinstance(data, str):
        return data
    return _format_page_summary(data)


@mcp.tool()
async def get_page_property(page_id: str, property_id: str) -> str:
    """Get a single property value from a page, with auto-pagination for large properties.
    Use when get_page returns a property as 'paginated' rather than inline.

    Args:
        page_id: Page UUID.
        property_id: Property ID (from get_page output).
    """
    pid = _normalize_id(page_id)
    data = await _paginate_get(f"/pages/{pid}/properties/{property_id}")
    if isinstance(data, str):
        return data
    return format_json(data, title=f"Property: {property_id}")


@mcp.tool()
async def create_page(
    parent_id: str,
    title: str,
    parent_type: str = "page",
    properties_json: str = "",
    content_markdown: str = "",
) -> str:
    """Create a new page under a parent page or inside a database.

    Args:
        parent_id: Parent page ID or database ID.
        title: Page title.
        parent_type: 'page' or 'database'.
        properties_json: JSON string of additional properties (for database pages).
        content_markdown: Optional initial content as simplified markdown.
    """
    pid = _normalize_id(parent_id)

    body = {}
    if parent_type == "database":
        body["parent"] = {"database_id": pid}
        # For database pages, title goes in the title property
        props = {}
        if properties_json:
            try:
                props = json.loads(properties_json)
            except json.JSONDecodeError:
                return f"Error: Invalid JSON in properties_json: {properties_json[:200]}"
        # Find or create title property
        has_title = any(
            isinstance(v, dict) and v.get("title") is not None
            for v in props.values()
        )
        if not has_title:
            props["Name"] = {"title": _rich_text_array(title)}
        body["properties"] = props
    else:
        body["parent"] = {"page_id": pid}
        body["properties"] = {"title": {"title": _rich_text_array(title)}}
        if properties_json:
            try:
                extra_props = json.loads(properties_json)
                body["properties"].update(extra_props)
            except json.JSONDecodeError:
                return f"Error: Invalid JSON in properties_json: {properties_json[:200]}"

    # Add initial content blocks if provided
    if content_markdown:
        blocks = _parse_markdown(content_markdown)
        # Only first 100 blocks can go in the create call
        if blocks:
            body["children"] = blocks[:MAX_BLOCKS_PER_APPEND]

    data = await api_post("/pages", body)
    if isinstance(data, str):
        return data

    new_id = data.get("id", "")
    new_url = data.get("url", "")

    output = f"## Page Created\n\n"
    output += f"- **Title:** {title}\n"
    output += f"- **ID:** {new_id}\n"
    output += f"- **URL:** {new_url}\n"

    # If more than 100 blocks, append the rest
    if content_markdown:
        blocks = _parse_markdown(content_markdown)
        if len(blocks) > MAX_BLOCKS_PER_APPEND:
            remaining = blocks[MAX_BLOCKS_PER_APPEND:]
            chunks = _chunk_blocks(remaining)
            appended = 0
            for chunk in chunks:
                result = await api_patch(f"/blocks/{new_id}/children", {"children": chunk})
                if isinstance(result, str):
                    output += f"\n**Warning:** Failed to append some blocks: {result}\n"
                    break
                appended += len(chunk)
            output += f"- **Blocks appended:** {MAX_BLOCKS_PER_APPEND + appended}\n"
        else:
            output += f"- **Blocks:** {len(blocks)}\n"

    return output


@mcp.tool()
async def update_page(
    page_id: str,
    properties_json: str = "",
    archived: bool = False,
) -> str:
    """Update page properties and/or archive status.

    Args:
        page_id: Page UUID.
        properties_json: JSON string of properties to update (Notion property format).
        archived: Set to True to archive (soft-delete) the page.
    """
    pid = _normalize_id(page_id)
    body = {}

    if properties_json:
        try:
            body["properties"] = json.loads(properties_json)
        except json.JSONDecodeError:
            return f"Error: Invalid JSON in properties_json: {properties_json[:200]}"

    if archived:
        body["archived"] = True

    if not body:
        return "Error: Nothing to update. Provide properties_json and/or archived=True."

    data = await api_patch(f"/pages/{pid}", body)
    if isinstance(data, str):
        return data

    return _format_page_summary(data)


@mcp.tool()
async def move_page(
    page_id: str,
    new_parent_id: str,
    new_parent_type: str = "page",
) -> str:
    """Move a page to a new parent.

    Args:
        page_id: Page to move.
        new_parent_id: Destination parent ID.
        new_parent_type: 'page', 'database', or 'workspace'.
    """
    pid = _normalize_id(page_id)
    npid = _normalize_id(new_parent_id)

    body = {}
    if new_parent_type == "database":
        body["parent"] = {"database_id": npid}
    elif new_parent_type == "workspace":
        body["parent"] = {"workspace": True}
    else:
        body["parent"] = {"page_id": npid}

    data = await api_patch(f"/pages/{pid}", body)
    if isinstance(data, str):
        return data

    return f"## Page Moved\n\n- **Page ID:** {pid}\n- **New parent:** {new_parent_type}: {npid}\n- **URL:** {data.get('url', '')}\n"


@mcp.tool()
async def archive_page(page_id: str) -> str:
    """Archive (soft-delete) a page.

    Args:
        page_id: Page UUID to archive.
    """
    return await update_page(page_id, archived=True)


# ============================================================
# TOOLS — Group 3: Blocks / Content
# ============================================================


@mcp.tool()
async def get_blocks(block_id: str, page_size: int = 100) -> str:
    """Get direct child blocks of a page or block. Auto-paginates.
    Does NOT recurse into nested blocks — use get_page_tree for recursive fetching.

    Args:
        block_id: Page ID or block ID to get children of.
        page_size: Items per page (auto-paginates to get all).
    """
    bid = _normalize_id(block_id)
    data = await _paginate_get(
        f"/blocks/{bid}/children",
        params={"page_size": min(page_size, 100)},
    )
    if isinstance(data, str):
        return data

    output = f"## Blocks ({len(data)} items)\n\n"
    for i, block in enumerate(data):
        block_type = block.get("type", "unknown")
        block_bid = block.get("id", "")
        has_children = block.get("has_children", False)
        content_text = _format_block_content(block)
        children_marker = " [has children]" if has_children else ""
        output += f"{i + 1}. `{block_type}` ({block_bid}){children_marker}\n   {content_text}"

    return output


@mcp.tool()
async def get_block(block_id: str) -> str:
    """Get a single block's full details including type, content, and whether it has children.

    Args:
        block_id: Block UUID.
    """
    bid = _normalize_id(block_id)
    data = await api_get(f"/blocks/{bid}")
    if isinstance(data, str):
        return data

    block_type = data.get("type", "unknown")
    has_children = data.get("has_children", False)
    created = data.get("created_time", "")[:10]
    edited = data.get("last_edited_time", "")[:10]

    output = f"## Block Details\n\n"
    output += f"- **ID:** {data.get('id', '')}\n"
    output += f"- **Type:** {block_type}\n"
    output += f"- **Has children:** {has_children}\n"
    output += f"- **Created:** {created}\n"
    output += f"- **Last edited:** {edited}\n"
    output += f"\n### Content\n{_format_block_content(data)}\n"
    output += f"\n### Raw\n```json\n{json.dumps(data.get(block_type, {}), indent=2)}\n```\n"

    return output


@mcp.tool()
async def append_blocks(parent_id: str, blocks_json: str) -> str:
    """Append block children to a page or block using raw Notion block JSON.
    Auto-chunks into batches of 100 if needed.
    For simpler content creation, use append_markdown instead.

    Args:
        parent_id: Page ID or block ID to append to.
        blocks_json: JSON string of block objects (Notion block format).
    """
    pid = _normalize_id(parent_id)

    try:
        blocks = json.loads(blocks_json)
    except json.JSONDecodeError:
        return f"Error: Invalid JSON in blocks_json."

    if not isinstance(blocks, list):
        blocks = [blocks]

    total = len(blocks)
    chunks = _chunk_blocks(blocks)
    appended = 0

    for chunk in chunks:
        result = await api_patch(f"/blocks/{pid}/children", {"children": chunk})
        if isinstance(result, str):
            return f"Error after appending {appended}/{total} blocks: {result}"
        appended += len(chunk)

    return f"## Blocks Appended\n\n- **Parent:** {pid}\n- **Blocks appended:** {appended}\n"


@mcp.tool()
async def append_markdown(parent_id: str, markdown: str) -> str:
    """Convert simplified markdown to Notion blocks and append to a page or block.
    This is the primary content creation tool. Auto-chunks at 100 blocks.

    Supported syntax: # headings, - bullets, 1. numbered, > quotes, --- dividers,
    ```code```, [ ]/[x] todos, **bold**, *italic*, `code`, ~~strike~~,
    >>>toggle (with indented children), !callout, | pipe | tables |.

    Args:
        parent_id: Page ID or block ID to append to.
        markdown: Content in simplified markdown format.
    """
    pid = _normalize_id(parent_id)
    blocks = _parse_markdown(markdown)

    if not blocks:
        return "Error: No blocks parsed from the markdown content."

    total = len(blocks)
    chunks = _chunk_blocks(blocks)
    appended = 0

    for chunk in chunks:
        result = await api_patch(f"/blocks/{pid}/children", {"children": chunk})
        if isinstance(result, str):
            return f"Error after appending {appended}/{total} blocks: {result}"
        appended += len(chunk)

    return f"## Markdown Appended\n\n- **Parent:** {pid}\n- **Blocks created:** {appended}\n"


@mcp.tool()
async def update_block(block_id: str, block_json: str) -> str:
    """Update a block's content.

    Args:
        block_id: Block UUID to update.
        block_json: JSON string with block type key and updated fields.
    """
    bid = _normalize_id(block_id)

    try:
        body = json.loads(block_json)
    except json.JSONDecodeError:
        return "Error: Invalid JSON in block_json."

    data = await api_patch(f"/blocks/{bid}", body)
    if isinstance(data, str):
        return data

    return f"## Block Updated\n\n- **ID:** {bid}\n- **Type:** {data.get('type', '')}\n{_format_block_content(data)}"


@mcp.tool()
async def delete_block(block_id: str) -> str:
    """Delete (archive) a block. Also deletes all its children.

    Args:
        block_id: Block UUID to delete.
    """
    bid = _normalize_id(block_id)
    data = await api_delete(f"/blocks/{bid}")
    if isinstance(data, str):
        return data
    return f"## Block Deleted\n\n- **ID:** {bid}\n- **Type:** {data.get('type', 'unknown')}\n"


@mcp.tool()
async def get_page_tree(page_id: str, max_depth: int = 2) -> str:
    """Recursively fetch a page's entire content tree as indented text.
    Returns page properties + all blocks with nesting.

    Args:
        page_id: Page to read.
        max_depth: How many levels deep to recurse (1=direct children only, max 3).
    """
    pid = _normalize_id(page_id)
    max_depth = min(max_depth, MAX_RECURSIVE_DEPTH)

    # Get page metadata
    page_data = await api_get(f"/pages/{pid}")
    if isinstance(page_data, str):
        return page_data

    output = _format_page_summary(page_data)
    output += "\n### Content\n\n"

    # Recursively fetch blocks
    async def _fetch_blocks(block_id: str, depth: int, indent: int) -> str:
        blocks = await _paginate_get(
            f"/blocks/{block_id}/children",
            params={"page_size": 100},
        )
        if isinstance(blocks, str):
            return f"{'  ' * indent}(Error loading blocks: {blocks})\n"

        result = ""
        for block in blocks:
            result += _format_block_content(block, indent=indent)
            if block.get("has_children", False) and depth < max_depth:
                bid = block.get("id", "")
                result += await _fetch_blocks(bid, depth + 1, indent + 1)
        return result

    output += await _fetch_blocks(pid, 1, 0)
    return output


# ============================================================
# TOOLS — Group 4: Databases
# ============================================================


@mcp.tool()
async def get_database(database_id: str) -> str:
    """Get database schema — title, description, and all properties with types.

    Args:
        database_id: Database UUID.
    """
    did = _normalize_id(database_id)
    data = await api_get(f"/databases/{did}")
    if isinstance(data, str):
        return data

    title = _extract_plain_text(data.get("title", []))
    desc = _extract_plain_text(data.get("description", []))
    url = data.get("url", "")

    output = f"## Database: {title or 'Untitled'}\n\n"
    output += f"- **ID:** {data.get('id', '')}\n"
    output += f"- **URL:** {url}\n"
    if desc:
        output += f"- **Description:** {desc}\n"

    props = data.get("properties", {})
    if props:
        output += f"\n### Properties ({len(props)})\n\n"
        output += "| Property | Type | Config |\n| --- | --- | --- |\n"
        for name, prop in props.items():
            prop_type = prop.get("type", "")
            config = ""
            if prop_type == "select":
                options = prop.get("select", {}).get("options", [])
                config = ", ".join(o.get("name", "") for o in options[:10])
                if len(options) > 10:
                    config += f"... (+{len(options) - 10})"
            elif prop_type == "multi_select":
                options = prop.get("multi_select", {}).get("options", [])
                config = ", ".join(o.get("name", "") for o in options[:10])
            elif prop_type == "status":
                groups = prop.get("status", {}).get("groups", [])
                all_opts = []
                for g in groups:
                    all_opts.extend(o.get("name", "") for o in g.get("options", []))
                config = ", ".join(all_opts[:10])
            elif prop_type == "formula":
                config = prop.get("formula", {}).get("expression", "")[:50]
            elif prop_type == "relation":
                config = f"→ {prop.get('relation', {}).get('database_id', '')}"
            output += f"| {name} | {prop_type} | {config} |\n"

    return output


@mcp.tool()
async def query_database(
    database_id: str,
    filter_json: str = "",
    sort_json: str = "",
    page_size: int = 100,
) -> str:
    """Query a database with optional filtering and sorting. Auto-paginates.

    Args:
        database_id: Database UUID.
        filter_json: JSON string of Notion filter object. Example: {"property": "Status", "select": {"equals": "Done"}}
        sort_json: JSON string of Notion sort array. Example: [{"property": "Date", "direction": "descending"}]
        page_size: Results per page (auto-paginates for all results).
    """
    did = _normalize_id(database_id)
    body = {"page_size": min(page_size, 100)}

    if filter_json:
        try:
            body["filter"] = json.loads(filter_json)
        except json.JSONDecodeError:
            return f"Error: Invalid JSON in filter_json."

    if sort_json:
        try:
            body["sorts"] = json.loads(sort_json)
        except json.JSONDecodeError:
            return f"Error: Invalid JSON in sort_json."

    data = await _paginate_post(f"/databases/{did}/query", body)
    if isinstance(data, str):
        return data

    if not data:
        return "## Database Query\n\nNo results found.\n"

    # Format results as a table
    # Collect all property names across all rows
    all_props = set()
    for item in data:
        all_props.update(item.get("properties", {}).keys())

    # Build table rows
    results = []
    for item in data:
        row = {"ID": item.get("id", "")}
        props = item.get("properties", {})
        for name in sorted(all_props):
            if name in props:
                row[name] = _format_property_value(props[name])
            else:
                row[name] = ""
        results.append(row)

    return format_json(results, title=f"Database Query ({len(results)} results)")


@mcp.tool()
async def update_database(
    database_id: str,
    title: str = "",
    description: str = "",
    properties_json: str = "",
) -> str:
    """Update database title, description, and/or property schema.

    Args:
        database_id: Database UUID.
        title: New title (empty = don't change).
        description: New description (empty = don't change).
        properties_json: JSON string of property schema updates (add/rename/reconfigure).
    """
    did = _normalize_id(database_id)
    body = {}

    if title:
        body["title"] = _rich_text_array(title)
    if description:
        body["description"] = _rich_text_array(description)
    if properties_json:
        try:
            body["properties"] = json.loads(properties_json)
        except json.JSONDecodeError:
            return "Error: Invalid JSON in properties_json."

    if not body:
        return "Error: Nothing to update. Provide title, description, or properties_json."

    data = await api_patch(f"/databases/{did}", body)
    if isinstance(data, str):
        return data

    new_title = _extract_plain_text(data.get("title", []))
    return f"## Database Updated\n\n- **Title:** {new_title}\n- **ID:** {did}\n- **URL:** {data.get('url', '')}\n"


@mcp.tool()
async def create_database(
    parent_id: str,
    title: str,
    properties_json: str,
    parent_type: str = "page",
) -> str:
    """Create a new inline database inside a page.

    Args:
        parent_id: Parent page ID.
        title: Database title.
        properties_json: JSON string of property definitions.
        parent_type: Always 'page' (databases must be inside pages).
    """
    pid = _normalize_id(parent_id)

    try:
        props = json.loads(properties_json)
    except json.JSONDecodeError:
        return "Error: Invalid JSON in properties_json."

    body = {
        "parent": {"page_id": pid},
        "title": _rich_text_array(title),
        "properties": props,
    }

    data = await api_post("/databases", body)
    if isinstance(data, str):
        return data

    return f"## Database Created\n\n- **Title:** {title}\n- **ID:** {data.get('id', '')}\n- **URL:** {data.get('url', '')}\n"


# ============================================================
# TOOLS — Group 5: Comments
# ============================================================


@mcp.tool()
async def get_comments(block_id: str, page_size: int = 100) -> str:
    """Get all comments on a page or block. Auto-paginates.

    Args:
        block_id: Page ID or block ID to get comments for.
        page_size: Results per page.
    """
    bid = _normalize_id(block_id)
    data = await _paginate_get(
        "/comments",
        params={"block_id": bid, "page_size": min(page_size, 100)},
    )
    if isinstance(data, str):
        return data

    if not data:
        return "## Comments\n\nNo comments found.\n"

    output = f"## Comments ({len(data)})\n\n"
    for i, comment in enumerate(data):
        text = _extract_plain_text(comment.get("rich_text", []))
        created = comment.get("created_time", "")[:10]
        author = comment.get("created_by", {}).get("name", comment.get("created_by", {}).get("id", ""))
        output += f"{i + 1}. **{author}** ({created}): {text}\n"

    return output


@mcp.tool()
async def add_comment(page_id: str, text: str) -> str:
    """Add a discussion comment to a page.

    Args:
        page_id: Page to comment on.
        text: Comment text (plain text).
    """
    pid = _normalize_id(page_id)
    body = {
        "parent": {"page_id": pid},
        "rich_text": _rich_text_array(text),
    }

    data = await api_post("/comments", body)
    if isinstance(data, str):
        return data

    return f"## Comment Added\n\n- **Page:** {pid}\n- **Comment ID:** {data.get('id', '')}\n- **Text:** {text[:100]}\n"


# ============================================================
# TOOLS — Group 6: Users
# ============================================================


@mcp.tool()
async def get_user(user_id: str) -> str:
    """Get a user's name, email, and type.

    Args:
        user_id: User UUID.
    """
    uid = _normalize_id(user_id)
    data = await api_get(f"/users/{uid}")
    if isinstance(data, str):
        return data

    output = "## User\n\n"
    output += f"- **Name:** {data.get('name', '')}\n"
    output += f"- **ID:** {data.get('id', '')}\n"
    output += f"- **Type:** {data.get('type', '')}\n"
    if data.get("type") == "person":
        output += f"- **Email:** {data.get('person', {}).get('email', '')}\n"
    return output


@mcp.tool()
async def list_users(page_size: int = 100) -> str:
    """List all users in the workspace. Auto-paginates.

    Args:
        page_size: Results per page.
    """
    data = await _paginate_get(
        "/users",
        params={"page_size": min(page_size, 100)},
    )
    if isinstance(data, str):
        return data

    results = []
    for user in data:
        results.append({
            "Name": user.get("name", ""),
            "Type": user.get("type", ""),
            "ID": user.get("id", ""),
            "Email": user.get("person", {}).get("email", "") if user.get("type") == "person" else "",
        })

    return format_json(results, title=f"Users ({len(results)})")


# ============================================================
# TOOLS — Group 7: Higher-Level Business Tools
# ============================================================


@mcp.tool()
async def create_page_with_content(
    parent_id: str,
    title: str,
    content_markdown: str,
    parent_type: str = "page",
    properties_json: str = "",
) -> str:
    """Create a new page with full content in one call.
    Combines create_page + append_markdown. Auto-chunks blocks.

    Args:
        parent_id: Parent page or database ID.
        title: Page title.
        content_markdown: Full page content in simplified markdown.
        parent_type: 'page' or 'database'.
        properties_json: Additional database properties as JSON.
    """
    pid = _normalize_id(parent_id)
    blocks = _parse_markdown(content_markdown)

    # Build the create body
    body = {}
    if parent_type == "database":
        body["parent"] = {"database_id": pid}
        props = {}
        if properties_json:
            try:
                props = json.loads(properties_json)
            except json.JSONDecodeError:
                return f"Error: Invalid JSON in properties_json."
        has_title = any(
            isinstance(v, dict) and v.get("title") is not None
            for v in props.values()
        )
        if not has_title:
            props["Name"] = {"title": _rich_text_array(title)}
        body["properties"] = props
    else:
        body["parent"] = {"page_id": pid}
        body["properties"] = {"title": {"title": _rich_text_array(title)}}
        if properties_json:
            try:
                extra_props = json.loads(properties_json)
                body["properties"].update(extra_props)
            except json.JSONDecodeError:
                return f"Error: Invalid JSON in properties_json."

    # Include first 100 blocks in create call
    if blocks:
        body["children"] = blocks[:MAX_BLOCKS_PER_APPEND]

    data = await api_post("/pages", body)
    if isinstance(data, str):
        return data

    new_id = data.get("id", "")
    new_url = data.get("url", "")
    total_blocks = len(blocks)
    appended = min(total_blocks, MAX_BLOCKS_PER_APPEND)

    # Append remaining blocks in chunks
    if total_blocks > MAX_BLOCKS_PER_APPEND:
        remaining = blocks[MAX_BLOCKS_PER_APPEND:]
        chunks = _chunk_blocks(remaining)
        for chunk in chunks:
            result = await api_patch(f"/blocks/{new_id}/children", {"children": chunk})
            if isinstance(result, str):
                return f"## Page Created (partial)\n\n- **ID:** {new_id}\n- **URL:** {new_url}\n- **Blocks:** {appended}/{total_blocks}\n- **Error:** {result}\n"
            appended += len(chunk)

    output = f"## Page Created\n\n"
    output += f"- **Title:** {title}\n"
    output += f"- **ID:** {new_id}\n"
    output += f"- **URL:** {new_url}\n"
    output += f"- **Blocks:** {appended}\n"

    return output


@mcp.tool()
async def replace_page_content(page_id: str, content_markdown: str) -> str:
    """Replace all content on a page with new markdown content.
    Deletes all existing blocks, then appends new content. Use with caution.

    Args:
        page_id: Page whose content to replace.
        content_markdown: New content in simplified markdown.
    """
    pid = _normalize_id(page_id)

    # Delete existing blocks
    del_result = await delete_all_blocks(pid)
    deleted_count = 0
    if "Deleted:" in del_result:
        try:
            deleted_count = int(del_result.split("Deleted:")[1].split("block")[0].strip())
        except (ValueError, IndexError):
            pass

    # Append new content
    blocks = _parse_markdown(content_markdown)
    if not blocks:
        return f"## Page Content Replaced\n\n- **Page:** {pid}\n- **Deleted:** {deleted_count} blocks\n- **Added:** 0 blocks\n"

    total = len(blocks)
    chunks = _chunk_blocks(blocks)
    appended = 0

    for chunk in chunks:
        result = await api_patch(f"/blocks/{pid}/children", {"children": chunk})
        if isinstance(result, str):
            return f"## Page Content Replaced (partial)\n\n- **Deleted:** {deleted_count}\n- **Added:** {appended}/{total}\n- **Error:** {result}\n"
        appended += len(chunk)

    return f"## Page Content Replaced\n\n- **Page:** {pid}\n- **Deleted:** {deleted_count} blocks\n- **Added:** {appended} blocks\n"


@mcp.tool()
async def find_or_create_page(
    parent_id: str,
    title: str,
    parent_type: str = "page",
    properties_json: str = "",
) -> str:
    """Search for a page by title — return if found, create if not.
    Prevents duplicate pages. Uses search to find existing pages.

    Args:
        parent_id: Parent page or database ID.
        title: Page title to search for / create.
        parent_type: 'page' or 'database'.
        properties_json: Properties for new page (only used if creating).
    """
    # Search for existing page
    body = {"query": title, "page_size": 10}
    body["filter"] = {"value": "page", "property": "object"}

    results = await _paginate_post("/search", body)
    if isinstance(results, str):
        # Search failed, try creating anyway
        return await create_page(parent_id, title, parent_type, properties_json)

    pid = _normalize_id(parent_id)

    # Check if any result matches the title and parent
    for item in results:
        # Check title match
        item_title = ""
        for prop in item.get("properties", {}).values():
            if prop.get("type") == "title":
                item_title = _extract_plain_text(prop.get("title", []))
                break

        if item_title.strip().lower() != title.strip().lower():
            continue

        # Check parent match
        parent = item.get("parent", {})
        parent_type_key = parent.get("type", "")
        parent_val = parent.get(parent_type_key, "")
        if isinstance(parent_val, str):
            parent_val = parent_val.replace("-", "")

        if parent_val == pid:
            # Found matching page
            return f"## Page Found (existing)\n\n- **Status:** found\n- **Title:** {item_title}\n- **ID:** {item.get('id', '')}\n- **URL:** {item.get('url', '')}\n"

    # Not found — create
    result = await create_page(parent_id, title, parent_type, properties_json)
    if result.startswith("Error"):
        return result

    return result.replace("## Page Created", "## Page Created (new)")


@mcp.tool()
async def delete_all_blocks(page_id: str) -> str:
    """Clear all blocks from a page by deleting each top-level block.

    Args:
        page_id: Page to clear.
    """
    pid = _normalize_id(page_id)

    blocks = await _paginate_get(
        f"/blocks/{pid}/children",
        params={"page_size": 100},
    )
    if isinstance(blocks, str):
        return f"Error fetching blocks: {blocks}"

    if not blocks:
        return f"## Blocks Cleared\n\n- **Page:** {pid}\n- **Deleted:** 0 blocks (page was already empty)\n"

    deleted = 0
    for block in blocks:
        bid = block.get("id", "")
        result = await api_delete(f"/blocks/{bid}")
        if isinstance(result, str) and result.startswith("Error"):
            return f"## Blocks Cleared (partial)\n\n- **Page:** {pid}\n- **Deleted:** {deleted}/{len(blocks)} blocks\n- **Error:** {result}\n"
        deleted += 1

    return f"## Blocks Cleared\n\n- **Page:** {pid}\n- **Deleted:** {deleted} blocks\n"


@mcp.tool()
async def get_child_pages(page_id: str) -> str:
    """List all child pages under a parent page.

    Args:
        page_id: Parent page ID.
    """
    pid = _normalize_id(page_id)
    blocks = await _paginate_get(
        f"/blocks/{pid}/children",
        params={"page_size": 100},
    )
    if isinstance(blocks, str):
        return blocks

    child_pages = []
    for block in blocks:
        if block.get("type") == "child_page":
            child_pages.append({
                "Title": block.get("child_page", {}).get("title", "Untitled"),
                "Page ID": block.get("id", ""),
                "Last Edited": block.get("last_edited_time", "")[:10],
            })
        elif block.get("type") == "child_database":
            child_pages.append({
                "Title": block.get("child_database", {}).get("title", "Untitled"),
                "Page ID": block.get("id", ""),
                "Last Edited": block.get("last_edited_time", "")[:10],
            })

    if not child_pages:
        return f"## Child Pages\n\nNo child pages found under {pid}.\n"

    return format_json(child_pages, title=f"Child Pages ({len(child_pages)})")


# --- Main ---

if __name__ == "__main__":
    mcp.run(transport="stdio")
