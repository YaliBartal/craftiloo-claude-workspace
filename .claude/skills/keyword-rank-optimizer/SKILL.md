---
name: keyword-rank-optimizer
description: Cross-references PPC spend with organic keyword ranking to find waste, opportunity, and the right keywords to focus on
triggers:
  - rank optimizer
  - rank vs spend
  - keyword rank analysis
  - ppc rank check
  - rank spend analysis
  - are we spending on the right keywords
  - rank investment
output_location: outputs/research/ppc-agent/rank-optimizer/
---

# Keyword Rank Optimizer

**USE WHEN** routed from the PPC Agent via: "rank optimizer", "rank vs spend", "keyword rank analysis", "ppc rank check"

**Also callable standalone** for deep-dive keyword-rank analysis.

---

## BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/keyword-rank-optimizer/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

Cross-references **PPC spend per keyword** with **organic rank movement** to answer: "Are we spending on the right keywords?" Classifies every keyword into one of six action categories, identifies wasted spend, flags keywords where we already rank well enough to reduce PPC, and discovers untapped high-value keywords we should target.

**Cadence:** Weekly (after Weekly PPC Analysis provides fresh targeting data)
**Token budget:** <60K tokens, <6 minutes

---

## Efficiency Standards

- **<60K tokens** per run
- **<6 minutes** execution time
- **Read existing weekly snapshots first** — only pull fresh PPC data if >7 days old
- **Always fetch fresh rank data** (rank is the core purpose of this skill)
- **No Apify calls** — DataDive + Ads API + context files only

---

## Global PPC Operating Rules

**These rules apply to ALL classifications and recommendations:**

1. **Never pause a campaign based on a single week of zero conversions.** Always check minimum 30 days (ideally 60 days) before recommending a pause. A campaign with zero orders in one week might just be in a rough patch.
2. **Never use round/organized bid amounts.** When recommending percentage changes, never use clean numbers like -30%, -50%, +20%. Always use slightly irregular amounts like -31%, -48%, +22%, -27%.

---

## Process

### Step 1: Read Lessons (Mandatory)

Read `.claude/skills/keyword-rank-optimizer/LESSONS.md` and apply all past lessons.

### Step 2: Determine Scope

Check user intent:
- **Portfolio-specific:** User mentions a specific portfolio → analyze only that portfolio's keywords
- **Account-wide:** User says "rank optimizer" without specifying → analyze all portfolios (default)

### Step 3: Load Existing Data

Read in parallel:

| File | Purpose | Required |
|------|---------|----------|
| `context/business.md` | Portfolio stages (Launch/Scaling/General), hero ASINs | Always |
| `context/search-terms.md` | Curated keyword relevance scores (38-100%) per product category | Always |
| Most recent `outputs/research/ppc-weekly/snapshots/*/targeting-report.json` | Keyword-level PPC spend, clicks, orders, ACoS, TOS impression share | Use if <7 days old |
| Most recent `outputs/research/ppc-weekly/snapshots/*/campaign-report.json` | Campaign-to-portfolio mapping, campaign types | Use if <7 days old |
| Most recent `outputs/research/ppc-weekly/snapshots/*/summary.json` | Weekly baseline metrics | Always |
| Most recent `outputs/research/ppc-agent/rank-optimizer/snapshots/*/rank-spend-matrix.json` | Previous run's classifications for delta tracking | If exists |
| Most recent `outputs/research/ppc-agent/rank-optimizer/snapshots/*/rank-radar-snapshot.json` | Previous rank data for cross-week trending | If exists |
| `outputs/research/ppc-agent/state/agent-state.json` | Last run dates | Always |
| `outputs/research/ppc-agent/bids/*-bid-changes-applied.json` | Recent bid changes (correlation: did changes move rank?) | Last 30 days |

**If targeting report is >7 days old or missing:** Pull a fresh keyword report:
```
create_ads_report(report_type="sp_keywords", date_range="LAST_7_DAYS", marketplace="US")
```
Poll and download. This gives per-keyword: `targeting`, `matchType`, `campaignName`, `adGroupName`, `impressions`, `clicks`, `cost`, `purchases7d`, `sales7d`, `topOfSearchImpressionShare`.

### Step 4: Fetch Fresh Rank Data

Rank data MUST be fresh — this is the core purpose of the skill.

1. **Get all active radars:**
   ```
   list_rank_radars()
   ```
   Returns per radar: `rankRadarId`, `asin`, `keywordCount`, `top10KW`, `top50KW`

2. **Match radars to portfolios** using the ASIN field cross-referenced against hero ASINs in `context/business.md`. If scope is portfolio-specific, only fetch radars for that portfolio's ASINs.

3. **Fetch 28-day rank history** for each relevant radar:
   ```
   get_rank_radar_data(rank_radar_id="{id}", start_date="{28 days ago}", end_date="{today}")
   ```
   Returns per keyword: `keyword`, `searchVolume`, and `ranks` array with daily `organicRank` + `impressionRank`.

4. **Extract per keyword:**

   | Field | Calculation |
   |-------|-------------|
   | `organic_rank_current` | `ranks[-1].organicRank` (latest day) |
   | `organic_rank_7d_ago` | `ranks[-7].organicRank` (7 days ago) |
   | `organic_rank_28d_ago` | `ranks[0].organicRank` (start of window) |
   | `rank_change_7d` | `organic_rank_7d_ago - organic_rank_current` (positive = improvement) |
   | `rank_change_28d` | `organic_rank_28d_ago - organic_rank_current` (positive = improvement) |
   | `rank_velocity` | Average daily position change over 28 days |
   | `rank_stability` | Standard deviation of daily organicRank (lower = more stable) |
   | `impression_rank_current` | `ranks[-1].impressionRank` |
   | `rank_trend` | IMPROVING (change ≥+3), STABLE (-2 to +2), DECLINING (change ≤-3) |

### Step 5: Fetch Keyword Universe (Conditional)

**Only fetch if:** the user wants the "untapped opportunities" analysis, or if the portfolio has <50 keywords tracked in Rank Radar.

1. `list_niches()` — get niche IDs matching the portfolio's product category
2. `get_niche_keywords(niche_id="{id}", page_size=200)` — returns full master keyword list with:
   - `keyword`, `searchVolume`, `relevancy` (Core/Related/Outlier), `organicRank`, `sponsoredRank`

3. Filter to keywords with:
   - `relevancy` == "Core" or "Related"
   - `searchVolume` >= 250
   - NOT already in our PPC targeting (will identify in Step 6)

### Step 6: Build the Rank-Spend Matrix

This is the core analysis — joining rank data with PPC spend data.

#### Step 6a: Build PPC Keyword Table

From the `sp_keywords` targeting report, extract for each keyword:

| Field | Source |
|-------|--------|
| `keyword` | `targeting` field |
| `match_type` | `matchType` |
| `campaign_name` | `campaignName` |
| `campaign_type` | From campaign name pattern: "SK" → Single Keyword, "MK" → Multi Keyword, "SPA"/"Auto" → Auto, "Broad" → Broad, "PT" → Product Targeting |
| `portfolio` | Join via `portfolioId` from campaign report |
| `portfolio_stage` | From `context/business.md` |
| `spend_7d` | `cost` |
| `clicks_7d` | `clicks` |
| `orders_7d` | `purchases7d` |
| `sales_7d` | `sales7d` |
| `acos` | `cost / sales7d * 100` (handle division by zero → ∞ if spend > 0 and sales = 0) |
| `cvr` | `purchases7d / clicks * 100` (handle division by zero) |
| `tos_impression_share` | `topOfSearchImpressionShare` |

**Dedup:** If the same keyword appears in multiple campaigns (SK exact + MK broad + Auto), keep each row separately but also compute an **aggregate row** summing spend/clicks/orders across all campaigns for that keyword.

#### Step 6b: Build Rank Table

From Step 4's DataDive data, already structured per keyword with rank metrics.

#### Step 6c: Full Outer Join

Join PPC keyword table with Rank table on `keyword` text (case-insensitive, trimmed).

This produces three sets:

| Set | Meaning | Count |
|-----|---------|-------|
| **Matched** | Both PPC spend AND rank data exist | Core analysis set |
| **PPC-only** | Spending on this keyword but no rank tracking | Blind spot — flag for Rank Radar addition |
| **Rank-only** | Tracking rank but no PPC spend | Potential opportunity or organic-only keyword |

#### Step 6d: Enrich with Keyword Universe

For matched + rank-only keywords, enrich with:

| Field | Source |
|-------|--------|
| `relevance_score` | `context/search-terms.md` (if keyword is listed) |
| `relevancy` | DataDive niche keywords (Core/Related/Outlier, if fetched in Step 5) |
| `keyword_priority_tier` | Computed from SOP priority rules (see below) |

**SOP Keyword Priority Tiers:**

| Tier | Criteria |
|------|----------|
| **Tier 1** | searchVolume > 3,000 AND relevance ≥ 80% |
| **Tier 2** | searchVolume 1,000-3,000 AND relevance ≥ 80% |
| **Tier 3** | searchVolume 250-1,000 AND relevance ≥ 80% AND organic rank 10-50 (close to page 1) |
| **Tier 4** | searchVolume ≥ 250 AND relevance 50-79% |
| **Unranked** | Not in search-terms.md or niche keywords — unknown priority |

### Step 7: Classify Keywords

Apply the six-category classification system. **All thresholds are stage-adjusted.**

#### Stage-Adjusted Thresholds

| Metric | Launch | Scaling | General |
|--------|--------|---------|---------|
| ACoS threshold for WASTING | >60% | >35% | >40% |
| Rank stagnation window | 28 days (4 weeks) | 14 days (2 weeks) | 21 days (3 weeks) |
| Min spend for WASTING flag | $25/week | $15/week | $20/week |
| Rank drop threshold for PROTECT | 8+ positions | 5+ positions | 5+ positions |

#### Category 1: WASTING MONEY

**Keywords where we spend heavily but rank isn't moving.**

All conditions must be true:
- `spend_7d` ≥ stage min spend threshold ($15-25/week)
- `rank_change_28d` ≤ 2 (rank flat or worse over 28 days)
- `rank_change_7d` ≤ 0 (not improving this week either)
- `acos` > stage ACoS threshold
- Portfolio stage is Scaling or General (Launch gets more tolerance unless spend is extreme)

**For Launch portfolios:** Only classify as WASTING if spend > $25/week AND rank_change_28d ≤ 0 AND acos > 60%. Launch expects high ACoS but still needs rank movement.

**TOS context:** If `tos_impression_share` is very low on a WASTING keyword, the campaign may not be reaching TOS at all. Sub-flag: "Low TOS IS — check if TOS modifier is set on this campaign. The spend may be going to low-converting ROS/PP placements."

**Action:** Decrease bids -22-31%, or redirect budget to higher-priority keywords. If low TOS IS is the issue, the problem may be a missing/low TOS modifier rather than the bid itself — recommend checking placement health.

#### Category 2: REDUCE SPEND

**Keywords where we already rank well organically — PPC is redundant.**

Conditions:
- `organic_rank_current` ≤ 10 (top 10 organic)
- Rank stable or improving (not declining)
- `spend_7d` > $5 (still spending meaningfully)

**Sub-classifications:**
| Organic Rank | Rank Trend | Action |
|-------------|------------|--------|
| 1-5 | Stable/Improving | REDUCE -16-22% (strong position, minimal PPC needed) |
| 6-10 | Stable | REDUCE -11-16% (good position, light PPC support) |
| 6-10 | Improving | HOLD — still climbing, don't cut yet |
| 1-5 | Declining | DON'T REDUCE — investigate why rank is slipping despite top position |

**TOS context:** If `tos_impression_share` is very high AND organic rank is strong (1-5), the keyword is dominating both organic and paid TOS. This is a stronger signal for reduction — we're paying for visibility we already have organically.

**Action:** Lower TOS modifier per SOP. Redirect savings to PROTECT/REDIRECT keywords.

#### Category 3: PROTECT

**Hero keywords where rank is dropping — needs immediate attention.**

Conditions (any one triggers PROTECT):
- `rank_change_7d` ≤ -5 (dropped 5+ positions this week, or 8+ for Launch)
- Keyword is in `context/search-terms.md` with relevance ≥ 80%
- Keyword is a hero keyword for the portfolio

**TOS context:** If `tos_impression_share` is low on a PROTECT keyword, we may not be competing for TOS at all. Recommend increasing TOS modifier specifically (not default bid) — per the TOS-First Philosophy, TOS is where conversions happen and where rank defense matters most.

**Action:** Increase TOS modifier +26% or create dedicated SK campaign (per SOP hero keyword defense rule).

#### Category 4: MAINTAIN

**Keywords where the PPC-rank relationship is healthy.**

Conditions (any one qualifies):
- `acos` ≤ portfolio ACoS target AND `rank_trend` == IMPROVING
- `acos` ≤ 25% AND `rank_trend` == STABLE AND organic_rank ≤ 20
- Launch stage AND `rank_trend` == IMPROVING (any ACoS acceptable)

**Action:** Hold. Log for trending.

#### Category 5: REDIRECT

**High-value keywords we're NOT targeting in PPC (or spending <$3/week).**

Source: DataDive niche keywords (Step 5) + `context/search-terms.md` keywords not found in PPC targeting.

Conditions:
- `keyword_priority_tier` is Tier 1 or Tier 2
- Either: no PPC campaign targets this keyword, OR `spend_7d` < $3
- `organic_rank_current` > 20 (not already ranking well organically)

**Priority within REDIRECT:**
| Priority | Criteria |
|----------|----------|
| **High** | Tier 1 keyword + organic rank 10-30 (close to page 1, PPC push could tip it) |
| **Medium** | Tier 2 keyword + organic rank 10-50 |
| **Low** | Tier 1-2 keyword + organic rank > 50 or unranked (longer road) |

**Action:** Create new SK/MK campaigns with TOS-heavy starting setup per TOS-First Philosophy (high TOS modifier, conservative default bid, LEGACY_FOR_SALES bidding strategy). Provide recommended campaign name (per SOP naming convention), starting bid (from `get_sp_bid_recommendations` if available), and suggested daily budget.

#### Category 6: MONITOR

**Insufficient data to classify.**

Conditions:
- Less than 7 days of rank data
- Less than $5 spend in the period
- New keyword just added to Rank Radar

**Action:** Log. Revisit in next run.

### Step 8: Compute Reallocation Plan

For every dollar identified in WASTING MONEY or REDUCE SPEND, propose where to redirect it:

1. **First priority:** PROTECT keywords (defend hero keyword positions)
2. **Second priority:** REDIRECT keywords (untapped high-value opportunities)
3. **Third priority:** MAINTAIN keywords that are budget-starved (efficient but capped)

Present as a simple table:

| From Keyword | Weekly Savings | To Keyword | Recommended Action | Expected Impact |
|-------------|---------------|------------|-------------------|-----------------|
| {wasting kw} -27% | ${X} | {redirect kw} new SK | {SV} monthly searches, Tier 1 |

**Net budget change:** Should be neutral or slightly reduced — this is about reallocation, not spending more.

### Step 9: Compare Against Previous Run

If a previous `rank-spend-matrix.json` exists:

1. **Classification changes:** Which keywords changed category? (e.g., MAINTAIN → WASTING)
2. **Efficiency score delta:** Did overall efficiency improve?
3. **Action follow-through:** Were previous recommendations acted on?
   - Check bid changes applied since last run
   - Check if REDIRECT keywords got new campaigns
   - Check if WASTING keywords had bids decreased
4. **Rank correlation with bid changes:** For keywords where bids were changed, did rank move in the expected direction?

### Step 10: Present Report

**Format:**

```markdown
# Keyword Rank Optimizer — {YYYY-MM-DD}

**Scope:** {Portfolio name or "Account-Wide"}
**Data window:** PPC: {date range} | Rank: 28-day trending ({start} to {end})
**Keywords analyzed:** {N} PPC keywords | {N} rank-tracked keywords | {N} matched
**Previous run:** {date or "First run — no baseline comparison"}

---

## Executive Summary

**Spend efficiency score:** {X}% of keyword spend is well-allocated (MAINTAIN + REDUCE categories as % of total spend)
- Wasted spend identified: ${X}/week on {N} keywords with no rank movement
- Savings from organic strength: ${X}/week reducible on {N} keywords already ranking top 10
- Untapped opportunities: {N} high-priority keywords not being targeted
- Rank protection alerts: {N} hero keywords dropping

**Top recommendation:** {single most impactful action}

---

## WASTING MONEY — ${X}/week on {N} keywords

Keywords with high spend but stagnant or declining rank. Redirect this budget.

| # | Keyword | Portfolio | Stage | SV | Spend/wk | ACoS | Rank Now | Rank 28d Ago | 28d Change | Campaign | Action |
|---|---------|-----------|-------|-----|----------|------|----------|-------------|-----------|----------|--------|
| 1 | {kw} | {port} | Scaling | {vol} | ${X} | X% | #{N} | #{N} | 0 | SK exact | Decrease -27% |

**Total wasted:** ${X}/week
**Root cause patterns:** {e.g., "3 of 5 are in the same portfolio — possible listing issue" or "All are high-competition >50K SV keywords — consider refocusing on medium-volume alternatives"}

---

## REDUCE SPEND — ${X}/week savings from {N} keywords

Already ranking top 10 organically — PPC spend is largely redundant.

| # | Keyword | Portfolio | SV | Organic Rank | Rank Trend | Spend/wk | ACoS | TOS IS | Action |
|---|---------|-----------|-----|-------------|------------|----------|------|--------|--------|
| 1 | {kw} | {port} | {vol} | #{N} | Stable | ${X} | X% | X% | Lower TOS -17% |

**Rationale:** Strong organic positions mean most clicks come free. Reduce PPC to a maintenance level.

---

## PROTECT — {N} Hero Keywords Dropping

Urgent: these high-value keywords lost significant rank this week.

| # | Keyword | Portfolio | SV | Rank Now | Rank 7d Ago | Drop | Rank 28d Ago | Spend/wk | Action |
|---|---------|-----------|-----|----------|-------------|------|-------------|----------|--------|
| 1 | {kw} | {port} | {vol} | #{N} | #{N} | -{N} | #{N} | ${X} | Increase TOS +26% |

**Urgency:** Act within 2-3 days — rank drops accelerate without intervention.

---

## REDIRECT — {N} Untapped Opportunities

High-value keywords we're not targeting (or barely targeting) in PPC.

| # | Keyword | SV | Relevance | Priority Tier | Organic Rank | Current PPC Spend | Recommended Action |
|---|---------|-----|-----------|--------------|-------------|-------------------|--------------------|
| 1 | {kw} | {vol} | X% | Tier 1 | #{N} or N/A | $0 | Create SK campaign, starting bid ${X} |

**Potential impact:** {total SV} combined monthly searches at {avg relevance}% relevance.

---

## MAINTAIN — {N} Keywords On Track

Healthy PPC-rank relationship. No changes needed.

| # | Keyword | Portfolio | SV | Rank | 28d Change | Spend/wk | ACoS | Status |
|---|---------|-----------|-----|------|-----------|----------|------|--------|
| 1 | {kw} | {port} | {vol} | #{N} | +{N} | ${X} | X% | Efficient + rank improving |

---

## MONITOR — {N} Keywords (Insufficient Data)

| # | Keyword | Portfolio | Reason | Days of Data | Spend |
|---|---------|-----------|--------|-------------|-------|
| 1 | {kw} | {port} | New keyword | {N} days | ${X} |

---

## 28-Day Rank Trending

Weekly rank snapshots showing trajectory over time.

| Keyword | SV | 28d Ago | 21d Ago | 14d Ago | 7d Ago | Today | Velocity | 28d Spend | Category |
|---------|-----|---------|---------|---------|--------|-------|----------|-----------|----------|
| {kw} | {vol} | #{N} | #{N} | #{N} | #{N} | #{N} | +X/wk | ${X} | MAINTAIN |

---

## Spend Reallocation Recommendation

| From (Reduce/Waste) | Weekly Savings | To (Redirect/Protect) | Recommended Action | Expected Impact |
|---------------------|---------------|----------------------|-------------------|-----------------|
| {kw} decrease -27% | ${X} | {kw} new SK | Tier 1, {SV} monthly SV |

**Net budget change:** ${X}/week ({neutral / slight increase / slight decrease})

---

## Portfolio Efficiency Breakdown

| Portfolio | Stage | Keywords | Wasting | Reduce | Protect | Maintain | Redirect | Efficiency |
|-----------|-------|----------|---------|--------|---------|----------|----------|------------|
| {name} | Scaling | {N} | {N} (${X}) | {N} (${X}) | {N} | {N} | {N} | X% |

---

## PPC-Only Keywords (Blind Spots)

Keywords we spend on but have NO rank tracking in DataDive.

| Keyword | Campaign | Spend/wk | Orders | Note |
|---------|----------|----------|--------|------|
| {kw} | {campaign} | ${X} | {N} | Consider adding to Rank Radar |

---

## vs Previous Run ({date})

| Metric | Previous | Current | Delta |
|--------|----------|---------|-------|
| Efficiency score | X% | X% | +/-X% |
| Keywords wasting | {N} (${X}) | {N} (${X}) | +/-{N} |
| Keywords reduce | {N} | {N} | +/-{N} |
| Keywords protect | {N} | {N} | +/-{N} |
| Total wasted spend/wk | ${X} | ${X} | +/-${X} |

**Classification changes since last run:**
- {keyword} moved from MAINTAIN → WASTING (rank stalled, ACoS increased)
- {keyword} moved from PROTECT → MAINTAIN (rank recovered after TOS increase)

**Bid change correlation:**
- {N} keywords had bids changed since last run
- {N} of those showed rank improvement (X% success rate)
```

### Step 11: User Approval Gate

Present findings and ask:

**"Review the analysis above. Options:**
1. **Generate bid recommendations** — I'll create a targeted bid change list for the Bid Recommender
2. **Prepare REDIRECT campaign specs** — I'll outline new campaign creation for untapped keywords
3. **Save for reference only** — no action, strategic insight only
4. **Modify classifications** — adjust any keywords before acting"

**This skill is analysis-only.** It does NOT apply bid changes or create campaigns directly:
- Bid changes → routed to **Bid Recommender**
- Campaign creation → provided as specs for **manual creation** by the user

### Step 12: Save Outputs

**Brief:**
`outputs/research/ppc-agent/rank-optimizer/briefs/{YYYY-MM-DD}-rank-optimizer.md`

**Rank-Spend Matrix (machine-readable):**
`outputs/research/ppc-agent/rank-optimizer/snapshots/{YYYY-MM-DD}/rank-spend-matrix.json`

```json
{
  "date": "YYYY-MM-DD",
  "scope": "account-wide",
  "ppc_data_window": "LAST_7_DAYS",
  "rank_data_window": "28 days",
  "previous_run": "YYYY-MM-DD",
  "efficiency_score": 0,
  "keywords": [
    {
      "keyword": "embroidery kit for kids",
      "portfolio": "Embroidery for Kids",
      "portfolio_stage": "Scaling",
      "campaign_name": "embroidery SK exact",
      "campaign_type": "SK",
      "match_type": "EXACT",
      "search_volume": 13067,
      "relevance_score": 88,
      "priority_tier": "Tier 1",
      "spend_7d": 15.50,
      "clicks_7d": 18,
      "orders_7d": 1,
      "acos": 72.3,
      "cvr": 5.6,
      "tos_impression_share": 12.3,
      "organic_rank_current": 28,
      "organic_rank_7d_ago": 22,
      "organic_rank_28d_ago": 18,
      "rank_change_7d": -6,
      "rank_change_28d": -10,
      "rank_velocity": -0.36,
      "rank_stability": 4.2,
      "impression_rank_current": 8,
      "rank_trend": "DECLINING",
      "classification": "WASTING_MONEY",
      "action": "Decrease bid -27%",
      "previous_classification": "MAINTAIN",
      "classification_changed": true
    }
  ],
  "ppc_only_keywords": [],
  "rank_only_keywords": [],
  "summary": {
    "total_matched": 0,
    "ppc_only": 0,
    "rank_only": 0,
    "wasting_money": {"count": 0, "weekly_spend": 0},
    "reduce_spend": {"count": 0, "weekly_spend": 0, "savings_potential": 0},
    "protect": {"count": 0},
    "maintain": {"count": 0, "weekly_spend": 0},
    "redirect": {"count": 0, "total_search_volume": 0},
    "monitor": {"count": 0, "weekly_spend": 0}
  },
  "portfolio_efficiency": {},
  "reallocation_plan": []
}
```

**Rank Radar Snapshot (THE KEY GAP FILL — persists rank data for historical trending):**
`outputs/research/ppc-agent/rank-optimizer/snapshots/{YYYY-MM-DD}/rank-radar-snapshot.json`

```json
{
  "date": "YYYY-MM-DD",
  "window_days": 28,
  "radars": [
    {
      "radar_id": "abc123",
      "asin": "B0B1927HCG",
      "portfolio": "Cross Stitch Hero",
      "keyword_count": 38,
      "top_10_count": 36,
      "keywords": [
        {
          "keyword": "kids cross stitch kit",
          "search_volume": 6299,
          "rank_today": 3,
          "rank_7d_ago": 3,
          "rank_14d_ago": 4,
          "rank_28d_ago": 5,
          "velocity": 0.07,
          "stability": 0.8,
          "impression_rank_today": 2,
          "trend": "IMPROVING"
        }
      ]
    }
  ]
}
```

**This snapshot is the critical piece that fills the gap.** Other skills (Bid Recommender, Weekly PPC, Monthly Review, Search Term Harvester) can read this for historical rank context without re-fetching from DataDive.

### Step 13: Update Agent State

Update `outputs/research/ppc-agent/state/agent-state.json` with:
```json
"last_rank_optimizer": "YYYY-MM-DD"
```

### Step 14: Update Lessons (Mandatory)

**Before presenting final results, update `.claude/skills/keyword-rank-optimizer/LESSONS.md`.**

#### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Result:** Success / Partial / Failed

**Scope:** {Portfolio name or Account-wide}
**Keywords analyzed:** {N} matched, {N} PPC-only, {N} rank-only
**Efficiency score:** {X}%
**WASTING identified:** {N} keywords, ${X}/week
**REDUCE identified:** {N} keywords, ${X}/week savings
**PROTECT alerts:** {N} keywords
**REDIRECT opportunities:** {N} keywords
**Reallocation proposed:** ${X}/week from waste → opportunity

**What happened:**
- (What went according to plan)

**What didn't work:**
- (Any issues)

**Lesson learned:**
- (What to do differently)

**Tokens/cost:** ~XX K tokens
```

#### 2. Update Issue Tracking

| Situation | Action |
|-----------|--------|
| New problem | Add to **Known Issues** |
| Known Issue happened again | Move to **Repeat Errors**, increment count, **tell the user** |
| Fixed a Known Issue | Move to **Resolved Issues** |

---

## Error Handling

| Issue | Response |
|-------|----------|
| No weekly targeting report exists | Pull fresh `sp_keywords` report (adds ~3 min) |
| Weekly snapshot >7 days old | Warn user, pull fresh report |
| DataDive rank radar returns empty | Skip that radar, note in output: "No rank data for {portfolio}" |
| `list_rank_radars` fails entirely | Cannot run — rank data is the core purpose. Tell user: "DataDive unavailable. Try again later." |
| Keyword text mismatch between PPC and DataDive | Use case-insensitive, trimmed matching. Log unmatched keywords in PPC-only and Rank-only sets. |
| Portfolio not in `context/business.md` | Default to "Scaling" thresholds (more conservative) |
| No previous rank optimizer snapshot | First run — skip "vs Previous Run" section, show absolute values only |
| `context/search-terms.md` missing | Skip relevance enrichment, note: "Keyword relevance scores unavailable" |
| Niche keywords API fails | Skip REDIRECT analysis, note: "Could not fetch full keyword universe" |
| `list_portfolios` truncated at 50 | Known issue — note some campaigns may be unmapped to portfolios |
