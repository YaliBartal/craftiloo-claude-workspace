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

## Organization & File Management Standards

**CRITICAL: Follow these standards for ALL work, ALL skills, ALL outputs.**

### File Organization Hierarchy

**Every output must be organized into clear, logical folders:**

```
outputs/
├── {project-type}/         # e.g., research, data, reports
│   ├── {specific-area}/    # e.g., market-intel, competitor-analysis
│   │   ├── briefs/         # Main outputs (what user reads first)
│   │   ├── reports/        # Detailed analysis (subfolders by type)
│   │   ├── data/           # Raw data files (subfolders by type)
│   │   ├── snapshots/      # Historical/comparison data
│   │   ├── scripts/        # Automation scripts ONLY
│   │   └── README.md       # Folder guide
```

### Naming Conventions (STRICT)

**Use consistent, predictable naming:**

| File Type | Format | Example |
|-----------|--------|---------|
| **Date-based outputs** | `YYYY-MM-DD-{descriptor}.ext` | `2026-02-09-morning-brief.md` |
| **Subject-based outputs** | `{subject-slug}-YYYY-MM-DD.ext` | `cross-stitch-analysis-2026-02-09.md` |
| **Data files** | `{type}-{subject}-YYYY-MM-DD.json` | `product-data-cross-stitch-2026-02-09.json` |
| **Scripts** | `{action}_{subject}.py` | `generate_report.py`, `process_data.py` |

**Rules:**
- Use lowercase with hyphens (kebab-case) for file/folder names
- Always include dates in format YYYY-MM-DD
- Be descriptive but concise (max 50 chars for filename)
- Group related files in subfolders, NOT with prefixes

### Forbidden Practices

**NEVER:**
- ❌ Dump files in root folders
- ❌ Mix scripts with output files in same folder
- ❌ Create temp files without cleaning them up
- ❌ Use ambiguous names like "output.json", "data.txt", "test.py"
- ❌ Create 25+ files in one folder without subfolders
- ❌ Use inconsistent naming (some with dates, some without)

### Efficiency Targets

**For every task:**
- ✅ <80K tokens per operation
- ✅ <$0.20 cost per operation (if using paid APIs)
- ✅ <5 minutes execution time
- ✅ Minimal file count (only what's necessary)
- ✅ Self-documenting structure (user can navigate without asking)

### Readability & Communication

**User must be able to:**
1. **See what you're doing** by looking at folder structure
2. **Find outputs easily** by following logical hierarchy
3. **Understand file purpose** from name alone
4. **Navigate without confusion** (clear README in each major folder)

### When Creating New Output Folders

**Always include a README.md with:**
- Folder purpose
- Folder structure diagram
- File naming conventions used
- What goes where (table format)
- Daily workflow (if applicable)

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
│       ├── daily-market-intel/  # Morning market intelligence
│       ├── listing-creator/     # Amazon listing generator
│       ├── image-planner/       # Product image strategy planner
│       ├── product-listing-development/  # Parent orchestrator (listing + images)
│       ├── automation-discovery-interview/  # 30-40 min workflow audit
│       ├── weekly-ppc-analysis/  # Weekly PPC analysis (campaign + search term + placement + targeting)
│       ├── negative-keyword-generator/  # Proactive negative keyword generation from product knowledge
│       └── customer-review-analyzer/  # Amazon review analysis for our products + competitors
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
| "Market check" / "Product pulse" | → `.claude/skills/daily-market-intel/` |
| "Create a listing" / "Amazon listing" | → `.claude/skills/listing-creator/` |
| "Image plan" / "Plan my images" | → `.claude/skills/image-planner/` |
| "Full listing" / "Launch product" / "Listing + images" | → `.claude/skills/product-listing-development/` |
| "Weekly PPC" / "PPC analysis" / "PPC review" / "Campaign analysis" | → `.claude/skills/weekly-ppc-analysis/` |
| "Search term analysis" / "Negate terms" / "Keyword mining" | → `.claude/skills/weekly-ppc-analysis/` |
| "Generate negatives" / "Negative keywords" / "Negative keyword list" | → `.claude/skills/negative-keyword-generator/` |
| "Review analysis" / "Customer reviews" / "What are customers saying" | → `.claude/skills/customer-review-analyzer/` |

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
| **GitHub** | Repository access, code search, issues, PRs | ⚙️ Configured |

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
