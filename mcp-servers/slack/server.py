"""
Slack MCP Server
Multi-workspace Slack Web API access with workspace aliases.
Single server handles multiple workspaces via a workspace parameter.

Base URL: https://slack.com/api/
Auth: Bot token (xoxb-) per workspace via Authorization header
Env: SLACK_WORKSPACE_{N}_BOT_TOKEN, _TEAM_ID, _NAME, _ALIASES
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

mcp = FastMCP("slack")

# --- Constants ---

BASE_URL = "https://slack.com/api"
RATE_LIMIT_DELAY = 1.0  # Slack Tier 2: ~1 request/second

_last_request_time = 0.0
_rate_lock = asyncio.Lock()


# --- Workspace Registry ---

WORKSPACES: dict[str, dict] = {}


def _build_workspace_registry():
    """Build workspace name/alias -> config mapping from env vars.
    Scans SLACK_WORKSPACE_1_*, SLACK_WORKSPACE_2_*, etc."""
    i = 1
    while True:
        token = os.environ.get(f"SLACK_WORKSPACE_{i}_BOT_TOKEN")
        if not token:
            break
        team_id = os.environ.get(f"SLACK_WORKSPACE_{i}_TEAM_ID", "")
        name = os.environ.get(
            f"SLACK_WORKSPACE_{i}_NAME", f"workspace{i}"
        ).strip().lower()
        aliases_str = os.environ.get(f"SLACK_WORKSPACE_{i}_ALIASES", "")

        config = {"token": token, "team_id": team_id, "name": name}
        WORKSPACES[name] = config

        for alias in aliases_str.split(","):
            alias = alias.strip().lower()
            if alias and alias not in WORKSPACES:
                WORKSPACES[alias] = config

        i += 1


_build_workspace_registry()


def _resolve_workspace(workspace: str) -> dict | str:
    """Resolve workspace name/alias to config dict. Returns error string if not found."""
    ws = workspace.strip().lower()
    if ws in WORKSPACES:
        return WORKSPACES[ws]
    available = sorted(set(c["name"] for c in WORKSPACES.values()))
    all_aliases = sorted(WORKSPACES.keys())
    return (
        f"Error: Unknown workspace '{workspace}'. "
        f"Available workspaces: {', '.join(available)}. "
        f"All accepted names/aliases: {', '.join(all_aliases)}."
    )


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


async def slack_api(
    workspace: str, method: str, params: dict | None = None
) -> dict | str:
    """Call a Slack Web API method via POST with JSON body.
    Returns parsed JSON dict on success, error string on failure."""
    config = _resolve_workspace(workspace)
    if isinstance(config, str):
        return config

    await _rate_limit()

    headers = {
        "Authorization": f"Bearer {config['token']}",
        "Content-Type": "application/json; charset=utf-8",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/{method}", headers=headers, json=params or {}
            )
    except httpx.TimeoutException:
        return f"Error: Request timed out (30s). Method: {method}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code == 429:
        retry = response.headers.get("Retry-After", "30")
        return f"Error: Rate limited (429). Retry after {retry}s."
    if response.status_code != 200:
        return (
            f"Error: HTTP {response.status_code}. Method: {method}. "
            f"Body: {response.text[:300]}"
        )

    try:
        data = response.json()
    except json.JSONDecodeError:
        return f"Error: Invalid JSON response from Slack. Method: {method}"

    if not data.get("ok"):
        error = data.get("error", "unknown")
        needed = data.get("needed", "")
        provided = data.get("provided", "")
        msg = f"Error: Slack API — {error}. Method: {method}"
        if needed:
            msg += f" (needed scope: {needed}, provided: {provided})"
        return msg

    return data


async def slack_api_form(
    workspace: str, method: str, data: dict | None = None
) -> dict | str:
    """Call Slack Web API method via POST with form data (for file uploads)."""
    config = _resolve_workspace(workspace)
    if isinstance(config, str):
        return config

    await _rate_limit()

    headers = {"Authorization": f"Bearer {config['token']}"}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BASE_URL}/{method}", headers=headers, data=data or {}
            )
    except httpx.TimeoutException:
        return f"Error: Request timed out (60s). Method: {method}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code != 200:
        return f"Error: HTTP {response.status_code}. Method: {method}"

    try:
        result = response.json()
    except json.JSONDecodeError:
        return f"Error: Invalid JSON response. Method: {method}"

    if not result.get("ok"):
        return f"Error: Slack API — {result.get('error', 'unknown')}. Method: {method}"

    return result


async def slack_api_get(
    workspace: str, method: str, params: dict | None = None
) -> dict | str:
    """Call Slack Web API method via GET (for search endpoints)."""
    config = _resolve_workspace(workspace)
    if isinstance(config, str):
        return config

    await _rate_limit()

    headers = {"Authorization": f"Bearer {config['token']}"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BASE_URL}/{method}", headers=headers, params=params or {}
            )
    except httpx.TimeoutException:
        return f"Error: Request timed out (30s). Method: {method}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code != 200:
        return f"Error: HTTP {response.status_code}. Method: {method}"

    try:
        data = response.json()
    except json.JSONDecodeError:
        return f"Error: Invalid JSON response. Method: {method}"

    if not data.get("ok"):
        error = data.get("error", "unknown")
        return f"Error: Slack API — {error}. Method: {method}"

    return data


# --- Channel Resolution ---

_channel_cache: dict[str, dict[str, str]] = {}


async def _resolve_channel(workspace: str, channel: str) -> str:
    """Resolve channel name to channel ID. Passes through if already an ID.
    Accepts: channel ID (C01ABC...), channel name (general), or #channel (#general)."""
    channel = channel.strip().lstrip("#")

    # If it looks like a channel ID, use directly
    if len(channel) >= 9 and channel[0] in "CGDW" and all(
        c.isalnum() for c in channel
    ):
        return channel

    # Look up by name
    config = _resolve_workspace(workspace)
    if isinstance(config, str):
        return channel  # Can't resolve, pass through

    ws_key = config["name"]
    if ws_key not in _channel_cache:
        result = await slack_api(workspace, "conversations.list", {
            "types": "public_channel,private_channel",
            "limit": 1000,
            "exclude_archived": True,
        })
        if isinstance(result, dict) and result.get("ok"):
            _channel_cache[ws_key] = {}
            for ch in result.get("channels", []):
                name = ch.get("name", "").lower()
                if name:
                    _channel_cache[ws_key][name] = ch["id"]
        else:
            return channel  # Can't resolve, pass through

    resolved = _channel_cache.get(ws_key, {}).get(channel.lower())
    if resolved:
        return resolved

    return channel  # Not found in cache, pass through (let API error if invalid)


def _invalidate_channel_cache(workspace: str):
    """Clear channel cache for a workspace (call after channel changes)."""
    config = _resolve_workspace(workspace)
    if isinstance(config, dict):
        _channel_cache.pop(config["name"], None)


# --- Format Helpers ---


def _format_message(msg: dict) -> str:
    """Format a single Slack message for display."""
    user = msg.get("user", msg.get("bot_id", "unknown"))
    text = msg.get("text", "")
    ts = msg.get("ts", "")
    thread_ts = msg.get("thread_ts", "")
    reply_count = msg.get("reply_count", 0)

    parts = [f"**{user}** (`{ts}`)"]
    if text:
        parts.append(text)
    if thread_ts and thread_ts != ts:
        parts.append(f"_Thread: {thread_ts}_")
    if reply_count:
        parts.append(f"_({reply_count} replies)_")

    return "\n".join(parts)


def _format_channel(ch: dict) -> str:
    """Format a single channel for display."""
    name = ch.get("name", "")
    cid = ch.get("id", "")
    topic = ch.get("topic", {}).get("value", "")
    members = ch.get("num_members", 0)
    is_private = ch.get("is_private", False)

    prefix = "private" if is_private else "#"
    line = f"{prefix} **{name}** (`{cid}`) — {members} members"
    if topic:
        line += f"\n  Topic: {topic}"
    return line


def _format_user(user: dict) -> str:
    """Format a single user for display."""
    name = user.get("real_name", user.get("name", ""))
    uid = user.get("id", "")
    display = user.get("profile", {}).get("display_name", "")
    title = user.get("profile", {}).get("title", "")
    is_bot = user.get("is_bot", False)

    line = f"**{name}**"
    if display and display != name:
        line += f" ({display})"
    line += f" — `{uid}`"
    if title:
        line += f" — {title}"
    if is_bot:
        line += " [bot]"
    return line


# --- Tools: Utility ---


@mcp.tool()
async def list_workspaces() -> str:
    """List all configured Slack workspaces and their aliases.
    Shows which workspace names you can use in the workspace parameter."""
    seen: dict[str, dict] = {}
    for key, config in WORKSPACES.items():
        name = config["name"]
        if name not in seen:
            seen[name] = {"team_id": config["team_id"], "aliases": []}
        if key != name:
            seen[name]["aliases"].append(key)

    if not seen:
        return (
            "No Slack workspaces configured. "
            "Add SLACK_WORKSPACE_1_BOT_TOKEN to .env."
        )

    output = "## Configured Slack Workspaces\n\n"
    for name, info in seen.items():
        output += f"- **{name}** (Team: `{info['team_id']}`)"
        if info["aliases"]:
            output += f" — aliases: {', '.join(info['aliases'])}"
        output += "\n"
    return output


# --- Tools: Channels ---


@mcp.tool()
async def list_channels(
    workspace: str,
    limit: int = 100,
    types: str = "public_channel",
    cursor: str = "",
) -> str:
    """List channels in a Slack workspace.

    workspace: Workspace name or alias (e.g. 'craft', 'craftiloo').
    limit: Max channels to return (default 100, max 1000).
    types: Comma-separated channel types: public_channel, private_channel, mpim, im.
    cursor: Pagination cursor from previous response (leave empty for first page)."""
    params: dict = {
        "types": types,
        "limit": min(limit, 1000),
        "exclude_archived": True,
    }
    if cursor:
        params["cursor"] = cursor

    data = await slack_api(workspace, "conversations.list", params)
    if isinstance(data, str):
        return data

    channels = data.get("channels", [])
    next_cursor = data.get("response_metadata", {}).get("next_cursor", "")

    if not channels:
        return f"No channels found in workspace '{workspace}'."

    output = f"## Channels ({len(channels)})\n\n"
    for ch in channels:
        output += _format_channel(ch) + "\n"

    if next_cursor:
        output += (
            f"\n_More channels available. "
            f"Use cursor='{next_cursor}' for next page._"
        )

    return output


@mcp.tool()
async def get_channel_info(
    workspace: str,
    channel: str,
) -> str:
    """Get detailed information about a channel (topic, purpose, members, creation).

    workspace: Workspace name or alias.
    channel: Channel name (e.g. 'general') or ID (e.g. 'C01ABC123')."""
    channel_id = await _resolve_channel(workspace, channel)

    data = await slack_api_get(workspace, "conversations.info", {
        "channel": channel_id,
    })
    if isinstance(data, str):
        return data

    ch = data.get("channel", {})
    topic = ch.get("topic", {}).get("value", "")
    purpose = ch.get("purpose", {}).get("value", "")
    created = ch.get("created", "")
    creator = ch.get("creator", "")
    members = ch.get("num_members", 0)
    is_private = ch.get("is_private", False)
    is_archived = ch.get("is_archived", False)

    output = f"## Channel: #{ch.get('name', '')}\n\n"
    output += f"- **ID:** `{ch.get('id', '')}`\n"
    output += f"- **Type:** {'Private' if is_private else 'Public'}\n"
    output += f"- **Members:** {members}\n"
    output += f"- **Created:** {created}\n"
    output += f"- **Creator:** {creator}\n"
    if is_archived:
        output += "- **Status:** Archived\n"
    if topic:
        output += f"- **Topic:** {topic}\n"
    if purpose:
        output += f"- **Purpose:** {purpose}\n"

    return output


@mcp.tool()
async def set_channel_topic(
    workspace: str,
    channel: str,
    topic: str,
) -> str:
    """Set or update a channel's topic.

    workspace: Workspace name or alias.
    channel: Channel name or ID.
    topic: New topic text."""
    channel_id = await _resolve_channel(workspace, channel)

    data = await slack_api(workspace, "conversations.setTopic", {
        "channel": channel_id,
        "topic": topic,
    })
    if isinstance(data, str):
        return data

    return f"Topic updated for channel `{channel_id}`: {topic}"


# --- Tools: Messages ---


@mcp.tool()
async def post_message(
    workspace: str,
    channel: str,
    text: str,
) -> str:
    """Post a message to a Slack channel.

    workspace: Workspace name or alias.
    channel: Channel name (e.g. 'general') or ID (e.g. 'C01ABC123').
    text: Message text (supports Slack markdown: *bold*, _italic_, `code`, ```code block```)."""
    channel_id = await _resolve_channel(workspace, channel)

    data = await slack_api(workspace, "chat.postMessage", {
        "channel": channel_id,
        "text": text,
    })
    if isinstance(data, str):
        return data

    ts = data.get("ts", "")
    ch = data.get("channel", channel_id)
    return f"Message posted to `{ch}` at `{ts}`."


@mcp.tool()
async def reply_to_thread(
    workspace: str,
    channel: str,
    thread_ts: str,
    text: str,
) -> str:
    """Reply to a message thread in Slack.

    workspace: Workspace name or alias.
    channel: Channel name or ID.
    thread_ts: Timestamp of the parent message (e.g. '1234567890.123456').
    text: Reply text."""
    channel_id = await _resolve_channel(workspace, channel)

    data = await slack_api(workspace, "chat.postMessage", {
        "channel": channel_id,
        "thread_ts": thread_ts,
        "text": text,
    })
    if isinstance(data, str):
        return data

    ts = data.get("ts", "")
    return f"Reply posted in thread `{thread_ts}` at `{ts}`."


@mcp.tool()
async def add_reaction(
    workspace: str,
    channel: str,
    timestamp: str,
    emoji: str,
) -> str:
    """Add an emoji reaction to a message.

    workspace: Workspace name or alias.
    channel: Channel name or ID.
    timestamp: Message timestamp (e.g. '1234567890.123456').
    emoji: Emoji name without colons (e.g. 'thumbsup', 'white_check_mark')."""
    channel_id = await _resolve_channel(workspace, channel)

    data = await slack_api(workspace, "reactions.add", {
        "channel": channel_id,
        "timestamp": timestamp,
        "name": emoji.strip(":"),
    })
    if isinstance(data, str):
        return data

    return f"Reaction :{emoji.strip(':')}:  added to message `{timestamp}`."


@mcp.tool()
async def get_channel_history(
    workspace: str,
    channel: str,
    limit: int = 20,
) -> str:
    """Get recent messages from a Slack channel.

    workspace: Workspace name or alias.
    channel: Channel name or ID.
    limit: Number of messages to return (default 20, max 100)."""
    channel_id = await _resolve_channel(workspace, channel)

    data = await slack_api(workspace, "conversations.history", {
        "channel": channel_id,
        "limit": min(limit, 100),
    })
    if isinstance(data, str):
        return data

    messages = data.get("messages", [])
    if not messages:
        return "No messages found in channel."

    output = f"## Channel History ({len(messages)} messages)\n\n"
    for msg in messages:
        output += _format_message(msg) + "\n\n---\n\n"

    return output


@mcp.tool()
async def get_thread_replies(
    workspace: str,
    channel: str,
    thread_ts: str,
) -> str:
    """Get all replies in a message thread.

    workspace: Workspace name or alias.
    channel: Channel name or ID.
    thread_ts: Timestamp of the parent message."""
    channel_id = await _resolve_channel(workspace, channel)

    data = await slack_api_get(workspace, "conversations.replies", {
        "channel": channel_id,
        "ts": thread_ts,
        "limit": 100,
    })
    if isinstance(data, str):
        return data

    messages = data.get("messages", [])
    if not messages:
        return f"No replies found for thread `{thread_ts}`."

    output = f"## Thread Replies ({len(messages)} messages)\n\n"
    for msg in messages:
        output += _format_message(msg) + "\n\n---\n\n"

    return output


@mcp.tool()
async def search_messages(
    workspace: str,
    query: str,
    sort: str = "timestamp",
    count: int = 20,
) -> str:
    """Search messages across all channels in a workspace.
    NOTE: Requires a user token (xoxp-) with search:read scope. Bot tokens (xoxb-) cannot search.

    workspace: Workspace name or alias.
    query: Search query (supports Slack search operators: from:user, in:channel, has:emoji, before:date, after:date).
    sort: Sort by 'timestamp' (newest first) or 'score' (most relevant first).
    count: Number of results (default 20, max 100)."""
    data = await slack_api_get(workspace, "search.messages", {
        "query": query,
        "sort": sort,
        "sort_dir": "desc",
        "count": min(count, 100),
    })
    if isinstance(data, str):
        return data

    matches = data.get("messages", {}).get("matches", [])
    total = data.get("messages", {}).get("total", 0)

    if not matches:
        return f"No messages found for query: '{query}'"

    output = (
        f"## Search Results — '{query}' "
        f"({total} total, showing {len(matches)})\n\n"
    )
    for msg in matches:
        channel_name = msg.get("channel", {}).get("name", "")
        user = msg.get("username", msg.get("user", ""))
        text = msg.get("text", "")[:300]
        ts = msg.get("ts", "")
        permalink = msg.get("permalink", "")

        output += f"**{user}** in #{channel_name} (`{ts}`)\n"
        output += f"{text}\n"
        if permalink:
            output += f"[Link]({permalink})\n"
        output += "\n---\n\n"

    return output


# --- Tools: Users ---


@mcp.tool()
async def get_users(
    workspace: str,
    limit: int = 100,
    cursor: str = "",
) -> str:
    """List users in a Slack workspace.

    workspace: Workspace name or alias.
    limit: Max users to return (default 100, max 1000).
    cursor: Pagination cursor from previous response."""
    params: dict = {"limit": min(limit, 1000)}
    if cursor:
        params["cursor"] = cursor

    data = await slack_api(workspace, "users.list", params)
    if isinstance(data, str):
        return data

    members = data.get("members", [])
    next_cursor = data.get("response_metadata", {}).get("next_cursor", "")

    active = [u for u in members if not u.get("deleted", False)]

    if not active:
        return "No active users found."

    output = f"## Users ({len(active)} active)\n\n"
    for user in active:
        output += _format_user(user) + "\n"

    if next_cursor:
        output += (
            f"\n_More users available. "
            f"Use cursor='{next_cursor}' for next page._"
        )

    return output


@mcp.tool()
async def get_user_profile(
    workspace: str,
    user_id: str,
) -> str:
    """Get detailed profile for a specific user.

    workspace: Workspace name or alias.
    user_id: Slack user ID (e.g. 'U01ABC123')."""
    data = await slack_api_get(workspace, "users.profile.get", {"user": user_id})
    if isinstance(data, str):
        return data

    profile = data.get("profile", {})

    output = f"## User Profile — {user_id}\n\n"
    fields = {
        "Display Name": profile.get("display_name", ""),
        "Real Name": profile.get("real_name", ""),
        "Title": profile.get("title", ""),
        "Email": profile.get("email", ""),
        "Phone": profile.get("phone", ""),
        "Status": (
            f"{profile.get('status_emoji', '')} "
            f"{profile.get('status_text', '')}"
        ).strip(),
        "Timezone": profile.get("tz", ""),
    }

    for label, value in fields.items():
        if value:
            output += f"- **{label}:** {value}\n"

    return output


# --- Tools: Files ---


@mcp.tool()
async def upload_snippet(
    workspace: str,
    channels: str,
    content: str,
    filename: str = "snippet.txt",
    title: str = "",
    initial_comment: str = "",
) -> str:
    """Upload a text snippet or file content to Slack channel(s).

    workspace: Workspace name or alias.
    channels: Comma-separated channel names or IDs to share the file in.
    content: Text content to upload.
    filename: Filename (default 'snippet.txt'). Use extension for syntax highlighting (e.g. 'data.json', 'script.py').
    title: Optional title for the file.
    initial_comment: Optional message to post with the file."""
    channel_list = [c.strip() for c in channels.split(",")]
    resolved = []
    for ch in channel_list:
        resolved.append(await _resolve_channel(workspace, ch))
    channel_ids = ",".join(resolved)

    form_data: dict = {
        "channels": channel_ids,
        "content": content,
        "filename": filename,
    }
    if title:
        form_data["title"] = title
    if initial_comment:
        form_data["initial_comment"] = initial_comment

    data = await slack_api_form(workspace, "files.upload", form_data)
    if isinstance(data, str):
        return data

    file_info = data.get("file", {})
    fid = file_info.get("id", "")
    fname = file_info.get("name", filename)
    permalink = file_info.get("permalink", "")

    output = f"File uploaded: **{fname}** (`{fid}`)"
    if permalink:
        output += f"\n[View in Slack]({permalink})"
    return output


# --- Tools: Scheduled Messages ---


@mcp.tool()
async def schedule_message(
    workspace: str,
    channel: str,
    text: str,
    post_at: int,
) -> str:
    """Schedule a message to be posted at a future time.

    workspace: Workspace name or alias.
    channel: Channel name or ID.
    text: Message text.
    post_at: Unix timestamp for when to post (must be in the future, within 120 days)."""
    channel_id = await _resolve_channel(workspace, channel)

    data = await slack_api(workspace, "chat.scheduleMessage", {
        "channel": channel_id,
        "text": text,
        "post_at": post_at,
    })
    if isinstance(data, str):
        return data

    msg_id = data.get("scheduled_message_id", "")
    post_at_val = data.get("post_at", post_at)
    return (
        f"Message scheduled.\n"
        f"- **Scheduled Message ID:** `{msg_id}`\n"
        f"- **Channel:** `{channel_id}`\n"
        f"- **Post at:** {post_at_val}\n"
        f"\nUse `delete_scheduled_message` to cancel."
    )


@mcp.tool()
async def list_scheduled_messages(
    workspace: str,
    channel: str = "",
) -> str:
    """List pending scheduled messages.

    workspace: Workspace name or alias.
    channel: Optional channel name or ID to filter by."""
    params: dict = {}
    if channel:
        params["channel"] = await _resolve_channel(workspace, channel)

    data = await slack_api(workspace, "chat.scheduledMessages.list", params)
    if isinstance(data, str):
        return data

    messages = data.get("scheduled_messages", [])
    if not messages:
        return "No scheduled messages found."

    output = f"## Scheduled Messages ({len(messages)})\n\n"
    for msg in messages:
        output += (
            f"- **ID:** `{msg.get('id', '')}`\n"
            f"  Channel: `{msg.get('channel_id', '')}`\n"
            f"  Post at: {msg.get('post_at', '')}\n"
            f"  Text: {msg.get('text', '')[:100]}\n\n"
        )

    return output


@mcp.tool()
async def delete_scheduled_message(
    workspace: str,
    channel: str,
    scheduled_message_id: str,
) -> str:
    """Cancel a scheduled message before it's posted.

    workspace: Workspace name or alias.
    channel: Channel name or ID the message was scheduled in.
    scheduled_message_id: The ID from schedule_message or list_scheduled_messages."""
    channel_id = await _resolve_channel(workspace, channel)

    data = await slack_api(workspace, "chat.deleteScheduledMessage", {
        "channel": channel_id,
        "scheduled_message_id": scheduled_message_id,
    })
    if isinstance(data, str):
        return data

    return f"Scheduled message `{scheduled_message_id}` cancelled."


# --- Main ---

if __name__ == "__main__":
    mcp.run(transport="stdio")
