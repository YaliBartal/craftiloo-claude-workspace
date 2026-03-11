# PPC Portfolio Action Plan — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`, `context/ppc-rules.md`, `context/tooling-workarounds.md`
> Run log archive → `outputs/research/ppc-agent/run-logs/`

## Skill-Specific Lessons

1. Always present per-campaign 30d metrics + per-placement breakdowns (TOS/ROS/PP spend, ACoS, orders) before asking for user approval
2. Check for existing PAUSED campaigns before creating new ones — Amazon rejects duplicate names
3. When reports are PENDING, extract portfolio data from account-wide cached search term reports by filtering on campaign IDs
4. Cross-session deep dives work: data collection (session 1) + execution (session 2). All data files persist
5. For product ad creation, get SKU from SP-API listings report (`GET_MERCHANT_LISTINGS_ALL_DATA`), not inventory endpoint (which aggregates)
6. Search term field names vary by report: `sales7d` vs `sales14d` — check actual field names in data
7. Campaign creator works end-to-end in 4 sequential API calls: campaign → ad group → product ad (with SKU) → keyword (~30 seconds)
8. SK campaigns need bid higher than MK broad effective bid to capture traffic: `SK_bid × (1 + TOS%) > MK_broad_bid × (1 + MK_TOS%)`
9. Variant economics drive strategy — don't blanket-optimize portfolios with mixed-margin variants (e.g., Owl 26.9% margin vs Hero 2.1%)
10. "Embroidery" ≠ "cross stitch" in shopper intent, even when product includes both elements
11. Keyword identity drift is measurable via rank radar — if "sewing" terms improving while "lacing" terms declining, PPC is teaching Amazon the wrong association
12. When user modifies recommended actions, follow user intent exactly — don't revert to original recommendation

## Known Issues

### 1. Never scope portfolios by campaign name patterns
**Impact:** CRITICAL — Name-based filtering matches campaigns across multiple portfolios. Caused entire wrong-portfolio analysis (caught by user).
**Rule:** Always use `portfolioId` field. Query `list_sp_campaigns` with `portfolio_id` parameter.

### 2. Campaign-level negative keywords: PAUSED not ARCHIVED
Valid states: ENABLED, PROPOSED, PAUSED. ARCHIVED → HTTP 400.

### 3. Weekly summary portfolio aggregation can produce wrong ACoS
Needlepoint showed 92% in summary vs 68.7% raw data (23pp gap). Always cross-validate by summing campaign-level data from raw report.

### 4. Campaign archiving is UI-only
`update_sp_campaigns` doesn't support ARCHIVED state. Flag as Seller Central action in plans.

## Repeat Errors

### 1. Amazon Ads reports stuck PENDING (x7+)
**Workaround:** See `context/tooling-workarounds.md`

### 2. SP v3 API SCREAMING_SNAKE_CASE format errors (x2)
**Rule:** See `context/api-patterns.md` — Amazon Ads API section

## Resolved Issues

_None yet._

## Recent Runs (last 3)

### Run: 2026-03-09 — Needlepoint (Deep Dive #2)
**Result:** Success (7/7 actions, 0 errors)
**Key outcome:** 30d ACoS 57.4%, CVR 5% = listing/product problem, not PPC. Root cause: wrong ACoS in weekly summary (92% vs actual 68.7%). User modified cross-negation → boost SK instead.
**New lessons:** #3 (weekly aggregation bug), user preference on converting terms (→ ppc-rules.md #10)

### Run: 2026-03-05 — Needlepoint (Deep Dive #1)
**Result:** Success (9/10 actions, 1 failed: archive not supported via API)
**Key outcome:** Root cause = MK broad cannibalization at 54% spend. Dead ASIN B09HVDYMDK still advertised. 2 new campaigns created.

### Run: 2026-03-05 — Latch Hook Kits
**Result:** Success (8 actions executed)
**Key outcome:** Rank collapse on "latch hook kit" (#45→>100) from paused campaign. Detail Page placement 19.6% ACoS but only 6% spend. 2 new campaigns created.
