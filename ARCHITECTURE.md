# Craftiloo Workspace Architecture - Complete System Map

> **What is this?** A complete guide to how the Craftiloo Claude Code Workspace operates.
> Every skill, every connection, every data flow - explained for someone seeing this
> system for the first time.
>
> **Last updated:** 2026-03-08

---

## Table of Contents

1. [What This Workspace Is](#1-what-this-workspace-is)
2. [How Claude Reads Its Instructions](#2-how-claude-reads-its-instructions)
3. [The Skill System](#3-the-skill-system)
4. [MCP Servers - External Connections](#4-mcp-servers---external-connections)
5. [Context Files - Living Memory](#5-context-files---living-memory)
6. [Business Operations Areas](#6-business-operations-areas)
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
- Monitor daily business health (sales, BSR, competitor moves, keyword ranks)
- Create and optimize product listings (copy, images, backend keywords)
- Analyze competitors, customer reviews, and new market niches
- Manage PPC advertising campaigns (bids, keywords, negatives, new campaigns)
- Track keyword rankings and organic growth trends
- Coordinate work across Slack, Asana, Notion, and Amazon

**The workspace is designed to cover the entire business** - not just one department.
PPC advertising happens to be the most developed area right now, but the architecture
is the same for every business function: skills + APIs + context + state + outputs.

**The key insight:** Claude does not remember between conversations. This workspace IS its memory.
Every file here exists so Claude can pick up exactly where it left off.

### System Layers

The workspace is organized in 5 layers, from top (user-facing) to bottom (infrastructure):

| Layer | What Lives Here | Purpose |
|:---:|---|---|
| **5. OUTPUTS** | outputs/research/*/ | Date-stamped deliverables the user reads |
| **4. STATE** | outputs/research/*/state/ + snapshots/ | Persistent operational memory between sessions |
| **3. SKILLS** | .claude/skills/*/SKILL.md + LESSONS.md | Reusable instruction sets + learning logs |
| **2. CONTEXT** | context/*.md + context/*.json | Business facts, product data, portfolio maps |
| **1. INFRA** | CLAUDE.md + .mcp.json + .env + mcp-servers/ | Master config, API connections, credentials |

Data flows **upward**: Infrastructure enables Context, Context informs Skills, Skills produce State updates and Outputs.

Instructions flow **downward**: CLAUDE.md loads first, tells Claude where to find Context, which triggers Skills, which read/write State and produce Outputs.

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

### Skill Categories by Business Function

The 23 skills cover 6 business areas:

**DAILY OPERATIONS** (Morning routine, task management)
- Daily Prep - morning check-in: tasks, deadlines, business pulse
- Daily Market Intel - BSR tracking, competitor monitoring, rank changes

**MARKET RESEARCH** (Competitor intelligence, new opportunities)
- Customer Review Analyzer - review scraping + sentiment analysis
- Niche Category Analysis - new market viability assessment
- Competitor Price/SERP Tracker - weekly competitive intelligence

**PRODUCT LISTINGS** (Creation, optimization, image strategy)
- Listing Creator - generate Amazon listings from scratch
- Listing Optimizer - audit existing listings + rewrite recommendations
- Image Planner - competitor image analysis + image strategy
- Product Listing Development - orchestrator combining Listing + Image + Notion upload

**PPC ADVERTISING** (Campaign management via PPC Agent orchestrator)
- PPC Agent orchestrates 10 sub-skills: Daily Health, Bid Recommender,
  Search Term Harvester, Portfolio Summary, Portfolio Action Plan,
  Campaign Creator, Keyword Rank Optimizer, TACoS Optimizer,
  Monthly Review, Weekly Analysis
- Negative Keyword Generator (standalone, proactive)
- Weekly PPC Analysis (standalone, can run outside PPC Agent)

**WORKSPACE MANAGEMENT** (Build and extend the system itself)
- Skill Creator - create new skills
- MCP Builder - connect new APIs

**WORKFLOW DISCOVERY**
- Automation Discovery Interview - map workflows, find automation opportunities

### Skill Hierarchy Map

```
USER INPUT
    |
    v
+--CLAUDE.md ROUTING TABLE--+
|                            |
|   Direct Match?            |
|   Yes --> Run Skill        |
|   No  --> PPC Agent?       |
|           Yes --> Route     |
|           No  --> Ask user  |
+----------------------------+
    |                   |
    v                   v
ORCHESTRATORS        STANDALONE SKILLS
    |                   |
    |                   +-- Daily Prep ............... Seller Board, Asana
    |                   +-- Daily Market Intel ....... Seller Board, DataDive, Apify
    |                   +-- Listing Creator .......... DataDive, Apify, Notion
    |                   +-- Listing Optimizer ........ SP-API, DataDive
    |                   +-- Image Planner ............ Apify, Notion
    |                   +-- Customer Review Analyzer . Apify
    |                   +-- Niche Category Analysis .. DataDive, Apify
    |                   +-- Negative Keyword Gen ..... DataDive, Ads API
    |                   +-- Weekly PPC Analysis ...... Ads API, DataDive
    |
    +-- PPC AGENT (orchestrator)
    |       |
    |       +-- Daily Health ............. Ads API (live), DataDive
    |       +-- Bid Recommender .......... Ads API (reports + write), DataDive
    |       +-- Search Term Harvester .... Ads API (reports + write)
    |       +-- Portfolio Summary ........ Ads API (reports)
    |       +-- Portfolio Action Plan .... Ads API (all), DataDive
    |       +-- Campaign Creator ......... Ads API (create)
    |       +-- Keyword Rank Optimizer ... DataDive, reads files
    |       +-- TACoS Optimizer .......... Seller Board, DataDive
    |       +-- Monthly Review ........... reads files only
    |
    +-- PRODUCT LISTING DEV (orchestrator)
            |
            +-- Listing Creator (shared research)
            +-- Image Planner (shared research)
            +-- Notion Upload (combined page)
```

### Read vs Write: What Each Skill Does

| Skill | Reads from APIs | Writes to APIs | Analysis Only |
|:---:|:---:|:---:|:---:|
| Daily Health | YES | - | YES |
| Bid Recommender | YES | YES (bids) | - |
| Search Term Harvester | YES | YES (negatives, keywords) | - |
| Portfolio Summary | YES | - | YES |
| Portfolio Action Plan | YES | YES (bids, negatives, campaigns) | - |
| Campaign Creator | YES | YES (campaigns, ad groups, keywords) | - |
| Keyword Rank Optimizer | YES | - | YES |
| TACoS Optimizer | YES | - | YES |
| Weekly Analysis | YES | - | YES |
| Monthly Review | - (reads files) | - | YES |
| Listing Creator | YES | - | YES (generates copy) |
| Listing Optimizer | YES | - | YES (generates rewrites) |

**4 skills write to Amazon Ads API** (modify live campaigns). The rest are analysis-only.

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

### API Usage Intensity Map

How heavily each MCP server is used across all skills:

| MCP Server | Skills Using It | Heaviest User | Read/Write |
|:---:|:---:|---|:---:|
| **Amazon Ads API** | 11 skills | Portfolio Action Plan (5 report types + writes) | READ + WRITE |
| **DataDive** | 9 skills | Listing Optimizer (4 tools + AI Copywriter) | READ only |
| **Seller Board** | 5 skills | TACoS Optimizer (3 report types) | READ only |
| **Apify** | 5 skills | Daily Market Intel (2 actor types) | READ only |
| **Amazon SP-API** | 2 skills | Listing Optimizer (get_listing) | READ + WRITE |
| **Notion** | 3 skills | Product Listing Dev (page creation) | WRITE only |
| **Asana** | 1 skill | Daily Prep (task lists) | READ only |
| **Slack** | 0 skills* | - | - |
| **GitHub** | 0 skills* | - | - |

*Slack and GitHub are available but not embedded in any skill workflow. Used ad-hoc by the user.

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

### Context File Dependency Map

Which skills depend on which context files:

```
context/business.md  <---- EVERY PPC skill, Listing Creator, Listing Optimizer,
  (MOST READ)              Niche Analysis, Neg Keyword Gen, Daily Prep, Market Intel
       |
       +-- Portfolio stages (Launch/Scaling/General)
       +-- Competitor ASINs (72 tracked)
       +-- Customer avatar (buyer vs user)
       +-- Product lines (Craftiloo + Shinshin)

context/profile.md   <---- Daily Prep, strategic planning sessions
       |
       +-- User preferences, 2026 priorities

context/projects.md  <---- Daily Prep, project status checks
       |
       +-- Active projects, pipeline, statuses

context/portfolio-name-map.json  <---- ALL PPC skills
       |
       +-- Portfolio name <-> API ID resolution
       +-- Portfolio stage lookup

context/sku-asin-mapping.json    <---- TACoS Optimizer, Market Intel
       |
       +-- SKU <-> ASIN bridge
       +-- Seller Board <-> Ads API data join
```

---

## 6. Business Operations Areas

The workspace covers multiple business functions. Each area has its own skills,
data sources, and output folders. Here is how each operates.

### Area 1: Daily Operations

**Daily Prep** ("start my day") pulls Seller Board sales data + Asana tasks to
brief the user on yesterday's results and today's priorities. Uses Seller Board
and Asana APIs.

**Daily Market Intel** ("market check") is a comprehensive daily intelligence
system that runs 5 parallel data agents to track competitor BSR, pricing, reviews,
keyword rankings, and own sales performance. Uses Seller Board, DataDive, Apify,
and SP-API. Produces daily snapshots that build a historical comparison baseline.
This is independent of PPC and serves the entire business - product development,
pricing decisions, competitive strategy, and listing optimization all rely on
this data.

### Area 2: Market Research

**Customer Review Analyzer** scrapes Amazon reviews for own products and competitors,
producing sentiment analysis and competitive gap reports. Uses Apify.

**Niche Category Analysis** evaluates whether to enter a new product category with
a 6-phase viability assessment (market landscape, pricing, keywords, reviews,
listing gaps, GO/NO-GO scorecard). Uses DataDive, SP-API, Seller Board, and Apify.

**Competitor Price/SERP Tracker** runs weekly competitive intelligence, scraping
competitor ASINs for price/BSR/review changes and tracking SERP positions for
category keywords. Uses Apify.

### Area 3: Product Listings

**Listing Creator** generates complete Amazon listings (title, bullets, description,
backend keywords) from competitor analysis and keyword research. Uses DataDive,
Apify, and Notion.

**Listing Optimizer** audits existing listings using Ranking Juice scores, keyword
gap analysis, and AI-generated rewrites in 4 modes. Uses SP-API and DataDive.

**Image Planner** analyzes competitor images and creates image-by-image strategy
plans. Uses Apify and Notion.

**Product Listing Development** is an orchestrator that combines Listing Creator +
Image Planner with shared research (saving ~50% API cost) and uploads everything
to a single Notion page.

### Area 4: PPC Advertising (via PPC Agent)

The PPC Agent is an orchestrator that routes to 10 sub-skills based on user intent
and cadence tracking. It is the most developed area currently, but architecturally
it follows the same pattern as every other skill area.

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

### PPC Agent Decision Flowchart

```
User says something PPC-related
            |
            v
  +---Read agent-state.json---+
  |   (cadence timestamps,    |
  |    portfolio index,       |
  |    pending actions)       |
  +---------------------------+
            |
            v
  Is this a specific request?
  (e.g., "bid review", "harvest")
     |                |
    YES              NO --> "PPC catch-up" or "PPC status"
     |                |
     v                v
  Route directly    Check cadence: what is overdue?
  to that skill        |
     |                 +-- Daily Health overdue? --> Run it
     |                 +-- Search Harvest overdue? --> Run it
     |                 +-- Bid Review overdue? --> Run it
     |                 +-- Weekly Analysis overdue? --> Run it
     |                 +-- Nothing overdue? --> "All caught up!"
     |                 |
     v                 v
  +----Execute Sub-Skill----+
  | 1. Read LESSONS.md      |
  | 2. Read portfolio state |
  | 3. Pull API data        |
  | 4. Analyze              |
  | 5. Present to user      |
  | 6. [If writes needed]   |
  |    User approval gate   |
  | 7. Apply changes        |
  | 8. Update state (BOTH!) |
  | 9. Write LESSONS.md     |
  +-------------------------+
```

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

**Note:** The state management system described below is currently used by the PPC Agent.
The same pattern could be applied to any business area that needs cross-session
decision tracking (e.g., listing optimization campaigns, competitor monitoring).

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

### State Lifecycle Diagram

How a portfolio tracker evolves through skill runs:

```
DAY 1: Portfolio Action Plan runs
  |
  +-- Sets baseline (write-once snapshot)
  +-- Sets goals (ACoS target, rank targets)
  +-- Creates pending_actions (P1-P4 priority queue)
  +-- Schedules reviews (7-day, 14-day re-checks)
  +-- Logs to change_log + skills_run
  |
DAY 2: Daily Health reads tracker
  |
  +-- Reads latest_metrics for comparison
  +-- Updates latest_metrics with today's data
  +-- Appends to metric_history (trend line)
  +-- Updates health_status (GREEN/YELLOW/RED)
  |
DAY 3: Bid Recommender runs
  |
  +-- Reads pending_actions (finds bid-related P1s)
  +-- Makes API changes (bid adjustments)
  +-- Logs changes to change_log (before/after)
  +-- Marks pending_actions as completed
  +-- Adds new scheduled_reviews (re-check in 7 days)
  +-- Updates improvement_assessment (trend direction)
  |
DAY 7: Scheduled review comes due
  |
  +-- Daily Health flags it in the morning brief
  +-- User triggers the appropriate skill
  +-- Cycle repeats with fresh data
```

### Portfolio Health Status Flow

```
              NEW PORTFOLIO
                   |
                   v
            [No data yet]
              status: null
                   |
     First skill run (Deep Dive or Summary)
                   |
                   v
    +----Classify Health----+
    |                       |
    v          v            v
  GREEN     YELLOW         RED
  ACoS OK   ACoS warning   ACoS critical
  Spend OK   Spend high     Spend blowout
  Ranks OK   Ranks slipping  Ranks dropping
    |          |              |
    |          |              v
    |          |        Flag for immediate
    |          |        attention in Daily
    |          |        Health brief
    |          |              |
    v          v              v
  Monitor    Watch closely   Run Bid Recommender
  (next       (next 1-2      or Portfolio Action
   scheduled   days)          Plan urgently
   review)
```

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

### Daily Operations & Intelligence

| Skill | Purpose | Key APIs | Budget |
|---|---|---|---|
| **Daily Prep** | Morning briefing: tasks + sales + stock alerts | Seller Board, Asana | <30K, <3min |
| **Daily Market Intel** | BSR + rank + competitor tracking vs baseline | Seller Board, DataDive, Apify | <50K, <5min |

### Market Research & Competitive Intelligence

| Skill | Purpose | Key APIs | Budget |
|---|---|---|---|
| **Customer Review Analyzer** | Amazon review scraping + sentiment analysis | Apify | <40K, <10min |
| **Niche Category Analysis** | New niche viability (GO/NO-GO scorecard) | DataDive, SP-API, Apify | <60K, <15min |
| **Competitor Price/SERP Tracker** | Weekly price/BSR/SERP position tracking | Apify | <50K, <10min |

### Product Listings

| Skill | Purpose | Key APIs | Budget |
|---|---|---|---|
| **Listing Creator** | Generate Amazon listings from scratch | DataDive, Apify, Notion | <60K, <10min |
| **Listing Optimizer** | Audit + Ranking Juice scores + rewrite recs | SP-API, DataDive (4 tools) | <60K, <8min |
| **Image Planner** | Competitor image analysis + image strategy | Apify, Notion | <40K, <8min |
| **Product Listing Dev** | Orchestrator: Listing + Image + Notion upload | All from sub-skills | <100K, <15min |

### PPC Advertising (via PPC Agent)

| Skill | Purpose | Key APIs | Budget |
|---|---|---|---|
| **Daily Health** | 5-min GREEN/YELLOW/RED scan | Ads (campaigns, portfolios), DataDive | <30K, <3min |
| **Bid Recommender** | SOP-based bid matrix + apply | Ads (reports, updates), DataDive | <60K, <5min |
| **Search Term Harvester** | NEGATE/PROMOTE/DISCOVER + apply | Ads (reports, negatives, keywords) | <60K, <8min |
| **Portfolio Summary** | Health scan + structure audit | Ads (campaign report) | <40K, <4min |
| **Portfolio Action Plan** | Deep dive + impact-ranked fixes + execute | Ads (5 reports + modify), DataDive | <120K, <15min |
| **Campaign Creator** | New campaigns from upstream signals | Ads (create all) | <70K, <10min |
| **Keyword Rank Optimizer** | PPC spend vs organic rank | DataDive, reads weekly | <60K, <6min |
| **TACoS Optimizer** | TACoS scoring + profit reality | Seller Board, DataDive | <60K, <5min |
| **Weekly Analysis** | 4-report deep dive + WoW comparison | Ads (4 reports), DataDive | <80K, <10min |
| **Monthly Review** | 4-week trends, stage transitions | Seller Board, DataDive | <100K, <10min |
| **Negative Keyword Gen** | Proactive negatives from product knowledge | DataDive, Ads | <40K, <5min |

### Workspace Management

| Skill | Purpose | Key APIs | Budget |
|---|---|---|---|
| **Skill Creator** | Create new skills with SKILL.md + LESSONS.md | None | <20K, <3min |
| **MCP Builder** | Connect new external APIs | None | <30K, <10min |
| **Automation Discovery** | Map workflows + find automation opportunities | None | <50K, <40min |

### Key Distinctions

- **Daily Market Intel** (company-wide intelligence) vs **Daily Health** (PPC-specific check)
- **Neg Keyword Gen** (PROACTIVE: product knowledge) vs **Search Term Harvester** (REACTIVE: spend data)
- **Listing Creator** (generate new) vs **Listing Optimizer** (audit existing)
- **Portfolio Summary** (quick scan) vs **Portfolio Action Plan** (deep dive + fix)
- **Daily Health** (5-min, no reports) vs **Weekly Analysis** (4-report deep dive)
- **Customer Review Analyzer** (sentiment mining) vs **Competitor Tracker** (price/BSR tracking)

---

## 10. Data Flow Diagrams

### Company-Wide Data Sources

```
SELLER BOARD -----> Daily Prep (sales pulse)
                    Daily Market Intel (own product performance)
                    TACoS Optimizer (profit reality)
                    Monthly Review (account trends)

DATADIVE ---------> Daily Market Intel (rank tracking, competitor estimates)
                    Listing Optimizer (Ranking Juice scores, keyword gaps)
                    Listing Creator (keyword research, optimization scores)
                    Niche Category Analysis (competitor discovery, keyword data)
                    PPC skills (rank-aware bid decisions)

APIFY ------------> Daily Market Intel (competitor BSR/price scraping)
                    Customer Review Analyzer (review scraping)
                    Niche Category Analysis (product discovery)
                    Listing Creator (competitor product scraping)
                    Competitor Tracker (SERP position scraping)

SP-API -----------> Listing Optimizer (current listing content)
                    Niche Category Analysis (catalog search, pricing)
                    Daily Market Intel (orders, inventory)

AMAZON ADS API ---> PPC skills (campaign data, reports, bid/keyword changes)

NOTION -----------> Listing Creator (uploads listings)
                    Image Planner (uploads image plans)
                    Product Listing Dev (combined pages)

ASANA ------------> Daily Prep (tasks, deadlines)

SLACK ------------> Ad-hoc messaging (not embedded in skills)
```

### Market Intel Data Flow

Daily Market Intel feeds intelligence across the entire business:

```
Daily Market Intel
     |
     +---> Seller Board (own sales, 7d) ---> Revenue trends
     +---> DataDive (rank radars) ---------> Keyword position changes
     +---> DataDive (competitors) ---------> Competitor sales estimates
     +---> Apify (product scraper) --------> Competitor BSR/price/reviews
     +---> Apify (search scraper) ---------> SERP position tracking
     |
     v
  Market Intel Snapshot (outputs/research/market-intel/snapshots/)
     |
     +---> Informs listing decisions (is our listing underperforming?)
     +---> Informs pricing decisions (are competitors undercutting?)
     +---> Informs PPC decisions (are we losing rank despite spend?)
     +---> Informs product decisions (is the market growing/shrinking?)
     +---> Baseline comparison (track changes over time)
```

### PPC Data Pipeline

How Weekly Analysis feeds PPC-specific downstream skills:

- **campaign-report.json** --> Bid Recommender, Portfolio Summary, TACoS Optimizer, Monthly Review
- **search-term-report.json** --> Search Term Harvester
- **placement-report.json** --> Daily Health (TOS health), Bid Recommender
- **targeting-report.json** --> Keyword Rank Optimizer
- **summary.json** --> Portfolio Summary, Monthly Review

### Listing Creation Flow

```
Product Listing Development (orchestrator)
    |
    v
PHASE 1: Shared Research (runs ONCE, saves ~50% API cost)
    +-- Apify: scrape competitor products (BSR, price, reviews)
    +-- Apify: scrape competitor images (all 7+ slots)
    +-- DataDive: get_niche_keywords (search volumes)
    +-- DataDive: get_niche_ranking_juices (optimization scores)
    |
    |   [Research data saved to disk]
    |
    v
PHASE 2: Listing Creator
    +-- Reads shared research (no re-fetching!)
    +-- Analyzes competitor titles, bullets, descriptions
    +-- Generates: title, 5 bullets, description, backend keywords
    +-- Output: {product}-listing-{date}.md
    |
    v
PHASE 3: Image Planner
    +-- Reads shared research (no re-fetching!)
    +-- Analyzes competitor image strategies (7+ slots)
    +-- Creates: image-by-image plan with 4 copy alternatives each
    +-- Output: {product}-image-plan-{date}.md
    |
    v
PHASE 4: Notion Upload
    +-- Combines listing + image plan on one Notion page
    +-- Parent page: Product Listing Development database
    +-- Output: Notion page (linked in brief)
```

### PPC Data Pipeline

How data flows through the PPC system from raw API to actionable decisions:

```
EXTERNAL APIS                    FILES ON DISK                    DECISIONS
=============                    =============                    =========

Amazon Ads API                   Weekly Snapshots
  |                                |
  +--create_ads_report----+       |
  |  (4 report types)     |       |
  |                       v       |
  |                  campaign-report -------> Bid Recommender ----> Adjust bids
  |                  search-term-report ----> Search Term Harvest -> Negate/Promote
  |                  placement-report ------> Daily Health -------> TOS health check
  |                  targeting-report ------> Keyword Rank Opt ---> Spend reallocation
  |                  summary ---------------> Monthly Review -----> Strategy shifts
  |
  +--list_sp_campaigns-----> Daily Health ------> Traffic light status
  +--list_portfolios-------> All PPC skills ----> Portfolio grouping
  +--get_sp_bid_recs-------> Bid Recommender ---> Amazon suggested bids

Seller Board
  +--get_sales_detailed----> TACoS Optimizer ---> Profit reality check
  +--get_ppc_marketing-----> Monthly Review ----> Account-level trends

DataDive
  +--get_rank_radar_data---> Bid Recommender ---> Rank-aware bid decisions
  |                          Keyword Rank Opt --> Spend vs rank matrix
  +--list_rank_radars------> Daily Health ------> Quick rank summary
```

### Cross-Skill Signal Flow

Skills produce **signals** that trigger other skills:

| Producing Skill | Signal | Consuming Skill | What Happens |
|---|---|---|---|
| Search Term Harvester | DISCOVER terms | Campaign Creator | New SK campaigns for high-potential terms |
| Portfolio Summary | Structure gaps found | Campaign Creator | Fill missing campaign types |
| Keyword Rank Optimizer | WASTING MONEY keywords | Bid Recommender | Reduce bids on rank-stalled keywords |
| Keyword Rank Optimizer | REDIRECT keywords | Campaign Creator | New campaigns for better targets |
| Daily Health | RED flag portfolio | Portfolio Action Plan | Deep dive for urgent attention |
| TACoS Optimizer | LOSS-MAKING portfolio | Bid Recommender | Aggressive cost reduction |
| Weekly Analysis | All 4 reports | 5+ downstream skills | Fresh data for the week |


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

### Global Workspace Rules

1. **Check skills before creating anything new.** Always look in .claude/skills/ first
2. **Update context files when you learn new info.** Business changes go in context/business.md
3. **Read LESSONS.md before every skill run.** Surface repeat errors to the user
4. **Write to LESSONS.md after every skill run.** Log results, issues, and learnings
5. **Follow naming conventions.** YYYY-MM-DD-descriptor.ext or subject-YYYY-MM-DD.ext
6. **Never dump files in root folders.** Everything goes in organized output subfolders

### PPC-Specific Rules

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

### Portfolio Stage Transitions

```
                     LAUNCH
                   (Stage 1-2)
                       |
                       | ACoS target: flexible (up to 60%)
                       | Priority: rank velocity > efficiency
                       | Typical duration: 2-8 weeks
                       |
                       v
          +----- CRITERIA MET? -----+
          |                         |
         YES                       NO
          |                         |
          v                         v
       SCALING                  Stay in LAUNCH
     (Stage 3)                  (extend timeline)
          |
          | ACoS target: 30% (goal, not hard line)
          | CVR target: 10%
          | Priority: efficiency + defend ranks
          |
          v
    [Ongoing optimization cycle]

    GENERAL portfolios (Catch All, Shield)
    operate outside this lifecycle:
    - Catch All Auto: discovery + catch unassigned traffic
    - Shield All: brand defense + competitor blocking
    - Stitch Dictionary: cross-product visibility
```

### Bid Decision Matrix (Simplified)

The Bid Recommender uses placement health + performance to decide what lever to pull:

| Placement Health | ACoS | Action | Which Lever |
|:---:|:---:|---|:---:|
| TOS Dominant + Efficient | Low | Protect: maintain current | None |
| TOS Dominant + Efficient | High | Reduce default bid | Default bid DOWN |
| TOS Efficient, ROS/PP Bleeding | Any | Cut waste placements | Default bid DOWN |
| TOS Bleeding | Any | Reduce TOS modifier | TOS modifier DOWN |
| All Bleeding | Any | NOT a bid problem! | Check listing/targeting |
| No TOS Modifier Set | Any | Missing strategy | Add TOS modifier |

### Efficiency Guardrails

Every skill has token budget (<30K to <120K) and time limit (<3min to <15min).

---

> **This document is a point-in-time snapshot.** The workspace evolves as new
> skills, APIs, and lessons are added. Check individual SKILL.md and LESSONS.md
> files for the most current state of each component.
