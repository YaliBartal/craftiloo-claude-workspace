# Brand Analytics Weekly — Lessons Learned

## Run Log

*(New entries go at the TOP)*

### Run: 2026-03-09 (Issue Resolution Pass)
**Result:** Success (all 3 issues from initial run resolved)

**What was fixed:**

1. **Search Terms report** — Successfully downloaded and processed. The report is 591 MB compressed / 3+ GB decompressed / 8.3M rows covering ALL Amazon search terms. Used streaming download to .gz file + ijson streaming JSON parser to extract the 46 rows where our ASINs appear in top 3. Complete competitor click share data now available.

2. **Unknown ASINs** — 14 ASINs identified via catalog API and added to `context/sku-asin-mapping.json` with product names and portfolio assignments. 3 ASINs (B09X55KL2C, B08FYH13CL, B0DKD2S3JT) were incorrectly in the competitor ASIN list in business.md — removed.

3. **MCP truncation fix** — Added `save_path` parameter to `get_report_document` in SP-API server.py. Also increased timeout from 60s to 120s and improved error handling. **Server restart required** for changes to take effect.

**Files updated:**
- Brief regenerated with correct product names and full Search Terms competitor section
- digest-snapshot.json updated with corrected names, portfolios, and competitor_movements
- sku-asin-mapping.json: +14 ASINs
- business.md: removed 3 own-ASINs from competitor list (71→69)

**Tokens/cost:** ~80K tokens (including initial run)

### Run: 2026-03-09 (Initial)
**Result:** Partial Success

**Period covered:** Feb 22 to Feb 28, 2026
**Reports pulled:** 4 of 5 (search_terms failed to download)
**WoW comparison:** First run — no baseline
**Click share movers:** N/A (first run)
**Funnel alerts:** N/A (first run)
**New keywords:** 27 tracked
**Competitor movements:** N/A (search_terms failed)

**What happened:**
- SCP and SQP reports downloaded and parsed successfully
- Market Basket and Repeat Purchase data processed from inline summaries
- All 7 output files generated (scp-raw.json, sqp-raw.json, market-basket-raw.json, repeat-purchase-raw.json, metadata.json, digest-snapshot.json, brief)
- Python processing script handled truncated MCP tool output gracefully

**What didn't work:**
- Search Terms report failed to download (API error) — competitor click share analysis skipped
- Both SCP and SQP raw data were truncated by MCP tool output limits (~50K chars). SCP got 37 of ~43 ASINs. SQP got only 27 keyword-ASIN rows (mostly fuse bead keywords; sewing/embroidery keywords likely missing from the 18-ASIN SQP query)
- SQP data was limited to one batch of 18 ASINs — remaining ASINs not queried

**Lesson learned:**
- MCP tool results are truncated at ~50K chars. For large BA reports (especially SCP with 40+ ASINs), need to either: (a) save report document to disk via save_path before reading, or (b) process in smaller batches
- SQP should be batched into 2-3 ASIN groups to stay under output limits and ensure all product categories are represented
- First run baseline is now established for WoW comparisons next week

**Tokens/cost:** ~40K tokens

---

## Known Issues

### 1. MCP Tool Output Truncation (~50K chars)
**First seen:** 2026-03-09
**Status:** Fix applied, awaiting MCP server restart
Both SCP and SQP report data were truncated when returned through MCP tool results. SCP lost ~6 ASINs; SQP lost most non-fuse-bead keywords.
**Fix:** Added `save_path` parameter to `get_report_document` in server.py. After restart, use `save_path` to save full report to disk, then read from disk.
**Workaround (until restart):** Download large reports directly via Python httpx, bypassing MCP tool output limits.

### 2. Search Terms Report Is Massive (591 MB compressed)
**First seen:** 2026-03-09
**Status:** Resolved with streaming approach
The Search Terms report covers ALL Amazon search terms (~8.3M rows, 3+ GB decompressed). Cannot load into memory.
**Solution:** Stream-download as .gz file, then use `ijson` streaming JSON parser with `dataByDepartmentAndSearchTerm.item` prefix to filter for our ASINs without loading full dataset. Processing takes ~2-3 minutes.
**Key structural note:** The JSON structure is flat `dataByDepartmentAndSearchTerm[]` array, NOT nested `dataByDepartment[].searchTerms[]`.

### 3. SQP Needs Multi-Batch ASIN Queries
**First seen:** 2026-03-09
**Status:** Known, not yet implemented
With 52 ASINs in sku-asin-mapping, SQP needs 3 batches (max 200 chars per query). First run only queried 1 batch (18 ASINs = fuse beads only). Need to batch all ASINs to get full category keyword coverage.

### 4. Some BA ASINs Not in sku-asin-mapping
**First seen:** 2026-03-09
**Status:** Partially resolved (14 of ~20 mapped)
Brand Analytics SCP/Repeat Purchase reports return ALL brand-registered ASINs, including older/variant SKUs not in the main product catalog. ~8 low-traffic ASINs remain unmapped.
**Impact:** Minor — these are near-zero traffic variants. Brief shows ASIN codes for unmapped products.

---

## Repeat Errors

*(None yet)*

---

## Resolved Issues

### 1. Search Terms Report Download Failure
**First seen:** 2026-03-09 | **Resolved:** 2026-03-09
**Root cause:** The report is 591 MB compressed. The MCP server's httpx timeout was 60s (too short) and the exception handler didn't display the error type.
**Fix:** (a) Increased timeout to 120s in server.py, (b) Added `type(e).__name__` to error messages, (c) For Search Terms specifically, bypass MCP and download directly via Python script with streaming.

### 2. Unknown ASINs in BA Data
**First seen:** 2026-03-09 | **Resolved:** 2026-03-09
**Root cause:** sku-asin-mapping.json only had 38 ASINs. Brand Analytics reports 52+ ASINs (including older products, bundle variants, etc.).
**Fix:** Used catalog API to identify 14 missing ASINs and added them with product names and portfolio assignments. Also removed 3 own-ASINs that were incorrectly in the competitor list.
