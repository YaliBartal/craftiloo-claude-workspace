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

## 📊 Sales Data — Use DataDive Only

**DO NOT estimate sales from BSR.** BSR-to-sales tables are wildly inaccurate for our category/volume.

**Primary sales source:** DataDive Competitor data (`sales` field = Jungle Scout monthly estimate)
- Use `dd_sales_mo` as the sales metric
- Convert to daily: `dd_sales_mo / 30`
- For hero products not found in DataDive niches, show "—" (no estimate)

**Sort the unified product table by DataDive monthly sales** (highest to lowest). Products without DataDive data go at the bottom.

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

**Four data sources, each with a clear job:**
1. **Amazon SP-API** — First-party BSR, pricing, and inventory for our hero products (fast, free, reliable)
2. **DataDive** — Keyword rankings (Rank Radar) + competitor intelligence (sales, revenue, rating, reviews)
3. **Apify** — Lightweight keyword scan ONLY (badges + new competitor detection)
4. **Seller Board** — Account financials (revenue, profit, margins)

| Data Need | Primary Source | Fallback |
|-----------|---------------|----------|
| Hero BSR + subcategory rank | **Amazon SP-API** `get_catalog_item` | DataDive competitors |
| Hero price | **Amazon SP-API** `get_competitive_pricing` | DataDive competitors |
| Hero stock levels / OOS alerts | **Amazon SP-API** `get_fba_inventory` | Seller Board inventory |
| Hero rating + reviews | **DataDive Competitors** (hero appears in niche data) | Previous snapshot |
| Competitor BSR, price, rating, reviews | **DataDive Competitors** | Previous snapshot |
| Our keyword rankings | **DataDive Rank Radar** | — |
| Our sponsored/PPC rank | **DataDive Rank Radar** | — |
| Keyword search volume | **DataDive Rank Radar + MKL** | — |
| Keyword rank movements | **DataDive Rank Radar** | — |
| Competitor sales estimates | **DataDive Competitors** | BSR-to-sales table |
| Competitor revenue | **DataDive Competitors** | Manual (price × units) |
| Competitor P1 keywords | **DataDive Competitors** | — |
| New competitor detection | **Apify light keyword scan** (9 keywords) | DataDive niche changes |
| Badge tracking | **Apify light keyword scan** | — |
| Account financials | **Seller Board dashboard** | — |

### Performance Targets

| Metric | Target |
|--------|--------|
| Total tokens | **~140K** |
| Wall-clock time | **~10 min** |
| Apify cost/day | **~$0.81** (keyword scan only) |
| SP-API calls | **~27** (13 catalog + 13 pricing + 1 inventory) |
| Keywords searched (Apify) | **9** |

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

**Phase B — Inventory (single call):**
3. Call `get_fba_inventory()` once → returns stock levels for ALL our FBA products
4. Match by ASIN to hero product list → flag any with `totalQuantity = 0` as OOS

**Total calls:** 13 + 13 + 1 = **27 calls** (~15 seconds with rate limiting)

### Competitor Data — NOT fetched here

**Competitor BSR, price, rating, and reviews are all provided by DataDive Competitors in Step 3.** No separate scraping needed for competitors.

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
| **Latch Hook** | LatchKits | B06XRRN4VL, B0CX9H8YGR |
| **Knitting** | Creativity for Kids | B004JIFCXO |
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

Fetch radars for these hero product ASINs:
- B09X55KL2C (Embroidery Kids) — 55 keywords
- B0DC69M3YD (Embroidery Adults) — 67 keywords
- B09WQSBZY7 (Fairy Sewing Kit) — 87 keywords
- B096MYBLS1 (Dessert Sewing Kit) — 50 keywords
- B08FYH13CL (Latch Hook Pencil Cases) — 53 keywords
- B0F8DG32H5 (Knitting Cat & Hat) — 81 keywords
- B09THLVFZK (Mini Fuse Beads) — 18 keywords
- B07D6D95NG (10mm Big Fuse Beads) — 38 keywords
- B0FQC7YFX6 (Princess Lacing Card) — 52 keywords

**Also fetch if available** (non-hero but useful):
- B0B1927HCG (Cross Stitch Kits) — 38 keywords
- B0FHMRQWRX (Latch Hook Kit) — 50 keywords
- B0DKD2S3JT (Crochet/Knitting) — 50 keywords

**Skip these** (low value, save tokens):
- B092SW839H (Punch Needle) — 0 keywords in top 10
- B0F8QZZQQM (Cross Stitch Beginner) — volatile, not primary hero
- B09HVDNFMR (Needlepoint) — 0 keywords in top 10

### How to Fetch

1. Call `GET /v1/niches/rank-radars?pageSize=50` to list all radars
2. Match radars to hero ASINs using the `asin` field
3. For each matched radar, call `GET /v1/niches/rank-radars/{radarId}?startDate={yesterday}&endDate={today}`
4. Rate limit: 1.1 seconds between requests

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
**API:** `GET /v1/niches/{nicheId}/competitors?pageSize=50`

### Niche IDs to Fetch

| Niche ID | Label | Hero Products |
|----------|-------|---------------|
| b4Nisjv3xy | Cross Stitch Kits for Kids | B08DDJCQKF |
| Er21lin0KC | Beginners Embroidery Kit for Kids | B09X55KL2C |
| gfot2FZUBU | Embroidery Stitch Practice Kit | B0DC69M3YD |
| RmbSD3OH6t | Sewing Kit for Kids | B09WQSBZY7, B096MYBLS1 |
| VqBgB5QQ07 | Latch Hook Kit for Kids | B08FYH13CL, B0F8R652FX |
| AY4AlnSj9g | Mini Perler Beads | B09THLVFZK |
| O6b4XATpTj | Loom Knitting | B0F8DG32H5 |
| Aw4EQhG6bP | Lacing Cards for Kids | B0FQC7YFX6 |

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
| `advertisedKws` | Keywords being advertised |

**Use DataDive sales estimates as PRIMARY** (more accurate than BSR-to-sales table).

### Hero Product Rating & Reviews

DataDive competitor data includes our hero products (they appear in their niche competitor lists). Extract `rating` and `reviewCount` for hero ASINs here. If a hero product is not found in any niche (e.g., B07D6D95NG 10mm Fuse Beads, B09HVSLBS6 Needlepoint), carry forward from the previous day's snapshot or baseline.

---

## 🔍 Step 4: Light Apify Keyword Scan — New Competitors + Badges ONLY

**PURPOSE:** Ultra-lightweight Amazon search scan. **Only** for:
1. **New competitor detection** — find unknown ASINs in top 10
2. **Badge tracking** — check for Overall Pick, Amazon's Choice on our products

**This does NOT replace keyword ranking tracking** — that's handled by DataDive Rank Radar (Step 2).

**Actor:** `igview-owner/amazon-search-scraper`
**Cost:** ~$0.09 per keyword × 9 = **~$0.81/day**
**Time:** ~4-5 min

### Keywords to Scan (9 total — 1 per category, highest volume)

| Category | Keyword | Volume |
|----------|---------|--------|
| Cross Stitch | embroidery kit for kids | 13,067 |
| Embroidery Kids | kids embroidery kit | 5,802 |
| Embroidery Adults | embroidery kit for beginners | 103,524 |
| Sewing | sewing kit for kids | 20,874 |
| Latch Hook | latch hook kits for kids | 16,625 |
| Fuse Beads | mini perler beads | 3,242 |
| Knitting | loom knitting kit | 8,102 |
| Lacing Cards | lacing cards | 4,524 |
| Needlepoint | needlepoint kits for kids | 1,416 |

**Input format:**
```json
{
  "query": "embroidery kit for kids",
  "maxPages": 1,
  "country": "US",
  "language": "en_US",
  "sortBy": "RELEVANCE"
}
```

### What to Extract (minimal)

For each keyword result, only extract **top 10 results**:
- `asin` — to match against hero/competitor lists
- `position` — rank on page
- `badge` — Overall Pick, Amazon's Choice, etc.
- `title` — for identifying unknown products

### Processing

1. Compare each ASIN against hero product list and competitor list
2. **Unknown ASINs in top 10** → flag as potential new competitors
3. **Our products with badges** → note in report
4. **Do NOT track our keyword positions from this** — use DataDive Rank Radar instead

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

## 💰 Step 5: Seller Board Dashboard — Account Financials

**PURPOSE:** Account-level revenue, profit, margins. Provides business context for the market position data.

**Tool:** `get_daily_dashboard_report` (MCP)
**Time:** ~10 seconds

### Extract from Dashboard

| Metric | Column |
|--------|--------|
| Revenue | SalesOrganic + SalesPPC |
| Units | UnitsOrganic + UnitsPPC |
| Net Profit | NetProfit |
| Margin | Margin |
| Ad Spend | SponsoredProducts + SponsoredDisplay + SponsoredBrands + SponsoredBrandsVideo |
| TACoS | Ad Spend / Revenue × 100 |

Calculate: latest day, 7-day average, trend (first half vs second half of week).

**Note:** Seller Board data lags ~2 days. Always note the most recent date available.

### Fallback

If Seller Board fetch fails:
- Note: "Seller Board unavailable"
- Continue with market data — do NOT block the report

---

## 📋 MANDATORY REPORT FORMAT

**Every daily report MUST follow this exact format:**

```markdown
# Market Intel - [DATE]

**Baseline:** 2026-02-11 | **Days Since Baseline:** [X]

---

## Account Snapshot (from Seller Board)

| Metric | Latest ([date]) | 7-Day Avg | Trend |
|--------|----------|-----------|-------|
| Total Revenue | $X | $X/day | +X% |
| Total Units | X | X/day | +X% |
| Net Profit | $X | $X/day | +X% |
| Profit Margin | X% | X% | +X pp |
| Ad Spend | $X | $X/day | +X% |
| TACoS | X% | X% | +X pp |

---

## Summary

| Metric | Count | vs Baseline |
|--------|-------|-------------|
| Products Improving (BSR ↓) | X | X vs baseline |
| Products Declining (BSR ↑) | X | X vs baseline |
| Products Stable | X | X vs baseline |

---

## Our Products (Unified by DataDive Sales)

| # | Product | ASIN | Category | BSR | DD Sales/mo | DD Revenue/mo | Subcat Rank | Reviews | Rating | Price | vs Yesterday | vs Baseline |
|---|---------|------|----------|-----|------------|--------------|-------------|---------|--------|-------|-------------|-------------|

*Sorted by DataDive monthly sales (highest → lowest). Products without DD data at bottom. Do NOT estimate sales from BSR.*

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

## Competitor Comparison

### [Category Name]

| Rank | Brand/ASIN | BSR | Subcat Rank | Reviews | DD Sales/mo | vs Us |
|------|-----------|-------------|-------------|---------|-------------|-------|

**Our Position:** #X of Y

*One table per category: Cross Stitch, Embroidery Kids, Embroidery Adults, Sewing, Latch Hook, Fuse Beads, Knitting, Lacing Cards*

---

## Badges

| Product | ASIN | Keyword | Badge |
|---------|------|---------|-------|

*From Apify light keyword scan. Only show products with badges.*

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
- **SP-API Calls:** X catalog + X pricing + 1 inventory = X total
- **DataDive Niches:** X niches, X competitor records
- **Rank Radars:** X radars, X total keywords tracked
- **Light Keyword Scan:** 9 keywords (badges + new competitors only)
- **Seller Board Data:** [date range] (lags ~2 days)
- **Sources:** Amazon SP-API (BSR, price, inventory), DataDive API (Rank Radar, Competitors, rating/reviews), Apify (keyword scan), Seller Board
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
| DataDive API fails | Fall back to BSR-to-sales estimates, note in report |
| Seller Board fails | Skip Account Snapshot, note in report |
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
- [ ] Load previous snapshot (yesterday or baseline)
- [ ] Re-read `context/competitors.md` for latest competitor ASINs
- [ ] Re-read `context/search-terms.md` for latest keywords (if scan keywords change)

**Phase 2 — Fetch All Data (parallel — launch all at once)**
- [ ] **SP-API:** `get_catalog_item` × 13 hero ASINs (BSR + subcategory rank)
- [ ] **SP-API:** `get_competitive_pricing` × 13 hero ASINs (current price)
- [ ] **SP-API:** `get_fba_inventory` × 1 call (stock levels for OOS alerts)
- [ ] **Apify:** Light keyword scan (9 keywords, top 10 only)
- [ ] **DataDive:** Fetch Rank Radar data for hero product radars
- [ ] **DataDive:** Fetch competitor data for 8 niches (includes rating/reviews for all products)
- [ ] **Seller Board:** Fetch daily dashboard report

**Phase 3 — Compile Report (sequential)**
- [ ] Merge SP-API BSR/price data with DataDive sales estimates + rating/reviews
- [ ] Calculate changes vs yesterday AND vs baseline
- [ ] Build unified product table sorted by estimated daily sales
- [ ] Build keyword rank snapshot from Rank Radar data (top 20 movements)
- [ ] Build competitor comparison tables per category
- [ ] Extract badges from light keyword scan
- [ ] Flag new competitors (unknown ASINs in top 5)
- [ ] Generate alerts (OOS, BSR spikes, wins, watches)
- [ ] Include Account Snapshot from Seller Board
- [ ] Generate report in MANDATORY FORMAT
- [ ] Save snapshot for tomorrow
- [ ] Present summary to user

---

## 💡 Key Reminders

1. **SP-API is PRIMARY for hero BSR + price** — first-party, real-time data from Amazon
2. **DataDive is PRIMARY for keyword ranks** — do NOT use Apify keyword scan positions for rank tracking
3. **DataDive Competitors provides rating + reviews** for all products (hero + competitors)
4. **Apify keyword scan is ONLY for badges + new competitor detection** — keep it lightweight
5. **Focus on OUR products first** — competitors are context
6. **BSR is relative** — always note the category
7. **Consistency matters** — same format every day
8. **Baseline is sacred** — the reference point for progress
9. **Lower BSR = Better** — we want numbers to go DOWN
10. **Run phases in parallel** — launch all data fetches simultaneously to hit ~10 min target
11. **If SP-API fails** — fall back to DataDive competitor BSR, don't block the report

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
