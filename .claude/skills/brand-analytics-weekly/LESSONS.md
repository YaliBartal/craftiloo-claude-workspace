# Brand Analytics Weekly — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`
> Run log archive → `outputs/research/brand-analytics/run-logs/`

## Skill-Specific Lessons

1. MCP tool results truncate at ~50K chars — use `save_path` for large BA reports (especially SCP with 40+ ASINs)
2. SQP should be batched into 2-3 ASIN groups (max 200 chars) to stay under output limits
3. Search Terms report: stream-download as .gz + use ijson streaming parser — filter for our ASINs without loading full dataset (2-3 min)
4. JSON structure for Search Terms: flat `dataByDepartmentAndSearchTerm[]` array (NOT nested)
5. Brand Analytics returns ALL brand-registered ASINs including older/variant SKUs not in main catalog

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

### Run: 2026-03-09 (Issue Resolution)
**Result:** Success — all 3 issues from initial run resolved. 591MB Search Terms processed via streaming.

### Run: 2026-03-09 (Initial)
**Result:** Partial — 4/5 reports pulled, search terms failed. First baseline established for WoW.
