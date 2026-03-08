---
name: ppc-tacos-optimizer
description: TACoS & Profit Optimizer — portfolio-level TACoS scoring, profit reality checks, organic momentum tracking
triggers:
  - tacos check
  - tacos optimizer
  - tacos scorecard
  - profit check
  - profit reality
  - tacos
  - profit
output_location: outputs/research/ppc-agent/tacos-optimizer/
---

# PPC TACoS & Profit Optimizer

**USE WHEN** routed from the PPC Agent via: "tacos check", "tacos optimizer", "profit check", "tacos scorecard", "profit reality"

**This skill is invoked through the PPC Agent orchestrator, not directly.**

---

## BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/ppc-tacos-optimizer/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

A **TACoS-first analysis** that cross-references PPC performance with Seller Board profit data to answer three questions ACoS alone cannot:

1. **Is our PPC investment building organic momentum?** (TACoS trajectory)
2. **Are we actually making money on PPC sales?** (profit reality check)
3. **Which portfolios deserve more/less investment?** (profit-weighted recommendations)

**Key metric: TACoS (Total Advertising Cost of Sales)**
```
TACoS = Ad Spend / Total Revenue (organic + PPC) x 100
```

TACoS is the north star because it captures the full picture — not just ad efficiency (ACoS) but the relationship between ad investment and total business health. A declining TACoS means organic is growing faster than ad spend. That's the goal.

**Cadence:** Weekly (after weekly analysis, before bid recommender)
**Token budget:** <60K tokens, <5 minutes
**API calls:** 5-7 total

**Distinction from existing skills:**

| Existing Skill | Focuses on | This Skill Adds |
|----------------|-----------|-----------------|
| Daily Health | ACoS traffic lights | TACoS traffic lights + profit reality |
| Bid Recommender | ACoS-based bid matrix | Profit-weighted bid priority |
| Portfolio Summary | ACoS + structure audit | TACoS scorecard + organic momentum |
| Monthly Review | ACoS trends over 4 weeks | TACoS trajectory + profit trend |

---

## Operating Rules

1. **Never recommend pausing a campaign based on a single week of zero conversions.** Always check a longer timeframe (minimum 30 days, ideally 60 days) before recommending a pause.
2. **Never use round/organized bid amounts in any recommendations.** Use slightly irregular amounts like -31%, -48%, -52%.
3. **TACoS goals are targets, not hard lines.** Context matters — a Launch portfolio at 45% TACoS with organic momentum building is healthier than a Scaling portfolio at 20% TACoS with organic eroding.
4. **Respect user-set TACoS targets.** If a portfolio tracker already has a `tacos_target`, use it. Only suggest changes — never overwrite without asking.
5. **Note Seller Board data freshness.** SB data typically lags 1-2 days. Always state the data date range in the output.

---

## Efficiency Standards

- **<60K tokens** per run
- **<5 minutes** execution time
- **5-7 API calls** (3 Seller Board + 2 Ads API + 1 DataDive + local files)
- **Summarize Seller Board CSV aggressively** — only extract needed columns, don't dump raw data

---

## Step 1: Load Data Sources (parallel)

Pull three data streams simultaneously:

### Stream A — Seller Board (profit + TACoS data)

```
1. get_sales_detailed_report()
   → Per-ASIN 30d: organic_sales, ppc_sales, total_sales, net_profit, margin_pct, ad_spend, sp_cost, sd_cost, sessions, cvr_pct, refunds

2. get_sales_detailed_7d_report()
   → Same fields but 7d window (for trajectory comparison)

3. get_ppc_marketing_report()
   → Account-level TACoS, ROAS, organic turnover, PPC sales, ad spend (validation)
```

### Stream B — Amazon Ads API (campaign-portfolio mapping)

```
4. list_portfolios(marketplace="US")
   → Portfolio ID → name mapping

5. list_sp_campaigns(state="ENABLED", marketplace="US")
   → Campaign → portfolio assignment
```

**Check first:** If a fresh campaign report exists at `outputs/research/ppc-weekly/snapshots/{recent}/campaign-report.json` (<3 days old), use it instead of pulling fresh.

### Stream C — Context + State (local files, no API cost)

```
6. Read context/business.md → portfolio stages, ASIN-to-portfolio mapping
7. Read outputs/research/ppc-agent/state/agent-state.json → portfolio index
8. Read portfolio tracker JSONs (state/{slug}.json) → existing goals, baselines, metric history
   - Only read the fields you need: portfolio.hero_asins, portfolio.secondary_asins, goals, latest_metrics, metric_history
9. list_rank_radars() → organic rank summary for momentum scoring
```

---

## Step 2: Build ASIN-to-Portfolio Map

**This is the critical bridge.** Seller Board reports per-ASIN. PPC campaigns group by portfolio. This step connects them.

**Sources for mapping (in priority order):**
1. Portfolio tracker `hero_asins[]` and `secondary_asins[]` — most reliable
2. `context/business.md` product listings — backup
3. Campaign product ads (from campaign data) — fallback

**Build the map:**
```
{
  "B09WQSBZY7": {"portfolio": "fairy-family", "role": "hero"},
  "B0BNDVTTSH": {"portfolio": "fairy-family", "role": "secondary"},
  ...
}
```

**Handle gaps:**
- ASINs in Seller Board but not in any portfolio → group as "Unassigned" and flag for user
- Portfolios with no ASINs mapped → note as "No ASIN mapping — TACoS approximate"
- If an ASIN appears in multiple portfolios (rare) → warn about double-counting

---

## Step 3: Compute Per-Portfolio TACoS

For each portfolio, aggregate the mapped ASIN data from Seller Board:

### 30-Day Metrics (from `get_sales_detailed_report`)

```
Portfolio Ad Spend 30d = sum(ad_spend) for all ASINs in portfolio
Portfolio Total Revenue 30d = sum(total_sales) for all ASINs
Portfolio Organic Revenue 30d = sum(organic_sales)
Portfolio PPC Revenue 30d = sum(ppc_sales)
Portfolio Net Profit 30d = sum(net_profit)
Portfolio Margin 30d = Portfolio Net Profit / Portfolio Total Revenue x 100

TACoS 30d = Portfolio Ad Spend / Portfolio Total Revenue x 100
ACoS 30d = Portfolio Ad Spend / Portfolio PPC Revenue x 100
Organic Ratio 30d = Portfolio Organic Revenue / Portfolio Total Revenue x 100
Break-Even ACoS = Portfolio Margin % (if ACoS > this, every PPC sale loses money)
```

### 7-Day Metrics (from `get_sales_detailed_7d_report`)

Same calculations but using 7d data. This gives the recent trajectory.

### Account-Level Validation

Compare your summed portfolio TACoS against the account-level TACoS from `get_ppc_marketing_report()`. They should be close (within 2-3 pts). If they diverge significantly, note it — likely unmapped ASINs or data lag.

---

## Step 4: Determine TACoS Goals per Portfolio

### Stage-Based Defaults

| Stage | Default TACoS Target | Red Flag Threshold | Rationale |
|-------|---------------------|-------------------|-----------|
| **Launch** | 42% | 60% | Heavy PPC investment expected; organic share should be growing |
| **Growth / Late Launch** | 28% | 40% | Organic should carry 40-60% of revenue |
| **Scaling / Efficiency** | 16% | 25% | Organic should carry 60-80% of revenue |
| **General** (Catch All/Shield) | 22% | 30% | Defensive spend, should be efficient |

### Adjustment Factors

Apply these adjustments to the stage default:

| Condition | Adjustment | Reason |
|-----------|-----------|--------|
| Margin >50% | Relax target +5 pts | High margin can absorb more ad spend |
| Margin 35-50% | No adjustment | Standard |
| Margin 25-35% | Tighten target -3 pts | Thinner margin needs more efficiency |
| Margin <25% | Tighten target -5 pts | Must be very efficient |
| Organic ratio >70% | Tighten target -3 pts | Organic is doing the heavy lifting |
| Organic ratio <30% | No adjustment (keep default) | Still PPC-dependent, tightening would be unrealistic |
| Hero keywords gaining rank (from rank radar) | Allow +3 pts tolerance | Investment is paying off in organic gains |
| Hero keywords losing rank | No relaxation | PPC investment not translating to organic |

### User Override

**If a portfolio tracker already has a `tacos_target` field set from a previous run, use it.** Only suggest changes — present them as: _"Current target: X%. Data suggests Y% may be more appropriate because [reason]. Update?"_

### Days-to-Goal Estimate

If TACoS is above target and trajectory is improving:
```
TACoS gap = current TACoS - target TACoS
Weekly improvement rate = (TACoS 30d - TACoS 7d) / ~3 weeks
Days to goal = (TACoS gap / weekly improvement rate) * 7

If improvement rate <= 0: "Not on track — TACoS flat or worsening"
If days > 180: "Long-term target — requires strategic changes"
```

---

## Step 5: TACoS Decomposition (the "WHY")

For each portfolio, explain why TACoS is at its current level and what's driving change.

### Decomposition Formula

```
TACoS change = TACoS_7d - TACoS_30d

Decompose into three components:

1. Ad Spend Effect:
   spend_delta = (ad_spend_7d_annualized - ad_spend_30d) / total_revenue_30d
   → Positive = spend increased, pushing TACoS up
   → Negative = spend decreased, pulling TACoS down

2. Organic Revenue Effect:
   organic_delta = -ad_spend_30d * (organic_rev_7d_annualized - organic_rev_30d) / (total_rev_30d * total_rev_7d_annualized)
   → Positive = organic grew, pulling TACoS down (good)
   → Negative = organic shrank, pushing TACoS up (bad)

3. PPC Revenue Effect:
   ppc_delta = -ad_spend_30d * (ppc_rev_7d_annualized - ppc_rev_30d) / (total_rev_30d * total_rev_7d_annualized)
   → Positive = PPC revenue grew, pulling TACoS down
   → Negative = PPC revenue shrank, pushing TACoS up
```

**Note on annualization:** To compare 7d and 30d fairly, annualize the 7d figures by multiplying by (30/7).

### TACoS Driver Classification

Based on the largest component:

| Classification | When | Signal |
|---------------|------|--------|
| **Organic Growth** | Organic revenue effect is the largest positive driver | TACoS declining because organic is growing. Ideal. |
| **Spend Reduction** | Ad spend effect is the largest positive driver | TACoS declining because we cut spend. May hurt rank long-term. |
| **PPC Efficiency** | PPC revenue effect is the largest positive driver | TACoS declining because PPC converts better. Good but fragile. |
| **Organic Erosion** | Organic revenue effect is the largest negative driver | TACoS rising because organic dropped. Danger — investigate immediately. |
| **Spend Inflation** | Ad spend effect is the largest negative driver | TACoS rising because spend grew faster than revenue. Check for waste. |
| **Mixed** | No single component dominates (all within 2 pts of each other) | Multiple factors at play. Note the direction of each. |

**Present the top 5 movers** (biggest TACoS change, positive or negative) with full decomposition tables.

---

## Step 6: Profit Reality Check

For each ASIN with meaningful PPC spend (>$5 in the 30d period), compute profitability:

### Per-ASIN Metrics

```
From Seller Board 30d:
- Total Sales
- PPC Sales
- Organic Sales
- Ad Spend
- Net Profit (already includes ad spend deduction in SB)
- Margin % = Net Profit / Total Sales x 100

Derived:
- ACoS = Ad Spend / PPC Sales x 100
- Break-Even ACoS = Margin % (the ACoS at which PPC sales generate zero profit)
- Profit per PPC Order = (PPC Revenue per order * Margin%) - (Ad Spend per order)
- Organic Ratio = Organic Sales / Total Sales x 100
```

### ASIN Profit Classification

| Status | Condition | Meaning |
|--------|-----------|---------|
| **PROFITABLE** | ACoS < margin - 10 pts | Healthy profit on PPC sales |
| **MARGINAL** | margin - 10 <= ACoS < margin - 3 | Thin profit, needs monitoring |
| **BREAK-EVEN** | margin - 3 <= ACoS <= margin + 3 | Roughly breaking even on PPC |
| **LOSS-MAKING** | ACoS > margin + 3 AND organic ratio < 60% | Every PPC sale loses money |
| **SUBSIDY** | ACoS > margin + 3 BUT organic ratio >= 60% | PPC investment justified by organic halo effect |

### Portfolio Roll-Up

For each portfolio, calculate:
```
% of ad spend on PROFITABLE ASINs
% of ad spend on MARGINAL ASINs
% of ad spend on BREAK-EVEN ASINs
% of ad spend on LOSS-MAKING ASINs
% of ad spend on SUBSIDY ASINs

Total monthly profit lost to LOSS-MAKING ASINs = sum(negative profit contributions)
```

---

## Step 7: Organic Momentum Score (0-100)

For each portfolio, compute a momentum score that answers: _"Is organic actually growing, or are we just cutting spend?"_

### Scoring Components (25 points each)

**Component 1: Organic Ratio Trend (0-25)**
```
organic_ratio_7d vs organic_ratio_30d
- Improving by 5+ pts: 25
- Improving by 2-5 pts: 20
- Improving by 0-2 pts: 15
- Flat (within 1 pt): 10
- Declining by 0-3 pts: 5
- Declining by 3+ pts: 0
```

**Component 2: Organic Sales Growth (0-25)**
```
organic_sales_7d_annualized vs organic_sales_30d
- Growing 20%+: 25
- Growing 10-20%: 20
- Growing 5-10%: 15
- Flat (+/- 5%): 10
- Declining 5-15%: 5
- Declining 15%+: 0
```

**Component 3: Hero Keyword Ranks (0-25)**
```
From rank radar data (if available):
- Net gaining positions (positive 7d movement): 25
- Stable (net movement within +/- 3): 15
- Net losing positions: 5
- No rank radar data: 12 (neutral — don't penalize missing data)
```

**Component 4: TACoS Driver (0-25)**
```
From Step 5 decomposition:
- Primary driver is Organic Growth: 25
- Primary driver is PPC Efficiency: 15
- Mixed with organic positive: 12
- Primary driver is Spend Reduction: 8
- Primary driver is Spend Inflation: 3
- Primary driver is Organic Erosion: 0
```

### Momentum Classification

| Score | Classification | Meaning |
|-------|---------------|---------|
| 75-100 | **Strong** | Organic carrying more weight, PPC investment paying off |
| 50-74 | **Building** | Positive signals but not yet dominant |
| 25-49 | **Stalled** | Organic not growing, PPC still doing heavy lifting |
| 0-24 | **Eroding** | Organic declining, PPC dependency increasing |

---

## Step 8: Generate Action Recommendations

Organize recommendations by urgency, using profit data to weight priority:

### P1 — Stop the Bleeding

Campaigns/ASINs where:
- ACoS > margin (LOSS-MAKING classification) AND
- TACoS > target by 10+ pts AND
- Organic momentum is Stalled or Eroding

**Action format:**
```
[P1] {Portfolio} — {ASIN/Campaign}: ACoS {X}% on {Y}% margin = losing ${Z}/month.
TACoS {A}% vs {B}% target. Momentum: {classification}.
→ Recommend: {specific action — lower TOS by X%, reduce budget, etc.}
```

### P2 — Optimize TACoS

Portfolios where:
- TACoS > target but margin is healthy (PROFITABLE or MARGINAL)
- Budget reallocation could improve TACoS

**Action format:**
```
[P2] {Portfolio}: TACoS {X}% vs {Y}% target (+{Z} pts gap).
Margin healthy at {M}%. TACoS driver: {classification}.
→ Recommend: Shift ${X}/wk from {low-efficiency campaign} to {high-efficiency campaign}
```

### P3 — Scale Winners

Portfolios/campaigns where:
- ACoS < margin by 20+ pts (PROFITABLE) AND
- Organic momentum is Strong or Building AND
- TACoS at or below target

**Action format:**
```
[P3] {Portfolio}: {M}% margin with {A}% ACoS = ${P} profit headroom.
Momentum: Strong ({score}/100). TACoS {X}% (target {Y}%).
→ Recommend: Increase budget by ${X}/wk on {campaign}. Room to scale.
```

### P4 — Goal Recalibration

Portfolios where TACoS target seems wrong based on current data:
- Target too aggressive (consistently 20+ pts above, even with good momentum)
- Target too lenient (easily beating target, could tighten)
- Stage transition signal (performance suggests portfolio has moved to next stage)

**Action format:**
```
[P4] {Portfolio}: Current TACoS target {X}% may need recalibration.
Current TACoS: {Y}%. Margin: {M}%. Organic ratio: {O}%.
→ Suggest: Adjust target to {Z}% because {reason}
```

---

## Step 9: Present TACoS Scorecard

### Output Brief

Save to: `outputs/research/ppc-agent/tacos-optimizer/{YYYY-MM-DD}-tacos-scorecard.md`

**Brief structure:**

```markdown
# TACoS & Profit Scorecard — {YYYY-MM-DD}

**Data sources:** Seller Board 30d ({date range}) + 7d ({date range}), Campaign Report
**Portfolios analyzed:** {N}

---

## Account Summary

| Metric | 30-Day | 7-Day | Trend | Note |
|--------|--------|-------|-------|------|
| Total Revenue | ${X} | ${X} | {up/down arrow} | |
| Organic Revenue | ${X} ({O}%) | ${X} ({O}%) | {arrow} | |
| PPC Revenue | ${X} ({P}%) | ${X} ({P}%) | {arrow} | |
| Ad Spend | ${X} | ${X} | {arrow} | |
| **TACoS** | **{X}%** | **{X}%** | **{arrow}** | **Target: {Y}%** |
| ACoS | {X}% | {X}% | {arrow} | |
| Net Profit | ${X} | ${X} | {arrow} | |
| Net Margin | {X}% | {X}% | {arrow} | |

---

## TACoS Scorecard

| Portfolio | Stage | TACoS 30d | TACoS 7d | Target | Gap | Trajectory | Days to Goal | Momentum | Grade |
|-----------|-------|-----------|----------|--------|-----|------------|-------------|----------|-------|
| {name} | Scaling | {X}% | {X}% | {Y}% | {+/-Z} pts | Improving | ~{N}d | Strong (82) | A |
| {name} | Launch | {X}% | {X}% | {Y}% | {+/-Z} pts | Flat | -- | Building (55) | C |

**Grading:** A = at/below target | B = within 5 pts | C = 5-10 pts above | D = 10-20 pts above | F = 20+ pts above or worsening

**At target:** {N}/{total} portfolios
**Improving:** {N} | **Flat:** {N} | **Worsening:** {N}

---

## TACoS Decomposition — Top Movers

### {Portfolio Name} — TACoS {X}% -> {Y}% ({+/-Z} pts)

| Component | Change | Impact on TACoS | Direction |
|-----------|--------|----------------|-----------|
| Ad Spend | {+/-$X} | {+/-Y} pts | {Increased/Decreased} |
| Organic Revenue | {+/-$X} | {+/-Y} pts | {Growing/Declining} |
| PPC Revenue | {+/-$X} | {+/-Y} pts | {Growing/Declining} |
| **Net** | | **{+/-Y} pts** | **{Driver classification}** |

(Repeat for top 5 movers)

---

## Profit Reality Check

### Portfolio Profit Map

| Portfolio | Ad Spend 30d | Net Profit 30d | Margin | Break-Even ACoS | Actual ACoS | Profit Health |
|-----------|-------------|----------------|--------|-----------------|-------------|---------------|
| {name} | ${X} | ${X} | {M}% | {B}% | {A}% | PROFITABLE |
| {name} | ${X} | -${X} | {M}% | {B}% | {A}% | LOSS-MAKING |

### ASIN-Level Flags ({count} flagged)

| ASIN | Product | Portfolio | Margin | ACoS | Break-Even | Ad Spend 30d | Monthly Impact | Status |
|------|---------|-----------|--------|------|-----------|-------------|----------------|--------|
| {asin} | {title} | {portfolio} | {M}% | {A}% | {B}% | ${X} | -${Y}/mo | LOSS-MAKING |

**Total monthly profit impact from LOSS-MAKING ASINs:** ${X}

---

## Organic Momentum Scores

| Portfolio | Score | Organic Trend | Organic Sales | Rank Trend | TACoS Driver | Assessment |
|-----------|-------|---------------|---------------|------------|-------------|------------|
| {name} | 82/100 | +5 pts | +15% | Gaining | Organic Growth | Strong |
| {name} | 18/100 | -3 pts | -12% | Dropping | Organic Erosion | Eroding |

---

## Recommendations

### P1 — Stop the Bleeding ({count})

{Formatted P1 recommendations from Step 8}

### P2 — Optimize TACoS ({count})

{Formatted P2 recommendations}

### P3 — Scale Winners ({count})

{Formatted P3 recommendations}

### P4 — Goal Recalibration ({count})

{Formatted P4 recommendations}

---

## Summary

| Metric | Value |
|--------|-------|
| Portfolios at TACoS target | {N}/{total} |
| Monthly profit lost to inefficiency | ${X} |
| Portfolios with Strong organic momentum | {N} |
| Portfolios with Eroding organic | {N} |
| Recommended weekly spend reallocation | ${X} |
```

### Output Snapshot

Save machine-readable data to: `outputs/research/ppc-agent/tacos-optimizer/{YYYY-MM-DD}-tacos-snapshot.json`

Structure:
```json
{
  "date": "YYYY-MM-DD",
  "data_freshness": {
    "seller_board_30d": "date range",
    "seller_board_7d": "date range",
    "campaign_data": "date or source"
  },
  "account_summary": {
    "total_revenue_30d": 0,
    "organic_revenue_30d": 0,
    "ppc_revenue_30d": 0,
    "ad_spend_30d": 0,
    "tacos_30d": 0,
    "tacos_7d": 0,
    "acos_30d": 0,
    "net_profit_30d": 0,
    "margin_30d": 0,
    "organic_ratio_30d": 0
  },
  "portfolios": {
    "{slug}": {
      "tacos_30d": 0,
      "tacos_7d": 0,
      "tacos_target": 0,
      "tacos_gap": 0,
      "tacos_grade": "A",
      "tacos_trajectory": "improving",
      "days_to_goal": null,
      "tacos_driver": "Organic Growth",
      "organic_momentum_score": 82,
      "organic_momentum_class": "Strong",
      "profit_health": "PROFITABLE",
      "margin_pct": 0,
      "break_even_acos": 0,
      "ad_spend_30d": 0,
      "net_profit_30d": 0,
      "total_revenue_30d": 0,
      "organic_revenue_30d": 0,
      "ppc_revenue_30d": 0,
      "organic_ratio_30d": 0,
      "decomposition": {
        "spend_effect": 0,
        "organic_effect": 0,
        "ppc_effect": 0
      }
    }
  },
  "asin_flags": [
    {
      "asin": "B0...",
      "product": "...",
      "portfolio": "...",
      "margin": 0,
      "acos": 0,
      "break_even_acos": 0,
      "ad_spend_30d": 0,
      "monthly_impact": 0,
      "status": "LOSS-MAKING"
    }
  ],
  "recommendations": {
    "p1": [],
    "p2": [],
    "p3": [],
    "p4": []
  }
}
```

---

## Step 10: Update State

### 10a. Update Portfolio Trackers

For each portfolio analyzed, update `outputs/research/ppc-agent/state/{slug}.json`:

**Add to `goals` (if not already present):**
```json
{
  "tacos_target": 16,
  "tacos_red_flag": 25,
  "break_even_acos": 42.5
}
```

**Update `latest_metrics.metrics` (add new fields alongside existing):**
```json
{
  "tacos": 18.3,
  "tacos_30d": 18.3,
  "tacos_7d": 16.1,
  "organic_revenue_30d": 4200,
  "ppc_revenue_30d": 1800,
  "total_revenue_30d": 6000,
  "net_profit_30d": 1250,
  "margin_pct": 20.8,
  "organic_momentum_score": 72,
  "organic_momentum_class": "Building",
  "profit_health": "PROFITABLE",
  "break_even_acos": 20.8
}
```

**Append to `metric_history`:**
```json
{
  "date": "YYYY-MM-DD",
  "source": "tacos-optimizer",
  "tacos": 18.3,
  "tacos_7d": 16.1,
  "organic_momentum": 72,
  "profit_health": "PROFITABLE",
  "margin_pct": 20.8,
  "note": "TACoS declining via organic growth. Momentum building."
}
```

**Append to `skills_run`:**
```json
{
  "skill": "ppc-tacos-optimizer",
  "date": "YYYY-MM-DD",
  "result": "success",
  "key_metrics": {
    "tacos_30d": 18.3,
    "tacos_7d": 16.1,
    "tacos_grade": "B",
    "organic_momentum": 72,
    "profit_health": "PROFITABLE"
  },
  "output_ref": "tacos-optimizer/YYYY-MM-DD-tacos-scorecard.md"
}
```

**Add pending actions** (from P1/P2 recommendations, if any):
```json
{
  "id": "to-001",
  "priority": "P1",
  "category": "PROFIT_BLEEDER",
  "action": "ACoS 53% on 21% margin — losing $X/month",
  "created": "YYYY-MM-DD",
  "source": "tacos-optimizer",
  "status": "pending"
}
```

### 10b. Update `agent-state.json`

**Add timestamp:**
```json
{
  "last_tacos_optimizer": "YYYY-MM-DD"
}
```

**Update each portfolio in `portfolio_index`:**
```json
{
  "{slug}": {
    "...existing fields...",
    "tacos": 18.3,
    "tacos_target": 16,
    "tacos_grade": "B",
    "organic_momentum": 72
  }
}
```

**Sync `all_pending_actions` and `upcoming_reviews`** if any new pending actions or reviews were added.

---

## Step 11: Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/ppc-tacos-optimizer/LESSONS.md`.**

### Write a Run Log Entry

Add at the **TOP** of the Run Log section:

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

### Update Issue Tracking

| Situation | Action |
|-----------|--------|
| New problem | Add to **Known Issues** |
| Known Issue happened again | Move to **Repeat Errors**, increment count, **tell the user** |
| Fixed a Known Issue | Move to **Resolved Issues** |

---

## Step 12: Present Results to User

After all state updates are complete, present to the user:

1. **Account TACoS headline** — "Account TACoS: X% (target Y%, {improving/worsening})"
2. **TACoS Scorecard table** — all portfolios with grades
3. **Top 3 profit flags** — biggest LOSS-MAKING concerns
4. **Top 3 momentum signals** — best and worst organic momentum
5. **Priority actions** — P1 items requiring immediate attention
6. **Link to full brief** — path to the scorecard markdown file

Keep the user-facing summary concise. The full brief has all the detail.

---

## Integration Notes

### Downstream Skills (read TACoS optimizer outputs)

| Skill | What It Should Read | How to Use |
|-------|-------------------|-----------|
| **Bid Recommender** | `break_even_acos` from portfolio tracker goals | When deciding bid changes, campaigns on LOSS-MAKING ASINs get priority for cuts over merely "high ACoS" campaigns |
| **Daily Health** | `tacos`, `tacos_target`, `tacos_grade` from agent-state portfolio_index | Add TACoS column to morning brief portfolio table |
| **Monthly Review** | `metric_history` entries with TACoS fields | Compute TACoS trajectory over the month |
| **Portfolio Action Plan** | `profit_health`, `organic_momentum_score` from portfolio tracker | Weight action plans by profit impact, not just ACoS |
| **Portfolio Summary** | `tacos_grade`, `organic_momentum` from agent-state | Add to portfolio rankings table |

### Shared Data (avoid redundant API calls)

| If this data exists fresh (<3 days) | Skip this API call |
|--------------------------------------|-------------------|
| Market intel snapshot with SB data | SB 7d report (use snapshot instead) |
| Weekly campaign report | Ads API campaign list |
| Rank radar snapshot | DataDive list_rank_radars |

---

## Handling Edge Cases

### General/Catch-All Portfolios
These target many ASINs across the catalog. TACoS is inherently approximate because the ASIN mapping is fuzzy. Flag these portfolios with a note: _"TACoS approximate — portfolio targets multiple product lines"_

### New Portfolios (No History)
If a portfolio tracker has no `metric_history` entries, this is the first TACoS data point. Set the TACoS target based on stage defaults, note _"First measurement — trajectory will be available after next run"_, and skip days-to-goal calculation.

### Missing Seller Board Data for Some ASINs
Some ASINs may not appear in SB reports (new products, very low sales). Note them as _"Insufficient data"_ and exclude from portfolio TACoS calculation. If >50% of a portfolio's ASINs are missing, flag the entire portfolio as _"Data insufficient — TACoS unreliable"_.

### Extremely High or Low TACoS
- TACoS >80%: Almost certainly a Launch product or data issue. Don't panic. Check if organic sales are near zero (expected for new products).
- TACoS <5%: Either organic is dominant (great) or ad spend is negligible (may need more PPC investment to defend rank).
