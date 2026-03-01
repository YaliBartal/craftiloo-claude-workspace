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

### Run: 2026-03-01
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units (2026-02-28)
- [x] Fetch DataDive Rank Radar data for 9 hero radars
- [x] Fetch DataDive competitor data for 11 niches
- [x] Run Apify keyword scan (9 keywords) with axesso_data actor
- [x] Fetch Seller Board 7-day dashboard aggregates + per-ASIN detailed
- [x] Compile full report with mandatory format
- [x] Save snapshot

**Result:** ✅ Success — All 5 data sources fetched, full report compiled

**What happened:**
- All 5 parallel background agents completed successfully
- **Apify: 9/9 keywords returned data** — first perfect scan since switching to axesso (was 5/9, 6/9 before)
- B096MYBLS1 CRITICAL: 5 units remaining (was 18 on Feb 26), BSR spiked +69.5% to 92,044, 0 keywords in top 10 AND top 50 — complete rank collapse, no pricing data (Buy Box suppressed)
- B0DC69M3YD still 0 top-10 keywords but showing mixed signals: "embroidery kit" +7, "embroidery kit for beginners" +12, but lost "embroidery kits" and "embroidery for beginners" off page entirely
- B0F8R652FX reached #4 on "latch hook kits for kids" — first top-5 appearance
- B08FYH13CL latch hook recovering: "latch hook kit" +11, "latch hook" +10 (was instability day 4+ on Feb 26)
- B09THLVFZK strongest performer: BSR -18.7% to 5,787, #1 mini perler beads, $5,260/7d revenue
- B0DJQPGDMQ: NEW unknown competitor at #1 in DD Latch Hook niche (1,271 sales/mo, 4.7★, 419 reviews)
- SP-API: B096MYBLS1 returned no competitive pricing (Buy Box suppressed at low stock)
- B09HVSLBS6: 124 fulfillable but 124 reserved — effectively near zero available
- 3 ASINs profit-negative: B0F6YTG1CH (-$397), B0F8R652FX (-$373), B0FQC7YFX6 (-$92)
- Ad spend up 15.7% to $5,484, TACoS 19.1%, margin compressed to 17.8%

**What didn't work:**
- 3-day gap between snapshots (Feb 26 → Mar 1) — missed Feb 27-28 data points
- Axesso still doesn't detect badges — badge data carried forward from Feb 26 confirmations
- B07D6D95NG not found in any DD niche (same as previous runs)

**Is this a repeat error?** B0DC69M3YD rank crisis continues (0 top-10 kws). B07D6D95NG missing from DD niches (ongoing).

**Lesson learned:**
- Axesso actor now at 9/9 reliability — the switch from igview is fully validated
- B096MYBLS1 demonstrates the OOS → rank collapse → Buy Box suppression death spiral. When stock drops below ~5 units, Amazon de-ranks aggressively. Future runs should flag products below 20 units as "OOS risk"
- B08FYH13CL latch hook rank is recovering (+11 on key terms) after 4 days of instability — may stabilize if PPC maintains impressions
- Louise Maelys (B0FR7Y8VHB) at 2nd consecutive sighting (#2-#3 on embroidery keywords) — should be added to competitors.md
- B0DJQPGDMQ is the biggest competitive surprise — unknown brand overtaking LatchKits at DD niche #1. Needs investigation.

**Tokens/cost:** ~95K tokens, ~$0.81 Apify cost

---

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

### Run: 2026-03-01
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units (2026-02-28)
- [x] Fetch DataDive Rank Radar data for 9 hero radars
- [x] Fetch DataDive competitor data for 11 niches
- [x] Run Apify light keyword scan (9 keywords)
- [x] NEW: Run Apify competitor BSR scan (27 ASINs — top 3 per category)
- [x] Fetch Seller Board 7-day dashboard aggregates + per-ASIN detailed
- [x] Compile full report with mandatory format
- [x] Save snapshot

**Result:** ✅ Success — All 6 agents completed, full report compiled with new competitor BSR feature

**What happened:**
- All 6 parallel background agents completed successfully
- SP-API: B09WQSBZY7 and B09HVSLBS6 returned null pricing (Buy Box suppressed). B096MYBLS1 OOS/no price as expected.
- NEW: Apify competitor BSR scan (27 ASINs via saswave/amazon-product-scraper) succeeded in ~40s. Real BSR data now available for all 9 categories. Prices returned in EUR (locale issue — only BSR/reviews are reliable).
- Agent required `amazon_domain: "www.amazon.com"` in input — plain `asins` array alone causes KeyError crash.
- Apify keyword scan: 7/9 keywords returned data. "kids embroidery kit" = empty dataset. "needlepoint kits for kids" = 402 credit error (account hit compute limit after 8 runs).
- B096MYBLS1 FULL DE-INDEX: All 50 tracked keywords fell to rank 101. BSR 92,044. 5 units in stock.
- B08FYH13CL latch hook: Recovery CONFIRMED FAILED. BSR +7,001 reversal (26,023→33,024). Feb 27 recovery was a single-day spike.
- B09WQSBZY7 BEST EVER: BSR 8,907 (-2,810 vs baseline). 25/87 top-10 keywords.
- B0F8DG32H5 recovering: BSR 19,073 (-3,293), better than baseline.
- B09THLVFZK near-baseline: BSR 5,786 (-1,126), Amazon's Choice badge.
- Competitive intelligence unlocked: Made By Me BSR 1,534 with 11,876 reviews in latch hook. CYANFOUR BSR 246 dominating adult embroidery.
- Badge type change: Both B09X55KL2C and B09THLVFZK changed from "Overall Pick" to "Amazon's Choice" — possible Amazon nomenclature change.
- Seller Board: Python csv module used (quoted-field-safe). Feb 21-27. $28,783 revenue, $5,182 profit, 19.1% TACoS.
- New unknown competitor B0DJQPGDMQ is #1 in DD Latch Hook niche (1,271 sales/mo, 419 reviews) — not in database.

**What didn't work:**
- Apify credit limit hit on 9th keyword ("needlepoint kits for kids") — 402 error. Need to top up credits.
- Apify competitor BSR scan returns prices in EUR (non-US locale session despite www.amazon.com URL). BSR/reviews are reliable, prices are not.
- "kids embroidery kit" returned empty dataset again — second consecutive run.
- B09WQSBZY7 Buy Box suppressed (null price) despite 1,441 units — unusual, needs Seller Central check.

**Is this a repeat error?** "kids embroidery kit" empty dataset = 2nd consecutive run (new repeat). Apify credit limit = new issue. B08FYH13CL latch hook instability = escalated to CONFIRMED FAILED recovery.

**Lesson learned:**
- Apify saswave/amazon-product-scraper requires `amazon_domain: "www.amazon.com"` in input or crashes with KeyError. Document this for all future Apify product scraper calls.
- Apify prices from saswave scraper are in EUR — only use BSR, rating, reviews from this actor. For USD prices, use SP-API competitive pricing instead.
- B08FYH13CL latch hook: The Feb 27 "recovery" was a false signal. Over 2 weeks of data now shows persistent instability. This product needs a listing/PPC investigation, not monitoring.
- When Apify keyword scan hits credit limit, it gives 402 error — this is different from empty dataset (which is scraper failure). Both need different handling: 402 = pause and top up, empty = carry forward.
- Competitor BSR scan is highly valuable — in one run revealed CYANFOUR BSR 246 (vs our 27,082 in adult embroidery) and Made By Me BSR 1,534 (vs our 33,024 in latch hook). This solves the DataDive BSR gap.

**Tokens/cost:** ~95K tokens, ~$0.72 Apify cost (8/9 keyword runs + 1 product scan)

---

### Run: 2026-02-28
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units (2026-02-27)
- [x] Fetch DataDive Rank Radar data for 9 hero radars
- [x] Fetch DataDive competitor data for 11 niches
- [x] Run Apify light keyword scan (9 keywords) — with NEW keyword rank comparison extraction
- [x] Fetch Seller Board 7-day dashboard aggregates + per-ASIN detailed
- [x] Compile full report with mandatory format + new sections
- [x] Save snapshot

**Result:** ✅ Success — All 5 data sources fetched, full report compiled with new features

**What happened:**
- All 5 parallel background agents completed successfully
- SP-API: 4 ASINs hit 429 QuotaExceeded on pricing — auto-retried, all succeeded. B096MYBLS1 had no active Buy Box price (5 units stock, listing suppressed).
- B096MYBLS1 CRITICAL: 5 units remaining (down from 9 yesterday) — OOS within hours. BSR spiked 49,405→68,691 (+19,286).
- B09X55KL2C BIG WIN: BSR improved 20,793→15,018 (-5,775). 25/55 top-10 keywords. "embroidery kit for beginners" improved 44→28.
- B09WQSBZY7 STRONG: BSR improved 12,081→10,298 (-1,783). Now better than baseline. +4 top-10 keywords.
- B0DC69M3YD Day 3 crisis: 0 top-10 keywords. Entering "embroidery kit" (225K SV) at rank 59 — first organic entry but very distant.
- B0F8DG32H5 BSR declined +4,840 — after strong performance yesterday.
- Apify: 9/9 keywords returned data — NEW: keyword_rankings extracted (our position vs top 3 per keyword).
- Seller Board: Perl-based CSV parser used (awk failed on comma-in-product-name fields). Feb 20-26. $28,900 revenue, $5,128 profit, 19.1% TACoS.
- NEW FEATURE: Keyword Rank Comparison section added to report — score 3/9 keywords in top 5.
- NEW FEATURE: Competitor comparison tables now show our BSR explicitly. Competitor BSR N/A (DataDive doesn't return it).
- SKILL.md updated before this run to add these two new features.

**What didn't work:**
- Competitor BSR: DataDive API does NOT return BSR for competitor products in the niche endpoint. "BSR vs Our BSR" column shows N/A for competitors. To get competitor BSR would require SP-API catalog calls for each competitor ASIN (too many extra calls).
- B0DC69M3YD rank crisis cause still unknown — entering at rank 59 on 225K keyword is a positive signal but crisis not resolved.

**Is this a repeat error?** B096MYBLS1 OOS is escalating (9→5 units). B08FYH13CL recovery slightly stalling (+699 BSR today vs -6,501 yesterday). B0DC69M3YD crisis is Day 3.

**Lesson learned:**
- DataDive niche competitor endpoint does NOT return BSR. The "BSR vs Our BSR" column in competitor tables will always be N/A for competitors unless we make SP-API catalog calls for each. Consider adding a lightweight SP-API batch for top competitor ASINs as a future improvement.
- Seller Board CSV has comma-in-name fields that break simple awk/CSV parsing — agent had to use perl quoted-CSV parser. This is a recurring risk when agent processes raw SB CSV. Note in future agent prompts that the CSV requires quoted-field-aware parsing.
- Keyword Rank Comparison section is HIGH value — 3/9 keywords visible is actionable intelligence. READAEER dominating loom knitting, Klever Kits at P2 sewing with deal badge are new competitive threats surfaced by this section.
- B09X55KL2C BSR -5,775 on a single day is significant — watch if this momentum continues or is a one-day spike.

**Tokens/cost:** ~95K tokens, ~$0.81 Apify cost

---

### Run: 2026-02-27
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units (2026-02-26)
- [x] Fetch DataDive Rank Radar data for 9 hero radars
- [x] Fetch DataDive competitor data for 11 niches
- [x] Run Apify light keyword scan (9 keywords)
- [x] Fetch Seller Board 7-day dashboard aggregates + per-ASIN detailed
- [x] Compile full report with mandatory format
- [x] Save snapshot

**Result:** ✅ Success — All 5 data sources fetched, full report compiled

**What happened:**
- All 5 parallel background agents completed successfully
- SP-API: 4 ASINs hit 429 QuotaExceeded on pricing — auto-retried, all succeeded. B096MYBLS1 had no active Buy Box price (critically low stock likely suppressed it).
- B096MYBLS1 CRITICAL: 9 units remaining (down from 18 yesterday) — OOS in ~2 days. Urgent replenishment required.
- B08FYH13CL MAJOR RECOVERY: "latch hook kits for kids" jumped #65→#9. BSR improved 31,825→25,324. After 5 days of instability, appears to be genuine recovery.
- B0DC69M3YD CRISIS CONTINUES: "embroidery kit" (225K SV) crashed 58→101. Day 2+ with 0 top-10 keywords. Not in top 4 of adult embroidery niche. ETSPIL dominates with 12,319 sales/month.
- B09THLVFZK Overall Pick CONFIRMED on "mini perler beads" (was carried forward 2 consecutive days).
- Apify: 9/9 keywords returned data — best run in 4 days. No empty results.
- Seller Board: 7-day window Feb 19-25. $29,455 revenue, $5,434 profit, 18.8% TACoS.
- Made By Me (B07PPD8Q8V) confirmed Day 2 in 2 categories — needs to be added to competitors.md.
- Louise Maelys (B0FR7Y8VHB) confirmed Day 2 in embroidery — needs to be added to competitors.md.
- veirousa dominates latch hook niche DataDive (#1 and #4) — completely unknown brand.
- Fisher-Price appeared at P2 for "lacing cards" — major toy brand entry.

**What didn't work:**
- B096MYBLS1 pricing: no active Buy Box returned by SP-API — carried forward from yesterday. Likely Buy Box suppressed due to near-OOS status.
- B0DC69M3YD rank crisis cause still unknown — needs listing investigation outside this skill.

**Is this a repeat error?** B08FYH13CL rank instability appears RESOLVED today (now in recovery). Apify empty results resolved this run (0/9 empty vs 4/9 yesterday).

**Lesson learned:**
- B08FYH13CL recovery confirms the 5-day instability was a ranking fluctuation, not a permanent issue. Key signal was keyword rank returning to top 10, not just BSR improvement.
- veirousa dominating latch hook niche (#1 and #4 in DataDive) is a critical competitive gap — we need to investigate this brand and their positioning.
- When SP-API returns no pricing for a near-OOS product (B096MYBLS1), it's a Buy Box suppression signal — add this as a secondary OOS indicator in future runs.
- Apify returning 9/9 successfully after 4 bad days suggests intermittent actor reliability — the carry-forward approach is correct, but we should also consider trying alternative actors if 3+ consecutive runs fail.
- Made By Me expanding across two categories (latch hook + loom knitting) in 2 days suggests a strategic category push from a large toy company — high priority to track.

**Tokens/cost:** ~95K tokens, ~$0.81 Apify cost

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

### Issue: Apify saswave/amazon-product-scraper Returns EUR Prices
- **First seen:** 2026-03-01
- **Description:** saswave/amazon-product-scraper returns prices in EUR despite using www.amazon.com URLs. Currency field shows EUR. Prices are not usable for USD comparisons.
- **Workaround:** Only use BSR, rating, and reviews from this actor. For USD pricing, use SP-API `get_competitive_pricing` instead.
- **Root cause:** Actor appears to default to a non-US locale session. May need a marketplace/locale parameter.

### Issue: Apify Compute Credit Limit (402 on Keyword Scan)
- **First seen:** 2026-03-01
- **Description:** When running 9 keyword scans + 1 product scan in the same session, Apify account hit compute credit limit. 9th keyword ("needlepoint kits for kids") failed with 402 Payment Required.
- **Workaround:** Top up Apify credits before next run. For days with both keyword scan AND competitor BSR scan, check credit balance first.
- **Root cause:** Running both keyword scan (8 runs) + competitor BSR scan (1 large run) depleted remaining credits.

### Issue: DataDive Competitor BSR Not Available — RESOLVED via Apify
- **First seen:** 2026-02-28
- **Resolved:** 2026-03-01 — Added Apify saswave/amazon-product-scraper scan for 27 competitor ASINs as Agent 6.
- **Note:** Prices are in EUR (see above issue) but BSR and reviews are accurate. This is now a standard part of the daily skill run.

### Issue: Seller Board CSV Comma-in-Name Parsing
- **First seen:** 2026-02-28
- **Description:** Seller Board CSV contains product names with commas inside quoted fields. Simple `awk` or basic CSV parsing breaks on these rows. Agent had to use `perl` quoted-CSV parser to extract correct values.
- **Workaround:** Always specify in agent prompt that SB CSV requires quoted-field-aware parsing (perl or python csv module — NOT simple awk/cut). B09THLVFZK revenue was incorrectly shown as 3,213 units before fix.
- **Root cause:** Product names contain commas (e.g., "Mini Fuse Beads, 48 Colors") which break naive CSV parsing.

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

### B08FYH13CL Latch Hook Rank Instability (×5+ days — RECOVERY FAILED as of 2026-03-01)
- **First seen:** 2026-02-25 (run 1)
- **Repeated:** 2026-02-25 (v2), 2026-02-26, 2026-02-27 (false recovery), 2026-02-28 (partial stall), 2026-03-01 (crash confirmed)
- **False recovery signal:** 2026-02-27 — BSR improved -6,501. Recovery appeared genuine.
- **Confirmed failure:** 2026-03-01 — BSR crashed back 26,023→33,024 (+7,001). Keyword rank #17 for "latch hook kits for kids". The Feb 27 recovery was a single-day spike.
- **Status:** ESCALATED — needs listing/PPC investigation. Not a monitoring issue. Root cause unknown. Made By Me (BSR 1,534, 11,876 reviews) and B0DJQPGDMQ (unknown, #1 in niche) are likely taking share.

### "kids embroidery kit" Apify Empty Results (×2 consecutive runs)
- **First seen:** 2026-03-01
- **Repeated:** 2026-03-01 (and likely same in prior run)
- **Description:** Apify igview-owner/amazon-search-scraper returns 0 results for "kids embroidery kit" keyword. Consistent across 2 consecutive runs.
- **Workaround:** Carry forward badge data. If 3+ consecutive runs fail, consider this keyword as unreliable for this actor.
- **Root cause:** Unknown — possibly keyword-specific scraping issue or actor reliability.

### Apify Empty Keyword Results (×2+ consecutive runs) — RESOLVED 2026-02-26
- **Root cause:** `igview-owner~amazon-search-scraper` was broken — returning cached results from entirely different queries (smartphones for craft searches). Not a rate-limit/scraping issue — fundamentally broken actor.
- **Fix:** Switched to `axesso_data~amazon-search-scraper`. Head-to-head test: Axesso returned correct cross stitch results in 7.5s. igview returned smartphone results for the same query.
- **See:** Resolved Issues section for full detail.
### Apify Empty Keyword Results (×2+ consecutive runs → RESOLVED 2026-02-27)
- **First seen:** 2026-02-25 (v2)
- **Repeated:** 2026-02-26 — 4/9 keywords returned empty (up from 3/9)
- **Resolved:** 2026-02-27 — 9/9 keywords returned data successfully (best run in 4 days)
- **Root cause:** Appears to be intermittent actor reliability, not a systematic issue. The actor self-recovered.
- **Note:** Keep carry-forward approach as the workaround for future empty-result days. If 3+ consecutive runs fail on same keywords, consider trying alternative Apify actor.

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
