# Bid Adjustment Recommender — Lessons Learned

## Run Log

*(New entries go at the TOP)*

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

## Known Issues

### 1. RULE: Never pause a campaign based on a single week of zero conversions
**Impact:** HIGH — Premature pausing kills campaigns that may just be in a rough patch.
**Rule:** Always check a longer timeframe (minimum 30 days, ideally 60 days) before recommending a pause. Only recommend pausing if the campaign shows sustained poor performance over the longer timeframe.

### 2. RULE: Never use round/organized bid amounts
**Impact:** MEDIUM — Predictable bid patterns reduce competitiveness in Amazon's auction dynamics.
**Rule:** When lowering or placing bids, never use clean percentages like -30%, -50%. Always use slightly irregular amounts like -31%, -48%, -52%, -27%.

### 4. Placement report missing `placementClassification` field
**Impact:** HIGH — Core skill capability (Step 4b Placement Health Classification) cannot function without per-placement ACoS data.
**First seen:** 2026-03-05
**Root cause:** The `sp_placements` report preset in the Amazon Ads MCP server may not include the placement type field. Alternatively, the `download_ads_report` tool may strip it during decompression/formatting.
**Workaround:** Infer placement health from campaign naming patterns (TOS campaigns = TOS-dominant by design). Less precise but functional.
**Fix needed:** Check `mcp-servers/amazon-ads-api/server.py` — ensure `sp_placements` report config includes `placementClassification` in the metrics list.

### 5. API modifier data can be stale within same day
**Impact:** MEDIUM — If another skill (e.g., portfolio action plan) changes TOS modifiers in a separate session, the `list_sp_campaigns` API call in this session returns pre-change values.
**First seen:** 2026-03-05 (Princess Lacing showed 262% when tracker said 148%)
**Rule:** Always cross-reference API TOS values with portfolio tracker `change_log` entries from today. Tracker is the source of truth.

### 3. RULE: Never negate a search term based on a single week of zero conversions
**Impact:** HIGH — Premature negation kills search terms that may convert in other weeks.
**Rule:** Always check a minimum 30-day window of data before recommending a search term for negation. A search term with zero orders in one week might convert in other weeks. Only recommend negating if the search term shows sustained zero conversions AND is clearly irrelevant to the product over the full 30-day window.

---

## Repeat Errors

*(Issues that have occurred 2+ times — MUST be surfaced to user)*

---

## Resolved Issues

*(Previously known issues that have been fixed)*
