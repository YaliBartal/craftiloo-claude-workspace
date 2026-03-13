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

### Run: 2026-03-12 (Hero Product BSR Scrape)
**Goals:**
- [x] Scrape BSR, price, rating, reviews for 13 hero ASINs via Apify saswave actor

**Result:** Partial success — 12/13 ASINs returned full data. B0DFPQ5LGD returned empty (no title, no BSR, no price).

**What worked:**
- Direct curl to Apify API (no Python available on this machine)
- saswave actor completed in ~30s for 13 ASINs
- Input format: `{"asins": [...], "amazon_domain": "www.amazon.com"}`

**What didn't:**
- B0DFPQ5LGD returned no data — may be suppressed/unlisted or new listing not yet indexed
- Prices returned in EUR currency despite scraping amazon.com — known saswave quirk
- B096MYBLS1 and B09THLVFZK had empty price fields

**Lessons:**
- Python is NOT available on this Windows machine (Store stubs return exit code 49). Use curl for API calls.
- saswave price field is unreliable — sometimes returns EUR, sometimes empty. SP-API `get_competitive_pricing` is more reliable for USD prices.

### Run: 2026-03-10
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units (2026-03-09)
- [x] Fetch DataDive Rank Radar data for 9 hero radars (B08DDJCQKF no radar)
- [ ] Fetch DataDive competitor data for 11 niches — ❌ ALL EMPTY (parsing error)
- [x] Run Apify keyword scan (20 keywords) with axesso_data actor — 20/20
- [x] Run Apify competitor BSR scan (34 ASINs — saswave actor)
- [ ] Fetch Seller Board 7-day dashboard + per-ASIN detailed — ❌ FAILED 401 (×5 consecutive)
- [x] Compile full report with mandatory format
- [x] Save snapshot

**Result:** ⚠️ Partial — SP-API, Apify keyword + BSR scan, and Rank Radar (counts only) succeeded. SB 401 again (fifth consecutive run). DD competitors all empty. Rank Radar movements unavailable.

**What happened:**
- SP-API: 100 orders, 100 units, $2,073.56 shipped revenue for Mar 9 (Monday low-volume). B08DDJCQKF stock ALERT RESOLVED — 925 units (yesterday's 73 reading confirmed API anomaly). B09X55KL2C Buy Box still at $21.58 (3rd party vs our $23.98).
- DataDive Rank Radar: 9/9 radars fetched. Movement data unavailable — script received list response from rank radar endpoint, crashed on `.get()` call. Only top10/top50 summary counts available (from list endpoint). B0FQC7YFX6 jumped +5 top-10 (6→11). B0DC69M3YD achieved 1 top-10 keyword for first time in 28+ days. B09WQSBZY7 declined -10 top10 (37→27).
- DataDive Competitors: ALL 11 niches returned empty. The script received a list-format response from the competitors endpoint. `.get()` on a list throws TypeError. Same root cause as Rank Radar — API may return different JSON structures (list vs dict) in some conditions.
- Apify keyword scan: 20/20 perfect. Fixed key bug from prior run: `(item.get("productDescription") or "")[:50]` — None value from API caused crash when using `.get("productDescription", "")[:50]`. axesso input confirmed: send `json=inp` directly (not wrapped), where `inp = {"input": [...]}`.
- Apify saswave: 34/34 scans. BSR confirmed: `bestsellerRanks[0].rank` comma-formatted string. bsr_category field came back empty in this run — likely actor behavior inconsistency. Prices still EUR — continue ignoring.
- Seller Board: 401 again (fifth consecutive run). Must fix TODAY.
- B08DDJCQKF SERP on "cross stitch kits for kids": #5 in morning scan, #1 in afternoon scan — SERP volatile, not a sustained drop. Always note time of scan in alerts.
- B09WQSBZY7 hit BSR 4,210 — new all-time best (baseline was 11,717 = -64% improvement).
- LatchKits reclaimed SERP #1+#2 on "latch hook kits for kids" (we held #1+#2 yesterday). SERP still volatile.
- Multiple new sewing kit competitors found on "kids sewing kit": GOASION (×2), Fairy Elves, unknown.

**What didn't work:**
- Seller Board 401 — tokens still expired. FIFTH consecutive failure.
- DataDive competitors: all 11 returned empty. Root cause: API returns list, script expects dict. Fix: wrap in `if isinstance(data, list)` check or handle both formats.
- Rank Radar movement data: same issue — list response, `.get()` crashes. Fix same way.
- saswave bsr_category returned empty strings in this run (was working in prior runs). Inconsistent actor behavior.

**Is this a repeat error?** Seller Board 401 = **Repeat Error ×5** (must fix TODAY — escalating). DataDive empty response = repeat error ×2 (occurs when API returns list instead of dict — need defensive parsing). Rank Radar movement failure = repeat error ×2.

**Lesson learned:**
- **DataDive API defensive parsing (CRITICAL)**: Both rank radar and competitors endpoints can return either a `dict` or a `list`. ALWAYS check: `if isinstance(data, list): data = {"items": data}` or similar before calling `.get()`. This has caused failures on multiple runs.
- **axesso None productDescription**: Use `(item.get("productDescription") or "")[:50]` — NOT `item.get("productDescription", "")[:50]`. API can return `None` explicitly.
- **B08DDJCQKF stock API anomaly confirmed**: Three consecutive low readings (82→73→925) prove the 82+73 values were FBA API anomalies. Rule: never alert on stock until 3+ consecutive readings confirm the trend.
- **saswave bsr_category**: Field is unreliable (empty strings in some runs, populated in others). Use only `bsr` field. Category carry-forward from prior snapshots is fine.
- **MUST FIX BEFORE NEXT RUN**: Seller Board tokens (×5 failures), DataDive parsing (dict vs list), Rank Radar movements (same fix), B08DDJCQKF Rank Radar creation.
- **SERP alert timing matters**: B08DDJCQKF showed #5 in morning scan and #1 in afternoon scan on same day. Do NOT alert on a SERP drop without noting scan time. Require 2 consecutive same-time-of-day readings before treating a SERP shift as sustained.
- **Background Agent with MCP tools succeeds where inline scripts fail for DataDive**: Background Agent using DataDive MCP tools directly got 11/11 niches; inline Python script got 0/11. Always use background Agent approach for DD competitors and rank radar. (Late-arriving agent from this run confirmed same: 11/11 via MCP tools.)
- **B0BXKB7QF6 misranking in sewing**: "30K+ bought in past month" — this is an adult travel sewing kit (Coquimbo brand), not a craft competitor. Misranking on "kids sewing kit" keyword. DISMISS if seen again.
- **saswave competitor_bsr with rating/reviews**: When running the full background agent approach (not inline script), the saswave output includes `rating` and `reviews` fields. The inline polling script got nulls. Prefer background agent for richer data.
- **B0F8DG32H5 knitting SERP gap confirmed**: Absent from all 4 knitting keyword SERPs (loom knitting kit, loom knitting, knitting kit for kids, knitting kit for beginners). B0DKD2S3JT (non-hero) does appear at #18 and #13. B0F8DG32H5 needs listing audit or PPC investigation.

**Tokens/cost:** ~110K tokens, ~$0.95 Apify cost (20 keywords + 1 BSR scan)

---

### Run: 2026-03-09
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units (2026-03-08)
- [x] Fetch DataDive Rank Radar data for 9 hero radars (B08DDJCQKF no radar)
- [x] Fetch DataDive competitor data for 11 niches
- [x] Run Apify keyword scan (20 keywords) with axesso_data actor
- [x] Run Apify competitor BSR scan (34 ASINs — saswave actor — BSR FIXED: bestsellerRanks[0].rank)
- [ ] Fetch Seller Board 7-day dashboard + per-ASIN detailed — ❌ FAILED 401 (×4 consecutive)

**Result:** ⚠️ Partial — 5/5 non-SB data sources succeeded. SB 401 again (fourth consecutive run).

**What happened:**
- SP-API: 100 orders, 103 units, $2,028.49 shipped revenue for Mar 8 (Sunday low-volume day — normal). B08DDJCQKF stock at 73 — CRITICAL (only ~2-3 days at current velocity). B09X55KL2C Buy Box at $21.58 (3rd party) vs our $23.98. B09HVSLBS6: 0 fulfillable, 124 inbound.
- DataDive Rank Radar: 9/9 radars. B09WQSBZY7 hit new record 37 top-10 keywords (+3 today). B0F8DG32H5 +3 top-10 (now 19) despite BSR worsening — lag expected. B0DC69M3YD losing on "embroidery kit" (218K SV, 77→92). B08FYH13CL recovering: "latch hook" (10K SV) returned to rank 49 from 101.
- DataDive Competitors: 11/11 niches. B09THLVFZK leads mini perler beads at 2,044 sales/mo (DD), 2x INSCRAFT. B09WQSBZY7 #3 in sewing niche at 1,333 sales/mo. New DD niche leader in lacing cards: B0B58BZ5KV (2,434 sales/mo — not previously tracked).
- Apify keyword scan: 20/20 perfect. BIG WIN: B0F8R652FX #1 + B08FYH13CL #2 on "latch hook kits for kids" (was #5+#17 yesterday). B09THLVFZK reclaimed #1 on "mini perler beads" (was #2 yesterday). kullaloo confirmed #1 on "sewing kit for kids" again.
- Apify saswave: 34/34 BSR FIXED — field is `bestsellerRanks[0].rank` (comma-formatted string e.g. "29,277"). B004JIFCXO BSR still null (product-level anomaly, not field issue). Prices still in EUR — continue to ignore price field from saswave.
- Seller Board: 401 again (fourth consecutive run). Also discovered SELLERBOARD_SALES_DETAILED_7D was never added to .env.

**What didn't work:**
- Seller Board 401 — tokens still expired. Additional issue: SELLERBOARD_SALES_DETAILED_7D env var is missing entirely from .env.
- B08DDJCQKF stock at 73 units is a genuine concern — likely NOT an API anomaly this time (was 82 yesterday which was flagged as anomaly vs 1,386 two days prior; consecutive low readings suggest real stock drop or FBA counting issue).

**Is this a repeat error?** Seller Board 401 = Repeat Error ×4 (escalating — must fix). saswave BSR null = RESOLVED (field confirmed as bestsellerRanks[0].rank). B0DC69M3YD rank crisis ongoing (day 27+). B08FYH13CL instability continuing. B08DDJCQKF no Rank Radar = still not configured.

**Lesson learned:**
- **saswave BSR field CONFIRMED**: `bestsellerRanks` is an array, `bestsellerRanks[0].rank` is a comma-formatted string (e.g., "29,277" = 29277). Update agent prompts to strip commas before parsing. B004JIFCXO consistently has no bestsellerRanks — product-level issue, not field mapping.
- **B08DDJCQKF stock alert**: 73 units at BSR 5,286 with ~30 units/day velocity = ~2-3 days. This is a critical inventory risk. May explain BSR decline (+865 today). If stock runs out, BSR will crash rapidly.
- **B09X55KL2C Buy Box lost to 3rd party at $21.58 vs our $23.98** — first time flagged. Needs investigation. Could be causing hidden revenue loss.
- **B0B58BZ5KV in lacing cards niche** (2,434 sales/mo) — new competitor not previously tracked. Should be investigated and potentially added to competitor tracking.
- **kullaloo and Louise Maelys** have been flagged for 7+ and 10+ days — both should be urgently added to context/competitors.md and competitor BSR scan list.
- **Seller Board fix steps**: (1) SB → Settings → Automation → Reports → regenerate all URLs, (2) update all 5 .env entries, (3) ADD new `SELLERBOARD_SALES_DETAILED_7D` entry that was never configured.

**Tokens/cost:** ~95K tokens, ~$0.95 Apify cost (20 keywords + 1 BSR scan)

---

### Run: 2026-03-08
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units (2026-03-07)
- [x] Fetch DataDive Rank Radar data for 10 hero radars (9 fetched — B08DDJCQKF no radar)
- [x] Fetch DataDive competitor data for 11 niches
- [x] Run Apify keyword scan (20 keywords) with axesso_data actor
- [x] Run Apify competitor BSR scan (34 ASINs — saswave actor — BSR field returned null)
- [ ] Fetch Seller Board 7-day dashboard + per-ASIN detailed — ❌ FAILED 401 (×3 consecutive)
- [x] Compile full report with mandatory format
- [x] Save snapshot

**Result:** ⚠️ Partial — 5/5 non-SB data sources succeeded. SB 401 again (third consecutive run).

**What happened:**
- SP-API: 171 orders, 189 units, $2,389.91 shipped revenue for Mar 7 (down from 214 orders Mar 6 — Sunday effect?). 4 pricing calls hit QuotaExceeded, auto-retried successfully.
- B08DDJCQKF inventory showing 82 (was 1,386 yesterday) — almost certainly API anomaly (BSR/keywords stable). Flagged as verify-in-Seller-Central.
- DataDive Rank Radar: 9/9 radars. B09X55KL2C reclaimed top-50 on "cross stitch for kids" (+71). B09WQSBZY7 massive long-tail gains (+72 on make your own stuffed animal). B08FYH13CL recovering — "latch hook kit" (20.6K SV) returned to rank 42 from off-page. B0F8DG32H5 lost "knitting for beginners kit" (-62) and "knitting kits" (-53) off page — new alert.
- DataDive Competitors: 11/11 niches. veirousa now #1 in latch hook niche (1,271 sales/mo at BSR 4,285). QUEFE brand emerging on perler beads.
- Apify keyword scan: 20/20 perfect. B09X55KL2C RECLAIMED #1 on "kids embroidery kit" (was #5 yesterday). B08DDJCQKF holding #1 on cross stitch keywords + needlepoint. LIHAO now #1 on "mini perler beads" (we dropped to #2).
- Apify saswave: 34/34 ASINs processed but BSR field returned null for all ASINs — actor output field name issue. Previous snapshot BSR used as fallback.
- Seller Board: 401 again (third consecutive run, since 2026-03-02).

**What didn't work:**
- Seller Board 401 — tokens still expired.
- Apify saswave: BSR field returned null across all 34 ASINs. The actor output format uses a different field name than "bsr". Need to inspect raw actor output to find correct field name (e.g., "rankingInCategory", "salesRank", etc.). Will need to fix field extraction in next run.
- B08DDJCQKF inventory showing 82 vs 1,386 — FBA API anomaly (known issue).

**Is this a repeat error?** Seller Board 401 = Repeat Error ×3 (escalating). saswave BSR null = NEW issue (first occurrence of this specific variant — saswave worked fine in 2026-02-28 and 2026-03-02 runs). Investigate field mapping next run.

**Lesson learned:**
- Need to audit saswave actor raw output to find correct BSR field name. The `bsr` field worked in Feb but may have changed in actor version or is named differently. Add field-name fallback list: try `bsr`, `bestSellerRank`, `salesRank`, `rankingInCategory`, `rank`.
- B08DDJCQKF inventory drop from 1,386→82 in one day = FBA API anomaly per LESSONS known issue. Rule reinforced: check BSR + keywords stability before flagging.

**Tokens/cost:** ~95K tokens, ~$0.95 Apify cost (20 keywords + 1 BSR scan)

---

### Run: 2026-03-07
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units (2026-03-06)
- [x] Fetch DataDive Rank Radar data for 10 hero radars
- [x] Fetch DataDive competitor data for 11 niches
- [x] Run Apify keyword scan (20 keywords) with axesso_data actor
- [x] Run Apify competitor BSR scan (34 ASINs — saswave actor)
- [ ] Fetch Seller Board 7-day dashboard + per-ASIN detailed — ❌ FAILED 401 (×2 consecutive)
- [x] Compile full report with mandatory format
- [x] Save snapshot

**Result:** ⚠️ Partial — 5/5 non-SB data sources succeeded. SB 401 again (second consecutive run).

**What happened:**
- SP-API: 214 orders, 227 units, $3,612.67 revenue for Mar 6 (strong day, up from 168/163/$2,527 on Mar 1).
- B09WQSBZY7 ALL-TIME BEST BSR: 4,624 (-4,746 vs Mar 2). Subcat rank #4 in Kids' Sewing Kits. Price dropped from $21.98→$17.98 — likely driving the surge. 34 top-10 keywords (+11 vs Mar 2).
- B0F8R652FX BSR 15,793 (-7,575 vs Mar 2). #1 sponsored "latch hook kits for kids."
- B07D6D95NG BSR 26,438 (-7,004). Strong keyword gains: melting beads +58, fuse beads kit +51, perler bead kit +29.
- B0FQC7YFX6 BSR 36,195 (-10,116) — best since launch.
- B08DDJCQKF: #1 organic "cross stitch for kids", #2 "embroidery kit for kids" (improved from #6 on Mar 2), #2 "needlepoint kits for kids."
- B09X55KL2C ALERT: dropped from #1 to #5 on "kids embroidery kit" — Louise Maelys (B0FR7Y8VHB) now #1. Also "cross stitch for kids" fell 28→101.
- B0DC69M3YD: Day 24+ rank crisis. 0 top-10 keywords. Multiple high-SV terms fell off page today. BSR improved 28,929→23,800 (misleading — keywords still collapsed).
- B096MYBLS1: OOS deepening. BSR 155,054 (+28K vs Mar 2). All 50 keywords at 101.
- B08FYH13CL: Latch hook instability day 7+. latch hook (10K SV) fell to 101. hook rug kits (-87), latchkits (-90) all off page. Only sponsored visibility.
- B08DDJCQKF has NO Rank Radar in DataDive — cannot track keyword performance for our 2nd-highest revenue product.
- 9/10 Rank Radars fetched (no radar for B08DDJCQKF).
- Apify: 20/20 keywords, 34/34 competitor BSR — perfect scan again.
- 5-day gap between snapshots (Mar 2 → Mar 7). Days Mar 3-6 missed.

**What didn't work:**
- Seller Board: 401 again (second consecutive run, fifth+ week without SB data).
- Apify agent full JSON not available in task output (file was 1 line). Only summary was returned in task notification. Competitor BSR table partially reconstructed from previous snapshot.
- B08DDJCQKF: No Rank Radar configured in DataDive. This is our #2 revenue product — needs a radar set up.

**Is this a repeat error?** Seller Board 401 = Repeat Error ×2 (escalating — move to Repeat Errors). B08FYH13CL instability = Repeat Error ×7+. B08DDJCQKF no Rank Radar = was flagged as user requirement on 2026-03-02 but still not configured.

**Lesson learned:**
- Apify agent task output file is unreliable for reading back detailed JSON (arrives empty or 1 line). When agent summary gives key positions, build the battleground table from that summary. Don't block the report waiting for the file.
- B09WQSBZY7 price drop ($21.98→$17.98) is the likely driver of BSR 4,624 (all-time best). Need to monitor margin via SB once tokens fixed. If BSR was won through price reduction, profitability may be impacted.
- B09X55KL2C losing #1 on "kids embroidery kit" to Louise Maelys is a key competitive event. If this holds for 2+ more runs, it should trigger a PPC/listing response.
- Louise Maelys (B0FR7Y8VHB) appearing 10+ days on multiple keywords at high positions — officially a major new competitor in embroidery kids space.
- B08DDJCQKF DataDive Rank Radar needs to be created urgently — it's one of our top 2 products and we have zero keyword rank visibility.
- kullaloo (B0CJZ3JV3K) holding #2 on both sewing keywords 7+ days — needs to be added to context/competitors.md.
- Daily run cadence slipped to 5-day gap (Mar 2→Mar 7). Missing consecutive daily runs reduces trend visibility.

**Tokens/cost:** ~95K tokens, ~$0.08 Apify cost (unusually low — may be estimate error; typical ~$0.95)

---

### Run: 2026-03-02
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units (2026-03-01)
- [x] Fetch DataDive Rank Radar data for 9 hero radars
- [x] Fetch DataDive competitor data for 11 niches
- [x] Run Apify keyword scan (9 keywords) with axesso_data actor
- [x] Run Apify competitor BSR scan (27 ASINs — saswave actor)
- [ ] Fetch Seller Board 7-day dashboard aggregates + per-ASIN detailed — ❌ FAILED (401)
- [x] Compile full report with mandatory format
- [x] Save snapshot

**Result:** ⚠️ Partial — 5/6 data sources fetched. Seller Board unavailable (401).

**What happened:**
- Apify: 9/9 keywords returned data (2nd consecutive perfect scan). No 402 errors. "kids embroidery kit" resolved (was empty ×2 consecutive).
- Competitor BSR scan: 27/27 ASINs returned. B004JIFCXO no BSR (same as last run).
- SP-API: 2 pricing 429s (auto-retried). Inventory showing 0 for B08FYH13CL, B0F8R652FX, B09THLVFZK, B07D6D95NG — inconsistent with BSR data, likely API anomaly.
- B09THLVFZK: BSR 5,012 — NEW ALL-TIME BEST, first time beating baseline (5,856).
- B0F8DG32H5: Rank Radar 10→19 top-10 keywords — biggest single-day jump so far.
- B09WQSBZY7: Rank Radar 17→23 top-10 keywords — strong keyword performance.
- B096MYBLS1: OOS confirmed. BSR 127,041 (+34,997). All 50 keywords collapsed.
- B09HVSLBS6: OOS confirmed. Not in keyword scan top 48.
- B0DC69M3YD: Day 20+ rank crisis. "embroidery kit" (225K SV) back to 101 after briefly returning.
- B08FYH13CL: BSR improved (-2,594) but "latch hook kits" (11.7K SV) fell to rank 101.
- B08DDJCQKF dropped from #2 to #6 on "embroidery kit for kids" — new entrants (Bradove, Pllieay) took positions 2-3.
- Made By Me now #1 latch hook + #2 loom knitting — cross-category expansion confirmed.

**What didn't work:**
- Seller Board: All 5 URLs returned 401 Unauthorized. Tokens expired.
- SP-API FBA inventory: 0 for 4 ASINs that are clearly active (API anomaly).
- B07D6D95NG BSR declined -5,975 — no clear cause.

**Is this a repeat error?** Seller Board 401 is a NEW issue. FBA inventory anomaly (multiple 0s for active products) is NEW variant of the truncation issue. B0DC69M3YD rank crisis ongoing (day 20+). B08FYH13CL instability continuing.

**Lesson learned:**
- Seller Board report tokens can expire without warning — add check to .env update process. The fix is: Seller Board → Settings → Automation → Reports → regenerate all URLs → update .env.
- FBA inventory API showing 0 for clearly active products (B09THLVFZK at BSR 5,012 cannot be OOS) — when BSR is active and improving, treat 0 inventory as API anomaly not real OOS. Real OOS = 0 inventory + BSR crashing + keywords collapsing (all three together).
- "kids embroidery kit" empty ×2 resolved on its own — the carry-forward approach was correct. Axesso actor is reliable overall.
- B0F8DG32H5 +9 top-10 keyword jump suggests the knitting category may be seasonally improving. Watch this product for BSR follow-through in next 2-3 days.
- B08DDJCQKF dropped from #2 to #6 on high-SV keyword — could be a one-day fluctuation or start of displacement. Monitor tomorrow.

**Tokens/cost:** ~95K tokens, ~$0.81 Apify cost

**User instruction (2026-03-02):** Always include B08DDJCQKF (Cross Stitch Backpack Charms) in the Rank Radar fetch and the "Hero Products — Top Keyword Positions" table. SKILL.md updated — now 10 radars.

---

### Run: 2026-03-05
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units (2026-03-04)
- [x] Fetch DataDive Rank Radar data for 9 hero radars
- [x] Fetch DataDive competitor data for 11 niches
- [x] Run Apify keyword scan — 20 keywords with axesso_data actor
- [x] Run Apify competitor BSR scan — 34 ASINs via saswave
- [x] Fetch Seller Board 7-day dashboard aggregates + per-ASIN detailed (7D report)
- [x] Compile full report with mandatory format
- [x] Save snapshot

**Result:** ✅ Success — All 5 agents completed, 20/20 keywords + 34/34 BSR scans succeeded

**What happened:**
- All 5 parallel background agents completed successfully
- **Apify: 20/20 keywords returned data** — second consecutive perfect scan
- **Apify: 34/34 competitor BSR scans succeeded** — saswave reliable again
- **Seller Board 7D report working** — date range Feb 25–Mar 3, NOT stale. Token refresh resolved the previous stale URL issue.
- SP-API: 202 orders, 208 units, $3,110 revenue (Mar 4). B096MYBLS1 null price (OOS, 0 units).
- B09WQSBZY7 **ALL-TIME BEST BSR 4,748** (-47% vs Mar 1, -59% vs baseline). Price cut $21.98→$17.98 driving explosive growth. Units 129→176 (+36%).
- B09THLVFZK **#1 earner** at $5,841/7d. BSR 4,585 (-21% vs Mar 1). "perler beads" (86K SV) slipping #6→#10 — watch closely.
- B09X55KL2C BSR 12,132 (-22% vs Mar 1). 24 top-10 KWs (+1). Revenue $1,916/7d (+$543).
- B096MYBLS1 **FULLY DEAD** — OOS (0 units), BSR 166,727 (+81% vs Mar 1). All 50 keywords at rank 101. No Buy Box.
- B0DC69M3YD **first top-10 keyword** (was 0). Keyword rotation: lost "embroidery kit for beginners" (33K SV, 41→101) but gained "embroidery kits for adults" (15K SV, 101→37).
- B0FQC7YFX6 lost 3 top-10 KWs (9→6). Lost sponsored #1 positions from Mar 1. Only 30 reviews vs competitors' 919+.
- B08FYH13CL BSR improved -9% but lost 3 top-10 KWs (13→10). Mixed signals continue.
- Profit up 36% ($6,992 vs $5,138) on flat ad spend. Margin 23.1% (was 17.8%). TACoS 17.8% (was 18.8%).
- kullaloo confirmed at #2 for "sewing kit for kids" (21K SV) — multi-run threat.
- Made By Me expanding: BSR 1,455, 11,880 reviews, appearing at #1 latch hook + #5 on knitting/sewing keywords.

**What didn't work:**
- **4-day gap** between snapshots (Mar 1 → Mar 5) — missed Mar 2-4 data points. "vs yesterday" comparisons not possible, used "vs Mar 1" instead.
- **axesso actor requires tilde format** — `axesso_data~amazon-search-scraper` (not forward slash). Agent initially tried forward slash which caused 404 errors.
- B07D6D95NG still not found in any DD niche (ongoing).
- Axesso still doesn't detect OP/AC badges — carried forward 3 badges from Mar 1.
- B0F8R652FX not found on "latch hook pillow kit" keyword — not competitive on this term.

**Is this a repeat error?** B07D6D95NG missing from DD niches (ongoing). Axesso badge detection gap (ongoing). B096MYBLS1 OOS/collapse (escalating). B0DC69M3YD rank crisis (continuing but showing first improvement signal).

**Lesson learned:**
- **B09WQSBZY7 price cut validated** — $4 price drop ($21.98→$17.98) resulted in 36% unit increase and 47% BSR improvement in 4 days. Revenue also increased (+28%) despite lower price. Price elasticity is extremely high in sewing kits.
- **Seller Board 7D report is the correct tool** — `get_sales_detailed_7d_report` returned current data (Feb 25–Mar 3, not stale). The stale URL issue from Mar 1 was resolved by token refresh.
- **axesso_data actor requires tilde format on Apify API** — document this: use `axesso_data~amazon-search-scraper`, not `axesso_data/amazon-search-scraper`. Forward slash causes 404 on runs API.
- **Profit surge (+36%) on flat ad spend = efficiency improving** — this is the most important business signal. Revenue up 6% but profit up 36% means margins are expanding significantly.
- **B09THLVFZK "perler beads" keyword (86K SV) slipping** — this is our highest-volume keyword and it's moving from #6 to #10. Needs PPC attention before losing page 1.

**Tokens/cost:** ~95K tokens, ~$1.95 Apify cost

---

### Run: 2026-03-01 (v3) — First run with updated skill
**Goals:**
- [x] Fetch SP-API BSR, pricing, inventory for 13 hero ASINs
- [x] Fetch SP-API Orders for yesterday's revenue/units (2026-02-28)
- [x] Fetch DataDive Rank Radar data for 9 hero radars (FULL keyword sets, no cap)
- [x] Fetch DataDive competitor data for 11 niches
- [x] Run Apify keyword scan — **20 keywords** (expanded from 9) with axesso_data actor
- [x] Run Apify competitor BSR scan — **34 ASINs** via saswave (NEW — merged into Apify agent)
- [x] Fetch Seller Board 7-day dashboard aggregates + per-ASIN detailed
- [x] Compile full report with mandatory format (merged sections)
- [x] Save snapshot
- [x] Snapshot discovery logic (find most recent previous snapshot)

**Result:** ✅ Success — All 5 agents completed, 20/20 keywords + 34/34 competitor BSR scans succeeded

**What happened:**
- All 5 parallel background agents completed successfully
- **Apify: 20/20 keywords returned data** — first perfect expanded scan. All 11 new keywords worked on first attempt.
- **Apify: 34/34 competitor BSR scans succeeded** — saswave actor with `amazon_domain: "www.amazon.com"` worked perfectly. First formalized run of Step 4B.
- SP-API: 160 orders, 172 units, $2,715.65 revenue (Feb 28). B096MYBLS1 null price (5 units, Buy Box suppressed).
- B09WQSBZY7 **BEST BSR EVER** — 8,903 (-24% vs baseline). 23 top-10 keywords.
- B096MYBLS1 **FULL ORGANIC COLLAPSE** — all 50 tracked keywords at rank 101. BSR 92,044. 5 units. No Buy Box.
- B0FQC7YFX6 **fastest improver** — +3 top-10 keywords, #1 on "lacing cards ages 3-5" and "ages 4-8" (sponsored).
- B0F8DG32H5 improving — "finger knitting kit" jumped 13→4. 18 top-10 keywords. BSR -14.7%.
- B08FYH13CL recovery FAILED again — BSR +26.9% vs yesterday. #18 on "latch hook kits for kids". Made By Me dominating.
- Snapshot discovery logic worked — found 2026-02-28.json as previous snapshot (1-day gap).
- Competitor BSR highlights: CYANFOUR BSR 246 (adult embroidery leader), KRAFUN BSR 538 (sewing leader), veirousa BSR 3,726 (latch hook).

**What didn't work:**
- **Seller Board detailed report STALE** — URL returned only Jan 28-29 data (over a month old). Used previous snapshot's per-ASIN data (Feb 20-26) as fallback. URL needs manual refresh in Seller Board Settings → Automation → Reports.
- **DataDive Rank Radar API truncates at 50 keywords** — despite SKILL.md instruction to fetch ALL keywords. The `list_rank_radars` endpoint provides accurate top10/top50 totals (covers all keywords), but `get_rank_radar_data` detail data caps at 50. Radars with >50 keywords (B09WQSBZY7=87, B0F8DG32H5=81, B0DC69M3YD=67) have incomplete movement data.
- **axesso still doesn't detect badges** — 0 badges detected. Carried forward 3 badges from Feb 28 snapshot (B09X55KL2C OP ×2, B09THLVFZK OP ×1).
- B07D6D95NG still not found in any DD niche (ongoing).

**Is this a repeat error?** B08FYH13CL latch hook instability continues (recovery failed again). B096MYBLS1 organic collapse escalating. B0DC69M3YD rank crisis continuing (0 top-10 KWs). B07D6D95NG missing from DD niches (ongoing). Axesso badge detection gap (ongoing).

**Lesson learned:**
- **20-keyword expansion validated** — 20/20 success rate on first run. No empty datasets. axesso handles the expanded set with no issues.
- **Competitor BSR scan validated** — 34/34 ASINs returned data via saswave. Merging into the Apify agent (instead of 6th agent) works perfectly — both jobs run async in parallel.
- **Seller Board detailed report URL can go stale** — the `.env` URL has an embedded date range. When it expires, it returns old data silently (no error). Must check the date range in returned data and flag if stale.
- **Rank Radar 50-keyword API limit is a platform constraint** — cannot fix in SKILL.md instructions. The top10/top50 summary counts from `list_rank_radars` are accurate (cover all keywords), so use those for headline numbers. Movement detail is limited to 50 keywords per radar.
- Total Apify cost ~$1.95 (20 keywords + 1 BSR batch). Within budget.

**Tokens/cost:** ~100K tokens, ~$1.95 Apify cost

---

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

### Run: 2026-03-01 (v1 — igview era + NEW competitor BSR scan)
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

## Known Issues

### Issue: B08DDJCQKF Has No Rank Radar in DataDive
- **First seen:** 2026-03-07
- **Description:** B08DDJCQKF (Cross Stitch Backpack Charms — our #2 revenue product at ~$4,169/7d) has no Rank Radar configured in DataDive. This means we cannot track keyword performance for one of our top 2 revenue products.
- **User requirement:** Per 2026-03-02 instruction, B08DDJCQKF should always be included in Rank Radar fetch. But no radar exists.
- **Fix:** Create a Rank Radar for B08DDJCQKF in DataDive. Go to DataDive → Rank Radars → Create New → seed with B08DDJCQKF ASIN.
- **Workaround:** Use Apify keyword scan positions (which show B08DDJCQKF performing well: #1 "cross stitch for kids", #2 "embroidery kit for kids"). No daily rank tracking available.

### Issue: Apify Agent Task Output File Empty/Unusable
- **First seen:** 2026-03-07
- **Description:** The Apify background agent's detailed JSON output is not accessible via the task output file (file contains only 1 line). Only the summary in the task notification is available. This means the full competitor_bsr table, keyword_battleground details, and badge data cannot be read from the file.
- **Workaround:** Build battleground tables from the task notification summary. For competitor BSR, fall back to previous snapshot data for any ASINs not explicitly mentioned in the summary. This approach works but loses some detail.
- **Root cause:** Background agent output file appears to be a reference to the agent transcript, not the returned text. The actual result is in the task notification.

### Issue: Seller Board Report Tokens Expired (401 Unauthorized)
- **First seen:** 2026-03-02
- **Description:** All 5 Seller Board report URLs returned 401 Unauthorized. Tokens embedded in the URLs have expired. This happened previously in 2026-03-01 v3 (returned stale data) and now returns outright 401.
- **Fix:** Log into Seller Board → Settings → Automation → Reports → regenerate all 5 report URLs → update `.env` with new values.
- **Affected:** SELLERBOARD_DAILY_DASHBOARD, SELLERBOARD_SALES_DETAILED, SELLERBOARD_SALES_SUMMARY, SELLERBOARD_INVENTORY_REPORT, SELLERBOARD_PPC_MARKETING.
- **Workaround:** Carry forward previous SB data — always clearly label as stale. Report works without SB (market data still fully available).
- **Prevention:** If any SB report returns 401 or stale data, check ALL URLs — they share the same token.

### Issue: FBA Inventory API Shows 0 for Active Products
- **First seen:** 2026-03-02
- **Description:** `get_fba_inventory(asin_filter=...)` returned 0 for B08FYH13CL, B0F8R652FX, B09THLVFZK, B07D6D95NG — all clearly active (ranking, getting sales, BSR intact). API data is wrong.
- **OOS detection rule (use ALL THREE signals):** Real OOS = 0 inventory + BSR crashing + keywords collapsing. A product showing 0 inventory alone is NOT a confirmed OOS.
- **Workaround:** When FBA shows 0 but BSR is stable/improving and keywords are ranking, mark as "⚠️ FBA data anomaly — verify in Seller Central" and do NOT alert OOS.

### Issue: DataDive Rank Radar API Truncates at 50 Keywords
- **First seen:** 2026-03-01 (v3)
- **Description:** `get_rank_radar_data` returns at most 50 keyword detail rows per radar, even for radars with 67-87 keywords. The `list_rank_radars` endpoint returns accurate top10/top50 summary counts covering ALL keywords.
- **Workaround:** Use `list_rank_radars` for headline top10/top50 counts (accurate). Accept that movement detail analysis covers only the first 50 keywords per radar. Radars affected: B09WQSBZY7 (87 kws), B0F8DG32H5 (81 kws), B0DC69M3YD (67 kws).
- **Root cause:** DataDive API pagination limit. No known workaround — the API does not expose a pagination parameter for rank radar keyword data.

### Issue: Apify saswave BSR Field — RESOLVED (2026-03-09)
- **First seen:** 2026-03-08 (null for all ASINs)
- **Resolved:** 2026-03-09 — field confirmed as `bestsellerRanks[0].rank` (comma-formatted string e.g. "29,277"). Strip commas before parsing to int. B004JIFCXO has no bestsellerRanks array — product-level anomaly.
- **Note:** bsr_category field (from same actor) returned empty strings on 2026-03-10 run — inconsistent. Use only `bsr` value, carry category forward from snapshots.

### Issue: Apify saswave/amazon-product-scraper Returns EUR Prices
- **First seen:** 2026-03-01
- **Description:** saswave/amazon-product-scraper returns prices in EUR despite using www.amazon.com URLs. Currency field shows EUR. Prices are not usable for USD comparisons.
- **Workaround:** Only use BSR, rating, and reviews from this actor. For USD pricing, use SP-API `get_competitive_pricing` instead.
- **Root cause:** Actor appears to default to a non-US locale session. May need a marketplace/locale parameter.

### Issue: Apify Compute Credit Limit (402 on Keyword Scan)
- **First seen:** 2026-03-01
- **Description:** When running keyword scans + competitor BSR scan, Apify account can hit compute credit limit. Originally failed on 9th of 9 keywords. Now running 20 keywords + 34-ASIN BSR scan (~$1.95/day total).
- **Workaround:** Top up Apify credits before next run. Estimated daily cost is ~$1.95 (20 keywords × $0.09 + 1 BSR scan × $0.15). Ensure sufficient balance.
- **Root cause:** Multiple async actor runs in a single session can deplete credits rapidly.

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
- **Workaround:** Use `asin_filter` parameter to filter to hero ASINs only (resolved the truncation issue — see Resolved Issues).
- **Root cause:** FBA inventory API caps at 50 results per call without filtering

### Issue: DataDive Competitor Research Date Staleness
- **First seen:** 2026-02-24
- **Description:** DataDive niche competitor data has research dates ranging from Dec 2025 to Feb 2026. Sales/revenue estimates may be 2+ months old.
- **Workaround:** Note research dates in report.
- **Root cause:** DataDive niches need manual re-running to refresh competitor data

---

## Repeat Errors

### Seller Board 401 Unauthorized (×5) — CRITICAL / ACTIVE
- **First seen:** 2026-03-02
- **Repeated:** 2026-03-07, 2026-03-08, 2026-03-09, 2026-03-10
- **Status:** CRITICAL ACTIVE — tokens expired for 8+ days. Data stale since Feb 21-27. Fix TODAY.
- **Fix:** Log into Sellerboard → Settings → Automation → Reports → regenerate all 5 URLs → update `.env`. ALSO add missing `SELLERBOARD_SALES_DETAILED_7D` env var (was never configured).
- **Impact:** All SB financials/per-ASIN data stale (carrying forward Feb 21–27). Cannot see profit, margin, TACoS, per-ASIN revenue until fixed.

### DataDive Competitors Inline Script Fails — Use Background Agent Instead (RESOLVED for competitors)
- **First seen:** 2026-03-09 (inline Python script)
- **Resolved for competitors:** 2026-03-10 — A background Agent using DataDive MCP tools directly succeeded (11/11 niches). The inline Python script's dict/list parsing was the issue, not the API itself.
- **Rank Radar movements still affected:** list response format crashes inline script `.get()` calls.
- **Fix for inline script:** Add defensive parsing: `if isinstance(data, list): items = data` before calling `.get()`.
- **Best practice going forward:** Use a background Agent with DataDive MCP for competitors (not inline Python). Rank Radar summary counts (from list endpoint) are still reliable inline.

### Rank Radar Movement Data Unavailable (×2) — ACTIVE
- **First seen:** 2026-03-09
- **Repeated:** 2026-03-10
- **Status:** ACTIVE — rank radar detail endpoint returns list, crashes on `.get()`
- **Fix:** Same as DataDive dict/list fix above. Also check pagination for large radars (87-keyword radars may need multiple pages).
- **Impact:** No keyword movement detail, no significant mover identification. Only headline top10/top50 counts available.

### FBA Inventory API Truncation (×2) — RESOLVED
- **First seen:** 2026-02-24 (run 1)
- **Repeated:** 2026-02-24 (v2)
- **Resolved:** 2026-02-24 — Added `asin_filter` parameter to `get_fba_inventory()`.
- **Root cause:** API was fetching all 294 SKUs correctly, but `format_json()` had `max_items=50` default that truncated the output.
- **Fix:** Pass `asin_filter="B08DDJCQKF,B09X55KL2C,..."` (comma-separated hero ASINs). Server now filters to only those ASINs, aggregates multiple SKUs per ASIN, and reports missing ASINs explicitly. No more truncation.

### B08FYH13CL Latch Hook Rank Instability (×6+ days — RECOVERY FAILED, ESCALATING)
- **First seen:** 2026-02-25 (run 1)
- **Repeated:** 2026-02-25 (v2), 2026-02-26, 2026-02-27 (false recovery), 2026-02-28 (partial stall), 2026-03-01 v1 (crash confirmed), 2026-03-01 v3 (continued decline), 2026-03-02 (BSR improved but key keyword fell off page)
- **Latest:** 2026-03-02 — BSR improved (-2,594) but "latch hook kits" (11.7K SV) fell to rank 101. Made By Me now #1 in latch hook.
- **Status:** ESCALATED — needs listing/PPC investigation. Not a monitoring issue. Made By Me (BSR 1,458, 11,876 reviews) and B0DJQPGDMQ (veirousa, BSR 3,726) are taking share.

### "kids embroidery kit" Apify Empty Results (×2 consecutive runs) — RESOLVED 2026-03-02
- **First seen:** 2026-03-01 v1 (igview era)
- **Resolved:** 2026-03-02 — axesso actor returned data for this keyword on 2nd consecutive perfect scan.
- **See:** Resolved Issues for full detail on igview → axesso switch.

---

## Resolved Issues

### Issue: Seller Board Detailed Report URL Stale (Returns Old Data)
- **First seen:** 2026-03-01 (v3) — URL returned only Jan 28-29 data (over a month old)
- **Resolved:** 2026-03-01 — Token refreshed. Also added new `SELLERBOARD_SALES_DETAILED_7D` report (7-day window, ~460 rows vs 2,335). SKILL.md updated to use `get_sales_detailed_7d_report` instead of `get_sales_detailed_report`.
- **Root cause:** Auth token expired across all 5 Seller Board URLs simultaneously.
- **Note:** Token expiry is recurring — see active Known Issue "Seller Board Report Tokens Expired (401)" for latest occurrence.

### Issue: DataDive Competitor BSR Not Available (Resolved 2026-03-01)
- **First seen:** 2026-02-28 — DataDive niche competitor endpoint does NOT return BSR for competitor products.
- **Resolved:** 2026-03-01 — Added Apify saswave/amazon-product-scraper scan for competitor ASINs. Now formalized as Step 4B in SKILL.md (34 ASINs, merged into Apify agent).
- **Note:** saswave prices return in EUR (not usable), but BSR, rating, and reviews are accurate.

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

---

## Archived Run Logs

<!-- Runs older than 2 weeks. Kept for reference only. -->

### Run: 2026-02-09 (Pre-MCP era)
**Result:** Partial — Required manual data from user. Pre-dates current MCP-based architecture.
**Key lesson:** Always use direct API/MCP connections. Don't assume data availability — ask or fetch programmatically.
