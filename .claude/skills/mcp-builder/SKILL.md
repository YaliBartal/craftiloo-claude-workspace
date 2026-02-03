---
name: mcp-builder
description: Connects external MCP services or builds custom API integrations
triggers:
  - add an MCP
  - connect to API
  - set up MCP
  - integrate with
  - add Notion
  - add YouTube
output_location: .mcp.json
---

# MCP Builder

**USE WHEN** user says: "add an MCP", "connect to API", "set up MCP", "integrate with", "add Notion/YouTube/etc"

---

## What This Does

Connects external services (MCPs) or builds custom API integrations. All configs go in `.mcp.json`.

---

## Process

### 1. Identify the Service
Ask:
- **What service/API do you want to connect?**
- **What do you want to do with it?** (read data, write, both)

### 2. Check for Existing MCP

Search for existing MCP servers:
- NPM: `@notionhq/notion-mcp-server`, `@kirbah/mcp-youtube`, etc.
- GitHub MCP repositories

**If exists** → Use existing (Path A)
**If not** → Build custom (Path B)

---

## Path A: Connect Existing MCP

### Step 1: Get API Key
Guide user to get credentials from the service:
- Notion: Settings → Integrations → Create integration
- YouTube: Google Cloud Console → Enable YouTube API → Create credentials
- etc.

### Step 2: Add to .env
```
SERVICE_API_KEY=your_key_here
```

### Step 3: Configure .mcp.json
Add to `mcpServers` object:

```json
"service-name": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@package/mcp-server"],
  "env": {
    "API_KEY": "${SERVICE_API_KEY}"
  }
}
```

### Step 4: Reload VS Code
User must reload for MCP to connect.

### Step 5: Test
Run: `claude mcp list` to verify connection.

---

## Path B: Build Custom MCP

For services without existing MCPs:

### Option 1: Python (FastMCP)
```bash
pip install mcp[cli]
```

### Option 2: TypeScript
```bash
npm install @modelcontextprotocol/sdk
```

### Key Rules
- **Never write to stdout** (breaks JSON-RPC)
- Use absolute paths in `.mcp.json`
- Route logging to stderr

### After Building
Configure in `.mcp.json` same as Path A, but point to your script:

```json
"custom-service": {
  "type": "stdio",
  "command": "python",
  "args": ["/absolute/path/to/server.py"]
}
```

---

## After Setup

Update `CLAUDE.md` MCP Services table:

```markdown
| Service Name | Purpose | Status |
|--------------|---------|--------|
| notion | Save research to database | ✅ Connected |
```

---

## Common MCPs

| Service | Package |
|---------|---------|
| Notion | `@notionhq/notion-mcp-server` |
| YouTube | `@kirbah/mcp-youtube` |
| GitHub | `@modelcontextprotocol/server-github` |
| Filesystem | `@modelcontextprotocol/server-filesystem` |
