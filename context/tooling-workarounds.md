# Tooling Workarounds

> Cross-skill workarounds for recurring technical issues.
> Last updated: 2026-03-11

---

## OneDrive EEXIST Error (x5+ across skills)

**Problem:** Write tool fails with EEXIST error on OneDrive-synced folders. Happens intermittently.
**Workaround chain:**
1. Try Write tool first
2. If EEXIST → try Bash heredoc (`cat << 'EOF' > file`)
3. If heredoc fails (quotes in content) → use Python `open()` to write file

**Affected skills:** listing-optimizer, listing-creator, any skill writing to outputs/

## MCP Tool Output Truncation (~50K chars)

**Problem:** MCP tool results are truncated at ~50K chars. Large reports (SCP with 40+ ASINs, search term data) lose data silently.
**Fix applied:** `save_path` parameter added to SP-API `get_report_document` and SB `get_sales_detailed_report`. Needs MCP server restart.
**Workaround (until restart):** Download large reports directly via Python httpx, bypassing MCP tool output limits.

## Seller Board MCP Server — save_path

**Problem:** `csv_to_summary()` caps at 100 rows. 30d reports have ~2,000 rows.
**Fix applied:** Added `save_path` param to `csv_to_summary()`, `get_sales_detailed_report()`, `get_sales_detailed_7d_report()`.
**Status:** Needs MCP server restart. Until then, fetch directly via httpx using URL from .env.

## Amazon Ads Reports Stuck PENDING

**Problem:** Reports can stay PENDING for 5-30+ min. Worst case: 10 reports, 0 resolved in full session.
**Workarounds (in priority order):**
1. Use cached data from `outputs/research/ppc-weekly/data/` if <3 days old
2. Extract portfolio data from account-wide cached search term reports by filtering on campaign IDs
3. Save report IDs and re-check in follow-up sessions (reports self-resolve in 1-2 days)
4. Don't create duplicate reports — re-check old report IDs first
**Root cause:** Amazon-side queue delay. Not a code/auth issue.

## Context Window Management

**Problem:** Heavy skills (PPC deep dives, weekly analysis) can hit 100-120K tokens.
**Patterns:**
- Use background agents for large file processing (search terms, rank radar, niche keywords)
- Save raw data to disk via `save_path` instead of returning through context
- Process data in agents, summarize before returning to main context
- Cross-session deep dives work: data collection (session 1) + execution (session 2)

## Python Script File Writing

**Problem:** Bash heredoc fails with single quotes, special chars in campaign names, or Unicode.
**Solution:** Write Python scripts to .py files instead of inline bash when dealing with complex data.
**Also:** Always validate JSON after Python script writes (Unicode/encoding issues on Windows cp1252).

## Campaign Data Parsing

**Problem:** `list_sp_campaigns` returns JSON code blocks, not markdown tables.
**Solution:** Use regex `json\n(.*?)\n` to extract campaign data, or save to file and parse with Python.
