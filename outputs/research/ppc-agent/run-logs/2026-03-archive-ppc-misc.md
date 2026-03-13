# PPC Sub-Skills — Run Log Archive (March 2026)

## Bid Adjustment Recommender

### Run: 2026-03-05
**Result:** Success

**Campaigns analyzed:** 121 (>$5 spend in 30d)
**Changes recommended:** 17 initially → 8 after dedup (8 TOS decreases)
**Changes skipped:** 8 (already changed today or paused)
**Changes applied:** 8 (all successful, 0 errors)
**Net weekly impact estimate:** -$86/week

**Portfolios affected:** Needlepoint (2), Bunny Knitting (1), Fairy Family (3), Cat & Hat Knitting (2)
**Portfolios skipped:** Princess Lacing (changed today), Latch Hook Pillow (changed today), 4 Flowers (emergency intervention in progress)

**What went well:**
- Cross-referenced every recommendation against portfolio trackers — caught 8 items that were already handled today or recently
- Used 30d data (not 7d) for all decisions — proper timeframe per SOP rules
- All 8 API calls succeeded on first try
- Properly deferred 4 Flowers (listing rewrite needs time) and Latch Hook Pillow (15 actions applied today)

**What didn't work:**
- Fresh `sp_campaigns` and `sp_placements` reports got stuck PENDING — had to use existing 30d deep dive data instead
- Placement report (`sp_placements`) downloaded without `placementClassification` field — couldn't do per-placement health classification (core skill capability missing)
- API-pulled TOS modifiers showed STALE values for Princess Lacing (showed 262% when tracker says 148% post-deep-dive). Root cause: modifiers pulled before portfolio action plan changes in separate session
- No tracker exists for Needlepoint — couldn't log changes there. Need to create one.
- Several campaigns not found in modifiers file (dessert sewing, embroidery beginner, some 4 flowers SKs) — likely paused campaigns showing historical spend in 30d report

**Lessons learned:**
- ALWAYS read portfolio trackers BEFORE presenting recommendations — the initial brief had 6 invalid items that were already handled
- The `list_sp_campaigns` API data can be stale if other sessions made changes earlier the same day. Cross-reference with portfolio tracker `change_log` as the source of truth.
- Campaigns not found in the ENABLED modifiers list are likely already PAUSED — check before recommending pauses
- The `sp_placements` report preset may need the `placementClassification` metric explicitly requested. Investigate MCP server report config.

**Tokens/cost:** ~65K tokens

---

## Search Term Harvester

### Run: 2026-03-05 (Full account harvest — first account-wide run)
**Result:** Success

**Terms analyzed:** 10,193 unique (13,503 raw rows, 30-day window)
**P1 negatives identified:** 46 raw → 13 safe after safety checks ($267 spend)
**P2 negatives identified:** 102 raw → 11 safe ($77 spend)
**Protected terms saved:** 22 terms ($662 spend) correctly removed from negate list
**Actual negatives applied:** 19 terms × 72 campaign-level entries, 0 errors
**Promote candidates:** 10 new terms without SK campaigns (top: "cross stitch kits for beginners" 35 orders/24% ACoS)
**Estimated monthly savings:** ~$82/month ($353/30d waste)

**What happened:**
- Requested fresh 14-day report but Amazon Ads API stuck PENDING >3 min (known issue). Fell back to existing 30-day report from Mar 3 — actually better for 30-day negation rule.
- Python classification script processed 13,503 rows, aggregated to 10,193 unique terms, mapped to portfolios via campaign list.
- Safety cross-reference was the hero: 22 protected terms ($662) would have been wrongly negated. Includes "embroidery for beginners" ($154), "lacing cards for kids ages 3-5" ($64), "toddler sewing kit" ($64).
- User approved all 13 P1, top 3 flagged + needlepoint pouch, and top 2 P2 (craft kits + 1 ASIN).
- Single API call applied all 72 campaign-level negatives with 0 errors.

**What didn't work:**
- Amazon Ads API 14-day search term report stuck PENDING for 3+ minutes. 6th occurrence of report generation delay.
- Some campaigns unmapped to portfolios (appear as "Unmapped" — likely PAUSED campaigns not in ENABLED campaign list).

**Lesson learned:**
- **30-day fallback data is actually superior for search term harvesting.** The 30-day rule means we need 30d data anyway — requesting 14d is suboptimal. Next run: request 30-day report directly, or reuse recent 30d data if <3 days old.
- **Python batch processing is essential at scale.** 13,503 rows cannot be analyzed inline. The classify_terms.py + safety_check.py pipeline works well.
- **Protected term safety net is critical.** 22 terms / $662 saved from false negation in a single run. Without it, we'd be negating our own target keywords.
- **Most waste is in Catch All Auto campaigns.** 10 of 13 P1 negates targeted catch-all auto campaigns. Consider a dedicated catch-all cleanup pass.
- **Campaign-level negatives batch well.** 72 entries in a single API call, 0 errors. No need to split into smaller batches under 100.

**Tokens/cost:** ~35K tokens, 0 fresh API reports (used cached 30d data)

**PROMOTE follow-up (same session):**
- Deep audit of all 8 promote candidates against existing campaign keywords (pulled keywords from 20 campaigns)
- **6 of 8 already fully covered** with EXACT match in existing SK/MK campaigns
- **2 gaps found and filled:**
  - "embroidery for kids" → added as EXACT ($0.39) to MK exact campaign 381587421028993
  - "cross stitch for kids 8-12" → new SK campaign created (270472026768698, $0.47, 86% TOS, $10/day)
- **1 reactivation:** SK campaign 309035836424147 renamed + enabled "cross stitch kits for beginners" at $0.36, TOS 13%, $7/day budget. Paused duplicate "cross stitch kits" keyword (covered elsewhere).
- **Lesson:** Always verify existing keyword coverage before creating new campaigns. 75% of promote candidates were already targeted — would have created redundant campaigns without checking.

### Run: 2026-03-02 (Dessert Family — targeted harvest while paused)
**Result:** Success

**Terms analyzed:** 46 (Dessert portfolio only, 30-day window)
**P1 negatives identified:** 3 ($75.82 spend) — BUT 3/3 were protected sewing terms. Removed from negate list.
**Actual negatives applied:** 4 (hygiene terms: "no sew kits for kids", "sewing machine", competitor brand, "felt crafts")
**Promote candidates:** 0
**Bids lowered:** 2 keywords — SK ages 8-12 ($0.74→$0.61, -17.6%), SK beginner ($0.92→$0.73, -20.7%)
**Estimated weekly savings:** Minimal from negatives ($2.80/wk). Real savings from bid reduction (~$3-4/wk at relaunch).

**What happened:**
- Pulled 30-day search term report (13,715 total, filtered to 46 Dessert terms).
- Key finding: 37/46 terms (80%) are protected sewing keywords. Problem was stock collapse, not bad keywords.
- Applied 4 hygiene negatives to MK broad campaign. Lowered bids on 2 keeper campaigns with irregular amounts per rules.
- All 4 campaigns remain PAUSED. Changes prep for restock relaunch in ~2 weeks.

**What didn't work:**
- Initial classification flagged protected terms as P1 negates. Safety cross-reference caught this correctly.

**Lesson learned:**
- When a portfolio's ACoS is terrible but search terms are all legitimate/protected, the root cause is likely external (stock, Buy Box, listing issue) — not keyword selection. Don't negate good keywords just because the product can't convert.
- Always run protected term check BEFORE presenting negate list to user.

**Tokens/cost:** ~40K tokens, 1 Ads API report

---

## Portfolio Performance Summary

### Run: 2026-03-02 (Deep Dive — Fuse Beads)
**Result:** Success

**Portfolio:** Fuse Beads (195178133158684)
**Campaigns analyzed:** 14 ENABLED, 35 PAUSED
**Keywords:** 35 enabled across 10 campaigns
**Search terms:** 278 (7d)
**Rank keywords:** 18 tracked

**What happened:**
- Full deep dive on Fuse Beads per user request. Pulled campaign list, all keywords, all targets, rank radar, seller board, search terms.
- Used background agents to pull keywords (14 campaigns) and targets (3 PT campaigns) in parallel — efficient.
- Identified 3 critical issues: SK fuse beads bleeding (119.5% ACoS), "fuse beads" rank dropped #4→#10, "perler beads bulk" rank collapsed #20→#40.
- Built full action plan with 9 prioritized items.

**What didn't work:**
- 14-day search term report didn't have campaignId field for filtering (different JSON schema than 7d). Used 7d only.
- Campaign list for ALL state returned 200 ARCHIVED first (API paginates by state). Had to make 2 separate calls for ENABLED and PAUSED.

**Lesson learned:**
- For portfolio deep dives, always call ENABLED and PAUSED separately — never ALL (200 ARCHIVED campaigns clog the response).
- Background agents for keyword/target pulls work well — saves time vs sequential calls.
- 7-day search term data is sufficient for pattern identification; 30-day needed only for negation decisions.
- Portfolio with strong organic (78% organic ratio) needs PPC focused on rank defense, not volume generation.

**Tokens/cost:** ~65K tokens (deep dive justified for top-spend portfolio)

### Run: 2026-03-02
**Result:** Success

**Portfolios analyzed:** 18
**Red flags:** 6 (Princess Lacing, 4 Flowers, Embroidery for Kids, Needlepoint, Bunny Knitting, Dessert Family)
**Structural gaps:** 11 portfolios missing required types (9 missing Broad — systemic gap)
**Dormant campaigns:** ~31 LOW BID across 5 portfolios
**New campaigns this week:** 0 (SOP violation flagged)

**What happened:**
- First run of this skill. Campaign report stuck in PENDING >2min — used 1-day-old weekly snapshot for metrics (per error handling protocol).
- Live campaign list (152 ENABLED) pulled successfully for structure audit.
- Classified all 152 campaigns by type using name pattern matching.
- Identified systemic Broad campaign gap across account.

**What didn't work:**
- `create_ads_report(sp_campaigns, LAST_7_DAYS)` stuck in PENDING indefinitely. Amazon API issue — not server-side.
- Some portfolio name mismatches between weekly snapshot display names and API portfolio names (e.g., "Cross Stitch Hero" vs "Cross stitch backpack charms").
- Bunny Knitting shows 0 ENABLED campaigns in portfolio but weekly snapshot shows $56 spend — campaigns may be assigned to wrong portfolio ID or unassigned.

**Lesson learned:**
- Always have fallback to weekly snapshot data when campaign reports are slow.
- Build a persistent portfolio name mapping (API name -> display name) to avoid mismatches.
- Campaign type classification by name works ~90% but "TOS" campaigns without SK/MK prefix are ambiguous — defaulted to SK.
- The Broad campaign gap is the #1 structural finding — worth making this a standard check.

**Tokens/cost:** ~35K tokens

---

## Campaign Creator

### Run: 2026-03-05 (Biggie Beads — 2 MK campaigns from PROMOTE candidates)
**Result:** Success

**Campaigns created:** 2
**Keywords added:** 4
**Product ads:** 2 (B07D6D95NG / O9-70DP-C5J6)

**What happened:**
- Created 2 MK EXACT campaigns from search term harvest PROMOTE candidates
- Campaign 1: "biggie beads - SPM MK large perler TOS" — "large perler beads" $0.78 + "big perler beads" $0.83, TOS 143%, PP 31%, ROS 14%, $12/d
- Campaign 2: "biggie beads - SPM MK large fuse TOS" — "large fuse beads" $0.72 + "jumbo perler beads" $0.68, TOS 137%, PP 27%, ROS 12%, $10/d
- User chose NOT to negate these terms from broad/auto campaigns — wants both running simultaneously

**What didn't work:**
- First campaign create attempt failed with HTTP 400 — `startDate` format must be `YYYY-MM-DD` (ISO), NOT `YYYYMMDD`. Fixed on retry.
- Product ad creation failed initially — Amazon Ads API v3 requires `sku` field alongside `asin`. Had to look up SKU from Seller Board 7d report.

**Lesson learned:**
- **startDate format is `YYYY-MM-DD`** — not `YYYYMMDD`. Amazon Ads API rejects the compact format.
- **Product ads need SKU field** — `manage_sp_product_ads` requires `{"asin": "...", "sku": "..."}`, not just ASIN. Get SKU from Seller Board 7d report or FBA inventory.
- **PP/ROS at creation is fine when user specifies it.** Known Issue #3 (TOS-only at creation) is a default rule, but user explicitly requested PP/ROS modifiers — follow user intent.
- **User may choose not to isolate traffic.** Don't assume negatives should be applied — always ask.

**Tokens/cost:** ~15K tokens (continuation from deep dive session)

---

## TACoS & Profit Optimizer

### Run: 2026-03-06 (corrected)
**Result:** Partial -> Corrected

**What happened:**
- First run produced WRONG numbers due to SB MCP server truncating data (100/2077 rows = only 2 days)
- User flagged cross-embroidery-kits at 82.6% TACoS as suspicious
- Root cause: csv_to_summary() in sellerboard/server.py has max_rows=100 default
- Re-fetched full 30d data directly via httpx, saved to 30d-full.csv
- Recomputed: account revenue $1,531 -> $21,093 (correct)
- Cross-embroidery TACoS corrected from 82.6% to 38.3%
- Updated SB server to accept save_path for full CSV export

**Root cause:** SB server csv_to_summary() caps at 100 rows. 30d report has 2077 rows. Only ~2 days got through.

**Fix:** Added save_path param to csv_to_summary(), get_sales_detailed_report(), get_sales_detailed_7d_report(). Server restart needed.

**Critical lesson:** ALWAYS verify SB data volume. If 30d < $10K rev for a $2M/yr business, data is truncated.

**Tokens/cost:** ~80K tokens

**What worked (from original run):**
- Portfolio ASIN mapping worked despite mixed formats (string vs dict) in trackers
- PPC Marketing report provided clean account-level trajectory (Feb vs Mar)
- Rank Radar data gave organic momentum signals per product

**What didn't work (from original run):**
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
