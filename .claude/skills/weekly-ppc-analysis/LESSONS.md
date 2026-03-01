# Lessons Learned — Weekly PPC Analysis

> **Living document.** Claude MUST read this before every run and write to it after every run.

---

## How to Use This File

### Before Every Run
1. Read this entire file
2. Check **Known Issues** for active problems to avoid
3. Check **Repeat Errors** — if you hit the same issue again, flag it to the user immediately
4. Apply all lessons to your execution plan

### After Every Run
1. Add a new entry under **Run Log** using the template below
2. If something went wrong, add it to **Known Issues**
3. If a Known Issue happened again, move it to **Repeat Errors** and increment the count
4. If you solved a Known Issue, move it to **Resolved Issues**

---

## Run Log

### Run: 2026-03-01 (post-restart — COMPLETE DATA)
**Goals:**
- [x] Re-create all PPC reports after server restart
- [x] Download full campaign data (166/166)
- [x] Download full search term data (4,001/4,001)
- [x] Download full targeting data (566/566)
- [x] Fetch portfolio list (70 portfolios)
- [x] Aggregate campaigns by portfolio
- [x] Write comprehensive report with all data
- [ ] Placement report (still fails — different error)

**Result:** SUCCESS (with one remaining issue)

**What worked:**
- **format_json fix is live** — all 166 campaigns, 4,001 search terms, 566 targeting entries fully visible
- **list_portfolios works** — 70 portfolios returned (was 404 before restart)
- **Background agents** for search terms + targeting processed large files efficiently (134s + 112s)
- **Python aggregation script** for portfolio grouping from campaign data
- Total execution: ~8 minutes including 60s report generation wait
- **Critical insight found:** 53.5% of PPC spend ($2,786/week) goes to zero-order search terms

**What didn't work:**
1. **Placement report STILL fails** — New error: `"invalid groupBy values: (placementClassification). Allowed values: (campaign, adGroup, campaignPlacement)"`. The fix used wrong value. Applied correct fix (`campaignPlacement`) but needs yet another server restart.
2. **list_portfolios truncated** — Shows 50 of 70 portfolios (list function truncation not yet fixed)
3. **Python script quote escaping** — Bash heredoc failed with single quotes in campaign names. Fixed by writing to .py file.

**Is this a repeat error?** YES — sp_placements error (×3, different cause), list function truncation (×3)

**Lessons learned:**
1. **Server restart unlocks everything.** Going from 50 to 166 campaigns changed the entire analysis quality.
2. **Placement groupBy value is `campaignPlacement`**, not `placementClassification`. Amazon's error messages helpfully list allowed values.
3. **Background agents for large file processing is the right pattern** — search terms (634K chars) and targeting (85K chars) processed cleanly.
4. **53.5% zero-order spend is the #1 finding** — worth more than any campaign-level optimization.
5. **Write Python scripts to files instead of inline bash** when dealing with complex data with special characters.
6. **8 minutes for complete analysis** is acceptable efficiency — aim for 5 minutes next time by parallelizing more.
7. **Portfolio grouping by campaign name prefix** works reliably since campaign naming is consistent.

**Tokens/cost:** ~80K tokens for this run (much more efficient than the 250K previous runs).

### Run: 2026-03-01 (continuation — report generation)
**Goals:**
- [x] Read existing partial report and overwrite with comprehensive version
- [x] Incorporate DataDive rank data for all 6 products
- [x] Incorporate Seller Board daily data (7 days)
- [x] WoW comparison against Feb 8-14 snapshot
- [x] Save updated snapshot summary.json
- [x] Update LESSONS.md

**Result:** ⚠️ Partial (same data limitations as initial run — server still not restarted)

**What worked:**
- Successfully wrote comprehensive report with all available data sources (Seller Board + DataDive + partial PPC)
- Rank movement analysis across 6 products with actionable insights
- Daily profit trend table from Seller Board adds real business context
- Portfolio mapping via list_sp_campaigns workaround (17 portfolios mapped by portfolioId)
- WoW comparison leveraging Feb 8-14 complete CSV snapshot
- Clean P1/P2/P3 action prioritization with specific bid adjustment recommendations

**What didn't work:**
1. **Same truncation issue** — Still only 50 of 166 campaigns, 50 of 4,033 search terms, 50 of 566 targets visible
2. **Placement report still fails** — Server not restarted
3. **list_portfolios still 404** — Workaround with list_sp_campaigns works but is slower
4. **Search term analysis impossible** — 50 alphabetically-sorted terms (all low-spend A/B terms) gives zero actionable negation data
5. **Context compaction** — Session ran across context limit, required continuation from summary
6. **Write tool requires Read first** — Existing file from previous session couldn't be overwritten without Read

**Is this a repeat error?** YES — sp_placements 400 error (×2), format_json truncation (×2)

**Lessons learned:**
1. **Server restart is the #1 blocker.** Two runs now with partial data. Must be resolved before next analysis.
2. **list_sp_campaigns name_filter is a viable portfolio mapping workaround** — but add `portfolioId` to the sp_campaigns report preset as a permanent fix.
3. **Context management is critical** — This skill uses 150K+ tokens across compaction. Need to be more efficient: process data in agents, summarize before returning to main context.
4. **Always Read a file before Write** — Even if you "know" the content, the tool requires it.
5. **Seller Board daily data is the most reliable source** for account-level health. It gives complete coverage while PPC data is truncated.
6. **DataDive rank data via background agent works well** — Good pattern for parallelizing data collection.
7. **list function truncation is a SEPARATE bug** from download truncation — ALL list_sp_* functions call format_json without max_items. Need to fix these too.

**Tokens/cost:** ~250K+ tokens total across both sessions (initial + continuation). Very high — need to optimize.

### Run: 2026-03-01
**Goals:**
- [x] Pull 4 PPC reports via Amazon Ads API (first API-based run)
- [x] Fetch DataDive Rank Radar data
- [x] Fetch Seller Board data
- [ ] Generate comprehensive weekly analysis
- [ ] Full search term negation/promotion analysis

**Result:** ⚠️ Partial

**What worked:**
- API report creation: 3 of 4 reports created successfully (campaigns, search terms, targeting)
- Report downloads worked — got 166 campaigns, 4,033 search terms, 566 targeting rows
- DataDive rank radar data fetched for 6 products (Cross Stitch + Fuse Beads inline, 4 others to files)
- Seller Board daily dashboard returned 7 days of complete data
- Previous snapshot loaded for WoW comparison
- Rank movement analysis produced valuable insights (perler beads #6→#11, cross-stitch kits #9→#28)

**What didn't work:**
1. **format_json 50-row truncation** — The MCP server's `format_json()` defaults to `max_items=50`, so download_ads_report only shows 50 rows even when the report has 166/4033/566. This meant I could only see ~30% of campaign spend and ~1% of search terms. Fix applied (line 1334: pass `max_items=max_rows`) but server needs restart.
2. **sp_placements report 400 error** — `placementClassification` was in `columns` instead of `groupBy`. Fix applied (line 119) but server needs restart.
3. **Campaign data lacks portfolio field** — The `sp_campaigns` report preset doesn't include portfolio name/ID, making it impossible to group campaigns by portfolio without cross-referencing via `list_sp_campaigns` or `list_portfolios`.
4. **Seller Board date range mismatch** — PPC data covers Feb 20-26, Seller Board covers Feb 22-28. Only 5 days overlap for TACoS calculation.
5. **Large DataDive responses** — Fairy (87 kw), Cat&Hat (81 kw), Latch Hook (50 kw), 4 Flowers (67 kw) were saved to files but couldn't be processed inline.
6. **Seller Board detailed report too large** — Saved to file, couldn't process inline for per-ASIN TACoS.

**Is this a repeat error?** No — first run.

**Lessons learned:**
1. **CRITICAL: Fix format_json before next run.** The 50-row cap makes the analysis nearly useless for campaigns and completely useless for search terms. The fix is already applied — just needs server restart.
2. **Add portfolioId to sp_campaigns preset.** Without portfolio data, campaign grouping is impossible. Need to add to the `groupBy` or `columns` in the report preset, or use `list_portfolios` + `list_sp_campaigns` for mapping.
3. **Consider saving raw JSON to files** instead of just returning formatted tables. A `save_to_file` option on download_ads_report would let us process full data across multiple reads.
4. **Align date ranges** — Calculate Seller Board date range to match PPC date range, or accept the mismatch and document it.
5. **Process large DataDive responses via Agent** — Spawn agents to read and summarize the saved files for rank movement.
6. **Campaign report max_rows should be 500** (not 5000) — 166 campaigns is well under 500. Search terms need 5000.
7. **The Seller Board "Real ACOS" column is TACoS** — it already calculates total ad spend / total revenue. No need to compute manually.

**Tokens/cost:** ~150K+ tokens (session ran across context compaction). High due to large data volumes and debugging.

---

## Known Issues

### 1. format_json 50-row display truncation
**Impact:** HIGH — Makes campaign and search term analysis nearly impossible.
**Fix applied:** `server.py` line 1334 — `max_items=max_rows`. **Needs server restart.**
**Workaround:** None effective. Must restart server.

### 2. sp_placements preset groupBy bug
**Impact:** MEDIUM — Placement report cannot be generated.
**Fix applied:** `server.py` line 119 — moved `placementClassification` from `columns` to `groupBy`. **Needs server restart.**
**Workaround:** Skip placement analysis until restart.

### 3. No portfolio field in sp_campaigns report
**Impact:** MEDIUM — Cannot group campaigns by portfolio without additional API calls.
**Fix needed:** Either add `portfolioId` to the `sp_campaigns` groupBy/columns, or call `list_portfolios` at the start to build a mapping.
**Workaround:** Infer portfolio from campaign name (unreliable for many campaigns).

### 5. list_sp_* function truncation (same as format_json issue)
**Impact:** HIGH — All list functions (list_sp_campaigns, list_sp_ad_groups, list_sp_keywords, etc.) call `format_json()` without `max_items` parameter, defaulting to 50 rows.
**Fix needed:** Add `max_items=max_results` to all format_json calls in list functions. Must also restart server.
**Workaround:** None — can't see more than 50 items from any list function.

### 6. list_portfolios returns 404
**Impact:** MEDIUM — Cannot list portfolios directly.
**Root cause:** Running server uses old code (`GET /v2/portfolios`), fixed code uses `POST /portfolios/list`. Server not restarted.
**Workaround:** Extract portfolioIds from `list_sp_campaigns` with name filters (works but slower).

### 4. Seller Board vs PPC date range mismatch
**Impact:** LOW — TACoS calculation uses slightly different windows.
**Fix needed:** Either pass explicit date params to Seller Board (if supported) or accept ±2 day mismatch.
**Workaround:** Document the mismatch, use overlapping days for comparison.

---

## Repeat Errors

### 1. sp_placements report 400 error (×3)
**Count:** 3 (all 3 runs on 2026-03-01)
- Run 1-2: `placementClassification` in columns → moved to groupBy
- Run 3: `placementClassification` in groupBy → wrong value entirely. **Correct value: `campaignPlacement`**
**Root cause:** Amazon API uses `campaignPlacement` not `placementClassification` as the groupBy value.
**Fix applied:** server.py line 119 now has `campaignPlacement`. **Needs server restart.**

### 2. format_json 50-row truncation (×2 — PARTIALLY RESOLVED)
**Count:** 2 (runs 1-2 on 2026-03-01). **Resolved for download_ads_report after restart.**
**Still affects:** All list_sp_* functions (list_portfolios showed 50 of 70). Needs code fix.
**Root cause:** list functions call format_json without max_items parameter.
**Fix needed:** Add max_items to all list function format_json calls.

---

## Resolved Issues

### 1. format_json truncation on download_ads_report (resolved 2026-03-01)
**Was:** download_ads_report returned max 50 rows regardless of data size.
**Fix:** Added `max_items=max_rows` to format_json call at line 1334. Server restart activated the fix.
**Result:** Full report data visible (166 campaigns, 4,001 search terms, 566 targeting entries).

### 2. list_portfolios 404 error (resolved 2026-03-01)
**Was:** Running server used old `GET /v2/portfolios` endpoint.
**Fix:** Code updated to `POST /portfolios/list`. Server restart activated the fix.
**Result:** 70 portfolios returned successfully.
