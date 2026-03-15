# Brand Analytics Weekly — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`
> Run log archive → `outputs/research/brand-analytics/run-logs/`

## Skill-Specific Lessons

1. MCP tool results truncate at ~50K chars — use `save_path` for large BA reports (especially SCP with 40+ ASINs)
2. SQP should be batched into 2-3 ASIN groups (max 200 chars) to stay under output limits
3. Search Terms report: stream-download as .gz + use ijson streaming parser — filter for our ASINs without loading full dataset (2-3 min)
4. **Search Terms actual field name is `clickedAsin` (single field with `clickShareRank`), NOT `clickedAsin1/2/3`.** Each row = one (searchTerm, ASIN, rank) triplet. Filter script updated — use `filter_search_terms.py`.
5. Brand Analytics returns ALL brand-registered ASINs including older/variant SKUs not in main catalog
6. SP-API MCP server may not be available in some sessions — fall back to direct Python script for report downloads: LWA auth + `requests.get(doc_url)` + `gzip.decompress()` (small reports) or streaming (Search Terms)
7. Previous week raw files may use different format (flat list vs `{'dataByAsin': [...]}`) depending on which session saved them. Always handle both formats when loading prev-week data.
8. The 2026-03-07 folder is current-week data (period Mar 1-7) saved on 2026-03-15. Naming convention: folder = last day of period, not run date.

## Known Issues

### 1. SQP needs multi-batch ASIN queries
52 ASINs need 3 batches. First run only queried 1 batch (18 ASINs = fuse beads only).

### 2. Some BA ASINs not in sku-asin-mapping
~8 low-traffic variants remain unmapped. Minor impact — brief shows ASIN codes.

## Repeat Errors

_None yet._

## Resolved Issues

### 1. Search Terms report download failure (2026-03-09)
Increased timeout 60→120s. For this report, bypass MCP and download via Python script with streaming.

### 2. Unknown ASINs in BA data (2026-03-09)
Added 14 missing ASINs to sku-asin-mapping.json. Removed 3 own-ASINs from competitor list.

## Recent Runs (last 3)

### Run: 2026-03-15 (period: 2026-03-01 to 2026-03-07)
**Result:** Success — all 5 reports pulled. WoW comparison vs Feb 22-28 available.
- Fixed critical bug: Search Terms field name is `clickedAsin`, not `clickedAsin1/2/3` (filter was returning 0 matches — now 86)
- SP-API MCP unavailable → used direct Python script for SQP B3 download
- Key findings: Purchases +17% WoW; Fuse Beads surging (+23pp on "small fuse beads"); Alert: "embroidery kits for kids" -26pp
- Previous run's Market Basket/Repeat Purchase saved as plain lists — handled both formats in analysis

### Run: 2026-03-09 (Issue Resolution)
**Result:** Success — all 3 issues from initial run resolved. 591MB Search Terms processed via streaming.

### Run: 2026-03-09 (Initial)
**Result:** Partial — 4/5 reports pulled, search terms failed. First baseline established for WoW.
