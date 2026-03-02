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

## Step 1: Read Agent State

Read `outputs/research/ppc-agent/agent-state.json` to understand what has been run recently.

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
  "last_campaign_creator": null,
  "last_negative_generation": {},
  "pending_actions": [],
  "applied_changes": []
}
```

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
| "deal prep" / "deal ppc" / "prep for deal" | **Deal Coordination** (Bid Recommender — deal mode) | `.claude/skills/ppc-bid-recommender/SKILL.md` |
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
| Campaign creation log | `outputs/research/ppc-agent/campaign-creator/{recent}/*-creation-log.json` | Avoids re-reading upstream sources for campaign creator |

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
```

4. **Also show pending actions** if any exist from previous runs:

```
**Pending Actions ({count})**
- [P1] {action description} (from {source skill}, {date})
- [P2] {action description}
```

5. Wait for user to choose which task to run, then route to that skill.

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
   - **P5.7:** Campaign Creator (if pending PROMOTE/REDIRECT/structure-gap actions exist)
   - **P6:** Monthly Review (if overdue)
3. Ask the user: "These tasks are overdue: {list}. Run them all in order, or pick specific ones?"
4. Execute in order, updating `agent-state.json` after each

**Do NOT run all tasks silently.** Present the list, get confirmation, then run sequentially.

---

## Step 5: Update Agent State (after every sub-skill run)

After any sub-skill completes, update `agent-state.json`:

1. **Update the timestamp** for the task that just ran
2. **Add any new pending actions** from the sub-skill's output (P1/P2 action items)
3. **Remove any pending actions** that were addressed during this run
4. **Log applied changes** (bid changes, negatives applied, etc.)

Example update:
```json
{
  "last_daily_health": "2026-03-01",
  "last_search_harvest": "2026-02-27",
  "pending_actions": [
    {"source": "daily-health-2026-03-01", "action": "Dessert Family ACoS at 72% — needs bid review", "priority": "P1", "status": "pending"}
  ]
}
```

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
