---
name: daily-market-intel
description: Morning market intelligence report for hero products vs competitors with week-over-week tracking
triggers:
  - market check
  - morning market
  - how are my products doing
  - market intel
  - daily market
  - product pulse
output_location: outputs/research/market-intel/
---

# Daily Market Intelligence

**USE WHEN** user says: "market check", "morning market", "how are my products doing", "market intel", "daily market", "product pulse"

---

## What This Does

Provides a daily morning briefing on your hero products' Amazon performance:
- **Current rankings** and BSR (Best Seller Rank) for each hero product
- **Competitor comparison** - how you stack up against top competitors in each category
- **Week-over-week trends** - are you gaining or losing ground?
- **Sales velocity signals** - review count changes, ranking movements
- **Market alerts** - significant competitor moves, price changes, new entrants

---

## ⚡ Organization & Efficiency Standards

**CRITICAL: Follow these standards for EVERY run:**

### File Organization
```
market-intel/
├── briefs/          # Daily briefs (MAIN OUTPUT - user reads these)
├── reports/         # Detailed analysis (products/ and competitors/)
├── data/            # Raw JSON data (products/, competitors/, search/)
├── snapshots/       # Historical comparison data
└── scripts/         # Python/automation scripts ONLY
```

### Naming Conventions (STRICT)
- **Briefs:** `YYYY-MM-DD-{time}.md` (e.g., `2026-02-09-morning.md`)
- **Product reports:** `{product-slug}-YYYY-MM-DD.md`
- **Competitor reports:** `{category-slug}-YYYY-MM-DD.md`
- **Data files:** `{type}-{slug}-YYYY-MM-DD.json`
- **Snapshots:** `YYYY-MM-DD-{time}.json`

### Efficiency Targets
- ✅ **<80K tokens** per run
- ✅ **<$0.20 cost** (Apify + processing)
- ✅ **<5 minutes** end-to-end
- ✅ **No temp files** in root folder
- ✅ **No duplicate files** with confusing names
- ✅ **1 brief per run** (main output)
- ✅ **1 snapshot per run** (for tomorrow's comparison)

### What to Create
**Every morning check:**
- `briefs/YYYY-MM-DD-morning.md` ← User reads this FIRST
- `snapshots/YYYY-MM-DD-morning.json` ← For tomorrow's comparison

**Only if requested:**
- Detailed product reports in `reports/products/`
- Detailed competitor reports in `reports/competitors/`

**Automatically organized:**
- Raw data files in `data/` subfolders

**NEVER in root folder:**
- ❌ Python scripts (go to `scripts/`)
- ❌ Temp files
- ❌ Test files
- ❌ Data files (go to `data/`)

---

## Data Sources

| Source | What We Get | How |
|--------|-------------|-----|
| **Apify** | Amazon product data (price, BSR, reviews, rating, rank) | `apify/amazon-product-scraper` or `junglee/amazon-product-scraper` |
| **context/hero-products.md** | Your hero product ASINs | Local file |
| **context/competitors.md** | Competitor brands and market context | Local file |
| **Historical snapshots** | Previous day/week data for comparison | `outputs/research/market-intel/history/` |

---

## Process

### Phase 1: Load Context

1. Read `context/hero-products.md` to get hero product ASINs
2. Read `context/competitors.md` to understand competitive landscape
3. Check for yesterday's snapshot in `outputs/research/market-intel/history/`

### Phase 2: Collect Fresh Data

**For each hero product ASIN:**

Use Apify's Amazon Product Scraper to get:
```json
{
  "asin": "B09THLVFZK",
  "title": "...",
  "price": 34.99,
  "bsr": 12453,
  "bsr_category": "Arts, Crafts & Sewing",
  "sub_category_rank": 45,
  "sub_category": "Fuse Beads",
  "rating": 4.7,
  "review_count": 2847,
  "in_stock": true
}
```

**Apify Actor to use:**
- Primary: `junglee/amazon-product-scraper` (reliable, fast)
- Alternative: `apify/amazon-product-scraper`

**Input format:**
```json
{
  "asins": ["B09THLVFZK", "B0DC69M3YD", "B08DDJCQKF", ...],
  "country": "US"
}
```

### Phase 3: Competitor Analysis

**REQUIRED: Automatically include top 3-4 competitors for each hero product category.**

**Competitor Metrics to Track:**
For EACH competitor, check and report:
- ✅ **BSR** - Current Best Seller Rank
- ✅ **BSR change** - vs yesterday (if baseline exists)
- ✅ **Price** - Current price
- ✅ **Price change** - Any deals or promotions vs yesterday
- ✅ **Reviews** - Total review count
- ✅ **Review velocity** - New reviews since yesterday
- ✅ **Rating** - Star rating
- ✅ **Category rank** - Position in category
- ✅ **Market share estimate** - Based on BSR + category rank

**Competitor Report Must Include:**
1. **New deals** - Any price drops, Lightning Deals, coupons
2. **Boosted review count** - Significant review increases (>5% in 24h)
3. **Last night performance** - BSR improvements/declines
4. **Market share shifts** - Are they gaining ground on us?

**Competitor ASINs to Track by Category:**

| Category | Our ASIN(s) | Competitor Brand | Competitor ASIN(s) |
|----------|-------------|------------------|-------------------|
| **Cross Stitch (Kids)** | B08DDJCQKF | Pllieay | B08T5QC9FS |
| | | KRAFUN | B0B7JHN4F1 |
| | | Caydo | B0CM9JKNCC |
| | | EZCRA | B0DFHN42QB |
| **Embroidery (Kids)** | B09X55KL2C | CraftLab | B087DYHMZ2 |
| | | KRAFUN | B0D8171TF1 |
| | | Pllieay | B08TC7423N |
| | | Louise Maelys | B0DP654CSV |
| **Embroidery (Adults)** | B0DC69M3YD | CYANFOUR | B0CZHKSSL4, B0DMHY2HF3 |
| | | Santune | B0BB9N74SG |
| | | Bradove | B0B762JW55 |
| | | ETSPIL | B0C3ZVKB46 |
| **Sewing (Kids)** | B09WQSBZY7, B096MYBLS1 | KRAFUN | B091GXM2Y6, B0C2XYP6L3, B0CV1F5CFS |
| | | EZCRA | B0CXY8JMTK, B0CYNNT2ZT |
| | | Klever Kits | B0CTTMWXYP |
| **Latch Hook** | B08FYH13CL, B0F8R652FX | LatchKits | B06XRRN4VL, B0CX9H8YGR |
| **Loom Knitting** | B0F8DG32H5 | Creativity for Kids | B004JIFCXO |
| | | Hapinest | B0B8W4FK4Q |
| **Mini Fuse Beads** | B09THLVFZK | INSCRAFT | B0C5WQD914 |
| | | ARTKAL | B0FN4CT867 |
| | | LIHAO | B08QV9CMFQ |
| | | FUNZBO | B0D5LF666P |
| **Lacing Cards** | B0FQC7YFX6 | Melissa & Doug | B00JM5G05I |
| | | KRAFUN | B0BRYRD91V |
| | | Serabeena | B0D178S25M |

### Phase 4: Calculate Changes

Compare today's data against:
1. **Yesterday** (daily delta)
2. **7 days ago** (weekly trend)
3. **Competitors** (relative position)

**Metrics to calculate:**
```
bsr_change_daily = today.bsr - yesterday.bsr
bsr_change_weekly = today.bsr - week_ago.bsr
review_velocity = (today.reviews - yesterday.reviews) / 1  # reviews per day
rank_vs_competitor = your_bsr - competitor_bsr  # negative = you're winning
```

### Phase 5: Generate Report

---

## Output Format

### Daily Market Intel Report

```markdown
# Market Intel - [DATE]

## Quick Summary

| Status | Count |
|--------|-------|
| Gaining Ground | 5 products |
| Stable | 4 products |
| Slipping | 2 products |
| Alert | 1 product |

---

## Hero Products Performance

### [Product Name] - [ASIN]

| Metric | Today | Yesterday | Weekly | Trend |
|--------|-------|-----------|--------|-------|
| BSR | 12,453 | 13,102 | 15,234 | Improving |
| Category Rank | #45 | #48 | #52 | Improving |
| Price | $34.99 | $34.99 | $34.99 | Stable |
| Reviews | 2,847 | 2,841 | 2,798 | +6/day |
| Rating | 4.7 | 4.7 | 4.7 | Stable |

**vs Competitors:**
- You: BSR 12,453 (Rank #1 in category)
- INSCRAFT: BSR 18,234 (Rank #2) - you're ahead by 5,781
- ARTKAL: BSR 22,456 (Rank #3)

**Status: GAINING GROUND**

---

[Repeat for each hero product]

---

## Alerts

| Product | Alert | Details |
|---------|-------|---------|
| Fairy Sewing Kit | COMPETITOR PRICE DROP | KRAFUN dropped price by $3 |
| Cross Stitch Girls | BSR SPIKE | Jumped 2,000 ranks - investigate |

---

## Competitor Movements

| Competitor | Category | Change | Impact |
|------------|----------|--------|--------|
| KRAFUN | Kids Sewing | Price drop $3 | Monitor |
| LatchKits | Latch Hook | New product launch | Research |

---

## Recommendations

1. **Capitalize on momentum** - Mini Fuse Beads showing strong improvement, consider PPC boost
2. **Investigate alert** - Cross Stitch Girls BSR spike needs review
3. **Competitive response** - Monitor KRAFUN price change impact this week
```

---

## File Storage

### Daily Snapshot
Save raw data to: `outputs/research/market-intel/history/[YYYY-MM-DD].json`

```json
{
  "date": "2026-02-08",
  "hero_products": {
    "B09THLVFZK": {
      "title": "48 Mini Fuse Beads Kit",
      "bsr": 12453,
      "category_rank": 45,
      "price": 34.99,
      "reviews": 2847,
      "rating": 4.7,
      "in_stock": true
    }
  },
  "competitors": {
    "B0XXXXXX": {...}
  }
}
```

### Daily Report
Save report to: `outputs/research/market-intel/daily-report-[YYYY-MM-DD].md`

---

## Execution Checklist

When user triggers this skill:

- [ ] Load hero product ASINs from `context/hero-products.md`
- [ ] Load competitor context from `context/competitors.md`
- [ ] Check for previous snapshots in history folder
- [ ] Use Apify to scrape fresh Amazon data for all hero ASINs
- [ ] Use Apify to scrape top 2-3 competitor products per category
- [ ] Calculate daily and weekly deltas
- [ ] Generate comparison against competitors
- [ ] Identify any alerts (significant changes)
- [ ] Generate markdown report
- [ ] Save snapshot to history
- [ ] Save report to daily reports
- [ ] Present summary to user

---

## Hero Products Reference

Quick reference of ASINs to track (from hero-products.md):

| # | Product | ASIN | Category |
|---|---------|------|----------|
| 1 | 48 Mini Fuse Beads | B09THLVFZK | Fuse Beads |
| 2 | 4 Embroidery Flowers Kit | B0DC69M3YD | Embroidery |
| 3 | Cross Stitch Kit - Girls | B08DDJCQKF | Cross Stitch |
| 4 | 10 Embroidery Patterns Kit | B09X55KL2C | Embroidery |
| 5 | Knitting Kit - Cat & Hat | B0F8DG32H5 | Knitting |
| 6 | Latch Hook - Rainbow Heart | B0F8R652FX | Latch Hook |
| 7 | Latch Hook Pencil Cases | B08FYH13CL | Latch Hook |
| 8 | Fairy Sewing Kit | B09WQSBZY7 | Sewing |
| 9 | Princess Lacing Card Kit | B0FQC7YFX6 | Lacing |
| 10 | Needlepoint Cat Wallet | B09HVSLBS6 | Needlepoint |
| 11 | Dessert Sewing Kit | B096MYBLS1 | Sewing |
| 12 | 10mm Big Fuse Beads | B07D6D95NG | Fuse Beads |
| 13 | Felt Unicorn Cross Stitch | B0DFPQ5LGD | Cross Stitch |

---

## API Costs Consideration

**Apify usage:**
- Amazon Product Scraper: ~$0.01-0.02 per product
- 13 hero products + ~20 competitors = ~33 products
- Daily cost estimate: ~$0.50-1.00

**Recommendation:** Run full competitor scan weekly, hero products daily.

---

## Error Handling

| Issue | Action |
|-------|--------|
| Apify rate limit | Wait and retry after 60s |
| Product not found | Flag in report, skip product |
| No historical data | Mark as "First run - no comparison" |
| Price/BSR = 0 | Product may be out of stock, flag it |

---

## Limitations & Future Improvements

**Current limitations:**
- No direct sales data access (would need Amazon Seller Central API)
- BSR is a proxy for sales velocity, not actual units
- Review velocity is slow-moving metric

**Future improvements to consider:**
- Add Seller Board integration for actual sales data
- Track search ranking for specific keywords (not just BSR)
- Add advertising performance data
- Weekly email summary via notification

---

## Notes

- Always ask before running if API costs are a concern
- First run will have no comparison data - that's expected
- Run consistently at same time each day for accurate trending
- Consider running at 6-7 AM before work to have fresh data
