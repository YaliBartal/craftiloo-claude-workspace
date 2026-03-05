# PPC Agent — Lessons Learned

## Run Log

*(New entries go at the TOP)*

### Run: 2026-03-05 (4)
**Task routed:** PT Campaign Restructuring — Cross & Embroidery (ppc-portfolio-action-plan)
**Result:** Success

**What happened:**
- User decided: keep dead embroidery campaigns paused (ce-001), keep large kit deactivated (ce-002), restructure PT campaign (ce-004).
- PT campaign 457220499383709: PAUSED→ENABLED, budget $7→$12/day, TOS 101%→31%, PP 0%→53%.
- Stale target B0D8171TF1 PAUSED. Existing bids reduced (EZCRA $0.92→$0.43, KRAFUN $0.92→$0.41).
- 7 new competitor ASIN targets created across 3 tiers. Total: 9 active targets.
- All pending actions for Cross & Embroidery portfolio now resolved (0 remaining).

**What didn't work:**
- `manage_sp_targets` create: expression type must be `ASIN_SAME_AS` (uppercase), not `asinSameAs` (camelCase from MCP docs). `expressionType` must be `MANUAL` (uppercase).
- SP targets use PAUSED not ARCHIVED for deactivation (same pattern as campaign-level negatives).
- Rate limit 429 on first target update attempt — succeeded on retry.

**Lesson learned:**
- **SP target API casing: ASIN_SAME_AS, MANUAL (all uppercase).** MCP tool docs show camelCase but API requires SCREAMING_SNAKE_CASE.
- **SP targets: PAUSED not ARCHIVED.** Third entity type with this pattern (campaign negatives, targets). Assume PAUSED-only for all v3 SP endpoints.
- **PT campaigns should emphasize PP modifier over TOS.** Product Pages had 14.4% ACoS vs TOS 44.2% — PP is where PT conversions happen.

**Tokens/cost:** ~10K tokens

### Run: 2026-03-05 (3)
**Task routed:** Campaign Creation — Cross & Embroidery SK "cross stitch kits" (ppc-campaign-creator)
**Result:** Success

**What happened:**
- User approved campaign card for SK EXACT "cross stitch kits" targeting B0F6YTG1CH (small kit).
- Campaign created ENABLED (user requested active state, not default PAUSED).
- 4-step creation: campaign → ad group → product ad → keyword. Product ad initially failed (SKU missing), resolved by pulling full inventory without asin_filter.
- 75 of 76 PHRASE negatives seeded successfully. 1 rejected: "counted cross stitch fabric only" (Amazon rejects >4 word negative phrases).
- Source negative "cross stitch kits" NEG_EXACT added in Auto campaign for traffic isolation.

**What didn't work:**
- Product ad creation failed first attempt: `manage_sp_product_ads` requires `sku` field. The `get_fba_inventory(asin_filter=...)` aggregates across SKUs and doesn't show individual SKU names. Had to call without asin_filter to get all 250 SKUs.
- Amazon Ads bid recommendation API returned 429 (rate limited) — used manual calculation from portfolio CPC data.
- "counted cross stitch fabric only" (5 words) rejected by Amazon as invalid negative keyword pattern.

**Lesson learned:**
- **SKU discovery: call `get_fba_inventory()` WITHOUT asin_filter.** The asin_filter parameter triggers aggregation that hides individual SKU names. Without filter, returns all 250 SKUs with ASIN mapping.
- **Amazon negative keyword limit: max 4 words per term.** "counted cross stitch fabric only" (5 words) rejected. Shorten or split when generating negatives.
- **Bid rec API 429s are common.** Fallback: use portfolio average CPC × PROMOTE factor (1.07) as base bid, then add irregularity.

**Tokens/cost:** ~15K tokens (continuation from deep dive session)

### Run: 2026-03-05 (2)
**Task routed:** Cross & Embroidery Kits Portfolio Deep Dive (ppc-portfolio-action-plan)
**Result:** Success

**What happened:**
- Full deep dive of Cross & Embroidery Kits portfolio: 7 ENABLED + 7 PAUSED campaigns, 2 ASINs (B0F6YTG1CH small kit, B0F8QZZQQM large kit).
- 30-day reports (5 total) stuck PENDING during initial session (Mar 3), all completed by Mar 5. Full 30d data: $729 spend, $1,744 sales, 41.8% ACoS, 86 orders, 8.2% CVR.
- Critical finding: ZERO negative keywords across all 14 campaigns. 48.5% of spend ($353) wasted on zero-order terms.
- "Embroidery kit for kids" keyword burning $73.91/30d at 312% ACoS — wrong product match for cross stitch kit.
- 2 ENABLED campaigns dead (0 impressions/30d) — root cause: ad groups PAUSED while campaigns ENABLED.
- User approved items 1-5 + 7-9 (negatives, keyword pauses, TOS reduction, keyword re-enables, bid adjustments). All executed: 14 negatives created, 2 keywords paused, 2 re-enabled, 3 bids adjusted, 1 campaign TOS updated. 0 errors.
- Item 6 (dead campaigns) investigated in detail — recommended pausing both embroidery campaigns entirely.

**What didn't work:**
- Reports PENDING during initial Mar 3 session (5th occurrence of this issue). Self-resolved by Mar 5. Lesson from earlier sessions applied: re-checked old report IDs instead of creating new ones.

**Lesson learned:**
- **PAUSED ad groups with ENABLED campaigns = invisible dead campaigns.** Neither campaign-level status checks nor budget utilization reveal this. Must check ad group state during structure audits.
- **Zero negative keywords across an entire portfolio is a massive red flag.** This should be a standard check in every deep dive — the first thing to look for.
- **Reports stuck PENDING self-resolve within 1-2 days.** 5th occurrence confirms this pattern. Always save report IDs and re-check rather than creating duplicates.
- **30d data critical for keyword-level decisions.** The "embroidery kit for kids" keyword appeared marginal in weekly data but 30d confirmed it's a $74/mo waste at 312% ACoS.

**Tokens/cost:** ~65K tokens (multi-session: initial data pull Mar 3 + execution Mar 5)

### Run: 2026-03-05
**Task routed:** Daily PPC Health Check (ppc-daily-health)
**Result:** Success

**What happened:**
- Routed "daily health check" → ppc-daily-health. Third run of this sub-skill.
- 156 ENABLED campaigns (+1 vs Mar 3). 2-day gap since last daily check.
- Fairy Family deep dive changes validated: +3 top-10 keywords in 2 days. Best rank gainer.
- 4 RED, 4 YELLOW, 9 GREEN, 1 PAUSED. Same structure as Mar 3.
- Flagged 4 Flowers listing verification as OVERDUE (due Mar 4).
- 13 pending actions. Net top-10 rank: -3 across account.

**What didn't work:**
- Market intel data 4 days stale (Mar 1). Weekly PPC data from Feb 20-26 still in use.

**Lesson learned:**
- Fairy Family +3 after TOS rebalancing validates the deep dive approach. Track at 7-day mark (Mar 10) for confirmation.
- Mini Fuse Beads -2 is expected post-restructuring noise. Don't overreact.

**Tokens/cost:** ~25K tokens

### Run: 2026-03-03 (5)
**Task routed:** Fairy Family Portfolio Deep Dive (ppc-portfolio-action-plan)
**Result:** Success

**What happened:**
- Full deep dive of Fairy Family portfolio: 20 ENABLED, 14 PAUSED campaigns. 87 rank radar keywords, 309 niche keywords, 272 search terms across 13 campaigns.
- Initial action plan had 5 P1 items based on structural analysis. When 30d report data became available, 3 of 5 P1 items were revised: two 900% TOS autos had zero activity (moved to P3), and the "lower TOS" on top performer was completely wrong (13.3% ACoS, 29.6% CVR).
- User corrected item 5: changed from "lower TOS" to "increase budget" — smart call.
- Revised plan: 4 P1 items (hero KW rank defense, add TOS to blind SK, reduce MK broad TOS + budget, increase top performer budget).
- 5/5 approved actions executed successfully, 2 API calls, 0 errors.
- Key finding: MK broad at 46.2% ACoS is cannibalization source (41% of portfolio spend competing with own SK campaigns).

**What didn't work:**
- Reports PENDING during initial collection (resolved ~1 hour later). This is the 4th occurrence of this issue.
- Initial P1 plan was significantly wrong without per-campaign 30d data. Structural analysis alone is unreliable for bid/TOS recommendations.

**Lesson learned:**
- **CRITICAL: Always get 30d per-campaign data before making TOS/bid recommendations.** Structure + weekly aggregate ≠ per-campaign truth. Two "emergency" items had zero financial impact, one "too aggressive" item was actually the best performer.
- **Present per-campaign metrics table to user before approval.** User demanded this and it was the right call — changed 3 of 5 items.
- **MK broad cannibalization is likely a systemic issue across portfolios.** The Fairy Family MK broad was competing with its own SK campaigns. Check this pattern in future deep dives.
- **Reports stuck in PENDING may self-resolve.** Re-checking old report IDs saved creating duplicate reports.

**Tokens/cost:** ~80K tokens (deep dive + data revision + execution)

### Run: 2026-03-03 (4)
**Task routed:** Catch-All Auto Portfolio Action Plan (ppc-portfolio-action-plan)
**Result:** Success

**What happened:**
- Full deep dive of 6 Catch-All Auto campaigns. Brief written with 5-item action plan.
- User challenged blanket negative copying — wanted performance validation first.
- Cross-referenced 1,099 negatives from campaigns 1-3 against 14-day search term data for all 6 campaigns.
- Key finding: 36 terms blocked in campaigns 1-3 actually convert well in 4-6 (50 orders, $1,053.76 sales, 10.8% ACoS).
- Built curated lists: 129 safe-to-negate (zero orders everywhere), 36 to un-negate.
- User approved: negated top 5 waste terms + 75 preventive terms in campaigns 4-6 (240 negatives applied). Un-negated 36 terms in campaigns 1-3 (58 keywords set to PAUSED).

**What didn't work:**
- Amazon Ads API search term reports stuck in PENDING (known issue — fell back to weekly snapshot data).
- New MCP tool `update_sp_campaign_negative_keywords` added to server.py but MCP server didn't auto-reload. Had to write standalone Python script for un-negation.
- Campaign-level negative keywords don't support ARCHIVED state — only ENABLED/PROPOSED/PAUSED. Had to use PAUSED instead of ARCHIVED for un-negation.

**Lesson learned:**
- **CRITICAL: Campaign-level negative keywords use PAUSED, not ARCHIVED.** The `campaignNegativeKeywords` v3 endpoint only accepts ENABLED/PROPOSED/PAUSED states. Ad-group level negatives accept ARCHIVED. Different endpoints, different state enums.
- **User insight is essential for negative keyword strategy.** Blanket copying negatives from mature campaigns would have killed 36 converting terms worth $1,053/14d. Always cross-reference with performance data before applying negatives.
- **MCP server changes require restart.** Adding new tools to server.py doesn't take effect until the MCP server process restarts. Keep a standalone script pattern as fallback for urgent operations.
- **Standalone API scripts work well as MCP fallback.** The unnegate_keywords.py pattern (load .env, get LWA token, make direct httpx calls) is reliable and reusable.
- **Batch operations at scale work fine.** Amazon Ads API handles 75 campaign negatives per call without issues (3 × 75 = 225 created in parallel).

**Tokens/cost:** ~80K tokens (multi-session, data-intensive)

### Run: 2026-03-03 (3)
**Task:** P1 Action Item Review — 30-day negation analysis + campaign verification
**Result:** Success

**What happened:**
- Reviewed all 8 P1 actions from weekly analysis + portfolio summary.
- Applied 'toddler sewing' NEGATIVE_EXACT in Princess Lacing MK broad (campaign 560718841724672). Saves ~$112/wk.
- Verified 3 bleeding campaigns already PAUSED, 'perler beads' already addressed, Fairy Family broad already exists.
- Found paused 'cross stitch kits' SK campaign (309035836424147) — re-enable recommended instead of creating new.
- Downloaded 30-day search term report (13,503 rows). Analyzed all 10 negation candidates.
- Critical finding: **4 of 10 flagged terms are actually profitable over 30 days.** Single-week zero-order data nearly led to negating $330/mo of converting keywords.
- Full brief saved to outputs/research/ppc-agent/briefs/2026-03-03-p1-action-review.md

**What didn't work:**
- Amazon Ads API 30-day search term reports take extremely long to generate — both LAST_30_DAYS preset and custom date range format stuck in PENDING for 30+ minutes. The original report from the previous session eventually completed (after session timeout + restart).
- User correctly identified multiple product relevance errors in initial analysis: "embroidery beginner" has the KIDS kit not 4 Flowers, "beginner crochet kit" IS relevant to Bunny Knitting, "sewing for toddlers" could be relevant to Princess Lacing.

**Lesson learned:**
- **CRITICAL: Never assume product→keyword relevance from campaign/portfolio name alone.** Always verify which ASIN a campaign targets before deciding if a search term is relevant. This caused 3 wrong recommendations in one session.
- **CRITICAL: The 30-day rule is essential.** 4 of 10 "negate" recommendations would have killed profitable keywords. Weekly data creates false negatives (terms that didn't convert in 7 days but do over 30 days).
- **Amazon Ads 30-day reports:** Expect 30-60 minute generation time for large accounts. Request the report early, do other work while waiting. The report ID persists across sessions — check old IDs first before creating new ones.
- **Consolidated briefs are better.** User explicitly asked for "all info in one place" rather than scattered findings. Always compile a single comprehensive brief for multi-action reviews.
- When verifying campaign existence, check PAUSED campaigns too — Amazon keeps them indefinitely and they can be re-enabled.

**Tokens/cost:** ~50K tokens

### Run: 2026-03-03 (2)
**Task:** 4 Flowers Phase 2 — Listing Rewrite Pushed via SP-API
**Result:** Success

**What happened:**
- Listing optimizer audit (Mar 2) found CRITICAL 10% Ranking Juice, wrong title ("Sunflower"), empty description, no backend keywords.
- Listing creator (Mar 2) generated optimized rewrite. Today pushed all 4 fields live via new SP-API `update_listing` tool.
- Key discovery: Amazon SKU is `7B-EONH-U3A3` (not internal catalog name EK17). Found via FBA inventory lookup.
- Product type: `ART_CRAFT_KIT` (found via Product Type Definitions API search).
- Submission ID: a7db9ea7233c4245962c10e5821723a0. Status: ACCEPTED, 0 issues.

**What didn't work:**
- SP-API Listings Items API `get_listing` doesn't return `productType` for this SKU — had to query Product Type Definitions API separately.
- Internal SKU "EK17" doesn't match Amazon SKU — need FBA inventory or all-listings report to find actual SKU.

**Lesson learned:**
- Amazon SKUs are auto-generated format (`XX-XXXX-XXXX`), not matching internal catalog names. Always verify via `get_fba_inventory(asin_filter=...)` first.
- SP-API `get_listing` may return `productType: None`. Use Product Type Definitions API with `item_type_keyword` value to look up correct type.
- Listing changes + PPC stabilization is a 1-2 punch: Phase 1 (PPC: Auto/Broad re-enabled) drives traffic, Phase 2 (listing rewrite) improves conversion. Monitor as combined intervention.
- Re-audit due Mar 10 to measure rank recovery + CVR impact of combined PPC + listing changes.

**Tokens/cost:** ~20K tokens, $0 API (SP-API free)

### Run: 2026-03-03
**Task routed:** Daily PPC Health Check (ppc-daily-health)
**Result:** Success

**What happened:**
- Routed "daily health" → ppc-daily-health. Second run of this sub-skill.
- 155 ENABLED campaigns (down from 163 yesterday after Dessert pause + cleanup).
- Day-over-day rank comparison working: Latch Hook Pencil -4 top-10 biggest drop, Fuse Beads +2 showing restructuring impact.
- 4 RED, 4 YELLOW, 9 GREEN, 1 PAUSED. Same RED portfolios as yesterday minus Dessert (now PAUSED).
- 12 pending actions total. Weekly P1 negation/pause actions still outstanding (~$481/wk savings).

**What didn't work:**
- Campaign data returned as JSON code blocks, needed temp Python script to parse (not markdown table).

**Lesson learned:**
- Day-over-day snapshot comparison is the most valuable part of the daily health check — surface rank drops fast.
- 12 pending P1 actions accumulating. Should prompt user more strongly to run Search Term Harvest to clear the backlog.

**Tokens/cost:** ~30K tokens

### Run: 2026-03-02 (5)
**Task routed:** Fuse Beads Action Plan Execution (Steps 1-6 — direct API changes)
**Result:** Success (5/6 executed, 1 pending user decision)

**What happened:**
- User approved 6-step action plan from deep dive. Steps 1-5 executed directly, Step 6 modified to check placement data first.
- Batched Steps 1+2 into single campaign update call (both succeeded).
- Step 3 (new SK campaign) required 4 sequential API calls: create campaign → create ad group → add keyword → add product ad.
- Step 4 (negative keyword) and Step 5 (add keywords) executed in parallel.
- Step 6 (placement analysis): pulled sp_placements report, extracted 4-row placement data for target campaign.

**What didn't work:**
- `create_sp_campaigns` startDate format: API requires `YYYY-MM-DD` (with dashes), not `YYYYMMDD`. Documentation example was misleading.
- `manage_sp_product_ads` create: requires `sku` field for seller accounts, not just `asin`. Had to pull listings report from SP-API to get SKU.
- `sp_placements` report preset: `campaignPlacement` groupBy dimension NOT included as column in report output. Report has 4 rows per campaign but no placement labels. Amazon API does not allow `campaignPlacement` as a column value — it's only a groupBy dimension.

**Lesson learned:**
- Campaign creation startDate must use dashes: `2026-03-02` not `20260302`.
- Product ad creation needs both ASIN and SKU. Keep a SKU-ASIN mapping file or cache the listings report.
- sp_placements report is broken — need to fix by either adding a mapping or using v2 placement API.
- CPC analysis can infer placement: highest CPC = TOS (modifier amplifies bid), highest impressions = ROS/Other.
- Batch independent campaign updates into single API call for efficiency.

**Tokens/cost:** ~45K tokens

### Run: 2026-03-02 (4)
**Task routed:** Fuse Beads Portfolio Deep Dive (ppc-portfolio-summary — single portfolio mode)
**Result:** Success

**What happened:**
- User requested full deep dive for Fuse Beads portfolio with no details spared.
- Pulled all data sources in parallel: campaigns (14 ENABLED, 35 PAUSED), 35 keywords, 7 targets, 18 rank radar keywords, seller board, 278 search terms.
- Identified 3 RED issues (SK fuse beads bleeding, fuse beads rank #4→#10, perler beads bulk rank #20→#40) and 4 YELLOW issues.
- Built 9-item prioritized action plan. Portfolio scored 6/10.

**What didn't work:**
- API returns 200 ARCHIVED campaigns first when using state=ALL. Had to split into ENABLED + PAUSED calls.

**Lesson learned:**
- For deep dives, always split API calls by state (never ALL).
- Background agents for keyword/target pulls are efficient for multi-campaign portfolios.
- Fuse Beads has strong organic base (78% organic) — PPC is rank defense, not volume play.

**Tokens/cost:** ~65K tokens

### Run: 2026-03-02 (3)
**Task routed:** 4 Flowers Deep Dive + Phase 1 Emergency Stabilization
**Result:** Success

**What happened:**
- User asked for 4 Flowers portfolio brief → initial summary felt inaccurate → pivoted to full API-driven deep dive.
- Pulled all 39 campaigns (7 ENABLED, 32 PAUSED), all keywords, all targets, Seller Board daily data, DataDive rank radar.
- Discovered death spiral: ranks -209 net, 0 top-10 keywords, organic near-zero, Auto+Broad paused killing discovery.
- Built phased recovery plan. User approved Phase 1 only (no bid cuts yet).
- Applied: Re-enabled Auto ($5/day, bid $0.31), Re-enabled Broad ($5/day, bid $0.27), Increased SK bid $0.38→$0.43 for rank #11 defense.

**What didn't work:**
- Amazon Ads API 30-day campaign + search term reports stuck in PENDING (3 separate attempts, all stuck). Known issue.
- Weekly snapshot + Seller Board + rank radar were sufficient fallbacks.

**Lesson learned:**
- Summary-level portfolio data can miss critical details (paused Auto/Broad, multi-ASIN structure). Always pull campaign-level data for deep dives.
- Rank radar data is essential for portfolio diagnosis — rank decline was the #1 signal.
- User prefers phased execution, not everything at once. Ask/confirm scope before applying.
- User wants bid system improvements before doing bid cuts. Respect that boundary.

**Tokens/cost:** ~70K tokens (deep dive is expensive but justified for RED FLAG portfolios)

### Run: 2026-03-02 (2)
**Task routed:** Portfolio Performance Summary (ppc-portfolio-summary)
**Result:** Success

**What happened:**
- Routed "portfolio check" to ppc-portfolio-summary. First run of this sub-skill.
- Campaign report stuck in PENDING — fell back to 1-day-old weekly snapshot for performance data.
- Pulled live campaign list (152 ENABLED) for structure audit.
- Analyzed 18 active portfolios: 4 HEALTHY, 6 NEEDS ATTENTION, 6 RED FLAG, 2 LOW VOLUME.
- Key finding: 9 of 18 portfolios missing Broad campaigns (systemic gap).
- 0 new test campaigns this week (SOP violation).

**What didn't work:**
- Amazon Ads API campaign report stuck in PENDING >2 minutes. Not a server code issue — Amazon-side delay.

**Lesson learned:**
- Weekly snapshot is an excellent fallback for portfolio-level metrics (1-day staleness is acceptable).
- Campaign type classification by name pattern works well for structure audit.
- Should build a portfolio name mapping file to persist across runs.

**Tokens/cost:** ~35K tokens

### Run: 2026-03-02
**Task routed:** Daily PPC Health Check (ppc-daily-health)
**Result:** Success

**What happened:**
- Routed "daily health check" → ppc-daily-health. First run of this sub-skill.
- Read agent state, loaded context, fetched campaign + portfolio + rank radar data.
- Generated morning brief with 5 RED, 3 YELLOW, 10 GREEN portfolios.
- Populated pending_actions from weekly PPC analysis (8 items) + 2 new from health check.

**What didn't work:**
- Nothing major — clean first run.

**Lesson learned:**
- Weekly PPC summary is the best source for portfolio ACoS (actual spend, not budget caps).
- Should carry forward pending_actions from weekly analysis into agent-state.json automatically.

**Tokens/cost:** ~25K tokens

---

## Known Issues

### 1. RULE: Never pause a campaign based on a single week of zero conversions
**Impact:** HIGH — Premature pausing kills campaigns that may just be in a rough patch.
**Rule:** Always check a longer timeframe (minimum 30 days, ideally 60 days) before recommending a pause. Only recommend pausing if the campaign shows sustained poor performance over the longer timeframe. Enforce this across all sub-skills.

### 2. RULE: Never use round/organized bid amounts
**Impact:** MEDIUM — Predictable bid patterns reduce competitiveness in Amazon's auction dynamics.
**Rule:** When lowering or placing bids, never use clean percentages like -30%, -50%. Always use slightly irregular amounts like -31%, -48%, -52%, -27%. Enforce this across all sub-skills.

### 3. RULE: Never negate a search term based on a single week of zero conversions
**Impact:** HIGH — Premature negation kills search terms that may convert in other weeks.
**Rule:** Always check a minimum 30-day window of data before recommending a search term for negation. A search term with zero orders in one week might convert in other weeks. Only recommend negating if the search term shows sustained zero conversions AND is clearly irrelevant to the product over the full 30-day window. Enforce this across all sub-skills.

---

## Repeat Errors

*(Issues that have occurred 2+ times — MUST be surfaced to user)*

---

## Resolved Issues

*(Previously known issues that have been fixed)*
