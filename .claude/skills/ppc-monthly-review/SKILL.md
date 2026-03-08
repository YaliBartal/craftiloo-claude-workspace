---
name: ppc-monthly-review
description: Monthly strategic PPC review — trends, stage transitions, budget reallocation, competitive landscape
triggers:
  - monthly ppc
  - monthly review
  - ppc month
  - monthly ppc review
output_location: outputs/research/ppc-agent/monthly/
---

# Monthly PPC Review

**USE WHEN** routed from the PPC Agent via: "monthly ppc", "monthly review", "ppc month"

**This skill is invoked through the PPC Agent orchestrator, not directly.**

---

## BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/ppc-monthly-review/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

A **strategic monthly deep dive** that aggregates 4 weeks of data to identify trends, recommend portfolio stage transitions, suggest budget reallocation, and flag dormant campaigns for cleanup. This is the PPC worker's 2-3 hour monthly review, compressed into structured analysis.

**Cadence:** Monthly (end of month)
**Token budget:** <100K tokens, <10 minutes

---

## Efficiency Standards

- **<100K tokens** per run
- **<10 minutes** execution time
- **No fresh API calls** — reads exclusively from existing snapshots
- If insufficient snapshots exist, note what's missing rather than pulling fresh data

---

## Process

### Step 1: Load All Monthly Data

Gather snapshots from the past 4 weeks. Read in parallel:

| File Pattern | Purpose |
|-------------|---------|
| `outputs/research/ppc-weekly/snapshots/*/summary.json` | 4 weekly summaries for trend calculation |
| `outputs/research/ppc-agent/portfolio-summaries/*-portfolio-snapshot.json` | All portfolio summaries this month |
| `outputs/research/ppc-agent/bids/*-bid-changes-applied.json` | All bid changes made this month |
| `outputs/research/ppc-agent/search-terms/*-applied-actions.json` | All search term actions this month |
| `outputs/research/ppc-agent/daily-health/*-health-snapshot.json` | Daily health checks for trend granularity |
| `outputs/research/market-intel/snapshots/*.json` | Market intel for competitive context |
| `context/business.md` | Current portfolio stages |

**Minimum requirement:** At least 2 weekly snapshots to compute trends. If fewer exist, note: "Insufficient data for full monthly analysis. {N} weekly snapshots available — need at least 2. Showing available data only."

### Step 2: Compute Monthly Trends

For each metric, calculate the 4-week trajectory:

| Metric | Week 1 | Week 2 | Week 3 | Week 4 | Trend | 4-Week Delta |
|--------|--------|--------|--------|--------|-------|-------------|
| Total Spend | ${X} | ${X} | ${X} | ${X} | {arrow} | +/-X% |
| Total Sales | ${X} | ${X} | ${X} | ${X} | {arrow} | +/-X% |
| Overall ACoS | X% | X% | X% | X% | {arrow} | +/-X pts |
| TACoS | X% | X% | X% | X% | {arrow} | +/-X pts |
| Organic Ratio | X% | X% | X% | X% | {arrow} | +/-X pts |
| Total Orders | {N} | {N} | {N} | {N} | {arrow} | +/-X% |
| CPC | ${X} | ${X} | ${X} | ${X} | {arrow} | +/-X% |

**Trend classification:**
- **Improving:** 3+ consecutive weeks of improvement
- **Worsening:** 3+ consecutive weeks of decline
- **Volatile:** No clear direction (up-down-up)
- **Stable:** <5% variation across weeks

### Step 3: Portfolio-Level Monthly Analysis

For each portfolio, compute:

| Metric | Month Start | Month End | Delta | Assessment |
|--------|------------|-----------|-------|------------|
| ACoS | X% | X% | +/-X pts | Improving / Worsening |
| CVR | X% | X% | +/-X pts | |
| Spend | ${X}/wk | ${X}/wk | +/-X% | |
| Orders | {N}/wk | {N}/wk | +/-X% | |
| Rank (avg hero keywords) | #{N} | #{N} | +/-{N} | |

**Classify each portfolio's monthly trajectory:**
- **Strong Improvement:** ACoS decreased >5 pts AND orders increased
- **Moderate Improvement:** ACoS decreased 2-5 pts OR orders increased >10%
- **Stable:** Changes within +/-2 pts ACoS and +/-10% orders
- **Moderate Decline:** ACoS increased 2-5 pts OR orders decreased >10%
- **Significant Decline:** ACoS increased >5 pts AND/OR orders decreased >20%

### Step 4: Portfolio Stage Transition Analysis

For each portfolio, evaluate whether its current stage is still appropriate:

#### Launch -> Scaling Transition Criteria

A Launch portfolio is ready for Scaling when:
- Hero keywords are ranked top 20 organically for 2+ consecutive weeks
- CVR has stabilized at >8%
- Organic ratio has grown to >40%
- Campaign structure is complete (Auto + Broad + SK + MK + PT per SOP)

#### Scaling -> Launch Regression Criteria

A Scaling portfolio should regress to Launch when:
- Hero keywords dropped below rank 30 for 2+ consecutive weeks
- Organic ratio declined below 30%
- Major competitor entered with aggressive pricing/advertising
- Product had significant OOS period (rank reset)

**For each portfolio where a transition is suggested, provide:**
- The data evidence (rank, ACoS, CVR, organic ratio over 4 weeks)
- The recommended new stage
- What changes in thresholds/strategy this implies
- **Present as recommendation only — stage transitions are human decisions**

### Step 5: Budget Allocation Analysis

Compute how efficiently each portfolio uses its budget:

| Portfolio | Monthly Spend | Monthly Orders | Cost Per Order | ROAS | Efficiency Rank |
|-----------|-------------|----------------|----------------|------|----------------|
| {name} | ${X} | {N} | ${X} | {X} | 1 (best) |

**Budget reallocation recommendations:**

Look for mismatches between spend and performance:
- **Over-invested:** High spend + high ACoS + declining orders = shift budget away
- **Under-invested:** Low spend + low ACoS + high CVR + budget starved = shift budget toward
- **Right-sized:** Spend proportional to returns

**Present as a simple table:**

| From Portfolio | To Portfolio | Amount | Reason |
|---------------|-------------|---------|--------|
| {over-invested} | {under-invested} | ${X}/week | {efficiency rationale} |

### Step 6: Actions Taken This Month

Summarize all PPC actions taken during the month:

| Action Type | Count | Details |
|-------------|-------|---------|
| Negatives applied | {N} | From {N} harvest runs + {N} NKG runs |
| Bid changes | {N} | {N} decreases, {N} increases, {N} pauses |
| Budget changes | {N} | Net +/-${X}/week |
| Keywords promoted | {N} | {list} |

**Assess impact:** Did the actions taken produce the expected results?
- Negatives applied → Did zero-order spend decrease?
- Bid decreases → Did ACoS improve without rank loss?
- Bid increases → Did rank improve?

### Step 7: Dormant Campaign Cleanup

Identify all campaigns that should be cleaned up:

| Category | Criteria | Count |
|----------|----------|-------|
| LOW BID | Campaign status LOW_BID for >14 days | {N} |
| Zero spend | $0 spend in past 30 days (but ENABLED) | {N} |
| Zero orders | $50+ spend but 0 orders in past 30 days | {N} |
| Duplicate intent | Multiple campaigns targeting the same keyword | {N} |

**Recommendation per campaign:** Pause, archive, increase bid, or restructure.

### Step 8: Competitive Landscape Changes

If market intel snapshots exist, summarize competitive shifts:

- New competitors appearing in hero keyword positions
- Price changes by top competitors
- BSR movements of main competitors
- Any competitor launching deals/promotions

**Source:** Market intel snapshots from `outputs/research/market-intel/snapshots/`

### Step 9: Generate Monthly Report

**Format:**

```markdown
# Monthly PPC Review — {Month YYYY}

**Period:** {first date} to {last date}
**Weekly snapshots used:** {N} of 4
**Data completeness:** {Complete / Partial — X weeks missing}

---

## Executive Summary

{3-5 bullet points summarizing the month:}
- Overall direction (improving/declining/stable)
- Biggest win this month
- Biggest concern this month
- Key metric movements
- Top recommendation for next month

---

## Monthly Trends

| Metric | Week 1 | Week 2 | Week 3 | Week 4 | Trend | Delta |
|--------|--------|--------|--------|--------|-------|-------|
| ... | ... | ... | ... | ... | ... | ... |

## Portfolio Performance Rankings

| Rank | Portfolio | Stage | Month-End ACoS | Monthly Trajectory | Key Metric |
|------|-----------|-------|----------------|-------------------|------------|
| 1 | {best} | Scaling | X% | Strong Improvement | Orders +25% |
| ... | ... | ... | ... | ... | ... |
| 15 | {worst} | Scaling | X% | Significant Decline | ACoS +12 pts |

## Portfolios That Improved Most
{Top 3 with why}

## Portfolios That Declined Most
{Bottom 3 with why and recommended action}

## Stage Transition Recommendations

| Portfolio | Current Stage | Recommended | Evidence |
|-----------|-------------|-------------|----------|
| {name} | Launch | -> Scaling | Hero keywords top 20 for 3 weeks, CVR 11%, organic ratio 45% |
| {name} | Scaling | -> Launch | Hero keywords dropped to 35+, organic ratio fell to 25% |

## Budget Reallocation

| From | To | Amount | Rationale |
|------|----|--------|-----------|
| {portfolio} | {portfolio} | ${X}/week | {reason} |

**Net budget change recommendation:** +/-${X}/week total PPC budget

## Actions Taken This Month

| Type | Count | Impact Assessment |
|------|-------|-------------------|
| Negatives applied | {N} | Zero-order spend {decreased/increased} ${X}/week |
| Bid changes | {N} | ACoS {improved/worsened} by X pts on affected campaigns |
| Keywords promoted | {N} | {N} new SK campaigns generating ${X} in sales |

## Campaign Cleanup Recommendations

| Campaign | Portfolio | Issue | Recommendation |
|----------|-----------|-------|----------------|
| {name} | {portfolio} | LOW BID 21 days | Pause |
| {name} | {portfolio} | $75 spend, 0 orders | Pause |

**Total cleanup candidates:** {N} campaigns, ${X}/month in potential savings

## Competitive Landscape

{Summary of competitor movements from market intel, or "No market intel snapshots available for competitive analysis"}

## Next Month Priorities

1. {Highest priority action}
2. {Second priority}
3. {Third priority}

## KPI Targets for Next Month

| Metric | This Month | Target | Why |
|--------|-----------|--------|-----|
| Overall ACoS | X% | X% | {rationale} |
| TACoS | X% | X% | {rationale} |
| Zero-order spend | ${X}/week | ${X}/week | {based on harvest cadence} |
```

### Step 10: Save Output

**Report:**
`outputs/research/ppc-agent/monthly/{YYYY-MM}-monthly-review.md`

---

## Error Handling

| Issue | Response |
|-------|----------|
| <2 weekly snapshots | Note data limitation, show what's available, skip trend analysis |
| No portfolio summaries | Use weekly snapshots only for portfolio data |
| No bid change logs | Skip "Actions Taken" assessment |
| No market intel snapshots | Skip competitive landscape section |
| Portfolio stages outdated in business.md | Flag: "Portfolio stages in business.md were last updated {date}. Review stage assignments." |

---

## AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/ppc-monthly-review/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM (Month)
**Result:** Success / Partial / Failed

**Weekly snapshots used:** {N} of 4
**Stage transitions recommended:** {N}
**Budget reallocations recommended:** {N} (${X} total)
**Cleanup candidates:** {N} campaigns

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
