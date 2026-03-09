# Brand Analytics Weekly — Lessons Learned

## Run Log

*(New entries go at the TOP)*

### Run: 2026-03-09
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
Both SCP and SQP report data were truncated when returned through MCP tool results. SCP lost ~6 ASINs; SQP lost most non-fuse-bead keywords.
**Workaround:** Save report documents to disk using save_path parameter before attempting to read, or split SQP into multiple smaller ASIN batches.

### 2. Search Terms Report Download Failure
**First seen:** 2026-03-09
Search Terms report returned an error during download. This is the slowest report (~5 min processing) and may be more prone to timeout/failure.
**Impact:** Competitor click share analysis is completely unavailable without this report.

---

## Repeat Errors

*(None yet)*

---

## Resolved Issues

*(None yet)*
