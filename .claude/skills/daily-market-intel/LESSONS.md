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

### Skill Update: 2026-02-26 — Switched Apify actor to axesso_data
**Changes:**
- Replaced `igview-owner~amazon-search-scraper` with `axesso_data~amazon-search-scraper`
- Updated input format: `{"input": [{"keyword": "...", "country": "US"}]}` (array-wrapped, `keyword` not `query`)
- Updated field mapping in SKILL.md: `searchResultPosition` (0-indexed +1), `productDescription` (title), `price` (float), `productRating` (string to parse), `countReview`, `salesVolume`, `sponsored` (boolean, new)
- Updated timing: Apify step now ~20-30s (was ~122s) since axesso completes in ~7.5s/keyword

**Trigger:** igview returned completely wrong data (smartphones for cross stitch query — cached/wrong search). Head-to-head test: Axesso correct, igview broken.

**Resolved:** "Apify Empty Keyword Results" repeat error (see Resolved Issues below).

**MCP server:** No changes needed — server is actor-agnostic, passes through any JSON.

---

### Run: 2026-02-26
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units (2026-02-25)
- [x] Fetch DataDive Rank Radar data for 9 hero radars
- [x] Fetch DataDive competitor data for 11 niches
- [x] Run Apify light keyword scan (9 keywords)
- [x] Fetch Seller Board 7-day dashboard aggregates + per-ASIN detailed
- [x] Compile full report with mandatory format
- [x] Save snapshot

**Result:** ✅ Success — All 5 data sources fetched, full report compiled

**What happened:**
- All 5 parallel background agents completed successfully
- SP-API: 4 ASINs hit QuotaExceeded on pricing — auto-retried with 2s delay, all succeeded
- B09HVSLBS6 RESTOCKED: 0 → 124 units. BSR spiked to 32,381 as expected post-OOS
- B0DC69M3YD (Embroidery Adults): Severe rank crisis — 0 top-10 keywords, fell off page for "embroidery kit for beginners" (34K SV) and "embroidery kit for adults". Gaining on needlepoint/cross-stitch terms instead — possible listing indexing issue
- B08FYH13CL rank instability continues — 4th consecutive day. "latch hook kits for kids" crashed #8→#65
- B0F8DG32H5 (Knitting): Strong day — +4 top-10 keywords, +24 top-50 keywords
- B09X55KL2C Overall Pick badges now CONFIRMED (were carried forward for 2 days)
- Apify: 4/9 keywords returned empty (same 3 + loom knitting kit now empty)
- Seller Board: 6-day window (Feb 18-23). $25,736 revenue, $5,160 profit, 18.4% TACoS
- 4 ASINs with negative 6-day profit: B0F6YTG1CH (-$397), B0F8R652FX (-$342), B0DC69M3YD (-$56), B0FQC7YFX6 (-$51)
- New competitor Made By Me (B07PPD8Q8V) appeared at #2 for "latch hook kits for kids" — first sighting, high priority
- B096MYBLS1 critically low: 18 units (~5 days stock)

**What didn't work:**
- Apify returned 0 results for 4 keywords (up from 3 yesterday) — pattern is worsening
- B0DC69M3YD rank crisis cause unknown — needs investigation outside this skill

**Is this a repeat error?** B08FYH13CL rank instability (×4 days). Apify empty results (×2 consecutive runs).

**Lesson learned:**
- B09X55KL2C badges confirmed after 2 days of "carried forward" — Apify actor eventually returns results for these keywords. The carry-forward approach is correct.
- B0DC69M3YD gaining on needlepoint terms while losing embroidery terms = possible listing category drift/re-indexing. A listing review (keywords in backend, category) should be triggered.
- Made By Me is a large toy company (Horizon Group) — their entry at #2 in latch hook is a serious threat if they scale.
- SP-API pricing QuotaExceeded self-resolves with 2s retry — normal operating behavior, not a bug.

**Tokens/cost:** ~95K tokens, ~$0.81 Apify cost

---

### Run: 2026-02-25 (v2)
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units
- [x] Fetch DataDive Rank Radar data for 9 hero radars
- [x] Fetch DataDive competitor data for 7 niches
- [x] Run Apify light keyword scan (9 keywords)
- [x] Fetch Seller Board 7-day dashboard aggregates
- [x] Compile full report with mandatory format
- [x] Save snapshot as v2

**Result:** ✅ Success — All 5 data sources fetched, full report compiled

**What happened:**
- All 5 data sources fetched successfully using 5 parallel background agents
- SP-API: All 13 catalog + 13 pricing + 1 inventory + 1 orders = 28 calls successful
- **B09HVSLBS6 pricing RESOLVED** — returned $17.98 (was null for previous 3 runs)
- **B09HVSLBS6 now OOS** — 0 units (was 1 yesterday). BSR spiking +16%.
- B096MYBLS1 critically low at 24 units (~4 days stock)
- DataDive: 9 radars + 7 niches fetched cleanly
- B0DC69M3YD massive gain on "embroidery kit" (225K vol, +40 positions)
- B09X55KL2C reached #1 on "embroidery kit for kids"
- B08FYH13CL latch hook rank instability continues (3rd day) — lost "latch hook kit" off page
- Apify: 6/9 keywords returned data, 3 returned empty datasets
- Seller Board: 7-day aggregates (Feb 18-24) — $29,846 revenue, $5,751 profit, 18.9% margin
- READAEER at #1 and #2 for "loom knitting kit" — 3rd consecutive day
- kullaloo at #3 for "sewing kit for kids" — 3rd consecutive day

**What didn't work:**
- Apify returned 0 results for 3 keywords: "embroidery kit for kids", "kids embroidery kit", "lacing cards" — could not confirm B09X55KL2C badges (carried forward)
- B08FYH13CL latch hook rank instability persists — needs investigation

**Is this a repeat error?** Apify empty results is new. B08FYH13CL rank instability is a repeat pattern (×3 days).

**Lesson learned:**
- B09HVSLBS6 pricing was not a permanent issue — resolved itself after 3 runs. May be intermittent Buy Box suppression.
- Apify actor `igview-owner~amazon-search-scraper` can return empty datasets for valid keywords — need a fallback or retry strategy
- READAEER and kullaloo seen 3 consecutive days → should be added to competitors.md
- 5 parallel background agents architecture works well — Seller Board fastest (~18s), DataDive competitors ~84s, SP-API ~125s, DataDive Rank Radar ~105s, Apify ~122s
- Carrying forward badge data when Apify fails is the right approach — note the caveat in the report

**Tokens/cost:** ~95K tokens, ~$0.81 Apify cost

---

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

### Issue: Apify Empty Results for Valid Keywords — RESOLVED 2026-02-26
- **Root cause:** `igview-owner~amazon-search-scraper` was returning cached data from entirely different searches (smartphones for cross stitch queries). Fundamentally broken actor.
- **Fix:** Switched to `axesso_data~amazon-search-scraper` — 104K runs, professional data company, confirmed correct results in head-to-head test. See Resolved Issues.

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

### B08FYH13CL Latch Hook Rank Instability (×4 days)
- **First seen:** 2026-02-25 (run 1)
- **Repeated:** 2026-02-25 (v2), 2026-02-26 — 4th consecutive day of latch hook keyword drops
- **Description:** Latch Hook Pencil Cases losing key latch hook keywords off page: "latch hook kits for kids" crashed #8→#65 (2026-02-26). "latch hook kit" partially recovering (#101→#33) but core kids term worsening.
- **Impact:** Core category keyword falling off page. BSR worsened to 31,825. New competitor Made By Me appeared at #2 same day.
- **Fix needed:** Investigate listing health, check backend keywords, review PPC. This is now 4 days — escalate to user as action required.

### Apify Empty Keyword Results (×2+ consecutive runs) — RESOLVED 2026-02-26
- **Root cause:** `igview-owner~amazon-search-scraper` was broken — returning cached results from entirely different queries (smartphones for craft searches). Not a rate-limit/scraping issue — fundamentally broken actor.
- **Fix:** Switched to `axesso_data~amazon-search-scraper`. Head-to-head test: Axesso returned correct cross stitch results in 7.5s. igview returned smartphone results for the same query.
- **See:** Resolved Issues section for full detail.

---

## Resolved Issues

### Issue: Apify Empty Keyword Results / Wrong Data (×3 runs → Resolved 2026-02-26)
- **First seen:** 2026-02-25 (v2) — 3/9 keywords empty
- **Repeated:** 2026-02-26 — 4/9 keywords empty, plus discovered returning smartphone results for craft queries
- **Root cause:** `igview-owner~amazon-search-scraper` is fundamentally broken — returning cached data from unrelated previous searches. Not recoverable via retries.
- **Fix:** Switched to `axesso_data~amazon-search-scraper`
  - New input format: `{"input": [{"keyword": "...", "country": "US"}]}`
  - Position field: `searchResultPosition` (0-indexed, add +1)
  - Title field: `productDescription`
  - Price field: `price` (float, not string)
  - Rating field: `productRating` (string "4.4 out of 5 stars", parse to float)
  - Review field: `countReview`
  - New bonus field: `sponsored` (boolean)
  - Missing vs igview: `is_best_seller`, `is_amazon_choice` (not in Axesso output)
- **Timing:** Axesso ~7.5s/keyword, Apify step now ~20-30s total (vs ~122s before)

### Issue: B09HVSLBS6 No Competitive Pricing (×3 → Resolved)
- **First seen:** 2026-02-24 (run 1)
- **Repeated:** 2026-02-24 (v2), 2026-02-25 (run 1)
- **Resolved:** 2026-02-25 (v2) — returned $17.98
- **Root cause:** Likely intermittent Buy Box suppression. Self-resolved after 3 runs.
- **Note:** Product is now OOS (0 units) which may have triggered price return (clearance?). Monitor if pricing disappears again after restock.

### Issue: Data Source Assumptions (from 2026-02-09)
- **Resolved:** 2026-02-24
- **How:** Rebuilt skill to use direct MCP connections (SP-API, DataDive, Seller Board) instead of relying on pre-existing Apify scraper data. No more guessing about data availability — all sources are API-based now.
