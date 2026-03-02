# PPC Agent — Lessons Learned

## Run Log

*(New entries go at the TOP)*

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
