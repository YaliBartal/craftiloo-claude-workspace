---
name: ppc-daily-health
description: Quick daily PPC health check — traffic-light status per portfolio with anomaly detection
triggers:
  - ppc morning
  - daily ppc
  - ppc health
  - morning ppc check
output_location: outputs/research/ppc-agent/daily/
---

# Daily PPC Health Check

**USE WHEN** routed from the PPC Agent via: "ppc morning", "daily ppc", "ppc health"

**This skill is invoked through the PPC Agent orchestrator, not directly.**

---

## BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/ppc-daily-health/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

A **5-minute scan** that tells the PPC worker "everything is normal" or "these 2-3 things need your attention today." This is NOT a deep analysis — it replaces the 20-minute manual Seller Board + Seller Central morning check.

**Time saved:** ~1.5 hrs/week (20 min/day x 5 days, reduced to ~5 min review)

**Token budget:** <30K tokens, <3 minutes execution

---

## Operating Rules

1. **Never recommend pausing a campaign based on a single day or week of zero conversions.** Always flag for further investigation with the Bid Recommender, which checks minimum 30 days (ideally 60 days) of data before recommending a pause. A campaign with zero orders in one period might just be in a rough patch.
2. **Never use round/organized bid amounts in any recommendations.** When suggesting bid adjustments, never use clean percentages like -30%, -50%. Always use slightly irregular amounts like -31%, -48%, -52%, -27%. This avoids predictable bid patterns and helps stand out in Amazon's auction dynamics.
3. **Never recommend negating a search term based on a single week of zero conversions.** Always flag for further investigation with the Search Term Harvester, which checks a minimum 30-day window before recommending negation. A search term with zero orders in one week might convert in other weeks. Only recommend negating if the search term shows sustained zero conversions AND is clearly irrelevant to the product over the full 30-day window.

---

## Efficiency Standards

- **<30K tokens** per run
- **<3 minutes** execution time
- **0 Apify calls** (no scraping needed)
- **Minimal API calls** — read from Market Intel snapshot where possible
- **1 output file** — brief + snapshot in one clean delivery

---

## Process

### Step 1: Load Context + Portfolio Trackers

Load these files (read in parallel where possible):

| File | Purpose |
|------|---------|
| `context/business.md` | Portfolio stages (Launch/Scaling/General) |
| `outputs/research/ppc-agent/agent-state.json` | Last run dates, global pending actions, portfolio_index |
| `outputs/research/ppc-agent/portfolios/*.json` | **All portfolio trackers** — for scheduled reviews, pending actions, improvement trends |
| Most recent `outputs/research/market-intel/snapshots/*.json` | Seller Board data (TACoS, ad spend, margin, organic ratio) |
| Most recent `outputs/research/ppc-agent/daily/*-health-snapshot.json` | Yesterday's health check (for day-over-day comparison) |
| Most recent `outputs/research/ppc-weekly/snapshots/*/summary.json` → `placement` section | Per-campaign placement health classifications (use if <7 days old) |

**From portfolio trackers, extract per portfolio:**
- `scheduled_reviews` — any reviews due today or overdue
- `pending_actions` with `status: "pending"` — count for the brief
- `improvement_assessment` — trend direction for context
- `latest_metrics` — for day-over-day comparison

**If today's Market Intel snapshot exists:** Use it. Do NOT re-fetch Seller Board data.
**If no Market Intel snapshot exists for today:** Note: "No market intel snapshot for today. Running with campaign data only. Consider running /daily-market-intel first for the full picture."

### Step 2: Pull Lightweight Campaign Data

Fetch current campaign status — no full report needed, just the live state:

```
list_sp_campaigns(state="ENABLED", marketplace="US", max_results=200)
```

**Extract per campaign:**
- `campaignName` — for portfolio grouping
- `campaignId` — for reference
- `budget` → `budget.budget` — daily budget
- `state` — should all be ENABLED (we filtered)
- `placementBidding` — current TOS/ROS/PP modifier percentages (for TOS health context)

**Then group campaigns by portfolio:**
```
list_portfolios(marketplace="US")
```

Map each campaign to its portfolio using `portfolioId`. Group campaigns without a portfolio under "Unassigned."

### Step 3: Check DataDive Rank Radar Summary

Fetch summary-level rank radar data (headline counts only — NOT full keyword lists):

```
list_rank_radars()
```

**Extract per radar:**
- `radarLabel` — portfolio/product name
- `totalKeywords` — how many keywords tracked
- `top10Count` — keywords in top 10 organically
- `top50Count` — keywords in top 50

**This is a fast call** — no per-keyword data needed for the daily check.

### Step 4: Build Portfolio Health Summary

For each portfolio, compute a traffic-light status:

#### Data Sources Per Portfolio

**Important:** Seller Board data is per-ASIN, not per-portfolio. Portfolio-level PPC metrics come from campaign data grouped by portfolio.

| Data Point | Source | Calculation |
|-----------|--------|-------------|
| Yesterday's PPC spend | `list_sp_campaigns` grouped by portfolio via `list_portfolios` | Sum of campaign budgets (approximate; actual spend requires reports) |
| 7-day avg portfolio ACoS | Most recent weekly snapshot (`summary.json`) | Spend / Sales per portfolio from campaign report |
| Account-level TACoS | Market Intel snapshot (Seller Board) | Total Ad Spend / Total Revenue (account-level, not portfolio) |
| Account-level organic ratio | Market Intel snapshot (Seller Board) | Organic Revenue / Total Revenue (account-level) |
| Per-ASIN sales/profit | Market Intel snapshot (Seller Board 7d detailed) | Match ASINs to portfolios via `context/business.md` ASIN list |
| Rank radar summary | DataDive `list_rank_radars` | top10/top50 counts per radar |
| Campaign count | `list_sp_campaigns` | Count of ENABLED campaigns in portfolio |
| Portfolio stage | `context/business.md` | Launch / Scaling / General |

**Portfolio-level ACoS** is derived from campaign data (Step 2), not Seller Board.
**Account-level TACoS and organic ratio** come from Seller Board (Market Intel snapshot).
**Per-ASIN profit/margin** from Seller Board is mapped to portfolios using the ASIN list in `context/business.md`.

#### Traffic Light Rules

**GREEN — All good, no action needed:**
- Scaling portfolio: ACoS <35%
- Launch portfolio: ACoS <60% (higher tolerance)
- Spend within 30% of 7-day average
- No hero keyword rank drops (if radar data available)

**YELLOW — Worth noting, monitor:**
- Scaling portfolio: ACoS 35-50%
- Launch portfolio: ACoS 60-80%
- Spend 30-50% above 7-day average
- 1-2 hero keywords dropped out of top 10
- Multiple campaigns in portfolio classified as "TOS BLEEDING" in weekly placement snapshot
- Most campaigns in portfolio have no TOS modifier set (0%) — missing TOS strategy

**RED — Needs attention today:**
- Scaling portfolio: ACoS >50%
- Launch portfolio: ACoS >80%
- Spend >50% above 7-day average (budget blowout)
- 3+ hero keywords dropped out of top 10
- ACoS more than doubled from yesterday
- Majority of campaigns in portfolio classified as "ALL BLEEDING" in weekly placement snapshot (not a bid problem — flag listing/targeting)
- Very high TOS modifier with poor TOS ACoS in weekly snapshot (overpaying for TOS)

#### Stage-Specific Context

Always note the portfolio stage next to its status:
- **Launch** portfolios in YELLOW are often fine — high ACoS is expected
- **Scaling** portfolios in YELLOW need monitoring
- **General** portfolios (Catch All, Shield) have different benchmarks

### Step 5: Check Pending Actions

Read pending actions from **two sources**:

**Portfolio trackers** (primary — portfolio-specific actions):
- For each portfolio, check `pending_actions` with `status: "pending"`
- Summarize: "{Portfolio Name}: {count} pending — top: {highest priority action}"

**`agent-state.json`** (secondary — global/cross-portfolio actions):
- Read `global_pending_actions` for any cross-portfolio P1 items

Also check `scheduled_reviews` in each portfolio tracker — flag any reviews due today or overdue.

List all pending P1 actions + overdue reviews in the brief.

### Step 6: Generate Morning Brief

**Format:**

```markdown
# PPC Morning Brief — {YYYY-MM-DD}

## Account Pulse

| Metric | Yesterday | 7-Day Avg | Trend |
|--------|-----------|-----------|-------|
| Total PPC Spend | ${X} | ${X} | {arrow up/down/flat} |
| Total PPC Sales | ${X} | ${X} | {arrow} |
| Overall ACoS | X% | X% | {arrow} |
| TACoS | X% | X% | {arrow} |
| Organic Ratio | X% | X% | {arrow} |

## Portfolio Status

| Portfolio | Stage | ACoS | Spend | TOS Health | Status | Note |
|-----------|-------|------|-------|------------|--------|------|
| {name} | Scaling | X% | ${X} | Strong | GREEN | — |
| {name} | Launch | X% | ${X} | No Data | YELLOW | ACoS elevated but expected for launch |
| {name} | Scaling | X% | ${X} | Bleeding | RED | TOS bleeding on 3/12 campaigns |

**TOS Health** column: "Strong" (mostly TOS DOMINANT/EFFICIENT), "Bleeding" (multiple TOS BLEEDING campaigns), "Mixed" (mixed classifications), "No Data" (no weekly placement snapshot or >7 days old)

**RED flags ({count}):**
- {Portfolio}: {specific issue and suggested action}
- {Portfolio}: ALL BLEEDING pattern — likely a listing/targeting issue, not a bid problem

**YELLOW flags ({count}):**
- {Portfolio}: {what to monitor}
- {Portfolio}: No TOS modifier set on most campaigns — missing TOS strategy

## Rank Radar Summary

| Radar | Keywords | Top 10 | Top 50 | Note |
|-------|----------|--------|--------|------|
| {name} | {N} | {N} | {N} | {stable / gained / lost} |

## Pending Actions ({count})

| Priority | Action | Source | Date |
|----------|--------|--------|------|
| P1 | {description} | {skill name} | {date} |

## Today's Recommendation

{One sentence: what the PPC worker should focus on today based on the status above.}
{If everything is GREEN: "All portfolios healthy. Good day for proactive work — consider running a search term harvest or reviewing bid recommendations."}
{If RED flags exist: "Priority: Address {portfolio} — {specific action}. Then {secondary recommendation}."}
```

### Step 7: Save Outputs + Update Portfolio Trackers

**Brief:**
`outputs/research/ppc-agent/daily/{YYYY-MM-DD}-health-check.md`

**Snapshot (machine-readable for other skills):**
`outputs/research/ppc-agent/daily/{YYYY-MM-DD}-health-snapshot.json`

**Portfolio tracker updates** — for each portfolio touched, update its tracker at `outputs/research/ppc-agent/portfolios/{slug}.json`:

1. **`latest_metrics`** — update with today's health check data (spend, ACoS from campaign grouping, campaign_count)
2. **`metric_history`** — append entry (max 90)
3. **`skills_run`** — append: `{"skill": "ppc-daily-health", "date": "YYYY-MM-DD", "result": "success", "key_metrics": {"status": "GREEN/YELLOW/RED", "acos": X}}`

**`agent-state.json` update:**
- Update `portfolio_index.{slug}.health_status` for each portfolio based on today's traffic light
- Update `portfolio_index.{slug}.last_updated` to today

```json
{
  "date": "YYYY-MM-DD",
  "account": {
    "total_spend": 0,
    "total_sales": 0,
    "acos": 0,
    "tacos": 0,
    "organic_ratio": 0
  },
  "portfolios": [
    {
      "name": "Portfolio Name",
      "stage": "Scaling",
      "acos": 0,
      "spend": 0,
      "status": "GREEN",
      "tos_health": "Strong",
      "avg_tos_modifier": 0,
      "campaign_count": 0,
      "note": ""
    }
  ],
  "rank_radar_summary": [
    {
      "radar": "Radar Name",
      "total_keywords": 0,
      "top10": 0,
      "top50": 0
    }
  ],
  "red_flags": [],
  "yellow_flags": [],
  "pending_actions_count": 0
}
```

---

## What This Does NOT Do

- **Does NOT pull full Ads API reports** — that's the Weekly PPC Analysis
- **Does NOT make bid adjustments** — that's the Bid Recommender
- **Does NOT analyze search terms** — that's the Search Term Harvester
- **Does NOT re-fetch Seller Board data** — reads from Market Intel snapshot
- **Does NOT do deep keyword rank analysis** — uses radar summary counts only

If the daily check surfaces a RED flag, tell the user which sub-skill to run next (e.g., "Run bid review for Dessert Family" or "Run search term harvest — 4 days overdue").

---

## Error Handling

| Issue | Response |
|-------|----------|
| No Market Intel snapshot for today | Note it in the brief, run with campaign data only |
| `list_sp_campaigns` returns <50 campaigns | Known truncation issue — note in brief that campaign count may be incomplete |
| `list_rank_radars` fails | Skip rank radar section, note "DataDive unavailable" |
| No previous health snapshot | Skip day-over-day comparison, show absolute values only |
| Portfolio not in `context/business.md` | Default to "Unknown" stage, flag for user to update |
| agent-state.json missing | Create it (first-time setup) |

---

## AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/ppc-daily-health/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
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
