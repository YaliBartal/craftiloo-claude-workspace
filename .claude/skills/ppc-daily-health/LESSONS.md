# Daily PPC Health Check — Lessons Learned

## Run Log

*(New entries go at the TOP)*

### Run: 2026-03-12
**Result:** Success

**What happened:**
- 171 ENABLED campaigns — identical to Mar 11. Total daily budget $2,650.
- CS Backpack Charms STOCK RESOLVED: B08DDJCQKF 73→2059 units. BSR 4677, #2 in subcategory. Downgraded RED→GREEN.
- Net top-10: 190 (−1 vs 191 yesterday). Only Cat & Hat -1 (crochet loom + knitting kits both dropped to rank 101, BSR +7,325 in 3 days).
- Needlepoint remains sole RED: 68.7% ACoS, 2 SK campaigns PAUSED since Mar 10 awaiting enable.
- BIG review day: 9 portfolios with 7-day reviews due today (Shield All P1 gate + 8 others).

**What didn't work:**
- Nothing — clean run. Market intel snapshot existed for today.

**Lesson learned:**
- Big review days (9 portfolios due same day) should be surfaced prominently. Recommend leading with count in Today's Recommendation.
- Cat & Hat BSR degradation pattern: BSR spike + two hero keywords dropping to rank 101 simultaneously is a signal to escalate to portfolio action plan immediately.

**Tokens/cost:** ~22K tokens, 0 API cost

---

### Run: 2026-03-11 (Refresh)
**Result:** Success

**What happened:**
- Second run today (refresh). 171 ENABLED campaigns — identical to morning run.
- DataDive rank radars flat (updates once/day): net top10 = 191, unchanged.
- Corrected 4 Flowers status: agent-state.json had duplicate key — first entry was stale RED, second entry (Mar 10 deep dive) was correct YELLOW. Fixed duplicate key, kept YELLOW.
- RED flags: 2 (CS Backpack Charms stock crisis + Needlepoint high ACoS / PAUSED campaigns). Down from 3 in morning run after 4 Flowers correction.
- 9 portfolios have 7-day reviews due TOMORROW (Mar 12) — big review day coming.

**What didn't work:**
- File write error on health-check.md (hadn't read it first) — used Edit instead after reading.

**Lesson learned:**
- If health check is re-run same day, DataDive rank radars will be identical (once-per-day update). Note this in the brief and skip surfacing false "flat" comparisons as significant news.
- Duplicate keys in agent-state.json JSON are silently handled by Python (last key wins) but can cause confusion in editors. Always fix on discovery.

**Tokens/cost:** ~20K tokens, 0 API cost

---

### Run: 2026-03-11
**Result:** Success

**What happened:**
- Fifth daily health check. 171 ENABLED campaigns (down from 173 on Mar 10 — 2 Needlepoint SK campaigns still PAUSED, not reflected in live count).
- 3-day gap since last check (Mar 8). Last daily_health run was Mar 10 (but Mar 10 was run from cached data — Ads API was unavailable then). Today: Ads API working, DataDive working.
- Live DataDive rank radars returned all 15 radars with fresh Mar 11 data.
- Net account-wide: -4 top-10 (195→191). Natural giveback after +10 on Mar 8.
- **Princess Lacing +6** (6→12) — listing push from Mar 8 confirmed working. Fastest 3-day rank response on record.
- **Fairy Sewing -5** (37→32) — pullback from record high. Natural post-listing volatility.
- **Cat & Hat -4** (19→15) — notable decline; ACoS also rising. Monitor.
- 4 GREEN, 10 YELLOW (including Punch Needle), 3 RED, 1 PAUSED.
- No market intel snapshot for Mar 10 or Mar 11 — running on Mar 9 data.

**What didn't work:**
- Campaign API returned 82K chars — had to save to file and parse with Python. Used Python heredoc via Bash (not built-in tools).
- Budget field in campaigns API is a scalar float (`"budget": 18.0`), not nested object. Previous parse attempt used `.get('budget', {}).get('budget', 0)` which failed.
- Mar 10 health snapshot was flagged as run successfully but the Ads API had been unavailable — that data was from cached weekly PPC. Today's run is the first with live Ads API data since Mar 8.

**Lesson learned:**
- Campaign `budget` field is a flat float in the API response, NOT a nested `{budget: X}` object. Use `c.get('budget', 0)` directly.
- When comparing rank radar counts day-over-day, always note whether the previous day had "assumed flat" values — these inflate apparent drops. Mar 10 snapshot had several "assumed flat" entries that made today's -4 look slightly worse than it is.
- Princess Lacing +6 in 3 days from listing push = fastest response seen. This validates the listing → PPC flywheel approach.
- Always check agent-state.json for `last_daily_health` duplicate keys — found two on Mar 10 (JSON duplicate key issue). Fixed during this run.

**Tokens/cost:** ~35K tokens, 0 API cost (no Apify, no reports)

---

## Known Issues

### 1. RULE: Never pause a campaign based on a single week of zero conversions
**Impact:** HIGH — Premature pausing kills campaigns that may just be in a rough patch.
**Rule:** Always check a longer timeframe (minimum 30 days, ideally 60 days) before recommending a pause. Only recommend pausing if the campaign shows sustained poor performance over the longer timeframe.

### 2. RULE: Never use round/organized bid amounts
**Impact:** MEDIUM — Predictable bid patterns reduce competitiveness in Amazon's auction dynamics.
**Rule:** When lowering or placing bids, never use clean percentages like -30%, -50%. Always use slightly irregular amounts like -31%, -48%, -52%, -27%.

### 3. RULE: Never negate a search term based on a single week of zero conversions
**Impact:** HIGH — Premature negation kills search terms that may convert in other weeks.
**Rule:** Always check a minimum 30-day window of data before recommending a search term for negation. A search term with zero orders in one week might convert in other weeks. Only recommend negating if the search term shows sustained zero conversions AND is clearly irrelevant to the product over the full 30-day window.

---

## Repeat Errors

*(Issues that have occurred 2+ times — MUST be surfaced to user)*

---

## Resolved Issues

*(Previously known issues that have been fixed)*
