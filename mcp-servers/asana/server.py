"""
Asana MCP Server
Exposes Asana REST API endpoints as MCP tools for project/task management.
Auth: Personal Access Token (Bearer token).

Base URL: https://app.asana.com/api/1.0
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

mcp = FastMCP("asana")

# --- Constants ---

BASE_URL = "https://app.asana.com/api/1.0"
RATE_LIMIT_DELAY = 0.2  # Conservative: ~5 requests/second
MAX_PAGE_SIZE = 100
MAX_PAGINATION_PAGES = 10

_last_request_time = 0.0
_rate_lock = asyncio.Lock()


# --- Helper Functions ---


def _get_token() -> str:
    """Get Asana Personal Access Token from env."""
    token = os.environ.get("ASANA_PERSONAL_ACCESS_TOKEN", "")
    if not token:
        return ""
    return token


async def _rate_limit():
    """Enforce rate limiting between requests."""
    global _last_request_time
    async with _rate_lock:
        now = time.time()
        elapsed = now - _last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            await asyncio.sleep(RATE_LIMIT_DELAY - elapsed)
        _last_request_time = time.time()


async def _asana_get(
    path: str, params: dict | None = None
) -> dict | str:
    """Make a GET request to the Asana API.
    Returns parsed JSON dict on success, error string on failure."""
    token = _get_token()
    if not token:
        return "Error: ASANA_PERSONAL_ACCESS_TOKEN not set in .env"

    await _rate_limit()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BASE_URL}{path}", headers=headers, params=params or {}
            )
    except httpx.TimeoutException:
        return f"Error: Request timed out (30s). Path: {path}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code == 429:
        retry = response.headers.get("Retry-After", "30")
        return f"Error: Rate limited (429). Retry after {retry}s."
    if response.status_code == 404:
        return f"Error: Not found (404). Path: {path}"
    if response.status_code == 403:
        return f"Error: Forbidden (403). Check token permissions. Path: {path}"
    if response.status_code not in (200, 201):
        body = response.text[:300] if response.text else ""
        return (
            f"Error: HTTP {response.status_code}. Path: {path}. "
            f"Body: {body}"
        )

    try:
        data = response.json()
    except json.JSONDecodeError:
        return f"Error: Invalid JSON response. Path: {path}"

    if "errors" in data:
        errors = data["errors"]
        msgs = [e.get("message", str(e)) for e in errors]
        return f"Error: Asana API — {'; '.join(msgs)}"

    return data


async def _asana_post(
    path: str, body: dict | None = None
) -> dict | str:
    """Make a POST request to the Asana API."""
    token = _get_token()
    if not token:
        return "Error: ASANA_PERSONAL_ACCESS_TOKEN not set in .env"

    await _rate_limit()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}{path}", headers=headers, json=body or {}
            )
    except httpx.TimeoutException:
        return f"Error: Request timed out (30s). Path: {path}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code == 429:
        retry = response.headers.get("Retry-After", "30")
        return f"Error: Rate limited (429). Retry after {retry}s."
    if response.status_code not in (200, 201):
        body_text = response.text[:300] if response.text else ""
        return (
            f"Error: HTTP {response.status_code}. Path: {path}. "
            f"Body: {body_text}"
        )

    try:
        data = response.json()
    except json.JSONDecodeError:
        return f"Error: Invalid JSON response. Path: {path}"

    if "errors" in data:
        errors = data["errors"]
        msgs = [e.get("message", str(e)) for e in errors]
        return f"Error: Asana API — {'; '.join(msgs)}"

    return data


async def _asana_put(
    path: str, body: dict | None = None
) -> dict | str:
    """Make a PUT request to the Asana API."""
    token = _get_token()
    if not token:
        return "Error: ASANA_PERSONAL_ACCESS_TOKEN not set in .env"

    await _rate_limit()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(
                f"{BASE_URL}{path}", headers=headers, json=body or {}
            )
    except httpx.TimeoutException:
        return f"Error: Request timed out (30s). Path: {path}"
    except httpx.RequestError as e:
        return f"Error: Request failed — {e}"

    if response.status_code == 429:
        retry = response.headers.get("Retry-After", "30")
        return f"Error: Rate limited (429). Retry after {retry}s."
    if response.status_code not in (200, 201):
        body_text = response.text[:300] if response.text else ""
        return (
            f"Error: HTTP {response.status_code}. Path: {path}. "
            f"Body: {body_text}"
        )

    try:
        data = response.json()
    except json.JSONDecodeError:
        return f"Error: Invalid JSON response. Path: {path}"

    if "errors" in data:
        errors = data["errors"]
        msgs = [e.get("message", str(e)) for e in errors]
        return f"Error: Asana API — {'; '.join(msgs)}"

    return data


async def _asana_delete(path: str) -> dict | str:
    """Make a DELETE request to the Asana API."""
    token = _get_token()
    if not token:
        return "Error: ASANA_PERSONAL_ACCESS_TOKEN not set in .env"

    await _rate_limit()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

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
        retry = response.headers.get("Retry-After", "30")
        return f"Error: Rate limited (429). Retry after {retry}s."
    if response.status_code not in (200, 201):
        body_text = response.text[:300] if response.text else ""
        return (
            f"Error: HTTP {response.status_code}. Path: {path}. "
            f"Body: {body_text}"
        )

    return {"data": {}}


async def _paginate_get(
    path: str, params: dict | None = None, max_pages: int = MAX_PAGINATION_PAGES
) -> list | str:
    """Auto-paginate a GET endpoint that returns a list. Returns combined items."""
    params = dict(params or {})
    params.setdefault("limit", MAX_PAGE_SIZE)
    all_items: list = []

    for _ in range(max_pages):
        data = await _asana_get(path, params)
        if isinstance(data, str):
            return data

        items = data.get("data", [])
        all_items.extend(items)

        next_page = data.get("next_page")
        if not next_page or not next_page.get("offset"):
            break
        params["offset"] = next_page["offset"]

    return all_items


# --- Format Helpers ---


def _format_task(task: dict, detail: bool = False) -> str:
    """Format a task for display."""
    name = task.get("name", "(untitled)")
    gid = task.get("gid", "")
    completed = task.get("completed", False)
    status = "[x]" if completed else "[ ]"
    due = task.get("due_on") or task.get("due_at") or ""
    assignee = task.get("assignee")
    assignee_name = assignee.get("name", "") if isinstance(assignee, dict) else ""

    line = f"- {status} **{name}** (`{gid}`)"
    if due:
        line += f" — due: {due}"
    if assignee_name:
        line += f" — @{assignee_name}"

    if detail:
        notes = task.get("notes", "")
        if notes:
            # Truncate long notes
            if len(notes) > 500:
                notes = notes[:500] + "..."
            line += f"\n  Notes: {notes}"

        tags = task.get("tags", [])
        if tags:
            tag_names = [t.get("name", "") for t in tags if t.get("name")]
            if tag_names:
                line += f"\n  Tags: {', '.join(tag_names)}"

        memberships = task.get("memberships", [])
        if memberships:
            sections = []
            for m in memberships:
                section = m.get("section", {})
                if section and section.get("name"):
                    sections.append(section["name"])
            if sections:
                line += f"\n  Section: {', '.join(sections)}"

        custom_fields = task.get("custom_fields", [])
        if custom_fields:
            cf_parts = []
            for cf in custom_fields:
                cf_name = cf.get("name", "")
                cf_val = cf.get("display_value") or cf.get("text_value") or cf.get("number_value")
                if cf_name and cf_val is not None:
                    cf_parts.append(f"{cf_name}: {cf_val}")
            if cf_parts:
                line += f"\n  Custom fields: {'; '.join(cf_parts)}"

    return line


def _format_project(project: dict) -> str:
    """Format a project for display."""
    name = project.get("name", "(untitled)")
    gid = project.get("gid", "")
    archived = project.get("archived", False)
    color = project.get("color", "")

    line = f"- **{name}** (`{gid}`)"
    if archived:
        line += " [archived]"
    if color:
        line += f" [{color}]"
    return line


# --- Tools: User & Workspace ---


@mcp.tool()
async def get_me() -> str:
    """Get the current authenticated Asana user's info.
    Useful for verifying the connection and getting your user GID."""
    data = await _asana_get("/users/me", {"opt_fields": "name,email,workspaces,workspaces.name"})
    if isinstance(data, str):
        return data

    user = data.get("data", {})
    output = "## Current User\n\n"
    output += f"- **Name:** {user.get('name', '')}\n"
    output += f"- **GID:** `{user.get('gid', '')}`\n"
    output += f"- **Email:** {user.get('email', '')}\n"

    workspaces = user.get("workspaces", [])
    if workspaces:
        output += "\n**Workspaces:**\n"
        for ws in workspaces:
            output += f"- {ws.get('name', '')} (`{ws.get('gid', '')}`)\n"

    return output


@mcp.tool()
async def list_workspaces() -> str:
    """List all Asana workspaces the authenticated user belongs to."""
    items = await _paginate_get("/workspaces", {"opt_fields": "name,is_organization"})
    if isinstance(items, str):
        return items

    if not items:
        return "No workspaces found."

    output = f"## Workspaces ({len(items)})\n\n"
    for ws in items:
        name = ws.get("name", "")
        gid = ws.get("gid", "")
        is_org = ws.get("is_organization", False)
        kind = "Organization" if is_org else "Workspace"
        output += f"- **{name}** (`{gid}`) — {kind}\n"

    return output


@mcp.tool()
async def list_users(
    workspace_gid: str,
) -> str:
    """List users in an Asana workspace.

    workspace_gid: The workspace GID (get from list_workspaces)."""
    items = await _paginate_get(
        f"/workspaces/{workspace_gid}/users",
        {"opt_fields": "name,email"}
    )
    if isinstance(items, str):
        return items

    if not items:
        return "No users found."

    output = f"## Users ({len(items)})\n\n"
    for user in items:
        name = user.get("name", "")
        gid = user.get("gid", "")
        email = user.get("email", "")
        output += f"- **{name}** (`{gid}`)"
        if email:
            output += f" — {email}"
        output += "\n"

    return output


# --- Tools: Teams ---


@mcp.tool()
async def list_teams(
    workspace_gid: str,
) -> str:
    """List teams in an Asana organization/workspace.

    workspace_gid: The workspace GID."""
    items = await _paginate_get(
        f"/organizations/{workspace_gid}/teams",
        {"opt_fields": "name,description"}
    )
    if isinstance(items, str):
        return items

    if not items:
        return "No teams found (teams are only available in organizations)."

    output = f"## Teams ({len(items)})\n\n"
    for team in items:
        name = team.get("name", "")
        gid = team.get("gid", "")
        desc = team.get("description", "")
        output += f"- **{name}** (`{gid}`)"
        if desc:
            output += f" — {desc[:100]}"
        output += "\n"

    return output


# --- Tools: Projects ---


@mcp.tool()
async def list_projects(
    workspace_gid: str,
    team_gid: str = "",
    archived: bool = False,
) -> str:
    """List projects in an Asana workspace, optionally filtered by team.

    workspace_gid: The workspace GID.
    team_gid: Optional team GID to filter projects.
    archived: Include archived projects (default false)."""
    params: dict = {
        "opt_fields": "name,archived,color,current_status_update,due_on,owner,owner.name",
        "archived": str(archived).lower(),
    }

    if team_gid:
        path = f"/teams/{team_gid}/projects"
    else:
        path = f"/workspaces/{workspace_gid}/projects"

    items = await _paginate_get(path, params)
    if isinstance(items, str):
        return items

    if not items:
        return "No projects found."

    output = f"## Projects ({len(items)})\n\n"
    for proj in items:
        output += _format_project(proj) + "\n"

    return output


@mcp.tool()
async def get_project(
    project_gid: str,
) -> str:
    """Get detailed information about a specific project.

    project_gid: The project GID."""
    data = await _asana_get(
        f"/projects/{project_gid}",
        {"opt_fields": "name,notes,archived,color,created_at,modified_at,"
         "due_on,start_on,owner,owner.name,team,team.name,"
         "current_status_update,current_status_update.title,"
         "current_status_update.status_type,members,members.name,"
         "custom_fields,custom_fields.name,custom_fields.display_value"}
    )
    if isinstance(data, str):
        return data

    proj = data.get("data", {})
    output = f"## Project: {proj.get('name', '')}\n\n"
    output += f"- **GID:** `{proj.get('gid', '')}`\n"

    owner = proj.get("owner")
    if isinstance(owner, dict) and owner.get("name"):
        output += f"- **Owner:** {owner['name']}\n"

    team = proj.get("team")
    if isinstance(team, dict) and team.get("name"):
        output += f"- **Team:** {team['name']}\n"

    if proj.get("start_on"):
        output += f"- **Start:** {proj['start_on']}\n"
    if proj.get("due_on"):
        output += f"- **Due:** {proj['due_on']}\n"
    if proj.get("archived"):
        output += "- **Status:** Archived\n"
    if proj.get("created_at"):
        output += f"- **Created:** {proj['created_at']}\n"

    status_update = proj.get("current_status_update")
    if isinstance(status_update, dict):
        output += f"- **Status update:** {status_update.get('status_type', '')} — {status_update.get('title', '')}\n"

    notes = proj.get("notes", "")
    if notes:
        if len(notes) > 500:
            notes = notes[:500] + "..."
        output += f"\n**Notes:**\n{notes}\n"

    members = proj.get("members", [])
    if members:
        names = [m.get("name", "") for m in members if m.get("name")]
        output += f"\n**Members ({len(names)}):** {', '.join(names)}\n"

    custom_fields = proj.get("custom_fields", [])
    if custom_fields:
        output += "\n**Custom Fields:**\n"
        for cf in custom_fields:
            cf_name = cf.get("name", "")
            cf_val = cf.get("display_value", "")
            if cf_name:
                output += f"- {cf_name}: {cf_val or '(empty)'}\n"

    return output


@mcp.tool()
async def create_project(
    workspace_gid: str,
    name: str,
    notes: str = "",
    team_gid: str = "",
    due_on: str = "",
    start_on: str = "",
    color: str = "",
) -> str:
    """Create a new project in an Asana workspace.

    workspace_gid: The workspace GID.
    name: Project name.
    notes: Optional project description.
    team_gid: Optional team GID (required for organizations).
    due_on: Optional due date (YYYY-MM-DD).
    start_on: Optional start date (YYYY-MM-DD).
    color: Optional color (dark-pink, dark-green, dark-blue, dark-red, dark-teal,
           dark-brown, dark-orange, dark-purple, dark-warm-gray, light-pink,
           light-green, light-blue, light-red, light-teal, light-brown,
           light-orange, light-purple, light-warm-gray)."""
    body: dict = {"data": {"workspace": workspace_gid, "name": name}}

    if notes:
        body["data"]["notes"] = notes
    if team_gid:
        body["data"]["team"] = team_gid
    if due_on:
        body["data"]["due_on"] = due_on
    if start_on:
        body["data"]["start_on"] = start_on
    if color:
        body["data"]["color"] = color

    data = await _asana_post("/projects", body)
    if isinstance(data, str):
        return data

    proj = data.get("data", {})
    return (
        f"Project created.\n"
        f"- **Name:** {proj.get('name', '')}\n"
        f"- **GID:** `{proj.get('gid', '')}`"
    )


# --- Tools: Sections ---


@mcp.tool()
async def list_sections(
    project_gid: str,
) -> str:
    """List all sections in a project. Sections organize tasks within a project.

    project_gid: The project GID."""
    items = await _paginate_get(
        f"/projects/{project_gid}/sections",
        {"opt_fields": "name,created_at"}
    )
    if isinstance(items, str):
        return items

    if not items:
        return "No sections found in this project."

    output = f"## Sections ({len(items)})\n\n"
    for section in items:
        name = section.get("name", "")
        gid = section.get("gid", "")
        output += f"- **{name}** (`{gid}`)\n"

    return output


@mcp.tool()
async def create_section(
    project_gid: str,
    name: str,
    insert_before: str = "",
    insert_after: str = "",
) -> str:
    """Create a new section in a project.

    project_gid: The project GID.
    name: Section name.
    insert_before: Optional section GID to insert before.
    insert_after: Optional section GID to insert after."""
    body: dict = {"data": {"name": name}}
    if insert_before:
        body["data"]["insert_before"] = insert_before
    if insert_after:
        body["data"]["insert_after"] = insert_after

    data = await _asana_post(f"/projects/{project_gid}/sections", body)
    if isinstance(data, str):
        return data

    section = data.get("data", {})
    return (
        f"Section created.\n"
        f"- **Name:** {section.get('name', '')}\n"
        f"- **GID:** `{section.get('gid', '')}`"
    )


@mcp.tool()
async def move_task_to_section(
    section_gid: str,
    task_gid: str,
    insert_before: str = "",
    insert_after: str = "",
) -> str:
    """Move a task to a specific section within a project.

    section_gid: The section GID to move the task into.
    task_gid: The task GID to move.
    insert_before: Optional task GID to insert before within the section.
    insert_after: Optional task GID to insert after within the section."""
    body: dict = {"data": {"task": task_gid}}
    if insert_before:
        body["data"]["insert_before"] = insert_before
    if insert_after:
        body["data"]["insert_after"] = insert_after

    data = await _asana_post(f"/sections/{section_gid}/addTask", body)
    if isinstance(data, str):
        return data

    return f"Task `{task_gid}` moved to section `{section_gid}`."


# --- Tools: Tasks ---


@mcp.tool()
async def list_tasks(
    project_gid: str = "",
    section_gid: str = "",
    assignee_gid: str = "",
    workspace_gid: str = "",
    completed_since: str = "",
) -> str:
    """List tasks. Provide either project_gid, section_gid, or (assignee_gid + workspace_gid).

    project_gid: List tasks in this project.
    section_gid: List tasks in this section.
    assignee_gid: List tasks assigned to this user (requires workspace_gid). Use 'me' for yourself.
    workspace_gid: Required when using assignee_gid.
    completed_since: Only return tasks completed after this date (ISO 8601, e.g. '2026-01-01'). Use 'now' for incomplete only."""
    opt_fields = "name,completed,due_on,assignee,assignee.name,tags,tags.name"

    if section_gid:
        path = f"/sections/{section_gid}/tasks"
        params: dict = {"opt_fields": opt_fields}
    elif project_gid:
        path = f"/projects/{project_gid}/tasks"
        params = {"opt_fields": opt_fields}
    elif assignee_gid and workspace_gid:
        path = "/tasks"
        params = {
            "assignee": assignee_gid,
            "workspace": workspace_gid,
            "opt_fields": opt_fields,
        }
    else:
        return "Error: Provide project_gid, section_gid, or both assignee_gid and workspace_gid."

    if completed_since:
        params["completed_since"] = completed_since

    items = await _paginate_get(path, params)
    if isinstance(items, str):
        return items

    if not items:
        return "No tasks found."

    output = f"## Tasks ({len(items)})\n\n"
    for task in items:
        output += _format_task(task) + "\n"

    return output


@mcp.tool()
async def get_task(
    task_gid: str,
) -> str:
    """Get detailed information about a specific task.

    task_gid: The task GID."""
    data = await _asana_get(
        f"/tasks/{task_gid}",
        {"opt_fields": "name,notes,completed,completed_at,due_on,due_at,"
         "start_on,start_at,created_at,modified_at,assignee,assignee.name,"
         "projects,projects.name,memberships,memberships.section,"
         "memberships.section.name,tags,tags.name,parent,parent.name,"
         "num_subtasks,custom_fields,custom_fields.name,"
         "custom_fields.display_value,permalink_url"}
    )
    if isinstance(data, str):
        return data

    task = data.get("data", {})
    completed = task.get("completed", False)
    status = "Completed" if completed else "Incomplete"

    output = f"## Task: {task.get('name', '')}\n\n"
    output += f"- **GID:** `{task.get('gid', '')}`\n"
    output += f"- **Status:** {status}\n"

    assignee = task.get("assignee")
    if isinstance(assignee, dict) and assignee.get("name"):
        output += f"- **Assignee:** {assignee['name']}\n"

    if task.get("start_on") or task.get("start_at"):
        output += f"- **Start:** {task.get('start_on') or task.get('start_at')}\n"
    if task.get("due_on") or task.get("due_at"):
        output += f"- **Due:** {task.get('due_on') or task.get('due_at')}\n"
    if task.get("completed_at"):
        output += f"- **Completed at:** {task['completed_at']}\n"

    projects = task.get("projects", [])
    if projects:
        proj_names = [f"{p.get('name', '')} (`{p.get('gid', '')}`)" for p in projects]
        output += f"- **Projects:** {', '.join(proj_names)}\n"

    memberships = task.get("memberships", [])
    if memberships:
        sections = []
        for m in memberships:
            section = m.get("section", {})
            if section and section.get("name"):
                sections.append(section["name"])
        if sections:
            output += f"- **Section:** {', '.join(sections)}\n"

    parent = task.get("parent")
    if isinstance(parent, dict) and parent.get("name"):
        output += f"- **Parent task:** {parent['name']} (`{parent.get('gid', '')}`)\n"

    num_subtasks = task.get("num_subtasks", 0)
    if num_subtasks:
        output += f"- **Subtasks:** {num_subtasks}\n"

    tags = task.get("tags", [])
    if tags:
        tag_names = [t.get("name", "") for t in tags if t.get("name")]
        if tag_names:
            output += f"- **Tags:** {', '.join(tag_names)}\n"

    if task.get("permalink_url"):
        output += f"- **Link:** {task['permalink_url']}\n"

    if task.get("created_at"):
        output += f"- **Created:** {task['created_at']}\n"
    if task.get("modified_at"):
        output += f"- **Modified:** {task['modified_at']}\n"

    custom_fields = task.get("custom_fields", [])
    if custom_fields:
        cf_parts = []
        for cf in custom_fields:
            cf_name = cf.get("name", "")
            cf_val = cf.get("display_value", "")
            if cf_name and cf_val:
                cf_parts.append(f"{cf_name}: {cf_val}")
        if cf_parts:
            output += f"\n**Custom Fields:**\n"
            for part in cf_parts:
                output += f"- {part}\n"

    notes = task.get("notes", "")
    if notes:
        if len(notes) > 1000:
            notes = notes[:1000] + "..."
        output += f"\n**Notes:**\n{notes}\n"

    return output


@mcp.tool()
async def create_task(
    name: str,
    project_gid: str = "",
    workspace_gid: str = "",
    assignee_gid: str = "",
    notes: str = "",
    due_on: str = "",
    start_on: str = "",
    section_gid: str = "",
) -> str:
    """Create a new task in Asana.

    name: Task name.
    project_gid: Project to add the task to (provide this or workspace_gid).
    workspace_gid: Workspace for the task (if not using project_gid).
    assignee_gid: Optional user GID to assign. Use 'me' for yourself.
    notes: Optional task description (plain text).
    due_on: Optional due date (YYYY-MM-DD).
    start_on: Optional start date (YYYY-MM-DD).
    section_gid: Optional section GID to place the task in (within the project)."""
    body: dict = {"data": {"name": name}}

    if project_gid:
        body["data"]["projects"] = [project_gid]
    if workspace_gid:
        body["data"]["workspace"] = workspace_gid
    if assignee_gid:
        body["data"]["assignee"] = assignee_gid
    if notes:
        body["data"]["notes"] = notes
    if due_on:
        body["data"]["due_on"] = due_on
    if start_on:
        body["data"]["start_on"] = start_on

    data = await _asana_post("/tasks", body)
    if isinstance(data, str):
        return data

    task = data.get("data", {})
    task_gid = task.get("gid", "")

    # Move to section if specified
    if section_gid and task_gid:
        section_result = await _asana_post(
            f"/sections/{section_gid}/addTask",
            {"data": {"task": task_gid}}
        )
        if isinstance(section_result, str):
            return (
                f"Task created but failed to move to section.\n"
                f"- **Name:** {task.get('name', '')}\n"
                f"- **GID:** `{task_gid}`\n"
                f"- Section error: {section_result}"
            )

    output = f"Task created.\n"
    output += f"- **Name:** {task.get('name', '')}\n"
    output += f"- **GID:** `{task_gid}`"
    if section_gid:
        output += f"\n- **Section:** `{section_gid}`"

    return output


@mcp.tool()
async def update_task(
    task_gid: str,
    name: str = "",
    notes: str = "",
    completed: bool | None = None,
    due_on: str = "",
    start_on: str = "",
    assignee_gid: str = "",
) -> str:
    """Update an existing task's properties.

    task_gid: The task GID.
    name: New task name (leave empty to keep current).
    notes: New description (leave empty to keep current).
    completed: Set to true to complete, false to reopen (leave null to keep current).
    due_on: New due date YYYY-MM-DD (leave empty to keep current, use 'null' to clear).
    start_on: New start date YYYY-MM-DD (leave empty to keep current, use 'null' to clear).
    assignee_gid: New assignee GID (leave empty to keep current, use 'null' to unassign)."""
    body: dict = {"data": {}}

    if name:
        body["data"]["name"] = name
    if notes:
        body["data"]["notes"] = notes
    if completed is not None:
        body["data"]["completed"] = completed
    if due_on:
        body["data"]["due_on"] = None if due_on == "null" else due_on
    if start_on:
        body["data"]["start_on"] = None if start_on == "null" else start_on
    if assignee_gid:
        body["data"]["assignee"] = None if assignee_gid == "null" else assignee_gid

    if not body["data"]:
        return "Error: No fields provided to update."

    data = await _asana_put(f"/tasks/{task_gid}", body)
    if isinstance(data, str):
        return data

    task = data.get("data", {})
    return (
        f"Task updated.\n"
        f"- **Name:** {task.get('name', '')}\n"
        f"- **GID:** `{task.get('gid', '')}`\n"
        f"- **Completed:** {task.get('completed', False)}"
    )


@mcp.tool()
async def delete_task(
    task_gid: str,
) -> str:
    """Delete a task permanently. This cannot be undone.

    task_gid: The task GID to delete."""
    data = await _asana_delete(f"/tasks/{task_gid}")
    if isinstance(data, str):
        return data

    return f"Task `{task_gid}` deleted."


# --- Tools: Subtasks ---


@mcp.tool()
async def list_subtasks(
    task_gid: str,
) -> str:
    """List subtasks of a task.

    task_gid: The parent task GID."""
    items = await _paginate_get(
        f"/tasks/{task_gid}/subtasks",
        {"opt_fields": "name,completed,due_on,assignee,assignee.name"}
    )
    if isinstance(items, str):
        return items

    if not items:
        return f"No subtasks found for task `{task_gid}`."

    output = f"## Subtasks ({len(items)})\n\n"
    for task in items:
        output += _format_task(task) + "\n"

    return output


@mcp.tool()
async def create_subtask(
    parent_task_gid: str,
    name: str,
    assignee_gid: str = "",
    notes: str = "",
    due_on: str = "",
) -> str:
    """Create a subtask under a parent task.

    parent_task_gid: The parent task GID.
    name: Subtask name.
    assignee_gid: Optional assignee GID. Use 'me' for yourself.
    notes: Optional description.
    due_on: Optional due date (YYYY-MM-DD)."""
    body: dict = {"data": {"name": name}}

    if assignee_gid:
        body["data"]["assignee"] = assignee_gid
    if notes:
        body["data"]["notes"] = notes
    if due_on:
        body["data"]["due_on"] = due_on

    data = await _asana_post(f"/tasks/{parent_task_gid}/subtasks", body)
    if isinstance(data, str):
        return data

    task = data.get("data", {})
    return (
        f"Subtask created.\n"
        f"- **Name:** {task.get('name', '')}\n"
        f"- **GID:** `{task.get('gid', '')}`\n"
        f"- **Parent:** `{parent_task_gid}`"
    )


# --- Tools: Comments (Stories) ---


@mcp.tool()
async def get_task_stories(
    task_gid: str,
    limit: int = 25,
) -> str:
    """Get comments and activity history on a task.

    task_gid: The task GID.
    limit: Max stories to return (default 25)."""
    items = await _paginate_get(
        f"/tasks/{task_gid}/stories",
        {"opt_fields": "created_at,created_by,created_by.name,text,type,resource_subtype",
         "limit": min(limit, 100)}
    )
    if isinstance(items, str):
        return items

    if not items:
        return f"No stories found for task `{task_gid}`."

    # Filter to comments for readability, but show system events too
    output = f"## Task Activity ({len(items)} entries)\n\n"
    for story in items:
        subtype = story.get("resource_subtype", "")
        created_by = story.get("created_by", {})
        author = created_by.get("name", "system") if isinstance(created_by, dict) else "system"
        created_at = story.get("created_at", "")
        text = story.get("text", "")

        if subtype == "comment_added":
            if len(text) > 500:
                text = text[:500] + "..."
            output += f"**{author}** commented ({created_at}):\n{text}\n\n---\n\n"
        else:
            # System event — show briefly
            if text:
                output += f"_[{subtype}] {author} ({created_at}): {text[:200]}_\n\n"

    return output


@mcp.tool()
async def add_comment(
    task_gid: str,
    text: str,
) -> str:
    """Add a comment to a task.

    task_gid: The task GID.
    text: Comment text (supports simple formatting)."""
    data = await _asana_post(
        f"/tasks/{task_gid}/stories",
        {"data": {"text": text}}
    )
    if isinstance(data, str):
        return data

    story = data.get("data", {})
    return (
        f"Comment added to task `{task_gid}`.\n"
        f"- **Story GID:** `{story.get('gid', '')}`"
    )


# --- Tools: Tags ---


@mcp.tool()
async def list_tags(
    workspace_gid: str,
) -> str:
    """List all tags in a workspace.

    workspace_gid: The workspace GID."""
    items = await _paginate_get(
        f"/workspaces/{workspace_gid}/tags",
        {"opt_fields": "name,color"}
    )
    if isinstance(items, str):
        return items

    if not items:
        return "No tags found."

    output = f"## Tags ({len(items)})\n\n"
    for tag in items:
        name = tag.get("name", "")
        gid = tag.get("gid", "")
        color = tag.get("color", "")
        output += f"- **{name}** (`{gid}`)"
        if color:
            output += f" [{color}]"
        output += "\n"

    return output


@mcp.tool()
async def add_tag_to_task(
    task_gid: str,
    tag_gid: str,
) -> str:
    """Add a tag to a task.

    task_gid: The task GID.
    tag_gid: The tag GID (get from list_tags)."""
    data = await _asana_post(
        f"/tasks/{task_gid}/addTag",
        {"data": {"tag": tag_gid}}
    )
    if isinstance(data, str):
        return data

    return f"Tag `{tag_gid}` added to task `{task_gid}`."


@mcp.tool()
async def remove_tag_from_task(
    task_gid: str,
    tag_gid: str,
) -> str:
    """Remove a tag from a task.

    task_gid: The task GID.
    tag_gid: The tag GID to remove."""
    data = await _asana_post(
        f"/tasks/{task_gid}/removeTag",
        {"data": {"tag": tag_gid}}
    )
    if isinstance(data, str):
        return data

    return f"Tag `{tag_gid}` removed from task `{task_gid}`."


# --- Tools: Search ---


@mcp.tool()
async def search_tasks(
    workspace_gid: str,
    text: str = "",
    assignee_gid: str = "",
    project_gid: str = "",
    completed: bool | None = None,
    is_subtask: bool | None = None,
    due_on_before: str = "",
    due_on_after: str = "",
    sort_by: str = "modified_at",
) -> str:
    """Search tasks across a workspace with various filters.

    workspace_gid: The workspace GID.
    text: Full-text search query.
    assignee_gid: Filter by assignee. Use 'me' for yourself.
    project_gid: Filter by project.
    completed: Filter by completion status (true/false, null for both).
    is_subtask: Filter by subtask status (true/false, null for both).
    due_on_before: Tasks due before this date (YYYY-MM-DD).
    due_on_after: Tasks due after this date (YYYY-MM-DD).
    sort_by: Sort by 'modified_at' (default), 'due_on', 'created_at', or 'likes'."""
    params: dict = {
        "opt_fields": "name,completed,due_on,assignee,assignee.name,projects,projects.name",
        "sort_by": sort_by,
        "sort_ascending": "false",
    }

    if text:
        params["text"] = text
    if assignee_gid:
        params["assignee.any"] = assignee_gid
    if project_gid:
        params["projects.any"] = project_gid
    if completed is not None:
        params["completed"] = str(completed).lower()
    if is_subtask is not None:
        params["is_subtask"] = str(is_subtask).lower()
    if due_on_before:
        params["due_on.before"] = due_on_before
    if due_on_after:
        params["due_on.after"] = due_on_after

    data = await _asana_get(
        f"/workspaces/{workspace_gid}/tasks/search",
        params
    )
    if isinstance(data, str):
        return data

    tasks = data.get("data", [])
    if not tasks:
        return "No tasks found matching your search."

    output = f"## Search Results ({len(tasks)} tasks)\n\n"
    for task in tasks:
        line = _format_task(task)
        projects = task.get("projects", [])
        if projects:
            proj_names = [p.get("name", "") for p in projects if p.get("name")]
            if proj_names:
                line += f"\n  Projects: {', '.join(proj_names)}"
        output += line + "\n"

    return output


# --- Tools: Task Dependencies ---


@mcp.tool()
async def add_dependency(
    task_gid: str,
    dependency_gid: str,
) -> str:
    """Add a dependency to a task (this task depends on the dependency task).

    task_gid: The task that depends on another.
    dependency_gid: The task that must be completed first."""
    data = await _asana_post(
        f"/tasks/{task_gid}/addDependencies",
        {"data": {"dependencies": [dependency_gid]}}
    )
    if isinstance(data, str):
        return data

    return f"Task `{task_gid}` now depends on `{dependency_gid}`."


@mcp.tool()
async def get_dependencies(
    task_gid: str,
) -> str:
    """Get tasks that this task depends on (blockers).

    task_gid: The task GID."""
    items = await _paginate_get(
        f"/tasks/{task_gid}/dependencies",
        {"opt_fields": "name,completed,due_on,assignee,assignee.name"}
    )
    if isinstance(items, str):
        return items

    if not items:
        return f"Task `{task_gid}` has no dependencies."

    output = f"## Dependencies ({len(items)}) — task `{task_gid}` depends on:\n\n"
    for task in items:
        output += _format_task(task) + "\n"

    return output


@mcp.tool()
async def get_dependents(
    task_gid: str,
) -> str:
    """Get tasks that depend on this task (tasks blocked by this one).

    task_gid: The task GID."""
    items = await _paginate_get(
        f"/tasks/{task_gid}/dependents",
        {"opt_fields": "name,completed,due_on,assignee,assignee.name"}
    )
    if isinstance(items, str):
        return items

    if not items:
        return f"Task `{task_gid}` has no dependents."

    output = f"## Dependents ({len(items)}) — these tasks depend on `{task_gid}`:\n\n"
    for task in items:
        output += _format_task(task) + "\n"

    return output


# --- Main ---

if __name__ == "__main__":
    mcp.run(transport="stdio")
