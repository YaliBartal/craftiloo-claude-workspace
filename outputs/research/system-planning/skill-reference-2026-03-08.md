# Craftiloo AI System — Skill Reference Guide
**Date:** 2026-03-08 | **Total Skills:** 24 built · 20 planned

> This document covers every existing skill: what it needs, what it does, what it produces, and whether it depends on another skill running first.

---

## How to Read This Document

| Field | Meaning |
|-------|---------|
| **Inputs** | What you (the user) must provide or what must exist for the skill to run |
| **Data Sources** | APIs, MCP servers, or files the skill reads from |
| **What It Does** | The skill's process in plain language |
| **Output** | Files and content produced |
| **Dependencies** | Must another skill run first? Can it run standalone? |
| **Cadence** | How often this skill is designed to run |

---

## TABLE OF CONTENTS

1. [Entry Points (Where You Start Your Day)](#1-entry-points)
2. [Market Intelligence Domain](#2-market-intelligence)
3. [PPC Domain](#3-ppc-domain)
4. [Content & Listing Domain](#4-content--listing)
5. [Customer Research Domain](#5-customer-research)
6. [System Tools](#6-system-tools)
7. [Dependency Map (Quick Reference)](#7-dependency-map)

---

## 1. ENTRY POINTS

These are the skills you use to kick off the day. They don't produce analysis — they orient you and route you to the right place.

---

### 1.1 Daily Prep

| | |
|--|--|
| **Purpose** | Your morning check-in — see yesterday's business pulse, share your to-do list, and get a breakdown of how Claude can help with each task |
| **Cadence** | Daily (first thing in the morning) |

**Inputs:**
- Your to-do list (you tell Claude what you're working on today)
- Nothing else required — runs automatically

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Seller Board (Daily Dashboard) | Yesterday's revenue, units, profit, margin, ad spend, TACoS |
| Seller Board (Inventory) | Stock levels — flags anything <7 days or reorder-now |
| `context/profile.md` | Your preferences and working style |
| `context/projects.md` | Active projects |
| `context/business.md` | Brand and product context |

**What It Does:**
1. Pulls yesterday's business snapshot from Seller Board before you say a word
2. Flags any stock alerts (low inventory / reorder now)
3. Asks you: "What's on your to-do list today?"
4. For each task you share, rates how much Claude can help (Full Autopilot / Heavy Lifting / Accelerate / Can't Help)
5. Gives you a time-saved estimate for the whole day

**Output:**
- Displayed in chat (no file saved by default)
- Optional: `outputs/data/daily-plan-YYYY-MM-DD.md` (if you ask to save it)

**Dependencies:** None — fully standalone. Runs best when Seller Board is accessible.

---

### 1.2 Automation Discovery Interview

| | |
|--|--|
| **Purpose** | 30-40 minute structured interview that maps ALL your workflows and identifies what to automate, what to systematize, and what Claude can handle |
| **Cadence** | One-time (or when major business changes happen) |

**Inputs:**
- Your time (30-40 minutes of conversation)
- No files or data sources needed — this is a discovery interview

**Data Sources:** None (pure conversation — Claude asks, you answer)

**What It Does:**
1. Walks you through every area of your business systematically
2. Classifies each workflow into: Full Automation / Claude Skill / Claude Advisor / Manual
3. Scores each opportunity by time saved, complexity, and strategic value
4. Produces an interactive dashboard showing your automation landscape

**Output:**
- `outputs/data/automation-dashboard-YYYY-MM-DD.html` — Interactive dashboard with all workflows mapped and prioritized

**Dependencies:** None — this IS the starting point for understanding what to build.

---

## 2. MARKET INTELLIGENCE

These skills track your competitive position, product performance, and market movements.

---

### 2.1 Daily Market Intel

| | |
|--|--|
| **Purpose** | Daily snapshot of your hero products' BSR and rank vs competitors — "Are we improving or declining?" |
| **Cadence** | Daily |

**Inputs:**
- No user input required — runs automatically
- First run: establishes baseline (2026-02-11 is the reference point)

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Seller Board (7-day Sales Detail) | Actual sales, units, profit, ACoS per ASIN |
| Apify (Amazon Product Scraper) | BSR, price, reviews, rating for our ASINs + competitor ASINs |
| DataDive (Competitor Data) | Estimated sales/revenue for competitors (Jungle Scout-powered) |
| `context/business.md` | List of our hero ASINs + competitor ASINs to track |
| Previous snapshot | Yesterday's data for day-over-day comparison |

**What It Does:**
1. Fetches current BSR and rank for all tracked products (ours + competitors)
2. Pulls actual sales from Seller Board (our products only — no estimating)
3. Compares to yesterday and to the baseline date
4. Calculates competitive position (our rank vs competitor ranks)
5. Flags any significant changes (BSR spike, review count jump, price change)
6. Saves snapshot for future comparison

**Output:**
- `outputs/research/market-intel/briefs/YYYY-MM-DD-market-intel.md` — Daily market brief
- `outputs/research/market-intel/snapshots/YYYY-MM-DD-snapshot.json` — Machine-readable data (used by PPC Daily Health)

**Dependencies:** None — standalone. Other skills (PPC Daily Health) benefit from it running first, but it can run in any order.

> ⚡ **Tip:** Run this before PPC Daily Health — the health check reads this snapshot automatically, saving you an extra API call.

---

### 2.2 Competitor Price & SERP Tracker

| | |
|--|--|
| **Purpose** | Weekly competitive intelligence scan — what are competitors doing on price, BSR, and search rankings? |
| **Cadence** | Weekly |

**Inputs:**
- `context/competitor-config.json` — List of competitor ASINs + keywords to track per category (set up once, maintained ongoing)
- No user input required each week — runs from config

**Data Sources:**
| Source | What It Reads/Does |
|--------|-------------------|
| Apify (Amazon Product Scraper) | Price, BSR, reviews, rating for every competitor ASIN |
| Apify (Amazon SERP Scraper) | Top 10 search results for each tracked keyword |
| Previous snapshot | Last week's data for week-over-week comparison |
| `outputs/research/ppc-agent/state/agent-state.json` | Cadence tracking |

**What It Does:**
1. Scrapes all tracked competitor ASINs for current price, BSR, review count, rating, availability
2. Scrapes SERP positions for each tracked keyword (who ranks where)
3. Compares week-over-week: price changes, BSR changes, new competitors appearing
4. Generates alerts for significant changes (competitor price drop, new entrant in top 5)
5. Flags new ASINs discovered in SERP top 10 (for you to decide whether to track)
6. Writes competitive flags to PPC agent state (so PPC decisions can account for competitor moves)

**Output:**
- `outputs/research/competitor-tracker/briefs/YYYY-MM-DD-competitor-brief.md` — Weekly competitive brief with alerts
- `outputs/research/competitor-tracker/snapshots/YYYY-MM-DD-snapshot.json` — WoW comparison data

**Dependencies:**
- First run = baseline capture only (no alerts yet)
- Requires `context/competitor-config.json` to be set up with your competitor list
- Runs best weekly (checks cadence against last run date)

> ⚠️ **Cost note:** ~$4-5 per run in Apify credits (product + SERP scraping).

---

## 3. PPC DOMAIN

The PPC domain has a two-tier structure: the **PPC Agent** orchestrator at the top, and 10 specialist sub-skills below it. You always enter through the PPC Agent — it routes to the right sub-skill.

---

### 3.1 PPC Agent (Orchestrator)

| | |
|--|--|
| **Purpose** | The entry point for ALL PPC work — reads cadence state, identifies what's overdue, and routes to the right sub-skill |
| **Cadence** | Every time you do PPC work |

**Inputs:**
- What you want to do ("ppc", "bid review", "harvest terms", "monthly ppc", etc.)
- No data preparation required — reads state files automatically

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| `outputs/research/ppc-agent/state/agent-state.json` | Last run dates, portfolio health summary, all pending actions |
| `outputs/research/ppc-agent/state/{slug}.json` | Individual portfolio tracker files (15 total) |
| `context/business.md` | Portfolio stages, ACoS targets |

**What It Does:**
1. Reads the master state file to see what has run recently and what's overdue
2. Shows you portfolio health at a glance (GREEN / YELLOW / RED per portfolio)
3. Shows all pending actions across all portfolios
4. Routes you to the correct sub-skill based on your request
5. After every sub-skill run: updates state files to keep everything in sync

**Output:**
- Updates `agent-state.json` after every sub-skill run
- No standalone output files (outputs come from sub-skills)

**Dependencies:** None — this IS the entry point.

> 💡 **Say "ppc" with no other context** and it will show you the full cadence status (what's overdue) and let you choose what to tackle.

---

### 3.2 PPC Daily Health Check

| | |
|--|--|
| **Purpose** | 5-minute morning scan — traffic-light status per portfolio, rank radar summary, and today's top action |
| **Cadence** | Daily |

**Inputs:**
- None — reads from existing files + live campaign data

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Amazon Ads API | Live campaign list, portfolio list, TOS modifier settings |
| DataDive (Rank Radars) | Keyword rank summary — keywords in top 10 / top 50 |
| Market Intel snapshot | Seller Board TACoS, organic ratio, ad spend (reads file from daily-market-intel) |
| Weekly PPC snapshot | Placement health classifications per campaign (if <7 days old) |
| Portfolio tracker files | Pending actions, scheduled reviews, trend direction |

**What It Does:**
1. Loads all portfolio trackers to see pending actions and trends
2. Pulls live campaign data and groups campaigns by portfolio
3. Gets rank radar summary counts from DataDive (fast — no per-keyword data)
4. Reads TACoS and organic ratio from Market Intel snapshot (no re-fetching)
5. Computes traffic-light status for each portfolio: GREEN / YELLOW / RED
6. Produces a one-page morning brief with portfolio table + rank summary + today's priority

**Output:**
- `outputs/research/ppc-agent/daily-health/YYYY-MM-DD-health-check.md` — Morning brief
- `outputs/research/ppc-agent/daily-health/YYYY-MM-DD-health-snapshot.json` — Machine-readable snapshot

**Dependencies:**
- **Runs standalone** — but is much richer if Daily Market Intel has already run today (reads its snapshot automatically)
- Invoked via PPC Agent orchestrator

> ⚡ Best run after Daily Market Intel. Takes ~5 minutes total.

---

### 3.3 PPC Bid Recommender

| | |
|--|--|
| **Purpose** | Applies the PPC SOP bid-adjustment logic automatically — reads performance data, computes changes, presents a table for your approval, then executes via API |
| **Cadence** | Every 2-3 days |

**Inputs:**
- Which portfolio(s) to review (or "all" for account-wide)
- User approval before any changes are applied

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Amazon Ads API | Campaign-level performance report (last 7 days) |
| DataDive (Rank Radar) | Organic rank per keyword — drives rank-aware bid decisions |
| Weekly PPC snapshot | Baseline for context (reads existing file if <3 days old) |
| Rank-spend matrix | Output from Keyword Rank Optimizer (if available) |
| TACoS snapshot | Output from TACoS Optimizer (profit-aware bid priority) |
| Portfolio tracker files | Previous bid changes (for dedup), stage, ACoS targets |
| `context/business.md` | Portfolio stages, ACoS targets |

**What It Does:**
1. Pulls campaign + keyword performance data
2. Applies TOS-first bidding philosophy to classify each campaign:
   - TOS efficient, ROS/PP bleeding → lower default bid
   - TOS bleeding → lower TOS modifier
   - Everything bleeding → NOT a bid problem, flag for listing review
3. Cross-references organic rank to protect keywords where rank is improving
4. Produces a bid change table: keyword, current bid, recommended bid, rationale
5. Waits for your approval per row
6. Applies approved changes via Amazon Ads API

**Output:**
- `outputs/research/ppc-agent/bids/YYYY-MM-DD-bid-recommendations.md` — Recommendations table
- `outputs/research/ppc-agent/bids/YYYY-MM-DD-bid-changes-applied.json` — Applied changes log

**Dependencies:**
- **Can run standalone** — pulls its own fresh data
- Better if Weekly PPC Analysis has run recently (uses its snapshot to avoid re-fetching)
- Better if Keyword Rank Optimizer has run (rank-aware decisions)
- Better if TACoS Optimizer has run (profit-weighted priorities)
- Invoked via PPC Agent orchestrator

---

### 3.4 PPC Search Term Harvester

| | |
|--|--|
| **Purpose** | Classifies every search term the account has spent on into NEGATE / PROMOTE / DISCOVER, applies negatives, and queues PROMOTE terms for Campaign Creator |
| **Cadence** | Every 2-3 days |

**Inputs:**
- Which portfolios to include (or "all")
- User approval before negatives are applied

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Amazon Ads API | Search term report (last 30 days — takes 1-3 minutes to generate) |
| `context/search-terms.md` | Protected terms — NEVER negate these |
| Portfolio tracker files | Previously applied negatives (dedup — don't re-apply) |
| `outputs/research/negative-keywords/` | Proactive negatives already applied |
| Weekly PPC snapshot | Baseline context |

**What It Does:**
1. Pulls the full search term report (30 days of data, thousands of rows)
2. Loads the protected terms list (keywords you always want to keep)
3. Checks previously applied negatives so it doesn't recommend them again
4. Classifies each term:
   - **NEGATE:** High spend, zero conversions, 30+ days — wasted money
   - **PROMOTE:** Converting well in a broad/auto campaign — deserves its own exact match campaign
   - **DISCOVER:** Interesting but needs more data — monitor
5. Presents classified list for approval
6. Applies approved negatives via Amazon Ads API
7. Queues PROMOTE terms as pending actions for Campaign Creator

**Output:**
- `outputs/research/ppc-agent/search-terms/YYYY-MM-DD-search-term-harvest.md` — Full classified list
- `outputs/research/ppc-agent/search-terms/YYYY-MM-DD-applied-actions.json` — What was applied

**Dependencies:**
- **Can run standalone**
- Reads existing weekly snapshot if available (saves report generation time)
- PROMOTE outputs feed into Campaign Creator (not required, but part of the flow)
- Invoked via PPC Agent orchestrator

---

### 3.5 PPC Portfolio Summary

| | |
|--|--|
| **Purpose** | A focused portfolio-level scan — health classification per portfolio, campaign structure audit (per SOP), and top 3 portfolios needing action |
| **Cadence** | Every 2-3 days |

**Inputs:**
- None — runs automatically across all portfolios

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Amazon Ads API | Campaign-level report (last 7 days, 1 report only) |
| Weekly PPC snapshot | Comparison baseline (reads existing file) |
| Previous portfolio snapshot | For trend detection (improving / stable / declining) |
| `context/business.md` | Portfolio stages, ACoS targets |
| `agent-state.json` | Last run dates |

**What It Does:**
1. Pulls a single campaign-level report and groups results by portfolio
2. For each portfolio: ACoS, spend, sales, CVR, campaign count
3. Checks campaign structure against SOP (missing campaign types, missing TOS modifiers, budget caps)
4. Classifies portfolio health: GREEN / YELLOW / RED
5. Identifies top 3 portfolios needing the most attention
6. Flags structural issues (e.g., "Portfolio X has no auto campaign — discovery gap")

**Output:**
- `outputs/research/ppc-agent/portfolio-summaries/YYYY-MM-DD-portfolio-summary.md` — Summary report
- `outputs/research/ppc-agent/portfolio-summaries/YYYY-MM-DD-portfolio-snapshot.json` — Machine-readable snapshot

**Dependencies:**
- **Can run standalone**
- Better if Weekly PPC snapshot exists (uses it as baseline, avoids re-fetching)
- Outputs feed Campaign Creator (structure gaps = campaign creation signals)
- Invoked via PPC Agent orchestrator

---

### 3.6 PPC Portfolio Action Plan (Deep Dive)

| | |
|--|--|
| **Purpose** | Full deep dive on a single portfolio — comprehensive diagnosis + impact-ranked action plan + API execution |
| **Cadence** | On demand (when a portfolio needs serious attention) |

**Inputs:**
- Which portfolio to analyze (you name it, or pick from a list)
- User approval per action item before execution

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Amazon Ads API | All 4 reports: campaigns, keywords, search terms, placements |
| DataDive (Rank Radar) | Keyword-level organic rank data |
| Portfolio tracker file | Historical metrics, previous changes, pending actions |
| TACoS snapshot | Profit context for this portfolio |
| `context/business.md` | Portfolio stage, goals, hero ASINs |

**What It Does:**
1. Pulls all 4 Ads API reports for the selected portfolio
2. Full diagnosis: campaign health, keyword waste, placement efficiency, search term leakage, rank trends, structure gaps
3. Generates a prioritized action plan: every available improvement ranked by impact
4. Presents the plan for granular approval (approve / reject / modify per item)
5. Executes approved actions via Amazon Ads API
6. Logs every change to the portfolio tracker

**Output:**
- `outputs/research/ppc-agent/deep-dives/briefs/YYYY-MM-DD-{portfolio}-brief.md` — Full analysis + action plan
- `outputs/research/ppc-agent/deep-dives/snapshots/YYYY-MM-DD-{portfolio}-snapshot.json` — Portfolio state
- `outputs/research/ppc-agent/deep-dives/action-logs/YYYY-MM-DD-{portfolio}-action-log.json` — What was executed

**Dependencies:**
- **Can run standalone** on any portfolio
- Best run when you have a RED or persistent YELLOW portfolio that lighter skills haven't fixed
- Invoked via PPC Agent orchestrator

> ⏱ Takes 10-15 minutes total (deep analysis + execution). Most token-intensive PPC skill.

---

### 3.7 PPC Campaign Creator

| | |
|--|--|
| **Purpose** | Builds new campaigns from upstream signals — PROMOTE terms from Harvester, REDIRECT/PROTECT keywords from Rank Optimizer, structure gaps from Portfolio Summary |
| **Cadence** | On demand (triggered by pending actions from other skills) |

**Inputs:**
- No direct user input required — reads pending signals from other skills
- User approval of the full campaign proposal before anything is created

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Search Term Harvester output | PROMOTE candidates (terms converting in broad/auto) |
| Keyword Rank Optimizer output | REDIRECT/PROTECT keywords (rank-based campaign signals) |
| Portfolio Summary output | Structure gaps (missing campaign types per portfolio) |
| `agent-state.json` | All pending campaign-creation actions |
| `context/business.md` | Portfolio stages, hero ASINs |
| Negative keyword lists | For seeding new campaigns with existing negatives |
| Existing campaigns | Deduplication — won't create a campaign that already exists |

**What It Does:**
1. Gathers all pending campaign creation signals from upstream skills
2. Scores and deduplicates candidates (prioritizes by potential impact)
3. Builds full campaign specifications: name, ASIN, bid, TOS modifier, budget, keyword list, negatives
4. Presents a detailed proposal (max 5 campaigns per run) for your approval
5. Creates approved campaigns via Amazon Ads API — all in PAUSED state (you enable manually after review in Seller Central)

**Output:**
- `outputs/research/ppc-agent/campaign-creator/YYYY-MM-DD-campaign-proposals.md` — Proposal for review
- `outputs/research/ppc-agent/campaign-creator/YYYY-MM-DD-creation-log.json` — What was created

**Dependencies:**
- **Requires upstream signals** — if Search Term Harvester, Rank Optimizer, or Portfolio Summary haven't run recently, there may be nothing to create
- If no signals exist, it will tell you to run one of those skills first
- Invoked via PPC Agent orchestrator

---

### 3.8 TACoS & Profit Optimizer

| | |
|--|--|
| **Purpose** | Cross-references PPC performance with actual Seller Board profit data to answer: Is our PPC building organic momentum? Are we actually making money? Which portfolios deserve more/less investment? |
| **Cadence** | Weekly (after Weekly PPC Analysis) |

**Inputs:**
- None — reads from existing files + live data

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Seller Board (Sales Summary) | Total revenue, organic sales, ad spend per ASIN |
| Seller Board (PPC Marketing) | TACoS, ROAS, ACOS, conversion rate |
| Amazon Ads API | Portfolio-level spend and sales |
| DataDive (Rank Radar) | Organic rank trajectory per keyword |
| Weekly PPC snapshot | ACoS baseline for comparison |
| Portfolio tracker files | TACoS targets per portfolio |

**What It Does:**
1. Calculates TACoS per portfolio: `Ad Spend / Total Revenue (organic + PPC)`
2. Tracks whether organic is growing faster than ad spend (declining TACoS = good)
3. Cross-references with actual profit margins from Seller Board
4. Computes a TACoS scorecard: grade A-F per portfolio with targets
5. Tracks organic momentum score (0-100) per portfolio
6. Recommends which portfolios deserve more investment (good TACoS + profit) vs cutbacks (poor TACoS + no organic momentum)

**Output:**
- `outputs/research/ppc-agent/tacos-optimizer/briefs/YYYY-MM-DD-tacos-report.md` — TACoS scorecard
- `outputs/research/ppc-agent/tacos-optimizer/snapshots/YYYY-MM-DD-tacos-snapshot.json` — Data snapshot

**Dependencies:**
- **Can run standalone** but is most valuable after Weekly PPC Analysis (uses its snapshot for ACoS context)
- TACoS snapshot is read by Bid Recommender for profit-aware bid decisions
- Invoked via PPC Agent orchestrator

---

### 3.9 Keyword Rank Optimizer

| | |
|--|--|
| **Purpose** | Cross-references PPC spend per keyword with organic rank movement — "Are we spending on the right keywords?" |
| **Cadence** | Weekly (after Weekly PPC Analysis) |

**Inputs:**
- Scope: a specific portfolio or account-wide (you specify, or defaults to all)

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| DataDive (Rank Radar Data) | Daily organic rank per keyword (fresh — rank is the core data) |
| Amazon Ads API | Keyword-level spend and performance (uses weekly snapshot if <7 days old) |
| `context/business.md` | Portfolio stages, hero ASINs |
| Weekly PPC snapshot | Keyword data if available |

**What It Does:**
1. Gets fresh organic rank data for all tracked keywords from DataDive
2. Matches organic rank to PPC spend per keyword
3. Classifies each keyword into 6 categories:
   - **INVEST:** Good rank + converting well → increase spend
   - **PROTECT:** Good organic rank but losing ground → defend with PPC
   - **REDIRECT:** Converting but organic rank weak → dedicated campaign needed
   - **MONITOR:** Some traction but needs more data
   - **REDUCE:** Already ranking organically top 5 → reduce PPC (organic is doing the work)
   - **PAUSE:** High spend, no rank movement, not converting → waste
4. Produces a keyword matrix with rank + spend + classification
5. Queues REDIRECT/PROTECT keywords as signals for Campaign Creator

**Output:**
- `outputs/research/ppc-agent/rank-optimizer/briefs/YYYY-MM-DD-rank-optimizer.md` — Keyword classification report
- `outputs/research/ppc-agent/rank-optimizer/snapshots/YYYY-MM-DD/rank-spend-matrix.json` — Data matrix (used by Bid Recommender + Campaign Creator)

**Dependencies:**
- **Can run standalone**
- Much richer with Weekly PPC Analysis data available (avoids re-fetching keyword performance)
- Outputs feed Campaign Creator (REDIRECT/PROTECT signals) and Bid Recommender (rank-aware decisions)
- Invoked via PPC Agent orchestrator

---

### 3.10 Weekly PPC Analysis (Standalone)

| | |
|--|--|
| **Purpose** | Full weekly PPC analysis — 4 API reports, week-over-week comparison, campaign diagnosis, search term actions, placement data, targeting insights |
| **Cadence** | Weekly |

**Inputs:**
- None — runs against the full account automatically

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Amazon Ads API | 4 reports: Campaign, Search Term, Placement, Targeting (current week) |
| Previous weekly snapshot | Last week's data for week-over-week comparison |
| `context/business.md` | Portfolio stages, ACoS targets |
| `context/search-terms.md` | Protected terms |

**What It Does:**
1. Requests all 4 Ads API reports (takes 1-3 minutes to generate)
2. Processes campaign-level data: ACoS, ROAS, CVR, spend, sales, orders per campaign
3. Analyzes placement performance: TOS vs ROS vs Product Pages — classifies each as efficient/bleeding/dominant
4. Reviews targeting: keyword vs ASIN effectiveness
5. Classifies search terms: NEGATE / PROMOTE / DISCOVER
6. Computes week-over-week deltas for every key metric
7. Produces a comprehensive report + saves all 4 raw reports to disk for other skills

**Output:**
- `outputs/research/ppc-weekly/briefs/weekly-ppc-analysis-YYYY-MM-DD.md` — Full weekly report
- `outputs/research/ppc-weekly/snapshots/YYYY-MM-DD/campaign-report.json` — Raw data
- `outputs/research/ppc-weekly/snapshots/YYYY-MM-DD/search-term-report.json`
- `outputs/research/ppc-weekly/snapshots/YYYY-MM-DD/placement-report.json`
- `outputs/research/ppc-weekly/snapshots/YYYY-MM-DD/targeting-report.json`
- `outputs/research/ppc-weekly/snapshots/YYYY-MM-DD/summary.json` — Used by 6+ other skills

**Dependencies:**
- **Fully standalone** — the foundational weekly skill
- Many other PPC skills (Bid Recommender, Portfolio Summary, TACoS Optimizer, Keyword Rank Optimizer, Monthly Review) read its output snapshot to avoid re-fetching data
- **Run this first in the weekly PPC cycle** — everything else benefits from its data

> ⚡ **This is the most important weekly skill to run.** Its output snapshot is shared by 6 downstream skills.

---

### 3.11 PPC Monthly Review

| | |
|--|--|
| **Purpose** | Strategic monthly review — 4-week trends, stage transition recommendations, budget reallocation, dormant campaign cleanup |
| **Cadence** | Monthly (end of month) |

**Inputs:**
- None — reads exclusively from existing snapshots (no fresh API calls)

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| 4 weekly PPC snapshots | Campaign, placement, targeting data across the month |
| Portfolio summary snapshots | Portfolio health across the month |
| Bid change logs | All bid adjustments made this month |
| Search term action logs | All negatives/promotions applied this month |
| Daily health snapshots | Day-level granularity for trends |
| Market intel snapshots | Competitive context for the month |

**What It Does:**
1. Aggregates all weekly snapshots into a 4-week view
2. Calculates month-over-month trends for every key metric
3. Identifies portfolio stage transition candidates (e.g., Launch → Scaling if ACoS has stabilized)
4. Suggests budget reallocation across portfolios based on performance trends
5. Flags dormant campaigns that haven't produced in 60+ days
6. Reviews all changes made this month — what worked, what to reverse
7. Produces strategic recommendations for next month

**Output:**
- `outputs/research/ppc-agent/monthly/YYYY-MM-DD-monthly-review.md` — Full strategic review
- `outputs/research/ppc-agent/monthly/YYYY-MM-DD-monthly-snapshot.json` — Monthly aggregate data

**Dependencies:**
- **Requires at least 2 weekly snapshots** from Weekly PPC Analysis to function (ideally 4)
- Will tell you if insufficient data exists
- Makes no fresh API calls — pure snapshot aggregation
- Invoked via PPC Agent orchestrator

---

### 3.12 Negative Keyword Generator (Standalone)

| | |
|--|--|
| **Purpose** | Proactively generates negative keyword lists from product knowledge — prevents irrelevant traffic before it happens (as opposed to waiting for wasted spend) |
| **Cadence** | Once per portfolio at setup, then quarterly refresh |

**Inputs:**
- Which portfolio / product to generate negatives for (you specify)
- No other user input — uses product catalog knowledge

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| `context/business.md` | Product catalogue — what the product IS and ISN'T |
| DataDive (Master Keyword List) | Relevancy scores per keyword — identifies outlier terms |
| Amazon Ads API | Optional: recent search term report for context |
| `context/search-terms.md` | Protected terms — never included in negatives |

**What It Does:**
1. Reads the product's specifications, category, audience, and catalogue context
2. Identifies all the ways a customer could reach this product with irrelevant intent
3. Generates categorized negatives: wrong audience, wrong product type, wrong use case, competitor brand names (flagged separately for your decision)
4. Cross-references DataDive keyword relevancy scores — low-relevance terms go on the list
5. Presents the full list for your review and approval
6. After approval: generates copy-paste output for Seller Central + applies via API if requested

**Output:**
- `outputs/research/negative-keywords/briefs/{portfolio}-negatives-YYYY-MM-DD.md` — Review list + copy-paste output

**Dependencies:**
- **Fully standalone** — runs from product knowledge alone
- Complements Search Term Harvester: this skill prevents waste proactively; harvester catches waste reactively
- Feed its output to Campaign Creator to seed new campaigns with negatives from day one

---

## 4. CONTENT & LISTING

These skills handle everything related to creating and optimizing product listings.

---

### 4.1 Listing Creator

| | |
|--|--|
| **Purpose** | Creates a full Amazon listing from scratch — title, 5 bullets, description, backend keywords — based on competitor analysis, customer language, and search data |
| **Cadence** | Per new product |

**Inputs:**
- Product type / product name
- Key differentiators (what makes your product unique)
- Competitor ASINs (or Claude finds them — check context files first)
- Product specifications (dimensions, materials, age range, contents, etc.)

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Apify (Amazon Product Scraper) | Competitor product data, titles, bullets |
| Apify (Amazon SERP Scraper) | Keyword search results for category |
| DataDive (Niche Keywords) | Top keywords with real search volumes |
| DataDive (Ranking Juice) | Optimization scores — where competitors are strong/weak |
| DataDive (AI Copywriter) | AI-generated listing alternatives (4 modes) |
| `context/business.md` | Our product catalog, brand voice |

**What It Does:**
1. Finds and scrapes top 5 competitors (checks context files first, avoids re-scraping)
2. Analyzes competitor titles, bullets, and content structure
3. Identifies Rufus Q&A questions customers are asking about this product type
4. Extracts top keywords from DataDive with search volumes
5. Gets DataDive optimization scores to find gaps vs competitors
6. Generates: title (200-char optimized), 5 bullets (keyword-rich + benefit-first), description, 250-byte backend keywords
7. Provides alternative options for each section

**Output:**
- `outputs/research/listings/briefs/{product-slug}-listing-YYYY-MM-DD.md` — Final listing (copy-paste ready)
- `outputs/research/listings/research/{product-slug}-research-YYYY-MM-DD.md` — Research detail
- `outputs/research/listings/data/{product-slug}-keywords-YYYY-MM-DD.json` — Keyword data

**Dependencies:**
- **Standalone** — can run independently
- Richer with Customer Review Analyzer run first (customer language for bullets)
- If running alongside Image Planner, use **Product Listing Development** instead — shares research between both and saves ~50% of API calls

---

### 4.2 Image Planner

| | |
|--|--|
| **Purpose** | Analyzes competitor product images and creates a strategic image plan — exact copy/text per image, visual direction, and competitive rationale |
| **Cadence** | Per new product (or for refreshing existing images) |

**Inputs:**
- Product type
- Competitor ASINs (or Claude finds them)
- Key differentiators (what makes your product unique)

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Apify (Amazon Product Scraper) | Competitor product images (all 7 slots) |
| Apify | Customer reviews and Q&A for copy insights |
| `context/business.md` | Our product catalog, brand context |
| Existing listing research | If listing-creator ran first, reuses competitor data |

**What It Does:**
1. Scrapes all 7 product images for each competitor ASIN
2. Analyzes competitor visual strategies: what angles they use, what copy appears on images, what's missing
3. Mines customer reviews and Q&A for the language customers care about most
4. Creates a 7-image plan with:
   - Image 1-7 purpose and positioning
   - Exact copy/text to put on each image (headlines, callouts, feature labels)
   - Visual direction (scene, angle, props, mood)
   - Competitive rationale (what we do better than competitors in this image)

**Output:**
- `outputs/research/image-plans/briefs/{product-slug}-image-plan-YYYY-MM-DD.md` — Full image plan
- `outputs/research/image-plans/competitor-analysis/{asin}-images-YYYY-MM-DD.md` — Competitor breakdown

**Dependencies:**
- **Standalone** — can run independently
- Shares research with Listing Creator if run via **Product Listing Development** orchestrator
- Benefits from Customer Review Analyzer output (customer language for image copy)

---

### 4.3 Product Listing Development (Orchestrator)

| | |
|--|--|
| **Purpose** | Runs Listing Creator + Image Planner together in one workflow — shares research so you don't pay for the same API calls twice |
| **Cadence** | Per new product (replaces running both skills separately) |

**Inputs:**
- Product type
- Competitor ASINs
- Key differentiators
- Product specifications

**Data Sources:** Same as Listing Creator + Image Planner combined (but each piece of research is done once and shared)

**What It Does:**
1. Gathers all inputs once
2. Checks if any research already exists (skips re-running what's done)
3. Runs shared research once: competitor scraping, review mining, Q&A, keyword extraction
4. Uses that shared research to generate the listing
5. Uses that same shared research to generate the image plan
6. Uploads everything to a single Notion page for easy access

**Output:**
- `outputs/research/product-launch/{product-slug}/listing/` — Listing output
- `outputs/research/product-launch/{product-slug}/image-plan/` — Image plan output
- `outputs/research/product-launch/{product-slug}/research/` — Shared research files
- Notion page: full listing + image plan in one place

**Dependencies:**
- **This is the recommended way** to create both listing and images for a new product
- Replaces running Listing Creator and Image Planner separately (saves ~50% of API calls)
- Benefits from Customer Review Analyzer run first (reuses review data)

---

### 4.4 Listing Optimizer

| | |
|--|--|
| **Purpose** | Audits an existing Craftiloo listing — scores it against competitors on optimization, cross-references with sales and rank data, produces specific rewrite recommendations |
| **Cadence** | Monthly (or when CVR drops, rank declines, or you want to refresh a listing) |

**Inputs (Single Product Audit):**
- ASIN or product name to audit

**Inputs (Portfolio Scan):**
- None — scans all 13 hero products automatically

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Amazon SP-API | Current listing content (title, bullets, description, backend keywords) |
| DataDive (Ranking Juice) | Optimization scores for our listing + competitor listings |
| DataDive (AI Copywriter) | 4 alternative listing versions (cosmo, ranking-juice, nlp, cosmo-rufus) |
| DataDive (Rank Radar) | Rank trends — are we going up or down? |
| Seller Board (7d Sales Detail) | Sales velocity — prioritize fixes by revenue impact |
| Weekly PPC snapshot | CVR data — validates listing weaknesses with conversion data |

**What It Does:**
1. Reads your current live listing from Amazon
2. Gets DataDive optimization scores for our listing vs top 5 competitors
3. Identifies gaps: keywords missing from title, missing root words, weak bullets
4. Cross-references with rank trends (is rank declining correlated with listing weakness?)
5. Cross-references with CVR data from PPC (is conversion low, validating listing issues?)
6. Generates 4 AI Copywriter versions of the listing for comparison
7. Produces specific rewrite recommendations prioritized by impact x revenue

**Output:**
- Single audit: `outputs/research/listing-optimizer/briefs/{product-slug}-listing-audit-YYYY-MM-DD.md`
- Portfolio scan: `outputs/research/listing-optimizer/briefs/portfolio-scan-YYYY-MM-DD.md`
- Rewrites: `outputs/research/listing-optimizer/rewrites/YYYY-MM-DD/{product-slug}-rewrites-YYYY-MM-DD.md`
- Snapshot: `outputs/research/listing-optimizer/snapshots/{slug}-snapshot-YYYY-MM-DD.json`

**Dependencies:**
- **Standalone** — reads live listing data directly from Amazon
- Better with Customer Review Analyzer run first (customer language informs rewrites)
- Better with Weekly PPC Analysis data available (CVR context)

---

## 5. CUSTOMER RESEARCH

These skills dig into what customers are actually saying and what market opportunities exist.

---

### 5.1 Customer Review Analyzer

| | |
|--|--|
| **Purpose** | Scrapes Amazon reviews for our products and competitors, extracts complaint/praise themes, finds listing improvement opportunities, and tracks review trends over time |
| **Cadence** | Monthly (or before creating/refreshing a listing) |

**Inputs:**
- Mode choice: Single Product Deep Dive OR Category Scan
- ASIN(s) to analyze (or Claude uses the standard competitor list from context files)

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| Apify (Amazon Product Scraper) | Reviews (up to 500 per ASIN), ratings, Q&A |
| `context/business.md` | Our ASINs + competitor ASINs per category |
| Previous review snapshots | For trend tracking (rating drift, theme changes) |

**What It Does:**
1. Scrapes reviews for our product + top 3 competitors (Single Deep Dive mode)
2. Groups reviews into themes: complaint clusters, praise clusters
3. Quantifies each theme ("47% of 1-star reviews mention difficulty of instructions")
4. Finds competitive gaps: what we do better, what competitors do better
5. Generates listing optimization suggestions from customer language
6. Flags quality/safety issues (critical for kids products)
7. Extracts natural keyword language customers use (PPC opportunity)
8. Saves trend snapshot — compare next month to see if changes worked

**Output:**
- Deep dive: `outputs/research/review-analysis/briefs/{product-slug}-review-analysis-YYYY-MM-DD.md`
- Category scan: `outputs/research/review-analysis/briefs/{category}-category-scan-YYYY-MM-DD.md`
- Raw data: `outputs/research/review-analysis/data/YYYY-MM-DD/reviews-{ASIN}-YYYY-MM-DD.json`
- Trend snapshot: `outputs/research/review-analysis/snapshots/{slug}-snapshot-YYYY-MM-DD.json`

**Dependencies:**
- **Fully standalone**
- Feeds downstream: Listing Creator, Listing Optimizer, Image Planner, Negative Keyword Generator
- Run BEFORE creating or refreshing a listing for maximum impact

> ⚠️ Uses Apify credits (~$2-3 per deep dive run depending on review count).

---

### 5.2 Niche Category Analysis

| | |
|--|--|
| **Purpose** | Full market deep-dive for a niche you're considering entering — who dominates, pricing landscape, keywords, listing gaps, viability assessment, go/no-go recommendation |
| **Cadence** | Per new product category exploration |

**Inputs:**
- 1-3 niche keywords (e.g., "diamond painting kits", "crochet kits for beginners")
- Seed ASIN (recommended — a known top product in the niche)
- Price range and competitive concerns (optional context)

**Data Sources:**
| Source | What It Reads |
|--------|--------------|
| DataDive (Niche Competitors) | Actual sales/revenue estimates for top competitors (Jungle Scout-powered) |
| DataDive (Niche Keywords) | Top keywords with real search volumes |
| DataDive (Ranking Juice) | Listing optimization scores per competitor |
| DataDive (Niche Roots) | Root keyword analysis — frequency and volume |
| DataDive (Niche Dive) | Full automated competitor discovery from seed ASIN |
| Amazon SP-API | Real-time pricing, BSR, catalog data |
| Apify | Review scraping for competitor sentiment (fallback or supplement) |
| Seller Board | Our profit data if we're already in this niche |

**What It Does:**
1. Discovers the top competitors in the niche (not just who you know — finds all of them)
2. Gets actual sales estimates for each competitor (not BSR guessing)
3. Analyzes market share distribution — is it concentrated (hard to enter) or fragmented (opportunity)?
4. Maps the pricing landscape: average, range, price clusters
5. Pulls the real top keywords with actual search volumes
6. Scores competitor listings on optimization — weak listings = opportunity
7. Mines competitor reviews for recurring complaints (your product can solve these)
8. Assesses viability: is this worth entering? Go / No-go / Conditional with rationale

**Output:**
- `outputs/research/niche-analysis/{niche-slug}-analysis-YYYY-MM-DD.md` — Full viability report
- `outputs/research/niche-analysis/{niche-slug}-data-YYYY-MM-DD.json` — Raw competitive data

**Dependencies:**
- **Fully standalone** — the starting point for any new product consideration
- If you decide to enter the niche: feeds into Customer Review Analyzer, Listing Creator, Image Planner (which can reuse the competitor data found here)

---

## 6. SYSTEM TOOLS

Infrastructure skills that build and maintain the system itself.

---

### 6.1 Skill Creator

| | |
|--|--|
| **Purpose** | Creates new skills — generates properly structured SKILL.md + LESSONS.md files, adds routing to CLAUDE.md |
| **Cadence** | When you need a new capability |

**Inputs:**
- Description of what the new skill should do
- Trigger phrases (how you'll invoke it)
- Any known data sources or outputs

**Data Sources:** `CLAUDE.md` (reads for context on existing skills and routing)

**What It Does:**
Interviews you about the skill's purpose, generates a complete SKILL.md following the workspace's standard structure, creates LESSONS.md, updates the routing table in CLAUDE.md.

**Output:**
- `.claude/skills/{skill-name}/SKILL.md`
- `.claude/skills/{skill-name}/LESSONS.md`
- Updated routing entry in `CLAUDE.md`

**Dependencies:** None.

---

### 6.2 MCP Builder

| | |
|--|--|
| **Purpose** | Connects a new external service (MCP) or builds a custom API integration |
| **Cadence** | When adding a new data source or tool connection |

**Inputs:**
- Service name and what you want to connect (e.g., "connect Google Sheets", "add Shopify API")
- API credentials / keys

**Data Sources:** `.mcp.json`, `.env`, official MCP documentation

**What It Does:**
Checks if an official MCP server exists, configures it in `.mcp.json`, or builds a custom Python MCP server if no official one exists. Updates CLAUDE.md with the new service documentation.

**Output:**
- `.mcp.json` — Updated configuration
- `mcp-servers/{service}/server.py` — Custom server if built from scratch

**Dependencies:** None.

---

## 7. DEPENDENCY MAP

### 7.1 Skills That Run Best First

| Run This First | Benefits These Skills |
|---------------|-----------------------|
| **Daily Market Intel** | PPC Daily Health (reads its Seller Board snapshot) |
| **Weekly PPC Analysis** | Bid Recommender, Portfolio Summary, TACoS Optimizer, Keyword Rank Optimizer, Monthly Review |
| **Customer Review Analyzer** | Listing Creator, Image Planner, Listing Optimizer, Negative Keyword Generator |
| **Niche Category Analysis** | Listing Creator (reuses competitor data), Customer Review Analyzer |
| **PPC Search Term Harvester** | Campaign Creator (PROMOTE signals) |
| **Keyword Rank Optimizer** | Campaign Creator (REDIRECT/PROTECT signals), Bid Recommender |
| **Portfolio Summary** | Campaign Creator (structure gap signals) |

### 7.2 Skills That Are Fully Standalone

These skills can run at any time with no prerequisites:

| Skill | Notes |
|-------|-------|
| Daily Prep | Pure conversation — no dependencies |
| Automation Discovery Interview | One-time setup interview |
| Daily Market Intel | First skill of the day |
| Competitor Price & SERP Tracker | Weekly, from config only |
| PPC Daily Health | Standalone (richer with market intel) |
| PPC Portfolio Action Plan | Standalone deep dive on any portfolio |
| Weekly PPC Analysis | The foundational weekly skill |
| Negative Keyword Generator | Product-knowledge based, no upstream needed |
| Customer Review Analyzer | Pure research, no prerequisites |
| Niche Category Analysis | Pure research, no prerequisites |
| Listing Creator | Standalone (richer with review data) |
| Image Planner | Standalone (richer with review data) |
| Listing Optimizer | Reads live Amazon data directly |
| Skill Creator | System tool, no dependencies |
| MCP Builder | System tool, no dependencies |

### 7.3 Skills That Require Upstream Output

| Skill | Requires |
|-------|----------|
| **PPC Campaign Creator** | At least one of: Search Term Harvester (PROMOTE), Rank Optimizer (REDIRECT/PROTECT), or Portfolio Summary (structure gaps) |
| **PPC Monthly Review** | Minimum 2 weekly snapshots from Weekly PPC Analysis |
| **PPC Sub-Skills (all)** | Invoked via PPC Agent orchestrator |

### 7.4 Recommended Weekly Sequence

```
MONDAY
  └── Daily Market Intel
  └── PPC Daily Health (reads market intel snapshot)
  └── Weekly PPC Analysis        ← run once/week
  └── TACoS Optimizer            ← after weekly
  └── Keyword Rank Optimizer     ← after weekly

EVERY 2-3 DAYS
  └── PPC Search Term Harvester
  └── PPC Bid Recommender
  └── PPC Portfolio Summary

ON DEMAND
  └── PPC Campaign Creator       ← when PROMOTE/REDIRECT signals exist
  └── PPC Portfolio Action Plan  ← when a portfolio is RED
  └── Competitor Price Tracker   ← weekly

MONTHLY
  └── PPC Monthly Review
  └── Customer Review Analyzer
  └── Listing Optimizer

PER NEW PRODUCT
  └── Niche Category Analysis
  └── Customer Review Analyzer
  └── Product Listing Development (Listing + Images together)
  └── Negative Keyword Generator
```

---

## QUICK REFERENCE TABLE

| Skill | Domain | Cadence | Standalone? | Key Output |
|-------|--------|---------|-------------|------------|
| Daily Prep | Entry | Daily | ✅ | Daily task plan |
| Automation Discovery | Entry | Once | ✅ | Automation dashboard |
| Daily Market Intel | Market | Daily | ✅ | BSR/rank snapshot |
| Competitor Tracker | Market | Weekly | ✅ (needs config) | Competitive brief |
| PPC Agent | PPC | Always | N/A | Routes to sub-skills |
| PPC Daily Health | PPC | Daily | ✅ | Morning PPC brief |
| PPC Bid Recommender | PPC | 2-3 days | ✅ | Bid change table |
| PPC Search Term Harvester | PPC | 2-3 days | ✅ | NEGATE/PROMOTE list |
| PPC Portfolio Summary | PPC | 2-3 days | ✅ | Portfolio health flags |
| PPC Portfolio Action Plan | PPC | On demand | ✅ | Deep dive + execution |
| PPC Campaign Creator | PPC | On demand | ⚠️ Needs signals | Campaign proposals |
| TACoS Optimizer | PPC | Weekly | ✅ | TACoS scorecard |
| Keyword Rank Optimizer | PPC | Weekly | ✅ | Rank-spend matrix |
| Weekly PPC Analysis | PPC | Weekly | ✅ | Full weekly report |
| PPC Monthly Review | PPC | Monthly | ⚠️ Needs 2+ weekly snapshots | Strategic review |
| Negative Keyword Generator | PPC | Quarterly | ✅ | Proactive negatives |
| Listing Creator | Content | Per product | ✅ | Full Amazon listing |
| Image Planner | Content | Per product | ✅ | 7-image plan |
| Product Listing Development | Content | Per product | ✅ (orchestrator) | Listing + images combined |
| Listing Optimizer | Content | Monthly | ✅ | Audit + rewrites |
| Customer Review Analyzer | Research | Monthly | ✅ | Review insights |
| Niche Category Analysis | Research | Per opportunity | ✅ | Viability report |
| Skill Creator | System | As needed | ✅ | New SKILL.md |
| MCP Builder | System | As needed | ✅ | API connection |
