---
name: ppc-agent
description: PPC Agent — orchestrates all PPC skills based on user intent and cadence tracking
triggers:
  - ppc
  - ppc check
  - ppc agent
  - ppc catch-up
  - ppc status
  - ppc morning
  - daily ppc
  - ppc health
  - adjust bids
  - bid recommendations
  - bid review
  - portfolio check
  - portfolio health
  - portfolio flags
  - harvest search terms
  - negate and promote
  - search term review
  - monthly ppc
  - monthly review
  - ppc month
  - deal prep
  - deal ppc
  - prep for deal
  - post deal
  - deal ended
  - deal cleanup
  - rank optimizer
  - rank vs spend
  - keyword rank analysis
  - ppc rank check
  - rank spend analysis
  - rank investment
  - create campaigns
  - campaign creator
  - build campaigns
  - new campaigns
  - propose campaigns
  - tacos check
  - tacos optimizer
  - tacos scorecard
  - profit check
  - profit reality
  - tacos
  - profit
  - portfolio deep dive
  - deep dive
  - portfolio action plan
  - fix portfolio
  - work on portfolio
output_location: outputs/research/ppc-agent/
---

# PPC Agent

**USE WHEN** user says anything PPC-related: "ppc", "ppc check", "ppc morning", "adjust bids", "portfolio check", "harvest search terms", "monthly ppc", "ppc catch-up", or similar.

---

## What This Is

The PPC Agent is an **orchestrator** — it does not perform PPC analysis itself. It routes to the right sub-skill based on user intent and cadence status, coordinates data sharing between skills, and tracks when each task was last run.

**Think of it as:** A PPC manager who delegates tasks to specialists and keeps the operating rhythm on track.

---

## BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/ppc-agent/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## Step 1: Read Agent State + Portfolio Trackers

Read `outputs/research/ppc-agent/state/agent-state.json` to understand what has been run recently.

If the file doesn't exist, create it with empty dates (everything is "never run" — first-time setup).

**State file structure:**
```json
{
  "last_daily_health": null,
  "last_search_harvest": null,
  "last_bid_review": null,
  "last_portfolio_summary": null,
  "last_weekly_analysis": null,
  "last_monthly_review": null,
  "last_rank_optimizer": null,
  "last_tacos_optimizer": null,
  "last_negative_generation": {},
  "portfolio_index": {
    "{portfolio-slug}": {
      "name": "Portfolio Name",
      "id": "portfolio_id",
      "tracker": "state/{slug}.json",
      "stage": "Scaling/Launch/General",
      "last_deep_dive": "YYYY-MM-DD",
      "last_updated": "YYYY-MM-DD",
      "health_status": "GREEN/YELLOW/RED",
      "trend": "improving/stable/declining/unknown",
      "acos": 30.0,
      "pending_count": 0,
      "top_action": "[P1] Brief description of most urgent pending action",
      "next_review": "YYYY-MM-DD"
    }
  },
  "all_pending_actions": [
    {"portfolio": "Name", "id": "ff-001", "priority": "P1", "category": "BID_DECREASE", "action": "Brief description", "created": "YYYY-MM-DD"}
  ],
  "upcoming_reviews": [
    {"date": "YYYY-MM-DD", "portfolio": "Name", "type": "7-day re-check", "source": "skill-run-date"}
  ],
  "global_pending_actions": [],
  "applied_changes": []
}
```

**The state file is the single source of truth for quick decisions.** Any skill can read agent-state.json and immediately know:
- Which portfolios need attention (`health_status`, `top_action`)
- What's overdue (`upcoming_reviews`, cadence timestamps)
- All pending work across all portfolios (`all_pending_actions`)
- Portfolio trends (`trend`, `acos`)

**No skill should need to read all 15 tracker files for routing or overview purposes.** Only open a specific tracker when working on that portfolio.

### Surfaced Data (maintained by every sub-skill)

| Field | What it surfaces | Updated by |
|-------|-----------------|------------|
| `portfolio_index.{slug}.acos` | Latest ACoS from tracker's `latest_metrics` | Daily health, portfolio summary, deep dive |
| `portfolio_index.{slug}.tacos` | Latest TACoS from TACoS optimizer | TACoS optimizer |
| `portfolio_index.{slug}.tacos_target` | Portfolio TACoS goal | TACoS optimizer |
| `portfolio_index.{slug}.tacos_grade` | TACoS grade (A-F) | TACoS optimizer |
| `portfolio_index.{slug}.organic_momentum` | Organic momentum score (0-100) | TACoS optimizer |
| `portfolio_index.{slug}.trend` | From tracker's `improvement_assessment.overall_trend` | Deep dive, significant metric shifts |
| `portfolio_index.{slug}.top_action` | Highest-priority pending action description | Any skill that adds/completes pending actions |
| `portfolio_index.{slug}.health_status` | Traffic light from last health check | Daily health, deep dive |
| `all_pending_actions` | **All** pending actions from all portfolio trackers, sorted by priority | Any skill that adds/completes pending actions |
| `upcoming_reviews` | **All** scheduled reviews from all portfolio trackers, sorted by date | Deep dive, bid recommender, search term harvester |

**When a sub-skill modifies a portfolio tracker's `pending_actions` or `scheduled_reviews`, it MUST also update `all_pending_actions` and `upcoming_reviews` in agent-state.json to keep them in sync.**

### Portfolio Tracker System (deep context)

Each portfolio has a dedicated tracker file at `outputs/research/ppc-agent/state/{slug}.json` containing full detail:
- **goals** — ACoS/CVR targets, rank targets, strategic notes
- **baseline** — write-once metrics snapshot from before agent started changes
- **latest_metrics** — most recent snapshot + delta vs baseline
- **metric_history** — time-series for trend tracking (max 90 entries)
- **change_log** — every API change made to this portfolio
- **pending_actions** — queued work with priority and due dates (source of truth, surfaced to agent-state)
- **scheduled_reviews** — upcoming re-check dates (source of truth, surfaced to agent-state)
- **skills_run** — log of skill executions
- **improvement_assessment** — is this portfolio improving?

When routing to a sub-skill, pass the portfolio tracker path so the sub-skill can read/write it directly.

---

## Step 2: Route Based on User Intent

### Routing Table

| User says | Route to | Skill location |
|-----------|----------|----------------|
| "ppc morning" / "daily ppc" / "ppc health" | **Daily PPC Health Check** | `.claude/skills/ppc-daily-health/SKILL.md` |
| "adjust bids" / "bid recommendations" / "bid review" | **Bid Adjustment Recommender** | `.claude/skills/ppc-bid-recommender/SKILL.md` |
| "portfolio check" / "portfolio health" / "portfolio flags" | **Portfolio Performance Summary** | `.claude/skills/ppc-portfolio-summary/SKILL.md` |
| "harvest search terms" / "negate and promote" / "search term review" | **Search Term Harvester** | `.claude/skills/ppc-search-term-harvester/SKILL.md` |
| "monthly ppc" / "monthly review" / "ppc month" | **Monthly PPC Review** | `.claude/skills/ppc-monthly-review/SKILL.md` |
| "weekly ppc" / "ppc analysis" / "weekly review" | **Weekly PPC Analysis** (standalone) | `.claude/skills/weekly-ppc-analysis/SKILL.md` |
| "negative keywords" / "generate negatives" | **Negative Keyword Generator** (standalone) | `.claude/skills/negative-keyword-generator/SKILL.md` |
| "rank optimizer" / "rank vs spend" / "keyword rank analysis" / "ppc rank check" | **Keyword Rank Optimizer** | `.claude/skills/keyword-rank-optimizer/SKILL.md` |
| "create campaigns" / "campaign creator" / "build campaigns" / "new campaigns" | **PPC Campaign Creator** | `.claude/skills/ppc-campaign-creator/SKILL.md` |
| "portfolio deep dive" / "deep dive {name}" / "portfolio action plan" / "fix {portfolio}" / "work on {portfolio}" | **Portfolio Action Plan** | `.claude/skills/ppc-portfolio-action-plan/SKILL.md` |
| "deal prep" / "deal ppc" / "prep for deal" | **Deal Coordination** (Bid Recommender — deal mode) | `.claude/skills/ppc-bid-recommender/SKILL.md` |
| "tacos check" / "tacos optimizer" / "profit check" / "tacos scorecard" / "profit reality" | **TACoS & Profit Optimizer** | `.claude/skills/ppc-tacos-optimizer/SKILL.md` |
| "ppc trends" / "ppc dashboard" / "trend check" / "trajectory" / "time series" / "30 day trend" / "inflection points" | **Weekly PPC Analysis** (includes trajectories) | `.claude/skills/weekly-ppc-analysis/SKILL.md` |
| "post deal" / "deal ended" / "deal cleanup" | **Deal Cleanup** (Bid Recommender — post-deal mode) | `.claude/skills/ppc-bid-recommender/SKILL.md` |
| "ppc" / "ppc check" / "ppc status" (ambiguous) | **Cadence Checker** (Step 3) | This skill |
| "ppc catch-up" / "ppc everything" | **Run All Overdue** (Step 4) | This skill |

### How to Route

1. **Read the target skill's LESSONS.md** first (mandatory per operating principles)
2. **Read the target skill's SKILL.md** for instructions
3. **Follow those instructions** step by step
4. **After completion:** Update `agent-state.json` (Step 5)
5. **After completion:** Update this skill's `LESSONS.md` (Step 6)

### Passing Shared Data

When routing to a sub-skill, check if upstream data already exists to avoid redundant API calls:

| Sub-skill needs | Check for | If found, pass the file path |
|----------------|-----------|------------------------------|
| Seller Board data | `outputs/research/market-intel/snapshots/{today}*.json` | Daily health check reads this instead of re-fetching |
| Campaign report | `outputs/research/ppc-weekly/snapshots/{recent}/campaign-report.json` | Bid recommender reads this if <3 days old |
| Search term report | `outputs/research/ppc-weekly/snapshots/{recent}/search-term-report.json` | Search term harvester reads this if <3 days old |
| Applied negatives | `outputs/research/negative-keywords/data/*-applied-*.json` | Search term harvester dedup check |
| Weekly summary | `outputs/research/ppc-weekly/snapshots/{recent}/summary.json` | Portfolio summary + bid recommender + monthly review |
| Targeting report | `outputs/research/ppc-weekly/snapshots/{recent}/targeting-report.json` | Keyword rank optimizer reads this instead of pulling fresh sp_keywords |
| Rank radar snapshot | `outputs/research/ppc-agent/rank-optimizer/snapshots/{recent}/rank-radar-snapshot.json` | Bid recommender + search term harvester for rank context |
| Rank-spend matrix | `outputs/research/ppc-agent/rank-optimizer/snapshots/{recent}/rank-spend-matrix.json` | Bid recommender for keyword waste signals |
| TACoS snapshot | `outputs/research/ppc-agent/tacos-optimizer/snapshots/{recent}/*-tacos-snapshot.json` | Bid recommender for profit-aware bid decisions; monthly review for TACoS trends |
| Campaign creation log | `outputs/research/ppc-agent/campaign-creator/{recent}/*-creation-log.json` | Avoids re-reading upstream sources for campaign creator |
| Trajectory data | Weekly snapshot history at `outputs/research/ppc-weekly/snapshots/*/summary.json` | Monthly review + any skill needing trajectory context (calculated in weekly analysis Step 13b) |

**Key principle:** Never re-fetch data that a recent skill run already has on disk.

---

## Step 3: Cadence Checker (for ambiguous "ppc" requests)

When the user says just "ppc" or "ppc check" without a specific task:

1. Read `agent-state.json`
2. Calculate what's overdue based on these cadences:

| Task | Cadence | Overdue if last run was... |
|------|---------|---------------------------|
| Daily Health Check | Daily | >1 day ago |
| Search Term Harvest | Every 2-3 days | >3 days ago |
| Bid Review | Every 2-3 days | >3 days ago |
| Portfolio Summary | Every 2-3 days | >3 days ago |
| Weekly Analysis | Weekly | >7 days ago |
| Keyword Rank Optimizer | Weekly (after weekly) | >7 days ago |
| TACoS & Profit Optimizer | Weekly (after weekly) | >7 days ago |
| Monthly Review | Monthly | >30 days ago |

**Non-cadence tasks (run on demand):**
- Campaign Creator: triggered by pending PROMOTE/REDIRECT/structure-gap actions (not time-based)

3. Present the cadence status to the user:

```
**PPC Cadence Status**

| Task | Last Run | Status |
|------|----------|--------|
| Daily Health Check | {date or "Never"} | OK / OVERDUE |
| Search Term Harvest | {date or "Never"} | OK / OVERDUE |
| Bid Review | {date or "Never"} | OK / OVERDUE |
| Portfolio Summary | {date or "Never"} | OK / OVERDUE |
| Weekly Analysis | {date or "Never"} | OK / OVERDUE |
| Keyword Rank Optimizer | {date or "Never"} | OK / OVERDUE |
| Monthly Review | {date or "Never"} | OK / OVERDUE |

**Recommendation:** {most overdue task} is {N} days overdue. Run it now?

**Overdue alerts:** If any skill is >3 days overdue, also read `.claude/skills/notification-hub/SKILL.md` → "Recipe: ppc-agent-cadence" and post an overdue alert to Slack.
```

4. **Show portfolio health from `portfolio_index`:**

```
**Portfolio Health Overview**

| Portfolio | Status | Pending | Next Review | Last Updated |
|-----------|--------|---------|-------------|--------------|
| {name} | GREEN/YELLOW/RED | {N} actions | {date or "—"} | {date} |
```

For any portfolio with `pending_count > 0`, load its tracker file and list the top pending actions:
```
**Portfolios with Pending Work ({count})**
- {Portfolio Name}: {pending_count} actions — top: "{highest priority action}" (P1, from {source})
```

5. **Also show global pending actions** if any exist from previous runs:

```
**Global Pending Actions ({count})**
- [P1] {action description} (from {source skill}, {date})
- [P2] {action description}
```

6. Wait for user to choose which task to run, then route to that skill.

---

## Step 4: Run All Overdue (for "ppc catch-up")

When the user says "ppc catch-up" or "ppc everything":

1. Run the cadence checker (Step 3)
2. List all overdue tasks in priority order:
   - **P1:** Daily Health Check (fastest, sets context for everything else)
   - **P2:** Search Term Harvest (biggest $ impact — zero-order spend)
   - **P3:** Bid Adjustments (biggest time savings)
   - **P4:** Portfolio Summary (monitoring)
   - **P5:** Weekly Analysis (if overdue)
   - **P5.5:** Keyword Rank Optimizer (after weekly provides fresh data)
   - **P5.6:** TACoS & Profit Optimizer (after weekly, before bid recommender)
   - **P5.7:** Campaign Creator (if pending PROMOTE/REDIRECT/structure-gap actions exist)
   - **P6:** Monthly Review (if overdue)
3. Ask the user: "These tasks are overdue: {list}. Run them all in order, or pick specific ones?"
4. Execute in order, updating `agent-state.json` after each

**Do NOT run all tasks silently.** Present the list, get confirmation, then run sequentially.

---

## Step 5: Update Agent State + Portfolio Trackers (after every sub-skill run)

**CRITICAL — DO NOT SKIP THIS STEP.** After ANY API change (bid, keyword, campaign, negative), you MUST update both agent-state.json AND the affected portfolio tracker JSON files BEFORE presenting results to the user. This is a hard requirement, not optional.

After any sub-skill completes, update **both** `agent-state.json` and affected portfolio tracker(s):

### 5a. Update `agent-state.json`

1. **Update the timestamp** for the task that just ran
2. **Add any new global pending actions** from the sub-skill's output (cross-portfolio items only)
3. **Remove any global pending actions** that were addressed during this run
4. **Log applied changes** to `applied_changes` (only for multi-portfolio changes)

### 5b. Update `portfolio_index` in `agent-state.json`

For each portfolio touched by the sub-skill:

1. **Update `last_updated`** to today's date
2. **Update `health_status`** based on sub-skill output (GREEN/YELLOW/RED)
3. **Update `trend`** — from tracker's `improvement_assessment.overall_trend`
4. **Update `acos`** — from tracker's `latest_metrics.metrics.acos`
5. **Update `pending_count`** — count of pending actions in the portfolio's tracker
6. **Update `top_action`** — `"[{priority}] {description}"` of highest-priority pending action (null if none)
7. **Update `next_review`** — earliest pending review from the portfolio's `scheduled_reviews`
8. **Update `last_deep_dive`** — if the sub-skill was a portfolio action plan

### 5b-2. Sync `all_pending_actions` in `agent-state.json`

**Rebuild from portfolio trackers after any change to pending actions.** This is the aggregated view — every pending action from every portfolio, sorted by priority (P1 first), then by date:

```json
{"portfolio": "Name", "id": "ff-001", "priority": "P1", "category": "BID_DECREASE", "action": "Brief description", "created": "YYYY-MM-DD"}
```

**When adding/completing pending actions in a tracker, also add/remove them from `all_pending_actions`.**

### 5b-3. Sync `upcoming_reviews` in `agent-state.json`

**Rebuild from portfolio trackers after any change to scheduled reviews.** Sorted by date (soonest first):

```json
{"date": "YYYY-MM-DD", "portfolio": "Name", "type": "7-day re-check", "source": "skill-run-date"}
```

### 5c. Update Portfolio Tracker Files

For each affected portfolio, update its tracker at `outputs/research/ppc-agent/state/{slug}.json`:

1. **`skills_run`** — append entry: `{"skill": "{skill-name}", "date": "{today}", "result": "success/partial/failed", "key_metrics": {}}`
2. **`change_log`** — append any API changes made (bid changes, negatives, campaigns created)
3. **`pending_actions`** — add new P1/P2 items, mark completed items
4. **`latest_metrics`** — update if the sub-skill produced fresh metrics
5. **`metric_history`** — append new entry if `latest_metrics` was updated (max 90 entries)
6. **`scheduled_reviews`** — add if sub-skill recommends a re-check date
7. **`improvement_assessment`** — update if enough history exists (compare `latest_metrics` vs `baseline`)

**Key principle:** Portfolio-specific data goes in the portfolio tracker. Only global/cross-portfolio data stays in `agent-state.json`.

---

## Step 6: Update Lessons (MANDATORY — after every run)

**Before presenting final results, update `.claude/skills/ppc-agent/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Task routed:** {which sub-skill was executed}
**Result:** Success / Partial / Failed

**What happened:**
- (What went according to plan)

**What didn't work:**
- (Any issues)

**Lesson learned:**
- (What to do differently)

**Tokens/cost:** ~XX K tokens
```

### 2. Update Issue Tracking

| Situation | Action |
|-----------|--------|
| New problem | Add to **Known Issues** |
| Known Issue happened again | Move to **Repeat Errors**, increment count, **tell the user** |
| Fixed a Known Issue | Move to **Resolved Issues** |

---

## Global PPC Operating Rules

**These rules apply to ALL PPC sub-skills and must NEVER be violated:**

1. **Never pause a campaign based on a single week of zero conversions.** Always check a longer timeframe (minimum 30 days, ideally 60 days) before recommending a pause. A campaign with zero orders in one week might just be in a rough patch. Only recommend pausing if the campaign shows sustained poor performance over the longer timeframe.
2. **Never use round/organized bid amounts.** When lowering or placing bids, never use clean percentages like -30%, -50%. Always use slightly irregular amounts like -31%, -48%, -52%, -27%. This avoids predictable bid patterns and helps stand out in Amazon's auction dynamics.
3. **Never negate a search term based on a single week of zero conversions.** Always check a minimum 30-day window of data before recommending a search term for negation. A search term with zero orders in one week might convert in other weeks. Only recommend negating if the search term shows sustained zero conversions AND is clearly irrelevant to the product over the full 30-day window.

**Enforce these rules when routing to any sub-skill.** If a sub-skill output contains round bid amounts, single-week pause recommendations, or single-week negation recommendations, flag it before presenting to the user.

---

## SOP Reference (Quick Access)

The PPC Agent must know these SOP decision frameworks to properly route and contextualize:

### Portfolio Stages (from `context/business.md`)

| Phase | ACoS Target | Primary KPI | Bid Flexibility |
|-------|------------|-------------|-----------------|
| **Launch** | Flexible (up to 60%+) | Rank velocity | High — spending to gain position |
| **Scaling** | 28-32% | ACoS + Rank retention | Medium — efficiency matters |
| **General** | N/A | Account-wide utility | Varies |

### Red Flag Thresholds

| Metric | Red Flag | Action |
|--------|----------|--------|
| ACoS >50% (Scaling portfolio) | Bleeding spend | Route to Bid Recommender |
| CVR <5% | Listing or targeting issue | Flag — may need listing review, not PPC fix |
| Hero keyword drops 5+ positions | Competitor attack or algo change | Route to Bid Recommender (increase TOS) |
| 50+ clicks, 0 orders on a keyword | Dead weight | Route to Search Term Harvester |
| Budget utilization >95% | Starved campaign | Flag in Daily Health Check |
| BSR declining despite increased spend | Market saturation | Flag for strategic review |

### Review Cadence Summary

| Cadence | Time Investment | What Happens |
|---------|----------------|--------------|
| **Daily** | 5 min (automated) | Health check brief — traffic lights per portfolio |
| **Every 2-3 days** | 15-20 min (review + approve) | Search term harvest + bid adjustments |
| **Weekly** | 30-45 min (review) | Comprehensive 4-report analysis with WoW comparison |
| **Monthly** | 60-90 min (strategic) | Trend analysis, stage transitions, budget reallocation |

---

## Error Handling

| Issue | Response |
|-------|----------|
| `agent-state.json` missing | Create it with all null dates (first-time setup) |
| Sub-skill's SKILL.md missing | Tell user: "Skill {name} has not been created yet. Build it first." |
| Sub-skill fails mid-run | Log the failure in agent state, update LESSONS.md, tell user what happened |
| Multiple tasks overdue | Present prioritized list, don't auto-run everything |
| User asks for a PPC task not covered by any skill | Suggest the closest skill or offer to help ad-hoc |
| Upstream snapshot data is stale (>7 days) | Warn user and suggest running the upstream skill first |
