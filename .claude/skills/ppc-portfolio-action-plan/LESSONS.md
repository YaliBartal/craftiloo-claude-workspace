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

### 1. Campaign-level negative keywords: PAUSED not ARCHIVED
**Impact:** HIGH — Using ARCHIVED state causes 400 error from Amazon Ads API.
**Workaround:** Use `"state": "PAUSED"` for campaign-level negatives. Only ad-group level negatives support ARCHIVED.
**Valid states:** ENABLED, PROPOSED, PAUSED.

---

## Repeat Errors

### 1. Amazon Ads API reports stuck in PENDING (x3)
**Impact:** MEDIUM — Fresh data unavailable during initial analysis; must fall back to weekly snapshot files.
**Occurrences:** Catch-All Auto run (2026-03-03), Fairy Family run (2026-03-03), Cross & Embroidery run (2026-03-03→05).
**Workaround:** Use existing data from `outputs/research/ppc-weekly/data/search-terms-*` as fallback. Reports may resolve after ~1 hour — worth re-checking old report IDs rather than creating new ones.
**Root cause:** Amazon-side delay. Not a code/auth issue.

---

## Resolved Issues

_None yet._
