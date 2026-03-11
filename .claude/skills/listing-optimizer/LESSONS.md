# Listing Optimizer — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`, `context/tooling-workarounds.md`
> Run log archive → `outputs/research/listing-manager/run-logs/`

## Skill-Specific Lessons

1. Combined audit+creator in single session is very efficient — no duplicate data fetching
2. When SKU not in sku-asin-mapping.json, use SP-API identifiers search
3. For #1 ranked hero products, always include a risk assessment section — listing changes carry medium risk
4. Launch-stage products often have listings written for humans (benefit copy) but not for Amazon algorithm (keyword indexing)
5. Products can rank for keywords not in listing via category cross-indexing — adding them explicitly amplifies the signal
6. Emoji decorators in bullets waste space that should be keyword-indexed text
7. Oldest products (launched 2020) have most room for improvement
8. Competitor brand names in titles are a real trademark risk — always flag
9. Backend keywords at 42% usage is the worst seen — easy massive win every time
10. Subagent approach for large MKL/Roots/RankRadar files works well

## Known Issues

### 1. DataDive AI Copywriter returns HTTP 400 on all modes (x2)
All 4 modes (cosmo, ranking-juice, nlp, cosmo-rufus) fail. Skip and use manual analysis.

### 2. Apify saswave scraper intermittently fails
Returns HTTP 400. Proceed with DataDive data + context/competitors.md when it fails.

### 3. New/recently launched products may not be tracked in DataDive niche
No Ranking Juice score, no organic rank data. Use word-level keyword coverage analysis instead. Recommend user add to DataDive.

### 4. DataDive niche mismatch for 4 Embroidery Flowers (gfot2FZUBU)
Niche contains mostly kids' cross stitch, not adult embroidery. MKL ranks compare against wrong competitors. Ranking Juice % still valid.

### 5. Amazon SKU may differ from internal catalog SKU
CC48 ≠ RV-FA22-4WFQ. Always check Seller Board for real Amazon SKU before `get_listing`.

## Repeat Errors

### 1. OneDrive EEXIST (x5)
See `context/tooling-workarounds.md`.

## Resolved Issues

_None yet._

## Recent Runs (last 3)

### Run: 2026-03-06 (f) — Latch Hook Pencil Cases
**Result:** Success — RJ 55.6%, title only 49% chars used, backend 38% used. Oldest product (2020), never optimized.

### Run: 2026-03-06 (e) — Princess Lacing Cards
**Result:** Success — Bullets have ZERO Ranking Juice. 3 missing high-BSV roots (sewing/toy/threading).

### Run: 2026-03-06 (d) — 10mm Big Fuse Beads
**Result:** Success — RJ 24.6% (#8 in niche, near bottom). Backend 42% usage (worst seen).
