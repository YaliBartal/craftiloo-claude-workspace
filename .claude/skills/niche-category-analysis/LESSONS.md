# Niche Category Analysis — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`
> Run log archive → `outputs/research/competitor-analysis/run-logs/`

## Skill-Specific Lessons

1. For small niches (4 competitors), DataDive provides complete picture — no need for SP-API catalog search
2. Always check `list_niches` first — existing niches are free and often overlap with target
3. Run DataDive competitors + keywords + ranking juice all in parallel at start — saves significant time
4. Seller Board data is valuable for internal baseline even when not technically "in the niche"
5. BSR estimation tables are unreliable for mid-tier products (off by 3-7x) — prefer Jungle Scout actuals from DataDive
6. SP-API pricing essential for real-time data — DataDive prices can be stale (showed $17.98 vs actual $21.98)
7. For doll-themed products: "sizing complaint" (hat too small) becomes a feature for doll accessories
8. Quilt-specific keywords are negligible (~250/mo) — "quilt kit for kids" is NOT a separate niche, it's sub-feature of "sewing kit for kids"

## Known Issues

### 1. DataDive `create_niche_dive` returns HTTP 400
Both seed ASINs tested. Can't create new niches — limited to existing 23.

### 2. DataDive keyword/roots responses exceed context window
138K-234K chars. Use subagents to extract and summarize.

### 3. DataDive prices may be stale
Always cross-reference with SP-API `get_competitive_pricing`.

### 4. Review scraper 8-review cap
See customer-review-analyzer LESSONS.md for full details and workarounds.

## Repeat Errors

_None yet._

## Resolved Issues

_None yet._

## Recent Runs (last 3)

### Run: 2026-02-26
**Result:** Success — CONDITIONAL GO (32/40) for Barbie/fashion-doll loom knitting kit
**Key outcome:** CRAFTILOO holds 41% niche revenue. Hapinest $16.49 vs our $22.98-$26.98. Barbie IP warning critical.

### Run: 2026-02-23
**Result:** Partial — niche dive creation failed, used existing "sewing kit for kids" niche
**Key outcome:** BSR tables underestimated market by 2.7x, Craftiloo by 6.7x.

### Run: 2026-02-22
**Result:** Success — first Apify-only analysis. CONDITIONAL GO (26/35).
