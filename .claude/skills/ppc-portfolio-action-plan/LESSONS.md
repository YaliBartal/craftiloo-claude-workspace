# Lessons Learned -- PPC Portfolio Action Plan

> **Living document.** Claude MUST read this before every run and write to it after every run.

---

## How to Use This File

### Before Every Run
1. Read this entire file
2. Check **Known Issues** for active problems to avoid
3. Check **Repeat Errors** -- if you hit the same issue again, flag it to the user immediately
4. Apply all lessons to your execution plan

### After Every Run
1. Add a new entry under **Run Log** using the template below
2. If something went wrong, add it to **Known Issues**
3. If a Known Issue happened again, move it to **Repeat Errors** and increment the count
4. If you solved a Known Issue, move it to **Resolved Issues**

---

## Run Log

### Run: 2026-03-09 — Needlepoint Portfolio (Deep Dive #2)
**Target:** Needlepoint (45080904945580) — 7 ENABLED campaigns, Scaling stage
**Result:** Success (7/7 actions executed, 0 errors)

**What happened:**
- Second deep dive. Health still 3/10, 30d ACoS 57.4% (target 30%), CVR 5.0% (target 10%).
- Full data collection: 30d campaigns (cached Mar 8), 30d search terms (364 rows), 30d placements (24 rows, fresh pull), rank radar (50 KW), niche keywords (130 KW). Seller Board skipped (MCP server error — known issue).
- **Critical data quality issue discovered:** Weekly summary showed 92% ACoS for Needlepoint, but raw campaign report data showed 68.7% for the same period. Bad aggregation in weekly summary processing step — miscounted sales from SK beginners campaign. User caught this by checking Seller Central directly. Corrected in weekly summary, needlepoint tracker, and brief.
- **User modified Item 3:** Instead of cross-negating "needlepoint pouch kit" from MK broad + Auto, user chose to boost SK pouch kit (TOS 157%→213%, bid $0.47→$0.57). Rationale: "I don't wanna negate the search term, even if it's cannibalising its own, if it's converting well." (29.3% ACoS in MK broad).
- All 7 actions batched into 4 parallel API calls: campaign TOS updates (4), ad group bid (1), keyword bids (2), negative creation (1). Zero errors.
- Root issue identified: **CVR 5% is a listing/product problem.** No PPC fix can make this portfolio profitable. Listing audit is the #1 pending action.

**What didn't work:**
- Seller Board MCP server error (`csv_to_summary() got unexpected keyword argument 'save_path'`). Known issue — server needs restart after code update. Used cached SB data from tracker instead.
- Rank radar (165K chars) and niche keywords (59K chars) exceeded token limits. Required separate agent processing.
- **92% ACoS figure was wrong** — propagated from bad weekly summary aggregation into the timeseries-backfill and then into the brief's executive summary. The user caught it by cross-checking in Seller Central. Root cause: weekly analysis aggregated portfolio data incorrectly (miscounted sales).

**New issues identified:**
- **Weekly summary portfolio aggregation can produce wrong ACoS.** The weekly-ppc-analysis skill needs a validation step: compare raw campaign report per-portfolio totals against the summary.json output. Discrepancy of 23pp (92% vs 68.7%) is unacceptable.
- **Calendar-aligned weeks vs rolling windows.** User requires calendar-aligned weeks (Mar 1-7) for comparisons, not rolling 7d (Feb 27-Mar 5). Amazon Ads API LAST_7_DAYS returns rolling windows. Must label exact date ranges and prefer calendar alignment. Saved to MEMORY.md.

**Is this a repeat error?** Yes — Seller Board MCP server error (known issue, needs restart). No — 92% aggregation error is new.

**Lesson learned:**
- **Always cross-validate aggregated portfolio totals against raw data.** Sum campaign-level spend/sales from the report file and compare to summary.json. Flag any discrepancy >2%.
- **User preference: don't negate converting terms even if cannibalizing.** When a search term converts profitably in MK broad AND has a dedicated SK campaign, user prefers boosting the SK campaign rather than negating in MK broad. This preserves the converting traffic as a safety net while the SK campaign ramps.
- **Label exact date ranges on every weekly metric.** Never say "this week's ACoS" — say "Feb 27-Mar 5 ACoS" or "Mar 1-7 ACoS."
- **Seller Board data can be sourced from tracker** when MCP server is down. The tracker's latest_metrics and tacos_optimizer entries contain margin, organic ratio, TACoS.

**Tokens/cost:** ~100K tokens across 2 sessions (context restart due to data quality investigation)

### Run: 2026-03-05 — Needlepoint Portfolio
**Target:** Needlepoint (45080904945580) — 5 ENABLED + 6 PAUSED campaigns, Scaling stage, 3 hero ASINs + 1 dead ASIN
**Result:** Success

**What happened:**
- First-ever deep dive. Health score 3/10, ACoS 56.7% (target 30%). 50 orders/30d.
- Full data collection: 30d campaigns (all 4 reports COMPLETED successfully), 14d search terms (191 terms for portfolio), 30d placements, 30d keywords (11 active), rank radar (50 KW), niche keywords (130 KW), Seller Board, budget utilization.
- **Root cause: MK broad cannibalization at 54% of spend.** Zero negative keywords for SK campaign terms in MK broad, so broad was winning auctions against its own SK campaigns. SK campaigns starved (0-4.6% budget utilization) while MK broad + Auto were 100-102% capped.
- **Dead ASIN B09HVDYMDK (Mermaid)** — returns 404 from catalog API but was still advertised in all 5 campaigns.
- 14-item action plan generated. User approved 10 items (all P1 + select P2/P3) with modifications.
- User requested full campaign proposal cards for SK "needlepoint pouch kit" and PT competitor targeting. Modified both from PAUSED→ENABLED. Modified SK TOS from 47%→157%.
- 2 new campaigns created: SK (73257765455257) and PT (42122197345124).
- 9/10 actions executed successfully. 1 failed (archive — API limitation).

**What didn't work:**
- Campaign archive API call failed — `ARCHIVED` state not supported via `update_sp_campaigns`. Only ENABLED/PAUSED/PROPOSED allowed. Must archive via Seller Central UI.
- Keyword pause failed on first attempt — used stale/fabricated keyword IDs from compacted context. Fixed by calling `list_sp_keywords` for correct IDs.
- PT target creation failed twice: first with `asinSameAs` (needs `ASIN_SAME_AS`), then with `manual` (needs `MANUAL`). SP v3 API uses SCREAMING_SNAKE_CASE.
- Campaign creation date format: `YYYYMMDD` rejected, needs `YYYY-MM-DD`.
- Bid recommendation API returned HTTP 429. Used search term CPC data as fallback.

**Is this a repeat error?** Yes — `ASIN_SAME_AS` casing (2nd occurrence, also hit in Latch Hook Pillow run).

**Lesson learned:**
- **Campaign `startDate` format is `YYYY-MM-DD`, not `YYYYMMDD`.** Amazon Ads API returns HTTP 400 for compact format.
- **PT target `expressionType` must be `MANUAL` (uppercase).** Same SCREAMING_SNAKE_CASE pattern as `ASIN_SAME_AS`.
- **Never trust keyword IDs from compacted/summarized context.** Always re-fetch via `list_sp_keywords` before modifying keywords. Context compression can fabricate or corrupt IDs.
- **Campaign archiving must be done in Seller Central.** Flag as UI-only action in future action plans — don't waste an API call.
- **MK broad cannibalization detection is now confirmed on 5+ portfolios.** Fairy Family, Needlepoint, Princess Lacing, Cross Stitch Backpack Charms, Embroidery for Kids — all had MK broad consuming >30% of spend. This is the most common structural issue. Auto-check in every deep dive.

**Tokens/cost:** ~120K tokens across 2 sessions (context restart)

### Run: 2026-03-05 — Latch Hook Kits Portfolio
**Target:** Latch Hook Kits (189174727582199) — 12 ENABLED + 2 PAUSED campaigns, Scaling stage
**Result:** Success

**What happened:**
- First deep dive. All 5 Amazon Ads reports (campaigns, search terms, placements, keywords, targets) completed successfully.
- Portfolio ACoS 36.5% vs 30% target (YELLOW). Strong CVR 12.1%. Hero keyword "latch hook kit for kids" drives 48% of spend.
- Major finding: rank collapse on "latch hook kit" (20.6K SV, #45 -> >100) and "latch hook" (10.2K SV, #28 -> >100) — likely from paused campaign.
- Detail Page placement delivers 19.6% ACoS but gets only 6% of spend due to zero PP modifiers.
- Executed 8 actions: PP modifiers on 4 campaigns, bid boosts on 4 keywords + re-enabled "latch hook kit", paused 1 bleeding campaign, lowered 2 bids, created 2 new campaigns (pencil case SK + auto winners MK).
- SKU lookup required for product ad creation — found via SP-API GET_MERCHANT_LISTINGS_ALL_DATA report.

**What didn't work:**
- MCP server code changes for inventory SKU display didn't take effect without server restart. Had to use listings report instead.

**Lesson learned:**
- For product ad creation, always get SKU from SP-API listings report (GET_MERCHANT_LISTINGS_ALL_DATA). The inventory endpoint aggregates SKUs by ASIN.
- When search terms report shows `sales7d` field (not `sales14d`), use that for metrics. Field names vary by report configuration.

**Tokens/cost:** ~80K tokens

### Run: 2026-03-05 — Shield All Portfolio
**Target:** Shield All (226460450341570) — 4 ENABLED + 7 PAUSED campaigns, defensive/shield portfolio
**Result:** Success

**What happened:**
- First-ever deep dive. General stage defensive portfolio — PT campaigns targeting own ASINs + brand keyword defense.
- 30d baseline: $899 spend, $3,245 sales, 27.7% ACoS, 141 orders, 13.0% CVR (only 4 ENABLED campaigns).
- Key finding: cross stitch kits TOS-IS only 7.5% — competitors own 92.5% of our product page.
- 7 campaigns were paused (previously poor performance). User approved conservative re-enable: $2/day budgets, 50%+ TOS cuts, high bids capped.
- 14 API calls, 0 errors. 3 execution batches: ENABLED adjustments, 7 campaign re-enables, 3 high bid reductions.
- Context restart mid-session (token limit). All data recovered from summary — clean continuation.

**What didn't work:**
- Reports stuck PENDING initially (repeat error x8+). Eventually resolved.
- Wrong report field names on first extraction attempt (`spend`/`sales` vs `cost`/`sales7d`). Fixed.

**Lesson learned:**
- When user says campaigns were paused "for a reason" — do NOT use original budgets/TOS. Cut everything 50%+ and use $2/d caps.
- Shield campaigns are PT (ASIN_SAME_AS), not keyword campaigns. Search term data appears as ASIN references.
- Budget utilization check is essential for shield campaigns — most were at 0-5% utilization.

**Tokens/cost:** ~80K tokens (including context restart)

### Run: 2026-03-05 — Cat and Hat Knitting Portfolio
**Target:** Cat and Hat Knitting (280615211735082) — 12 ENABLED, 1 PAUSED campaigns, 2 ASINs (B0F8DG32H5 Cat hero, B0DKD2S3JT Bunny secondary)
**Result:** Success

**What happened:**
- First-ever deep dive. Late Launch → Early Scaling stage. 45.1% ACoS, $1,138/30d spend, 92 orders.
- Full data collection: 30d campaigns, search terms, placements, keywords, targets, rank radar (50 KW per ASIN), niche keywords, Seller Board.
- Key finding: Auto is star performer (13.5% ACoS, 10.2% CVR, 24 orders on 9% of spend). Top 3 spenders (MK broad + PT + SK loom kit) consume 78% of budget at 62% blended ACoS.
- Placement analysis revealed fundamental structural problem: massive TOS modifiers (121-261%) inflate bids on Top of Search, but most conversions happen on "Other on Amazon."
- 9 of 12 campaigns at 0% budget utilization because TOS-only placement structure — invisible on PP/ROS.
- 12-item action plan generated. User approved Actions 1-6, rejected Action 7 (pause 2 dead MK campaigns — user thinks knitting root has potential).
- User modified Action 1 (Auto budget $15→$20/day), Actions 4+5 (lower PP/ROS modifiers to ~15% each).
- User flagged PP/ROS modifiers as "test run" — uncertain about conversion, wants to monitor.
- 12 API calls (9 campaigns + 2 targets + 1 keyword), 0 errors.

**What didn't work:**
- Nothing significant — all API calls succeeded on first attempt.
- Bid recommender had already partially executed (MK broad TOS 207%→183%) before deep dive. Noted and continued to user's target of 148%.

**Lesson learned:**
- **User concerns about PP/ROS conversion are valid and should be explicitly tracked.** The user flagged PP/ROS as a test run — this means at the 7-day re-check, PP/ROS placement-specific performance must be pulled and presented. If conversion is poor, user may want modifiers removed.
- **Users may reject "pause" recommendations in favor of "investigate."** Action 7 (pause 2 dead MK campaigns) was rejected because user sees potential in the knitting root keyword family. Always present pausing as optional, not default.
- **No dedicated "knitting loom" campaign exists** — user asked about this specifically. Only related items: PAUSED keyword "loom knitting kit" in MK root, active "knitting loom kit" in MK other root, and the SK loom knitting kit campaign. The Auto-discovered "knitting loom" (8.9% ACoS) remains a P3 campaign creation candidate.
- **Seller Board variant economics drive strategy.** Cat is PPC-dependent (55-67% revenue), Bunny is organic-dominant (0-33%). This mirrors Latch Hook Pillow's Owl pattern. Don't blanket-optimize.

**Tokens/cost:** ~60K tokens

### Run: 2026-03-05 — Biggie Beads Portfolio
**Target:** Biggie Beads (212667249843570) — 5 ENABLED, 1 PAUSED, 5 ARCHIVED campaigns, 1 ASIN (B07D6D95NG)
**Result:** Success

**What happened:**
- First-ever deep dive. Scaling portfolio (30% ACoS target). 31.9% ACoS, $1,001/30d spend.
- Old "biggie beads auto" campaign is ARCHIVED (not active as assumed from cached search term data).
- Root cause of inefficiency: No PP/ROS modifiers on ANY campaign, SK biggie beads outbid by MK broad (broken traffic isolation), 3 campaigns with zero negatives, 2 dead campaigns (MK root hero keyword PAUSED, SK 10mm starved).
- 7 API changes executed, 0 errors: 3 PP/ROS modifier additions, 1 bid increase ($0.52→$1.08), 3 campaign-level negatives ("biggie beads" EXACT on MK broad for isolation, "orbeez" EXACT on MK broad + SPA auto).
- Search term harvest found 0 P1 negates (portfolio well-protected with 74 negatives), 4 P2 (2 recommended for negation), 14 PROMOTE candidates, 60 DISCOVER terms.
- Identified 2 high-value keyword families for new SK campaigns: "large perler beads" (18 orders combined, 17.8% blended ACoS) and "large fuse beads" (11 orders, 13.5% ACoS).
- Portfolio tracker fully populated from empty skeleton. Agent-state updated.

**What didn't work:**
- All Amazon Ads reports stuck PENDING (repeat error). Used cached 30d data as workaround.
- Cached data uses `campaignName` not `campaignId` — must filter by name.
- Rank radar and niche keyword files too large for Read tool, required Python scripts.
- Unicode encoding error in niche keyword parsing on Windows cp1252 (partial data captured).

**Lesson learned:**
- "Old" campaigns in cached search term data may be ARCHIVED — always verify current state via list_sp_campaigns before assuming a campaign exists.
- PP/ROS missing is systemic across many portfolios. Now confirmed on 3 deep dives (Latch Hook, Princess Lacing, Biggie Beads). Should be checked in every future audit.
- SK campaigns need bid higher than the MK broad effective bid to capture traffic. Formula: SK_bid × (1 + TOS%) > MK_broad_bid × (1 + MK_TOS%). Otherwise MK broad cannibalizes.
- Account-level search term harvesting on a portfolio-filtered basis works well. 687 terms classified efficiently.

**Tokens/cost:** ~80K tokens across 2 sessions (context restart)

### Run: 2026-03-05 — Latch Hook Pillow Portfolio
**Target:** Latch Hook Pillow (123410007744587) — 10 ENABLED, 0 PAUSED campaigns, 3 ASINs (B0F8R652FX hero, B0FHMRQWRX Owl profit engine, B0F8R6J7JR Googley Eyes poor CVR)
**Result:** Success

**What happened:**
- First-ever deep dive for this portfolio. Stage: Late Launch → Early Scaling (30% ACoS target).
- Full data collection: Seller Board 30d (3 ASINs), Rank Radar (50 KW via Owl variant), niche keywords, per-campaign keywords/negatives/bids/budget utilization, bid recommendations.
- All 10 Amazon Ads reports (5 original + 5 retry) stuck PENDING throughout entire session (repeat error x10+). **Workaround: extracted Latch Hook Pillow campaign data from account-wide 30d search term report cached from Mar 3.** This gave 479 entries across 10 campaigns — sufficient for full 30d per-campaign analysis.
- **Key discovery: 0% budget utilization was misleading.** Daily snapshot showed 8/10 campaigns at 0% utilization, but 30d search term data proved all 10 were spending. Root cause of under-spending: 7 campaigns missing PP/ROS placement modifiers = invisible on non-TOS placements.
- **Owl variant (B0FHMRQWRX) is profit engine:** $2,148 sales, 26.9% margin, 87% organic, 7.3% TACoS. Correctly excluded from PPC changes.
- **Googley Eyes (B0F8R6J7JR) has listing problem:** 0.72% CVR on 139 clicks = not a PPC issue. Flagged for listing review.
- 12-item action plan covering: self-ASIN negation, PT restructure, Auto taming, PP/ROS activation on 7 dormant campaigns, waste negatives, competitor targeting, star campaign budget increase, cross-campaign isolation.
- User approved all 12 with modification: Action 4 PP +26% / ROS +31% (instead of proposed +13% / +18%).
- All 12 actions executed: 0 API errors. 10 campaigns modified, 9 negatives added, 1 target added, 1 target negated.

**What didn't work:**
- Amazon Ads reports stuck PENDING for entire session — 10 reports created (5 + 5 retry), ALL remained PENDING. Worst occurrence yet. Workaround with cached search term data was effective.
- `manage_sp_negative_targets` API requires uppercase `ASIN_SAME_AS` expression type, not camelCase `asinSameAs`. HTTP 400 on first attempt.
- `create_sp_campaign_negative_keywords` requires `campaignId` and `state` in each keyword object. HTTP 400 without them.
- `get_sp_bid_recommendations` returned wrong results when using fabricated ad group ID. Must pull actual ad group ID first.
- HTTP 429 rate limit on bid recommendations — resolved by retry.

**Is this a repeat error?** Yes — Amazon Ads reports stuck in PENDING (worst occurrence: 10 reports, 0 resolved in entire session. x7+ for portfolio action plan runs).

**Lesson learned:**
- **0% budget utilization is a DAILY snapshot, not a structural indicator.** Always cross-reference with 30d search term spend data before concluding campaigns are dead. 8 campaigns at 0% today were all spending over 30 days.
- **Missing PP/ROS modifiers = invisible campaigns on non-TOS placements.** This is likely the #1 cause of "dormant but ENABLED" campaigns across the account. Should be checked in every deep dive.
- **Account-wide search term data is a reliable fallback when campaign reports are PENDING.** Filter by campaign IDs to get per-campaign 30d performance. The data was cached from a previous session and worked perfectly.
- **API format: `ASIN_SAME_AS` (uppercase), not `asinSameAs` (camelCase).** Same pattern as targets: SP v3 API uses SCREAMING_SNAKE_CASE for expression types.
- **Campaign negative keywords require campaignId + state in EACH object.** Unlike ad-group negatives where the ad group ID is a parent parameter.
- **Seller Board 30d per-ASIN data reveals variant economics.** Owl at 26.9% margin vs Hero at 2.1% margin = completely different PPC strategies per variant. Don't blanket-optimize.

**Tokens/cost:** ~120K tokens across 2 sessions (context continuation)

### Run: 2026-03-05 — Princess Lacing Cards Portfolio
**Target:** Princess Lacing Cards (96459368614125) — 8 ENABLED, 5 PAUSED campaigns, 1 ASIN (B0FQC7YFX6)
**Result:** Success

**What happened:**
- First-ever deep dive for this portfolio. Was flagged as RED FLAG (62.4% ACoS) in portfolio summary.
- Full data collection: 30d campaign report (cached Mar 2), 14d search terms (cached Mar 2), rank radar (50 KW, 27 top-50), niche keywords (41 KW), Seller Board 7d.
- All 5 Amazon Ads reports stuck PENDING throughout session (repeat error x7). Used cached reports as fallback.
- **Critical discovery: keyword identity crisis.** Product is "Princess Lacing Card Kit" but MK broad was driving rank on "sewing" terms, not "lacing" terms. Rank radar confirmed: "sewing" keywords improving, "lacing" keywords declining. "Lacing cards" (6,761 SV, #1 keyword) dropped 22→34.
- **User corrected portfolio stage: this is LAUNCH, not Scaling.** Changed analysis framework from ACoS-focused (30% target) to rank-velocity-focused (60%+ acceptable). This fundamentally shifted recommendations from cost-cutting to rank-building.
- Two existing PAUSED SK campaigns for "lacing cards" and "lacing cards for kids ages 3-5" were re-enabled as Tier 1 hero campaigns (new bids, TOS, budgets) instead of creating new ones.
- 15 API calls, 0 errors. Major restructuring: MK broad demoted from 49.6% spend driver to discovery role, 2 hero SK campaigns enabled, traffic isolation via 8 new negatives.

**What didn't work:**
- Amazon Ads API reports stuck in PENDING during entire session (7th occurrence). No fresh 30d or placement data available.
- Initial analysis used Scaling framework (30% ACoS target) until user corrected to Launch. This would have led to over-aggressive cost-cutting recommendations that harm rank velocity.
- Attempted to create 2 new campaigns but they already existed as PAUSED — had to pivot to re-enabling with updated settings.

**Is this a repeat error?** Yes — Amazon Ads reports stuck in PENDING (Known Issue → Repeat Error, 7th occurrence overall).

**Lesson learned:**
- **ALWAYS ask/verify portfolio stage before analysis.** The difference between Launch (rank velocity priority) and Scaling (ACoS priority) fundamentally changes every recommendation. For Launch: high ACoS may be acceptable if driving rank. For Scaling: high ACoS is the problem to solve. This portfolio was misanalyzed initially because stage wasn't in business.md.
- **Check for existing PAUSED campaigns before creating new ones.** Amazon rejects duplicate campaign names. The two "lacing cards" campaigns already existed but were paused — re-enabling with new settings was the right move and saved time.
- **MK broad cannibalization of SK campaigns is a structural pattern.** When MK broad's effective TOS bid exceeds SK exact bids on the same terms, MK broad wins the auction and the SK campaigns starve. The fix is traffic isolation via negatives in MK broad, NOT raising SK bids.
- **"Dead" SK campaigns may not need bid changes — they need traffic isolation.** 5 of 8 campaigns were getting <$8 spend/30d not because bids were too low, but because MK broad was eating all their impressions. Negating the relevant terms from MK broad is the structural fix.
- **Keyword identity drift is measurable via rank radar.** "Sewing" terms improving + "lacing" terms declining = PPC spend is teaching Amazon the wrong product association. The fix is creating dedicated SK exact campaigns for the target identity keywords.
- **Cached data from recent runs is a reliable PENDING fallback.** 30d campaign report from Mar 2 (3 days old) was sufficient for analysis. Search terms 14d from Mar 2 provided enough waste signal. Always check cached data before waiting for fresh reports.

**Tokens/cost:** ~80K tokens across 2 sessions (context continuation)

### Run: 2026-03-05 — Embroidery for Kids Portfolio
**Target:** Embroidery for Kids (71655754369545) — 8 ENABLED, 8 PAUSED campaigns, 2 ASINs (B09X55KL2C hero, B08DJYBH4D legacy/paused)
**Result:** Success

**What happened:**
- First-ever deep dive for this portfolio. Was flagged as RED FLAG (61.3% ACoS) in weekly summary.
- Full data collection: 30d campaign report, 30d search terms (295+87+17+6 terms), 30d placements, rank radar (50 KW), niche keywords (89 KW), Seller Board 7d, budget utilization.
- All 5 Amazon Ads reports initially stuck PENDING (repeat issue x4+). Reports resolved ~30 minutes later — all 5 downloaded successfully.
- Critical findings: MK broad at 47.9% of spend (48.8% ACoS), SK TOS at 199% (46.7% ACoS), PT budget-starved at 99.66%, negative profitability on Seller Board.
- **Placement data was the game-changer:** Revealed that MK exact TOS was actually efficient (32.3% ACoS) while "Other on-Amazon" was the real waste (81.5%). This revised the original Item 4 recommendation — presented 3 options (A/B/C) to user with full transparency.
- 12-item action plan generated across P1-P4. User approved all 4 P1 items.
- Execution: 4 API calls, 0 errors. 3 TOS reductions + 1 budget increase.

**What didn't work:**
- Amazon Ads API reports stuck in PENDING during initial data collection (5th+ occurrence across all portfolio action plan runs).
- Context window ran out during initial session — required session continuation.
- Initial Item 4 recommendation (lower MK exact TOS 158%→107%) was based on 30d campaign-level data. Placement data revealed TOS was actually the efficient placement — the waste was in "Other on-Amazon" (81.5% ACoS, no placement modifier available). Presented revised options to user.

**Is this a repeat error?** Yes — Amazon Ads reports stuck in PENDING (Known Issue → Repeat Error, 4th+ occurrence in portfolio action plan runs).

**Lesson learned:**
- **ALWAYS pull placement data before making TOS recommendations.** Campaign-level ACoS hides placement-level efficiency. A campaign at 31.6% ACoS might have TOS at 32.3% (efficient) and "Other" at 81.5% (terrible). Reducing TOS on this campaign would hurt the good placement. This is the same class of error as the Fairy Family lesson (900% TOS on dead campaign ≠ emergency) — structural analysis alone is misleading.
- **Placement report is the most valuable report for TOS decisions.** Prioritize getting this report before making any TOS recommendations. If reports are PENDING, wait for placements specifically.
- **"Other on-Amazon" placement has no bid modifier.** Amazon only offers TOS and Product Page modifiers. When "Other" is the waste source, the lever is lowering the DEFAULT BID (not TOS). This wasn't obvious until this run.
- **Present multiple options when placement data contradicts initial recommendation.** User appreciated the transparency of Options A/B/C for Item 4.
- **Reports DO eventually resolve.** All 5 reports that were PENDING for 30+ minutes resolved within the same session. Worth checking periodically rather than immediately falling back to weekly snapshots.
- **Budget-starved campaigns are the easiest wins.** PT at 99.66% utilization with 31.8% ACoS — increasing budget from $7→$12 is pure upside.

**Tokens/cost:** ~100K tokens across 2 sessions (context continuation)

### Run: 2026-03-05 — Cross Stitch Backpack Charms Portfolio
**Target:** Cross Stitch Backpack Charms (69655270409648) — 15 ENABLED, 4 PAUSED campaigns, 4 ASINs
**Result:** Success

**Goals:**
- [x] Deep dive analysis (15 ENABLED campaigns)
- [x] Action plan generation (9 items)
- [x] Execution of approved items (7/9 executed, 2 deferred as P3 investigate)

**What happened:**
- Full deep dive with rank radar (38 KW, 35 top-10), niche keywords (100+ KW), Seller Board, 30d reports (campaigns, search terms, placements).
- 30d data: $2,001 spend, $6,326 sales, 31.6% ACoS, 293 orders, 15.0% CVR (vs 30% ACoS / 10% CVR targets).
- Hero campaign MK broad 2 at 28.9% ACoS and 18.4% CVR was budget-capped at $35/d — immediate budget increase.
- Two SK TOS push campaigns underperforming (42-64% ACoS) on keywords where B08DDJCQKF already ranks #1 organically.
- 6 dormant campaigns with $80/d allocated budget generating $0.93 total spend — flagged for investigation.
- User approved 7 of 9 actions with modifications (budget $50→$45 for MK broad 2). Required detailed placement breakdowns (TOS/ROS/PP spend, ACoS, orders) for each campaign before approving actions 3-9.
- Executed: 2 budget increases, 4 TOS modifier reductions, 9 phrase negatives across 3 campaigns. 0 API errors.

**What didn't work:**
- **CRITICAL: Initial analysis included campaigns from WRONG portfolios.** Name-based filtering (patterns like "cross stitch") matched campaigns from portfolio 8418766616949 ("Cross And Embroidery Kits") and 226460450341570 ("Shield All"). User caught the error: "This is not the right portfolio."
- Fix: Verified each campaign's `portfolioId` field via API. Rebuilt entire analysis using only the 15 correct campaign IDs.
- Amazon Ads reports initially stuck PENDING but all resolved by the time analysis continued (6th occurrence).
- API `list_sp_campaigns` with `state=ALL` returned 200 items (max limit), all PAUSED/ARCHIVED, hiding the 15 ENABLED campaigns. Had to use `state=ENABLED` with name filters.

**Is this a repeat error?** Yes — Amazon Ads reports stuck in PENDING (6th occurrence overall, 4th in portfolio action plan runs).

**Lesson learned:**
- **CRITICAL: Never scope a portfolio by campaign name patterns.** Campaign names like "cross stitch" appear across multiple portfolios. Always verify portfolio membership via the `portfolioId` field on each campaign. This caused an incorrect analysis that the user had to catch.
- **API `state=ALL` is unreliable for large portfolios.** The 200-item limit means ARCHIVED campaigns fill the response before ENABLED ones appear. Always query `state=ENABLED` explicitly.
- **User requires placement-level detail before approving TOS changes.** Showing per-placement ACoS, spend, and orders (TOS vs ROS vs PP) is essential for informed decisions. Added to standard pre-approval data requirements.
- **Organic rank dominance reduces TOS value.** B08DDJCQKF ranks #1 organically on most core keywords — aggressive TOS pushes provide diminishing returns. TOS spending should focus on keywords where organic rank is weak (#4+), not where it's already dominant.
- **Budget-capped campaigns at good ACoS = easy win.** MK broad 2 at 28.9% ACoS hitting 100% budget utilization was the highest-impact single change.

**Tokens/cost:** ~90K tokens (multi-session: initial data pull → user correction → reanalysis → execution)

### Run: 2026-03-03 — Fairy Family Portfolio
**Goals:**
- [x] Deep dive analysis (20 ENABLED, 14 PAUSED campaigns)
- [x] Action plan generation (12 items across P1-P4)
- [x] Execution of approved items (5/5 success)

**Result:** Success

**What happened:**
- Full deep dive with rank radar (87 KW), niche keywords (309 KW), Seller Board, campaign structure, and search terms (272 terms across 13 campaigns).
- Initial action plan had 5 P1 items. 30d report data (finally available after being stuck PENDING in earlier session) revealed 2 of 5 P1 items had zero financial impact (900% TOS autos were completely dead) and 1 P1 item was WRONG (recommending TOS decrease on the best performer at 13.3% ACoS).
- Revised P1 to 4 items. User approved all + modified item 5 from "lower TOS" to "increase budget" (correct call).
- All 5 approved changes executed: 2 API calls, 0 errors.
- Added 7 new pending actions for follow-up (bleeding SK sewing for kids, keyword gap campaigns, 7-day re-check).

**What didn't work:**
- Amazon Ads API reports stuck in PENDING during initial data collection. They came through ~1 hour later when user requested detailed data.
- Initial P1 recommendations were wrong without 30d data. Two 900% TOS campaigns appeared scary but had zero activity. Top performer appeared over-TOS'd but was actually crushing it.

**Is this a repeat error?** Yes — Amazon Ads reports stuck in PENDING (Known Issue #2, 2nd occurrence across portfolio action plan runs).

**Lesson learned:**
- **NEVER make TOS/bid recommendations without 30d campaign performance data.** Structural analysis alone is misleading — 900% TOS on a dead campaign is cleanup, not emergency. 311% TOS on a 13.3% ACoS campaign is working perfectly.
- **Always present per-campaign 30d metrics (spend, sales, ACoS, CVR, orders) before asking for approval.** User correctly demanded this and it changed 3 of 5 P1 items.
- **User instincts on their own campaigns are valuable.** User recognized top performer and redirected action from "lower TOS" to "increase budget."
- **Reports stuck in PENDING may resolve after time.** Worth re-checking old report IDs in follow-up sessions rather than always creating new reports.
- **MK broad cannibalization is a systemic issue.** The MK broad was 41% of portfolio spend at 46.2% ACoS, competing with its own SK campaigns. This pattern likely exists in other portfolios.

**Tokens/cost:** ~80K tokens (deep dive + data revision + execution)

### Run: 2026-03-05 (cont.) — Cross & Embroidery Campaign Creation
**Target:** Cross And Embroidery Kits (8418766616949) — New SK "cross stitch kits" EXACT
**Result:** Success

**What happened:**
- Created SK EXACT campaign for "cross stitch kits" — proven 13.7% ACoS, 18.5% CVR via Auto discovery.
- Campaign 44316151159540 created ENABLED, ad group 486177026939878, keyword 350687503244165 ($0.58 bid), ad 532726538014658.
- 75 PHRASE negatives seeded (1 rejected: "counted cross stitch fabric only" too long). Source negative in Auto campaign for traffic isolation.
- SKU `75-24RO-YAXR` found by calling get_fba_inventory without asin_filter (asin_filter aggregates).

**What didn't work:**
- Product ad creation needed SKU — `get_fba_inventory(asin_filter=...)` aggregates and hides SKU names.
- Amazon rejects negative keywords >4 words.
- Bid rec API returned 429 — used manual CPC calculation.

**Lesson learned:**
- **get_fba_inventory without asin_filter returns individual SKUs.** With filter, it aggregates across SKUs and hides names. Known issue with MCP server aggregation logic.
- **Amazon campaign negative keyword max: 4 words.** Factor this into negative keyword generator.
- **Campaign creator works end-to-end in 4 API calls.** Campaign → ad group → product ad (with SKU) → keyword. Can be done sequentially in ~30 seconds.

**Tokens/cost:** ~15K tokens (continuation session)

### Run: 2026-03-05 — Cross & Embroidery Kits Portfolio
**Target:** Cross And Embroidery Kits (8418766616949) — 7 ENABLED, 7 PAUSED campaigns, 2 ASINs
**Result:** Success

**What happened:**
- Deep dive started Mar 3, 30d reports stuck PENDING. Completed Mar 5 when all 5 reports resolved.
- Full 30d data: $729 spend, $1,744 sales, 41.8% ACoS, 86 orders, 452 search terms.
- CRITICAL finding: Zero negative keywords across all 14 campaigns. 48.5% waste ($353/30d).
- 2 ENABLED campaigns dead (0 impressions/30d) — root cause: ad groups PAUSED while campaigns ENABLED.
- "Embroidery kit for kids" keyword bleeding $73.91/30d at 312% ACoS.
- 12-item action plan generated. User approved items 1-5 + 7-9. Item 6 investigated in detail (dead campaigns).
- Execution: 14 negatives created, 2 keywords paused, 2 re-enabled, 3 bids adjusted, 1 TOS modifier reduced. 0 errors.
- Large kit (B0F8QZZQQM) losing rank rapidly (-60 positions/28d) with all campaigns paused — flagged for user decision.

**What didn't work:**
- 30d reports stuck PENDING during initial Mar 3 session (5th occurrence across all runs).
- Context window ran out during Mar 3 data collection — required session continuation on Mar 5.

**Is this a repeat error?** Yes — Amazon Ads reports stuck in PENDING (Known Issue #2, 3rd occurrence in portfolio action plan runs).

**Lesson learned:**
- **PAUSED ad groups are an invisible killer.** Campaign-level checks show ENABLED, budget checks show allocation. Only ad-group-level query reveals the truth. Add to standard deep dive checklist.
- **Zero negatives = immediate P1 action.** This should be the FIRST thing checked in every portfolio deep dive. If zero negatives, flag before any other analysis.
- **30d reports self-resolve in 1-2 days.** Save report IDs and re-check in follow-up sessions. Don't create duplicate reports.
- **Cross-session deep dives work.** Data collection (session 1) + execution (session 2) is a valid pattern when reports are slow. All data files persisted correctly between sessions.
- **Embroidery ≠ cross stitch in shopper intent.** Even though the product includes embroidery elements, "embroidery kit for kids" shoppers want traditional embroidery, not cross stitch. This pattern likely applies to other portfolios with mixed craft terms.

**Tokens/cost:** ~65K tokens across 2 sessions

---

### Run: 2026-03-03 — Catch-All Auto Portfolio
**Target:** Catch All Auto (6 campaigns: 3 mature with negatives, 3 unprotected with zero negatives)
**Result:** Success

**What happened:**
- Deep dive identified critical negative keyword gap: campaigns 4-6 had 0 negatives vs 215-450 in campaigns 1-3.
- User correctly challenged blanket negative copying — demanded performance validation.
- Cross-referenced 1,099 negatives from campaigns 1-3 against 14-day search term data (7,080 rows).
- Found 81.5% of spend in campaigns 4-6 ($764.40) went to zero-order terms.
- Built curated lists preserving all converting terms:
  - LIST 1: 129 safe-to-negate (zero orders across ALL 6 campaigns)
  - LIST 2: 36 to un-negate from campaigns 1-3 (converting well in 4-6)
- Applied: 5 top waste negatives + 75 preventive negatives in campaigns 4-6 (240 total). Un-negated 36 terms in campaigns 1-3 (58 keywords PAUSED).

**What didn't work:**
- Amazon Ads API search term reports stuck in PENDING — fell back to weekly snapshot.
- Campaign-level negative keywords don't support ARCHIVED state (only ENABLED/PROPOSED/PAUSED).
- New MCP tool needed for un-negation but server didn't auto-reload — used standalone Python script.

**Lesson learned:**
- **Always cross-reference negatives with performance data before applying.** Mature campaign negatives can include terms that convert in other campaigns.
- **Campaign-level negatives use PAUSED (not ARCHIVED) for deactivation.** Different from ad-group level negatives.
- **User collaboration on negative strategy is essential.** The user's instinct to protect converting head terms saved $1,053/14d in revenue.
- **Preventive negation is high-value, low-risk.** 75 terms with zero spend AND zero orders across all campaigns = zero risk of revenue loss.
- **Standalone API scripts are reliable MCP fallback.** Pattern: load .env → LWA token → httpx PUT/POST with v3 headers.

---

## Known Issues

### 1. Never scope portfolios by campaign name patterns
**Impact:** CRITICAL — Name-based filtering (e.g. "cross stitch") matches campaigns across multiple portfolios. This caused an entire analysis to include wrong campaigns, caught only by the user.
**Rule:** Always verify campaign membership via the `portfolioId` field. Query `list_sp_campaigns` with `portfolio_id` parameter, NOT name patterns, to get the correct campaign set.
**Also:** `state=ALL` with large portfolios returns 200 ARCHIVED items first, hiding ENABLED campaigns. Always query `state=ENABLED` explicitly.

### 2. Campaign-level negative keywords: PAUSED not ARCHIVED
**Impact:** HIGH — Using ARCHIVED state causes 400 error from Amazon Ads API.
**Workaround:** Use `"state": "PAUSED"` for campaign-level negatives. Only ad-group level negatives support ARCHIVED.
**Valid states:** ENABLED, PROPOSED, PAUSED.

### 3. Weekly summary portfolio aggregation can produce wrong ACoS
**Impact:** HIGH — Needlepoint showed 92% ACoS in weekly summary but raw data showed 68.7%. 23pp discrepancy. Propagated into timeseries-backfill and deep dive brief.
**Rule:** When using weekly summary data for portfolio-level metrics, cross-validate by summing campaign-level data from the raw report file. Flag any discrepancy >2%.
**Root cause:** Weekly analysis summary.json aggregation step miscounted sales for Needlepoint portfolio. Discovered 2026-03-09 by user checking Seller Central.

### 4. Always label exact date ranges on weekly metrics
**Impact:** MEDIUM — "This week's ACoS" is ambiguous. Amazon Ads API `LAST_7_DAYS` returns rolling windows (e.g., Feb 27–Mar 5 when pulled Mar 8), not calendar weeks (Mar 1–7). User requires calendar-aligned weeks.
**Rule:** Never say "this week" without the exact date range. Prefer calendar-aligned weeks (Mar 1–7, Mar 8–14). When using API rolling windows, always label: "Feb 27–Mar 5 (rolling 7d)."

---

## Repeat Errors

### 1. Amazon Ads API reports stuck in PENDING (x7+)
**Impact:** MEDIUM — Fresh data unavailable during initial analysis; must fall back to weekly snapshot files or cached account-wide data.
**Occurrences:** Catch-All Auto (2026-03-03), Fairy Family (2026-03-03), Cross & Embroidery (2026-03-03→05), Cross Stitch Backpack Charms (2026-03-05), Embroidery for Kids (2026-03-05), Princess Lacing Cards (2026-03-05), **Latch Hook Pillow (2026-03-05 — worst: 10 reports, 0 resolved)**.
**Workaround:** Use existing data from `outputs/research/ppc-weekly/data/search-terms-*` as fallback. Reports may resolve after ~30min — worth re-checking old report IDs. In the Embroidery for Kids run, all 5 reports resolved within the same session after ~30 minutes. **New fallback: extract portfolio data from account-wide cached search term reports by filtering on campaign IDs.**
**Root cause:** Amazon-side delay. Not a code/auth issue.

### 2. SP v3 API SCREAMING_SNAKE_CASE format errors (x2)
**Impact:** LOW — API call fails with 400, fixed on retry with correct casing.
**Occurrences:** Latch Hook Pillow (2026-03-05: `asinSameAs` → `ASIN_SAME_AS`), Needlepoint (2026-03-05: `asinSameAs` → `ASIN_SAME_AS`, `manual` → `MANUAL`).
**Rule:** All SP v3 expression types and enum values use SCREAMING_SNAKE_CASE: `ASIN_SAME_AS`, `MANUAL`, `NEGATIVE_EXACT`, `LEGACY_FOR_SALES`, etc. Never use camelCase.

---

## Resolved Issues

_None yet._
