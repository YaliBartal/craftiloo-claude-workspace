---
name: brand-analytics-weekly
description: Weekly Brand Analytics digest — pulls all 5 BA reports, computes WoW changes, surfaces opportunities and warnings
triggers:
  - brand analytics
  - ba weekly
  - ba digest
  - weekly brand analytics
  - organic search report
output_location: outputs/research/brand-analytics/
---

# Brand Analytics Weekly Digest

**USE WHEN** user says: "brand analytics", "ba weekly", "ba digest", "weekly brand analytics", "organic search report"

**Standalone skill** — runs independently, not routed through PPC Agent.

---

## BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/brand-analytics-weekly/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

Pulls all 5 Brand Analytics report types weekly, saves raw data for historical archive, compares against previous week's data, and produces a digest surfacing click share movements, conversion funnel changes, new keyword opportunities, competitor movements, bundle intelligence, and loyalty trends.

**Cadence:** Weekly (Monday or Tuesday — after Sunday close + 48h SLA)
**Token budget:** <45K tokens, <25 minutes (search_terms streaming adds ~8-10 min)

---

## Efficiency Standards

- **<45K tokens** per run
- **<8 minutes** execution time (BA report processing is the bottleneck — ~5 min for search_terms, ~60s each for others)
- **5 BA API calls** + file reads for previous week comparison
- **No Apify/DataDive calls** — this skill is purely Brand Analytics + context files
- **Save raw data to disk** — other skills read from the archive instead of pulling their own BA reports

---

## Context Management

**Estimated token cost:** 30–45K tokens (within budget — no compaction needed in normal runs)

**Bottleneck:** Search Terms takes ~8-10 min total (5min generation + 2-3min streaming download + 1-2min ijson filter). All other reports take ~45–60s each.

**If context approaches 60% mid-run** (e.g., large search terms report + previous week comparison):
- Save current findings to `outputs/research/brand-analytics/briefs/YYYY-MM-DD-interim.md`
- Compact, then continue at Step 5 (WoW Deltas)

**Before any compact — save to handoff:**
- Which reports are downloaded and their file paths
- Current week vs previous week date ranges confirmed
- Any reports still PENDING

---

## Process

### Step 1: Read Lessons (Mandatory)

Read `.claude/skills/brand-analytics-weekly/LESSONS.md` and apply all past lessons.

### Step 2: Load Context

Read in parallel:

| File | Purpose | Required |
|------|---------|----------|
| `context/sku-asin-mapping.json` | ASIN list for SQP queries | Always |
| `context/business.md` | Portfolio stages, hero ASINs, product names | Always |
| Most recent `outputs/research/brand-analytics/weekly/*/` folder | Previous week's raw data for WoW comparison | If exists |
| Most recent `outputs/research/ppc-weekly/snapshots/*/summary.json` | PPC spend data to cross-reference with organic performance | If exists (<14 days old) |

### Step 3: Pull All 5 BA Reports

**Timing note:** Run on Tuesday or later. Weekly reports cover Sun-Sat and have a 48h SLA after period close. Using `periods_back=2` ensures we get a completed week.

**Launch all 5 reports in parallel:**

#### 3a. Search Catalog Performance (SCP)

```
create_brand_analytics_report(report_name="scp", period="WEEK", periods_back=2)
```
Poll → download. Per ASIN: `impressions`, `clicks`, `cartAdds`, `purchases`, `clickShare`, `conversionShare`.

**No asins param needed.** Returns data for all brand ASINs.

#### 3b. Search Query Performance (SQP)

Get hero ASINs from `context/sku-asin-mapping.json`. Batch into groups of max 200 chars (space-separated).

```
create_brand_analytics_report(report_name="sqp", period="WEEK", periods_back=2, asins="{batch}")
```

If >200 chars of ASINs, run multiple SQP calls (one per batch). Merge results.

Poll → download. Per keyword: `searchQuery`, `impressions`, `clicks`, `cartAdds`, `purchases`, `clickShare`, `conversionShare`.

#### 3c. Search Terms (Top Clicked ASINs)

**⚠️ This is the large report (591MB compressed / 3GB+ decompressed). Use the streaming procedure below — NOT a plain `get_report_document` call.**

**Step 1 — Create the report** (launch alongside the others):
```
create_brand_analytics_report(report_name="search_terms", period="WEEK", periods_back=2)
```

**Step 2 — Poll until DONE** (every 60s, up to 15 attempts — this report takes ~5 min)

**Step 3 — Stream-download as .gz** (set `save_path` ending in `.gz` to trigger byte-streaming mode):
```
get_report_document(
    document_id="...",
    save_path="/tmp/search-terms-{YYYY-MM-DD}.gz"
)
```
This streams ~591MB directly to disk. No decompression in memory. Takes ~2-3 min. Returns the .gz path when done.

**Step 4 — Filter for our ASINs** (run via Bash — takes ~1-2 min, ~50MB RAM):
```bash
python3 /home/yali/workspace/outputs/research/brand-analytics/scripts/filter_search_terms.py \
  /tmp/search-terms-{YYYY-MM-DD}.gz \
  {space-separated list of all active ASINs from sku-asin-mapping.json} \
  --output /home/yali/workspace/outputs/research/brand-analytics/weekly/{YYYY-MM-DD}/search-terms-raw.json
```
Output: only rows where our ASINs appear in positions 1, 2, or 3. Typically ~5,000-20,000 rows.

**Step 5 — Clean up the .gz** (free ~591MB disk):
```bash
python3 -c "import os; os.remove('/tmp/search-terms-{YYYY-MM-DD}.gz')"
```

**Actual row fields (one row per ASIN per term):** `searchTerm`, `departmentName`, `searchFrequencyRank`, `clickedAsin`, `clickedItemName`, `clickShareRank` (1/2/3), `clickShare`, `conversionShare`

**Important:** Each search term appears up to 3 times — once per rank position. Field is `clickedAsin` (not `clickedAsin1/2/3`).

**Processing time: ~8-10 minutes total** (5min report generation + 2-3min download + 1-2min filter).

**If any step fails:**
- Step 3 timeout → retry once; if still failing, skip Search Terms and note in digest
- Step 4 error → check that ijson is installed (`pip install ijson`); check .gz file exists
- Step 5 can be skipped if Bash fails — .gz auto-expires from /tmp on reboot

#### 3d. Market Basket

```
create_brand_analytics_report(report_name="market_basket", period="WEEK", periods_back=2)
```
Poll → download. Per ASIN: co-purchased products with frequency.

#### 3e. Repeat Purchase

```
create_brand_analytics_report(report_name="repeat_purchase", period="WEEK", periods_back=2)
```
Poll → download. Per ASIN: `orders`, `uniqueCustomers`, `repeatCustomerCount`, `repeatPurchaseRevenue`.

**If any report fails:** Continue with available reports. Note which failed in the digest.

### Step 4: Save Raw Data Archive

Save all raw report data to:
```
outputs/research/brand-analytics/weekly/{YYYY-MM-DD}/
├── scp-raw.json
├── sqp-raw.json
├── search-terms-raw.json
├── market-basket-raw.json
├── repeat-purchase-raw.json
└── metadata.json
```

**metadata.json:**
```json
{
  "run_date": "YYYY-MM-DD",
  "period": "WEEK",
  "period_dates": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
  "reports_pulled": ["scp", "sqp", "search_terms", "market_basket", "repeat_purchase"],
  "reports_failed": [],
  "asin_batches": 1,
  "previous_week_available": true
}
```

**This archive is the key output.** Other skills (listing-optimizer, keyword-rank-optimizer, ppc-monthly-review, listing-ab-analyzer) can read from this archive instead of pulling their own BA reports.

### Step 5: Compute WoW Deltas

**Skip if no previous week's data exists** (first run). Show absolute values only.

For each report type, join current week with previous week on the key field (ASIN or keyword) and compute deltas:

#### 5a. SCP Deltas (per ASIN)

| Metric | Calculation |
|--------|-------------|
| `impressions_delta` | current - previous |
| `clicks_delta` | current - previous |
| `purchases_delta` | current - previous |
| `click_share_delta` | current - previous (in percentage points) |
| `conv_share_delta` | current - previous (in percentage points) |
| `ctr_current` | clicks / impressions × 100 |
| `ctr_delta` | current CTR - previous CTR |
| `conv_click_ratio` | conversionShare / clickShare |

#### 5b. SQP Deltas (per keyword)

Same metrics as SCP but per keyword. Additionally:
| Metric | Calculation |
|--------|-------------|
| `cart_rate_current` | cartAdds / clicks × 100 |
| `purchase_rate_current` | purchases / cartAdds × 100 |
| `funnel_bottleneck` | Stage with largest drop-off |
| `new_keyword` | true if keyword not in previous week |

#### 5c. Search Terms Deltas

For each keyword, compare top-3 clicked ASINs:
- **Our ASIN gained position** — we moved up in the top 3
- **Our ASIN lost position** — competitor displaced us
- **New competitor appeared** — ASIN not in previous week's top 3
- **Click share change** — our click share on this keyword rose/fell

#### 5d. Market Basket Deltas

- **New co-purchase** — product pair not in previous week
- **Frequency change** — co-purchase frequency rising/falling

#### 5e. Repeat Purchase Deltas

- **Repeat rate change** — repeatCustomerCount / uniqueCustomers vs previous week

### Step 6: Cross-Reference with PPC Data

If a recent weekly PPC snapshot exists (<14 days old), cross-reference:

| BA Data Point | PPC Cross-Reference | Signal |
|---------------|---------------------|--------|
| High click share + high conv share keyword | Check PPC spend on same keyword | If PPC spend high → candidate for PPC reduction (organic carrying it) |
| Low click share + PPC spending heavily | Check if PPC is compensating | PPC may be necessary; don't reduce |
| New high-volume keyword appearing in SQP | Check if we target it in PPC | If not → REDIRECT opportunity for Rank Optimizer |
| Click share dropping on hero keyword | Check if PPC spend also dropped | Correlate: did we cut PPC too much, or is it competitive pressure? |

Add a `ppc_cross_ref` field to each keyword with: `ppc_spend_7d`, `ppc_signal` (one of: "PPC redundant", "PPC needed", "PPC opportunity", "No PPC data").

### Step 7: Generate Weekly Digest

**Output file:** `outputs/research/brand-analytics/briefs/{YYYY-MM-DD}-ba-weekly.md`

```markdown
# Brand Analytics Weekly Digest — {YYYY-MM-DD}

**Period:** {week start} to {week end}
**Reports pulled:** {N} of 5 ({list failed if any})
**WoW comparison:** {Available / First run — no baseline}
**Data source:** Amazon Brand Analytics (first-party data, not estimates)

---

## Executive Summary

{3-5 bullet points:}
- Overall organic search health (impressions/clicks trending up or down)
- Biggest click share gain this week
- Biggest click share loss this week
- Notable conversion funnel change
- Top actionable recommendation

---

## Click Share Movers

Keywords where our click share changed >2 percentage points.

### Gaining Click Share

| Keyword | Portfolio | Click Share | Delta | Conv Share | Delta | PPC Spend | Signal |
|---------|-----------|------------|-------|------------|-------|-----------|--------|
| {kw} | {port} | X% | +X pts | X% | +X pts | ${X}/wk | {signal} |

### Losing Click Share

| Keyword | Portfolio | Click Share | Delta | Conv Share | Delta | PPC Spend | Signal |
|---------|-----------|------------|-------|------------|-------|-----------|--------|
| {kw} | {port} | X% | -X pts | X% | -X pts | ${X}/wk | {signal} |

**Action items:**
- {kw losing share}: {recommended action — increase PPC, check listing, investigate competitor}
- {kw gaining share}: {recommended action — reduce PPC if PPC redundant, or maintain momentum}

---

## Conversion Funnel Alerts

Keywords where Conv/Click Ratio dropped below 0.8 or changed significantly WoW.

| Keyword | Portfolio | CTR | Cart Rate | Purchase Rate | Conv/Click Ratio | WoW Change | Bottleneck |
|---------|-----------|-----|-----------|---------------|-----------------|------------|------------|
| {kw} | {port} | X% | X% | X% | {X}x | {delta} | {clicks/carts/purchases} |

**Funnel diagnosis:**
- **CTR problem** ({N} keywords): Title/image not compelling → flag for Listing Optimizer
- **Cart Rate problem** ({N} keywords): Bullets/price not convincing → check pricing + bullet copy
- **Purchase Rate problem** ({N} keywords): Checkout friction or competitor undercut → investigate

---

## New Keyword Opportunities

Keywords appearing for the first time this week with meaningful volume.

| Keyword | Impressions | Clicks | Purchases | Conv Rate | In PPC? | Action |
|---------|------------|--------|-----------|-----------|---------|--------|
| {kw} | {N} | {N} | {N} | X% | {Yes/No} | {Add to PPC / Monitor / Already targeted} |

---

## Competitor Movements (Search Terms)

Changes in top-3 clicked ASINs for our hero keywords.

| Keyword | Position | Previous ASIN | Current ASIN | Change | Our Click Share Impact |
|---------|----------|--------------|-------------|--------|----------------------|
| {kw} | #1 | {our ASIN} | {competitor} | Lost #1 | -X pts |
| {kw} | #3 | {competitor A} | {competitor B} | New entrant | Neutral |

**Competitor alert threshold:** Flag if a single competitor gained >5% click share on any of our hero keywords.

---

## Bundle Intelligence (Market Basket)

Products most frequently bought together with ours.

### Top Co-Purchased Products

| Our Product | Co-Purchased Product | Frequency | New? | Opportunity |
|-------------|---------------------|-----------|------|-------------|
| {ASIN} | {product name/ASIN} | {N} times | {Y/N} | {Bundle / Cross-sell PPC / Listing mention} |

### New Co-Purchase Patterns

{Any product pairs that appeared this week but not last week — emerging bundle opportunities}

---

## Customer Loyalty Trends (Repeat Purchase)

| Product | Portfolio | Unique Customers | Repeat Rate | WoW Change | Revenue from Repeats | Signal |
|---------|-----------|-----------------|-------------|------------|---------------------|--------|
| {name} | {port} | {N} | X% | {+/- X pts} | ${X} | {Rising loyalty / Declining / Stable} |

**Insights:**
- **Rising loyalty:** {products} — consider Subscribe & Save, justify higher PPC ACoS
- **Declining loyalty:** {products} — investigate product quality, review complaints
- **S&S candidates** (>30% repeat): {products}

---

## Portfolio Organic Health (SCP)

Per-ASIN organic search funnel for the full portfolio.

| Product | Portfolio | Impressions | WoW | Clicks | WoW | Purchases | WoW | CTR | Conv Rate |
|---------|-----------|------------|-----|--------|-----|-----------|-----|-----|-----------|
| {name} | {port} | {N} | {+/-X%} | {N} | {+/-X%} | {N} | {+/-X%} | X% | X% |

**Overall organic trend:** {Impressions up/down X%, Clicks up/down X%, Purchases up/down X%}

---

## PPC vs Organic Efficiency

*Only shown if recent PPC data available.*

| Keyword | Organic Click Share | Organic Conv Share | PPC Spend/wk | Recommendation |
|---------|--------------------|--------------------|-------------|----------------|
| {kw} | X% (strong) | X% (strong) | ${X} | Reduce PPC — organic carrying it |
| {kw} | X% (weak) | X% (weak) | ${X} | Maintain PPC — organic needs support |
| {kw} | N/A (not targeted) | N/A | $0 | Consider PPC — high organic potential |

---

## Data Confidence

| Report | Status | Rows | Notes |
|--------|--------|------|-------|
| SCP | {Success/Failed} | {N} ASINs | |
| SQP | {Success/Failed} | {N} keywords | {N} ASIN batches |
| Search Terms | {Success/Failed} | {N} keywords | |
| Market Basket | {Success/Failed} | {N} pairs | |
| Repeat Purchase | {Success/Failed} | {N} ASINs | |

---

*Generated by Brand Analytics Weekly Digest — {YYYY-MM-DD}*
*Data source: Amazon Brand Analytics (first-party, not estimated)*
```

### Step 8: Save Digest Snapshot (Machine-Readable)

Save a JSON snapshot alongside the brief for other skills to consume:

`outputs/research/brand-analytics/weekly/{YYYY-MM-DD}/digest-snapshot.json`

```json
{
  "run_date": "YYYY-MM-DD",
  "period": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
  "previous_week": "YYYY-MM-DD",
  "click_share_movers": {
    "gaining": [{"keyword": "", "portfolio": "", "click_share": 0, "delta": 0, "conv_share": 0, "ppc_signal": ""}],
    "losing": [{"keyword": "", "portfolio": "", "click_share": 0, "delta": 0, "conv_share": 0, "ppc_signal": ""}]
  },
  "funnel_alerts": [{"keyword": "", "portfolio": "", "conv_click_ratio": 0, "wow_change": 0, "bottleneck": ""}],
  "new_keywords": [{"keyword": "", "impressions": 0, "purchases": 0, "in_ppc": false}],
  "competitor_movements": [{"keyword": "", "position": 0, "previous_asin": "", "current_asin": "", "our_click_share_impact": 0}],
  "bundle_opportunities": [{"our_asin": "", "co_purchased_asin": "", "frequency": 0, "is_new": false}],
  "loyalty_trends": [{"asin": "", "portfolio": "", "repeat_rate": 0, "wow_change": 0}],
  "portfolio_organic_health": [{"asin": "", "portfolio": "", "impressions": 0, "impressions_wow": 0, "clicks": 0, "purchases": 0}],
  "ppc_efficiency": [{"keyword": "", "organic_click_share": 0, "organic_conv_share": 0, "ppc_spend_7d": 0, "recommendation": ""}],
  "summary": {
    "total_impressions": 0,
    "total_clicks": 0,
    "total_purchases": 0,
    "impressions_wow_pct": 0,
    "clicks_wow_pct": 0,
    "purchases_wow_pct": 0,
    "keywords_gaining_share": 0,
    "keywords_losing_share": 0,
    "funnel_alerts_count": 0,
    "new_keywords_count": 0,
    "competitor_alerts_count": 0,
    "reports_succeeded": 5,
    "reports_failed": 0
  }
}
```

### Step 9: Post Notifications

Read `.claude/skills/notification-hub/SKILL.md` → use the recipe below.

**Channel:** `#claude-product-updates`
**Format:**
```
:mag: *Brand Analytics Weekly* — {date range}

*Organic search:* {impressions_wow_pct}% impressions | {clicks_wow_pct}% clicks | {purchases_wow_pct}% purchases

*Click share:*
:chart_with_upwards_trend: Gaining: {N} keywords ({top keyword +X pts})
:chart_with_downwards_trend: Losing: {N} keywords ({top keyword -X pts})

*Alerts:*
- Funnel problems: {N} keywords
- Competitor movements: {N} keywords
- New opportunities: {N} keywords

*Loyalty:* {top insight from repeat purchase data}

:memo: Full digest → outputs/research/brand-analytics/briefs/
```

**Alert escalation to `#claude-alerts`:**
- Any hero keyword losing >5% click share → alert
- Any competitor gaining >10% click share on a hero keyword → alert
- Organic purchases dropping >20% WoW across account → alert

If Slack MCP is unavailable, skip and note in run log.

---

## Error Handling

| Issue | Response |
|-------|----------|
| SQP report fails | Continue with SCP (provides ASIN-level funnel). Note: "SQP unavailable — keyword-level analysis limited to Search Terms report" |
| Search Terms stream-download fails | Retry once with fresh `get_report_document` call (use same document_id — URL stays valid). If still failing, continue without Search Terms and note in digest. |
| Search Terms filter script fails | Check ijson installed. Check .gz file exists and is non-zero size. If unrecoverable, continue without competitor ASIN data. |
| Search Terms report fails (other) | Continue with SQP for keyword data. Note: "Search Terms unavailable — competitor click share analysis skipped" |
| Market Basket report fails | Skip "Bundle Intelligence" section |
| Repeat Purchase report fails | Skip "Customer Loyalty Trends" section |
| SCP report fails | Critical — this is the core ASIN-level data. Note prominently: "SCP unavailable — portfolio organic health section skipped" |
| All reports fail | Cannot run. Tell user: "Brand Analytics API unavailable. Try again later." |
| No previous week data | First run — show absolute values, skip all WoW deltas. Note: "First run — WoW comparisons will be available next week" |
| No ASINs in sku-asin-mapping | Skip SQP. Other 4 reports still work. |
| >200 chars of ASINs for SQP | Batch into multiple SQP calls. Merge results. |
| PPC weekly snapshot >14 days old | Skip "PPC vs Organic Efficiency" section. Note: "PPC data stale — run weekly PPC analysis for cross-reference" |
| Report returns 0 rows | Note: "Report returned empty — may indicate data not yet available for this period" |
| `periods_back=2` returns same period as last run | Skip — data already archived. Note: "No new weekly period available yet" |

---

## AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/brand-analytics-weekly/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Result:** Success / Partial / Failed

**Period covered:** {week start} to {week end}
**Reports pulled:** {N} of 5 ({list any failed})
**WoW comparison:** {Available / First run}
**Click share movers:** {N} gaining, {N} losing
**Funnel alerts:** {N}
**New keywords:** {N}
**Competitor movements:** {N}

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
