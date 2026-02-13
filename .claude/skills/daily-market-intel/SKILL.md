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

## ⚠️ CORE PURPOSE

**This skill tracks ONE thing: Are we improving or declining?**

Every daily report answers:
1. What is our current BSR and rank?
2. What is our position vs competitors?
3. Did we improve or decline since yesterday?
4. Did we improve or decline since baseline (2026-02-11)?

**The baseline (2026-02-11) is the reference point for all future reports.**

---

## 📊 Category Difficulty Context

**IMPORTANT:** Not all categories are equal. Rankings must be interpreted in context.

| Category | Difficulty | Why |
|----------|------------|-----|
| **Toys & Games** | 🔴 HARD | Massive category, millions of products, intense competition |
| **Arts, Crafts & Sewing** | 🟡 MEDIUM | Smaller category, easier to rank well |

**What this means:**
- BSR 5,000 in Toys & Games = EXCELLENT (top 0.01%)
- BSR 5,000 in Arts & Crafts = GOOD (top 0.1%)
- A product in Toys & Games with BSR 10,000 may be selling MORE than one in Arts & Crafts with BSR 5,000

**Always note the category when reporting BSR.**

---

## 📁 File Organization

```
market-intel/
├── briefs/              # Daily reports (user reads these)
│   └── YYYY-MM-DD.md    # One per day, consistent format
├── snapshots/           # Raw data for comparison
│   └── YYYY-MM-DD.json  # One per day
└── baseline.json        # The baseline snapshot (2026-02-11)
```

---

## 🔧 Apify Scraper Settings

**Actor:** `saswave/amazon-product-scraper`
**Cost:** $0.001 per product
**Success Rate:** 95%+

**Input format:**
```json
{
  "asins": ["B08DDJCQKF", "B09WQSBZY7"],
  "amazon_domain": "www.amazon.com"
}
```

**Output fields we use:**
| Field | What It Contains |
|-------|------------------|
| `bestsellerRanks` | Array with BSR in main category + subcategory |
| `stars` | Rating (e.g., "4.5") |
| `reviewsCount` | Number of reviews |
| `price` | Current price |
| `availability` | In stock or not |

**Batching Rules:**
| Rule | Requirement |
|------|-------------|
| Max ASINs per call | **5 ASINs** (never more) |
| On timeout | STOP immediately, use data collected |
| Mode | `async: true` then check results (don't block)

---

## 📋 MANDATORY REPORT FORMAT

**Every daily report MUST follow this exact format:**

```markdown
# Market Intel - [DATE]

**Baseline:** 2026-02-11 | **Days Since Baseline:** [X]

---

## Summary

| Metric | Count | vs Baseline |
|--------|-------|-------------|
| Products Improving (BSR ↓) | X | — |
| Products Declining (BSR ↑) | X | — |
| Products Stable | X | — |

---

## Our Products by Category

### [Amazon Category] - [Difficulty: 🔴 HARD / 🟡 MEDIUM]

| Product | ASIN | BSR | Subcategory Rank | Reviews | Rating | vs Baseline |
|---------|------|-----|------------------|---------|--------|-------------|
| [Name] | BXXXXXXXXX | #X,XXX | #X in [Subcategory] | X,XXX | X.X★ | ↑/↓ X,XXX |

**Notes:** [Any observations about this category]

---

[Repeat for each Amazon category: Arts Crafts & Sewing, Toys & Games]

---

## Competitor Comparison

### [Subcategory Name]

| Rank | Brand | ASIN | BSR | Subcat Rank | Reviews | vs Us |
|------|-------|------|-----|-------------|---------|-------|
| #1 | [Brand] | BXXX | #X,XXX | #X | X,XXX | We're ahead/behind |
| #2 | ... | ... | ... | ... | ... | ... |

**Our Position:** #X of Y

---

## Alerts

| Type | Product | Details |
|------|---------|---------|
| 🔴 BSR SPIKE | [Product] | BSR went from X to Y (+Z) |
| 🟡 WATCH | [Product] | [What to monitor] |
| 🟢 WIN | [Product] | [Good news] |

---

## Data Notes

- **Source:** Apify saswave/amazon-product-scraper
- **Products scraped:** X hero + X competitors
- **Missing data:** [List any that failed]
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

## 🎯 What to Track

### For Each Hero Product:
1. **BSR** - Best Seller Rank (lower = better)
2. **Category** - Which category it's in (affects interpretation)
3. **Position vs Competitors** - Are we #1, #2, #3 in our niche?
4. **Change vs Yesterday** - Daily movement
5. **Change vs Baseline** - Overall progress since tracking started

### For Each Competitor:
1. **BSR** - Their current rank
2. **Change** - Are they improving or declining?
3. **Gap to Us** - How far ahead/behind are we?

---

## 🏷️ Hero Products by Category

| Category | Amazon Category | Difficulty | Our Products |
|----------|-----------------|------------|--------------|
| **Cross Stitch** | Arts, Crafts & Sewing | 🟡 MEDIUM | B08DDJCQKF, B0F6YTG1CH |
| **Embroidery (Kids)** | Arts, Crafts & Sewing | 🟡 MEDIUM | B09X55KL2C |
| **Embroidery (Adults)** | Arts, Crafts & Sewing | 🟡 MEDIUM | B0DC69M3YD |
| **Sewing** | Toys & Games | 🔴 HARD | B09WQSBZY7, B096MYBLS1 |
| **Latch Hook** | Arts, Crafts & Sewing | 🟡 MEDIUM | B08FYH13CL, B0F8R652FX |
| **Knitting** | Arts, Crafts & Sewing | 🟡 MEDIUM | B0F8DG32H5 |
| **Fuse Beads** | Arts, Crafts & Sewing | 🟡 MEDIUM | B09THLVFZK, B07D6D95NG |
| **Lacing Cards** | Arts, Crafts & Sewing | 🟡 MEDIUM | B0FQC7YFX6 |
| **Needlepoint** | Arts, Crafts & Sewing | 🟡 MEDIUM | B09HVSLBS6 |

---

## 🏆 Key Competitors by Category

| Category | Competitor | ASIN | Notes |
|----------|------------|------|-------|
| **Cross Stitch** | Pllieay | B08T5QC9FS | Budget option |
| | EZCRA | B0DFHN42QB | Ages 5-8 focus |
| **Embroidery (Kids)** | CraftLab | B087DYHMZ2 | Award winner |
| **Embroidery (Adults)** | CYANFOUR | B0CZHKSSL4 | Market leader |
| **Sewing** | KRAFUN | B091GXM2Y6 | Dominant player |
| **Latch Hook** | LatchKits | B06XRRN4VL | Market leader |
| **Knitting** | Creativity for Kids | B004JIFCXO | Retail presence |
| **Fuse Beads** | INSCRAFT | B0C5WQD914 | Value leader |
| **Lacing Cards** | Melissa & Doug | B00JM5G05I | Brand leader |

---

## 🔍 Keyword Search Rankings

**Actor:** `igview-owner/amazon-search-scraper`
**Cost (BRONZE):** ~$0.09 per keyword (1 page)
**Daily budget:** ~$1.26 for 14 keywords (top 2 per category)

**Input format:**
```json
{
  "query": "kids cross stitch kit",
  "maxPages": 1,
  "country": "US",
  "language": "en_US",
  "sortBy": "RELEVANCE"
}
```

**Output fields we use:**
| Field | What It Contains |
|-------|------------------|
| `title` | Product title (match to our products) |
| `asin` | ASIN to match against hero/competitor lists |
| `position` | Rank position on the search results page |
| `badge` | Special badges like "Overall Pick", "Amazon's Choice" |

**Top 2 Keywords Per Category:**

| Category | Keyword 1 | Keyword 2 |
|----------|-----------|-----------|
| Cross Stitch | kids cross stitch kit | embroidery kit for kids |
| Embroidery Adults | embroidery kit for beginners | embroidery kits for adults |
| Sewing Kids | sewing kit for kids | kids sewing kit |
| Latch Hook | latch hook kits for kids | latch kits |
| Fuse Beads | mini perler beads | mini fuse beads |
| Knitting | loom knitting kit | knitting kit for kids |
| Lacing Cards | lacing cards | lacing cards for kids ages 3-5 |

**Execution notes:**
- Run keyword searches AFTER BSR scraping
- Some keywords may return empty results on first try — re-run failed ones once
- "loom knitting kit" and "lacing cards" have been unreliable (scraper limitation)
- Results show position on page 1 only (maxPages: 1)
- Track our position AND top competitor position for each keyword
- First keyword baseline: 2026-02-12

---

## ⚠️ Error Handling

| Issue | Action |
|-------|--------|
| Apify timeout | STOP, use data collected, note in report |
| Batch fails | Skip batch, continue, note in report |
| No baseline | Create baseline first |
| Missing yesterday | Compare to baseline only |

**NEVER wait indefinitely.** Partial data > No report.

---

## 📝 Baseline Rules

1. **Baseline date:** 2026-02-11
2. **Baseline file:** `snapshots/baseline.json` (copy of first snapshot)
3. **All future reports compare to baseline**
4. **Baseline never changes** unless explicitly requested

---

## ✅ Execution Checklist

- [ ] Load previous snapshot (yesterday or baseline)
- [ ] Scrape hero products (batches of 5, async mode)
- [ ] Scrape key competitors (batches of 5, async mode)
- [ ] Calculate changes vs yesterday AND vs baseline
- [ ] Note category difficulty for each product
- [ ] Run keyword searches (top 2 per category, 14 total)
- [ ] Re-run any failed keyword searches once
- [ ] Generate report in MANDATORY FORMAT (BSR + keyword rankings)
- [ ] Save snapshot for tomorrow
- [ ] Present summary to user

---

## 💡 Key Reminders

1. **Focus on OUR products first** - competitors are context
2. **BSR is relative** - always note the category
3. **Consistency matters** - same format every day
4. **Baseline is sacred** - the reference point for progress
5. **Lower BSR = Better** - we want numbers to go DOWN
