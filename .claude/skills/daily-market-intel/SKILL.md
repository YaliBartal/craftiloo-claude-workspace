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

## 📊 BSR Normalization & Sales Velocity

**IMPORTANT:** BSR is NOT comparable across categories without normalization. A product in Toys & Games with BSR 10,000 sells MORE than one in Arts & Crafts with BSR 5,000.

**Sales Velocity Reference Points:**

| BSR | Toys & Games (Est. Daily Sales) | Arts, Crafts & Sewing (Est. Daily Sales) |
|-----|--------------------------------|------------------------------------------|
| 1,000 | ~2,500 | ~1,700 |
| 5,000 | ~1,000 | ~680 |
| 10,000 | ~570 | ~390 |
| 25,000 | ~250 | ~170 |
| 50,000 | ~130 | ~90 |
| 100,000 | ~65 | ~45 |

**Category multiplier:** Toys & Games BSR ≈ 1.46x the sales velocity of Arts, Crafts & Sewing at the same BSR.

**HOW TO USE THIS:** When reporting, present ALL products in a **single unified table** sorted by estimated daily sales (highest to lowest). This lets the user instantly see which products are actually selling the most, regardless of category.

**Do NOT split products into separate Toys & Games vs Arts & Crafts tables.** One list, sorted by sales velocity.

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

## Our Products (Unified by Sales Velocity)

| # | Product | ASIN | Category | BSR | Est. Daily Sales | Subcat Rank | Reviews | Rating | vs Yesterday | vs Baseline |
|---|---------|------|----------|-----|-----------------|-------------|---------|--------|-------------|-------------|
| 1 | [Top seller] | BXXX | T&G / AC&S | #X,XXX | ~XXX | #X in [Sub] | X,XXX | X.X★ | ↑/↓ X | ↑/↓ X |
| 2 | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

*Sorted by Est. Daily Sales (highest → lowest). Use BSR-to-sales reference table for conversion.*

**Notes:** [Observations about movers, trends, anomalies]

---

## Competitor Comparison

### [Subcategory Name]

| Rank | Brand | ASIN | BSR | Subcat Rank | Reviews | vs Us |
|------|-------|------|-----|-------------|---------|-------|
| #1 | [Brand] | BXXX | #X,XXX | #X | X,XXX | We're ahead/behind |
| #2 | ... | ... | ... | ... | ... | ... |

**Our Position:** #X of Y

---

## New / Rising Competitors

| Niche | Brand | ASIN | Found On Keyword | Position | BSR | Reviews | Alert |
|-------|-------|------|-----------------|----------|-----|---------|-------|
| [Category] | [Brand] | BXXX | [keyword] | #X | #X,XXX | X | 🆕 New / 📈 Rising |

*No new competitors detected* (if none found)

---

## Alerts

| Type | Product | Details |
|------|---------|---------|
| 🔴 BSR SPIKE | [Product] | BSR went from X to Y (+Z) |
| 🟡 WATCH | [Product] | [What to monitor] |
| 🟢 WIN | [Product] | [Good news] |
| 🆕 NEW COMPETITOR | [Product] | [Brand] appearing at #X for [keyword] |

---

## Data Notes

- **Source:** Apify saswave/amazon-product-scraper
- **Products scraped:** X hero + X competitors (all with ASINs from competitors.md)
- **Keywords searched:** 27 (top 3 × 9 categories)
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

## 🏆 Competitor Scraping — ALL ASINs from competitors.md

**RULE: Scrape EVERY competitor that has an ASIN in `context/competitors.md`.** Skip competitors with "—" (no ASIN). This is mandatory — do not cherry-pick.

**Full competitor ASIN list (from competitors.md):**

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

**Total: ~31 unique competitor ASINs** (7 batches of 5, async mode)

**When competitors.md is updated with new ASINs, automatically include them in future runs.** Always re-read `context/competitors.md` at the start of each run to catch additions.

---

## 🆕 New Competitor Detection

**PURPOSE:** Identify new or rising competitors that aren't yet in `context/competitors.md`.

**HOW:** During the keyword search step (below), scan the top 10 results for each keyword. Flag any product that:
1. **Is NOT in our hero products list** AND **NOT in our competitors list**
2. **Ranks in the top 10** for one of our tracked keywords
3. **Has a BSR that's improving** (compare to previous run if available)

**What to look for:**
- New ASINs appearing in top search positions that weren't there before
- Products with low review counts but high rankings (suggests rapid sales velocity — new entrant gaining traction)
- Products from brands not in `context/competitors.md`

**Report format (add to daily brief):**

```markdown
## New / Rising Competitors

| Niche | Brand | ASIN | Found On Keyword | Position | BSR | Reviews | Alert |
|-------|-------|------|-----------------|----------|-----|---------|-------|
| [Category] | [Brand] | BXXX | [keyword] | #X | #X,XXX | X | 🆕 New / 📈 Rising |
```

**If new competitors are found:**
- Flag them in the Alerts section as 🟡 WATCH
- If they appear in 2+ consecutive daily runs, suggest adding them to `context/competitors.md`

**If no new competitors found:** Simply note "No new competitors detected" in the report.

---

## 🔍 Keyword Search Rankings

**Actor:** `igview-owner/amazon-search-scraper`
**Cost (BRONZE):** ~$0.09 per keyword (1 page)
**Daily budget:** ~$1.89 for 21 keywords (top 3 per category)

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

**Top 3 Keywords Per Category (from `context/search-terms.md`):**

| Category | Keyword 1 | Keyword 2 | Keyword 3 |
|----------|-----------|-----------|-----------|
| Cross Stitch | embroidery kit for kids | kids cross stitch kit | beginner cross stitch kits for kids |
| Embroidery Kids | kids embroidery kit | embroidery kit for beginners kids | kids embroidery kits ages 8-12 |
| Embroidery Adults | embroidery kit for beginners | embroidery kits for adults | needle point kits adults |
| Sewing Kids | sewing kit for kids | kids sewing kit | sewing kits for kids 8-12 |
| Latch Hook | latch hook kits for kids | hook rug kits for kids | latch kits |
| Fuse Beads | mini perler beads | mini beads | mini fuse beads |
| Knitting | loom knitting kit | knitting loom kit | knitting kit for kids |
| Lacing Cards | lacing cards | lacing cards for kids ages 3-5 | lacing cards for kids ages 4-8 |
| Needlepoint | needlepoint kits for kids | kids needlepoint kit | beginner cross stitch kits for kids |

**Total: 27 keyword searches** (9 categories × 3 keywords)

**IMPORTANT:** Always pull keywords from `context/search-terms.md` — if the file is updated with better terms, use those instead of the hardcoded list above.

**Execution notes:**
- Run keyword searches AFTER BSR scraping
- Some keywords may return empty results on first try — re-run failed ones once
- "loom knitting kit" and "lacing cards" have been unreliable (scraper limitation)
- Results show position on page 1 only (maxPages: 1)
- Track our position AND top competitor position for each keyword
- **Scan top 10 results for unknown ASINs** (feeds New Competitor Detection)
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
- [ ] Re-read `context/competitors.md` to get latest competitor ASINs
- [ ] Re-read `context/search-terms.md` to get latest top 3 keywords per category
- [ ] Scrape hero products (batches of 5, async mode)
- [ ] Scrape ALL competitors with ASINs (~31 ASINs, ~7 batches of 5, async mode)
- [ ] Calculate estimated daily sales velocity for each product (use BSR reference table)
- [ ] Calculate changes vs yesterday AND vs baseline
- [ ] Build unified product table sorted by estimated daily sales (single list, not split by category)
- [ ] Run keyword searches (top 3 per category, 27 total)
- [ ] Re-run any failed keyword searches once
- [ ] Scan keyword results for new/unknown competitors (New Competitor Detection)
- [ ] Generate report in MANDATORY FORMAT (unified BSR + keywords + new competitors)
- [ ] Save snapshot for tomorrow
- [ ] Present summary to user

---

## 💡 Key Reminders

1. **Focus on OUR products first** - competitors are context
2. **BSR is relative** - always note the category
3. **Consistency matters** - same format every day
4. **Baseline is sacred** - the reference point for progress
5. **Lower BSR = Better** - we want numbers to go DOWN
