# Lessons Learned — Daily Market Intel

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

<!-- Add new entries at the TOP (newest first). Use this exact format: -->

### Run: 2026-02-24
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch DataDive Rank Radar data for 12 radars (589 keywords)
- [x] Fetch DataDive competitor data for 8 niches
- [x] Fetch Seller Board daily dashboard
- [ ] Run Apify light keyword scan (skipped to save tokens)
- [x] Compile full report with mandatory format
- [x] Save snapshot for tomorrow

**Result:** ✅ Success (Apify skipped)

**What happened:**
- All 4 data sources fetched successfully using parallel background agents
- SP-API returned BSR, pricing, and partial inventory for all 13 hero ASINs
- DataDive returned 12 rank radars with 589 total keywords tracked
- DataDive returned competitor data for all 8 niches
- Seller Board returned 7 days of dashboard data (Feb 16-22)
- Compiled full report with all sections populated
- Apify keyword scan intentionally skipped to stay within token budget

**What didn't work:**
- FBA inventory API capped at 50 results — 5 hero ASINs not in results (B096MYBLS1, B08FYH13CL, B0F8R652FX, B09THLVFZK, B07D6D95NG, B09HVSLBS6)
- B09HVSLBS6 (Needlepoint Wallet) returned no competitive pricing — possible Buy Box suppression
- DataDive competitor research dates vary widely (Dec 2025 - Feb 2026) — sales estimates may be stale

**Is this a repeat error?** No — first run with MCP-based architecture

**Lesson learned:**
- Parallel background agents work well — launched 3 agents + 1 direct call simultaneously
- FBA inventory needs pagination (max_results=50 misses some hero ASINs) — next time request with higher limit or make 2 calls
- Apify scan is the lowest-priority data source — OK to skip when other sources cover the essentials
- DataDive competitor dates should be noted prominently since they can be 2+ months old
- Total execution was efficient — all data fetched in ~3-4 minutes

**Tokens/cost:** ~150K tokens (within target)

---

### Run: 2026-02-09
**Goals:**
- [ ] Fetch competitor data via Apify API
- [ ] Generate daily market intel brief

**Result:** ⚠️ Partial

**What happened:**
- Eventually completed the report after user provided data manually

**What didn't work:**
- Assumed API access to Apify would work — tried multiple endpoints without checking if data already existed
- No upfront question — should have asked "where is the scraper output?" immediately
- Wasted attempts on incorrect API endpoints
- Didn't check for existing JSON files in outputs/ before fetching
- Used 60% of context budget on failed API calls

**Is this a repeat error?** No — first run

**Lesson learned:**
- ASK FIRST: "Do you have fresh scraper data, or should I run a new scrape?"
- CHECK for existing recent files in outputs/ before fetching via API
- Don't retry failed API approaches — ask user for guidance immediately
- Be direct with questions early to save context budget

**Tokens/cost:** ~60% of budget wasted on failed API calls

---

## Known Issues

### Issue: BSR-to-Sales Estimates Are Wildly Inaccurate — NEVER USE
- **First seen:** 2026-02-24
- **Description:** The BSR-to-sales velocity table (e.g., BSR 5,000 = ~680/day in ACS) produces numbers 4-10x too high for our products. Example: B08DDJCQKF at BSR 4,143 was estimated at ~775/day but DataDive shows 5,934/month (~198/day). **User flagged this as a critical inaccuracy.**
- **Fix:** SKILL.md updated to remove BSR-to-sales table entirely. Use DataDive monthly sales as the ONLY sales estimate. Never estimate sales from BSR.
- **Root cause:** Generic BSR-to-sales tables don't account for subcategory dynamics, seasonal variation, or category-specific conversion rates.

### Issue: FBA Inventory API Pagination
- **First seen:** 2026-02-24
- **Description:** `get_fba_inventory(max_results=50)` returns only 50 SKUs. 5-6 hero ASINs consistently fall outside the first 50 results.
- **Workaround:** Make 2 calls or increase max_results. Or use Seller Board inventory report as fallback.
- **Root cause:** FBA inventory API caps at 50 results per call

### Issue: B09HVSLBS6 No Competitive Pricing
- **First seen:** 2026-02-24
- **Description:** Needlepoint Cat Wallet returns no competitive pricing from SP-API. May have suppressed Buy Box.
- **Workaround:** Carry forward previous price or check listing health in Seller Central.
- **Root cause:** Unknown — possible listing suppression or no active Buy Box offer

### Issue: DataDive Competitor Research Date Staleness
- **First seen:** 2026-02-24
- **Description:** DataDive niche competitor data has research dates ranging from Dec 2025 to Feb 2026. Sales/revenue estimates may be 2+ months old.
- **Workaround:** Note research dates in report. Use BSR-to-sales estimates for more current data.
- **Root cause:** DataDive niches need manual re-running to refresh competitor data

---

## Repeat Errors

_None yet._

---

## Resolved Issues

### Issue: Data Source Assumptions (from 2026-02-09)
- **Resolved:** 2026-02-24
- **How:** Rebuilt skill to use direct MCP connections (SP-API, DataDive, Seller Board) instead of relying on pre-existing Apify scraper data. No more guessing about data availability — all sources are API-based now.
