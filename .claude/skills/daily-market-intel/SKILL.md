---
name: daily-market-intel
description: Daily tracking of our hero products' BSR and rank vs competitors
triggers:
  - market check
  - morning market
  - how are my products doing
  - market intel
  - daily market
  - product pulse
output_location: outputs/research/market-intel/
baseline_date: 2026-02-11
---

# Daily Market Intelligence

**First:** Read `.claude/skills/daily-market-intel/LESSONS.md`. Check Known Issues and Repeat Errors. If you hit a Repeat Error, tell the user: _"⚠️ Repeat issue (×N): [description]"_

---

## Core Purpose

**This skill tracks: Are we improving or declining?**

Every daily report answers:
1. Current BSR and rank
2. Position vs competitors
3. Change vs yesterday and vs baseline (2026-02-11)

---

## Sales Data Rules

- **Our products:** Seller Board `get_sales_detailed_7d_report` actuals (SB_Rev_7d, SB_Units_7d, SB_Profit_7d). DataDive JS estimates are 2-10x inflated — never use for our products.
- **Competitors:** DataDive `sales` field (JS Est.) — label as "JS Est." in tables
- **Sort:** Unified product table by SB actual 7-day revenue (highest → lowest)
- **BSR:** Tracked for trend direction only, not sales estimation

---

## File Organization

```
market-intel/
├── briefs/YYYY-MM-DD.md     # Daily reports
├── snapshots/YYYY-MM-DD.json # Raw data for comparison
├── scripts/                   # Automation scripts
└── baseline.json              # Baseline snapshot (2026-02-11)
```

---

## Architecture

**Six data sources, fetched by 6 parallel agents:**

| # | Source | Provides | Time |
|---|--------|----------|------|
| 1 | **SP-API** (Catalog/Pricing/Inventory) | Hero BSR, subcategory rank, price, stock levels | ~15s |
| 2 | **SP-API Orders** | Yesterday's real-time revenue + units | ~10s |
| 3 | **DataDive Rank Radar** | Our keyword rankings (500+ keywords, 10 radars) | ~115s |
| 4 | **DataDive Competitors** | Competitor sales/revenue (JS Est.), rating, reviews (11 niches) | ~84s |
| 5 | **Apify** | 20-keyword battleground + 34-ASIN competitor BSR scan | ~60s |
| 6 | **Seller Board** | 7-day aggregate financials + per-ASIN actuals | ~18s |
| 6b | **Brand Analytics SCP** (optional) | Search funnel: impressions → clicks → carts → purchases | ~60s |

**Wall-clock bottleneck:** SP-API catalog+pricing (~2 min). Launch all agents in parallel.

### Data Source Priority

| Data Need | Primary | Fallback |
|-----------|---------|----------|
| Hero BSR + price | SP-API `get_catalog_item` + `get_competitive_pricing` | DataDive competitors |
| Yesterday's revenue/units | SP-API `get_orders(date=yesterday)` | Seller Board (note 2-day lag) |
| Our 7-day revenue/units/profit | Seller Board `get_sales_detailed_7d_report` | SP-API Orders total |
| Rating + reviews (all products) | DataDive Competitors | Previous snapshot |
| Our keyword rankings | DataDive Rank Radar | — |
| Competitor BSR (real-time) | Apify saswave scan | DataDive competitor BSR |
| Keyword battleground + badges | Apify axesso keyword scan | Previous snapshot (carry forward) |
| 7-day profit, margin, TACoS | Seller Board dashboard | — |

### Data Freshness Rules

| Data Age | Rule |
|----------|------|
| Same day / yesterday | Include freely |
| 2+ days old (day-specific) | Exclude — stale and misleading |
| 7-day aggregates | OK even with 2-day lag |

**Seller Board lags ~2 days.** Show 7-day aggregates only. Use SP-API Orders for yesterday's data.

### Agent Output Compression

Each background agent must return **<5K tokens** to main context:
1. Omit null/empty fields
2. No raw API dumps — process inside agent, return only extracted values
3. Apify: return only `keyword_battleground`, `badges_found`, `new_competitors`, `competitor_bsr`
4. Rank Radar: return top 20 keyword movements + per-product summary
5. DataDive Competitors: top 4 competitors per niche + hero ratings/reviews
6. SP-API: return only BSR, subcategory rank, category, price, stock per ASIN
7. Seller Board: per-ASIN 7-day totals (rev, units, profit) for hero ASINs only

### Performance Targets

| Metric | Target |
|--------|--------|
| Total tokens | <110K |
| Wall-clock time | <5 min |
| Apify cost/day | ~$1.95 |
| SP-API calls | ~28 (13 catalog + 13 pricing + 1 inventory + 1 orders) |

---

## Step 1: SP-API — Hero Product BSR, Price, Inventory

**Extracts:** BSR, subcategory rank, category name, current price, stock levels.
**Tools:** `get_catalog_item`, `get_competitive_pricing`, `get_fba_inventory`
**Rate limit:** 0.5s between calls (built into MCP server)

**How to fetch:**
1. Load 13 hero ASINs from `context/hero-products.md`
2. For each hero ASIN: call `get_catalog_item(asin=ASIN)` + `get_competitive_pricing(asin=ASIN)`
3. Call `get_fba_inventory(asin_filter="comma-separated hero ASINs")` — single call
4. Flag `Fulfillable = 0` as OOS. "NOT FOUND IN FBA INVENTORY" = investigate.

**Note:** SP-API does NOT return rating or review count — those come from DataDive Competitors (Step 3).

---

## Step 2: DataDive Rank Radar — Our Keyword Rankings

**PRIMARY source for keyword ranking data.** Replaces old Apify keyword search for rank tracking.
**API:** `get_rank_radar_data` per radar. Rate limit: 1.1s between requests.

### Active Radars (fetch these only)

- **B08DDJCQKF** (Cross Stitch Backpack Charms) — always include (user requirement)
- B09X55KL2C (Embroidery Kids) — 55 keywords
- B0DC69M3YD (Embroidery Adults) — 67 keywords
- B09WQSBZY7 (Fairy Sewing Kit) — 87 keywords
- B096MYBLS1 (Dessert Sewing Kit) — 50 keywords
- B08FYH13CL (Latch Hook Pencil Cases) — 53 keywords
- B0F8DG32H5 (Knitting Cat & Hat) — 81 keywords
- B09THLVFZK (Mini Fuse Beads) — 18 keywords
- B07D6D95NG (10mm Big Fuse Beads) — 38 keywords
- B0FQC7YFX6 (Princess Lacing Card) — 52 keywords

**Skip:** B092SW839H, B0F8QZZQQM, B09HVDNFMR, B0B1927HCG, B0FHMRQWRX, B0DKD2S3JT (low value / non-hero)

### How to fetch

1. Call `list_rank_radars(pageSize=50)` to get all radars
2. Match to active ASINs above using the `asin` field
3. For each matched radar: `get_rank_radar_data(rankRadarId, startDate=yesterday, endDate=today)`

**CRITICAL:** Fetch ALL keywords per radar — do NOT cap at 50. Radars have 18-87 keywords each. Fetch all pages if paginated. Top10/top50 counts must reflect the FULL keyword set.

### Extract per keyword
- `keyword`, `searchVolume`, `ranks[].organicRank`, `ranks[].impressionRank`
- Calculate change vs yesterday

**Report output:** Top 20 movements by impact (search volume × rank change).

---

## Step 3: DataDive Competitors — Sales, Rating, Reviews

**Provides:** JS sales/revenue estimates, rating, reviewCount for all products (hero + competitor). Primary source for rating/reviews since SP-API doesn't return them.
**API:** `get_niche_competitors(nicheId, pageSize=4)` — top 4 per niche, sorted by sales desc.
**Rate limit:** 1.1s between requests.

### Niche IDs (11 active)

| Niche ID | Label | Hero Products |
|----------|-------|---------------|
| u1y83aQfmK | Kids Cross Stitch Kit | B08DDJCQKF, B0F6YTG1CH |
| gfot2FZUBU | Embroidery Stitch Practice Kit | B0DC69M3YD, B09X55KL2C |
| Er21lin0KC | Beginners Embroidery Kit for Kids | B09X55KL2C |
| RmbSD3OH6t | Sewing Kit for Kids | B09WQSBZY7, B096MYBLS1 |
| 3qbggwOhO2 | Latch Hook Kits for Kids | B08FYH13CL, B0F8R652FX |
| AY4AlnSj9g | Mini Perler Beads | B09THLVFZK |
| O6b4XATpTj | Loom Knitting | B0F8DG32H5 |
| Aw4EQhG6bP | Lacing Cards for Kids | B0FQC7YFX6 |
| 5IGkCmOM0h | Needlepoint Pouch Kit | B09HVSLBS6 |
| kZRreyE7kJ | Cross Stitch Kits (broad) | B08DDJCQKF, B09X55KL2C |
| WFV3TE3beK | Fuse Beads | B07D6D95NG |

**Retired niches (skip):** `b4Nisjv3xy`, `VqBgB5QQ07`

**Extract per competitor:** asin, bsr, sales, revenue, price, rating, reviewCount, kwRankedOnP1. Omit null fields.

**Hero rating/reviews:** Our hero products appear in niche competitor lists — extract their rating + reviewCount here. If missing, carry forward from previous snapshot.

---

## Step 4: Apify — Keyword Battleground + Competitor BSR

This agent runs TWO parallel Apify jobs:

### 4A: Keyword Scan (20 keywords)

**Actor:** `axesso_data/amazon-search-scraper`
**Cost:** ~$0.09/keyword × 20 = ~$1.80
**Provides:** Keyword battleground (us vs competitor positions), badge tracking (OP/AC), new competitor detection

**Input:** `{"input": [{"keyword": "...", "country": "US"}]}` — one keyword per actor call, all 20 launched async.

**Key gotcha:** `searchResultPosition` is **0-indexed** — add 1 for display.

#### Keywords (20 total)

| # | Category | Keyword |
|---|----------|---------|
| 1 | Cross Stitch | embroidery kit for kids |
| 2 | Cross Stitch | cross stitch kits for kids |
| 3 | Cross Stitch | cross stitch for kids |
| 4 | Embroidery Kids | kids embroidery kit |
| 5 | Embroidery Adults | embroidery kit for beginners |
| 6 | Sewing | sewing kit for kids |
| 7 | Sewing | kids sewing kit |
| 8 | Latch Hook | latch hook kits for kids |
| 9 | Latch Hook | latch hook pillow kit |
| 10 | Fuse Beads | mini perler beads |
| 11 | Fuse Beads | perler beads |
| 12 | Fuse Beads | mini fuse beads |
| 13 | Knitting | loom knitting kit |
| 14 | Knitting | loom knitting |
| 15 | Knitting | knitting kit for kids |
| 16 | Knitting | knitting kit for beginners |
| 17 | Lacing Cards | lacing cards |
| 18 | Lacing Cards | lacing cards for kids ages 3-5 |
| 19 | Lacing Cards | lacing cards for kids ages 4-8 |
| 20 | Needlepoint | needlepoint kits for kids |

#### Agent processing (inside agent, not main context)

1. For each keyword result, match ASINs against hero list (`context/hero-products.md`) and competitor list (`context/competitors.md`)
2. Record positions of all matched ASINs → build `keyword_battleground`
3. Our products with badges → `badges_found`
4. Unknown ASINs in **top 5** → `new_competitors` (top 10 is too noisy)
5. Omit tracked ASINs not found in results (don't include with position: null)

**New competitor rules:** Flag if NOT in hero/competitor lists AND in top 5. If seen in 2+ consecutive runs, suggest adding to `context/competitors.md`.

#### Agent output format

```json
{
  "keyword_battleground": [
    {"category": "...", "keyword": "...", "search_volume": 13067,
     "positions": [{"asin": "...", "brand": "...", "position": 1, "is_hero": true}]}
  ],
  "badges_found": [{"asin": "...", "keyword": "...", "badge": "Overall Pick"}],
  "new_competitors": [{"asin": "...", "brand": "...", "keyword": "...", "position": 3}],
  "keyword_rankings": [
    {"keyword": "...", "our_asin": "...", "our_position": 9,
     "top_3": [{"position": 1, "asin": "...", "brand": "...", "badge": "..."}]}
  ]
}
```

Never return the raw product list array.

### 4B: Competitor BSR Scan

**Actor:** `saswave~amazon-product-scraper`
**Cost:** ~$0.15/run
**Provides:** Real-time BSR for all tracked competitor ASINs (solves DataDive BSR gap)

**Input:** Load all competitor ASINs from `context/competitors.md`. Pass as:
```json
{"asins": ["B08T5QC9FS", "B0B7JHN4F1", ...], "amazon_domain": "www.amazon.com"}
```

**CRITICAL:** Must include `amazon_domain: "www.amazon.com"` or actor crashes with KeyError.

**Extract per ASIN:** `bsr` (from `bestsellerRanks[0].rank` — comma-formatted string), `bsr_category`, `rating`, `reviews`. Ignore `price` (returns EUR due to locale issue).

**Agent output format:**
```json
{
  "competitor_bsr": {
    "B08T5QC9FS": {"bsr": 26473, "category": "Arts, Crafts & Sewing", "rating": 4.2, "reviews": 1353}
  }
}
```

### 4C: Brand Analytics SCP (Optional)

If tokens allow, fetch SCP: `create_brand_analytics_report(report_name="scp", period="WEEK", periods_back=2 on Sun/Mon else 1)`. Poll `get_report_status` every 15s (max 8×), then `get_report_document`.
Adds per-ASIN funnel: impressions → clicks → carts → purchases + click/conversion share.
If fetched, add columns to Our Products table. If failed, continue without — note in report.

---

## Step 5: Seller Board — 7-Day Aggregates + Per-ASIN Actuals

**Tools:** `get_daily_dashboard_report` + `get_sales_detailed_7d_report`
**SB lags ~2 days.** Extract 7-day sums only, no single-day metrics. Always note the date range.

### 5A: Dashboard (7-day aggregates)

Sum last 7 available days: NetProfit, Margin (avg), Ad Spend (SponsoredProducts + Display + Brands + Video), TACoS (Ad Spend / Revenue × 100), Revenue (SalesOrganic + SalesPPC).

### 5B: Sales Detailed 7D (per-ASIN actuals)

Uses 7-day window report (~460 rows) instead of 30-day (~2,335 rows).

**How to extract:**
1. Filter to `Marketplace = Amazon.com` only
2. For each hero ASIN, sum across all SKUs and all 7 days:
   - `SB_Rev_7d` = SUM(SalesOrganic + SalesPPC)
   - `SB_Units_7d` = SUM(UnitsOrganic + UnitsPPC)
   - `SB_Profit_7d` = SUM(NetProfit)
3. Daily avg = divide by 7
4. Note date range (e.g., "Mar 2-8")

**If SB fails:** Note in report, fall back to DataDive JS Est. for unified table. Continue with other data.

---

## Step 6: SP-API Orders — Yesterday's Revenue

**Tool:** `get_orders(date="YYYY-MM-DD")` where date = yesterday. Auto-paginates.

**Extract:** Total orders, total units (shipped + pending), shipped revenue.

**Caveat:** Revenue includes marketplace sales tax. SB strips tax; SP-API doesn't. Note in report.

---

## Report Format

**Trend indicators:** 📈 = BSR improved (went DOWN), 📉 = BSR declined (went UP), ➡️ = stable (<5% change), ↑/↓ X = position change, — = no data. **Lower BSR = Better.**

```markdown
# Market Intel - [DATE]

**Baseline:** 2026-02-11 | **Days Since Baseline:** [X]

---

## Yesterday's Business ([date]) — from SP-API Orders

| Metric | Value |
|--------|-------|
| Orders | X |
| Units | X |
| Revenue (incl. tax) | $X |

---

## 7-Day Financial Snapshot ([date range]) — from Seller Board

| Metric | 7-Day Total | Daily Avg | Trend |
|--------|-------------|-----------|-------|
| Net Profit | $X | $X/day | +X% |
| Profit Margin | — | X% | +X pp |
| Ad Spend | $X | $X/day | +X% |
| TACoS | — | X% | +X pp |

---

## Summary

| Metric | Count | vs Baseline |
|--------|-------|-------------|
| Products Improving (BSR ↓) | X | X |
| Products Declining (BSR ↑) | X | X |
| Products Stable | X | X |

---

## Our Products (by Actual Revenue)

| # | Product | ASIN | Category | BSR | SB Rev/7d | SB Units/7d | SB Profit/7d | Subcat Rank | Reviews | Rating | Price | vs Yesterday | vs Baseline |
|---|---------|------|----------|-----|-----------|-------------|-------------|-------------|---------|--------|-------|-------------|-------------|

Sorted by SB 7-day revenue. If SCP data available, append: Impressions | Clicks | Carts | Purchases | Click Share | Conv Share.

---

## Keyword Rank Snapshot (from DataDive Rank Radar)

### Hero Products — Top Keyword Positions

| Product | ASIN | Top 10 KWs | Top 50 KWs | Sig. Movers | Trend |
|---------|------|-----------|-----------|-------------|-------|

### Key Rank Movements Today

| Keyword | Product | Search Vol | Yesterday | Today | Change | Alert |
|---------|---------|-----------|-----------|-------|--------|-------|

Top 20 movements by impact (search volume × rank change).

---

## Keyword Battleground — Us vs Competitors

One mini-table per keyword (20 total, grouped by category). Bold our products. OP = Overall Pick, AC = Amazon's Choice. Empty Apify results carry forward from previous day marked "(prev day)".

### [Category]: "[keyword]" ([SV] SV)

| Brand | ASIN | Keyword Pos | BSR | BSR Source | Badge |
|-------|------|------------|-----|-----------|-------|

---

## Competitor Comparison

One table per category (9 categories). Our products show SB 7-day revenue. Competitors show DD JS Est. (monthly).

### [Category Name]
*DataDive niche: [name] ([ID])*

| Rank | Brand | ASIN | BSR | BSR vs Ours | Reviews | Rating | Sales (source) | Revenue |
|------|-------|------|-----|-------------|---------|--------|---------------|---------|

**Our Position:** #X of Y

---

## New / Rising Competitors

| Category | Brand/Title | ASIN | Found On Keyword | Position | Alert |
|----------|------------|------|-----------------|----------|-------|

---

## Alerts

| Type | Product | Details |
|------|---------|---------|
| ⚠️ OOS | — | Out of stock |
| 🔴 BSR SPIKE | — | BSR increased >20% vs yesterday |
| 🟡 WATCH | — | Keyword rank drop, new competitor |
| 🟢 WIN | — | BSR improved, reviews gained, badge earned |
| 🆕 NEW COMPETITOR | — | Appearing at #X for [keyword] |

---

## Data Notes

Include: report date, baseline date (+ days), SP-API call counts, orders date, DataDive niche/radar counts, keyword scan results (X/20 returned, Y carried forward), competitor BSR scan count, SB date range, all sources used.
```

---

## Error Handling

| Issue | Action |
|-------|--------|
| SP-API auth/rate limit/timeout | Note in report, retry once for 429, skip ASIN on timeout, fall back to DataDive for BSR |
| Apify empty dataset | Carry forward from previous snapshot as "(prev day)". Do NOT retry |
| SP-API Orders fails | Skip "Yesterday's Business" section |
| DataDive fails | Use previous snapshot data |
| Seller Board fails | Skip financial sections, use DD JS Est. in product table |
| No previous snapshot | Compare to baseline only |

**Partial data > No report.** Never wait indefinitely.

---

## Execution Flow

### Phase 1 — Load Context (sequential)
1. Glob `snapshots/YYYY-MM-DD*.json` — most recent (skip today) = "previous snapshot". If none, use `baseline.json`. If gap >1 day, label "vs [date]" not "vs yesterday"
2. Load `snapshots/baseline.json`
3. Load `context/hero-products.md` (13 hero ASINs)
4. Load `context/competitors.md` (competitor ASINs)

### Phase 2 — Fetch All Data (parallel — launch all 6 agents at once)
- SP-API: catalog × 13 + pricing × 13 + inventory × 1 + orders × 1
- DataDive: Rank Radar × 10 radars + Competitors × 11 niches
- Apify: keyword scan × 20 + competitor BSR scan × 1
- Seller Board: dashboard + sales detailed 7D
- Brand Analytics SCP (optional, parallel)

### Phase 3 — Compile Report
1. Merge SP-API BSR/price + SB per-ASIN actuals + DataDive rating/reviews
2. Calculate changes vs yesterday AND vs baseline
3. Build all report sections in mandatory format
4. Save snapshot for tomorrow
5. Present summary to user

---

## Post-Run

**Notifications:** Read `.claude/skills/notification-hub/SKILL.md` → "Recipe: daily-market-intel". If Slack unavailable, skip.

**Lessons:** Update `.claude/skills/daily-market-intel/LESSONS.md` per CLAUDE.md lessons system. Log run entry, update issues, note lessons learned.
