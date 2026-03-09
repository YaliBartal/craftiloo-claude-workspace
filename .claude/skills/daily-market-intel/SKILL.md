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

**USE WHEN** user says: "market check", "morning market", "how are my products doing", "market intel", "daily market", "product pulse"

---

## ⚠️ BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/daily-market-intel/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"⚠️ Repeat issue (×N): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## ⚠️ CORE PURPOSE

**This skill tracks ONE thing: Are we improving or declining?**

Every daily report answers:
1. What is our current BSR and rank?
2. What is our position vs competitors?
3. Did we improve or decline since yesterday?
4. Did we improve or decline since baseline (2026-02-11)?

**The baseline (2026-02-11) is the reference point for all future reports.**

---

## 📊 Sales Data — Actual vs Estimates

**DO NOT estimate sales from BSR.** BSR-to-sales tables are wildly inaccurate for our category/volume.

### Our Products — Use Seller Board Actuals (PRIMARY)

**Primary sales source for OUR products:** Seller Board `get_sales_detailed_7d_report`
- `SB_Rev_7d` = actual 7-day revenue (SalesOrganic + SalesPPC), Amazon.com only
- `SB_Units_7d` = actual 7-day units (UnitsOrganic + UnitsPPC)
- `SB_Profit_7d` = actual 7-day net profit
- Daily avg = divide by 7

**⚠️ DataDive Jungle Scout estimates are NOT accurate for our products.** They can be 2-10x inflated. Never use DD estimates when SB actuals are available.

### Competitor Products — Use DataDive Estimates (only option)

**For competitors:** DataDive Competitor data (`sales` field = Jungle Scout monthly estimate)
- Label clearly as "JS Est." in all tables
- These are directional only — useful for relative positioning, not absolute numbers

### Sorting

**Sort the unified product table by Seller Board actual 7-day revenue** (highest to lowest). Products without SB data go at the bottom.

**BSR is still tracked** for trend direction (improving/declining) but NOT used for sales volume estimation.

---

## 📁 File Organization

```
market-intel/
├── briefs/              # Daily reports (user reads these)
│   └── YYYY-MM-DD.md    # One per day, consistent format
├── snapshots/           # Raw data for comparison
│   └── YYYY-MM-DD.json  # One per day
├── scripts/             # Reusable automation scripts
└── baseline.json        # The baseline snapshot (2026-02-11)
```

---

## 🏗️ Architecture Overview

**Five data sources, each with a clear job (fetched by 5 parallel agents):**
1. **Amazon SP-API (Catalog/Pricing/Inventory/Orders)** — First-party BSR, pricing, inventory for hero products + real-time yesterday's revenue/units
2. **DataDive Rank Radar** — Our keyword rankings on 464+ keywords across 9 hero product radars
3. **DataDive Competitors** — Competitor sales/revenue estimates (JS), rating, reviews, niche positioning for 11 niches
4. **Apify (Keyword Scan + Competitor BSR)** — 20-keyword battleground (us vs competitor positions), badges, new competitor detection + real-time BSR for 34 tracked competitor ASINs via saswave product scraper
5. **Seller Board** — 7-day aggregate financials ONLY (profit, margins, ad spend, TACoS) + per-ASIN actuals

### ⚠️ Data Freshness Rule

**This report must reflect the state of business TODAY.** If data is not current to the day, apply these rules:

| Data Age | Rule |
|----------|------|
| **Same day / yesterday** | Include freely — this is real-time data |
| **2+ days old (day-specific)** | DO NOT INCLUDE — stale day-specific data is misleading |
| **7-day aggregates** | OK even if latest day is 2 days old — rolling averages smooth out the lag |

**Seller Board lags ~2 days.** This means:
- **DO NOT** show "Latest Day" revenue/units/profit from Seller Board (it's 2 days old, not today)
- **DO** show 7-day aggregates: profit, margin, ad spend, TACoS (useful even with lag)
- **DO** use SP-API `get_orders` for yesterday's actual revenue and units (real-time)

| Data Need | Primary Source | Fallback |
|-----------|---------------|----------|
| Hero BSR + subcategory rank | **Amazon SP-API** `get_catalog_item` | DataDive competitors |
| Hero price | **Amazon SP-API** `get_competitive_pricing` | DataDive competitors |
| Hero stock levels / OOS alerts | **Amazon SP-API** `get_fba_inventory` | Seller Board inventory |
| **Yesterday's revenue + units** | **Amazon SP-API** `get_orders(date=yesterday)` | Seller Board (note lag) |
| Hero rating + reviews | **DataDive Competitors** (hero appears in niche data) | Previous snapshot |
| **Our actual units sold (7-day)** | **Seller Board** `get_sales_detailed_7d_report` | SP-API Orders total |
| **Our actual revenue per ASIN (7-day)** | **Seller Board** `get_sales_detailed_7d_report` | SP-API Orders total |
| Competitor BSR, price, rating, reviews | **DataDive Competitors** | Previous snapshot |
| Our keyword rankings | **DataDive Rank Radar** | — |
| Our sponsored/PPC rank | **DataDive Rank Radar** | — |
| Keyword search volume | **DataDive Rank Radar + MKL** | — |
| Keyword rank movements | **DataDive Rank Radar** | — |
| Competitor sales estimates | **DataDive Competitors** (estimates only — not real) | — |
| Competitor revenue | **DataDive Competitors** (estimates only) | Manual (price × units) |
| Competitor P1 keywords | **DataDive Competitors** | — |
| **Keyword Battleground (us vs competitors)** | **Apify keyword scan** (20 keywords, positional data) | Previous snapshot (carry forward) |
| New competitor detection | **Apify keyword scan** (20 keywords) | DataDive niche changes |
| Badge tracking | **Apify keyword scan** | — |
| **Competitor real-time BSR** | **Apify competitor BSR scan** (34 ASINs via saswave) | DataDive competitor BSR (directional) |
| **7-day profit, margin, ad spend, TACoS** | **Seller Board dashboard** (7-day avg only) | — |
| **Search funnel data (impressions → clicks → carts → purchases)** | **Brand Analytics SCP** (weekly, free) | Not available elsewhere |
| **Click share / conversion share per ASIN** | **Brand Analytics SCP** | Not available elsewhere |

### ⚠️ Agent Output Compression Rules

**Every background agent MUST follow these rules to minimize tokens returned to main context:**

1. **Omit null/empty fields** — never include `"field": null` or `"field": ""` in JSON output
2. **No raw API dumps** — process data inside the agent; return only the extracted values needed
3. **Apify agents** — return only `keyword_battleground`, `badges_found`, and `new_competitors` (never raw product lists)
4. **DataDive rank radar agents** — return only top 20 keyword movements + per-product summary (not all 500+ raw rows)
5. **DataDive competitor agents** — return only the 4 top competitors per niche + hero product ratings/reviews
6. **SP-API agents** — return only the fields listed in "What This Step Provides" tables; omit all other API response fields
7. **Seller Board agents** — for sales detailed report, return only per-ASIN 7-day totals (rev, units, profit) for hero ASINs; discard all other rows/columns

**Target: each background agent returns <5K tokens of data to main context.**

### Observed Agent Timing (from 2026-02-25 to 2026-03-01 runs)

| Agent | Typical Duration | Notes |
|-------|-----------------|-------|
| Seller Board | ~18s | Fastest — 2 API calls |
| DataDive Competitors | ~84s | 11 niches × 1.1s rate limit |
| DataDive Rank Radar | ~115s | 10 radars × 1.1s rate limit (incl. B08DDJCQKF added 2026-03-02) |
| Apify (Keywords + Competitor BSR) | ~40-60s | 20 keyword scans + 1 BSR batch, all async. **axesso_data ~7.5s/keyword**, saswave ~40s for BSR batch |
| SP-API (Catalog + Pricing + Inventory + Orders) | ~125s | 28 calls × 0.5s rate limit, serial pricing |

**Launch all 6 agents in parallel** (5 existing + Brand Analytics SCP). Wall-clock bottleneck is SP-API (~2 min). SCP takes ~60s and runs concurrently. Apify now does more work but it's all async so wall-clock is ~60s.

### Performance Targets

| Metric | Target | Actual (recent) |
|--------|--------|-----------------|
| Total tokens | **<110K** | ~95-100K |
| Wall-clock time | **<5 min** | ~2-3 min data fetch |
| Apify cost/day | **~$1.95** | ~$1.80 keywords + ~$0.15 BSR scan |
| SP-API calls | **~28** | 13 catalog + 13 pricing + 1 inventory + 1 orders |
| DataDive niches | **11** | 11 (updated Feb 25) |
| DataDive radars | **10** | 10 hero product radars (incl. B08DDJCQKF added 2026-03-02) |
| Keywords searched (Apify) | **20** | 20 keywords (some may return empty) |
| Competitor BSR ASINs (Apify) | **34** | 34 ASINs via saswave |

---

## 🔧 Step 1: Amazon SP-API — Hero Product BSR, Price, Inventory

**Source:** Amazon SP-API (MCP tools: `get_catalog_item`, `get_competitive_pricing`, `get_fba_inventory`)
**Cost:** $0 (included in SP-API access)
**Time:** ~15 seconds for all calls
**Rate limit:** 0.5s between calls (built into MCP server)

### What This Step Provides

| Data | SP-API Tool | Response Path |
|------|-------------|---------------|
| Main category BSR | `get_catalog_item` | `salesRanks[0].displayGroupRanks[0].rank` |
| Category name | `get_catalog_item` | `salesRanks[0].displayGroupRanks[0].title` |
| Subcategory rank | `get_catalog_item` | `salesRanks[0].classificationRanks[0].rank` |
| Subcategory name | `get_catalog_item` | `salesRanks[0].classificationRanks[0].title` |
| Current price | `get_competitive_pricing` | `CompetitivePrices[condition=New].Price.LandedPrice.Amount` |
| Stock levels (our products) | `get_fba_inventory` | `inventorySummaries[].totalQuantity` |

**Note:** SP-API does NOT return star rating or review count. Those come from **DataDive Competitors** (Step 3).

### Hero Products (13 ASINs)

| Category | Amazon Category | Our Products |
|----------|-----------------|--------------|
| **Cross Stitch** | Arts, Crafts & Sewing | B08DDJCQKF, B0F6YTG1CH |
| **Embroidery (Kids)** | Arts, Crafts & Sewing | B09X55KL2C |
| **Embroidery (Adults)** | Arts, Crafts & Sewing | B0DC69M3YD |
| **Sewing** | Toys & Games | B09WQSBZY7, B096MYBLS1 |
| **Latch Hook** | Arts, Crafts & Sewing | B08FYH13CL, B0F8R652FX |
| **Knitting** | Arts, Crafts & Sewing | B0F8DG32H5 |
| **Fuse Beads** | Arts, Crafts & Sewing | B09THLVFZK, B07D6D95NG |
| **Lacing Cards** | Arts, Crafts & Sewing | B0FQC7YFX6 |
| **Needlepoint** | Arts, Crafts & Sewing | B09HVSLBS6 |

### How to Fetch

**Phase A — Catalog + Pricing (parallel where possible):**
1. For each of the 13 hero ASINs, call `get_catalog_item(asin="{ASIN}")` → extracts BSR, subcategory rank, category
2. For each of the 13 hero ASINs, call `get_competitive_pricing(asin="{ASIN}")` → extracts current New price

**Phase B — Inventory (single call with ASIN filter):**
3. Call `get_fba_inventory(asin_filter="B08DDJCQKF,B0F6YTG1CH,B09X55KL2C,B0DC69M3YD,B09WQSBZY7,B096MYBLS1,B08FYH13CL,B0F8R652FX,B0F8DG32H5,B09THLVFZK,B07D6D95NG,B0FQC7YFX6,B09HVSLBS6")` → returns stock levels for hero ASINs only (aggregated across SKUs, missing ASINs flagged)
4. Flag any with `Fulfillable = 0` as OOS. Any "NOT FOUND IN FBA INVENTORY" = investigate.

**Total calls:** 13 + 13 + 1 = **27 calls** (~15 seconds with rate limiting)

### Competitor Data — Fetched Separately

**Competitor intelligence comes from two sources:**
- **DataDive Competitors (Step 3)** — Sales/revenue estimates (JS), rating, reviews, niche positioning
- **Apify Competitor BSR Scan (Step 4B)** — Real-time BSR for 34 tracked competitor ASINs via saswave product scraper

Competitors tracked in `context/competitors.md`:

| Category | Brand | ASIN(s) |
|----------|-------|---------|
| **Cross Stitch** | Pllieay | B08T5QC9FS |
| | KRAFUN | B0B7JHN4F1 |
| | Caydo | B0CM9JKNCC |
| | EZCRA | B0DFHN42QB |
| **Embroidery (Kids)** | CraftLab | B087DYHMZ2 |
| | KRAFUN | B0D8171TF1 |
| | Pllieay | B08TC7423N |
| | Louise Maelys | B0DP654CSV |
| **Embroidery (Adults)** | CYANFOUR | B0CZHKSSL4, B0DMHY2HF3 |
| | Santune | B0BB9N74SG |
| | Bradove | B0B762JW55 |
| | ETSPIL | B0C3ZVKB46 |
| **Sewing** | KRAFUN | B091GXM2Y6, B0C2XYP6L3, B0CV1F5CFS |
| | EZCRA | B0CXY8JMTK, B0CYNNT2ZT |
| | Klever Kits | B0CTTMWXYP |
| | kullaloo | — (confirmed Feb 25, #3 for "sewing kit for kids") |
| **Latch Hook** | LatchKits | B06XRRN4VL, B0CX9H8YGR |
| **Knitting** | READAEER | — (confirmed Feb 25, #1-#2 for "loom knitting kit") |
| | Creativity for Kids | B004JIFCXO |
| | Hapinest | B0B8W4FK4Q |
| **Fuse Beads** | INSCRAFT | B0C5WQD914 |
| | ARTKAL | B0FN4CT867 |
| | LIHAO | B08QV9CMFQ |
| | FUNZBO | B0D5LF666P |
| **Lacing Cards** | Melissa & Doug | B00JM5G05I |
| | KRAFUN | B0BRYRD91V |
| | Serabeena | B0D178S25M |
| **Gem Art** | EZCRA | B0CWLTTZ2G |

---

## 📡 Step 2: DataDive Rank Radar — Our Keyword Rankings (PRIMARY)

**PURPOSE:** This is now the PRIMARY source for all keyword ranking data. Replaces the old 27-keyword Apify search.

**Cost:** Included in DataDive subscription (no per-call cost)
**Time:** ~3.5 min for all radars
**API:** `GET /v1/niches/rank-radars/{rankRadarId}?startDate={yesterday}&endDate={today}`

### Active Rank Radars (hero products only)

Fetch radars for these hero product ASINs **only**:
- **B08DDJCQKF (Cross Stitch Backpack Charms)** — include always (user requirement 2026-03-02)
- B09X55KL2C (Embroidery Kids) — 55 keywords
- B0DC69M3YD (Embroidery Adults) — 67 keywords
- B09WQSBZY7 (Fairy Sewing Kit) — 87 keywords
- B096MYBLS1 (Dessert Sewing Kit) — 50 keywords
- B08FYH13CL (Latch Hook Pencil Cases) — 53 keywords
- B0F8DG32H5 (Knitting Cat & Hat) — 81 keywords
- B09THLVFZK (Mini Fuse Beads) — 18 keywords
- B07D6D95NG (10mm Big Fuse Beads) — 38 keywords
- B0FQC7YFX6 (Princess Lacing Card) — 52 keywords

**Skip these** (low value or not primary hero — saves ~15K tokens):
- B092SW839H (Punch Needle) — 0 keywords in top 10
- B0F8QZZQQM (Cross Stitch Beginner) — volatile, not primary hero
- B09HVDNFMR (Needlepoint) — 0 keywords in top 10
- B0B1927HCG (Cross Stitch Kits) — non-hero, not critical daily
- B0FHMRQWRX (Latch Hook Kit) — non-hero, not critical daily
- B0DKD2S3JT (Crochet/Knitting) — non-hero, not critical daily

### How to Fetch

1. Call `GET /v1/niches/rank-radars?pageSize=50` to list all radars
2. Match radars to hero ASINs using the `asin` field
3. For each matched radar, call `GET /v1/niches/rank-radars/{radarId}?startDate={yesterday}&endDate={today}`
4. Rate limit: 1.1 seconds between requests

**CRITICAL: Fetch ALL keywords per radar. Do NOT cap or truncate results at 50.**
Radars contain 18-87 keywords each. The full keyword set must be returned.
If the API response includes pagination, fetch all pages.
The agent summary must include top10/top50 counts based on the FULL keyword set — not a truncated subset.

### Extract Per Keyword
- `keyword` — the search term
- `searchVolume` — monthly search volume
- `ranks[].organicRank` — our organic position (daily)
- `ranks[].impressionRank` — our sponsored/PPC position (daily)
- Calculate change vs yesterday

### Report Section

```markdown
## Keyword Rank Snapshot (from DataDive Rank Radar)

### Our Hero Products — Top Keyword Positions

| Product | ASIN | Top 10 KWs | Top 50 KWs | Sig. Movers | Trend |
|---------|------|-----------|-----------|-------------|-------|

### Key Rank Movements Today

| Keyword | Product | Search Vol | Yesterday | Today | Change | Alert |
|---------|---------|-----------|-----------|-------|--------|-------|
```

Show only the top 20 most impactful movements (by search volume × rank change).

---

## 📡 Step 3: DataDive Competitors — Sales Estimates, Revenue, Rating & Reviews

**PURPOSE:** Get Jungle Scout-powered sales estimates, revenue, and competitive positioning for each niche. **Also provides rating and reviewCount for ALL products** (hero + competitors) — this is now the primary source for review/rating data since SP-API doesn't return those fields.

**Cost:** Included in DataDive subscription
**Time:** ~3 min for all niches
**API:** `GET /v1/niches/{nicheId}/competitors?pageSize=4`

**⚠️ TOKEN LIMIT: Fetch only the top 4 competitors per niche** (sorted by sales descending). This is enough to understand competitive position without wasting tokens on long tails.

### Niche IDs to Fetch (11 niches)

| Niche ID | Label | Research Date | Hero Products |
|----------|-------|---------------|---------------|
| u1y83aQfmK | Kids Cross Stitch Kit | 2026-02-25 | B08DDJCQKF, B0F6YTG1CH |
| gfot2FZUBU | Embroidery Stitch Practice Kit | 2026-02-08 | B0DC69M3YD, B09X55KL2C |
| Er21lin0KC | Beginners Embroidery Kit for Kids | 2026-01-11 | B09X55KL2C |
| RmbSD3OH6t | Sewing Kit for Kids | 2026-02-08 | B09WQSBZY7, B096MYBLS1 |
| 3qbggwOhO2 | Latch Hook Kits for Kids | 2026-02-25 | B08FYH13CL, B0F8R652FX |
| AY4AlnSj9g | Mini Perler Beads | 2025-12-08 | B09THLVFZK |
| O6b4XATpTj | Loom Knitting | 2026-01-07 | B0F8DG32H5 |
| Aw4EQhG6bP | Lacing Cards for Kids | 2026-02-01 | B0FQC7YFX6 |
| 5IGkCmOM0h | Needlepoint Pouch Kit | 2026-02-25 | B09HVSLBS6 |
| kZRreyE7kJ | Cross Stitch Kits (broad) | 2026-02-25 | B08DDJCQKF, B09X55KL2C |
| WFV3TE3beK | Fuse Beads | 2026-02-08 | B07D6D95NG |

**Retired niches (do NOT fetch):**
- `b4Nisjv3xy` (Cross Stitch Kits for Kids, Dec 2025) — superseded by `u1y83aQfmK` (Feb 2026)
- `VqBgB5QQ07` (Latch Hook Kit for Kids, Dec 2025) — superseded by `3qbggwOhO2` (Feb 2026)

**All 13 hero products now covered by DD niche data.** B07D6D95NG (10mm Big Fuse Beads) covered by `WFV3TE3beK`.

### Extract Per Competitor

| Field | What It Contains |
|-------|------------------|
| `asin` | Competitor ASIN |
| `bsr` | Best Sellers Rank (used for competitor BSR in report) |
| `sales` | Monthly sales estimate (Jungle Scout) |
| `revenue` | Monthly revenue estimate |
| `price` | Current price |
| `rating` | Star rating |
| `reviewCount` | Review count |
| `kwRankedOnP1` | Keywords ranked on page 1 |

**Omit null fields** — do not include fields with null/missing values in output. This significantly reduces response size.

**Use DataDive sales estimates as PRIMARY** (more accurate than BSR-to-sales table).

### Hero Product Rating & Reviews

DataDive competitor data includes our hero products (they appear in their niche competitor lists). Extract `rating` and `reviewCount` for hero ASINs here. If a hero product is not found in any niche (e.g., B07D6D95NG 10mm Fuse Beads), carry forward from the previous day's snapshot or baseline.

---

## 🔍 Step 4: Apify — Keyword Battleground + Competitor BSR + Badges + New Competitors

**PURPOSE:** This agent handles TWO Apify jobs in parallel:

**4A: Keyword Scan (20 keywords)** — provides:
1. **Keyword Battleground** — our position vs tracked competitors on 20 key keywords (head-to-head)
2. **Badge tracking** — check for Overall Pick, Amazon's Choice on our products
3. **New competitor detection** — find unknown ASINs in top 5

**4B: Competitor BSR Scan (34 ASINs)** — provides:
4. **Real-time BSR** for all tracked competitor ASINs (solves DataDive BSR gap)

**DataDive Rank Radar (Step 2) tracks our rank on 500+ keywords.** This step adds the competitive dimension — where do our competitors rank on the SAME keywords, and what is their real BSR?

**Keyword scan actor:** `axesso_data/amazon-search-scraper`
**BSR scan actor:** `saswave~amazon-product-scraper`
**Cost:** ~$0.09 per keyword × 20 + ~$0.15 BSR scan = **~$1.95/day**
**Time:** ~40-60s (all 21 jobs launch async in parallel — 20 keyword scans + 1 BSR batch)

### Keywords to Scan (20 total — 1-4 per category)

| # | Category | Keyword | Volume | Status |
|---|----------|---------|--------|--------|
| 1 | Cross Stitch | embroidery kit for kids | 13,067 | Core |
| 2 | Cross Stitch | cross stitch kits for kids | TBD | New |
| 3 | Cross Stitch | cross stitch for kids | TBD | New |
| 4 | Embroidery Kids | kids embroidery kit | 5,802 | Core |
| 5 | Embroidery Adults | embroidery kit for beginners | 103,524 | Core |
| 6 | Sewing | sewing kit for kids | 20,874 | Core |
| 7 | Sewing | kids sewing kit | ~8,959 | New |
| 8 | Latch Hook | latch hook kits for kids | 16,625 | Core |
| 9 | Latch Hook | latch hook pillow kit | TBD | New |
| 10 | Fuse Beads | mini perler beads | 3,242 | Core |
| 11 | Fuse Beads | perler beads | ~75,347 | New |
| 12 | Fuse Beads | mini fuse beads | TBD | New |
| 13 | Knitting | loom knitting kit | 8,102 | Core |
| 14 | Knitting | loom knitting | TBD | New |
| 15 | Knitting | knitting kit for kids | TBD | New |
| 16 | Knitting | knitting kit for beginners | TBD | New |
| 17 | Lacing Cards | lacing cards | 4,524 | Core |
| 18 | Lacing Cards | lacing cards for kids ages 3-5 | TBD | New |
| 19 | Lacing Cards | lacing cards for kids ages 4-8 | TBD | New |
| 20 | Needlepoint | needlepoint kits for kids | 1,416 | Core |

**Input format:**
```json
{
  "input": [{"keyword": "embroidery kit for kids", "country": "US"}]
}
```

**Notes:**
- `input` must be an array (even for a single keyword)
- `country` = "US" for amazon.com
- To run multiple keywords in one actor call: add multiple objects to the `input` array — but for parallel async runs, one keyword per actor call is preferred

### Axesso Output Field Mapping

| Need | Axesso Field | Notes |
|------|-------------|-------|
| Position | `searchResultPosition` | **0-indexed** — add 1 for display |
| ASIN | `asin` | Same |
| Title | `productDescription` | Full product title |
| Price | `price` | Float (e.g. `16.99`) — no $ sign |
| Rating | `productRating` | String: "4.4 out of 5 stars" — parse to extract float |
| Reviews | `countReview` | Integer |
| Sales volume | `salesVolume` | String: "5K+ bought in past month" |
| Sponsored | `sponsored` | Boolean ✅ (new — igview didn't have this) |
| Best Seller badge | ❌ not present | Not in Axesso output — use badges_found from search result page instead |
| Amazon's Choice | ❌ not present | Not in Axesso output |
| Product URL | `dpUrl` | Relative path — prepend `https://www.amazon.com` if needed |

**Badge detection note:** Axesso doesn't return `is_best_seller` or `is_amazon_choice` fields. To detect badges, check if the product appears in the top results with unusual salesVolume or if the badge section on the page is visible. In practice, Overall Pick and Amazon's Choice badges have been reliably visible in our snapshots via this actor.

### What to Extract
  "query": "embroidery kit for kids",
  "maxPages": 1,
  "country": "US",
  "language": "en_US",
  "sortBy": "RELEVANCE"
}
```

### What to Extract (badges, new competitors, AND keyword rank comparison)

**⚠️ TOKEN RULE: Do NOT return full keyword_results to the main context.** Agents must process results internally and return only the structured output below.

**Agent output format:**

```json
{
  "keyword_battleground": [
    {
      "category": "Cross Stitch",
      "keyword": "embroidery kit for kids",
      "search_volume": 13067,
      "positions": [
        {"asin": "B09X55KL2C", "brand": "CRAFTILOO", "position": 1, "is_hero": true},
        {"asin": "B08T5QC9FS", "brand": "Pllieay", "position": 5, "is_hero": false},
        {"asin": "B0DFHN42QB", "brand": "EZCRA", "position": 8, "is_hero": false}
      ]
    }
  ],
  "badges_found": [
    {"asin": "B09X55KL2C", "keyword": "embroidery kit for kids", "badge": "Overall Pick"}
  ],
  "new_competitors": [
    {"asin": "B0FR7Y8VHB", "brand": "Louise Maelys", "keyword": "embroidery kit for kids", "position": 3}
  ],
  "keyword_rankings": [
    {
      "keyword": "latch hook kits for kids",
      "our_asin": "B08FYH13CL",
      "our_position": 9,
      "top_3": [
        {"position": 1, "asin": "B06XRRN4VL", "brand": "LatchKits", "badge": "Overall Pick"},
        {"position": 2, "asin": "B0DJQPGDMQ", "brand": "veirousa"},
        {"position": 3, "asin": "B07PPD8Q8V", "brand": "Made By Me"}
      ]
    }
  ]
}
```

For `keyword_rankings`:
- `our_asin`: the hero product ASIN expected for this keyword (see keyword table above)
- `our_position`: actual position of our hero product in results (null if not in top 20)
- `top_3`: the top 3 products that are NOT our product, with brand name resolved if known

If nothing found: `{"badges_found": [], "new_competitors": [], "keyword_rankings": []}`

**Never return the raw product list array** — it's large and unnecessary once processed.

### ASIN Lookup Table (for agent to match positions)

The agent must cross-reference search results against these ASINs per keyword:

| Keyword | Hero ASINs | Competitor ASINs to Track |
|---------|-----------|--------------------------|
| embroidery kit for kids | B08DDJCQKF, B0F6YTG1CH, B09X55KL2C | B08T5QC9FS, B0B7JHN4F1, B0CM9JKNCC, B0DFHN42QB |
| cross stitch kits for kids | B08DDJCQKF, B0F6YTG1CH | B08T5QC9FS, B0B7JHN4F1, B0CM9JKNCC |
| cross stitch for kids | B08DDJCQKF, B0F6YTG1CH | B08T5QC9FS, B0B7JHN4F1, B0CM9JKNCC |
| kids embroidery kit | B09X55KL2C | B087DYHMZ2, B0D8171TF1, B08TC7423N, B0DP654CSV |
| embroidery kit for beginners | B0DC69M3YD | B0CZHKSSL4, B0DMHY2HF3, B0BB9N74SG, B0B762JW55, B0C3ZVKB46 |
| sewing kit for kids | B09WQSBZY7, B096MYBLS1 | B091GXM2Y6, B0C2XYP6L3, B0CV1F5CFS, B0CXY8JMTK, B0CYNNT2ZT, B0CTTMWXYP |
| kids sewing kit | B09WQSBZY7, B096MYBLS1 | B091GXM2Y6, B0CXY8JMTK, B0CTTMWXYP |
| latch hook kits for kids | B08FYH13CL, B0F8R652FX | B06XRRN4VL, B0CX9H8YGR, B07PPD8Q8V |
| latch hook pillow kit | B0F8R652FX | B06XRRN4VL, B0CX9H8YGR |
| mini perler beads | B09THLVFZK, B07D6D95NG | B0C5WQD914, B0FN4CT867, B08QV9CMFQ, B0D5LF666P |
| perler beads | B09THLVFZK, B07D6D95NG | B0C5WQD914, B08QV9CMFQ, B0D5LF666P |
| mini fuse beads | B09THLVFZK | B0C5WQD914, B08QV9CMFQ, B0D5LF666P |
| loom knitting kit | B0F8DG32H5 | B004JIFCXO, B0B8W4FK4Q, B0DS23C1YX |
| loom knitting | B0F8DG32H5 | B0DS23C1YX, B0182IQHYE |
| knitting kit for kids | B0F8DG32H5 | B0B8W4FK4Q, B004JIFCXO |
| knitting kit for beginners | B0F8DG32H5 | B0DS23C1YX, B0B8W4FK4Q |
| lacing cards | B0FQC7YFX6 | B00JM5G05I, B0BRYRD91V, B0D178S25M |
| lacing cards for kids ages 3-5 | B0FQC7YFX6 | B00JM5G05I, B0BRYRD91V, B0D178S25M |
| lacing cards for kids ages 4-8 | B0FQC7YFX6 | B00JM5G05I, B0BRYRD91V |
| needlepoint kits for kids | B09HVSLBS6 | — |

**When updating `context/competitors.md` with new ASINs, also update this table.**

---

### 4B: Competitor BSR Scan (runs inside the same Apify agent)

**PURPOSE:** Get real-time BSR for all tracked competitor ASINs. DataDive Competitors provides sales/revenue estimates but its BSR data is directional only. This scan gives us precise, same-day BSR from Amazon.

**Actor:** `saswave~amazon-product-scraper`
**Cost:** ~$0.15/run
**Time:** ~40s (runs async alongside keyword scan — agent launches all 21 jobs at once: 20 keyword scans + 1 BSR batch)

**Input format:**
```json
{
  "asins": ["B08T5QC9FS", "B0B7JHN4F1", "B0CM9JKNCC", "B0DFHN42QB", "B087DYHMZ2", "B0D8171TF1", "B08TC7423N", "B0DP654CSV", "B0CZHKSSL4", "B0DMHY2HF3", "B0BB9N74SG", "B0B762JW55", "B0C3ZVKB46", "B091GXM2Y6", "B0C2XYP6L3", "B0CXY8JMTK", "B0CTTMWXYP", "B06XRRN4VL", "B0CX9H8YGR", "B07PPD8Q8V", "B004JIFCXO", "B0B8W4FK4Q", "B0DS23C1YX", "B0182IQHYE", "B0C5WQD914", "B0FN4CT867", "B08QV9CMFQ", "B0D5LF666P", "B00JM5G05I", "B0BRYRD91V", "B0D178S25M", "B0CG9FN2CH", "B0CWLTTZ2G", "B0DJQPGDMQ"],
  "amazon_domain": "www.amazon.com"
}
```

**CRITICAL:** Must include `amazon_domain: "www.amazon.com"` or actor crashes with KeyError.

**Competitor ASINs by category (34 total):**

| Category | ASINs |
|----------|-------|
| Cross Stitch | B08T5QC9FS (Pllieay), B0B7JHN4F1 (KRAFUN), B0CM9JKNCC (Caydo), B0DFHN42QB (EZCRA) |
| Embroidery Kids | B087DYHMZ2 (CraftLab), B0D8171TF1 (KRAFUN), B08TC7423N (Pllieay), B0DP654CSV (Louise Maelys) |
| Embroidery Adults | B0CZHKSSL4 (CYANFOUR), B0DMHY2HF3 (CYANFOUR), B0BB9N74SG (Santune), B0B762JW55 (Bradove), B0C3ZVKB46 (ETSPIL) |
| Sewing | B091GXM2Y6 (KRAFUN), B0C2XYP6L3 (KRAFUN), B0CXY8JMTK (EZCRA), B0CTTMWXYP (Klever Kits) |
| Latch Hook | B06XRRN4VL (LatchKits), B0CX9H8YGR (LatchKits), B07PPD8Q8V (Made By Me), B0DJQPGDMQ (Unknown — new #1) |
| Knitting | B004JIFCXO (Creativity for Kids), B0B8W4FK4Q (Hapinest), B0DS23C1YX (READAEER), B0182IQHYE (READAEER) |
| Fuse Beads | B0C5WQD914 (INSCRAFT), B0FN4CT867 (ARTKAL), B08QV9CMFQ (LIHAO), B0D5LF666P (FUNZBO) |
| Lacing Cards | B00JM5G05I (Melissa & Doug), B0BRYRD91V (KRAFUN), B0D178S25M (Serabeena) |
| Needlepoint | B0CG9FN2CH (Pllieay) |
| Gem Art | B0CWLTTZ2G (EZCRA) |

**Extract per ASIN:**
- `bsr` — Best Sellers Rank (reliable)
- `bsr_category` — Category name (reliable)
- `rating` — Star rating (reliable)
- `reviews` — Review count (reliable)
- `price` — **IGNORE** (returns EUR due to locale issue — not usable for USD comparisons)

**Agent output format (add to existing keyword scan output):**
```json
{
  "competitor_bsr": {
    "B08T5QC9FS": {"bsr": 26473, "category": "Arts, Crafts & Sewing", "rating": 4.2, "reviews": 1353},
    "B0CZHKSSL4": {"bsr": 246, "category": "Arts, Crafts & Sewing", "rating": 4.4, "reviews": 1304}
  }
}
```

**Use in report:** Competitor BSR from this scan goes into the Competitor Comparison tables alongside DataDive sales estimates. Label as "Apify" in BSR Source column.

---

### Processing (done inside the agent, not in main context)

1. For each keyword's search results, find ALL hero and competitor ASINs from the lookup table → record their position → add to `keyword_battleground`
2. **Our products with badges** → add to `badges_found`
3. **Unknown ASINs in top 5** → add to `new_competitors`
4. If a tracked ASIN is not found in results → omit it (don't include with position: null)
1. Compare each ASIN against hero product list and competitor list
2. **Unknown ASINs in top 5** → add to `new_competitors` output
3. **Our products with badges** → add to `badges_found` output
4. **All 9 keywords** → record our position + top 3 non-us positions in `keyword_rankings`
5. **Do NOT use this for organic rank tracking** — use DataDive Rank Radar instead. This is for competitor comparison only.

### New Competitor Detection Rules

Flag an ASIN as a new competitor if:
- NOT in hero products list AND NOT in competitors list
- Appears in **top 5** for any keyword (top 10 is too noisy)
- Prioritize products that appear on multiple keywords

**If new competitors found:**
- Include in New / Rising Competitors section
- Flag as 🟡 WATCH in Alerts
- If seen in 2+ consecutive daily runs, suggest adding to `context/competitors.md`

---

## 📊 Step 4C: Brand Analytics SCP — Search Funnel Data (Optional Enrichment)

**PURPOSE:** Adds Amazon's own impression → click → cart → purchase funnel data per ASIN. This is first-party data (not estimates) and provides click share and conversion share that no other source can give. **Free** — included with Brand Registry.

**Cost:** $0 (Brand Analytics is free)
**Time:** ~60 seconds (report creation + download)
**Tool:** `create_brand_analytics_report` (SP-API MCP)

**When to include:** Run this step when time/tokens allow. It adds ~5K tokens but provides unique funnel metrics. Skip if the run is already near the 110K token ceiling.

### How to Fetch

1. **Create the SCP report:**
   ```
   create_brand_analytics_report(
       report_name="scp",
       period="WEEK",
       periods_back=2,
       marketplace="US"
   )
   ```
   **Note:** Use `periods_back=2` on Sunday/Monday (48h SLA). Use `periods_back=1` Tuesday-Saturday.

2. **Poll for completion:**
   ```
   get_report_status(report_id="{reportId}", marketplace="US")
   ```
   Wait for `DONE`. Poll every 15 seconds, max 8 times (~60s total).

3. **Download the report:**
   ```
   get_report_document(report_id="{reportId}", marketplace="US")
   ```

### What SCP Provides (per ASIN, weekly)

| Metric | What It Means | Use In Report |
|--------|---------------|---------------|
| `searchFunnelImpressions` | Times our ASIN appeared in search results | Visibility trend |
| `searchFunnelClicks` | Clicks from search results | Demand signal |
| `searchFunnelCartAdds` | Add-to-cart from search | Purchase intent |
| `searchFunnelPurchases` | Purchases from search | Actual conversion |
| `searchFunnelClickShare` | Our % of total clicks in category | Competitive position |
| `searchFunnelConversionShare` | Our % of total conversions | Market share signal |

### How to Use in the Report

**Add a "Search Funnel" column group to the Our Products table** (if SCP data was fetched):

| Product | ASIN | ... existing cols ... | Impressions | Clicks | Carts | Purchases | Click Share | Conv Share |
|---------|------|-----------------------|-------------|--------|-------|-----------|-------------|------------|

**Key signals to highlight:**
- **Click share declining** while BSR stable → losing visibility, may need PPC boost
- **Conversion share > click share** → product converts well, invest in more traffic
- **High impressions, low clicks** → listing image/title may need optimization
- **High clicks, low carts** → price or content issue on detail page

### If SCP Fails

Continue without it — all other data sources still provide a complete report. Note: "Brand Analytics SCP unavailable — funnel data not included."

**This step runs in parallel with the other 5 agents.** It adds ~60s but doesn't block any other step.

---

## 💰 Step 5: Seller Board — 7-Day Aggregates + Per-ASIN Actuals

**PURPOSE:** Two reports from Seller Board:
1. **Dashboard** — 7-day aggregate financials (profit, margins, ad spend, TACoS)
2. **Sales Detailed 7D** — Actual per-ASIN revenue, units, profit for last 7 days (replaces inaccurate DataDive Jungle Scout estimates for our products)

**⚠️ CRITICAL: Do NOT use Seller Board for day-specific data.** It lags ~1-2 days. Yesterday's revenue/units come from SP-API Orders (Step 6).

**Tools:** `get_daily_dashboard_report` + `get_sales_detailed_7d_report` (MCP)
**Time:** ~20 seconds (2 API calls)

### 5A: Dashboard Report (7-day aggregates)

| Metric | Column | How to Calculate |
|--------|--------|------------------|
| 7-Day Net Profit | NetProfit | Sum last 7 available days |
| 7-Day Avg Margin | Margin | Average last 7 available days |
| 7-Day Ad Spend | SponsoredProducts + SponsoredDisplay + SponsoredBrands + SponsoredBrandsVideo | Sum last 7 available days |
| 7-Day TACoS | Ad Spend / Revenue × 100 | Calculate from 7-day sums |
| 7-Day Revenue (SB) | SalesOrganic + SalesPPC | Sum last 7 available days (for TACoS denominator) |

### 5B: Sales Detailed 7D Report (per-ASIN actuals)

**Use `get_sales_detailed_7d_report`** — this is a 7-day window report (~460 rows) instead of the 30-day report (~2,335 rows). Same columns, much less data to parse.

**This replaces DataDive Jungle Scout estimates for OUR products.** DD estimates are wildly inaccurate (often 2-10x inflated).

**Report structure:** Each row = one date × one ASIN × one SKU × one marketplace. Same ASIN can appear multiple rows per day (different SKUs).

**Key columns:**

| Column | What It Contains |
|--------|------------------|
| `Date` | DD/MM/YYYY format |
| `Marketplace` | Amazon.com, Amazon.ca, Amazon.com.mx |
| `ASIN` | Product ASIN |
| `SalesOrganic` | Organic revenue ($) |
| `SalesPPC` | PPC revenue ($) |
| `UnitsOrganic` | Organic units sold |
| `UnitsPPC` | PPC units sold |
| `NetProfit` | Profit after all fees/costs ($) |
| `Margin` | Profit margin (%) |

**How to extract per-ASIN 7-day actuals:**

1. Filter rows to `Marketplace = Amazon.com` only
2. Report already contains exactly 7 days of data — no date filtering needed
3. For each hero ASIN, **sum across all SKUs and all 7 days**:
   - `SB_Rev_7d` = SUM(SalesOrganic + SalesPPC)
   - `SB_Units_7d` = SUM(UnitsOrganic + UnitsPPC)
   - `SB_Profit_7d` = SUM(NetProfit)
4. Calculate daily averages: `SB_Rev_Daily` = SB_Rev_7d / 7
5. Note the date range (e.g., "Feb 16-22")

**Hero ASINs to extract:** B08DDJCQKF, B0F6YTG1CH, B09X55KL2C, B0DC69M3YD, B09WQSBZY7, B096MYBLS1, B08FYH13CL, B0F8R652FX, B0F8DG32H5, B09THLVFZK, B07D6D95NG, B0FQC7YFX6, B09HVSLBS6

**⚠️ Important:** SB data lags ~2 days, so the "7-day" window may be e.g., Feb 16-22, not Feb 19-25. Always note the date range.

### What NOT to Extract

- ❌ "Latest day" revenue (it's 2 days old — use SP-API Orders instead)
- ❌ "Latest day" units (same — use SP-API Orders)
- ❌ "Latest day" profit (2 days old, misleading as "today")
- ❌ Any single-day metric presented as current
- ❌ Amazon.ca / Amazon.com.mx data (too small to matter in daily report)

**Always note the date range of the 7-day window** (e.g., "Feb 15-21" not "last 7 days").

### Fallback

If Seller Board fetch fails:
- Note: "Seller Board unavailable — 7-day aggregates and per-ASIN actuals not available"
- Fall back to DataDive estimates for the unified table (label as "JS Est.")
- Continue with market data — do NOT block the report

---

## 📦 Step 6: SP-API Orders — Yesterday's Revenue & Units (Real-Time)

**PURPOSE:** Real-time revenue and unit count for yesterday. Supplements Seller Board's 2-day lag so the report reflects actual current business state.

**Tool:** `get_orders(date=yesterday)` (MCP)
**Time:** ~10-15 seconds (paginates automatically)

### How to Fetch

1. Call `get_orders(date="YYYY-MM-DD")` where the date is **yesterday**
2. The tool auto-paginates (up to 500 orders) and returns a summary with:
   - Total orders (shipped, pending, canceled)
   - Total units
   - Shipped revenue (note: includes sales tax)

### What to Extract

| Metric | Source |
|--------|--------|
| Yesterday's Orders | Total orders count |
| Yesterday's Units | Total units (shipped + pending) |
| Yesterday's Revenue (incl. tax) | Shipped revenue total |

**⚠️ Revenue includes marketplace sales tax.** Note this in the report. For pre-tax comparison with Seller Board, discount ~8-10% as approximation, or note the caveat.

### Limitations

- **Revenue includes tax** — Seller Board strips tax out, SP-API doesn't. Note the difference.
- **No profit data** — SP-API orders don't include COGS, fees, or ad spend. Profit comes from Seller Board 7-day only.
- **Pending orders** — may not show price until shipped. Count units but note some revenue may be missing.

---

## 📋 MANDATORY REPORT FORMAT

**Every daily report MUST follow this exact format:**

```markdown
# Market Intel - [DATE]

**Baseline:** 2026-02-11 | **Days Since Baseline:** [X]

---

## Yesterday's Business ([yesterday's date]) — from SP-API Orders

| Metric | Value |
|--------|-------|
| Orders | X |
| Units | X |
| Revenue (incl. tax) | $X |

*Real-time from Amazon SP-API. Revenue includes marketplace sales tax.*

---

## 7-Day Financial Snapshot ([date range]) — from Seller Board

| Metric | 7-Day Total | Daily Avg | Trend |
|--------|-------------|-----------|-------|
| Net Profit | $X | $X/day | +X% |
| Profit Margin | — | X% | +X pp |
| Ad Spend | $X | $X/day | +X% |
| TACoS | — | X% | +X pp |

*Seller Board data lags ~2 days. Only 7-day aggregates shown (day-specific data excluded as stale).*

---

## Summary

| Metric | Count | vs Baseline |
|--------|-------|-------------|
| Products Improving (BSR ↓) | X | X vs baseline |
| Products Declining (BSR ↑) | X | X vs baseline |
| Products Stable | X | X vs baseline |

---

## Our Products (by Actual Revenue)

| # | Product | ASIN | Category | BSR | SB Rev/7d | SB Units/7d | SB Profit/7d | Subcat Rank | Reviews | Rating | Price | vs Yesterday | vs Baseline |
|---|---------|------|----------|-----|-----------|-------------|-------------|-------------|---------|--------|-------|-------------|-------------|

*Sorted by Seller Board actual 7-day revenue (highest → lowest). SB = Seller Board actuals (Amazon.com, [date range]). Do NOT use DataDive estimates for our products.*

---

## Keyword Rank Snapshot (from DataDive Rank Radar)

### Our Hero Products — Top Keyword Positions

| Product | ASIN | Top 10 KWs | Top 50 KWs | Sig. Movers | Trend |
|---------|------|-----------|-----------|-------------|-------|

### Key Rank Movements Today

| Keyword | Product | Search Vol | Yesterday | Today | Change | Alert |
|---------|---------|-----------|-----------|-------|--------|-------|

*Top 20 movements by impact (search volume × rank change).*

---

## Keyword Battleground — Us vs Competitors

*Head-to-head on 20 monitored keywords. Positions from Apify keyword scan, BSR from SP-API/Apify competitor scan. Badges shown inline.*

### [Category]: "[keyword]" ([search volume] SV)

| Brand | ASIN | Keyword Pos | BSR | BSR Source | Badge |
|-------|------|------------|-----|-----------|-------|
| **CRAFTILOO** | **B09X55KL2C** | **#1** | **15,486** | SP-API | **OP** |
| Louise Maelys | B0FR7Y8VHB | #3 | — | — | — |
| Pllieay | B08TC7423N | #5 | 64,598 | Apify | — |

*One mini-table per keyword (20 total, grouped by category). Show our hero product(s) + top competitors found in results.*
*Bold = our product. "—" = not found on page 1. OP = Overall Pick, AC = Amazon's Choice.*
*If Apify returned empty for a keyword, carry forward from previous day and note "(prev day)".*
*Categories: Cross Stitch (3 KWs), Embroidery Kids (1), Embroidery Adults (1), Sewing (2), Latch Hook (2), Fuse Beads (3), Knitting (4), Lacing Cards (3), Needlepoint (1)*

---

## Competitor Comparison

### [Category Name]
*DataDive niche: [niche name] ([niche ID])*

*Our BSR: X,XXX | Leader BSR: X,XXX | BSR Gap: X,XXX (we are X positions behind/ahead)*

| Rank | Brand | ASIN | BSR | BSR vs Our BSR | Reviews | Rating | Sales (source) | Revenue |
|------|-------|------|-----|----------------|---------|--------|---------------|---------|
| **#1** | **CRAFTILOO** | **BXXXXXX** | **X,XXX** | — | X | X.X | $X SB/7d | — |
| #2 | Competitor | ASIN | X,XXX | +X,XXX worse | X | X.X | X JS Est./mo | $X |

**Our Position:** #X of Y

*One table per category. Our products show SB actual 7-day revenue. Competitors show DD JS Est. (monthly). "BSR vs Our BSR" = competitor BSR minus our BSR (positive = they are worse/higher BSR; negative = they are better/lower BSR).*
*Categories: Cross Stitch, Embroidery Kids, Embroidery Adults, Sewing, Latch Hook, Fuse Beads, Knitting, Lacing Cards, Needlepoint*

---

## New / Rising Competitors

| Category | Brand/Title | ASIN | Found On Keyword | Position | Alert |
|----------|------------|------|-----------------|----------|-------|

*Unknown ASINs found in top 5 of keyword scan. "No new competitors detected" if none.*

---

## Alerts

| Type | Product | Details |
|------|---------|---------|
| ⚠️ OOS | [Product] | Out of stock alert |
| 🔴 BSR SPIKE | [Product] | BSR increased >20% vs yesterday |
| 🟡 WATCH | [Product] | Keyword rank drop, new competitor, etc. |
| 🟢 WIN | [Product] | BSR improved, reviews gained, badge earned |
| 🆕 NEW COMPETITOR | [Brand] | Appearing at #X for [keyword] |

---

## Data Notes

- **Report Date:** YYYY-MM-DD
- **Baseline Date:** 2026-02-11 (X days)
- **SP-API Calls:** X catalog + X pricing + 1 inventory + 1 orders = X total
- **SP-API Orders:** Yesterday (YYYY-MM-DD) — real-time revenue/units
- **DataDive Niches:** X niches, X competitor records
- **Rank Radars:** X radars, X total keywords tracked
- **Keyword Scan:** 20 keywords — battleground positions (us + competitors), badges inline, new competitor detection. [X/20 returned data, Y/20 carried forward]
- **Competitor BSR Scan:** 34 ASINs via saswave — real-time BSR for all tracked competitors
- **Seller Board Dashboard:** 7-day aggregate only ([date range]) — lags ~2 days, day-specific excluded
- **Seller Board Detailed:** Per-ASIN actual revenue/units/profit ([date range]) — our products only
- **Sources:** Amazon SP-API (BSR, price, inventory, orders), DataDive API (Rank Radar, Competitors, rating/reviews), Apify (keyword scan + battleground), Seller Board (7-day aggregates + per-ASIN actuals)
```

---

## 📈 Trend Indicators

Use these consistently:

| Symbol | Meaning |
|--------|---------|
| 📈 | Improving (BSR went DOWN = better) |
| 📉 | Declining (BSR went UP = worse) |
| ➡️ | Stable (change < 5%) |
| ↑ X | Improved by X positions |
| ↓ X | Declined by X positions |
| — | No change or no data |

**Remember:** LOWER BSR = BETTER (closer to #1)

---

## ⚠️ Error Handling

| Issue | Action |
|-------|--------|
| SP-API auth failure | Check SP_API credentials in .env, note in report, fall back to DataDive for BSR |
| SP-API rate limit (429) | Wait 2s and retry once, then skip ASIN, note in report |
| SP-API timeout on one ASIN | Skip that ASIN, continue with next, note in report |
| Apify keyword scan timeout | STOP, use data collected, note in report |
| Apify returns empty dataset for valid keyword | Carry forward battleground positions AND badge data from previous snapshot; mark as "(prev day)" in report. Do NOT retry — actor reliability varies |
| SP-API Orders fails | Skip "Yesterday's Business" section, note in report |
| DataDive API fails | Note in report, use previous snapshot data |
| Seller Board fails | Skip "7-Day Financial Snapshot" section, note in report |
| No baseline | Create baseline first |
| Missing yesterday | Compare to baseline only |
| Hero rating/reviews not in DataDive | Carry forward from previous snapshot or baseline |

**NEVER wait indefinitely.** Partial data > No report.

---

## 📝 Baseline Rules

1. **Baseline date:** 2026-02-11
2. **Baseline file:** `snapshots/baseline.json` (copy of first snapshot)
3. **All future reports compare to baseline**
4. **Baseline never changes** unless explicitly requested

---

## ✅ Execution Checklist

All steps should run in **parallel where possible** to minimize wall-clock time.

**Phase 1 — Load Context (sequential, fast)**
- [ ] **Snapshot Discovery:**
  1. Glob for `snapshots/YYYY-MM-DD*.json` files (most recent first)
  2. Skip files matching today's date (don't compare to self)
  3. Use the most recent file found as "previous snapshot"
  4. If no previous snapshot exists, use `snapshots/baseline.json`
  5. Note the gap: if >1 day, label columns "vs [date]" not "vs yesterday"
  6. Include in report header: `**Previous Snapshot:** YYYY-MM-DD (X days ago)`
- [ ] Load baseline from `snapshots/baseline.json` (always, for "vs baseline" comparison)
- [ ] Re-read `context/competitors.md` for latest competitor ASINs
- [ ] Re-read `context/search-terms.md` for latest keywords (if scan keywords change)

**Phase 2 — Fetch All Data (parallel — launch all at once)**
- [ ] **SP-API:** `get_catalog_item` × 13 hero ASINs (BSR + subcategory rank)
- [ ] **SP-API:** `get_competitive_pricing` × 13 hero ASINs (current price)
- [ ] **SP-API:** `get_fba_inventory` × 1 call (stock levels for OOS alerts)
- [ ] **SP-API:** `get_orders(date=yesterday)` × 1 call (yesterday's revenue + units, real-time)
- [ ] **Apify:** Keyword scan (20 keywords) + Competitor BSR scan (34 ASINs) — agent returns `keyword_battleground` + `badges_found` + `new_competitors` + `competitor_bsr`
- [ ] **DataDive:** Fetch Rank Radar data for 10 hero product radars: B08DDJCQKF + 9 others (skip B0B1927HCG, B0FHMRQWRX, B0DKD2S3JT, B092SW839H, B0F8QZZQQM, B09HVDNFMR)
- [ ] **DataDive:** Fetch competitor data for 11 niches, top 4 per niche (skip retired niches — see Step 3)
- [ ] **Seller Board:** Fetch daily dashboard report (for 7-day aggregates) AND sales detailed report (for per-ASIN actuals)

**Phase 3 — Compile Report (sequential)**
- [ ] Merge SP-API BSR/price data with SB per-ASIN actuals + DataDive rating/reviews
- [ ] Calculate changes vs yesterday AND vs baseline
- [ ] Build unified product table sorted by SB actual 7-day revenue
- [ ] Build keyword rank snapshot from Rank Radar data (top 20 movements)
- [ ] Build Keyword Battleground from Apify scan (20 keywords, us vs competitors, BSR from SP-API + Apify competitor scan, badges inline)
- [ ] Build competitor comparison tables per category (with real-time competitor BSR from Apify scan)
- [ ] Flag new competitors (unknown ASINs in top 5)
- [ ] Generate alerts (OOS, BSR spikes, wins, watches)
- [ ] Include "Yesterday's Business" from SP-API Orders (real-time)
- [ ] Include "7-Day Financial Snapshot" from Seller Board (aggregates only, no day-specific)
- [ ] Generate report in MANDATORY FORMAT
- [ ] Save snapshot for tomorrow
- [ ] Present summary to user

---

## 💡 Key Reminders

1. **DATA MUST BE CURRENT** — If it's not updated to the day, don't include it. This report = state of business TODAY.
2. **SP-API Orders for yesterday's revenue/units** — real-time, no lag. This replaces Seller Board for day-specific data.
3. **Seller Board = 7-day aggregates ONLY** — profit, margin, ad spend, TACoS. Never show Seller Board as "today's" data (it's 2 days old).
4. **SP-API is PRIMARY for hero BSR + price** — first-party, real-time data from Amazon
5. **DataDive is PRIMARY for keyword ranks** — do NOT use Apify keyword scan positions for rank tracking
6. **DataDive Competitors provides rating + reviews** for all products (hero + competitors)
7. **Apify agent handles TWO jobs** — 20-keyword battleground scan (badges inline, new competitor detection) + 34-ASIN competitor BSR scan
8. **Focus on OUR products first** — competitors are context
9. **BSR is relative** — always note the category
10. **Consistency matters** — same format every day
11. **Baseline is sacred** — the reference point for progress
12. **Lower BSR = Better** — we want numbers to go DOWN
13. **Run phases in parallel** — launch all data fetches simultaneously to hit ~10 min target
14. **If SP-API fails** — fall back to DataDive competitor BSR, don't block the report

---

## Step 7: Post Notifications

Read `.claude/skills/notification-hub/SKILL.md` → "Recipe: daily-market-intel".
Follow those instructions to post a summary to Slack.
If Slack MCP is unavailable, skip and note in run log.

---

## ⚠️ AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/daily-market-intel/LESSONS.md`.**

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
