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

### 5. Skill Lessons System (continuous improvement)

**Every skill has a `LESSONS.md` file** that tracks what worked, what failed, and what to avoid.

**Before every skill run:**
1. Read the skill's `LESSONS.md`
2. Check Known Issues and Repeat Errors
3. If a Repeat Error is encountered, **tell the user immediately** with occurrence count

**After every skill run:**
1. Log a Run Entry with: goals, result (success/partial/fail), what worked, what didn't, lessons learned
2. Update Known Issues / Repeat Errors / Resolved Issues as appropriate
3. End output with a brief **Lessons Update** note to the user

**Rules:**
- Never skip reading LESSONS.md — it's the first step of every skill
- Never skip writing to LESSONS.md — it's the last step of every skill
- If a Known Issue happens again, move it to Repeat Errors and increment the count
- Repeat Errors must be surfaced to the user with: _"⚠️ Repeat issue (×N): [description]"_
- Be honest — log failures and partial results, not just successes

| File | Location | Purpose |
|------|----------|---------|
| `LESSONS.md` | `.claude/skills/{skill-name}/LESSONS.md` | Per-skill learning log |

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
│   └── skills/            # Project-specific skills (each has SKILL.md + LESSONS.md)
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
│       ├── customer-review-analyzer/  # Amazon review analysis for our products + competitors
│       ├── niche-category-analysis/  # New niche/category deep-dive research & viability
│       └── listing-optimizer/        # Listing audit & optimization (Ranking Juice + keywords + rank trends)
│       # Each skill folder contains:
│       #   SKILL.md    — Instructions (reads LESSONS.md first, writes to it last)
│       #   LESSONS.md  — Run log, known issues, repeat errors, resolved issues
│
├── mcp-servers/           # Custom MCP server implementations
│   ├── sellerboard/       # Seller Board CSV report server
│   │   └── server.py
│   ├── datadive/          # DataDive API server (keywords, ranks, competitors)
│   │   └── server.py
│   ├── amazon-sp-api/     # Amazon SP-API (orders, catalog, inventory, pricing, reports)
│   │   └── server.py
│   ├── notion/            # Notion API server (pages, blocks, databases, 28 tools)
│   │   └── server.py
│   ├── slack/             # Slack multi-workspace server (messages, channels, files, scheduling, 16 tools)
│   │   └── server.py
│   └── asana/             # Asana API server (projects, tasks, sections, comments, search, 26 tools)
│       └── server.py
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
| "Niche analysis" / "Category research" / "Explore a niche" / "New niche" | → `.claude/skills/niche-category-analysis/` |
| "Listing audit" / "Audit listing" / "Listing optimizer" / "Listing score" / "Portfolio scan" / "Listing health" | → `.claude/skills/listing-optimizer/` |

**New skills** → Always save to `.claude/skills/[skill-name]/SKILL.md` (project-local, not global)

---

## MCP Services

*Currently connected:*

| Service | Purpose | Status |
|---------|---------|--------|
| **Apify** | Actor runner — run scrapers, check status, get results (custom Python MCP, 7 tools) | ⚙️ Configured |
| **Notion** | Full workspace management — pages, blocks, databases, comments, search (28 tools) | ⚙️ Configured |
| **Asana** | Project/task management — tasks, projects, sections, subtasks, comments, search, dependencies (custom Python MCP, 26 tools) | ⚙️ Configured |
| **Slack** | Multi-workspace messaging, channels, search, scheduled messages, file upload (custom Python MCP, 16 tools) | ⚙️ Configured |
| **GitHub** | Repository access, code search, issues, PRs | ⚙️ Configured |
| **Seller Board** | Sales, profit, inventory, PPC, daily dashboard (5 CSV reports) | ⚙️ Configured |
| **DataDive** | Keyword rank tracking, competitor data, search volume, niche research (12 tools) | ⚙️ Configured |
| **Amazon SP-API** | Orders, catalog, inventory, pricing, reports — direct Amazon data (13 tools) | ⚙️ Configured |

**Apify MCP Server** (`mcp-servers/apify/server.py`):

Custom Python MCP server for Apify Platform API. Auth: Bearer token. Rate limiting: 0.5s between requests.

| Tool | API | Key Data |
|------|-----|----------|
| `search_store_actors` | Store Search | Find actors by use case — name, stats, actorId |
| `run_actor` | Run Actor (async) | Start actor, get run ID + dataset ID |
| `run_actor_sync` | Run Actor (sync) | Run + wait + return results (max 300s) |
| `get_run_status` | Run Details | Status, timing, compute units, dataset ID |
| `get_run_dataset` | Dataset Items | Scraped data from completed runs |
| `list_recent_runs` | List Runs | Recent runs with status, filterable by actor |
| `abort_run` | Abort Run | Cancel a running/ready actor |

**Env variable:** `APIFY_API_TOKEN` in `.env`

**Commonly used actors:**
- `saswave~amazon-product-scraper` — Product data (BSR, price, reviews, ratings)
- `axesso_data~amazon-search-scraper` — Keyword search results (position, badges, prices). Input: `{"input": [{"keyword": "...", "country": "US"}]}`. Fields: `searchResultPosition` (0-indexed), `productDescription` (title), `price` (float), `productRating` (string), `countReview`, `salesVolume`, `sponsored` (bool).

**Skills using Apify data:**
- **Daily Market Intel** → Product scraping for BSR/price/review snapshots
- **Customer Review Analyzer** → Review scraping for competitor analysis
- **Niche Category Analysis** → Competitor product discovery

**If API stops working** → check APIFY_API_TOKEN in .env. Get token from Apify Console → Settings → Integrations.

**Seller Board MCP Server** (`mcp-servers/sellerboard/server.py`):

Custom Python MCP server exposing 6 tools for all Seller Board CSV reports.

| Tool | Report | Key Data |
|------|--------|----------|
| `get_inventory_report` | FBA Inventory | Stock levels, ROI, margin, reorder recs, velocity |
| `get_sales_detailed_report` | Sales Detailed (59 cols) | Per-ASIN: organic/PPC sales, fees, COGS, profit, ACOS, sessions |
| `get_sales_summary_report` | Sales Summary (41 cols) | Daily financials, ad spend by channel, profit by ASIN |
| `get_daily_dashboard_report` | Daily Dashboard (31 cols) | Daily aggregate: revenue, units, ad spend, profit, margin |
| `get_ppc_marketing_report` | PPC Marketing (15 cols) | PPC sales, organic turnover, TACOS, ROAS, ACOS, CPC, conversion |
| `get_all_reports_summary` | All 5 combined | Complete business snapshot |

**Env variables** (5 report URLs in `.env`, auth token embedded):
`SELLERBOARD_INVENTORY_REPORT`, `SELLERBOARD_SALES_DETAILED`, `SELLERBOARD_SALES_SUMMARY`, `SELLERBOARD_DAILY_DASHBOARD`, `SELLERBOARD_PPC_MARKETING`

**Skills using Seller Board data:**
- **Weekly PPC Analysis** → TACoS, profitability, organic vs PPC split
- **Daily Market Intel** → Actual sales/profit alongside BSR estimates
- **Daily Prep** → Yesterday's business pulse + stock alerts

**If reports stop working** → tokens may have expired in Seller Board → Settings → Automation → Reports

**DataDive MCP Server** (`mcp-servers/datadive/server.py`):

Custom Python MCP server exposing 12 tools for all DataDive API endpoints. Auth via `x-api-key` header. Built-in rate limiting (1 req/sec).

| Tool | Endpoint | Key Data |
|------|----------|----------|
| `get_profile` | Account Profile | Token balance, account info |
| `list_niches` | List Niches | nicheId, nicheLabel, heroKeyword (23 active) |
| `get_niche_keywords` | Master Keyword List | keyword, searchVolume, relevancy, organic/sponsored ranks |
| `get_niche_competitors` | Competitor Data | ASIN, BSR, sales, revenue, rating, reviews, P1 keywords |
| `get_niche_ranking_juices` | Ranking Juice | Title/bullets/description optimization scores |
| `get_niche_roots` | Keyword Roots | Root words, frequency, broadSearchVolume |
| `run_ai_copywriter` | AI Copywriter | Optimized listing copy (4 modes: cosmo, ranking-juice, nlp, cosmo-rufus) |
| `list_rank_radars` | List Rank Radars | 15 active radars, keyword counts, top10/50 stats |
| `get_rank_radar_data` | Rank Radar Data | Daily organicRank + impressionRank per keyword |
| `create_niche_dive` | Create Dive | Token-consuming niche discovery from seed ASIN |
| `get_niche_dive_status` | Dive Status | in_progress/success/error + results |
| `get_niche_overview` | Niche Overview | Combined competitors + keywords + roots snapshot |

**Env variable:** `DATADIVE_API_KEY` in `.env`

**Skills using DataDive data:**
- **Weekly PPC Analysis** → Rank Radar data replaces "check Data Dive" callouts with automated rank-aware decisions
- **Daily Market Intel** → Competitor sales/revenue estimates + keyword rank tracking
- **Negative Keyword Generator** → Master Keyword List relevancy scores + outlier keyword identification

**Other skills that benefit:**
- **Niche Category Analysis** → `create_niche_dive` + `get_niche_competitors` for automated competitor discovery
- **Listing Creator** → `get_niche_keywords` for search volume data; `get_niche_ranking_juices` for optimization gaps

**If API stops working** → check DATADIVE_API_KEY in .env. Rate limit: 1 request/second (built into MCP server).

**Amazon SP-API MCP Server** (`mcp-servers/amazon-sp-api/server.py`):

Custom Python MCP server for direct Amazon Selling Partner API access. Auth: LWA OAuth2 (auto-refreshing access token). Rate limiting: 0.5s between requests.

| Tool | API | Key Data |
|------|-----|----------|
| `get_marketplace_participations` | Sellers | Registered marketplaces (US, CA, MX) |
| `get_orders` | Orders | Recent orders: ID, status, date, total, fulfillment |
| `get_order_items` | Orders | Line items for an order: ASIN, SKU, qty, price |
| `get_catalog_item` | Catalog 2022 | ASIN details: title, brand, images, dimensions, sales rank |
| `search_catalog` | Catalog 2022 | Search by keywords: matching ASINs with titles, brands |
| `get_competitive_pricing` | Pricing | Landed price, listing price, Buy Box data |
| `get_item_offers` | Pricing | All active offers for an ASIN with prices, seller info |
| `get_fba_inventory` | FBA Inventory | SKU/ASIN stock: fulfillable, inbound, reserved quantities |
| `create_report` | Reports | Request any Amazon report (orders, traffic, inventory, Brand Analytics) |
| `get_report_status` | Reports | Check report progress (DONE/IN_PROGRESS/FATAL) |
| `get_report_document` | Reports | Download completed report data (CSV/TSV) |
| `get_my_listings` | Reports | Shortcut: request all-listings report |

**Env variables:** `SP_API_CLIENT_ID`, `SP_API_CLIENT_SECRET`, `SP_API_REFRESH_TOKEN`, `SP_API_MARKETPLACE_US`, `SP_API_MARKETPLACE_CA`, `SP_API_MARKETPLACE_MX`

**No AWS credentials required** — auth uses LWA token exchange only. Access token auto-refreshes (1hr expiry).

**Registered roles:** Product Listing, Pricing, Brand Analytics, Amazon Fulfillment

**If API stops working** → Check if app is still authorized in Seller Central → Apps & Services → Manage Your Apps. Refresh token is permanent unless app is de-authorized.

**Notion MCP Server** (`mcp-servers/notion/server.py`):

Custom Python MCP server replacing the official `@notionhq/notion-mcp-server`. Full workspace access with 28 tools in 7 groups. Auth: Bearer token. Rate limiting: 0.33s between requests (~3/sec).

| Tool | Group | Key Capability |
|------|-------|----------------|
| `search` | Search | Search pages/databases by title across workspace |
| `get_self` | Search | Verify integration connection |
| `get_page` | Pages | Page metadata + all properties |
| `get_page_property` | Pages | Single property with pagination |
| `create_page` | Pages | Create page (with optional initial content) |
| `update_page` | Pages | Update properties / archive |
| `move_page` | Pages | Move to new parent |
| `archive_page` | Pages | Soft-delete convenience wrapper |
| `get_blocks` | Blocks | Direct child blocks (auto-paginates) |
| `get_block` | Blocks | Single block details |
| `append_blocks` | Blocks | Raw JSON blocks (auto-chunks at 100) |
| `append_markdown` | Blocks | **Simplified markdown → Notion blocks** |
| `update_block` | Blocks | Update block content |
| `delete_block` | Blocks | Delete block + children |
| `get_page_tree` | Blocks | **Recursive full page content (max 3 levels)** |
| `get_database` | Databases | Schema, properties, types |
| `query_database` | Databases | Filter + sort + auto-paginate |
| `update_database` | Databases | Update title/description/schema |
| `create_database` | Databases | Create inline database with properties |
| `get_comments` | Comments | All comments on page/block |
| `add_comment` | Comments | Add discussion comment |
| `get_user` | Users | User name, email, type |
| `list_users` | Users | All workspace users |
| `create_page_with_content` | Higher-level | **Page + full markdown content in one call** |
| `replace_page_content` | Higher-level | **Delete all blocks + append new content** |
| `find_or_create_page` | Higher-level | **Search → return if found, create if not** |
| `delete_all_blocks` | Higher-level | Clear all blocks from a page |
| `get_child_pages` | Higher-level | List child pages under a parent |

**Env variable:** `NOTION_API_KEY` in `.env`

**Key features:**
- Auto-pagination (up to 1000 items)
- Auto-chunking (100-block limit handled transparently)
- Simplified markdown input (`append_markdown`, `create_page_with_content`)
- Recursive page reading (`get_page_tree`)
- Dedup pattern (`find_or_create_page`)

**Skills using Notion:**
- **Product Listing Development** → `find_or_create_page` + `append_markdown` for full product pages
- **Listing Creator** → Listing content uploaded to Notion
- **Image Planner** → Image plan content uploaded to Notion

**If API stops working** → Check NOTION_API_KEY in .env. Ensure pages/databases are shared with the integration in Notion settings.

**Slack MCP Server** (`mcp-servers/slack/server.py`):

Custom Python MCP server replacing the official `@modelcontextprotocol/server-slack` NPM package. Single server handles both workspaces via a `workspace` parameter with alias support. Auth: Bot token per workspace. Rate limiting: 1 req/sec (Slack Tier 2).

**Workspaces:**

| Key | Aliases | Team ID | Description |
|-----|---------|---------|-------------|
| `craft` | `crafti` | T06KHD4CS6N | Workspace 1 (craft crafti craftiloo) |
| `craftiloo` | — | T01Q3BTU0DA | Workspace 2 (craftiloo) |

**Tools (16):**

| Tool | Group | Slack API Method | Key Capability |
|------|-------|------------------|----------------|
| `list_workspaces` | Utility | — | Show configured workspaces + aliases |
| `list_channels` | Channels | `conversations.list` | List channels with pagination |
| `get_channel_info` | Channels | `conversations.info` | Channel details: topic, purpose, members |
| `set_channel_topic` | Channels | `conversations.setTopic` | Update channel topic |
| `post_message` | Messages | `chat.postMessage` | Post to channel |
| `reply_to_thread` | Messages | `chat.postMessage` (threaded) | Reply in thread |
| `add_reaction` | Messages | `reactions.add` | Add emoji reaction |
| `get_channel_history` | Messages | `conversations.history` | Recent messages |
| `get_thread_replies` | Messages | `conversations.replies` | Thread replies |
| `search_messages` | Messages | `search.messages` | Search across channels (needs user token) |
| `get_users` | Users | `users.list` | List workspace users |
| `get_user_profile` | Users | `users.profile.get` | User details |
| `upload_snippet` | Files | `files.upload` | Upload text/code snippet |
| `schedule_message` | Scheduling | `chat.scheduleMessage` | Schedule future message |
| `list_scheduled_messages` | Scheduling | `chat.scheduledMessages.list` | View pending messages |
| `delete_scheduled_message` | Scheduling | `chat.deleteScheduledMessage` | Cancel scheduled message |

**Env variables:** `SLACK_WORKSPACE_{N}_BOT_TOKEN`, `_TEAM_ID`, `_NAME`, `_ALIASES`

**Key features:**
- Multi-workspace with aliases (`craft`/`crafti` → WS1, `craftiloo` → WS2)
- Auto channel name resolution (pass `general` instead of `C01ABC123`)
- Channel cache (populated on first use per workspace)
- Scope-aware error messages (shows needed vs provided scopes)

**Note:** `search_messages` requires a user token (`xoxp-`) with `search:read` scope. Bot tokens (`xoxb-`) will get a `missing_scope` error.

**If API stops working** → Check bot tokens in .env. Verify app is still installed in each workspace at https://api.slack.com/apps.

**Asana MCP Server** (`mcp-servers/asana/server.py`):

Custom Python MCP server replacing the NPM `@roychri/mcp-server-asana` package. Full project/task management with 26 tools in 8 groups. Auth: Personal Access Token (Bearer). Rate limiting: 0.2s between requests (~5/sec).

**Tools (24):**

| Tool | Group | Asana API | Key Capability |
|------|-------|-----------|----------------|
| `get_me` | User | `GET /users/me` | Current user info + workspace list |
| `list_workspaces` | User | `GET /workspaces` | All workspaces/organizations |
| `list_users` | User | `GET /workspaces/{gid}/users` | Users in a workspace |
| `list_teams` | Teams | `GET /organizations/{gid}/teams` | Teams in an organization |
| `list_projects` | Projects | `GET /workspaces/{gid}/projects` | Projects, filterable by team |
| `get_project` | Projects | `GET /projects/{gid}` | Full project details + members + custom fields |
| `create_project` | Projects | `POST /projects` | Create project with name, dates, team, color |
| `list_sections` | Sections | `GET /projects/{gid}/sections` | Sections within a project |
| `create_section` | Sections | `POST /projects/{gid}/sections` | Create section with ordering |
| `move_task_to_section` | Sections | `POST /sections/{gid}/addTask` | Move task between sections |
| `list_tasks` | Tasks | `GET /projects/{gid}/tasks` | Tasks by project, section, or assignee |
| `get_task` | Tasks | `GET /tasks/{gid}` | Full task details + notes + custom fields |
| `create_task` | Tasks | `POST /tasks` | Create task with assignee, dates, section |
| `update_task` | Tasks | `PUT /tasks/{gid}` | Update name, notes, completed, dates, assignee |
| `delete_task` | Tasks | `DELETE /tasks/{gid}` | Permanently delete a task |
| `list_subtasks` | Subtasks | `GET /tasks/{gid}/subtasks` | Child tasks under a parent |
| `create_subtask` | Subtasks | `POST /tasks/{gid}/subtasks` | Create subtask under parent |
| `get_task_stories` | Comments | `GET /tasks/{gid}/stories` | Comments + activity history |
| `add_comment` | Comments | `POST /tasks/{gid}/stories` | Add comment to a task |
| `list_tags` | Tags | `GET /workspaces/{gid}/tags` | All tags in workspace |
| `add_tag_to_task` | Tags | `POST /tasks/{gid}/addTag` | Tag a task |
| `remove_tag_from_task` | Tags | `POST /tasks/{gid}/removeTag` | Remove tag from task |
| `search_tasks` | Search | `GET /workspaces/{gid}/tasks/search` | Full-text search with filters |
| `add_dependency` | Dependencies | `POST /tasks/{gid}/addDependencies` | Set task dependency |
| `get_dependencies` | Dependencies | `GET /tasks/{gid}/dependencies` | Tasks this task depends on |
| `get_dependents` | Dependencies | `GET /tasks/{gid}/dependents` | Tasks blocked by this task |

**Env variable:** `ASANA_PERSONAL_ACCESS_TOKEN` in `.env`

**Key features:**
- Auto-pagination (up to 1000 items across 10 pages)
- Full CRUD for tasks, projects, sections, subtasks
- Task search with text, assignee, project, date, completion filters
- Dependency management (blockers + dependents)
- Comment/activity history on tasks
- Section-based task organization

**Skills using Asana:**
- **Daily Prep** → Task lists, upcoming deadlines, assigned work

**If API stops working** → Check ASANA_PERSONAL_ACCESS_TOKEN in .env. Get token from https://app.asana.com/0/my-apps → Create Personal Access Token.

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
