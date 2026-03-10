---
name: listing-ab-analyzer
description: Measures actual revenue impact of listing changes by comparing Brand Analytics data before and after a listing edit
triggers:
  - listing ab
  - before after listing
  - measure listing change
  - did that listing change work
  - listing impact
  - ab analysis
output_location: outputs/research/listing-optimizer/ab-tests/
---

# Listing Change Impact Analyzer

**USE WHEN** user says: "listing ab", "before after listing", "measure listing change", "did that listing change work", "listing impact", "ab analysis"

**Standalone skill** — can also be auto-triggered 3 weeks after a listing push (from portfolio tracker `scheduled_reviews`).

---

## BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/listing-ab-analyzer/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

Compares **Brand Analytics SQP/SCP data** from weeks before and after a listing change to quantify the actual revenue impact. Answers: "Did that listing change work, and by how much?"

Currently the workflow is: Listing Optimizer recommends changes → changes get pushed → **nobody measures if they worked.** This skill closes that feedback loop with real Amazon data.

**Cadence:** On-demand, or auto-triggered 3 weeks after a listing push
**Token budget:** <35K tokens, <5 minutes

---

## Efficiency Standards

- **<35K tokens** per run
- **<5 minutes** execution time
- **Prefer BA weekly archive** at `outputs/research/brand-analytics/weekly/*/` over fresh API calls
- **Only pull fresh BA reports** if the archive doesn't cover the needed periods
- **No Apify/DataDive calls** — Brand Analytics + PPC snapshots + context files only

---

## Required Inputs

| Input | Source | Required? |
|-------|--------|-----------|
| **ASIN** | User provides, or auto-detect from portfolio tracker | Yes |
| **Change date** | Portfolio tracker `change_log`, or user provides | Yes |
| **What changed** | Portfolio tracker details, or user describes | Recommended (affects which metrics to focus on) |

If the user doesn't provide these, ask: "Which product (ASIN or name), when was the listing changed, and what was modified (title, bullets, description, images, or backend keywords)?"

---

## Process

### Step 1: Read Lessons (Mandatory)

Read `.claude/skills/listing-ab-analyzer/LESSONS.md` and apply all past lessons.

### Step 2: Identify the Change

**Option A — Auto-detect from portfolio tracker:**

1. Read `context/sku-asin-mapping.json` to resolve ASIN ↔ portfolio
2. Read `outputs/research/ppc-agent/state/{portfolio-slug}.json`
3. Search `change_log` for entries with type containing "listing" or "push"
4. Extract: change date, what was modified, old vs new values (if logged)

**Option B — User provides:**

User gives ASIN + date + what changed. Read `context/sku-asin-mapping.json` to map ASIN to portfolio.

**Validation checks:**
- Change must be at least 7 days ago (need minimum 1 full after-week)
- If <14 days ago, warn: "Only 1 after-week available. Results are preliminary — re-run after {date} for full analysis."
- If multiple listing changes exist within 4 weeks of each other: flag "Multiple changes detected in analysis window — impact attribution may be unreliable."

### Step 3: Determine Before/After Windows

Calculate calendar-aligned weekly windows:

```
Change date: {YYYY-MM-DD}

Transition week: The Sun-Sat week containing the change date (EXCLUDED — noisy data)

Before period:
  Week B2: 2nd full week before the change (Sun-Sat)
  Week B1: 1st full week before the change (Sun-Sat)

After period:
  Week A1: 1st full week after the change (Sun-Sat)
  Week A2: 2nd full week after the change (Sun-Sat)
```

**Example:** Change on Wed Mar 4, 2026
- Transition week: Mar 1-7 (excluded)
- Before: Feb 16-22 (B2) + Feb 23-Mar 1 (B1)
- After: Mar 8-14 (A1) + Mar 15-21 (A2)

**Calculate `periods_back` for each week:** Count how many full Sun-Sat weeks back from today each window is. BA weekly reports use `periods_back` relative to the most recently completed week.

### Step 4: Load Context Data

Read in parallel:

| File | Purpose | Required |
|------|---------|----------|
| `context/sku-asin-mapping.json` | ASIN → portfolio mapping | Always |
| `context/business.md` | Portfolio stage, product details | Always |
| Portfolio tracker JSON for this ASIN's portfolio | Change log details, recent actions | Always |
| `outputs/research/ppc-agent/bids/*-bid-changes-applied.json` | Confounding factor: bid changes in window | Last 60 days |
| `outputs/research/competitor-tracker/snapshots/` | Confounding factor: competitor changes | If exists |

### Step 5: Fetch Before/After Brand Analytics Data

**Priority: Read from BA weekly archive first.**

Check if `outputs/research/brand-analytics/weekly/{date}/` folders exist for the needed weeks. If they do, read the raw SCP and SQP files directly — no API calls needed.

**If archive doesn't cover the periods, pull fresh:**

#### 5a. SCP Reports (ASIN-level funnel)

Pull SCP for each of the 4 weekly periods:

```
create_brand_analytics_report(report_name="scp", period="WEEK", periods_back={N})
```

Poll → download. Filter results to our ASIN. Extract: `impressions`, `clicks`, `cartAdds`, `purchases`, `clickShare`, `conversionShare`.

**Optimization:** If the before/after periods are consecutive (no large gap), you may be able to use a MONTH period instead of 4 separate WEEK calls. But WEEK gives cleaner before/after separation.

#### 5b. SQP Reports (per-keyword funnel)

Pull SQP for each of the 4 weekly periods:

```
create_brand_analytics_report(report_name="sqp", period="WEEK", periods_back={N}, asins="{ASIN}")
```

Poll → download. Extract per keyword: `searchQuery`, `impressions`, `clicks`, `cartAdds`, `purchases`, `clickShare`, `conversionShare`.

**SQP is the high-value report here** — it shows which specific keywords were affected by the listing change.

**If SQP fails for any period:** Fall back to SCP only (ASIN-level, no per-keyword breakdown). Note: "SQP unavailable for {period} — per-keyword impact analysis limited."

#### 5c. Before/After PPC Data

Read from existing weekly PPC snapshots (no fresh API calls):

| File | Purpose |
|------|---------|
| `outputs/research/ppc-weekly/snapshots/{before-date}/summary.json` | PPC metrics before change |
| `outputs/research/ppc-weekly/snapshots/{after-date}/summary.json` | PPC metrics after change |

Filter to campaigns in the ASIN's portfolio. Extract: spend, sales, orders, ACoS, CVR.

If no PPC snapshots exist for the periods: skip PPC correlation layer.

### Step 6: Compute Impact Analysis

Three layers of comparison:

#### Layer 1 — ASIN-Level Funnel (SCP)

Average the 2 before-weeks and 2 after-weeks separately, then compute deltas:

| Metric | Before (avg) | After (avg) | Delta | % Change | Significant? |
|--------|-------------|-------------|-------|----------|-------------|
| Impressions | {N} | {N} | {+/-N} | {%} | {>10% = Yes} |
| Clicks | {N} | {N} | {+/-N} | {%} | |
| CTR | {%} | {%} | {+/- pts} | | {>2 pts = Yes} |
| Cart Adds | {N} | {N} | {+/-N} | {%} | |
| Cart Rate | {%} | {%} | {+/- pts} | | {>2 pts = Yes} |
| Purchases | {N} | {N} | {+/-N} | {%} | |
| Purchase Rate | {%} | {%} | {+/- pts} | | {>2 pts = Yes} |
| Click Share | {%} | {%} | {+/- pts} | | {>2 pts = Yes} |
| Conv Share | {%} | {%} | {+/- pts} | | {>2 pts = Yes} |
| Conv/Click Ratio | {X}x | {X}x | {+/-} | | {>0.2 = Yes} |

**Significance thresholds:**
- Volume metrics (impressions, clicks, purchases): >10% change
- Rate metrics (CTR, cart rate, purchase rate): >2 percentage points
- Share metrics (click share, conv share): >2 percentage points
- Conv/Click Ratio: >0.2 change

**Derived metrics:**
- `ctr` = clicks / impressions × 100
- `cart_rate` = cartAdds / clicks × 100
- `purchase_rate` = purchases / cartAdds × 100
- `conv_click_ratio` = conversionShare / clickShare

#### Layer 2 — Per-Keyword Impact (SQP)

For each keyword that appears in both before and after periods:

| Keyword | SV | Before CTR | After CTR | Before Cart Rate | After Cart Rate | Before Purchase Rate | After Purchase Rate | Impact |
|---------|-----|-----------|-----------|-----------------|-----------------|---------------------|---------------------|--------|

**Focus analysis based on what changed:**

| What Changed | Primary Metrics to Compare | Expected Impact Location |
|-------------|---------------------------|--------------------------|
| **Title** | CTR (title drives click-through) | Impressions may shift if keyword coverage changed; CTR should change |
| **Bullets** | Cart Rate (bullets drive add-to-cart after click) | CTR unchanged; Cart Rate should change |
| **Description** | Purchase Rate (description influences final decision) | CTR + Cart Rate unchanged; Purchase Rate should change |
| **Images** | CTR + Cart Rate (images drive both click and conversion) | Both CTR and Cart Rate should change |
| **Backend keywords** | Impressions for new keywords (backend drives search inclusion) | New keywords appearing; existing keyword metrics unchanged |

**Keyword-level verdicts:**
- **Improved:** Primary metric improved >2 pts
- **Declined:** Primary metric declined >2 pts
- **Neutral:** Change within +/-2 pts

Show top 10 keywords by impressions. Highlight any keyword where the change type should have affected it but didn't (unexpected non-response).

#### Layer 3 — PPC Performance Correlation

If PPC data exists for both periods:

| Metric | Before | After | Delta | Correlation |
|--------|--------|-------|-------|-------------|
| PPC CVR | {%} | {%} | {+/- pts} | Should track SCP purchase rate |
| PPC ACoS | {%} | {%} | {+/- pts} | Should improve if conversion improved |
| PPC Sales | ${X}/wk | ${X}/wk | {%} | Revenue impact from PPC |
| PPC Orders | {N}/wk | {N}/wk | {%} | Volume impact from PPC |

**Cross-validation:** If SCP shows conversion improved but PPC ACoS didn't improve, investigate — possible that PPC is targeting different keywords than the ones the listing change affected.

### Step 7: Confounding Factor Check

Before declaring a verdict, check for factors that could explain the change besides the listing edit:

| Factor | How to Check | Source |
|--------|-------------|--------|
| **PPC bid changes** | Were bids changed in the same period? | `outputs/research/ppc-agent/bids/*-bid-changes-applied.json` |
| **Competitor changes** | Did a competitor enter/exit or change price? | `outputs/research/competitor-tracker/snapshots/` |
| **Seasonality** | Is this a seasonal product with natural volume swings? | `context/business.md` + common sense (e.g., holiday products in Dec) |
| **Stock issues** | Was there an OOS period in either window? | Portfolio tracker or Seller Board data |
| **Multiple listing changes** | Were other changes made to the same ASIN in the window? | Portfolio tracker `change_log` |
| **Campaign structure changes** | Were campaigns created, paused, or restructured? | Portfolio tracker `change_log` |

**For each confounder found, add to the report:**
```
**Confounding factors detected:**
- {factor}: {description} — impact on results: {likely / unlikely / unknown}
```

**Confidence scoring:**
- **High confidence:** No confounders detected, 2 full weeks before + after, >10% metric change
- **Medium confidence:** 1 minor confounder, or only 1 after-week available, or 5-10% metric change
- **Low confidence:** Multiple confounders, or <1 full after-week, or <5% metric change

### Step 8: Calculate Revenue Impact

Estimate the monthly revenue impact of the listing change:

```
weekly_purchase_delta = after_avg_purchases - before_avg_purchases
avg_order_value = (from PPC data: sales / orders, or from Seller Board)
weekly_revenue_delta = weekly_purchase_delta × avg_order_value
monthly_revenue_impact = weekly_revenue_delta × 4.33
annualized_impact = monthly_revenue_impact × 12
```

**Present as:**
- Estimated weekly impact: +/- ${X}/week
- Estimated monthly impact: +/- ${X}/month
- Estimated annual impact: +/- ${X}/year (if trend sustained)

**Caveat:** "Revenue estimates based on Brand Analytics purchase data and average order value. Actual revenue may differ due to order cancellations, returns, and price variations."

### Step 9: Determine Verdict

Based on the analysis, assign one of four verdicts:

| Verdict | Criteria | Recommendation |
|---------|----------|----------------|
| **POSITIVE** | Primary metric improved >10% OR >2 pts AND confidence ≥ Medium | **KEEP** — change produced measurable improvement |
| **NEGATIVE** | Primary metric declined >10% OR >2 pts AND confidence ≥ Medium | **REVERT** — consider rolling back to previous version |
| **NEUTRAL** | Changes within significance thresholds | **KEEP** — no harm done, but no clear benefit either |
| **INCONCLUSIVE** | Confidence = Low, OR after period incomplete, OR multiple confounders | **MONITOR** — re-run after {date} for more data |

**Nuanced verdicts:**
- If some metrics improved and others declined: **ITERATE** — "{area} improved but {other area} declined. Suggest: {next change to try}."
- If the change was to title and CTR improved but cart rate dropped: the title is attracting a different audience. Consider whether the new audience is the right one.

**Downstream suggestion for NEGATIVE/ITERATE verdicts:**
When verdict is NEGATIVE or ITERATE, add to the report: "Suggest running listing-manager in ITERATE mode for {ASIN} to generate a targeted rewrite using both the original audit findings and these AB results."

### Step 10: Generate Report

**Output file:** `outputs/research/listing-optimizer/ab-tests/{ASIN}-{YYYY-MM-DD}-ab-analysis.md`

```markdown
# Listing Change Impact Analysis — {Product Name}

**ASIN:** {ASIN}
**Portfolio:** {portfolio name} ({stage})
**Change date:** {YYYY-MM-DD}
**What changed:** {title / bullets / description / images / backend keywords}
**Before period:** {date range} (2 weeks)
**After period:** {date range} (2 weeks)
**Data source:** Brand Analytics SCP + SQP (first-party Amazon data)

---

## Verdict: {POSITIVE / NEGATIVE / NEUTRAL / INCONCLUSIVE}

**{One-sentence summary of the impact}**

| Metric | Value |
|--------|-------|
| **Estimated monthly impact** | +/- ${X}/month |
| **Confidence** | {High / Medium / Low} |
| **Recommendation** | {KEEP / REVERT / ITERATE / MONITOR} |

---

## ASIN-Level Funnel Comparison (SCP)

| Metric | Before (avg 2 wks) | After (avg 2 wks) | Delta | % Change | Significant? |
|--------|--------------------|--------------------|-------|----------|-------------|
| Impressions | {N} | {N} | {+/-N} | {%} | {Y/N} |
| Clicks | {N} | {N} | {+/-N} | {%} | {Y/N} |
| CTR | {%} | {%} | {+/- pts} | | {Y/N} |
| Cart Adds | {N} | {N} | {+/-N} | {%} | {Y/N} |
| Cart Rate | {%} | {%} | {+/- pts} | | {Y/N} |
| Purchases | {N} | {N} | {+/-N} | {%} | {Y/N} |
| Purchase Rate | {%} | {%} | {+/- pts} | | {Y/N} |
| Click Share | {%} | {%} | {+/- pts} | | {Y/N} |
| Conv Share | {%} | {%} | {+/- pts} | | {Y/N} |
| Conv/Click Ratio | {X}x | {X}x | {+/-} | | {Y/N} |

**Funnel visualization:**
```
Before: Impressions ({N}) → Clicks ({N}, {CTR}%) → Carts ({N}, {CR}%) → Purchases ({N}, {PR}%)
After:  Impressions ({N}) → Clicks ({N}, {CTR}%) → Carts ({N}, {CR}%) → Purchases ({N}, {PR}%)
```

---

## Per-Keyword Impact (SQP)

**Change type ({what changed}) — expected impact on: {primary metric}**

| # | Keyword | SV | Before {metric} | After {metric} | Delta | Impact |
|---|---------|-----|-----------------|----------------|-------|--------|
| 1 | {kw} | {N} | {%} | {%} | {+/- pts} | Improved |
| 2 | {kw} | {N} | {%} | {%} | {+/- pts} | Declined |

**Summary:** {N} keywords improved, {N} declined, {N} neutral

{If backend keyword change:}
**New keyword appearances:**
| Keyword | After Impressions | After Clicks | Note |
|---------|------------------|-------------|------|
| {kw} | {N} | {N} | First time appearing — backend change working |

---

## PPC Performance Correlation

| Metric | Before | After | Delta | Tracks SCP? |
|--------|--------|-------|-------|-------------|
| CVR | {%} | {%} | {+/- pts} | {Yes/No — should match purchase rate} |
| ACoS | {%} | {%} | {+/- pts} | {Yes/No — should improve if conversion up} |
| Sales/wk | ${X} | ${X} | {%} | |
| Orders/wk | {N} | {N} | {%} | |

{Or: "No PPC data available for the analysis periods."}

---

## Confounding Factors

| Factor | Checked | Found? | Impact |
|--------|---------|--------|--------|
| PPC bid changes | {Y/N} | {Y/N} | {description if found} |
| Competitor changes | {Y/N} | {Y/N} | {description if found} |
| Seasonality | {Y/N} | {Y/N} | {description if found} |
| Stock issues | {Y/N} | {Y/N} | {description if found} |
| Multiple listing changes | {Y/N} | {Y/N} | {description if found} |
| Campaign structure changes | {Y/N} | {Y/N} | {description if found} |

**Confidence:** {High / Medium / Low} — {reason}

---

## Revenue Impact Estimate

| Timeframe | Impact |
|-----------|--------|
| Weekly | +/- ${X} |
| Monthly | +/- ${X} |
| Annualized | +/- ${X} |

*Based on BA purchase delta × avg order value. Actual revenue may differ.*

---

## Recommendation

**{KEEP / REVERT / ITERATE / MONITOR}**

{Detailed recommendation:}
- {What to do next}
- {If ITERATE: specific suggestion for next change}
- {If MONITOR: when to re-run}

---

## Change Details

**What was modified:**
{Description of the change — old vs new if available from portfolio tracker}

**Change source:** {Listing Optimizer / Listing Creator / Manual / Unknown}

---

*Generated by Listing AB Analyzer — {YYYY-MM-DD}*
*Data source: Amazon Brand Analytics (first-party, not estimated)*
```

### Step 11: Save Snapshot (Machine-Readable)

**Snapshot file:** `outputs/research/listing-optimizer/ab-tests/{ASIN}-{YYYY-MM-DD}-ab-snapshot.json`

```json
{
  "asin": "",
  "product_name": "",
  "portfolio": "",
  "portfolio_stage": "",
  "change_date": "",
  "change_type": "",
  "change_source": "",
  "analysis_date": "",
  "before_period": {"start": "", "end": ""},
  "after_period": {"start": "", "end": ""},
  "verdict": "POSITIVE",
  "confidence": "High",
  "recommendation": "KEEP",
  "monthly_revenue_impact": 0,
  "funnel_comparison": {
    "impressions": {"before": 0, "after": 0, "delta": 0, "delta_pct": 0, "significant": false},
    "clicks": {"before": 0, "after": 0, "delta": 0, "delta_pct": 0, "significant": false},
    "ctr": {"before": 0, "after": 0, "delta_pts": 0, "significant": false},
    "cart_adds": {"before": 0, "after": 0, "delta": 0, "delta_pct": 0, "significant": false},
    "cart_rate": {"before": 0, "after": 0, "delta_pts": 0, "significant": false},
    "purchases": {"before": 0, "after": 0, "delta": 0, "delta_pct": 0, "significant": false},
    "purchase_rate": {"before": 0, "after": 0, "delta_pts": 0, "significant": false},
    "click_share": {"before": 0, "after": 0, "delta_pts": 0, "significant": false},
    "conv_share": {"before": 0, "after": 0, "delta_pts": 0, "significant": false},
    "conv_click_ratio": {"before": 0, "after": 0, "delta": 0, "significant": false}
  },
  "keyword_impacts": [
    {
      "keyword": "",
      "search_volume": 0,
      "before_primary_metric": 0,
      "after_primary_metric": 0,
      "delta": 0,
      "impact": "Improved"
    }
  ],
  "ppc_correlation": {
    "cvr": {"before": 0, "after": 0, "delta_pts": 0},
    "acos": {"before": 0, "after": 0, "delta_pts": 0},
    "sales_weekly": {"before": 0, "after": 0, "delta_pct": 0},
    "orders_weekly": {"before": 0, "after": 0, "delta_pct": 0}
  },
  "confounders": [
    {"factor": "", "found": false, "description": "", "impact": ""}
  ],
  "data_sources": {
    "scp_before_weeks": 2,
    "scp_after_weeks": 2,
    "sqp_before_weeks": 2,
    "sqp_after_weeks": 2,
    "ppc_data_available": true,
    "from_ba_archive": false
  }
}
```

### Step 12: Update Portfolio Tracker

Update the ASIN's portfolio tracker with the analysis result:

Add to `change_log`:
```json
{
  "date": "YYYY-MM-DD",
  "skill": "listing-ab-analyzer",
  "type": "ab_analysis",
  "details": "{verdict}: {one-line summary}. Monthly impact: +/-${X}. Recommendation: {KEEP/REVERT/ITERATE/MONITOR}",
  "change_analyzed": "{change_date} {change_type}"
}
```

If verdict is REVERT: add to `pending_actions`:
```json
{
  "action": "Consider reverting listing change from {change_date}",
  "reason": "{one-line from analysis}",
  "priority": "P2",
  "added_by": "listing-ab-analyzer",
  "added_date": "YYYY-MM-DD"
}
```

If verdict is MONITOR: add to `scheduled_reviews`:
```json
{
  "review_type": "listing-ab-recheck",
  "date": "{2 weeks from now}",
  "context": "Re-run AB analysis for {ASIN} — previous run was inconclusive"
}
```

### Step 13: Post Notifications

Read `.claude/skills/notification-hub/SKILL.md` → use the recipe below.

**Channel:** `#claude-product-updates`
**Format:**
```
:test_tube: *Listing Change Analysis* — {Product Name}

*Changed:* {what} on {date}
*Verdict:* {POSITIVE/NEGATIVE/NEUTRAL/INCONCLUSIVE}
*Revenue impact:* +/-${X}/month
*Confidence:* {High/Medium/Low}

*Key metrics:*
- CTR: {before}% → {after}% ({delta})
- Cart Rate: {before}% → {after}% ({delta})
- Purchases: {before}/wk → {after}/wk ({delta}%)

*Recommendation:* {KEEP/REVERT/ITERATE/MONITOR}
```

**Alert escalation to `#claude-alerts`:**
- NEGATIVE verdict with High confidence → alert (listing change is actively hurting sales)
- Monthly revenue impact > -$100/month → alert

If Slack MCP is unavailable, skip and note in run log.

---

## Error Handling

| Issue | Response |
|-------|----------|
| After period incomplete (<2 weeks) | Show partial data with 1 week. Note: "Preliminary — re-run after {date} for full analysis." Verdict defaults to INCONCLUSIVE unless change is dramatic (>25%) |
| After period incomplete (<1 week) | Cannot run. "Too early — need at least 1 full week of after data. Re-run after {date}." |
| No SQP data for any period | Use SCP only (ASIN-level). Note: "Per-keyword analysis unavailable — using ASIN-level funnel only." |
| No SCP data for before period | Cannot run meaningful analysis. "BA data not available for before period. Try pulling a monthly report instead." |
| No SCP data for after period | Cannot run. "BA data not available for after period — may not be processed yet. Try again tomorrow." |
| No PPC weekly snapshots for periods | Skip PPC correlation layer. Note in output. |
| Multiple listing changes in window | Flag prominently: "Multiple changes detected — cannot isolate impact of individual change." Reduce confidence to Low. |
| ASIN not in sku-asin-mapping | Ask user for portfolio context. If unknown, skip portfolio tracker updates. |
| BA weekly archive covers the periods | Read from archive — no fresh API calls needed. Note: "Data sourced from BA weekly archive." |
| Change was to backend keywords only | Focus on impressions for new keywords rather than conversion metrics. New keywords may take 1-2 weeks to index. |
| Zero purchases in both periods | Small product — use click share and CTR instead of purchase metrics for verdict. Note: "Low volume product — statistical significance limited." |
| Portfolio tracker has no change_log entry | User must provide change details manually. Note: "Change not found in portfolio tracker — using user-provided information." |

---

## AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/listing-ab-analyzer/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Result:** Success / Partial / Failed

**ASIN:** {ASIN}
**Product:** {name}
**Change analyzed:** {date} — {what changed}
**Verdict:** {POSITIVE / NEGATIVE / NEUTRAL / INCONCLUSIVE}
**Confidence:** {High / Medium / Low}
**Monthly impact:** +/-${X}
**Recommendation:** {KEEP / REVERT / ITERATE / MONITOR}
**Data source:** {BA archive / fresh API calls}
**Confounders:** {N} found

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
