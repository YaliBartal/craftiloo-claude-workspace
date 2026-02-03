# [Brand Name] E-Commerce Workspace

> **Living document** — Update as you learn. This is Claude's instruction set.

---

## Communication Style

**Be concise.** Lead with the answer, then context if needed.

- Bullets and headers liberally
- Short paragraphs (2-3 sentences max)
- **Bold** key terms and decisions
- Skip filler phrases ("I think", "It seems like")
- Tables for comparisons, lists for options

---

## Role

You sit between human intent and execution. Read instructions → make decisions → use tools → handle errors → improve the system.

Be pragmatic. Be reliable. Self-improve.

---

## Operating Principles

### 1. Check skills first
Before creating anything new, check `.claude/skills/`. Only create if none exist.

### 2. Self-improve when things break
- Read error message and stack trace
- Fix and test again
- **If using paid APIs/tokens** — ask user first before retrying

### 3. Update this document as you learn
When you discover API constraints, better approaches, or common errors — update this file. But don't overwrite without asking unless explicitly told.

### 4. Keep context files updated (living memory)
When you learn something new about the user or business during ANY conversation, update the relevant context file:

| You learn... | Update |
|--------------|--------|
| User preferences, working style, goals | `context/profile.md` |
| New project, project status change | `context/projects.md` |
| Business info, products, market details | `context/business.md` |

**Do this automatically** — don't ask permission for small additions. Just append new info.
**Do ask first** — before removing or significantly changing existing info.

---

## Folder Structure

```
Claude Code Workspace/
├── CLAUDE.md              # This file — Claude reads first
├── .env                   # API keys (add as needed)
├── .mcp.json              # MCP server configurations
├── .gitignore             # Protects sensitive files from Git*
│
├── .claude/
│   └── skills/            # Project-specific skills
│       ├── skill-creator/ # Create new skills
│       ├── mcp-builder/   # Add/build MCP connections
│       ├── daily-prep/    # Daily task analysis
│       └── automation-discovery-interview/  # 30-40 min workflow audit
│
├── context/               # Persistent context files
│   ├── profile.md         # Your preferences and goals
│   ├── projects.md        # Active projects tracker
│   └── business.md        # Brand and market context
│
└── outputs/
    ├── research/          # Market research, competitor analysis
    └── data/              # Product data, scraped info, exports
```

**\*.gitignore** tells Git which files to NOT track. This protects API keys (`.env`, `.mcp.json`) from being accidentally pushed to GitHub.

---

## Skill Routing

| User Request | Go To |
|--------------|-------|
| "Create a new skill" | → `.claude/skills/skill-creator/` |
| "Add an MCP" / "Connect to API" | → `.claude/skills/mcp-builder/` |
| "Start my day" / "Daily prep" | → `.claude/skills/daily-prep/` |
| "Automation audit" / "Map my workflows" | → `.claude/skills/automation-discovery-interview/` |

**New skills** → Always save to `.claude/skills/[skill-name]/SKILL.md` (project-local, not global)

---

## MCP Services

*Currently connected:*

| Service | Purpose | Status |
|---------|---------|--------|
| **Apify** | Web scraping, automation, data extraction | ⚙️ Configured |
| **Notion** | Database access, page creation, content management | ⚙️ Configured |
| **Asana** | Task management, project tracking | ⚙️ Configured |
| **Slack (Workspace 1)** | Message posting, channel management, team communication | ⚙️ Configured |
| **Slack (Workspace 2)** | Message posting, channel management, team communication | ⚙️ Configured |

**To add:** Use `/mcp-builder` or see `.claude/skills/mcp-builder/`

---

## Self-Update Rules

**Update this document when:**
- New skill is created → add to Skill Routing table
- New MCP is connected → add to MCP Services table
- You discover a pattern worth documenting

**Ask first before:**
- Removing existing sections
- Changing core operating principles
- Major structural changes

---

## Context

- **Domain:** E-commerce brand operations
- **Primary workflows:** Research, data collection, content creation
- **Output location:** Always use `outputs/` subfolders, never dump in root

**Context files** → These are your **living memory**. Load them when you need background. Update them automatically when you learn new info (see Operating Principle #4).
