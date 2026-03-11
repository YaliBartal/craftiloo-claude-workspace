# Brand Analytics Weekly — Run Log Archive (March 2026)

> Extracted from `.claude/skills/brand-analytics-weekly/LESSONS.md`. Run entries only — Known Issues, Repeat Errors, and Resolved Issues remain in the original file.

---

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
- business.md: removed 3 own-ASINs from competitor list (71->69)

**Tokens/cost:** ~80K tokens (including initial run)

---

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
