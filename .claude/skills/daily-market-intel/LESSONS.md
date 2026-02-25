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

### Run: 2026-02-25
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units
- [x] Fetch DataDive Rank Radar data for 12 radars
- [x] Fetch DataDive competitor data for 8 niches
- [x] Run Apify light keyword scan (9 keywords)
- [x] Fetch Seller Board 7-day dashboard aggregates
- [x] Compile full report with mandatory format
- [x] Save snapshot

**Result:** ✅ Success — All 5 data sources fetched, full report compiled

**What happened:**
- All 5 data sources fetched successfully using 4 parallel background agents
- SP-API inventory pagination fix confirmed working — all 13 hero ASINs retrieved (6 pages, 294 SKUs)
- Critical alerts: B09HVSLBS6 = 1 unit (near OOS), B096MYBLS1 = 27 units (low stock)
- B08FYH13CL rank crash on "latch kits" (#7 → #90) and "latch hook for kids" (#6 → #41)
- Big win: B0DC69M3YD jumped +40 positions on "embroidery kit" (225K vol keyword)
- DataDive agent took ~21 min — longest step as expected (12 radars + 8 niches, 1.1s rate limit)
- 3 new competitors confirmed for 2nd consecutive day: Louise Maelys, kullaloo, READAEER

**What didn't work:**
- B09HVSLBS6 still returns no competitive pricing (repeat issue ×3)
- DataDive Latch Hook niche still stale — hero ASINs B08FYH13CL and B0F8R652FX missing from competitor set
- SP-API catalog/pricing hit 429s on first attempt — retried with 2-3s delay (self-resolved)

**Is this a repeat error?** Yes — B09HVSLBS6 pricing (×3), Latch Hook niche stale (×2)

**Lesson learned:**
- FBA inventory pagination fix works perfectly — do NOT set max_results=50 anymore, let it paginate all pages
- Serializing SP-API pricing calls is correct — parallel calls still hit 429s on catalog
- DataDive is the slowest agent (~21 min) — launch it first or accept it as the bottleneck
- New competitors appearing 2 days in a row should be flagged as confirmed and added to context/competitors.md

**Tokens/cost:** ~120K tokens, ~$0.81 Apify cost

---

### Run: 2026-02-24 (v2)
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units
- [x] Fetch DataDive Rank Radar data for 12 radars (~589 keywords)
- [x] Fetch DataDive competitor data for 8 niches
- [x] Run Apify light keyword scan (9 keywords — badges + new competitors)
- [x] Fetch Seller Board 7-day dashboard aggregates
- [x] Compile full report with mandatory format
- [x] Save snapshot as v2

**Result:** ✅ Success — All 5 data sources fetched, full report compiled

**What happened:**
- All 5 data sources fetched successfully using parallel background agents
- SP-API: 13 catalog + 13 pricing + 1 inventory + 1 orders = 28 calls
- DataDive: 12 rank radars (589 keywords) + 8 niche competitor sets
- Apify: 9 keyword scans completed — 3 Overall Pick badges found on hero products
- Seller Board: 7-day aggregates (Feb 17-23) with Feb 23 anomaly noted
- SP-API Orders: 150 orders, 162 units, $2,287.07 shipped revenue for Feb 23

**What didn't work:**
- FBA inventory still truncated at 50 rows — 6 hero ASINs missing stock data (repeat issue)
- B09HVSLBS6 still returns no competitive pricing (repeat issue)
- DataDive Latch Hook niche data still stale (Dec 2025) — hero ASINs B08FYH13CL and B0F8R652FX missing
- SP-API pricing calls hit 429 rate limits when run in parallel — agent resolved by serializing

**Is this a repeat error?** Yes — FBA inventory truncation (×2) and B09HVSLBS6 pricing (×2)

**Lesson learned:**
- Apify keyword scan works well with async `run_actor` — all 9 completed in ~5 min
- 5 parallel background agents is the right architecture — total wall-clock time ~5 min for data fetch
- SP-API pricing calls should be serialized (not parallel) to avoid 429 rate limits
- Latch Hook niche needs a fresh DataDive niche dive to get current competitor data
- The Feb 23 Seller Board anomaly (-$147 profit) is worth investigating — $2,375 Amazon fees vs ~$1,400 avg

**Tokens/cost:** ~120K tokens, ~$0.81 Apify cost

---

### Skill Update: 2026-02-24 (post-run)
**Changes:**
- Added **Data Freshness Rule** to architecture: if data isn't current to the day, exclude it
- Added **SP-API Orders** as Step 6: `get_orders(date=yesterday)` for real-time revenue + units
- Changed **Seller Board** (Step 5) to 7-day aggregates ONLY — no day-specific data (it's 2 days old)
- Restructured mandatory report format: "Yesterday's Business" (SP-API, real-time) + "7-Day Financial Snapshot" (Seller Board, aggregates)
- Fixed SP-API server: `get_orders` now has `date` param + pagination; `get_fba_inventory` now paginates all SKUs
- Key rule: **SP-API Orders for day-specific revenue/units, Seller Board for 7-day profit/margin/adspend/TACoS**

**Trigger:** User feedback that Seller Board's 2-day lag made day-specific data misleading in a daily report

---

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

### FBA Inventory API Truncation (×2) — RESOLVED
- **First seen:** 2026-02-24 (run 1)
- **Repeated:** 2026-02-24 (v2)
- **Resolved:** 2026-02-24 — Added `asin_filter` parameter to `get_fba_inventory()`.
- **Root cause:** API was fetching all 294 SKUs correctly, but `format_json()` had `max_items=50` default that truncated the output.
- **Fix:** Pass `asin_filter="B08DDJCQKF,B09X55KL2C,..."` (comma-separated hero ASINs). Server now filters to only those ASINs, aggregates multiple SKUs per ASIN, and reports missing ASINs explicitly. No more truncation.

### B09HVSLBS6 No Competitive Pricing (×3)
- **First seen:** 2026-02-24 (run 1)
- **Repeated:** 2026-02-24 (v2)
- **Description:** Needlepoint Cat Wallet returns empty CompetitivePrices array from SP-API. Listing exists (has BSR) but no active Buy Box offer.
- **Impact:** Cannot track pricing for this product.
- **Fix needed:** Check listing health in Seller Central. May need manual price entry.

---

## Resolved Issues

### Issue: Data Source Assumptions (from 2026-02-09)
- **Resolved:** 2026-02-24
- **How:** Rebuilt skill to use direct MCP connections (SP-API, DataDive, Seller Board) instead of relying on pre-existing Apify scraper data. No more guessing about data availability — all sources are API-based now.
