---
name: ppc-portfolio-summary
description: Portfolio-level performance summary with health classification and campaign structure audit
triggers:
  - portfolio check
  - portfolio health
  - portfolio flags
  - portfolio summary
output_location: outputs/research/ppc-agent/portfolio/
---

# Portfolio Performance Summary

**USE WHEN** routed from the PPC Agent via: "portfolio check", "portfolio health", "portfolio flags"

**This skill is invoked through the PPC Agent orchestrator, not directly.**

---

## BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/ppc-portfolio-summary/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

A **focused portfolio-level scan** that classifies each portfolio's health, checks campaign structure completeness per SOP, and identifies the top 3 portfolios needing action. Faster and lighter than the full Weekly PPC Analysis.

**Cadence:** Every 2-3 days (between weekly deep dives)
**Time saved:** ~3-4 hrs/week
**Token budget:** <40K tokens, <4 minutes

**Distinction from Weekly PPC Analysis:**
- **This skill** = portfolio-level flags, campaign structure audit, quick status
- **Weekly PPC Analysis** = campaign-by-campaign deep dive, search term analysis, placement data, full WoW comparison

---

## Efficiency Standards

- **<40K tokens** per run
- **<4 minutes** execution time
- **1 Ads API report** (campaign report only — no search terms, placements, or targeting)
- **Reads weekly snapshot** for comparison baseline

---

## Process

### Step 1: Load Context

Load in parallel:

| File | Purpose |
|------|---------|
| `context/business.md` | Portfolio stages (Launch/Scaling/General) |
| Most recent `outputs/research/ppc-weekly/snapshots/*/summary.json` | Weekly baseline for delta comparison |
| Most recent `outputs/research/ppc-agent/portfolio/*-portfolio-snapshot.json` | Previous portfolio summary (for trend) |
| `outputs/research/ppc-agent/agent-state.json` | Last run dates |

### Step 2: Pull Fresh Campaign Data

Pull a fresh campaign-level report (last 7 days):

```
create_ads_report(report_type="sp_campaigns", date_range="LAST_7_DAYS", marketplace="US")
```

Poll and download inline (campaign reports are small enough — typically <500 rows):
```
download_ads_report(report_id="{id}", marketplace="US", max_rows=500)
```

### Step 3: Map Portfolios

```
list_portfolios(marketplace="US")
```

Group every campaign into its portfolio. Campaigns without a portfolio go under "Unassigned."

### Step 4: Compute Portfolio Metrics

For each portfolio, aggregate:

| Metric | Calculation |
|--------|-------------|
| **Spend** | Sum of `cost` across all campaigns |
| **Sales** | Sum of `sales7d` |
| **Orders** | Sum of `purchases7d` |
| **ACoS** | Spend / Sales (handle division by zero) |
| **ROAS** | Sales / Spend |
| **CVR** | Orders / Clicks |
| **CPC** | Spend / Clicks |
| **Campaign Count** | Number of ENABLED campaigns |
| **Campaign Types** | Count of Auto, Broad, SK, MK, PT, Shield, Other |

### Step 5: Classify Portfolio Health

| Classification | Criteria |
|---------------|----------|
| **TOP PERFORMER** | ACoS <20% AND CVR >12% AND Orders >10 |
| **HEALTHY** | ACoS within stage target AND CVR >8% |
| **NEEDS ATTENTION** | ACoS 10-20% above stage target OR CVR 6-8% |
| **RED FLAG** | ACoS >20% above stage target OR CVR <6% OR Orders dropped >30% WoW |
| **DORMANT** | <$5 spend in 7 days OR all campaigns paused/LOW BID |

**Stage-specific ACoS targets (from `context/business.md`):**
- Launch: target 40%, red flag >80%
- Scaling: target 30%, red flag >50%
- General: target 35%, red flag >60%

### Step 6: Campaign Structure Audit

Per SOP, each portfolio must have at minimum:

| Campaign Type | Required | How to Identify |
|--------------|----------|-----------------|
| **Auto** | 1 | Campaign name contains "SPA" or "Auto" |
| **Broad** | 1 | Campaign name contains "Broad" and match type = BROAD |
| **SK (Single Keyword)** | ~3 | Campaign name contains "SK" |
| **MK (Multi Keyword)** | ~2 | Campaign name contains "MK" |
| **Product Targeting** | 1 | Campaign name contains "PT" |
| **Shield** | 1 (in Shield portfolio) | Campaign name contains "Shield" |

For each portfolio, report:
- **Complete:** Has all required campaign types
- **Gaps:** Missing campaign types listed
- **Excess:** Unusual number of campaigns (>20 may indicate disorganization)
- **Idle:** Campaigns with LOW BID status or $0 spend in 14 days

### Step 7: Compare Against Weekly Baseline

If a weekly snapshot exists, compute deltas:

| Portfolio | This Period ACoS | Weekly ACoS | Delta | Direction |
|-----------|-----------------|-------------|-------|-----------|
| {name} | X% | X% | +/-X% | Improving / Worsening / Stable |

Flag portfolios that changed classification since the weekly analysis.

### Step 8: Generate Report

**Format:**

```markdown
# Portfolio Performance Summary — {YYYY-MM-DD}

**Data period:** Last 7 days
**Portfolios analyzed:** {N}
**Total spend:** ${X} | **Total sales:** ${X} | **Overall ACoS:** X%

---

## Portfolio Rankings

| Rank | Portfolio | Stage | ACoS | CVR | Spend | Orders | Status | vs Weekly |
|------|-----------|-------|------|-----|-------|--------|--------|-----------|
| 1 | {name} | Scaling | X% | X% | ${X} | {N} | TOP PERFORMER | Stable |
| 2 | {name} | Launch | X% | X% | ${X} | {N} | HEALTHY | Improving |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 15 | {name} | Scaling | X% | X% | ${X} | {N} | RED FLAG | Worsening |

## Top 3 Portfolios Needing Action

### 1. {Portfolio Name} — RED FLAG
- **Issue:** ACoS at X% (target: 30%), worsened X% from weekly
- **Root cause:** {top spending campaign with poor performance}
- **Recommended action:** Run bid review for this portfolio

### 2. {Portfolio Name} — NEEDS ATTENTION
- **Issue:** {description}
- **Recommended action:** {specific action}

### 3. {Portfolio Name} — NEEDS ATTENTION
- **Issue:** {description}
- **Recommended action:** {specific action}

## Campaign Structure Audit

| Portfolio | Auto | Broad | SK | MK | PT | Shield | Status |
|-----------|------|-------|-----|-----|-----|--------|--------|
| {name} | 1 | 1 | 3 | 2 | 1 | N/A | Complete |
| {name} | 1 | 0 | 2 | 0 | 0 | N/A | Gaps: Broad, MK, PT |
| {name} | 1 | 1 | 5 | 3 | 2 | N/A | Complete (high count) |

**Structural gaps found:** {N} portfolios missing required campaign types
**Dormant campaigns:** {N} campaigns with $0 spend (consider cleanup)

## Experimental Campaign Check (SOP Section 13)

The SOP requires **1-2 new test campaigns per week** (testing new keywords, match types, or targeting strategies).

Check campaign creation dates from `list_sp_campaigns` results:
- Count campaigns created in the last 7 days (filter by `startDate`)
- If 0 new campaigns this week: Flag — "No new test campaigns created this week. SOP recommends 1-2 experimental campaigns per week."
- If 1-2: Note — "On track with SOP experimental cadence."
- If 3+: Note — "Active testing week — {N} new campaigns. Monitor performance in next bid review."

| New Campaigns This Week | Campaign Name | Portfolio | Type | Start Date |
|------------------------|---------------|-----------|------|------------|
| {name} | {portfolio} | {Auto/Broad/SK/etc.} | {date} |

## Dormant/Idle Campaigns ({count})

| Campaign | Portfolio | Status | Days Idle | Last Spend | Recommendation |
|----------|-----------|--------|-----------|------------|----------------|
| {name} | {portfolio} | LOW BID | {N} | ${X} | Pause or increase bid |

## Summary

| Classification | Count | Total Spend | % of Account |
|---------------|-------|-------------|-------------|
| TOP PERFORMER | {N} | ${X} | X% |
| HEALTHY | {N} | ${X} | X% |
| NEEDS ATTENTION | {N} | ${X} | X% |
| RED FLAG | {N} | ${X} | X% |
| DORMANT | {N} | ${X} | X% |

**Next recommended action:** {Based on findings — e.g., "Run bid review for {portfolio}" or "All portfolios healthy — no immediate action needed"}
```

### Step 9: Save Outputs

**Brief:**
`outputs/research/ppc-agent/portfolio/{YYYY-MM-DD}-portfolio-summary.md`

**Snapshot (machine-readable):**
`outputs/research/ppc-agent/portfolio/{YYYY-MM-DD}-portfolio-snapshot.json`

```json
{
  "date": "YYYY-MM-DD",
  "portfolios": [
    {
      "name": "...",
      "stage": "Scaling",
      "acos": 0,
      "cvr": 0,
      "spend": 0,
      "orders": 0,
      "status": "HEALTHY",
      "campaign_count": 0,
      "campaign_types": {"auto": 1, "broad": 1, "sk": 3, "mk": 2, "pt": 1},
      "structure_complete": true,
      "missing_types": [],
      "idle_campaigns": 0,
      "vs_weekly": "stable"
    }
  ],
  "account_totals": {
    "spend": 0,
    "sales": 0,
    "acos": 0,
    "orders": 0
  },
  "red_flag_count": 0,
  "dormant_campaign_count": 0
}
```

---

## Error Handling

| Issue | Response |
|-------|----------|
| Campaign report fails | Retry once. If still fails, use most recent weekly snapshot data (note staleness) |
| `list_portfolios` returns <50 (truncated) | Known issue — note some portfolios may be missing. Flag for server fix. |
| No weekly snapshot for comparison | Skip WoW delta column, show absolute values only |
| Portfolio not in `context/business.md` | Default to "Scaling" thresholds, flag for user to update business.md |
| Campaign name doesn't match any type pattern | Classify as "Other" — may indicate non-standard naming |

---

## AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/ppc-portfolio-summary/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Result:** Success / Partial / Failed

**Portfolios analyzed:** {N}
**Red flags:** {N}
**Structural gaps:** {N} portfolios
**Dormant campaigns:** {N}

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
