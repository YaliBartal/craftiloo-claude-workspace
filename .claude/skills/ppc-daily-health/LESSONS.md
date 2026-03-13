# Daily PPC Health Check — Lessons Learned

## Run Log

*(New entries go at the TOP)*

### Run: 2026-03-13
**Result:** Success

**What happened:**
- 171 ENABLED campaigns — identical to Mar 12. Total daily budget $2,668.
- Net top-10 improved 190→195 (+5). Cat & Hat leading with +6 (14→20). BSR also improved -11,383.
- 4 Flowers crisis deepens: top-10 hit 0 (was 1). Crisis day 30. P1 audit 3d overdue.
- 5 listing re-audits due today (Fairy Family, Fuse Beads, CS Backpack Charms, LH Kits, Biggie Beads) — 7d from Mar 6 listing push.
- Needlepoint remains sole RED: 68.7% ACoS, 2 SK campaigns still AWAITING_ENABLE.
- QUEFE competitive threat flagged: dominating #1-2 on 'perler beads'.

**What didn't work:**
- Campaign API returned 82K chars again — saved to file, parsed with Python JSON block extraction. Budget field confirmed as flat float.

**Lesson learned:**
- When 5+ portfolios have listing re-audits due on the same day, surface this as a consolidated action item (not buried in individual portfolio rows).
- Cat & Hat BSR degradation from Mar 12 reversed in 1 day — avoid escalating single-day BSR spikes to RED. Flag as YELLOW + monitor.

**Tokens/cost:** ~28K tokens, 0 API cost

---

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
