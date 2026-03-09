# Craftiloo Workspace - Complete Skill Workflow Guide

> **What is this?** A day-by-day, week-by-week plan for running every skill
> in the workspace. Shows what to run, when, in what order, and why.
>
> **Last updated:** 2026-03-08

---

## Table of Contents

1. [Quick Reference Calendar](#1-quick-reference-calendar)
2. [Daily Workflow](#2-daily-workflow)
3. [PPC Recurring Workflow](#3-ppc-recurring-workflow)
4. [Weekly Workflow](#4-weekly-workflow)
5. [Monthly Workflow](#5-monthly-workflow)
6. [Product & Listing Workflows](#6-product--listing-workflows)
7. [Research & Intelligence Workflows](#7-research--intelligence-workflows)
8. [Full Week Example](#8-full-week-example)
9. [Workflow Decision Trees](#9-workflow-decision-trees)
10. [Skill Chaining Rules](#10-skill-chaining-rules)
11. [Time and Cost Estimates](#11-time-and-cost-estimates)

---

## 1. Quick Reference Calendar

### What Runs When

**Daily Operations (every morning):**

| Cadence | Skill | Area | Est. Time | Est. Cost |
|:---:|---|---|:---:|:---:|
| **Every morning** | Daily Market Intel | Intelligence | ~5 min | ~$2.00 |
| **Every morning** | Daily PPC Health | PPC | ~3 min | ~$0.05 |

**Recurring (every 2-3 days):**

| Cadence | Skill | Area | Est. Time | Est. Cost |
|:---:|---|---|:---:|:---:|
| **Every 2-3 days** | Search Term Harvest | PPC | ~8 min | ~$0.10 |
| **Every 2-3 days** | Bid Review | PPC | ~5 min | ~$0.10 |
| **Every 2-3 days** | Portfolio Summary | PPC | ~4 min | ~$0.07 |

**Weekly:**

| Cadence | Skill | Area | Est. Time | Est. Cost |
|:---:|---|---|:---:|:---:|
| **Weekly** | Weekly PPC Analysis | PPC | ~10 min | ~$0.15 |
| **Weekly (after PPC)** | Keyword Rank Optimizer | PPC | ~6 min | ~$0.10 |
| **Weekly (after PPC)** | TACoS Optimizer | PPC | ~5 min | ~$0.10 |
| **Weekly** | Competitor Price/SERP Tracker | Intelligence | ~10 min | ~$2.00 |

**Monthly / On-Demand:**

| Cadence | Skill | Area | Est. Time | Est. Cost |
|:---:|---|---|:---:|:---:|
| **Monthly** | Monthly PPC Review | PPC | ~10 min | ~$0.15 |
| **On demand** | Listing Creator / Optimizer | Listings | ~10 min | ~$0.10 |
| **On demand** | Niche Category Analysis | Research | ~15 min | ~$0.15 |
| **On demand** | Customer Review Analyzer | Research | ~10 min | ~$0.10 |
| **On demand** | Portfolio Action Plan (deep dive) | PPC | ~15 min | ~$0.20 |
| **On demand** | Campaign Creator | PPC | ~10 min | ~$0.12 |

### Weekly Rhythm at a Glance

```
MON             TUE             WED             THU             FRI
 |               |               |               |               |
 v               v               v               v               v
Market Intel    Market Intel    Market Intel    Market Intel    Market Intel
PPC Health      PPC Health      PPC Health      PPC Health      PPC Health
 |               |               |               |               |
 v               v               |               v               |
Weekly PPC      Keyword         |              Search           |
Analysis        Rank Opt        |              Term Harvest     |
 |              TACoS Opt       |               |               |
 |               |               v               |               v
 |               |              Bid Review       |           Portfolio
 |               |               |               |           Summary
 |               |               |               |               |
 v               v               v               v               v
[On demand: Listing work, Niche Analysis, Review Analysis, Deep Dives]
```

**This is a SUGGESTED rhythm, not a rigid schedule.** The cadence system tracks
actual run dates. "PPC catch-up" identifies overdue PPC tasks regardless of day.

**Non-PPC skills** (listings, research, reviews, niche analysis) are triggered by
business need, not by a fixed cadence. Market Intel is the daily constant.

---

## 2. Daily Workflow

### Morning Routine (~10 minutes)

The daily routine serves the **entire business**, not just PPC.

**Step 1: Daily Market Intel** (~5 min, ~$2/day Apify cost)

```
User says: "market check" or "product pulse"
```

What it does:
- Scrapes competitor BSR, prices, reviews via Apify
- Pulls own sales data from Seller Board (7d)
- Checks DataDive Rank Radars for keyword position changes
- Compares everything to baseline (established 2026-02-11)

What you get:
- Hero product performance vs yesterday/baseline
- Competitor movement alerts (price drops, BSR jumps, new reviews)
- Keyword rank changes across all tracked radars
- Sales trend vs historical baseline

**This feeds the entire business:** listing decisions, pricing strategy,
product development priorities, and competitive positioning - not just PPC.

**Step 2: Daily PPC Health Check** (~3 min)

```
User says: "ppc morning" or "daily ppc" or "ppc health"
```

What it does:
- Pulls live campaign data (budgets, states, modifiers)
- Checks Rank Radar summary (keyword positions)
- Reads yesterday's health snapshot for comparison
- Produces GREEN / YELLOW / RED per portfolio

What to do with results:

| Result | Action |
|---|---|
| GREEN across the board | Proceed to other work |
| YELLOW flags | Note them, addressed in next bid review or harvest |
| RED flags | Consider running Portfolio Action Plan or Bid Review immediately |

### Daily Workflow Diagram

```
START OF DAY
     |
     v
Run "market check"
(competitor + sales intelligence)
     |
     v
Any competitor alerts?
  |         |
 YES        NO
  |         |
  v         v
Note for    Run "ppc morning"
listing/    (campaign health)
pricing          |
review           v
  |         Any RED flags?
  |           |         |
  |          YES        NO
  |           |         |
  |           v         v
  |        Address    Done!
  |        PPC issue  Proceed to
  v        immediately other work
Continue
to PPC health
```

---

## 3. PPC Recurring Workflow

These three skills run on a rotating basis. The PPC Agent tracks when each last ran
and "PPC catch-up" will tell you what is overdue.

### Search Term Harvest (~8 min)

```
User says: "harvest search terms" or "search term review"
```

**Run every 2-3 days.** This is the most impactful recurring task.

What it does:
1. Pulls 14-day search term report from Amazon Ads API
2. Classifies each term: NEGATE (waste) / PROMOTE (winner) / DISCOVER (potential)
3. Runs 5-step safety cross-reference (prevents false negations)
4. Presents classification to user for approval
5. Applies approved negations via API

What happens with results:

| Classification | What Happens |
|---|---|
| NEGATE | Applied as campaign-level negative keywords |
| PROMOTE | Flagged for exact-match campaign creation (Campaign Creator) |
| DISCOVER | Saved for next Campaign Creator run |

**Key safety:** The 5-step cross-reference checks: protected terms, rank data, existing negatives,
product title words, and cross-portfolio performance. This prevents accidentally negating
terms that convert in other campaigns.

### Bid Review (~5 min)

```
User says: "adjust bids" or "bid review"
```

**Run every 2-3 days.** Applies the TOS-First Bidding Philosophy.

What it does:
1. Reads placement + keyword reports (from most recent Weekly Analysis)
2. Classifies each campaign's placement health (6 categories)
3. Applies SOP decision matrix: ACoS x CVR x Rank Trend x Stage
4. Generates specific bid adjustment recommendations
5. User approval gate
6. Applies approved changes via API (TOS modifiers and/or default bids)

What gets changed:
- TOS modifier % (the primary lever)
- Default bid amounts (secondary lever, controls ROS/PP)
- Never uses round numbers (e.g., -31% not -30%)

### Portfolio Summary (~4 min)

```
User says: "portfolio check" or "portfolio health"
```

**Run every 2-3 days.** Quick health scan across all portfolios.

What it does:
1. Pulls campaign-level data grouped by portfolio
2. Classifies each: TOP PERFORMER / HEALTHY / NEEDS ATTENTION / RED FLAG / DORMANT
3. Audits campaign structure (does each portfolio have Auto, Broad, SK, MK, PT?)
4. Checks for experimental campaigns (SOP Section 13 compliance)

When to skip:
- Can be skipped if Daily Health showed all GREEN and no structural changes needed

### Rotating Schedule Suggestion

```
Day 1: Search Term Harvest
Day 2: Bid Review
Day 3: Portfolio Summary (or skip if all healthy)
Day 4: Search Term Harvest (cycle repeats)
Day 5: Bid Review
...
```

Or just say **"PPC catch-up"** and let the cadence system decide.

---

## 4. Weekly Workflow

### Monday/Tuesday: Weekly Analysis + Follow-ups (~25 min total)

**Step 1: Weekly PPC Analysis** (~10 min) -- THE data producer

```
User says: "weekly PPC" or "PPC analysis"
```

What it does:
1. Requests 4 async reports from Amazon Ads API (in parallel):
   - Campaign performance (spend, sales, ACoS, orders per campaign)
   - Search term performance (which queries triggered ads)
   - Placement performance (TOS vs ROS vs PP breakdown)
   - Keyword/targeting performance (bid efficiency per target)
2. Downloads + saves all 4 reports as JSON snapshots
3. Merges with DataDive Rank Radar data
4. Generates week-over-week comparison brief

**Why this is critical:** This produces the data files that 5+ other skills consume.
Without fresh weekly data, the Bid Recommender uses stale placement data, the
Search Term Harvester misses new terms, and the Keyword Rank Optimizer cannot cross-reference.

**Step 2: Keyword Rank Optimizer** (~6 min) -- run AFTER weekly analysis

```
User says: "rank optimizer" or "rank vs spend"
```

What it does:
1. Pulls fresh rank radar data from DataDive
2. Cross-references with PPC keyword spend from the weekly report
3. Classifies each keyword into 6 categories:

| Category | Meaning | Action |
|---|---|---|
| WASTING MONEY | Spending, rank not moving | Reduce/stop spend |
| REDUCE SPEND | Rank achieved, overspending | Lower bid |
| PROTECT | Rank achieved, maintain | Keep current bid |
| MAINTAIN | Rank improving, keep pushing | Continue spend |
| REDIRECT | Spending on wrong keywords | Shift to better targets |
| MONITOR | Not enough data | Wait for more data |

**Step 3: TACoS Optimizer** (~5 min) -- run AFTER weekly analysis

```
User says: "TACoS check" or "profit check"
```

What it does:
1. Pulls Seller Board profit data (actual revenue, COGS, fees, profit)
2. Calculates TACoS per portfolio: Ad Spend / Total Revenue x 100
3. Grades each portfolio: A (<target), B (target to 1.5x), C (1.5-2x), D (2-3x), F (>3x)
4. Checks organic momentum (is organic revenue growing as PPC spend stays flat?)
5. Profit reality check: is this portfolio actually profitable after all costs?

### Weekly Workflow Diagram

```
MONDAY/TUESDAY
     |
     v
Run Weekly Analysis
(4 reports generated)
     |
     +----------+-----------+
     |          |           |
     v          v           v
  Keyword    TACoS       Reports saved
  Rank Opt   Optimizer   for downstream
  (rank vs   (profit     skills
   spend)    reality)
     |          |
     v          v
  Signals    TACoS grades
  for bid    + profit
  changes    classifications
     |          |
     +-----+----+
           |
           v
     All state files
     updated with
     weekly data
```

### If You Miss a Week

No problem. Next time you say "PPC catch-up", the cadence system will flag
Weekly Analysis as overdue (>7 days) and run it first. Downstream skills
will use the fresh data once it exists.

---

## 5. Monthly Workflow

### First Week of Month: Monthly Review (~10 min)

```
User says: "monthly review" or "monthly PPC"
```

**Prerequisite:** At least 3-4 weekly snapshots should exist from the past month.

What it does:
1. Reads all weekly snapshots from the past 4 weeks (NO fresh API calls)
2. Reads all daily health snapshots for trend analysis
3. Reads all portfolio trackers for change history
4. Evaluates portfolio stage transitions:
   - Should any Launch portfolio graduate to Scaling?
   - Should any Scaling portfolio regress to Launch?
5. Budget reallocation recommendations
6. Dormant campaign cleanup recommendations
7. Competitive landscape changes (from market intel data)
8. Next month's strategic priorities

What it does NOT do:
- Does NOT pull fresh API data (reads files only)
- Does NOT make any changes (strategy recommendations only)
- Does NOT replace weekly granular analysis

### Monthly Decision: Portfolio Stage Transitions

```
Monthly Review evaluates each portfolio:

LAUNCH --> SCALING?
  Criteria:
  - ACoS trending toward 30% target
  - At least 3-5 hero keywords in top 10 organically
  - CVR stabilizing above 8%
  - Consistent order volume (not just spikes)

SCALING --> LAUNCH? (regression)
  Criteria:
  - ACoS deteriorating significantly
  - Lost key organic positions
  - New competitor entered and disrupted

Result: Updated portfolio stages in context/business.md
```

---

## 6. On-Demand Workflows

These are triggered by need, not by schedule.

### Portfolio Action Plan ("Deep Dive") -- ~15 min

```
User says: "deep dive [portfolio name]" or "fix [portfolio name]"
```

**When to run:**
- Daily Health shows RED for a portfolio
- Portfolio has been YELLOW for 3+ consecutive days
- User wants comprehensive optimization of a specific portfolio
- New portfolio needs initial setup

**What it does (most comprehensive PPC sub-skill):**
1. Pulls 5 report types for that ONE portfolio (30-day window)
2. Analyzes campaigns, keywords, search terms, placements, targeting
3. Checks Rank Radar trends for hero keywords
4. Generates impact-ranked action plan (P1 = highest impact)
5. User selects which actions to approve
6. Executes approved actions via API
7. Schedules follow-up reviews (7-day, 14-day)

### Campaign Creator -- ~10 min

```
User says: "create campaigns" or "build campaigns"
```

**When to run:**
- After Search Term Harvester identified DISCOVER terms
- After Portfolio Summary found structure gaps
- After Keyword Rank Optimizer found REDIRECT keywords
- User wants to expand a portfolio's campaign coverage

**Safety cap:** Maximum 5 campaigns per run, all created in PAUSED state.

### Listing Creator -- ~10 min

```
User says: "create a listing for [product]"
```

**When to run:** New product launching or existing listing needs complete rewrite.

### Listing Optimizer -- ~8 min

```
User says: "audit my listing" or "listing score"
```

**When to run:**
- Periodic listing health check (monthly)
- Conversion rate dropping despite good traffic
- Competitor has overtaken you in search results

### Niche Category Analysis -- ~15 min

```
User says: "explore [niche]" or "niche analysis"
```

**When to run:** Evaluating a new product category to enter.

### Customer Review Analyzer -- ~10 min

```
User says: "review analysis for [product]"
```

**When to run:** Before launching a competitor product, after negative review spike, or quarterly competitive intelligence.

---

## 6. Product & Listing Workflows

These are triggered by business need - product launches, optimization cycles,
or competitive pressure.

### New Product Launch Workflow

```
1. Niche Category Analysis ("explore [niche]")
   - Is this market worth entering?
   - GO / CONDITIONAL GO / NO-GO scorecard
       |
       v (if GO)
2. Customer Review Analyzer ("review analysis")
   - What do customers love/hate in this category?
   - What gaps can we fill?
       |
       v
3. Product Listing Development ("full listing")
   - Shared research (competitors + keywords)
   - Listing Creator (title, bullets, description, backend)
   - Image Planner (image-by-image strategy)
   - Notion upload (combined page)
       |
       v
4. Negative Keyword Generator ("generate negatives")
   - Proactive negatives from product knowledge
   - Applied before PPC campaigns launch
       |
       v
5. PPC Campaign Creator ("create campaigns")
   - Build initial campaign structure
   - All created PAUSED for manual review
```

### Existing Listing Optimization Workflow

```
1. Listing Optimizer ("audit my listing")
   - Ranking Juice scores vs competitors
   - Keyword gap analysis
   - AI-generated rewrites in 4 modes
       |
       v
   Score acceptable?
     |         |
    YES        NO
     |         |
     v         v
   Monitor   Listing Creator ("create listing")
   via next   - Full rewrite with latest data
   Market     - Push to Amazon via SP-API
   Intel          |
                  v
              Track impact in
              next Market Intel runs
```

### Competitor Response Workflow

```
1. Competitor Tracker ("competitor check")
   - Weekly price/BSR/SERP tracking
   - Alert on significant changes
       |
       v
   Competitor dropped price or gained rank?
     |         |
    YES        NO
     |         |
     v         v
2a. Customer Review   Monitor
    Analyzer          next week
    (what are they
     doing right?)
     |
     v
2b. Listing Optimizer
    (are we losing on
     listing quality?)
     |
     v
2c. Consider pricing
    or PPC response
```

---

## 7. Research & Intelligence Workflows

### Niche Viability Assessment

```
User says: "explore [niche]" or "niche analysis"
```

6-phase deep dive:
1. Market Landscape (how big, how competitive)
2. Pricing Analysis (price bands, margin potential)
3. Keyword Research (search volume, relevancy)
4. Review Mining (customer pain points, gaps)
5. Listing/Ranking Gap Analysis (where can we win?)
6. Viability Scorecard (0-40 points: GO / CONDITIONAL GO / NO-GO)

Uses: DataDive, SP-API, Seller Board, Apify

### Customer Sentiment Analysis

```
User says: "review analysis for [product]"
```

Two modes:
- **Deep Dive:** 1 product + 3 competitors, 50 reviews each
- **Category Scan:** Quick sentiment across a product category

Produces: Sentiment breakdown, competitive gaps, listing improvement opportunities

### Automation Discovery

```
User says: "automation audit" or "map my workflows"
```

30-40 minute structured interview that maps all business workflows and identifies
automation opportunities. Produces an interactive HTML dashboard with prioritized
recommendations scored by time saved x frequency x complexity.

---

## 8. Full Week Example

A realistic week showing how **all business areas** fit together, not just PPC.

### Monday -- Weekly Analysis Day

| Time | Action | Area | Command | Duration |
|:---:|---|---|---|:---:|
| 9:00 AM | Market intelligence | Intelligence | "market check" | 5 min |
| 9:05 AM | PPC health check | PPC | "ppc morning" | 3 min |
| 9:10 AM | Weekly PPC Analysis | PPC | "weekly PPC" | 10 min |
| 9:20 AM | Review weekly brief | PPC | Read output | 5 min |
| 9:25 AM | Keyword Rank Optimizer | PPC | "rank optimizer" | 6 min |
| 9:31 AM | TACoS Optimizer | PPC | "TACoS check" | 5 min |
| 9:36 AM | Competitor tracker | Intelligence | "competitor check" | 10 min |
| | **Total: ~45 minutes** | | | |

### Tuesday -- PPC + Listings

| Time | Action | Area | Command | Duration |
|:---:|---|---|---|:---:|
| 9:00 AM | Market intelligence | Intelligence | "market check" | 5 min |
| 9:05 AM | PPC health check | PPC | "ppc morning" | 3 min |
| 9:10 AM | Search Term Harvest | PPC | "harvest search terms" | 8 min |
| 9:18 AM | Review + approve | PPC | Interactive | 5 min |
| 9:25 AM | Listing audit (if needed) | Listings | "audit my listing" | 8 min |
| | **Total: ~29 minutes** | | | |

### Wednesday -- Light Day

| Time | Action | Area | Command | Duration |
|:---:|---|---|---|:---:|
| 9:00 AM | Market intelligence | Intelligence | "market check" | 5 min |
| 9:05 AM | PPC health check | PPC | "ppc morning" | 3 min |
| 9:10 AM | Bid Review | PPC | "adjust bids" | 5 min |
| 9:15 AM | Review + approve | PPC | Interactive | 5 min |
| | **Total: ~18 minutes** | | | |

### Thursday -- PPC + Research

| Time | Action | Area | Command | Duration |
|:---:|---|---|---|:---:|
| 9:00 AM | Market intelligence | Intelligence | "market check" | 5 min |
| 9:05 AM | PPC health check | PPC | "ppc morning" | 3 min |
| 9:10 AM | Search Term Harvest | PPC | "harvest search terms" | 8 min |
| 9:18 AM | Review + approve | PPC | Interactive | 5 min |
| 9:25 AM | Niche research (if exploring) | Research | "explore [niche]" | 15 min |
| | **Total: ~36 minutes** | | | |

### Friday -- Wrap-Up

| Time | Action | Area | Command | Duration |
|:---:|---|---|---|:---:|
| 9:00 AM | Market intelligence | Intelligence | "market check" | 5 min |
| 9:05 AM | PPC health check | PPC | "ppc morning" | 3 min |
| 9:10 AM | Portfolio Summary | PPC | "portfolio check" | 4 min |
| 9:14 AM | Bid Review (2nd run) | PPC | "adjust bids" | 5 min |
| | **Total: ~17 minutes** | | | |

### Weekend

No scheduled runs. Campaigns continue on autopilot.
Monday morning: fresh weekly data + competitor tracking.

### Monthly Addition (First Monday)

Add to Monday's routine:

| Time | Action | Command | Duration |
|:---:|---|---|:---:|
| After weekly | Monthly Review | "monthly review" | 10 min |
| After review | Update portfolio stages if needed | Manual | 5 min |

---

## 9. Workflow Decision Trees

### "Something Feels Wrong" Decision Tree

```
Problem: A portfolio is underperforming
     |
     v
Have you run Daily Health today?
  |          |
  NO         YES
  |          |
  v          v
Run it     What color is the portfolio?
  |          |           |           |
  |        GREEN       YELLOW       RED
  |          |           |           |
  |          v           v           v
  |     Probably      Run Portfolio  Run Portfolio
  |     fine. Check   Summary for    Action Plan
  |     back in       quick audit    (deep dive)
  |     2-3 days          |              |
  |                       v              v
  |                  Minor issues?   Major issues?
  |                    |     |         |      |
  |                   YES    NO       YES    NO
  |                    |     |         |      |
  |                    v     v         v      v
  |               Run Bid  Done    Execute  Investigate
  |               Review          fixes     listing/
  |               next            via API   targeting
  |               cycle                     (not PPC)
```

### "I Haven't Run PPC in a While" Decision Tree

```
How long has it been?
     |            |              |
  2-3 days     1 week        2+ weeks
     |            |              |
     v            v              v
  "PPC         "PPC           "PPC catch-up"
  catch-up"   catch-up"       (will run everything
  (will run    (will run        overdue in priority
  1-2 tasks)   3-4 tasks)       order)
     |            |              |
     v            v              v
  ~15 min      ~30 min        ~45-60 min
```

### "Should I Create New Campaigns?" Decision Tree

```
Why do you want new campaigns?
     |              |              |              |
     v              v              v              v
  DISCOVER       Structure     Rank            User
  terms from     gap found     Optimizer       request
  Harvester      by Summary    REDIRECT
     |              |              |              |
     v              v              v              v
  Run Campaign    Run Campaign   Run Campaign   Run Campaign
  Creator         Creator        Creator        Creator
  (auto-populates (fills gaps:   (new keyword   (user specifies
   from signals)   Auto, SK, PT)  targets)       targets)
     |
     +-- Max 5 campaigns per run
     +-- All created PAUSED
     +-- User must enable manually
```

### "What Should I Focus On Today?" Decision Tree

```
What is the business priority right now?
     |              |              |              |
     v              v              v              v
  Product        Competitor     Sales are      New market
  launching      gaining        dropping       to explore
  soon           ground
     |              |              |              |
     v              v              v              v
  Product        Competitor     Run Market     Niche Category
  Listing Dev    Tracker +      Intel +        Analysis
  (full          Review         Listing        (viability
   workflow)     Analyzer       Optimizer      assessment)
     |              |              |              |
     v              v              v              v
  Then set up   Then Listing   Then check     Then Customer
  PPC campaigns Optimizer      PPC health     Review
  (Campaign     (are we        (is PPC        Analyzer
   Creator)      behind?)      causing it?)   (gaps?)
```

### "What Listing Work Should I Do?" Decision Tree

```
What is the situation?
     |              |              |              |
     v              v              v              v
  New product    Existing       CVR dropping   Competitor
  launching      listing        despite good   overtook us
                 check-up       traffic
     |              |              |              |
     v              v              v              v
  Full listing   Listing        Listing        Listing
  workflow:      Optimizer      Optimizer      Optimizer
     |           (audit mode)   (audit mode)   + Customer
     v              |              |           Review
  Product           v              v           Analyzer
  Listing Dev    Score report   Identifies         |
  (orchestrator) with rewrite   specific           v
     |           recs           weak points   Competitive
     |              |              |           gap analysis
     v              v              v
  Listing +      Apply          Apply
  Image Plan     rewrites       rewrites
  + Notion       if score       focusing on
  page           is low         conversion
```

---

## 10. Skill Chaining Rules

### Must-Run-Before Dependencies

| Skill | Must Have Run First | Why |
|---|---|---|
| Keyword Rank Optimizer | Weekly Analysis | Needs targeting-report.json |
| TACoS Optimizer | Weekly Analysis | Needs campaign data for context |
| Campaign Creator | Search Term Harvester OR Portfolio Summary | Needs upstream signals |
| Monthly Review | 3-4 Weekly Analyses | Needs month of snapshot data |
| Bid Recommender | Weekly Analysis (within 7 days) | Needs placement-report.json |
| Daily Health | None | Self-contained (uses live API) |
| Search Term Harvester | None | Self-contained (pulls own report) |
| Portfolio Summary | None | Self-contained (pulls own report) |
| Portfolio Action Plan | None | Self-contained (pulls all 5 reports) |

### Optimal Chaining Order

When running multiple skills in one session, this order maximizes data reuse:

```
1. Weekly Analysis (produces data files)
     |
     +---> 2. Keyword Rank Optimizer (reads targeting report)
     |
     +---> 3. TACoS Optimizer (reads campaign data)
     |
     +---> 4. Search Term Harvest (reads search term report)
     |          |
     |          +---> 5. Campaign Creator (reads DISCOVER signals)
     |
     +---> 6. Bid Review (reads placement report)
     |
     +---> 7. Portfolio Summary (reads campaign report)
```

**Never run in wrong order:**
- Do not run Keyword Rank Optimizer before Weekly Analysis (no data)
- Do not run Campaign Creator before Search Term Harvester (no signals)
- Do not run Monthly Review with less than 3 weeks of weekly data

### Parallel vs Sequential

| Combination | Run In... | Why |
|---|:---:|---|
| Market Intel + PPC Health | Parallel | Independent data sources |
| Weekly Analysis then Rank Optimizer | Sequential | Rank Opt reads weekly data |
| Weekly Analysis then TACoS Optimizer | Sequential | TACoS reads weekly data |
| Search Term Harvest then Campaign Creator | Sequential | Creator reads harvest signals |
| Bid Review + Portfolio Summary | Either | Independent analyses |
| Niche Analysis then Review Analyzer | Sequential | Niche identifies competitors to review |
| Review Analyzer then Listing Creator | Sequential | Reviews inform listing strategy |
| Listing Optimizer then Listing Creator | Sequential | Audit first, then create |
| Market Intel + Competitor Tracker | Parallel | Independent data sources |

---

## 11. Time and Cost Estimates

### Weekly Total (Recommended Cadence)

**Daily Operations (all areas):**

| Activity | Area | Frequency | Time/Run | Weekly Total | Weekly Cost |
|---|---|:---:|:---:|:---:|:---:|
| Market Intel | Intelligence | 5x | 5 min | 25 min | $10.00 |
| PPC Health | PPC | 5x | 3 min | 15 min | $0.25 |
| Competitor Tracker | Intelligence | 1x | 10 min | 10 min | $2.00 |

**PPC Recurring:**

| Activity | Area | Frequency | Time/Run | Weekly Total | Weekly Cost |
|---|---|:---:|:---:|:---:|:---:|
| Search Term Harvest | PPC | 2x | 8 min | 16 min | $0.20 |
| Bid Review | PPC | 2x | 5 min | 10 min | $0.20 |
| Portfolio Summary | PPC | 1x | 4 min | 4 min | $0.07 |
| Weekly Analysis | PPC | 1x | 10 min | 10 min | $0.15 |
| Keyword Rank Optimizer | PPC | 1x | 6 min | 6 min | $0.10 |
| TACoS Optimizer | PPC | 1x | 5 min | 5 min | $0.10 |

**Weekly Total: ~100 min across all areas, ~$13**

**On-demand (as needed):**

| Activity | Area | Frequency | Time/Run | Weekly Cost |
|---|---|:---:|:---:|:---:|
| Listing Optimizer | Listings | 0-1x | 8 min | $0-0.10 |
| Listing Creator | Listings | 0-1x | 10 min | $0-0.10 |
| Niche Analysis | Research | 0-1x | 15 min | $0-0.15 |
| Review Analyzer | Research | 0-1x | 10 min | $0-0.10 |
| Portfolio Action Plan | PPC | 0-1x | 15 min | $0-0.20 |
| Campaign Creator | PPC | 0-1x | 10 min | $0-0.12 |

### Monthly Total

| Item | Estimate |
|---|---|
| Intelligence & monitoring | ~3-4 hours/month |
| PPC management | ~5-6 hours/month |
| Listing & research (as needed) | ~2-3 hours/month |
| API/token costs | ~$50-60/month (mostly Apify for Market Intel) |
| Claude Code tokens | ~$4-6/month |
| **Total monthly cost** | **~$55-65/month** |
| **Total time** | **~10-13 hours/month** |
| **Time saved vs manual** | **~25-35 hours/month** |

### Cost Breakdown by API

| API | Cost Driver | Typical Monthly |
|---|---|---|
| Amazon Ads API | Free (included with Seller Central) | $0 |
| Amazon SP-API | Free (included with Seller Central) | $0 |
| Seller Board | Subscription (not per-call) | Included |
| DataDive | Token-based for niche dives only | $0-5 |
| Apify | Per-actor-run ($0.25-0.50/run) | $6-10 |
| Notion API | Free | $0 |
| Slack API | Free | $0 |
| Asana API | Free | $0 |

---

> **This workflow is a living document.** As new skills are added or business
> priorities shift, update this file. PPC cadence tracking lives in agent-state.json.
> Non-PPC skills are triggered by business need and user judgment.
