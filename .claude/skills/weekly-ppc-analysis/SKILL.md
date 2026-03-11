---
name: weekly-ppc-analysis
description: Comprehensive weekly PPC analysis via Amazon Ads API with WoW comparison, 30-day trajectories, and inflection detection
triggers:
  - weekly ppc
  - ppc analysis
  - weekly review
  - ppc report
  - weekly ppc analysis
  - analyze ppc
  - campaign analysis
  - ppc review
  - ppc trends
  - ppc dashboard
  - trend check
  - trajectory
  - time series
  - 30 day trend
  - inflection points
  - ppc timeline
output_location: outputs/research/ppc-weekly/
---

# Weekly PPC Analysis

**USE WHEN** user says: "weekly ppc", "ppc analysis", "weekly review", "ppc report", "campaign analysis", "ppc review", "analyze ppc", "search term analysis", "negate terms", "keyword mining", "ppc trends", "ppc dashboard", "trend check", "trajectory", "time series", "30 day trend", "inflection points"

---

## ⚠️ BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/weekly-ppc-analysis/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"⚠️ Repeat issue (×N): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

Pulls 4 reports via the **Amazon Ads API** (Campaign, Search Term, Placement, Targeting) and produces a comprehensive weekly PPC analysis covering:

1. **Account & portfolio health** — ACoS, ROAS, CVR, spend, sales, orders
2. **Campaign-level diagnosis** — what's working, what's bleeding, what to adjust
3. **Placement insights** — TOS vs ROS vs Product Pages performance
4. **Targeting insights** — keyword vs ASIN effectiveness, target-level performance
5. **Search term actions** — Negate, Promote, Discover classifications
6. **Week-over-week comparison** — deltas against previous week's snapshot
7. **30-day trajectories** — trend direction per portfolio from weekly snapshot history
8. **Inflection point detection** — statistically significant metric shifts correlated with change_log events

Replaces the separate PPC Portfolio Review and Search Term Analysis skills. **No manual CSV exports needed** — all data is pulled programmatically via the Amazon Ads API MCP server.

---

## Organization & Efficiency Standards

### File Organization

```
outputs/research/ppc-weekly/
├── briefs/        # Weekly analysis reports (what user reads)
├── snapshots/     # Archived weekly data for WoW comparison
│   └── YYYY-MM-DD/
│       ├── campaign-report.json
│       ├── search-term-report.json
│       ├── placement-report.json
│       ├── targeting-report.json
│       └── summary.json
├── data/          # Any processed/intermediate data
└── README.md      # Folder guide
```

### Naming Conventions

| File Type | Format | Example |
|-----------|--------|---------|
| Weekly report | `weekly-ppc-analysis-YYYY-MM-DD.md` | `weekly-ppc-analysis-2026-02-24.md` |
| Snapshot folder | `YYYY-MM-DD/` | `2026-02-24/` |
| Snapshot data | `{report-type}-report.json` | `campaign-report.json` |
| Summary data | `summary.json` | `summary.json` |

### Efficiency Targets

- **< 80K tokens** per analysis
- **< 5 minutes** execution time
- **No additional cost** — uses Amazon Ads API (free with approval) + Seller Board auto-reports + DataDive API

### Forbidden Practices

- Use SOP bid adjustment ranges when recommending changes (see Bid Adjustment Framework in Step 6)
- Do NOT make assumptions about rank movement — flag as "check Data Dive" instead
- Do NOT auto-negate competitor brand terms — always separate list for human decision
- Do NOT negate terms with fewer than 3 impressions — not enough data
- Do NOT skip low-activity campaigns or low-impression terms — flag them
- Do NOT combine PAUSED/ARCHIVED campaigns into analysis — filter them out
- Do NOT use data from the last 2 days — the API date range automatically excludes last 2 days per SOP
- Do NOT combine data from different date ranges in one analysis
- **NEVER recommend pausing a campaign based on a single week of zero conversions.** Always check a longer timeframe (minimum 30 days, ideally 60 days) before recommending a pause. A campaign with zero orders in one week might just be in a rough patch. Only recommend pausing if the campaign shows sustained poor performance over the longer timeframe.
- **NEVER use round/organized bid amounts.** When lowering or placing bids, never use clean percentages like -30%, -50%. Always use slightly irregular amounts like -31%, -48%, -52%, -27%. This avoids predictable bid patterns and helps stand out in Amazon's auction dynamics.
- **NEVER negate a search term based on a single week of zero conversions.** Always check a minimum 30-day window of data before recommending a search term for negation. A search term with zero orders in one week might convert in other weeks. Only recommend negating if the search term shows sustained zero conversions AND is clearly irrelevant to the product over the full 30-day window.

---

## Input — Amazon Ads API (Automated)

**All data is pulled programmatically via the Amazon Ads API MCP server.** No manual CSV exports needed.

### Report Types & API Presets

| Report Type | API Preset | Key Fields |
|-------------|-----------|------------|
| **Campaign** | `sp_campaigns` | campaignName, campaignId, campaignStatus, campaignBudgetAmount, **portfolioId**, impressions, clicks, cost, purchases7d, sales7d, costPerClick, clickThroughRate |
| **Search Term** | `sp_search_terms` | searchTerm, campaignName, adGroupName, targeting, impressions, clicks, cost, purchases7d, sales7d, costPerClick, clickThroughRate |
| **Placement** | `sp_placements` | campaignName, campaignId, placementClassification, impressions, clicks, cost, purchases7d, sales7d |
| **Targeting** | `sp_keywords` | campaignName, adGroupName, targeting, matchType, impressions, clicks, cost, purchases7d, sales7d, topOfSearchImpressionShare |

**Additional data pull (not a report — direct API call):**

| Source | API Call | Key Fields |
|--------|----------|------------|
| **Campaign TOS Modifiers** | `list_sp_campaigns(state="ENABLED", marketplace="US")` | `placementBidding` (current TOS/ROS/PP modifier percentages per campaign) |

This enables the "Current TOS%" column in placement health analysis and the Bid Recommender's lever selection logic.

### API Field → Metric Mapping

The API uses different field names than Seller Central CSV exports. Use this mapping when processing data:

| API Field | Metric Name (used in analysis) |
|-----------|-------------------------------|
| `cost` | Spend |
| `purchases7d` | Orders |
| `sales7d` | Sales |
| `costPerClick` | CPC |
| `clickThroughRate` | CTR |
| `campaignBudgetAmount` | Budget |
| `campaignStatus` | Status |
| `searchTerm` | Customer Search Term |
| `placementClassification` | Placement |
| `matchType` | Match Type |
| `topOfSearchImpressionShare` | Top-of-search IS |

**Calculated metrics** (not in raw API data — compute during analysis):
- **ACoS** = cost / sales7d × 100
- **ROAS** = sales7d / cost
- **CVR** = purchases7d / clicks × 100

### Date Range

All 4 reports use the same date range: **last 9 days through 2 days ago** (7 full days, excluding last 2 per PPC SOP).

The `create_ads_report` tool accepts `LAST_7_DAYS` which covers yesterday through 7 days back. To properly exclude the last 2 days per SOP, use a **custom date range**: calculate `today - 9 days` to `today - 3 days` and pass as `YYYYMMDD-YYYYMMDD`.

### Marketplace

Default marketplace: **US** (profile 4231260294381475). If user requests CA analysis, pass `marketplace="CA"`.

---

## Process

### Step 1: Pull Data via Amazon Ads API

**All 4 reports are created and downloaded programmatically. No user action needed.**

#### 1a. Calculate Date Range

```
end_date = today - 3 days   (exclude last 2 days per SOP)
start_date = today - 9 days  (7-day window)
date_range = "YYYYMMDD-YYYYMMDD"  (e.g., "20260220-20260226")
```

Tell user: "Pulling PPC data for {start_date} to {end_date} via Amazon Ads API..."

#### 1a.5. Fetch Portfolio Mapping (MANDATORY)

**Call `list_portfolios(marketplace="US")` to get portfolio ID-to-name mapping.**

This returns all portfolios with `portfolioId`, `name`, `state`, `inBudget`, and `budgetPolicy`. Build a lookup dict: `{portfolioId: portfolioName}`.

**Why this matters:** The `sp_campaigns` report now includes `portfolioId` for each campaign. Instead of guessing portfolio membership from campaign names (error-prone), join campaign data with portfolio mapping for accurate portfolio-level grouping.

Store this mapping for use in Step 3 (Parse Campaign Report) and Step 4 (Calculate Portfolio-Level Metrics).

#### 1a.6. Fetch Budget Utilization (MANDATORY)

**Call `get_sp_campaign_budget_usage(campaign_ids="{all enabled campaign IDs}", marketplace="US")` to check budget constraints.**

If you don't have campaign IDs yet (they come from the campaign report), defer this to after Step 1d when campaign data is available. Alternatively, call `list_sp_campaigns(state="ENABLED")` to quickly get all campaign IDs and run budget check in parallel with report generation.

**Parse budget utilization data for each campaign:**
- `budgetUtilization` percentage — how much of daily budget was consumed
- `isConstrained` — whether the campaign hit its budget limit

**Flag any campaign where:**
- `isConstrained = true` AND ACoS < 35% → **Budget Starved** — this campaign is profitable but can't spend its full potential. Money left on the table.
- `isConstrained = true` AND ACoS > 50% → **Budget Wasted** — campaign is hitting budget AND unprofitable.

Store budget utilization data for use in Step 6 (Campaign-by-Campaign Analysis).

#### 1b. Create All 4 Reports (in parallel if possible)

Call `create_ads_report` for each report type:

| # | Call | Params |
|---|------|--------|
| 1 | `create_ads_report` | `report_type="sp_campaigns"`, `date_range="{calculated}"`, `marketplace="US"` |
| 2 | `create_ads_report` | `report_type="sp_search_terms"`, `date_range="{calculated}"`, `marketplace="US"` |
| 3 | `create_ads_report` | `report_type="sp_placements"`, `date_range="{calculated}"`, `marketplace="US"` |
| 4 | `create_ads_report` | `report_type="sp_keywords"`, `date_range="{calculated}"`, `marketplace="US"` |

Each call returns a **report ID**. Save all 4 report IDs.

#### 1c. Poll Report Status

Reports take 1-5+ minutes to generate (search term reports can take longer due to volume).

**Polling strategy:**
1. Wait ~30 seconds, then call `get_ads_report_status(report_id="{id}", marketplace="US")` for each report
2. Check status: `COMPLETED`, `IN_PROGRESS`, or `FAILED`
3. If any still `IN_PROGRESS` → wait another 30 seconds and poll again
4. Repeat up to 10 times (max ~5 minutes total wait)
5. If a report hits `FAILED` → note the failure and continue with the other 3 reports

**Tell user progress:** "Reports generating... Campaign: COMPLETED, Search Terms: IN_PROGRESS, Placement: COMPLETED, Targeting: COMPLETED"

#### 1d. Download Completed Reports

For each `COMPLETED` report, download using the appropriate strategy:

**Campaign, Placement, Targeting reports** (typically < 500 rows):
```
download_ads_report(report_id="{id}", marketplace="US", max_rows=1000)
```
These return data inline — parse directly for analysis.

**Search Term report** (typically 3,000-5,000+ rows — use `save_to_file`):
```
download_ads_report(
    report_id="{id}",
    marketplace="US",
    save_to_file="outputs/research/ppc-weekly/snapshots/{YYYY-MM-DD}/search-term-report.json"
)
```
This writes the full report to disk and returns only a summary (row count, columns, aggregate metrics, 5-row preview). Then **read the saved JSON file** for detailed search term analysis in Step 10.

**Why `save_to_file`:** Without this, 4,000+ search term rows flood the context window. The file-based approach lets you process terms in batches and stay within token budget.

**For all reports:** After downloading, also save campaign/placement/targeting data to the snapshot folder for WoW comparison:
- `outputs/research/ppc-weekly/snapshots/{YYYY-MM-DD}/campaign-report.json`
- `outputs/research/ppc-weekly/snapshots/{YYYY-MM-DD}/placement-report.json`
- `outputs/research/ppc-weekly/snapshots/{YYYY-MM-DD}/targeting-report.json`

#### 1e. Validate Data

After downloading:
- Confirm all 4 reports have data (rows > 0)
- If a report has 0 rows → note: "No data for {report_type} in this period"
- Tell user: "All 4 reports downloaded — {X} campaigns, {Y} search terms, {Z} placement rows, {W} targeting rows. Analyzing now."

#### 1f. CSV Fallback (Manual)

If the API fails for any reason (auth expired, rate limit, service down), fall back to manual:
1. Tell user: "API unavailable — falling back to manual export."
2. Ask user to drop CSV exports into `outputs/research/ppc-weekly/input/`
3. Glob for `outputs/research/ppc-weekly/input/*.*` and auto-detect report types by headers:
   - **Campaign**: Has "Budget" column, no "Customer Search Term" or "Placement"
   - **Search Term**: Has "Customer Search Term" column
   - **Placement**: Has "Placement" column
   - **Targeting**: Has "Targeting" + "Match Type", no "Customer Search Term" or "Budget"

### Step 1g: Fetch DataDive Rank Radar Data (for Rank-Aware PPC Decisions)

**MANDATORY:** Always fetch DataDive Rank Radar data. This replaces ALL "check Data Dive" manual callouts with actual automated rank data.

**Why this matters:** The PPC SOP says never cut bids on a campaign if the keyword's organic rank is improving. Without rank data, we had to flag every decision with "check Data Dive manually." Now we pull it directly.

**API Details:**
- **Base URL:** `https://api.datadive.tools`
- **Auth:** Header `x-api-key` with value from `.env` → `DATADIVE_API_KEY`

**How to fetch:**

1. **List Rank Radars:**
   ```
   GET /v1/niches/rank-radars?pageSize=50
   ```
   Returns all active Rank Radars with ASIN, keywordCount, top10KW, top10SV, top50KW, top50SV.

2. **For each Rank Radar, fetch keyword rankings:**
   ```
   GET /v1/niches/rank-radars/{rankRadarId}?startDate={7daysAgo}&endDate={today}
   ```
   Returns per keyword: `keyword`, `searchVolume`, and `ranks` array with daily `organicRank` and `impressionRank`.

3. **Match Rank Radar ASINs to PPC portfolios:**
   - Cross-reference Rank Radar ASINs with campaign ad group ASINs
   - Each portfolio typically maps to 1-2 hero ASINs

4. **Extract for each keyword tracked in Rank Radar:**

   | Metric | Source Field | Use |
   |--------|-------------|-----|
   | **Organic Rank (today)** | `ranks[-1].organicRank` | Current position |
   | **Organic Rank (7 days ago)** | `ranks[0].organicRank` | WoW rank comparison |
   | **Rank Direction** | Compare first vs last | Improving / Stable / Declining |
   | **Impression Rank** | `ranks[-1].impressionRank` | Sponsored position |
   | **Search Volume** | `searchVolume` | Keyword importance |

5. **Build a rank movement table per portfolio:**
   - Keywords improving (rank going down = better)
   - Keywords declining (rank going up = worse)
   - Keywords stable (< 3 position change)

6. **If DataDive fetch fails** (API error, timeout, rate limit):
   - Note: "DataDive rank data unavailable — rank-aware callouts deferred to manual check"
   - Continue with PPC-only analysis as before
   - Do NOT block the entire analysis

### Step 1h: Fetch Seller Board Data (for TACoS + Profitability Context)

**MANDATORY:** Always fetch Seller Board data to unlock TACoS and profit-level analysis.

1. **Fetch the Daily Dashboard report** using WebFetch on the URL from `.env` → `SELLERBOARD_DAILY_DASHBOARD`
   - URL: `https://app.sellerboard.com/en/automation/reports?id=913d974aa62049cca4493b384553adaf&format=csv&t=9cf6b6e82d14453e89d923b881b333b8`
   - This returns daily aggregate data: total sales, organic sales, PPC sales, ad spend, profit, margin, sessions

2. **Fetch the Sales Detailed report** using WebFetch on the URL from `.env` → `SELLERBOARD_SALES_DETAILED`
   - URL: `https://app.sellerboard.com/en/automation/reports?id=0440a7773b7049e2a359b670a7a172a5&format=csv&t=9cf6b6e82d14453e89d923b881b333b8`
   - This returns per-ASIN data: organic/PPC/sponsored sales split, FBA fees, COGS, net profit, ACOS, sessions

3. **Filter to match the PPC data window** — only use Seller Board rows from the same date range as the 4 PPC exports
4. **Extract key metrics for each ASIN and account-wide:**

   | Metric | Source Column(s) | Use |
   |--------|-----------------|-----|
   | **Total Revenue** (organic + PPC) | SalesOrganic + SalesPPC | TACoS denominator |
   | **Organic Sales** | SalesOrganic | Organic vs paid split |
   | **PPC Sales** | SalesPPC, SalesSponsoredProducts, SalesSponsoredDisplay | Cross-validate with PPC reports |
   | **Ad Spend** | SponsoredProducts + SponsoredDisplay + Google ads + Facebook ads | Total ad spend including non-Amazon |
   | **Net Profit** | NetProfit | Profitability context |
   | **Margin %** | Margin column or NetProfit / Total Sales | Profit health |
   | **COGS** | Cost of Goods | Unit economics |
   | **FBA Fees** | AmazonFees | Fee burden |
   | **Sessions** | Sessions | Traffic context |
   | **Unit Session %** | Unit Session Percentage | Conversion at listing level |

5. **Calculate TACoS:**
   - **TACoS = Total Ad Spend / Total Revenue (organic + paid) × 100**
   - Calculate account-wide AND per-portfolio (match ASINs to portfolios)
   - This is the KPI that was previously impossible without Seller Board

6. **Calculate Organic Sales Ratio:**
   - **Organic Ratio = Organic Sales / Total Sales × 100**
   - Shows PPC dependency — higher organic % = healthier
   - Per portfolio and account-wide

7. **If Seller Board fetch fails** (URL expired, timeout, etc.):
   - Note: "Seller Board data unavailable — TACoS and profitability sections skipped"
   - Continue with PPC-only analysis as before
   - Do NOT block the entire analysis

### Step 2: Load Previous Snapshot (for WoW Comparison)

**MANDATORY:** Always check for previous week's analysis. This is not optional — every report must show how we've improved or worsened compared to last week.

1. Glob for `outputs/research/ppc-weekly/snapshots/*/summary.json`
2. If snapshots exist → load the **most recent** `summary.json` (sort by folder date)
3. **Also check for previous brief:** Glob for `outputs/research/ppc-weekly/briefs/weekly-ppc-analysis-*.md` and load the most recent one (excluding the one being created now). This gives richer context than just the summary.json numbers — it shows what actions were recommended and whether they appear to have been taken.
4. If no snapshots → note this is the first run (no WoW comparison available)
5. Store previous data for comparison in later steps

### Step 3: Parse Campaign Report

1. Parse the campaign data from the API response (or CSV fallback)
2. **Join with portfolio mapping:** For each campaign, look up `portfolioId` in the portfolio mapping from Step 1a.5 to get the portfolio name. Campaigns with no `portfolioId` go into an "Unassigned" group.
3. **Filter OUT** all campaigns with status PAUSED or ARCHIVED
4. Separate campaigns into:
   - **Active with data**: ENABLED campaigns with Spend > $0 or Impressions > 0
   - **Active but dormant**: ENABLED campaigns with $0 spend and 0 impressions
5. Group campaigns by **portfolio name** (using the portfolioId→name mapping, NOT campaign name guessing)
5. For each campaign, classify its type:

#### Campaign Classification

| Type | How to Identify |
|------|----------------|
| **Auto** (SPA) | Targeting = AUTOMATIC |
| **Broad** (SPM) | Manual, broad match — look for "broad" in name |
| **Product Targeting** (PAT) | Manual, product/ASIN targeting — look for "PT" or "PAT" in name |
| **Single Keyword** (SK) | Manual, single keyword — look for "SK" in name |
| **Multi Keyword** (MK) | Manual, multiple keywords — look for "MK" in name |
| **TOS Push** | Look for "TOS" in campaign name |
| **Video** (SB/SBV) | Type = SB or SB2, or "video" in name |
| **Sponsored Display** (SD) | Type = SD |
| **Brand Shield** | Look for "shield" or "brand" + "defense" in name |
| **Catch-all** | Look for "catch" in name, or in a catch-all portfolio |

### Step 4: Calculate Portfolio-Level Metrics

For each portfolio with active campaigns:

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

Then calculate **account-level totals** by summing all portfolios.

### Step 5: Determine Portfolio Stages

Assess each portfolio's stage per the PPC SOP lifecycle:

**Stage 1 — Launch: Initial Traffic**
- **Outcome:** Organic ranking foundation
- **Primary KPI:** Rank movement (profitability NOT required)
- Most campaigns started within last 3 months
- Low total order volume (< 20 orders/week)
- Few campaign types present (Exact SK, Broad SK, Auto Close Match, Phrase)
- Focus on exact and near-exact intent
- Budget is used to force visibility — ranking velocity > efficiency

**Stage 2 — Launch: Targeted Traffic**
- **Outcome:** Indirect ranking benefit + conversion signal
- **Primary KPI:** CVR + Rank stability
- Expanding reach while maintaining relevance (PT, Broad Brand, Auto Substitutes/Complements)
- Still ranking-oriented but conversion data becoming more important
- Begin filtering obvious waste

**Stage 3 — Scale: Maintain Profitability & Brand Defense**
- **Outcome:** Cost-effective traffic
- **Primary KPI:** ACoS + Rank retention
- Defending rankings already achieved
- Campaigns include Brand Defense, SB Video, SD Remarketing, Placement Split Testing
- ACoS discipline is enforced
- Budget reallocated to winners, weak keywords paused/isolated
- Brand defense becomes mandatory

**Stage 4 — Scale: Niche Domination & Reach**
- **Outcome:** Top-of-funnel control
- **Primary KPI:** Impression share + Market coverage
- Campaigns include SB Headline, SB Audience, SD CPM, DSP
- Data is less precise, spend is strategic not reactive
- These campaigns support dominance, not ranking discovery

**Portfolio stages are stored in `context/business.md` under "PPC Portfolio Stages".** Load this table at the start of every analysis. If a portfolio is NOT in the table, ask the user what stage it's in.

**Phase mapping:**
- **General** → Catch-all / Shield (account-wide, use catch-all/shield rules)
- **Launch** → Stage 1-2 (rank velocity > efficiency, ACoS flexibility permitted)
- **Scaling** → Stage 3 (ACoS discipline, defend rankings)

**Stage-specific thresholds:**

| Metric | Launch (Stage 1-2) | Scaling (Stage 3) | General (Catch-All/Shield) |
|--------|-------------------|-------------------|---------------------------|
| **ACoS target** | Flexible (rank > profit) | ~30% (goal, not hard line) | 20-25% |
| **Primary KPI** | Rank velocity + CVR | ACoS + Rank retention | Efficiency |
| **CVR target** | Secondary | ~10% (goal, not hard line) | Monitor only |
| **High ACoS tolerance** | Yes — rank movement justifies | Low — but some compromise is OK | Very low |

**IMPORTANT: The 30% ACoS and 10% CVR are goals, not hard lines.** Not every campaign in every portfolio needs to hit these exactly. Some campaigns/portfolios may reasonably operate above these targets if they provide strategic value (TOS ranking, brand defense, discovery). Use judgment — flag outliers but don't treat every campaign above 30% ACoS as a red flag.

### Step 6: Campaign-by-Campaign Analysis

**Sort campaigns by spend (highest first).**

For EACH active campaign, apply the decision matrix:

#### Core Decision Matrix (ACoS vs CVR)

| ACoS | CVR | Action | Priority |
|------|-----|--------|----------|
| > 40% | < 10% | **Lower bids significantly, consider pausing** | P1 |
| > 40% | >= 10% | **Lower bids/TOS% — targeting is right, too expensive** | P1 |
| 30-40% | < 10% | **Investigate targeting relevance, check search terms** | P2 |
| 30-40% | >= 10% | **Minor bid reduction, monitor** | P2 |
| 20-30% | >= 10% | **Healthy — maintain or scale slightly** | P3 (no action) |
| < 20% | >= 15% | **Top performer — consider increasing budget** | P3 (scale) |
| < 25% | < 10% | **Efficient but low conversion — check relevance** | P2 |

#### Special Campaign Rules

| Campaign Type | Special Rule |
|--------------|-------------|
| **TOS campaigns** | High ACoS can be tolerated IF driving rank movement. Always recommend checking Data Dive before cutting. |
| **New campaigns (< 8 weeks old)** | Focus on CVR as primary metric. Tolerate higher ACoS. Flag as "experimental — needs more data" if < 3 weeks. |
| **Catch-all campaigns** | Stricter ACoS target: 20-25%. Flag if above 25%. |
| **Brand shield** | Low spend is expected and fine. Only flag if ACoS is unusually high. |
| **Video campaigns (SB/SBV)** | Consider DPV (detail page views) as an additional metric if available. |
| **SD campaigns** | Lower CTR is normal. Consider viewable impressions. |
| **0 orders + significant spend (> $10)** | Flag as urgent — bleeding money with no return. |
| **Very low spend (< $1/week) + ENABLED** | Flag as under-bidding. Either increase bids or evaluate if worth keeping. |
| **Running 3+ months with near-zero activity** | Flag as dead campaign — either revive or cut. |

#### Bid Adjustment Framework (per SOP)

When recommending bid changes, use these SOP-defined percentage ranges:

**Bid Increase Criteria:**
- ACoS <25% and rank stagnant/declining → increase bids
- CVR >12% and impression share <50% → increase bids
- Losing TOS placement to competitors on hero keywords → increase bids

| Performance Level | Increase Range |
|-------------------|---------------|
| Strong performers | +19-31% (use irregular amounts, e.g., +22%, +27%, +31%) |
| Moderate performers | +8-16% (e.g., +9%, +13%, +16%) |
| Test increments | +4-11% (e.g., +6%, +8%, +11%) |

**Bid Decrease Criteria:**
- ACoS >40% for 7+ days with no rank improvement → decrease bids
- CVR <6% (indicates poor relevance or listing issue) → decrease bids
- Keyword ranked top 5 organically → reduce paid dependency

| Severity | Decrease Range |
|----------|---------------|
| Severe waste | -28-52% (use irregular amounts, e.g., -31%, -43%, -52%) |
| Marginal efficiency | -13-22% (e.g., -14%, -17%, -22%) |

**IMPORTANT: Never use round/clean percentages** like -30%, -50%, +20%. Always use slightly irregular amounts (e.g., -31%, -48%, +22%) to avoid predictable bid patterns in Amazon's auction.

**Pause Criteria:**
- 50+ clicks, 0 orders (over a 30-60 day window — never based on a single week)
- ACoS consistently >100% with no strategic ranking value (verified over 30+ days)
- Keyword intent completely misaligned with product
- **NEVER pause a campaign based on a single week of zero conversions.** Always verify sustained poor performance over minimum 30 days, ideally 60 days.
- **NEVER negate a search term based on a single week of zero conversions.** Always check a minimum 30-day window before recommending negation. Only negate if the term shows sustained zero conversions AND is clearly irrelevant over the full 30-day window.

**Important:** For TOS campaigns, always check Data Dive for rank movement before decreasing bids — the SOP permits high ACoS if rank is improving.

#### Budget Adequacy Check (per SOP)

Flag campaigns where budget appears inadequate:

| Campaign Priority | Budget Rule | Flag If |
|-------------------|------------|---------|
| **High priority** (SK, Exact Halo) | Budget should be 2-3x avg daily spend | Budget = daily spend (capping out) |
| **Discovery** (Auto, Broad) | Budget should be 1.5x avg daily spend | Budget = daily spend (capping out) |
| **Defense** (Shield, Brand) | Budget must never cap | Any sign of budget capping |

#### ASIN Consolidation Check (per SOP)

Per SOP: "Always drive spend through one main ASIN. Ranking strength comes from concentrated traffic."

For each portfolio, check if spend is split across multiple ASINs (visible in targeting/ad group data):
- If multiple ASINs are receiving significant ad spend → flag for consolidation
- Identify the best-performing ASIN (highest CVR, most orders) → recommend consolidating spend to this ASIN
- Exception: Launch phase where all family ASINs are included to identify best performer

#### Experimental Campaign Cadence (per SOP)

Per SOP: "Launch 1-2 new test campaigns per week."

Check campaign start dates from the campaign report:
- If no campaigns were started in the last 2 weeks → flag: "No new test campaigns launched recently — SOP recommends 1-2 per week"
- Note any campaigns < 14 days old as "In evaluation period" — don't make premature decisions on these
- For campaigns in evaluation: Scale if ACoS <35% and CVR >8%. Pause if ACoS >60% and CVR <5%.

#### Rank-Aware Decision Making (Automated via DataDive API)

**Critical SOP principle:** PPC decisions must consider rank movement, not just ACoS/CVR in isolation.

**DataDive Rank Radar data is now fetched automatically in Step 1g.** Use it to make rank-informed decisions instead of flagging for manual checks.

**How to apply rank data to campaign decisions:**

| Scenario | Without Rank Data | With DataDive Rank Data |
|----------|------------------|------------------------|
| High ACoS SK/TOS campaign | "Check Data Dive" | If `organicRank` improved 3+ positions this week → **MAINTAIN spend** (rank velocity > efficiency). If rank is flat/declining → **Lower bids per matrix.** |
| ACoS 30-45%, campaign gaining traction | "Check Data Dive" | If keyword moved from e.g. #22→#18 → **Maintain — rank is improving.** If stagnant → **Minor bid reduction.** |
| Low ACoS, keyword ranked well | "Verify rank" | If `organicRank` < 10 and improving → **Lower TOS bid -15% per SOP** (organic rank carrying the weight). If rank is slipping → **Hold bids.** |
| Hero keyword losing position | "Flag for review" | If `organicRank` worsened 5+ spots → **P1 ACTION: Increase TOS bid or create dedicated SK.** |

**Rank movement classification:**
- **Improving:** organicRank decreased by 3+ positions (closer to #1) over the 7-day window
- **Stable:** organicRank changed by < 3 positions
- **Declining:** organicRank increased by 3+ positions (further from #1)

**If DataDive data is unavailable:** Fall back to flagging with "DataDive unavailable — check rank manually before acting" for TOS/SK campaigns with high ACoS.

Always include a **"Rank Movement Summary"** section showing keyword rank changes from DataDive alongside PPC performance.

#### CTR as Listing Quality Indicator

Per SOP Section 16: CTR indicates listing quality.

For each campaign, evaluate CTR:
- **CTR > 0.5%**: Normal for SP campaigns
- **CTR < 0.3%**: Flag as potential listing quality issue — main image, title, or price may need improvement
- **CTR declining WoW**: Flag — competitors may have improved their creative or pricing

### Step 7: Structure Check

For each portfolio, verify the mandatory baseline campaign structure per SOP:

| Required | Minimum Count | Check |
|----------|--------------|-------|
| **Auto campaign** | 1 | Present? Active? |
| **Broad campaign** | 1 | Present? Active? |
| **Single Keyword (SK) campaigns** | ~3 | Present? For hero keywords? |
| **Multi Keyword (MK, same root) campaigns** | ~2 | Present? Active? |
| **Product Targeting (PT) campaign** | 1 | Present? Active? |
| **Shield campaign** | 1 (Shield portfolio only) | Present in Shield portfolio? |

**Stage-dependent additions:**
- Stage 2+: Should have PT, Broad Brand, Auto Substitutes/Complements
- Stage 3+: Should have Brand Defense, SB Video, SD Remarketing
- Stage 4: May include SB Headline, SB Audience, SD CPM, DSP

Note any gaps — missing campaign types the portfolio should have based on its stage.

### Step 8: Parse Placement Report

1. Parse placement data from the API response (field: `placementClassification`)
2. Group by portfolio, then by campaign
3. For each campaign, calculate metrics per placement:

| Placement | Metrics to Calculate |
|-----------|---------------------|
| **Top of Search (first page)** | Impressions, Clicks, CTR, Spend, CPC, Orders, Sales, ACoS, CVR |
| **Rest of Search** | Same metrics |
| **Product Pages** | Same metrics |

4. Calculate account-wide placement distribution:
   - What % of total spend goes to TOS vs ROS vs Product Pages?
   - What % of total orders come from each placement?

5. **Read current TOS/ROS/PP modifier percentages** from the `list_sp_campaigns` call. Match each campaign by `campaignId` to attach the current modifiers to the placement performance data.

6. **Classify each campaign's Placement Health** using the same framework as the Bid Recommender (see `ppc-bid-recommender/SKILL.md` → Step 4b for the full classification table). For each campaign, assign one of:

   | Classification | Condition |
   |---|---|
   | **TOS DOMINANT** | TOS is efficient (below stage target) and drives most orders |
   | **TOS EFFICIENT / ROS-PP BLEEDING** | TOS below target, ROS and/or PP significantly above target |
   | **TOS BLEEDING / ROS-PP EFFICIENT** | TOS above target, ROS and/or PP below target |
   | **ALL EFFICIENT** | All placements within stage target |
   | **ALL BLEEDING** | All placements above stage target |
   | **INSUFFICIENT DATA** | Not enough clicks/spend to classify |

   Compare each placement's ACoS against the portfolio's stage target. The **relative performance between placements** determines the classification.

7. Identify placement insights:
   - Campaigns classified TOS EFFICIENT / ROS-PP BLEEDING → recommend lowering default bid (not TOS modifier)
   - Campaigns classified TOS BLEEDING → recommend lowering TOS modifier
   - Campaigns classified ALL BLEEDING → flag as listing/targeting issue, not a bid problem
   - Campaigns where TOS modifier is low but TOS ACoS is efficient → leaving TOS share on the table
   - Campaigns where TOS modifier is very high but TOS ACoS is above target → overpaying for TOS
   - Campaigns with no TOS modifier set (0%) → missing TOS strategy entirely

### Step 9: Parse Targeting Report

1. Parse targeting data from the API response (uses `sp_keywords` preset with `matchType` field)
2. Group by portfolio, then by campaign
3. Separate targets into types:
   - **Keyword targets** (broad, phrase, exact)
   - **ASIN/Product targets** (product targeting expressions)
4. For each target, calculate: Impressions, Clicks, CTR, Spend, CPC, Orders, Sales, ACoS, CVR

5. Identify targeting insights:
   - **High-spend zero-order targets** ($10+ spend, 0 orders): Flag for pausing or bid reduction — apply same logic as search term negation
   - **Top performing targets** (low ACoS, good CVR): Flag for budget increase
   - **Keyword vs ASIN split**: What % of spend/orders comes from keywords vs ASINs?
   - **Match type effectiveness**: How does broad vs phrase vs exact perform across the account?

### Step 10: Parse Search Term Report

1. Parse search term data from the API response (field: `searchTerm`)
2. Cross-reference campaign names against campaign classifications from Step 3
3. Note the match type for each row:
   - Broad match terms → candidates for phrase/exact promotion
   - Auto-discovered terms → candidates for manual campaign migration
   - Exact match terms → already targeted, focus on bid optimization

4. For EACH unique search term, calculate:

| Metric | Formula |
|--------|---------|
| **Total Impressions** | Sum across all campaigns |
| **Total Clicks** | Sum across all campaigns |
| **Total Spend** | Sum across all campaigns |
| **Total Orders** | Sum across all campaigns |
| **Total Sales** | Sum across all campaigns |
| **CTR** | Total Clicks / Total Impressions |
| **CVR** | Total Orders / Total Clicks |
| **ACoS** | Total Spend / Total Sales (if sales > 0) |
| **CPC** | Total Spend / Total Clicks |

5. Classify each search term:

#### NEGATE (Add as negative keyword)

| Condition | Priority | Reasoning |
|-----------|----------|-----------|
| **$10+ spend, 0 orders** | P1 | Bleeding money with zero return |
| **20+ clicks, 0 orders** (per SOP) | P1 | No conversions after significant clicks |
| **$5-10 spend, 0 orders, CTR < 0.3%** | P1 | Low relevance + wasted spend |
| **$5-10 spend, 0 orders, CTR > 0.3%** | P2 | Getting clicks but not converting |
| **ACoS > 100%, 3+ clicks** | P1 | Spending more than earning |
| **ACoS > 3x portfolio target** (per SOP) | P1 | Massively exceeding target with no ranking benefit |
| **ACoS > 70%, 5+ clicks** | P2 | Very unprofitable |
| **Clearly irrelevant term** | P1 | Wrong product/audience entirely |

**Irrelevance signals** (auto-flag for negation):
- Adult/inappropriate terms on kids products
- Wrong product category entirely (e.g., "sewing machine" on a sewing kit)
- Wrong age group (e.g., "adult" terms on kids products, unless the product targets adults)
- Wrong craft type (e.g., "crochet hook" on an embroidery kit)
- Competitor brand names WITH high ACoS (searching for competitor and not converting)
- Single-letter or gibberish terms

#### PROMOTE (Graduate to exact/phrase campaigns)

Per SOP: Promote when **3+ orders with ACoS <40%** and clear buying intent, and keyword not already targeted in an exact campaign.

| Condition | Priority | Action |
|-----------|----------|--------|
| **3+ orders, ACoS <40%, from Auto** (per SOP) | P1 | Add as exact match in manual campaign |
| **3+ orders, ACoS <40%, from Broad** (per SOP) | P1 | Add as phrase or exact match |
| **2 orders, ACoS < 30%, CVR > 15%** | P2 | Strong signal, needs more data |
| **5+ orders, ACoS 30-40%** | P2 | Converting but expensive — control via exact |
| **High CVR (>15%) + reasonable ACoS from broad/auto** | P2 | Move to tighter match type |

**Promotion path:**
- From **Auto** → Add to **Broad or Exact** manual campaign
- From **Broad** → Add to **Phrase or Exact** campaign
- From **Phrase** → Add to **Exact** campaign
- When promoting, also add as **negative exact** in the source campaign to prevent cannibalization
- **Monitor for 7 days before scaling budget** (per SOP)

#### DISCOVER (New keyword opportunities)

| Condition | Signal |
|-----------|--------|
| Converting term NOT in any manual campaign | New keyword to test |
| High impressions + decent CTR but from Auto only | Market demand, worth testing manually |
| Variant/misspelling of known high-performer | Add as separate exact target |
| Seasonal/trending term appearing for first time | Time-sensitive opportunity |
| Long-tail term with strong CVR | Low competition opportunity |

**Stage-specific ACoS thresholds for search term decisions:**

| Portfolio Stage | Negate at ACoS > | Promote at ACoS < |
|-----------------|-------------------|---------------------|
| Stage 1 (Launch Initial) | 3x target / flexible | 50% |
| Stage 2 (Launch Targeted) | 80% (still flexible) | 40% (per SOP) |
| Stage 3 (Scale Profitability) | 50% | 30% |
| Stage 4 (Scale Domination) | 50% | 30% |
| Catch-all | 40% | 25% |

6. **Relevance check against business context:**
   - Check `context/business.md` for product categories — don't negate relevant terms
   - Check `context/search-terms.md` for tracked keywords — don't negate known high-value terms
   - Flag competitor brand names (Kraftlab, Fanzbo, Krafun, etc.) separately — these need human decision

### Step 10b: Get Bid Recommendations for Promote-Tier Keywords

**After identifying P1 Promote keywords in Step 10**, use the Amazon Ads API to get data-driven bid suggestions instead of generic "+10%/-15%" advice.

**For each P1 Promote keyword** (3+ orders, ACoS <40%):
1. Identify the **target campaign and ad group** where the keyword should be promoted to
2. Call `get_sp_bid_recommendations`:
   ```
   get_sp_bid_recommendations(
       campaign_id="{target_campaign_id}",
       ad_group_id="{target_ad_group_id}",
       keywords='[{"keyword": "{search_term}", "matchType": "EXACT"}]',
       marketplace="US"
   )
   ```
3. The API returns `lowBid`, `medBid`, `highBid` — three competitiveness tiers

**Apply these to the Promote recommendations:**

| Bid Level | When to Use | Description |
|-----------|-------------|-------------|
| `lowBid` | Conservative start | Safe starting bid; lower impression share |
| `medBid` | **Recommended default** | Balanced — good impression share without overspending |
| `highBid` | Aggressive push / rank velocity | Maximum competitiveness; use for Launch-phase portfolios or hero keywords losing rank |

**In the Promote table**, replace the generic "Set initial bid at current CPC" with the actual recommended bid:

| Search Term | Recommended Bid | Low / Med / High | Current CPC | Action |
|-------------|----------------|-------------------|-------------|--------|
| {term} | ${medBid} | $X / $X / $X | ${currentCPC} | Add as EXACT at ${medBid} in {campaign} |

**If bid recommendations fail** (campaign/ad group doesn't exist yet, or API error): Fall back to "Set initial bid at current CPC or slightly below" and note the failure.

**Limit:** Only fetch bid recs for the top 10-15 Promote keywords to stay within token budget and rate limits.

### Step 10c: Budget Utilization Analysis

**Using budget utilization data from Step 1a.6**, create a dedicated budget analysis section:

1. **For each campaign in the campaign report**, join budget utilization data:
   - Budget amount (from campaign report `campaignBudgetAmount`)
   - Budget utilization % (from `get_sp_campaign_budget_usage`)
   - ACoS (from campaign report)

2. **Classify each campaign's budget status:**

| Budget Status | Condition | Implication |
|---------------|-----------|-------------|
| **Starved** | Utilization >90% AND ACoS <35% | Profitable campaign being throttled. Increase budget. |
| **Wasteful** | Utilization >80% AND ACoS >50% | Hitting budget limit while being unprofitable. Decrease budget. |
| **Underperforming** | Utilization <30% AND ACoS >40% | Not spending but also not efficient. Needs keyword/creative work. |
| **Healthy** | Utilization 30-90% AND ACoS in target | Properly allocated. Maintain. |
| **Idle** | Utilization <10% | Campaign barely spending. Review bids or keywords. |

3. **Calculate total budget headroom:**
   - Sum of (daily budget - daily spend) across all campaigns = wasted daily capacity
   - Identify top 3 campaigns where budget increase would have highest impact (starved + low ACoS)

4. **Output a Budget Health section** in the report (see output format update below).

### Step 11: Week-over-Week Comparison

If a previous snapshot `summary.json` was loaded in Step 2:

1. Calculate deltas for account-level metrics:
   - Spend: current vs previous, $ change, % change
   - Sales: current vs previous, $ change, % change
   - ACoS: current vs previous, point change
   - ROAS: current vs previous, change
   - Orders: current vs previous, # change, % change
   - CVR: current vs previous, point change
   - Zero-order spend: current vs previous
   - P1 negation count: current vs previous
   - Estimated savings: current vs previous

2. Calculate deltas for each portfolio:
   - Same metrics as above, per portfolio
   - Note portfolios that improved vs worsened
   - Note new portfolios appearing / portfolios going dormant

3. Track previous P1 actions:
   - Compare current P1 list against previous P1 list
   - Note which actions appear to have been addressed (campaign no longer P1)
   - Note which actions are still open (campaign still P1)
   - Note new P1 actions that weren't there last week

4. Highlight key changes:
   - **Top improvements** — biggest ACoS reductions, biggest spend savings
   - **New problems** — campaigns that went from healthy to P1, new bleeders
   - **Trends** — is the account getting better or worse overall?

5. **State of PPC assessment (MANDATORY):**
   Write a clear, honest paragraph assessing the overall state of the PPC account compared to last week. Be specific:
   - Where have we improved? (Name portfolios, campaigns, metrics)
   - Where have we gotten worse or slacked? (Name portfolios, campaigns, metrics)
   - Are previous P1 actions being addressed or are they still open?
   - Overall trend: improving, stable, or declining?
   - What's the single most important thing to fix this week?

   This should read like a manager's weekly check-in — not just data tables, but an honest narrative of what's happening.

### Step 12: Generate Unified Report

Output the full analysis as a structured markdown report following the exact output format below.

### Step 13: Save Snapshot

After generating the report:

1. Create snapshot folder: `outputs/research/ppc-weekly/snapshots/YYYY-MM-DD/`
2. Save all 4 API report datasets as JSON files with standardized names:
   - `campaign-report.json`
   - `search-term-report.json`
   - `placement-report.json`
   - `targeting-report.json`
3. Generate `summary.json` with key metrics (see format below)

**summary.json format:**

```json
{
  "date": "YYYY-MM-DD",
  "data_window": "Feb 4 - Feb 10, 2026",
  "account": {
    "spend": 0.00,
    "sales": 0.00,
    "acos": 0.00,
    "roas": 0.00,
    "orders": 0,
    "clicks": 0,
    "cvr": 0.00,
    "zero_order_spend": 0.00,
    "active_portfolios": 0,
    "active_campaigns": 0,
    "tacos": 0.00,
    "total_revenue": 0.00,
    "organic_sales": 0.00,
    "organic_ratio": 0.00,
    "net_profit": 0.00,
    "profit_margin": 0.00,
    "sessions": 0
  },
  "portfolios": {
    "portfolio-name": {
      "spend": 0.00,
      "sales": 0.00,
      "acos": 0.00,
      "roas": 0.00,
      "orders": 0,
      "cvr": 0.00,
      "stage": "maintenance",
      "status": "HEALTHY"
    }
  },
  "placement": {
    "account_totals": {
      "top_of_search": { "spend": 0.00, "sales": 0.00, "acos": 0.00, "orders": 0, "cvr": 0.00 },
      "rest_of_search": { "spend": 0.00, "sales": 0.00, "acos": 0.00, "orders": 0, "cvr": 0.00 },
      "product_pages": { "spend": 0.00, "sales": 0.00, "acos": 0.00, "orders": 0, "cvr": 0.00 }
    },
    "per_campaign_health": [
      {
        "campaign_id": "...",
        "campaign_name": "...",
        "portfolio": "...",
        "tos_acos": 0.00,
        "ros_acos": 0.00,
        "pp_acos": 0.00,
        "tos_spend_share": 0.00,
        "tos_order_share": 0.00,
        "current_tos_modifier": 0,
        "current_ros_modifier": 0,
        "current_pp_modifier": 0,
        "health": "TOS_DOMINANT",
        "recommended_lever": "tos_modifier"
      }
    ],
    "health_distribution": {
      "tos_dominant": 0,
      "tos_efficient_ros_pp_bleeding": 0,
      "tos_bleeding_ros_pp_efficient": 0,
      "all_efficient": 0,
      "all_bleeding": 0,
      "insufficient_data": 0
    }
  },
  "search_terms": {
    "total_terms": 0,
    "zero_order_terms": 0,
    "zero_order_spend": 0.00,
    "p1_negations": 0,
    "p1_promotions": 0,
    "estimated_savings": 0.00
  },
  "p1_actions": [
    "portfolio | campaign | action description"
  ]
}
```

---

## Output Format

Generate a markdown report with these sections in this exact order:

```markdown
# Weekly PPC Analysis — {YYYY-MM-DD}

**Data Window:** {date range from exports}
**Portfolios Analyzed:** {X active} of {Y total}
**Previous Snapshot:** {YYYY-MM-DD} (or "None — first run")

---

## Week-over-Week Summary

> Only include this section if a previous snapshot exists. If first run, replace with:
> "**First analysis run.** No previous data for comparison. Next week's report will include week-over-week trends."

### Key Metrics

| Metric | This Week | Last Week | Change | % Change |
|--------|-----------|-----------|--------|----------|
| Total Spend | ${X} | ${X} | {+/- $X} | {+/- X%} |
| Total Sales | ${X} | ${X} | {+/- $X} | {+/- X%} |
| Account ACoS | X% | X% | {+/- X pp} | — |
| Account ROAS | X | X | {+/- X} | — |
| Total Orders | X | X | {+/- X} | {+/- X%} |
| Account CVR | X% | X% | {+/- X pp} | — |
| Zero-Order Spend | ${X} | ${X} | {+/- $X} | — |
| TACoS | X% | X% | {+/- X pp} | — |
| Net Profit | ${X} | ${X} | {+/- $X} | {+/- X%} |
| Organic Ratio | X% | X% | {+/- X pp} | — |
| P1 Actions | X | X | {+/- X} | — |

### Top Improvements This Week
- {Portfolio/campaign}: {what improved and by how much}
- {Portfolio/campaign}: {what improved}

### New Problems This Week
- {Portfolio/campaign}: {what worsened or appeared}
- {Portfolio/campaign}: {what worsened}

### Previous P1 Actions Status
- [ ] {action from last week} — **{Addressed / Still Open}**
- [ ] {action from last week} — **{Addressed / Still Open}**

### State of the PPC — Honest Assessment

{2-4 paragraph narrative: Where we improved, where we slacked, what's the trend, what's the #1 priority this week. Be specific — name portfolios and campaigns, don't be vague.}

---

## Account Overview

| Metric | Value |
|--------|-------|
| Total Account Spend | ${X} |
| Total Account Sales | ${X} |
| Account ACoS | X% |
| Account ROAS | X |
| Total Orders | X |
| Total Clicks | X |
| Account CVR | X% |
| Active Portfolios | X |
| Catch-All Portfolios | X |
| Shield Portfolios | X |

**Account-Level Assessment:** {2-3 sentences on overall account health, main issues, and key strengths}

### Red Flag Check (per SOP Section 16.3)

| Red Flag | Current Status |
|----------|---------------|
| CVR < 5% (any portfolio) | {List affected portfolios or "None"} |
| ACoS > 50% for 7+ days (any portfolio) | {List affected portfolios or "None"} |
| Hero keywords dropping (from DataDive) | {List keywords that dropped 5+ spots, or "None"} |
| No new test campaigns in last 2 weeks | {Yes/No — SOP expects 1-2/week} |

### Keyword Rank Movement (from DataDive Rank Radar)

> Only include if DataDive data was successfully fetched. If unavailable, note: "DataDive data unavailable — rank section skipped."

#### Account-Wide Rank Summary

| Metric | Value |
|--------|-------|
| Total Keywords Tracked | {X} across {Y} Rank Radars |
| Keywords in Top 10 | {X} (SV: {X}) |
| Keywords in Top 50 | {X} (SV: {X}) |
| Keywords Improving (7d) | {X} |
| Keywords Declining (7d) | {X} |
| Keywords Stable (7d) | {X} |

#### Top Rank Improvements This Week

| Keyword | Portfolio | Search Vol | Rank 7d Ago | Rank Now | Change | PPC Action Impact |
|---------|-----------|-----------|-------------|----------|--------|-------------------|
| {keyword} | {portfolio} | {sv} | #{old} | #{new} | +{X} | {Maintain spend / Can reduce bids} |

#### Top Rank Declines This Week (P1 Attention)

| Keyword | Portfolio | Search Vol | Rank 7d Ago | Rank Now | Change | PPC Action Needed |
|---------|-----------|-----------|-------------|----------|--------|-------------------|
| {keyword} | {portfolio} | {sv} | #{old} | #{new} | -{X} | {Increase TOS bid / Create SK / Investigate} |

#### Rank vs PPC Spend Correlation

For each portfolio, show whether PPC spend is translating to rank improvements:

| Portfolio | Ad Spend | Keywords Improving | Keywords Declining | Rank ROI Assessment |
|-----------|----------|-------------------|-------------------|---------------------|
| {name} | ${X} | {X} | {X} | {Spend driving rank / Spend not translating / Mixed} |

### TACoS & Profitability (from Seller Board)

> Only include this section if Seller Board data was successfully fetched. If unavailable, note: "Seller Board data unavailable — TACoS section skipped."

| Metric | Value | vs Last Week | Target | Status |
|--------|-------|-------------|--------|--------|
| **TACoS** (Ad Spend / Total Revenue) | X% | {+/- X pp} | <15% | {OK / Above / Red Flag} |
| **Total Revenue** (organic + PPC) | ${X} | {+/- $X} | — | — |
| **Organic Sales** | ${X} (X%) | {+/- $X} | — | — |
| **PPC Sales** | ${X} (X%) | {+/- $X} | — | — |
| **Organic Ratio** | X% | {+/- X pp} | >60% | {Healthy / PPC Dependent / Over-Reliant} |
| **Net Profit** | ${X} | {+/- $X} | — | — |
| **Profit Margin** | X% | {+/- X pp} | — | — |
| **Sessions** | X | {+/- X} | — | — |

**TACoS Interpretation:**
- <10% = Excellent organic strength, PPC is efficient layer
- 10-15% = Healthy balance of paid/organic
- 15-25% = PPC dependency growing, watch organic rankings
- >25% = Over-reliant on PPC — organic strategy needs attention

#### Per-Portfolio TACoS

| Portfolio | Ad Spend | Total Revenue | TACoS | Organic % | Net Profit | Margin |
|-----------|----------|--------------|-------|-----------|------------|--------|
| {name} | ${X} | ${X} | X% | X% | ${X} | X% |

**Profitability Assessment:** {2-3 sentences on overall profit health — which portfolios are profitable, which are being subsidized by others, and whether PPC spend is justified by total revenue growth.}

---

## Portfolio Rankings

### By Spend (where the money goes)

| Rank | Portfolio | Spend | % of Total | ACoS | ROAS | Orders | WoW ACoS | Status |
|------|-----------|-------|------------|------|------|--------|----------|--------|
| 1 | {name} | ${X} | X% | X% | X | X | {+/- X pp} | {HEALTHY / WATCH / NEEDS ATTENTION / RED FLAG / TOP PERFORMER} |

### Efficiency Leaderboard (best ACoS)

| Rank | Portfolio | ACoS | ROAS | Spend | Orders |
|------|-----------|------|------|-------|--------|
| 1 | {name} | X% | X | ${X} | X |

### Volume Leaders (most orders)

| Rank | Portfolio | Orders | Sales | ACoS | Spend |
|------|-----------|--------|-------|------|-------|
| 1 | {name} | X | ${X} | X% | ${X} |

---

## Portfolio-by-Portfolio Analysis

### {Portfolio Name} — {HEALTHY / WATCH / NEEDS ATTENTION / RED FLAG / TOP PERFORMER}

**Stage:** {Stage 1: Launch Initial / Stage 2: Launch Targeted / Stage 3: Scale Profitability / Stage 4: Scale Domination}

| Metric | Value | Target | Status | WoW |
|--------|-------|--------|--------|-----|
| Spend | ${X} | — | — | {+/- $X} |
| Sales | ${X} | — | — | {+/- $X} |
| ACoS | X% | X% | {OK / Above / Well Above} | {+/- X pp} |
| ROAS | X | — | — | — |
| Orders | X | — | — | {+/- X} |
| CVR | X% | 10% | {OK / Below} | {+/- X pp} |
| Active Campaigns | X | — | — | — |

#### Campaign Breakdown

| Campaign | Type | Spend | ACoS | CVR | Orders | Priority |
|----------|------|-------|------|-----|--------|----------|
| {name} | {Auto/Broad/SK/etc.} | ${X} | X% | X% | X | {P1/P2/P3/OK} |

**P1 Actions:**
- {Campaign}: {specific action + reason}

**Placement Snapshot:**
| Placement | Spend | ACoS | CVR | Orders |
|-----------|-------|------|-----|--------|
| Top of Search | ${X} | X% | X% | X |
| Rest of Search | ${X} | X% | X% | X |
| Product Pages | ${X} | X% | X% | X |

**Key Issue:** {1 sentence}
**Quick Win:** {1 sentence}

---

[Repeat for each active portfolio, sorted by spend descending]

---

## Placement Insights (Account-Wide)

### Placement Performance Summary

| Placement | Spend | % of Total | Sales | ACoS | Orders | CVR |
|-----------|-------|------------|-------|------|--------|-----|
| Top of Search | ${X} | X% | ${X} | X% | X | X% |
| Rest of Search | ${X} | X% | ${X} | X% | X | X% |
| Product Pages | ${X} | X% | ${X} | X% | X | X% |

### Per-Campaign Placement Health (top campaigns by spend)

| Campaign | Portfolio | TOS ACoS | ROS ACoS | PP ACoS | TOS Spend% | Current TOS% | Health | Recommended Lever |
|----------|-----------|----------|----------|---------|------------|--------------|--------|-------------------|
| {name} | {portfolio} | X% | X% | X% | X% | X% | {classification} | {TOS modifier / Default bid / Hold / Flag listing} |

**Health Distribution:** {N} TOS Dominant, {N} TOS Eff/ROS Bleed, {N} TOS Bleeding, {N} All Efficient, {N} All Bleeding, {N} Insufficient Data

### TOS Modifier Opportunities

- {Campaign}: TOS is efficient but modifier is low — leaving TOS impression share on the table
- {Campaign}: TOS modifier is very high but TOS ACoS is above target — overpaying for TOS
- {Campaign}: No TOS modifier set (0%) — missing TOS strategy entirely

### ROS/PP Bleed Alerts

- {Campaign}: ROS+PP spend dominates and ACoS is significantly worse than TOS → lower default bid
- {Campaign}: Product Pages spending heavily with poor CVR → investigate targeting

---

## Budget Health (from Budget Utilization API)

> Only include if budget utilization data was successfully fetched in Step 1a.6. If unavailable, note: "Budget utilization data unavailable — budget section skipped."

### Budget-Constrained Campaigns (Money Left on Table)

Campaigns that are **profitable but throttled** — increasing budget here has the highest ROI.

| Campaign | Portfolio | Budget | Utilization | ACoS | Orders | Budget Status | Recommended Budget |
|----------|-----------|--------|-------------|------|--------|---------------|-------------------|
| {name} | {portfolio} | ${X}/day | X% | X% | X | **Starved** | ${X}/day (+X%) |

**Total daily budget headroom wasted: ~${X}/day across {N} starved campaigns.**

### Over-Budget Unprofitable Campaigns

Campaigns hitting budget limits while being unprofitable — reduce or pause.

| Campaign | Portfolio | Budget | Utilization | ACoS | Orders | Action |
|----------|-----------|--------|-------------|------|--------|--------|
| {name} | {portfolio} | ${X}/day | X% | X% | X | Reduce to ${X}/day or pause |

### Budget Reallocation Recommendation

> If we shift ${X}/day from wasteful campaigns to starved campaigns, estimated additional sales: ${X}/week at current conversion rates.

---

## Targeting Insights (Account-Wide)

### Target Type Performance

| Target Type | Spend | % of Total | Sales | ACoS | Orders | CVR |
|-------------|-------|------------|-------|------|--------|-----|
| Keyword (Broad) | ${X} | X% | ${X} | X% | X | X% |
| Keyword (Phrase) | ${X} | X% | ${X} | X% | X | X% |
| Keyword (Exact) | ${X} | X% | ${X} | X% | X | X% |
| Product/ASIN | ${X} | X% | ${X} | X% | X | X% |

### High-Spend Zero-Order Targets (Cut or Reduce)

| # | Target | Campaign | Portfolio | Spend | Clicks | Orders | Action |
|---|--------|----------|-----------|-------|--------|--------|--------|
| 1 | {target} | {campaign} | {portfolio} | ${X} | X | 0 | {Lower bid significantly / Pause} |

### Top Performing Targets (Scale)

| # | Target | Campaign | Portfolio | Spend | ACoS | CVR | Orders | Action |
|---|--------|----------|-----------|-------|------|-----|--------|--------|
| 1 | {target} | {campaign} | {portfolio} | ${X} | X% | X% | X | {Increase budget / Scale} |

---

## Search Term Actions

### P1 — NEGATE IMMEDIATELY

These terms are bleeding budget with zero or terrible return. Add as negative keywords today.

| # | Search Term | Source Campaign | Portfolio | Match | Clicks | Spend | Orders | ACoS | Reason |
|---|-------------|----------------|-----------|-------|--------|-------|--------|------|--------|
| 1 | {term} | {campaign} | {portfolio} | {type} | X | ${X} | 0 | — | {reason} |

**Negation instructions:**
- {Specific instructions for where and how to negate each term or group of terms}

**Total P1 spend recoverable: ~${X}/week**

### P2 — NEGATE SOON (Review First)

| # | Search Term | Source Campaign | Portfolio | Match | Clicks | Spend | Orders | ACoS | Reason |
|---|-------------|----------------|-----------|-------|--------|-------|--------|------|--------|
| 1 | {term} | {campaign} | {portfolio} | {type} | X | ${X} | X | X% | {reason} |

### HIGH-ACOS ACTIVE TERMS

Terms converting but at terrible efficiency. Lower bids significantly or negate.

| # | Search Term | Campaign | Portfolio | Spend | Orders | Sales | ACoS | CVR | Action |
|---|-------------|----------|-----------|-------|--------|-------|------|-----|--------|
| 1 | {term} | {campaign} | {portfolio} | ${X} | X | ${X} | X% | X% | {action} |

### P1 — PROMOTE NOW

High-performing terms to graduate to tighter match types.

| # | Search Term | Source Campaign | Current Match | Orders | Sales | ACoS | CVR | Recommended Bid (Low/Med/High) | Recommended Action |
|---|-------------|----------------|---------------|--------|-------|------|-----|-------------------------------|-------------------|
| 1 | {term} | {campaign} | {auto/broad} | X | ${X} | X% | X% | ${low} / **${med}** / ${high} | Add as EXACT at **${med}** in {target campaign} |

**Bid recommendation source:** Amazon Ads API `get_sp_bid_recommendations` (fetched in Step 10b). Use `medBid` as default. Use `highBid` for Launch-phase portfolios or hero keywords losing rank. Use `lowBid` for conservative testing.

**Promotion checklist:**
- [ ] Add term as exact/phrase in target campaign at recommended bid
- [ ] Add as negative exact in source campaign (prevent cannibalization)
- [ ] Monitor for 1 week after promotion before scaling

### P2 — WATCH & PROMOTE LATER

| # | Search Term | Source Campaign | Current Match | Orders | Sales | ACoS | CVR | Why Watching |
|---|-------------|----------------|---------------|--------|-------|------|-----|--------------|
| 1 | {term} | {campaign} | {type} | X | ${X} | X% | X% | {reason} |

### NEW KEYWORD OPPORTUNITIES

| # | Search Term | Where Found | Impressions | Clicks | Orders | ACoS | Opportunity |
|---|-------------|-------------|-------------|--------|--------|------|-------------|
| 1 | {term} | {campaign} | X | X | X | X% | {why it's interesting} |

### COMPETITOR BRAND TERMS (Human Decision Required)

| # | Search Term | Spend | Orders | ACoS | Recommendation |
|---|-------------|-------|--------|------|----------------|
| 1 | {competitor term} | ${X} | X | X% | {Keep if profitable / Negate if wasteful} |

---

## Consolidated Action To-Do List

### P1 — Act Now (Highest Impact)

| # | Source | Portfolio | Campaign/Term | Action | Spend at Risk |
|---|--------|-----------|---------------|--------|---------------|
| 1 | Campaign | {portfolio} | {campaign} | {action} | ${X} |
| 2 | Search Term | {portfolio} | "{term}" | Negate — {reason} | ${X}/week |
| 3 | Targeting | {portfolio} | {target} | {action} | ${X} |
| 4 | Placement | {portfolio} | {campaign} | {action} | — |

### P2 — Investigate & Adjust
- [ ] {action + context}

### P3 — Monitor / Scale
- [ ] {action + context}

### Structure Gaps
- [ ] {Portfolio}: Missing {campaign type} — {recommendation}

---

## Appendix

### A. Dormant Portfolios

| Portfolio | Status | Recommendation |
|-----------|--------|----------------|
| {name} | ENABLED, $0 spend | {Clean up / Investigate / Revive} |

### B. Dormant Campaigns

| Campaign | Portfolio | Budget | Start Date | Recommendation |
|----------|-----------|--------|------------|----------------|
| {name} | {portfolio} | ${X} | {date} | {Increase bids / Cut / Investigate} |

### C. Structure Check

| Portfolio | Auto | Broad | SK (~3) | MK (~2) | PAT | Shield | Gaps |
|-----------|------|-------|---------|---------|-----|--------|------|
| {name} | {Yes/No} | {Yes/No} | {count} | {count} | {Yes/No} | {N/A or Yes/No} | {Missing types} |

### D. Full Search Term Table

<details>
<summary>Click to expand full search term table (sorted by spend, highest first)</summary>

| Search Term | Campaign | Portfolio | Imp | Clicks | Spend | Orders | Sales | ACoS | CVR | Classification |
|-------------|----------|-----------|-----|--------|-------|--------|-------|------|-----|----------------|
| {term} | {campaign} | {portfolio} | X | X | ${X} | X | ${X} | X% | X% | {Negate/Promote/Keep/Watch} |

</details>

### E. Account Health Assessment

#### Portfolio Stage Distribution

| Stage | Count | Portfolios |
|-------|-------|------------|
| Stage 1: Launch Initial | X | {names} |
| Stage 2: Launch Targeted | X | {names} |
| Stage 3: Scale Profitability | X | {names} |
| Stage 4: Scale Domination | X | {names} |

#### ACoS Distribution

| Range | Count | Portfolios |
|-------|-------|------------|
| < 25% (Excellent) | X | {names} |
| 25-35% (Healthy) | X | {names} |
| 35-50% (Above Target) | X | {names} |
| > 50% (Red Flag) | X | {names} |

#### Budget Concentration

| Top 3 Portfolios | Spend | % of Total |
|-------------------|-------|------------|
| {name} | ${X} | X% |

**Concentration Risk:** {Assessment}
```

---

## Output Location

1. Save the report to: `outputs/research/ppc-weekly/briefs/weekly-ppc-analysis-YYYY-MM-DD.md`
2. Create snapshot at: `outputs/research/ppc-weekly/snapshots/YYYY-MM-DD/`
   - Save all 4 API report datasets as JSON files
   - Generate `summary.json`

---

## Token Budget Strategy

With 4 API reports, data can be large. To stay within 80K tokens:

1. **Campaign + Placement + Targeting reports**: Typically < 200 rows each — process fully
2. **Search term report**: Can be 3,000-5,000+ rows. Focus detailed analysis on terms with **$3+ spend**. Terms below $3 spend get listed in appendix only, not individually analyzed
3. **Previous snapshot**: Load only `summary.json` (not full JSON datasets) for WoW comparison
4. **If token budget is tight**: Prioritize campaign analysis + search term P1 actions. Summarize placement + targeting at account level rather than per-portfolio
5. **API report downloads**: Use `max_rows` parameter to control data volume. Default 500 for campaign/placement/targeting, increase to 5000 for search terms

---

## Execution Checklist

Before delivering the report, verify:

### Data Loading & Processing
- [ ] Portfolio mapping fetched via `list_portfolios()` (Step 1a.5)
- [ ] Budget utilization fetched via `get_sp_campaign_budget_usage()` (Step 1a.6)
- [ ] All 4 API reports created via `create_ads_report` (sp_campaigns, sp_search_terms, sp_placements, sp_keywords)
- [ ] All 4 reports polled to COMPLETED status via `get_ads_report_status`
- [ ] Campaign/placement/targeting reports downloaded via `download_ads_report` with `max_rows=1000`
- [ ] Search term report downloaded via `download_ads_report` with `save_to_file` (full data to disk)
- [ ] Campaign data joined with portfolio mapping via `portfolioId` (not name-guessing)
- [ ] API field names mapped to metric names (cost→Spend, purchases7d→Orders, sales7d→Sales, etc.)
- [ ] ACoS, ROAS, CVR calculated from raw API fields
- [ ] DataDive Rank Radar data fetched (all active Rank Radars + keyword rankings for PPC date window) — or failure noted
- [ ] Rank Radar ASINs matched to PPC portfolios
- [ ] Rank movement calculated per keyword (7-day direction: improving/stable/declining)
- [ ] Seller Board data fetched (Daily Dashboard + Sales Detailed) — or failure noted
- [ ] Seller Board data filtered to match PPC date window
- [ ] TACoS calculated (account-wide + per-portfolio)
- [ ] Only ENABLED campaigns with activity are analyzed (PAUSED/ARCHIVED filtered out)
- [ ] Campaigns sorted by spend (highest first) within each portfolio
- [ ] Data includes CTR calculations (Clicks ÷ Impressions × 100)

### Campaign Analysis
- [ ] Portfolio stages stated and thresholds adjusted accordingly (Stage 1-4 per SOP)
- [ ] Every active campaign has classification, metrics, assessment, and recommendation
- [ ] ACoS evaluated relative to stage-specific targets (not a fixed 30% for all)
- [ ] TOS campaigns flagged for Data Dive check (not auto-recommended for cutting)
- [ ] New campaigns (< 8 weeks) evaluated primarily on CVR
- [ ] Catch-all campaigns use stricter ACoS thresholds (20-25%)

### SOP-Aligned Bid & Budget Checks
- [ ] Bid adjustments use SOP percentage ranges (+20-30%, -30-50%, etc.) — not vague "increase/decrease"
- [ ] Bid recommendations fetched via `get_sp_bid_recommendations()` for top 10-15 Promote keywords (Step 10b)
- [ ] Promote table includes actual low/med/high bid values (not generic "set at CPC")
- [ ] Budget utilization analyzed: Starved, Wasteful, Underperforming, Healthy, Idle classifications (Step 10c)
- [ ] Budget Health section included in report with reallocation recommendations
- [ ] Budget adequacy checked: SK/Exact need 2-3x avg daily CPC, Auto/Broad need 1.5x, Shield never capped
- [ ] ASIN consolidation checked: Flagged if hero ASINs spread thin across 5+ campaigns
- [ ] Experimental campaign cadence: Noted if portfolios are creating new campaigns weekly without learning

### Rank & Red Flag Checks
- [ ] DataDive rank data integrated into campaign decisions (no more "check Data Dive" — use actual rank movement)
- [ ] Rank Movement Summary section included (account-wide + per-portfolio + top improvements + top declines)
- [ ] High-ACoS TOS/SK campaigns evaluated against actual rank direction before recommending bid cuts
- [ ] Hero keyword rank drops identified from Rank Radar data and flagged as P1 actions
- [ ] CTR flagged as listing quality indicator: <0.3% = listing problem, not just bid problem
- [ ] Red flags identified: CVR <5%, ACoS >50% for 7+ days, hero keyword rank drops, impression share losses
- [ ] TACoS calculated from Seller Board data (or unavailability noted)

### Placement & Targeting
- [ ] Placement data analyzed per portfolio and account-wide
- [ ] Targeting data analyzed — high-spend zero-order targets identified

### Search Term Analysis
- [ ] All search terms classified (Negate / Promote / Discover / Keep / Watch)
- [ ] Search terms sorted by spend within each category
- [ ] Negation thresholds applied: ACoS >3x target OR 20+ clicks with 0 orders
- [ ] Promotion threshold applied: ACoS <40% (flat, per SOP) + "Monitor 7 days before scaling"
- [ ] Competitor brand terms separated for human decision (not auto-negated)
- [ ] Business context cross-reference done (no relevant terms accidentally flagged)
- [ ] Estimated savings calculated from P1 negation spend

### Structure & Actions
- [ ] Structure check covers all required campaign types per portfolio: ~3 SK, ~2 MK, Auto, Broad, Shield (if top-seller), plus stage-dependent additions
- [ ] Consolidated action to-do list is prioritized (P1 > P2 > P3) across all data sources
- [ ] Actions are specific (not "optimize this" — say exactly what to do)

### Output & Housekeeping
- [ ] WoW comparison included (or first-run note if no previous snapshot)
- [ ] Snapshot saved with all 4 JSON datasets + summary.json
- [ ] Report saved to correct output location

---

## Error Handling

| Issue | Response |
|-------|----------|
| **API auth failure** (token expired) | Tell user: "Ads API token may need refresh — check ADS_API credentials in .env." Fall back to CSV if user provides exports. |
| **Report creation fails** (400/403/500) | Retry once. If still failing, tell user the specific error and fall back to CSV for that report type. |
| **Report stuck IN_PROGRESS** (>5 min) | Tell user the report is still generating. Offer to continue with available reports or wait longer. Search term reports can take 5+ min for large accounts. |
| **Report FAILED status** | Note the failure, continue with the other 3 reports. Offer to retry or fall back to CSV for the failed report. |
| **Download returns 0 rows** | Note: "No data for {report_type} in this period." Continue with available data. |
| **Rate limiting** (429 error) | Built into MCP server (0.5s between requests). If still rate-limited, wait 60s and retry. |
| No active campaigns with data | Report that the account has no recent activity. Ask if date range is correct. |
| User doesn't know portfolio stages | Estimate from campaign ages and volume, but ask for confirmation. |
| Previous snapshot summary.json is corrupted | Skip WoW comparison, note "Previous snapshot unreadable — treating as first run." |
| Very large search term report (5000+ terms) | Focus on terms with $5+ spend for detailed analysis. Summarize remainder. |
| Duplicate campaign names across portfolios | Always show portfolio name alongside campaign name to disambiguate. |
| Zero-spend report (all campaigns paused) | Report that all campaigns are paused. No analysis needed. |

---

### Step 13b: Calculate 30-Day Trajectories & Detect Inflections

**After saving this week's snapshot, calculate trajectories from snapshot history.**

This replaces the standalone ppc-timeseries-dashboard skill — trajectory analysis is now part of the weekly analysis.

#### 13b-1: Load Snapshot History

Glob for `outputs/research/ppc-weekly/snapshots/*/summary.json`. Load all summaries from the last 90 days. Each contains per-portfolio metrics (spend, sales, acos, orders, cvr, status).

#### 13b-2: Build Per-Portfolio Trajectory

For each portfolio present in 2+ snapshots within the last 30 days:

1. Extract the metric values across snapshot dates
2. Calculate trajectory:
   - `start` = earliest value in 30d window
   - `end` = latest value (this week)
   - `delta` = end - start
   - `trend` = classify using thresholds:

| Metric | Improving | Declining | Stable |
|--------|-----------|-----------|--------|
| ACoS | delta < -2pp | delta > +2pp | abs(delta) <= 2pp |
| Rank_top10 | delta > +2 | delta < -2 | abs(delta) <= 2 |
| Spend, Sales | delta_pct > +10% | delta_pct < -10% | abs(delta_pct) <= 10% |
| CVR | delta > +1pp | delta < -1pp | abs(delta) <= 1pp |

3. Confidence: `high` (4+ snapshots), `medium` (3), `low` (2)

#### 13b-3: Detect Inflection Points

**Only for metrics with 3+ data points.**

For each portfolio metric at this week's value:
1. Compute mean and stdev of prior values
2. z-score = (current - mean) / stdev
3. If `abs(z) > 1.5` → inflection detected
4. If stdev = 0, use absolute thresholds: ACoS >5pp, Rank >3, Spend >25%, CVR >2pp

**Correlate with changes:** For each inflection, check the portfolio's tracker `change_log[]` for events within 7 days prior. Link as correlated events.

#### 13b-4: Add to Report

Add a **Trajectories & Inflections** section to the weekly brief (after WoW Summary, before Account Overview):

```markdown
## 30-Day Trajectories

| Portfolio | ACoS Trend | Rank Trend | Spend Trend | Confidence | Inflections |
|-----------|------------|------------|-------------|------------|-------------|
| Fairy Family | Improving (-6pp) | Surging (+17) | Stable | Low (2 pts) | 2 |

## Inflection Points Detected

### {Portfolio} — {Metric} {Direction}
- **Change:** {prior_avg} → {current} (z={z_score})
- **Correlated actions:** {change_log events within 7d prior}
- **Verdict:** {one-sentence interpretation}
```

If no snapshots exist for trajectory (first run), skip this section with: "Trajectories available after 2+ weekly runs."

#### 13b-5: Update Portfolio Tracker metric_history

For each portfolio, append this week's metrics to `outputs/research/ppc-agent/state/{slug}.json → metric_history[]`:

```json
{
  "date": "YYYY-MM-DD",
  "source": "weekly-analysis",
  "acos": X,
  "spend_7d": X,
  "sales_7d": X,
  "orders_7d": X,
  "cvr": X,
  "rank_top10": X,
  "health_status": "GREEN/YELLOW/RED",
  "note": "Weekly analysis snapshot"
}
```

**Dedup:** Skip if date already exists. Cap at 90 entries.

---

### Step 14: Slack Notification

**Skip this step.** The PPC Agent orchestrator handles Slack notifications via Step 8e after every sub-skill completes.

---

## ⚠️ AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/weekly-ppc-analysis/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Goals:**
- [ ] Goal 1
- [ ] Goal 2

**Result:** ✅ Success / ⚠️ Partial / ❌ Failed

**What happened:**
- (What went according to plan)

**What didn't work:**
- (Any issues, with specifics)

**Is this a repeat error?** Yes/No — if yes, which one?

**Lesson learned:**
- (What to do differently next time)

**Tokens/cost:** ~XX K tokens
```

### 2. Update Issue Tracking

| Situation | Action |
|-----------|--------|
| New problem | Add to **Known Issues** |
| Known Issue happened again | Move to **Repeat Errors**, increment count, **tell the user** |
| Fixed a Known Issue | Move to **Resolved Issues** |

### 3. Tell the User

End your output with a **Lessons Update** note:
- What you logged
- Any repeat errors encountered
- Suggestions for skill improvement

**Do NOT skip this. The system only improves if every run is logged honestly.**
