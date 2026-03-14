# Craftiloo E-Commerce Workspace

> **Living document** — Update as you learn. This is Claude's instruction set.

---

## Business Snapshot

**Brand:** Craftiloo — family-owned craft kit e-commerce brand (est. 2017)
**Sub-brand:** shinshin creation (fuse beads for adults)
**Revenue:** ~$2M/year | **Primary channel:** Amazon US (FBA)
**Products:** 76 SKUs across 8 categories (cross stitch, embroidery, sewing, latch hook, knitting, fuse beads, Barbie licensed, specialty)
**Hero products:** 13 active (see `context/hero-products.md`)
**PPC portfolios:** 17 active (see `context/portfolio-name-map.json`)
**Competitive position:** #1 in kids' cross stitch, kids' embroidery, mini fuse beads. Mid-tier in sewing, latch hook, knitting.
**Target customer:** Grandparents/parents buying gifts for girls aged 6-12
**Key 2026 initiative:** 8 Barbie-licensed kits launching

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

### 5. Lessons System (two-tier continuous improvement)

Knowledge is split into **shared context files** (cross-skill) and **skill-specific LESSONS.md** (lean).

**Shared knowledge files (loaded by relevant skills):**
| File | Content | Loaded by |
|------|---------|-----------|
| `context/api-patterns.md` | API quirks, formats, auth, field names | All skills using APIs |
| `context/ppc-rules.md` | PPC business rules, user preferences, structural patterns | PPC agent + sub-skills |
| `context/tooling-workarounds.md` | OneDrive, MCP truncation, PENDING reports, context mgmt | All skills |

**Skill-specific LESSONS.md** — lean format, no boilerplate, no duplicated rules:
- **Skill-Specific Lessons** (distilled list, max ~15 items)
- **Known Issues / Repeat Errors / Resolved Issues** (skill-specific only)
- **Recent Runs** (last 3 only, 4-5 lines each)

**Run log archives** → `outputs/research/{area}/run-logs/` (full narratives, never auto-loaded)

**Before every skill run:**
1. Read relevant shared knowledge files (api-patterns, ppc-rules, tooling-workarounds)
2. Read the skill's `LESSONS.md`
3. If a Repeat Error is encountered, **tell the user immediately** with occurrence count

**After every skill run:**
1. Write a run log file to `outputs/research/{area}/run-logs/YYYY-MM-DD-{skill}-{subject}.md` (full narrative)
2. Update LESSONS.md: add/update distilled lessons, update issues, replace oldest of 3 recent runs (4-5 lines)
3. If lesson is cross-skill, add to the appropriate `context/` knowledge file instead
4. End output with a brief **Lessons Update** note to the user

**Rules:**
- Never skip reading lessons — shared files + skill LESSONS.md are the first step
- Never skip writing — updating LESSONS.md is the last step
- If a Known Issue happens again, move to Repeat Errors and increment count
- Repeat Errors must be surfaced: _"⚠️ Repeat issue (×N): [description]"_
- Max 3 recent runs in LESSONS.md — older entries live in run-logs archive
- Don't create LESSONS.md for skills that haven't run yet — create on first run
- Cross-skill lessons go in `context/` files, NOT duplicated across LESSONS.md files

---

## Safety Rules (Money & Live Changes)

**Always confirm with user before:**
- Pausing or archiving any campaign or ad group
- Increasing any single bid by more than 30%
- Creating a new campaign (always propose first, wait for approval)
- Changing daily budgets
- Negating a keyword with >$5 total spend (might be valuable)

**Never:**
- Make changes to more than 3 campaigns in a single batch without user review
- Apply bid changes to "Launch" stage portfolios without explicit approval (rank velocity matters more than efficiency)
- Delete anything — always archive/pause instead

**Audit mode** (toggled via PPC agent) disables all write operations. Default: audit mode ON for new conversations.

---

## Context Management Protocol

**Context pressure thresholds — output quality degrades sharply and silently:**

| Context % | What's Happening | Required Action |
|-----------|-----------------|-----------------|
| 0–50% | Normal operation | Work freely |
| 50–70% | Minor slowdown | Prefer shorter outputs; use `save_path` for data |
| **70%** | **Precision drops noticeably** | **Run /compact at next logical break** |
| **85%** | **Hallucinations increase** | **Stop current task, /compact immediately** |
| **90%+** | **Erratic behavior** | **Write handoff → /clear → fresh session** |

**Strategic compaction in long skill runs — follow this phase structure:**
- **Phase 1:** Fetch all API data, save everything to disk via `save_path` — do NOT analyze yet
- **→ COMPACT HERE** (note all file paths written before compacting)
- **Phase 2:** Re-read saved files from disk, perform analysis, write intermediate findings
- **→ COMPACT HERE if context >60%** (optional second compact)
- **Phase 3:** Write final outputs, update LESSONS.md, send Slack notification

**Before any /compact or /clear — always write a handoff file first:**
- Path: `outputs/research/handoffs/YYYY-MM-DD-HHMM-[topic]-handoff.md`
- Must include: task status, files written (with paths), key findings/numbers, pending work, resume instructions
- The next session reads this handoff before starting

**Context efficiency rules:**
- Never pass raw API data through context — use `save_path` for any output >1KB
- Read only needed file sections (use `offset` + `limit` params on large files)
- Parallel API calls over sequential — batching cuts turns and context load in half
- The moment all data is fetched and saved to disk = the right time to compact

---

## Organization & File Management Standards

**CRITICAL: Follow these standards for ALL work, ALL skills, ALL outputs.**

### File Organization Hierarchy

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

| File Type | Format | Example |
|-----------|--------|---------|
| **Date-based outputs** | `YYYY-MM-DD-{descriptor}.ext` | `2026-02-09-morning-brief.md` |
| **Subject-based outputs** | `{subject-slug}-YYYY-MM-DD.ext` | `cross-stitch-analysis-2026-02-09.ext` |
| **Data files** | `{type}-{subject}-YYYY-MM-DD.json` | `product-data-cross-stitch-2026-02-09.json` |
| **Scripts** | `{action}_{subject}.py` | `generate_report.py`, `process_data.py` |

**Rules:**
- Use lowercase with hyphens (kebab-case) for file/folder names
- Always include dates in format YYYY-MM-DD
- Be descriptive but concise (max 50 chars for filename)
- Group related files in subfolders, NOT with prefixes

### Forbidden Practices

- Never dump files in root folders
- Never mix scripts with output files in same folder
- Never create temp files without cleaning them up
- Never use ambiguous names like "output.json", "data.txt", "test.py"
- Never create 25+ files in one folder without subfolders
- Never use inconsistent naming (some with dates, some without)

### Efficiency Guidelines

- Prefer the smallest API call that answers the question (7d report vs 30d when 7d suffices)
- Batch related API calls in parallel where possible
- Save large data to disk via `save_path` instead of passing through context
- When a skill exceeds 100K tokens, note it in LESSONS.md with what drove the cost
- Minimal file count (only what's necessary)
- Self-documenting structure (user can navigate without asking)

### When Creating New Output Folders

**Always include a README.md with:**
- Folder purpose
- Folder structure diagram
- File naming conventions used
- What goes where (table format)

---

## Folder Structure

```
Claude Code Workspace/
├── CLAUDE.md              # This file — Claude reads first
├── .env                   # API keys (71 vars)
├── .mcp.json              # MCP server configurations
├── .gitignore             # Protects .env and .mcp.json from Git
├── ARCHITECTURE.md        # System architecture overview
├── WORKFLOW.md            # Workflow documentation
│
├── .claude/
│   └── skills/            # 28 project-specific skills (see Skill Routing below)
│
├── automation/
│   ├── AUTOMATION-PLAN.md # n8n automation plan + architecture + testing guide
│   ├── config.yaml        # Skill runner config (timeouts, prompts, channels)
│   ├── skill-api.py       # HTTP API bridge for n8n → host (port 5680)
│   ├── skill-runner.py    # Production runner (locking, logging, git, Claude)
│   ├── n8n-workflows/     # n8n workflow JSONs (master + chains + git-sync)
│   ├── health-check.sh    # Daily server health ping to Slack
│   └── setup.sh           # One-time server setup
│
├── mcp-servers/           # 8 custom Python MCP servers (see MCP Services below)
│   ├── amazon-ads-api/    ├── amazon-sp-api/
│   ├── apify/             ├── asana/
│   ├── datadive/          ├── notion/
│   ├── sellerboard/       └── slack/
│
├── scripts/               # Utility scripts (data fetching, uploads)
│
├── context/               # Persistent context files
│   ├── profile.md              # User preferences, goals, working style
│   ├── projects.md             # Active projects tracker
│   ├── business.md             # Brand, products, market, competitors overview
│   ├── hero-products.md        # 13 hero products with ASINs, details, selling points
│   ├── products.md             # Full 76-SKU product catalog (EXW prices, contents, dimensions)
│   ├── competitors.md          # Competitor rankings by category, market share estimates
│   ├── search-terms.md         # Target search terms by category
│   ├── sku-asin-mapping.json   # SKU ↔ ASIN ↔ product name ↔ portfolio (ALWAYS check first)
│   ├── portfolio-name-map.json # Portfolio names, IDs, slugs, stages (for API calls)
│   ├── competitor-config.json  # Competitor ASIN tracking configuration
│   ├── notification-config.json # Slack channel routing for notifications
│   ├── mcp-reference.md        # Full MCP tool-by-tool documentation
│   ├── api-patterns.md         # Shared API gotchas (Amazon Ads, SP-API, Apify, DataDive, SB)
│   ├── ppc-rules.md            # PPC decision rules, user preferences, structural patterns
│   ├── tooling-workarounds.md  # Cross-skill workarounds (OneDrive, MCP, PENDING, etc.)
│   └── craftiloo-catalog.xlsx  # Original supplier catalog (Shantou Sorsa)
│
└── outputs/
    ├── research/          # All skill outputs organized by area
    │   ├── brand-analytics/
    │   ├── competitor-analysis/
    │   ├── competitor-tracker/
    │   ├── market-intel/
    │   ├── listing-manager/ # Listing state tracker, optimizations, new product research
    │   ├── ppc-agent/     # PPC state, briefs, data (14 subdirs)
    │   ├── ppc-weekly/
    │   ├── product-launch/ # (legacy — new products now go through listing-manager)
    │   ├── review-analysis/
    │   └── system-planning/
    └── data/              # Raw data exports
```

---

## Skill Routing

| User Request | Go To |
|--------------|-------|
| "Create a new skill" | → `.claude/skills/skill-creator/` |
| "Add an MCP" / "Connect to API" | → `.claude/skills/mcp-builder/` |
| "Start my day" / "Daily prep" | → `.claude/skills/daily-prep/` |
| "Automation audit" / "Map my workflows" | → `.claude/skills/automation-discovery-interview/` |
| "Market check" / "Product pulse" | → `.claude/skills/daily-market-intel/` |
| "Create a listing" / "New listing" / "Amazon listing" / "Listing for" | → `.claude/skills/listing-manager/` (NEW_PRODUCT mode) |
| "Optimize listing" / "Fix listing" / "Listing needs work" | → `.claude/skills/listing-manager/` (OPTIMIZE mode) |
| "Full listing" / "Launch product" / "Listing + images" | → `.claude/skills/listing-manager/` (NEW_PRODUCT + image plan) |
| "Image plan" / "Plan my images" | → `.claude/skills/image-planner/` (standalone) or listing-manager IMAGE_ONLY |
| "PPC" / "PPC check" / "PPC agent" / "PPC catch-up" / "PPC status" | → `.claude/skills/ppc-agent/` (Smart Catch-Up) |
| "Portfolio review" / "Full review" / "Review all portfolios" | → `.claude/skills/ppc-agent/` (Portfolio Review) |
| "Audit mode on" / "Audit mode off" / "Live mode" | → `.claude/skills/ppc-agent/` (toggles analysis-only mode) |
| "PPC morning" / "Daily PPC" / "PPC health" | → `.claude/skills/ppc-agent/` → ppc-daily-health |
| "Adjust bids" / "Bid recommendations" / "Bid review" | → `.claude/skills/ppc-agent/` → ppc-bid-recommender |
| "Portfolio check" / "Portfolio health" / "Portfolio flags" | → `.claude/skills/ppc-agent/` → ppc-portfolio-summary |
| "Harvest search terms" / "Negate and promote" / "Search term review" | → `.claude/skills/ppc-agent/` → ppc-search-term-harvester |
| "Create campaigns" / "Campaign creator" / "Build campaigns" | → `.claude/skills/ppc-agent/` → ppc-campaign-creator |
| "Portfolio deep dive" / "Deep dive" / "Portfolio action plan" / "Fix portfolio" | → `.claude/skills/ppc-agent/` → ppc-portfolio-action-plan |
| "Rank optimizer" / "Rank vs spend" / "Keyword rank analysis" | → `.claude/skills/ppc-agent/` → keyword-rank-optimizer |
| "Monthly PPC" / "Monthly review" / "PPC month" | → `.claude/skills/ppc-agent/` → ppc-monthly-review |
| "TACoS check" / "TACoS optimizer" / "Profit check" / "Profit reality" | → `.claude/skills/ppc-agent/` → ppc-tacos-optimizer |
| "PPC trends" / "PPC dashboard" / "30 day trend" | → `.claude/skills/weekly-ppc-analysis/` (trajectories built in) |
| "Weekly PPC" / "PPC analysis" / "Campaign analysis" | → `.claude/skills/weekly-ppc-analysis/` |
| "Search term analysis" / "Keyword mining" | → `.claude/skills/weekly-ppc-analysis/` |
| "Generate negatives" / "Negative keywords" | → `.claude/skills/negative-keyword-generator/` |
| "Review analysis" / "Customer reviews" / "What are customers saying" | → `.claude/skills/customer-review-analyzer/` |
| "Niche analysis" / "Category research" / "Explore a niche" | → `.claude/skills/niche-category-analysis/` |
| "Listing audit" / "Listing optimizer" / "Listing score" / "Portfolio scan" | → `.claude/skills/listing-optimizer/` |
| "Listing AB" / "Before after listing" / "Measure listing change" | → `.claude/skills/listing-ab-analyzer/` |
| "Competitor check" / "Competitor tracker" / "SERP tracker" | → `.claude/skills/competitor-price-serp-tracker/` |
| "Brand analytics" / "BA weekly" / "BA digest" | → `.claude/skills/brand-analytics-weekly/` |
| "Test notifications" / "Check notifications" | → `.claude/skills/notification-hub/` |

**New skills** → Always save to `.claude/skills/[skill-name]/SKILL.md` (project-local, not global)

---

## MCP Services

| Service | Tools | Purpose |
|---------|-------|---------|
| **Amazon Ads API** | 29 | Campaign management, keywords, targeting, product ads, negative keywords, bid recs, async reports |
| **Amazon SP-API** | 15 | Orders, catalog, inventory, pricing, listings, Brand Analytics reports |
| **Apify** | 7 | Web scraping — product data, search results, reviews |
| **Asana** | 26 | Project/task management, sections, subtasks, comments, search, dependencies |
| **DataDive** | 12 | Keyword rank tracking, competitor data, search volume, niche research |
| **GitHub** | — | Repository access, code search, issues, PRs (official MCP) |
| **Notion** | 28 | Pages, blocks, databases, comments, search, markdown import |
| **Seller Board** | 7 | Sales, profit, inventory, PPC marketing, daily dashboard (CSV reports) |
| **Slack** | 18 | Multi-workspace messaging, channels, search, scheduled messages, file upload |

**Full tool-by-tool reference:** `context/mcp-reference.md`

### Apify

Auth: Bearer token. Rate limit: 0.5s. **Env:** `APIFY_API_TOKEN`

**Gotchas:**
- Commonly used: `saswave~amazon-product-scraper` (BSR/price/reviews), `axesso_data~amazon-search-scraper` (SERP position/prices)
- axesso input format: `{"input": [{"keyword": "...", "country": "US"}]}`. Position field is `searchResultPosition` (0-indexed).

**Used by:** Daily Market Intel, Customer Review Analyzer, Niche Category Analysis
**If broken:** Check APIFY_API_TOKEN in .env. Get token from Apify Console → Settings → Integrations.

### Seller Board

Auth: Token embedded in report URLs. Rate limit: 0.5s. **Env:** `SELLERBOARD_INVENTORY_REPORT`, `SELLERBOARD_SALES_DETAILED`, `SELLERBOARD_SALES_DETAILED_7D`, `SELLERBOARD_SALES_SUMMARY`, `SELLERBOARD_DAILY_DASHBOARD`, `SELLERBOARD_PPC_MARKETING`

**Gotchas:**
- **CSV output capped at 100 rows by default.** Always use `save_path` parameter for 30d reports (~2000 rows). Without it you get ~5% of data.
- Sanity check: Craftiloo US does ~$170K/month revenue. If SB 30d data shows <$10K total, data is truncated.
- 7d report preferred for daily intel (~460 rows, manageable without save_path).

**Used by:** Weekly PPC, Daily Market Intel, Daily Prep
**If broken:** Tokens may have expired in Seller Board → Settings → Automation → Reports.

### DataDive

Auth: `x-api-key` header. Rate limit: 1 req/sec. **Env:** `DATADIVE_API_KEY`

**Gotchas:**
- `create_niche_dive` consumes tokens — confirm with user before running
- 23 active niches, 15 active rank radars

**Used by:** Weekly PPC, Daily Market Intel, Negative Keyword Generator, Niche Category Analysis, Listing Creator
**If broken:** Check DATADIVE_API_KEY in .env.

### Amazon SP-API

Auth: LWA OAuth2 (auto-refreshing, 1hr expiry). No AWS credentials needed. Rate limit: 0.5s.
**Env:** `SP_API_CLIENT_ID`, `SP_API_CLIENT_SECRET`, `SP_API_REFRESH_TOKEN`, `SP_API_SELLER_ID`, `SP_API_MARKETPLACE_US`, `SP_API_MARKETPLACE_CA`, `SP_API_MARKETPLACE_MX`

**Gotchas:**
- Brand Analytics weekly = Sun-Sat. Use `periods_back=2` on Sun/Mon (48h SLA — most recent week may not be ready)
- SQP report **requires `asins` param** (space-separated, max 200 chars) — all other BA reports don't
- SCP ≈ SQP organized by ASIN — if SQP fails, SCP provides equivalent funnel data
- Demographics report is console-only — NOT API-accessible
- Reports are async: create → poll status → download when DONE
- BA processing times: market_basket ~45s, sqp/scp/repeat ~60s, search_terms ~5min

**Used by:** Weekly PPC, Brand Analytics Weekly, Listing Optimizer, Daily Market Intel
**If broken:** Check app authorization in Seller Central → Apps & Services → Manage Your Apps. Refresh token is permanent unless de-authorized.

### Amazon Ads API

Auth: LWA OAuth2 (auto-refreshing). Rate limit: 0.5s. v3 endpoints use versioned Content-Type headers.
**Env:** `ADS_API_CLIENT_ID`, `ADS_API_CLIENT_SECRET`, `ADS_API_REFRESH_TOKEN`, `ADS_API_PROFILE_US`, `ADS_API_PROFILE_CA`

**Gotchas:**
- Report presets: `sp_campaigns`, `sp_search_terms`, `sp_keywords`, `sp_targets`, `sp_placements`, `sp_purchased_products`
- Reports are async: create → poll status → download + decompress
- Always use calendar-aligned date ranges, NOT `LAST_7_DAYS` (rolling window causes WoW comparison drift)

**Used by:** Weekly PPC, PPC Agent (all sub-skills), Negative Keyword Generator
**If broken:** Check ADS_API credentials in .env. Verify app is authorized in Amazon Advertising console.

### Notion

Auth: Bearer token. Rate limit: 0.33s (~3/sec). **Env:** `NOTION_API_KEY`

**Gotchas:**
- Auto-pagination up to 1000 items, auto-chunking at 100-block limit
- Use `append_markdown` or `create_page_with_content` for simplified markdown input
- Use `find_or_create_page` for dedup pattern
- Product Listing Development parent page: `30557318-d05c-806a-a94f-f5a439d94d10`

**Used by:** Product Listing Development, Listing Creator, Image Planner
**If broken:** Check NOTION_API_KEY in .env. Ensure pages/databases are shared with the integration.

### Slack

Auth: Bot token per workspace. Rate limit: 1 req/sec (Tier 2). **Env:** `SLACK_WORKSPACE_{N}_BOT_TOKEN`, `_TEAM_ID`, `_NAME`, `_ALIASES`

**Gotchas:**
- Two workspaces: `craft`/`crafti` (T06KHD4CS6N) and `craftiloo` (T01Q3BTU0DA)
- Auto channel name resolution — pass `general` not `C01ABC123`
- `search_messages` requires user token (`xoxp-`) with `search:read` scope — bot tokens get `missing_scope` error
- `create_channel` and `invite_to_channel` require `channels:manage` scope
- Notification channels: `#claude-morning-brief`, `#claude-ppc-updates`, `#claude-product-updates`, `#claude-competitor-watch`, `#claude-alerts`

**Used by:** Notification Hub (all 20+ skills post summaries)
**If broken:** Check bot tokens in .env. Verify app installed in each workspace at https://api.slack.com/apps.

### Asana

Auth: Personal Access Token (Bearer). Rate limit: 0.2s (~5/sec). **Env:** `ASANA_PERSONAL_ACCESS_TOKEN`

**Gotchas:**
- Auto-pagination up to 1000 items across 10 pages
- Task search supports text, assignee, project, date, completion filters

**Used by:** Daily Prep (task lists, upcoming deadlines)
**If broken:** Check token in .env. Get new token from https://app.asana.com/0/my-apps.

---

## Self-Update Rules

**Update this document when:**
- New skill is created → add to Skill Routing table
- New MCP is connected → add to MCP Services section
- You discover a pattern worth documenting

**Ask first before:**
- Removing existing sections
- Changing core operating principles
- Major structural changes

---

## Context

- **Domain:** E-commerce brand operations
- **Primary workflows:** Research, data collection, content creation, PPC management
- **Output location:** Always use `outputs/` subfolders, never dump in root

**Context files** → These are your **living memory**. Load them when you need background. Update them automatically when you learn new info (see Operating Principle #4).
