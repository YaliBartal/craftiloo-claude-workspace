# Craftiloo Workspace Architecture - Complete System Map

> **What is this?** A complete guide to how the Craftiloo Claude Code Workspace operates.
> Every skill, every connection, every data flow - explained for someone seeing this
> system for the first time.
>
> **Last updated:** 2026-03-06

---

## Table of Contents

1. [What This Workspace Is](#1-what-this-workspace-is)
2. [How Claude Reads Its Instructions](#2-how-claude-reads-its-instructions)
3. [The Skill System](#3-the-skill-system)
4. [MCP Servers - External Connections](#4-mcp-servers---external-connections)
5. [Context Files - Living Memory](#5-context-files---living-memory)
6. [The PPC Agent - The Core Engine](#6-the-ppc-agent---the-core-engine)
7. [State Management - How Decisions Persist](#7-state-management---how-decisions-persist)
8. [Output Structure - Where Everything Goes](#8-output-structure---where-everything-goes)
9. [Complete Skill Reference](#9-complete-skill-reference)
10. [Data Flow Diagrams](#10-data-flow-diagrams)
11. [The Lessons System - Continuous Learning](#11-the-lessons-system---continuous-learning)
12. [Operating Rules and Safety Rails](#12-operating-rules-and-safety-rails)

---

## 1. What This Workspace Is

This is a **Claude Code workspace** - a folder on a Windows machine that Claude (an AI assistant)
reads every time it starts a conversation. The folder contains instructions, skills, API connections,
context files, and outputs that together form an **automated e-commerce operations system** for
**Craftiloo**, a family-owned craft kit brand selling primarily on Amazon US.

**Think of it as:** An AI-powered operations center where Claude acts as a virtual employee who can:
- Manage PPC advertising campaigns (bids, keywords, negatives, new campaigns)
- Create and optimize product listings
- Analyze competitors and market niches
- Track keyword rankings and organic growth
- Monitor daily business health
- Coordinate across Slack, Asana, Notion, and Amazon

**The key insight:** Claude does not remember between conversations. This workspace IS its memory.
Every file here exists so Claude can pick up exactly where it left off.

---

## 2. How Claude Reads Its Instructions

When Claude starts a conversation, it reads files in this order:

```
1. CLAUDE.md                          <- Master instruction file (always loaded first)
2. memory/MEMORY.md                   <- Persistent cross-session memory
3. context/*.md                       <- Business context (loaded on demand)
4. .claude/skills/{name}/SKILL.md     <- Skill instructions (loaded when triggered)
5. .claude/skills/{name}/LESSONS.md   <- Past run history (loaded before every skill run)
```

### CLAUDE.md - The Master File

This is the most important file. It contains:
- **Communication style rules** - Be concise, use bullets, skip filler
- **Operating principles** - Check skills first, self-improve, update context
- **Skill routing table** - Maps user phrases to specific skills
- **MCP server documentation** - What each API connection does and how to use it
- **File organization standards** - Naming conventions, folder structure, forbidden practices
- **Efficiency targets** - Token budgets, cost limits, execution time limits

**Key concept:** CLAUDE.md is a living document. Claude updates it when new skills are created,
new MCP servers are connected, or new patterns are discovered.

### memory/MEMORY.md - Cross-Session Memory

A persistent memory file that survives across conversations. Contains:
- **Critical rules** the user has stated (e.g., "always update portfolio trackers after changes")
- **Known system quirks** (e.g., "Seller Board MCP truncates data at 100 rows")
- **Links to topic-specific memory files** (e.g., api-patterns.md)

This is Claude's "notebook" - things it needs to remember that are not part of any specific skill.

---

## 3. The Skill System

Skills are **reusable instruction sets** stored as markdown files. Each skill lives in its own
folder under .claude/skills/ and contains:

```
.claude/skills/{skill-name}/
  SKILL.md      <- Instructions (the "how-to" guide)
  LESSONS.md    <- Run history, known issues, repeat errors (the "learning log")
```

### How Skills Get Triggered

The user types a natural language phrase. Claude matches it against the routing table in CLAUDE.md:

| User says... | Claude runs... |
|---|---|
| "ppc morning" | PPC Agent -> Daily Health Check |
| "create a listing" | Listing Creator |
| "audit my listing" | Listing Optimizer |
| "review analysis" | Customer Review Analyzer |
| "niche analysis" | Niche Category Analysis |
| "full listing" | Product Listing Development (orchestrator) |

### Skill Categories

The 23 skills fall into four functional groups:

**ORCHESTRATORS** (Route to sub-skills, coordinate data sharing)
- PPC Agent (routes to 10 PPC sub-skills)
- Product Listing Development (routes to Listing Creator + Image Planner)

**PPC SUB-SKILLS** (Invoked through PPC Agent, not directly)
- Daily Health Check, Bid Recommender, Search Term Harvester
- Portfolio Summary, Portfolio Action Plan, Campaign Creator
- Keyword Rank Optimizer, TACoS Optimizer, Monthly Review
- Weekly Analysis (can also run standalone)

**STANDALONE SKILLS** (Run independently)
- Listing Creator, Listing Optimizer, Image Planner
- Daily Market Intel, Customer Review Analyzer, Niche Category Analysis
- Negative Keyword Generator, Daily Prep

**UTILITY SKILLS** (Build/extend the workspace itself)
- Skill Creator, MCP Builder

---

## 4. MCP Servers - External Connections

**MCP (Model Context Protocol)** servers are custom Python programs that give Claude access to
external APIs. They run as background processes and expose tools Claude can call.

### Server Architecture

| Server | Tools | External API | Key Capabilities |
|--------|-------|-------------|-----------------|
| amazon-ads-api/server.py | 29 | Amazon Advertising API | SP/SB/SD campaigns, keywords, bids, async reports, negative keywords, product ads |
| amazon-sp-api/server.py | 14 | Amazon Selling Partner API | Orders, catalog, inventory, pricing, listing read/write, reports |
| sellerboard/server.py | 7 | Seller Board CSV Reports | Sales detailed (30d, 7d), inventory, PPC marketing, dashboard, summary |
| datadive/server.py | 12 | DataDive API | Keyword rank tracking (Rank Radars), competitor data, niche discovery, AI Copywriter |
| apify/server.py | 7 | Apify Platform | Web scraping actors, product/search/review scraping |
| notion/server.py | 28 | Notion API | Page CRUD, blocks, databases, markdown upload |
| slack/server.py | 16 | Slack (2 workspaces) | Messages, channels, search, scheduling |
| asana/server.py | 26 | Asana | Projects, tasks, sections, comments, search |
| GitHub (built-in) | 20+ | GitHub API | Repos, issues, PRs, code search |

### Which Skills Use Which APIs

| Skill | Amazon Ads | Amazon SP | Seller Board | DataDive | Apify | Notion | Asana |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **PPC Daily Health** | list_sp_campaigns, list_portfolios | - | reads snapshot | list_rank_radars | - | - | - |
| **PPC Bid Recommender** | create_ads_report, update_sp_campaigns, update_sp_ad_groups, get_sp_bid_recommendations | - | - | get_rank_radar_data | - | - | - |
| **PPC Search Term Harvester** | create_ads_report, manage_sp_negative_keywords, manage_sp_keywords | - | - | - | - | - | - |
| **PPC Portfolio Summary** | create_ads_report | - | - | - | - | - | - |
| **PPC Portfolio Action Plan** | create_ads_report (5), update/manage tools | - | - | get_rank_radar_data | - | - | - |
| **PPC Campaign Creator** | create_sp_campaigns, create_sp_ad_groups, manage_sp_keywords, manage_sp_product_ads | - | - | - | - | - | - |
| **Keyword Rank Optimizer** | reads weekly snapshot | - | - | get_rank_radar_data | - | - | - |
| **TACoS Optimizer** | reads weekly snapshot | - | get_sales_detailed, get_ppc_marketing | list_rank_radars | - | - | - |
| **Weekly PPC Analysis** | create_ads_report (x4) | - | - | get_rank_radar_data | - | - | - |
| **Monthly Review** | reads weekly snapshots | - | get_ppc_marketing, get_sales_summary | list_rank_radars | - | - | - |
| **Negative Keyword Gen** | manage_sp_negative_keywords | - | - | get_niche_keywords | - | - | - |
| **Daily Market Intel** | - | - | get_sales_detailed_7d | get_niche_competitors, list_rank_radars | run_actor | - | - |
| **Listing Creator** | - | - | - | get_niche_keywords, get_niche_ranking_juices | run_actor | create_page_with_content | - |
| **Listing Optimizer** | - | get_listing | - | 4 tools | - | - | - |
| **Image Planner** | - | - | - | - | run_actor | append_markdown | - |
| **Product Listing Dev** | - | - | - | get_niche_keywords, get_niche_ranking_juices | run_actor | find_or_create_page | - |
| **Customer Review Analyzer** | - | - | - | - | run_actor | - | - |
| **Niche Category Analysis** | - | - | - | create_niche_dive, get_niche_competitors, get_niche_keywords | run_actor | - | - |
| **Daily Prep** | - | - | get_sales_detailed_7d | - | - | - | list_tasks |

### API Authentication

All credentials in .env (git-ignored, never committed):

| Service | Auth Method | Key Variables |
|---|---|---|
| Amazon Ads | LWA OAuth2 (auto-refresh) | ADS_API_CLIENT_ID, SECRET, REFRESH_TOKEN, PROFILE_US |
| Amazon SP-API | LWA OAuth2 (auto-refresh) | SP_API_CLIENT_ID, SECRET, REFRESH_TOKEN, SELLER_ID |
| Seller Board | Embedded auth in report URLs | SELLERBOARD_INVENTORY_REPORT, etc. (6 URLs) |
| DataDive | API key header | DATADIVE_API_KEY |
| Apify | Bearer token | APIFY_API_TOKEN |
| Notion | Bearer token | NOTION_API_KEY |
| Slack | Bot tokens per workspace | SLACK_WORKSPACE_N_BOT_TOKEN |
| Asana | Personal access token | ASANA_PERSONAL_ACCESS_TOKEN |

### Rate Limiting (built into each MCP server)

| Server | Delay | Reason |
|---|---|---|
| Amazon Ads/SP | 0.5s | Amazon throttle limit |
| DataDive | 1.0s | Documented limit |
| Apify | 0.5s | Platform limit |
| Notion | 0.33s | Notion rate limit |
| Slack | 1.0s | Slack Tier 2 |
| Asana | 0.2s | Asana rate limit |

---

## 5. Context Files - Living Memory

Persistent reference data in context/, auto-updated by Claude when it learns new info:

### profile.md - Who The User Is
- Family-owned e-commerce since 2017
- Structured workflow: Asana (tasks), Notion (docs), Slack (comms)
- Values: efficiency, quality, data-driven decisions
- 2026 priorities: Barbie launches, retail expansion, branding
- Read by: Daily Prep, contextual skills

### projects.md - Current Projects
- Strategic projects with statuses and priorities
- Product pipeline (8+4 Barbie kits, ~4 new crafty kits)
- Ongoing initiatives (PPC, influencer, competitor analysis)
- Read by: Daily Prep, strategic skills

### business.md - The Business Bible (MOST READ FILE)

| Section | Contents | Why It Matters |
|---|---|---|
| Brand info | Craftiloo (sewing kits) + Shinshin Creations (fuse beads) | Product identity |
| Customer avatar | Grandparents/parents buying for girls 6-12 | Listing/keyword strategy |
| PPC Portfolio Stages | 17 portfolios with Launch/Scaling/General phase | **Every PPC decision depends on this** |
| Phase definitions | Launch = rank velocity, flexible ACoS. Scaling = efficiency, 30% ACoS | Threshold rules |
| Competitor list | 30+ primary, 12+ adjacent, 72 tracked ASINs | Competitive analysis |
| Sales channels | Amazon US, Shopify, Barnes and Noble | Multi-channel context |
| Tech stack | Asana, Slack, Notion, Toggl, etc. | Integration map |
| Notion database IDs | Product Listing Development page | Notion uploads |

### portfolio-name-map.json
Maps portfolio names to Amazon Ads portfolio IDs. Used by PPC skills.

### sku-asin-mapping.json
Maps SKUs to ASINs. Bridges Seller Board (SKUs) and Amazon Ads (ASINs).
Used by TACoS Optimizer and Daily Market Intel.

---

## 6. The PPC Agent - The Core Engine

The most complex part of the workspace. An orchestrator routing to 10 sub-skills
based on user intent + cadence tracking.

### Architecture

The PPC Agent sits at the center, routing user intent to specialized sub-skills:

**Layer 1 - User Intent Detection:**
- User says "ppc morning" / "daily ppc" / "ppc health" --> routes to Daily Health
- User says "adjust bids" / "bid review" --> routes to Bid Recommender
- User says "harvest search terms" / "negate" --> routes to Search Term Harvester
- User says "portfolio check" --> routes to Portfolio Summary
- User says "deep dive" / "fix portfolio" --> routes to Portfolio Action Plan
- User says "create campaigns" --> routes to Campaign Creator
- User says "rank optimizer" --> routes to Keyword Rank Optimizer
- User says "TACoS check" / "profit check" --> routes to TACoS Optimizer
- User says "monthly review" --> routes to Monthly Review
- User says "PPC catch-up" / "PPC status" --> checks cadence, runs what is overdue

**Layer 2 - Cadence Check:**
- Before routing, PPC Agent reads agent-state.json for last-run timestamps
- If the user said "PPC catch-up", it finds ALL overdue tasks and runs them in priority order
- If a specific skill is requested, it runs that skill regardless of cadence

**Layer 3 - Sub-Skill Execution:**
- Each sub-skill reads its own LESSONS.md first
- Pulls data from APIs or reads from files left by other skills
- Writes outputs to its designated folder
- Updates portfolio trackers and agent-state.json

### The Cadence System

| Task | Cadence | Purpose |
|------|---------|---------|
| **Daily Health** | Every day | 5-min traffic-light scan per portfolio |
| **Search Term Harvest** | Every 2-3 days | NEGATE/PROMOTE/DISCOVER + apply negatives |
| **Bid Review** | Every 2-3 days | SOP-based bid matrix + apply changes |
| **Portfolio Summary** | Every 2-3 days | Quick health scan + structure audit |
| **Weekly Analysis** | Weekly | 4-report deep dive with WoW comparison |
| **Keyword Rank Optimizer** | Weekly (after weekly) | PPC spend vs organic rank |
| **TACoS Optimizer** | Weekly (after weekly) | TACoS scoring + profit reality |
| **Campaign Creator** | On demand | New campaigns from upstream signals (max 5/run) |
| **Portfolio Action Plan** | On demand | Single-portfolio deep dive + fix everything |
| **Monthly Review** | Monthly | 4-week trends, stage transitions, budget realloc |

### Sub-Skill Data Sharing (files on disk)

Skills share data by reading files other skills wrote to disk. No skill re-fetches data that already exists:

**Weekly Analysis produces (other skills consume):**
- outputs/research/ppc-weekly/snapshots/{date}/campaign-report.json --> Bid Recommender, Portfolio Summary, TACoS Optimizer, Monthly Review
- outputs/research/ppc-weekly/snapshots/{date}/search-term-report.json --> Search Term Harvester
- outputs/research/ppc-weekly/snapshots/{date}/placement-report.json --> Daily Health (TOS health column), Bid Recommender
- outputs/research/ppc-weekly/snapshots/{date}/targeting-report.json --> Keyword Rank Optimizer
- outputs/research/ppc-weekly/snapshots/{date}/summary.json --> Portfolio Summary, Monthly Review, Daily Health

**Daily Health produces (next day consumes):**
- outputs/research/ppc-agent/daily-health/{date}-health-snapshot.json --> Next day's Daily Health (day-over-day comparison)

**Search Term Harvester produces:**
- outputs/research/ppc-agent/search-terms/{date}-classification-raw.json --> Campaign Creator (DISCOVER terms become new campaign seeds)

**Portfolio Action Plan produces:**
- outputs/research/ppc-agent/deep-dives/{portfolio}-{date}.md --> Monthly Review (referenced for context)

**Seller Board data (via Market Intel):**
- outputs/research/market-intel/snapshots/{date}-snapshot.json --> Daily Health, TACoS Optimizer, Monthly Review

**Key principle:** Never re-fetch data that another skill already has on disk.

---

## 7. State Management - How Decisions Persist

Two-tier state system for cross-session decision-making:

### Tier 1: Global Agent State

**File:** outputs/research/ppc-agent/state/agent-state.json

The dashboard file. Any skill can read it and immediately know:
- **Cadence timestamps** - when each task last ran (is anything overdue?)
- **Portfolio index** - per-portfolio quick-glance: health_status, ACoS, TACoS, trend, pending_count, top_action, next_review
- **All pending actions** - aggregated from every portfolio tracker, sorted by priority
- **Upcoming reviews** - scheduled re-check dates from all portfolios
- **Global pending actions** - cross-portfolio items

### Tier 2: Individual Portfolio Trackers

**Files:** outputs/research/ppc-agent/state/{portfolio-slug}.json (~17 files)

| Section | What It Stores | Why |
|---|---|---|
| goals | ACoS/CVR targets, rank targets | Decision thresholds |
| baseline | Write-once pre-agent snapshot | Measure improvement |
| latest_metrics | Most recent data + delta vs baseline | Current state |
| metric_history | Time-series (max 90 entries) | Trend detection |
| change_log | Every API change made | Audit trail, avoid re-doing |
| pending_actions | Queued work with priority/due dates | What to do next |
| scheduled_reviews | Upcoming re-check dates | When to revisit |
| skills_run | Execution history | Run log |
| improvement_assessment | Trend classification | Is this working? |

### State Update Rules (CRITICAL - #1 MOST VIOLATED RULE)

After ANY API change, update BOTH:
1. Portfolio tracker (state/{slug}.json) - change_log, pending_actions, metrics
2. Agent state (state/agent-state.json) - portfolio_index, all_pending_actions

Updated IMMEDIATELY after API calls succeed, BEFORE presenting results to user.

---

## 8. Output Structure - Where Everything Goes

All outputs live under the outputs/ folder, organized by function:

**outputs/research/ppc-agent/** - All PPC Agent outputs
- daily-health/ - Daily health check briefs + JSON snapshots (1 per day)
- bids/ - Bid recommendation briefs + change logs
- search-terms/ - Search term classification JSONs + action logs
- portfolio-summaries/ - Portfolio summary briefs
- deep-dives/ - Portfolio Action Plan deep dive reports
- tacos-optimizer/ - TACoS scorecards + profit analysis
- data/ - Raw API data files (campaign, keyword, search term, placement JSONs)
- briefs/ - Miscellaneous analysis briefs
- state/ - Portfolio trackers + agent-state.json (THE state management layer)

**outputs/research/ppc-weekly/** - Weekly PPC Analysis outputs
- snapshots/{date}/ - campaign-report.json, search-term-report.json, placement-report.json, targeting-report.json, summary.json
- briefs/ - Weekly analysis narrative reports

**outputs/research/market-intel/** - Daily Market Intel outputs
- snapshots/ - Daily BSR/rank/sales snapshots
- briefs/ - Market intel narrative reports

**outputs/research/listing-optimizer/** - Listing audit outputs
- briefs/ - Listing audit reports with scores and recommendations
- snapshots/ - Raw listing data snapshots

**outputs/research/listings/** - New listing outputs
- briefs/ - Generated Amazon listings (title, bullets, description, keywords)

**outputs/research/niche-analysis/** - Niche research
- reports/ - Viability assessments with competitor/keyword/pricing analysis

**outputs/research/customer-reviews/** - Review analysis
- reports/ - Sentiment analysis, competitive insights

### Naming: YYYY-MM-DD-{descriptor}.ext or {subject}-YYYY-MM-DD.ext

---

## 9. Complete Skill Reference

### PPC Skills (via PPC Agent)

| Skill | Purpose | Key APIs | Budget |
|---|---|---|---|
| **Daily Health** | 5-min GREEN/YELLOW/RED scan | Ads (campaigns, portfolios), DataDive (radars) | <30K, <3min |
| **Bid Recommender** | SOP-based bid matrix + apply | Ads (reports, updates), DataDive (ranks) | <60K, <5min |
| **Search Term Harvester** | NEGATE/PROMOTE/DISCOVER + apply | Ads (reports, negatives, keywords) | <60K, <8min |
| **Portfolio Summary** | Health scan + structure audit | Ads (campaign report) | <40K, <4min |
| **Portfolio Action Plan** | Deep dive + impact-ranked fixes + execute | Ads (5 reports + modify tools), DataDive | <120K, <15min |
| **Campaign Creator** | New campaigns from upstream signals | Ads (create all) | <70K, <10min |
| **Keyword Rank Optimizer** | PPC spend vs organic rank | DataDive (rank data), reads weekly | <60K, <6min |
| **TACoS Optimizer** | TACoS scoring + profit reality | Seller Board, DataDive, reads weekly | <60K, <5min |
| **Weekly Analysis** | THE data producer: 4 reports + WoW | Ads (4 reports), DataDive | <80K, <10min |
| **Monthly Review** | 4-week trends, stage transitions | Seller Board, DataDive, reads weekly | <100K, <10min |

### Standalone Skills

| Skill | Purpose | Key APIs |
|---|---|---|
| **Daily Market Intel** | BSR + rank tracking vs competitors | Seller Board, DataDive, Apify |
| **Listing Creator** | Complete Amazon listings from scratch | DataDive, Apify, Notion |
| **Listing Optimizer** | Audit + score vs competitors + rewrite recs | SP-API, DataDive (4 tools) |
| **Image Planner** | Competitor image analysis + strategy | Apify, Notion |
| **Product Listing Dev** | Orchestrator: Listing + Image (~50% API savings) | All from sub-skills |
| **Customer Review Analyzer** | Amazon review scraping + sentiment | Apify |
| **Niche Category Analysis** | New niche viability assessment | DataDive (3), Apify |
| **Negative Keyword Gen** | Proactive negatives from product knowledge | DataDive, Ads |
| **Daily Prep** | Morning check-in: yesterday + today | Seller Board, Asana |

### Key Distinctions

- **Neg Keyword Gen** (PROACTIVE: product knowledge) vs **Search Term Harvester** (REACTIVE: spend data)
- **Listing Creator** (generate new) vs **Listing Optimizer** (audit existing)
- **Portfolio Summary** (quick scan) vs **Portfolio Action Plan** (deep dive + fix)
- **Daily Health** (5-min, no reports) vs **Weekly Analysis** (4-report deep dive)

---

## 10. Data Flow Diagrams

### How Weekly Analysis Feeds Everything

The Weekly PPC Analysis is THE data producer for the entire PPC system.
It generates 4 reports via Amazon Ads API:

- **campaign-report.json** --> Bid Recommender, Portfolio Summary, TACoS Optimizer, Monthly Review
- **search-term-report.json** --> Search Term Harvester
- **placement-report.json** --> Daily Health (TOS health), Bid Recommender
- **targeting-report.json** --> Keyword Rank Optimizer
- **summary.json** --> Portfolio Summary, Monthly Review

### Listing Creation Flow

Product Listing Development (orchestrator) runs 4 phases:

1. **Shared Research** (runs ONCE) - Apify scrapers + DataDive keywords/ranking_juices
2. **Listing Creator** - Analyzes competitors, generates title, bullets, backend keywords
3. **Image Planner** - Analyzes competitor images, creates image-by-image strategy
4. **Notion Upload** - Combines listing + images on one Notion page



---

## 11. The Lessons System - Continuous Learning

Every skill has a LESSONS.md with:
- **Known Issues** - documented problems with workarounds
- **Repeat Errors** - issues that keep happening (with count, surfaced to user)
- **Resolved Issues** - fixed problems
- **Run Log** - dated entries with result, what worked/failed, lessons

**Before each run:** Read lessons. If Repeat Error occurs, tell user: "Repeat issue (xN): description"
**After each run:** Log result. Update Known/Repeat/Resolved.

**Why:** Claude has no memory between sessions. LESSONS.md IS the memory.

---

## 12. Operating Rules and Safety Rails

### Global PPC Rules

1. **Never pause on single-week zero conversions.** Check 30+ days first
2. **Never use round bid amounts.** Use -31%, -48%, not -30%, -50%
3. **Never negate on single-week zero conversions.** Check 30+ days first

### TOS-First Bidding Philosophy

- TOS (Top of Search) = primary conversion channel (best ACoS, best CVR)
- TOS modifier = THE lever (not default bid)
- Default bid = controls ROS/PP only
- New campaigns start TOS-heavy
- Bid increases = TOS modifier increases
- If TOS OK but ROS/PP waste -> lower default bid
- If TOS bleeding -> lower TOS modifier
- If everything bleeding -> NOT a bid problem (check listing/targeting)

### State Update Rule

After ANY API change: update BOTH portfolio tracker AND agent-state.json
IMMEDIATELY, BEFORE presenting results. This is the #1 most enforced rule.

### Efficiency Guardrails

Every skill has token budget (<30K to <120K) and time limit (<3min to <15min).

---

> **This document is a point-in-time snapshot.** The workspace evolves as new
> skills, APIs, and lessons are added. Check individual SKILL.md and LESSONS.md
> files for the most current state of each component.
