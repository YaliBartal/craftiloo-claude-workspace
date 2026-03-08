# TACoS & Profit Optimizer — Lessons Learned

## Run Log

### Run: 2026-03-06 (corrected)
**Result:** Partial -> Corrected

**What happened:**
- First run produced WRONG numbers due to SB MCP server truncating data (100/2077 rows = only 2 days)
- User flagged cross-embroidery-kits at 82.6% TACoS as suspicious
- Root cause: csv_to_summary() in sellerboard/server.py has max_rows=100 default
- Re-fetched full 30d data directly via httpx, saved to 30d-full.csv
- Recomputed: account revenue ,531 -> 21,093 (correct)
- Cross-embroidery TACoS corrected from 82.6% to 38.3%
- Updated SB server to accept save_path for full CSV export

**Root cause:** SB server csv_to_summary() caps at 100 rows. 30d report has 2077 rows. Only ~2 days got through.

**Fix:** Added save_path param to csv_to_summary(), get_sales_detailed_report(), get_sales_detailed_7d_report(). Server restart needed.

**Critical lesson:** ALWAYS verify SB data volume. If 30d < 0K rev for a M/yr business, data is truncated.

**Tokens/cost:** ~80K tokens

**What worked (from original run):**
- Portfolio ASIN mapping worked despite mixed formats (string vs dict) in trackers
- PPC Marketing report provided clean account-level trajectory (Feb vs Mar)
- Rank Radar data gave organic momentum signals per product

**What didnt work (from original run):
- 7d SB report too large for inline processing
- CSV parsing required BOM handling
- Some tracker hero_asins stored as dicts {asin, product, role} instead of strings - needed type handling
- CSV parsing required special handling for BOM characters and double-quoted headers

**Lessons learned:**
- Always handle both string and dict formats when reading hero_asins/secondary_asins from portfolio trackers
- SB 30d report returns 2077 rows and exceeds token limit - must save to file and parse from disk
- For 7d comparison, consider using date-filtered 30d data instead of separate 7d API call
- Break-even ACoS = margin %. Several ASINs have ACoS 2-4x their margin, meaning every PPC sale loses money. The business model works because organic (65%) generates the profit.

**Tokens/cost:** ~50K tokens

---

## Known Issues

### Known Issue: Mixed ASIN formats in trackers
Some portfolio trackers store hero_asins as strings, others as dicts with {asin, product, role}. The parse logic must handle both.

### Known Issue: 7d per-portfolio TACoS not computed
Future runs should save 7d data to disk first via save_path parameter.

### Known Issue: SB server needs restart for save_path
The save_path parameter was added to the SB MCP server code but requires a server restart to take effect. Until restarted, fetch data directly via httpx as a workaround.

---

## Repeat Errors

(None yet)

---

## Resolved Issues

### Resolved: SB data truncation (2026-03-06)
csv_to_summary() in sellerboard/server.py capped output at 100 rows. Added save_path parameter to save full CSV to disk. Also added save_path to get_sales_detailed_report() and get_sales_detailed_7d_report(). ALWAYS use save_path for reports with >100 rows.
