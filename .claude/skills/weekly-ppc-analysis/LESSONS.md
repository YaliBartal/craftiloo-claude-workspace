# Weekly PPC Analysis — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`, `context/ppc-rules.md`, `context/tooling-workarounds.md`
> Run log archive → `outputs/research/ppc-agent/run-logs/`

## Skill-Specific Lessons

1. 5+ min PENDING is normal for 4 simultaneous reports — set expectations, poll every 30-60s
2. `save_to_file` for ALL reports is the right pattern — even campaign report (184 rows) benefits from disk storage
3. Use 3 parallel agents for data processing (campaigns+placements, search terms, targeting) — keeps main context clean
4. Placement report validates TOS strategy — 58% spend goes to TOS at 32.7% ACoS with 12.4% CVR
5. Phrase match is underutilized — 32.7% ACoS / 13.7% CVR vs exact's 41.2% ACoS / 9.4% CVR
6. 3 financial data points is barely enough for trajectories — need 4+ weekly snapshots for "medium" confidence
7. Daily health snapshots have stale financial data (reuse latest weekly numbers) — don't count as independent financial data points
8. Trajectory stored in summary.json enables future WoW trajectory comparison — the real value of 30d trending
9. Portfolio grouping by campaign name prefix works reliably since naming is consistent
10. Write Python scripts to files instead of inline bash for complex data with special characters

## Known Issues

### 1. No portfolio field in sp_campaigns report — CANNOT FIX
Amazon Ads API rejects `portfolioId` as async report column (HTTP 400). Use `list_sp_campaigns` for mapping.

### 2. list_sp_* function truncation
All list functions call `format_json()` without `max_items`, defaulting to 50 rows. Needs code fix + server restart.

### 3. Seller Board vs PPC date range mismatch
PPC and SB may cover slightly different windows (±2 days). Document mismatch, use overlapping days.

## Repeat Errors

### 1. format_json 50-row truncation (x2) — PARTIALLY RESOLVED
Resolved for `download_ads_report` after restart. Still affects all `list_sp_*` functions.

## Resolved Issues

### 1. format_json truncation on download_ads_report (2026-03-01)
Added `max_items=max_rows` at line 1334. Full data visible after restart.

### 2. list_portfolios 404 (2026-03-01)
Updated from `GET /v2/portfolios` to `POST /portfolios/list`. Works after restart.

### 3. sp_placements preset (2026-03-05)
Added `placementClassification` to columns. Returns labeled placements. Confirmed working 2026-03-08.

## Recent Runs (last 3)

### Run: 2026-03-08 (Step 13b — Trajectories)
**Result:** Success — 6 inflection points detected, trajectory data stored in summary.json
**Key outcome:** Listing push + PPC deep dive → rank surge → ACoS improvement 5-10 days later (confirmed pattern)

### Run: 2026-03-08
**Result:** Success — first run with all 4 reports including placement (499 rows)
**Key outcome:** Best week: ACoS 37.5%→34.2%, Net Profit +41.6%, zero-order waste -20.5%

### Run: 2026-03-01 (post-restart)
**Result:** Success — 166 campaigns, 4,001 search terms, 566 targeting fully visible
**Key outcome:** 53.5% of PPC spend ($2,786/week) goes to zero-order search terms
