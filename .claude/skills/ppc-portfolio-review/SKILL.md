# PPC Portfolio Review

**USE WHEN** user says: "ppc review", "portfolio review", "campaign analysis", "analyze portfolio", "ppc analysis", "ad performance", "review my campaigns", "full account review", "account report", "review all portfolios"

---

## What This Does

**Two modes:**

1. **Single Portfolio Review** — Analyzes one portfolio's campaign export, applies PPC SOP rules, determines portfolio stage, and generates a prioritized action to-do list with campaign-by-campaign breakdown.

2. **Full Account Review** — Analyzes ALL portfolios together using the Portfolios summary CSV + individual campaign CSVs. Generates a master report ranking all portfolios, identifying account-wide issues, and consolidating P1 actions across the entire account.

---

## Organization & Efficiency Standards

### File Organization

```
outputs/research/ppc-review/
├── input/         # DROP CSV EXPORTS HERE — skill auto-detects them
├── briefs/        # Portfolio analysis reports (what user reads)
├── data/          # Processed CSV exports moved here after analysis
└── README.md      # Folder guide
```

### Naming Conventions

| File Type | Format | Example |
|-----------|--------|---------|
| Analysis reports | `{portfolio-slug}-review-YYYY-MM-DD.md` | `cross-girl-review-2026-02-17.md` |
| Full account report | `full-account-review-YYYY-MM-DD.md` | `full-account-review-2026-02-17.md` |
| Raw data | `{portfolio-slug}-export-YYYY-MM-DD.csv` | `cross-girl-export-2026-02-17.csv` |

### Efficiency Targets

- **< 80K tokens** per portfolio analysis
- **< 5 minutes** execution time
- **No paid API calls** — works entirely from user-provided data

### Forbidden Practices

- Do NOT make assumptions about rank movement — flag as "check Data Dive" instead
- Do NOT recommend specific bid amounts — recommend direction (raise/lower) and magnitude (slightly/significantly)
- Do NOT skip low-activity campaigns — flag them as under-bidding or irrelevant
- Do NOT combine PAUSED/ARCHIVED campaigns into analysis — filter them out
- Do NOT use data from the last 2 days — remind user their export should exclude last 2 days per SOP

---

## Input

### Auto-Detection (Preferred)

**The skill automatically checks `outputs/research/ppc-review/input/` for CSV files.**

When the skill starts:
1. Glob for `outputs/research/ppc-review/input/*.csv`
2. If **one CSV found** → use it automatically, tell the user which file was detected
3. If **multiple CSVs found** → list them and ask the user which one to analyze
4. If **no CSVs found** → ask the user to either:
   - Drop a Seller Central export CSV into the `input/` folder and re-run
   - Provide a file path directly
   - Paste the data

### Workflow

1. User exports campaign data from Seller Central (last 7 days, exclude last 2 days)
2. User saves the CSV to `outputs/research/ppc-review/input/`
3. User says "ppc review" — skill picks up the file automatically
4. After analysis, the CSV is copied to `data/` folder with proper naming for archival

### Manual Override

User can also provide:
- **A CSV file path** directly (from anywhere on disk)
- **Pasted table data** from Seller Central

### Data Requirements

The data should cover **the last 7 days, excluding the last 2 days** (per SOP standard data window).

**Required columns** (from Seller Central export):
- Campaign name, Status, Type, Targeting (manual/auto), Start date
- Portfolio name, Budget
- Impressions, Clicks, CTR, Spend, CPC
- Orders, Sales, ACoS, ROAS
- Top-of-search IS (if available)

---

## Process

### Step 1: Find & Load Data

1. **Auto-detect:** Glob for `outputs/research/ppc-review/input/*.csv`
   - If 1 file found → read it, tell user: "Found: {filename} — analyzing now."
   - If multiple files → list them, ask user which to analyze
   - If no files → check if user provided a path or pasted data. If neither, tell them: "Drop your Seller Central export CSV into `outputs/research/ppc-review/input/` and run again."
2. If user provided a **file path** instead, read that file directly
3. Read the CSV file contents

### Step 2: Parse & Filter

1. Parse the campaign data from the CSV
2. **Filter OUT** all campaigns with status PAUSED or ARCHIVED
3. Separate campaigns into two groups:
   - **Active with data**: ENABLED campaigns with Spend > $0 or Impressions > 0
   - **Active but dormant**: ENABLED campaigns with $0 spend and 0 impressions (flag these separately)
4. Identify the **portfolio name** from the data

### Step 3: Calculate Portfolio-Level Metrics

Calculate for active campaigns with data:

| Metric | Formula |
|--------|---------|
| **Total Spend** | Sum of all campaign spend |
| **Total Sales** | Sum of all campaign sales |
| **Portfolio ACoS** | Total Spend / Total Sales |
| **Portfolio ROAS** | Total Sales / Total Spend |
| **Total Orders** | Sum of all campaign orders |
| **Total Clicks** | Sum of all campaign clicks |
| **Portfolio CVR** | Total Orders / Total Clicks |
| **Campaign Count** | Number of active campaigns with data |

### Step 4: Determine Portfolio Stage

Assess the portfolio stage based on these signals:

**Launch Stage** indicators:
- Most campaigns started within last 3 months
- Low total order volume (< 20 orders/week)
- Few campaign types present
- Product is new to market

**Growth Stage** indicators:
- Mix of established (3+ months) and newer campaigns
- Moderate order volume (20-50 orders/week)
- Building out campaign structure
- Adding single keyword and TOS campaigns

**Optimization Stage** indicators:
- Most campaigns 3+ months old
- Consistent order volume (50+ orders/week)
- Full campaign structure present
- Focus on refining bids and keywords

**Maintenance Stage** indicators:
- Long-running campaigns (6+ months)
- Stable, predictable performance
- Complete campaign structure
- Focus on health monitoring and cost control

**If unsure, ask the user** what stage this portfolio is in. Don't guess — the stage affects all thresholds.

**Stage-specific thresholds:**

| Metric | Launch | Growth | Optimization | Maintenance |
|--------|--------|--------|-------------|-------------|
| **ACoS target** | Flexible (focus on CVR) | ~35% | ~30% | ~30% or lower |
| **CVR focus** | PRIMARY metric | Important | Target 10% | Target 10%+ |
| **High ACoS tolerance** | Yes, if CVR > 10% | Moderate | Low | Low |

### Step 5: Campaign-by-Campaign Analysis

**Sort campaigns by spend (highest first)** — highest spend = highest priority.

For EACH active campaign, evaluate:

#### 4a. Campaign Classification

Identify the campaign type from its name and targeting:
- **Auto** (SPA): Targeting = AUTOMATIC
- **Broad** (SPM Broad): Manual, broad match
- **Product Targeting** (PAT): Manual, product/ASIN targeting
- **Single Keyword** (SK): Manual, single keyword focus — look for "SK" in name
- **Multi Keyword** (MK): Manual, multiple keywords — look for "MK" in name
- **TOS Push**: Look for "TOS" in campaign name — these have Top-of-Search focus
- **Video** (SB/SBV): Type = SB or SB2
- **Sponsored Display** (SD): Type = SD
- **Brand Shield**: Look for "shield" or "brand" + "defense" in name
- **Catch-all**: Look for "catch" in name, or if it's a broad campaign in a catch-all portfolio

#### 4b. Calculate Campaign Metrics

| Metric | Formula |
|--------|---------|
| **CVR** | Orders / Clicks (show as %) |
| **% of portfolio spend** | Campaign Spend / Total Portfolio Spend |

#### 4c. Apply Decision Rules

**Core Decision Matrix:**

| ACoS | CVR | Action | Priority |
|------|-----|--------|----------|
| > 40% | < 10% | **Lower bids significantly, consider pausing** | P1 |
| > 40% | >= 10% | **Lower bids/TOS% — targeting is right, too expensive** | P1 |
| 30-40% | < 10% | **Investigate targeting relevance, check search terms** | P2 |
| 30-40% | >= 10% | **Minor bid reduction, monitor** | P2 |
| 20-30% | >= 10% | **Healthy — maintain or scale slightly** | P3 (no action) |
| < 20% | >= 15% | **Top performer — consider increasing budget** | P3 (scale) |
| < 25% | < 10% | **Efficient but low conversion — check relevance** | P2 |

**Special Campaign Rules:**

| Campaign Type | Special Rule |
|--------------|-------------|
| **TOS campaigns** | High ACoS can be tolerated IF driving rank movement. Always recommend checking Data Dive before cutting. |
| **New campaigns (< 8 weeks old)** | Focus on CVR as primary metric. Tolerate higher ACoS. Flag as "experimental — needs more data" if < 3 weeks. |
| **Catch-all campaigns** | Stricter ACoS target: 20-25%. Flag if above 25%. |
| **Brand shield** | Low spend is expected and fine. Only flag if ACoS is unusually high. |
| **Video campaigns (SB/SBV)** | Consider DPV (detail page views) as an additional metric if available. |
| **SD campaigns** | Evaluate with different expectations — lower CTR is normal. Consider viewable impressions. |
| **0 orders + significant spend (> $10)** | Flag as urgent — bleeding money with no return. |
| **Very low spend (< $1/week) + ENABLED** | Flag as under-bidding. Either increase bids or evaluate if worth keeping. |
| **Running 3+ months with near-zero activity** | Flag as dead campaign — either revive or cut. |

### Step 6: Structure Check

Verify the portfolio has the required campaign types per SOP:

| Required | Check |
|----------|-------|
| 1 Auto campaign | Present? Active? |
| 1 Broad campaign | Present? Active? |
| 1 Product targeting campaign | Present? With 3-5 single targets + 2 multi-keyword? |
| Single keyword campaigns (for top performers) | Present if portfolio is at Growth+ stage? |

Note any **gaps** — missing campaign types the portfolio should have based on its stage.

### Step 7: Generate Report

Output the full analysis as a structured markdown report. Follow the exact output format below.

---

## Output Format

Generate a markdown report with these sections in this exact order:

```markdown
# PPC Portfolio Review: {Portfolio Name}

**Date:** {YYYY-MM-DD}
**Data Window:** Last 7 days (excl. last 2 days)
**Portfolio Stage:** {Launch / Growth / Optimization / Maintenance}

---

## Portfolio Overview

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Spend | ${X} | — | — |
| Total Sales | ${X} | — | — |
| Portfolio ACoS | X% | {stage-based target}% | {OK / Above Target / Well Above} |
| Portfolio ROAS | X | — | — |
| Total Orders | X | — | — |
| Portfolio CVR | X% | 10% | {OK / Below Target} |
| Active Campaigns | X | — | — |

---

## Action To-Do List

### P1 — Act Now (Highest Impact)
- [ ] {Campaign name}: {specific action + reason}
- [ ] {Campaign name}: {specific action + reason}

### P2 — Investigate & Adjust
- [ ] {Campaign name}: {specific action + reason}
- [ ] {Campaign name}: {specific action + reason}

### P3 — Monitor / Scale
- [ ] {Campaign name}: {specific action + reason}

### Structure Gaps
- [ ] {Missing campaign type}: {recommendation}

---

## Campaign-by-Campaign Analysis

### 1. {Campaign Name} — {HEALTHY / WATCH / NEEDS ACTION / TOP PERFORMER / FLAG}

| Metric | Value | vs. Target |
|--------|-------|------------|
| Type | {Auto/Broad/SK/MK/PAT/TOS/Video/SD/Shield} | — |
| Spend | ${X} ({Y}% of portfolio) | — |
| ACoS | X% | {Above/Below/At} {target}% |
| CVR | X% (orders/clicks) | {Above/Below} 10% |
| CPC | ${X} | — |
| CTR | X% | — |
| Orders | X | — |
| Sales | ${X} | — |
| Budget | ${X}/day | — |
| TOS IS | X% | (if applicable) |
| Age | {X months} (started {date}) | — |

**Assessment:** {1-2 sentence analysis explaining what's happening}

**Recommendation:** {Specific action to take}

---

[Repeat for each active campaign, sorted by spend descending]

---

## Dormant Campaigns (ENABLED but no activity)

| Campaign | Budget | Start Date | Recommendation |
|----------|--------|------------|----------------|
| {name} | ${X} | {date} | {Increase bids / Cut / Investigate} |

---

## Structure Check

| Required Type | Present? | Campaign | Status |
|--------------|----------|----------|--------|
| Auto | {Yes/No} | {name or "Missing"} | {Healthy/Needs work} |
| Broad | {Yes/No} | {name or "Missing"} | {Healthy/Needs work} |
| Product Targeting | {Yes/No} | {name or "Missing"} | {Healthy/Needs work} |
| Single Keyword | {Yes/No} | {name or "Missing"} | {Healthy/Needs work} |

**Gaps:** {List any missing campaign types and recommendations}

---

## Summary

**What's working:** {1-2 bullet points on top performers}
**What needs attention:** {1-2 bullet points on biggest issues}
**Quick wins:** {1-2 immediate actions with highest ROI}
**Data Dive checks needed:** {List any campaigns where rank movement needs verification}
```

---

## Output Location

1. Save the report to: `outputs/research/ppc-review/briefs/{portfolio-slug}-review-YYYY-MM-DD.md`
2. **Copy** the input CSV to: `outputs/research/ppc-review/data/{portfolio-slug}-export-YYYY-MM-DD.csv` (archived with proper naming)
3. **Delete** the original CSV from `outputs/research/ppc-review/input/` to keep the input folder clean for the next run

---

## Execution Checklist

Before delivering the report, verify:

- [ ] Only ENABLED campaigns with activity are analyzed
- [ ] Campaigns are sorted by spend (highest first)
- [ ] Portfolio stage is stated and thresholds adjusted accordingly
- [ ] Every active campaign has a classification, metrics, assessment, and recommendation
- [ ] ACoS is evaluated relative to stage-specific targets (not a fixed 30% for all)
- [ ] TOS campaigns are flagged for Data Dive check (not auto-recommended for cutting)
- [ ] New campaigns (< 8 weeks) are evaluated primarily on CVR
- [ ] Catch-all campaigns use stricter ACoS thresholds (20-25%)
- [ ] Structure check covers all required campaign types
- [ ] Action to-do list is prioritized (P1 > P2 > P3)
- [ ] Actions are specific (not "optimize this campaign" — say exactly what to do)
- [ ] Dormant campaigns are listed separately
- [ ] Report is saved to correct output location

---

## Error Handling

| Issue | Response |
|-------|----------|
| CSV is for multiple portfolios | Ask user which portfolio to analyze, or offer to do them one at a time |
| Missing columns (no ACoS, no Orders) | Calculate from available data if possible. Flag missing data. |
| No active campaigns with data | Report that the portfolio has no recent activity. Ask if date range is correct. |
| User doesn't know portfolio stage | Estimate from campaign ages and volume, but ask for confirmation |
| Data includes last 2 days | Warn user that last 2 days may have unreliable attribution data per SOP |

---

## Full Account Review Mode

**Triggered by:** "full account review", "account report", "review all portfolios", or when user provides a Portfolios summary CSV + multiple campaign CSVs.

### When to Use

Use this mode when the user wants a bird's-eye view across ALL portfolios — comparing performance, identifying account-wide patterns, and prioritizing where to focus time.

### Input

Requires **one of**:
1. **Portfolios summary CSV** from Seller Central (portfolio-level export with spend/sales/ACoS per portfolio)
2. **Individual portfolio review reports** already generated in `briefs/`
3. **Both** (preferred — summary for totals, individual reports for detail)

### Process

#### Step 1: Load Data

1. Check for Portfolios summary CSV in `outputs/research/ppc-review/input/` (file containing "Portfolio" in the name)
2. Check for existing individual portfolio reviews in `outputs/research/ppc-review/briefs/`
3. If both are available, use both. If only the summary CSV, work from that.

#### Step 2: Filter Active Portfolios

From the Portfolios summary:
1. Filter OUT portfolios with $0 spend and 0 impressions
2. Separate into:
   - **Product portfolios** — standard product-based portfolios
   - **Catch-all portfolios** — look for "catch" in the name
   - **Shield portfolios** — look for "shield" in the name
   - **Dormant portfolios** — ENABLED with $0 activity

#### Step 3: Calculate Account-Level Metrics

| Metric | Formula |
|--------|---------|
| **Total Account Spend** | Sum of all active portfolio spend |
| **Total Account Sales** | Sum of all active portfolio sales |
| **Account ACoS** | Total Spend / Total Sales |
| **Account ROAS** | Total Sales / Total Spend |
| **Total Orders** | Sum of all portfolio orders |
| **Active Portfolios** | Count of portfolios with spend > $0 |

#### Step 4: Rank Portfolios

Create rankings by:
1. **Spend** (highest → lowest) — where is money going?
2. **ACoS** (lowest → highest) — who is most efficient?
3. **ROAS** (highest → lowest) — who returns the most?
4. **Orders** (highest → lowest) — who drives the most volume?

Flag outliers:
- Portfolios with ACoS > 50% → **RED FLAG**
- Portfolios with ACoS < 25% → **TOP PERFORMER**
- Portfolios spending > 15% of total account spend → **HIGH CONCENTRATION**

#### Step 5: Identify Account-Wide Patterns

Look for:
- **Budget concentration** — is spend spread evenly or concentrated in a few portfolios?
- **ACoS distribution** — how many portfolios are above/below target?
- **Structural gaps** — which portfolios are missing campaign types? (from individual reviews)
- **Launch vs. established** — how many portfolios are in each stage?

#### Step 6: Consolidate P1 Actions

If individual portfolio reviews exist, pull ALL P1 actions across all portfolios into a single prioritized list, sorted by:
1. Spend impact (highest spend campaigns first)
2. Severity (ACoS > 50% before ACoS > 40%)

#### Step 7: Generate Full Account Report

### Full Account Report Format

```markdown
# PPC Full Account Review

**Date:** {YYYY-MM-DD}
**Data Window:** Last 7 days (excl. last 2 days)
**Portfolios Analyzed:** {X active} of {Y total}

---

## Account Overview

| Metric | Value |
|--------|-------|
| Total Account Spend | ${X} |
| Total Account Sales | ${X} |
| Account ACoS | X% |
| Account ROAS | X |
| Total Orders | X |
| Active Portfolios | X |
| Catch-All Portfolios | X |
| Shield Portfolios | X |

---

## Portfolio Rankings

### By Spend (where the money goes)

| Rank | Portfolio | Spend | % of Total | ACoS | ROAS | Orders | Status |
|------|-----------|-------|------------|------|------|--------|--------|
| 1 | {name} | ${X} | X% | X% | X | X | {OK / WATCH / FLAG} |

### Efficiency Leaderboard (best ACoS)

| Rank | Portfolio | ACoS | ROAS | Spend | Orders |
|------|-----------|------|------|-------|--------|
| 1 | {name} | X% | X | ${X} | X |

### Volume Leaders (most orders)

| Rank | Portfolio | Orders | Sales | ACoS | Spend |
|------|-----------|--------|-------|------|-------|
| 1 | {name} | X | ${X} | X% | ${X} |

---

## Account Health Assessment

### Portfolio Stage Distribution

| Stage | Count | Portfolios |
|-------|-------|------------|
| Launch | X | {names} |
| Growth | X | {names} |
| Optimization | X | {names} |
| Maintenance | X | {names} |

### ACoS Distribution

| Range | Count | Portfolios |
|-------|-------|------------|
| < 25% (Excellent) | X | {names} |
| 25-35% (Healthy) | X | {names} |
| 35-50% (Above Target) | X | {names} |
| > 50% (Red Flag) | X | {names} |

### Budget Concentration

| Top 3 Portfolios | Spend | % of Total |
|-------------------|-------|------------|
| {name} | ${X} | X% |

**Concentration Risk:** {Assessment — is spend too concentrated or well-distributed?}

---

## Consolidated P1 Actions (Act Now)

Priority actions across ALL portfolios, ranked by spend impact:

| # | Portfolio | Campaign | Action | Spend at Risk |
|---|-----------|----------|--------|---------------|
| 1 | {portfolio} | {campaign} | {action} | ${X} |

---

## Portfolio-by-Portfolio Summary

### {Portfolio Name} — {HEALTHY / WATCH / NEEDS ATTENTION / RED FLAG}

| Metric | Value | Status |
|--------|-------|--------|
| Spend | ${X} | — |
| ACoS | X% | {status} |
| ROAS | X | — |
| Orders | X | — |
| Stage | {stage} | — |
| P1 Actions | X | — |

**Key Issue:** {1 sentence}
**Quick Win:** {1 sentence}

[Repeat for each active portfolio]

---

## Dormant Portfolios

| Portfolio | Status | Last Activity | Recommendation |
|-----------|--------|---------------|----------------|
| {name} | ENABLED, $0 spend | {date or "Unknown"} | {Clean up / Investigate / Revive} |

---

## Account-Level Recommendations

**Top 3 Priorities This Week:**
1. {Specific action with portfolio + campaign}
2. {Specific action}
3. {Specific action}

**Structural Improvements:**
- {Gaps to fill across portfolios}

**Budget Reallocation Opportunities:**
- {Where to shift spend for better returns}

**Data Dive Checks Needed:**
- {List of TOS campaigns across all portfolios that need rank verification}
```

### Output Location

Save the full account report to: `outputs/research/ppc-review/briefs/full-account-review-YYYY-MM-DD.md`

### Batch Processing

When the user drops **multiple campaign CSVs** into `input/` and says "review all portfolios" or "full account review":

1. Detect all CSVs in `input/`
2. Also check for a Portfolios summary CSV (contains "Portfolio" in filename and has portfolio-level columns)
3. For each campaign CSV, launch an individual portfolio review (can run in parallel via background agents)
4. After all individual reviews complete, generate the full account report
5. Archive all CSVs to `data/` and clear `input/`
