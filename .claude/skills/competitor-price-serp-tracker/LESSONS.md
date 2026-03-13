# Competitor Price & SERP Tracker — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`, `context/tooling-workarounds.md`
> Run log archive → `outputs/research/competitor-analysis/run-logs/`

## Skill-Specific Lessons

1. Parallel launch of all Apify runs (3 product + 5 SERP) — all succeed in ~90 seconds
2. Python processing script approach avoids context window overflow from 5,052 SERP results
3. Axesso batching: 20-24 keywords per run. saswave: 31-33 ASINs per run
4. Script needs safe_float/safe_int for all numeric fields (null and string types common)
5. Our ASINs only appear in SERP results, not product scrape — use Seller Board for own price/BSR

## Known Issues

### 1. Price precision from saswave
Returns prices like $10.3231502. Round to 2 decimal places.

### 2. Uncategorized ASINs need mapping
66 uncategorized ASINs scraped but not assigned to any category.

## Repeat Errors

_None yet._

## Resolved Issues

_None yet._

## Recent Runs (last 3)

### Run: 2026-03-08 (BASELINE)
**Result:** Success — 97 products, 103 keywords, 5,052 SERP results, 286 unknown ASINs in top 10
**Runtime:** ~5 min. Apify cost: ~$3-4.
