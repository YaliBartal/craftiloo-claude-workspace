# Daily PPC Health Check — Lessons Learned

## Run Log

*(New entries go at the TOP)*

### Action: 2026-03-02 — Dessert Family Emergency Pause
**Result:** Success — All 4 campaigns PAUSED via API

**What happened:**
- User confirmed restock ETA ~2 weeks. Paused all 4 ENABLED Dessert Family campaigns.
- Campaigns paused: SK ages 8-12, SK beginner, SK sewing for kids, MK broad.
- Savings: ~$14/day ($96/week) in wasted spend on 5-unit inventory.
- Relaunch plan logged: re-enable 2 best campaigns at restock, keep 2 bleeding paused until negatives applied.

**Lesson learned:**
- When stock <10 units with no Buy Box, PPC is pure waste — pause immediately, don't debate.
- Log relaunch plan in agent-state so future sessions know what to do when stock arrives.

---

### Run: 2026-03-02
**Result:** Success

**What happened:**
- First-ever daily health check run. Loaded Mar 1 market intel + weekly PPC summary + live campaign data (163 campaigns) + DataDive rank radars (15 active).
- Successfully mapped 18 portfolios with traffic-light status: 10 GREEN, 3 YELLOW, 5 RED.
- Rank radar data aligned with yesterday's market intel — no discrepancies.
- Carried forward 8 P1 pending actions from weekly PPC analysis.

**What didn't work:**
- No market intel snapshot for today (Mar 2) — used yesterday's data. Brief notes this.
- Campaign data gives budgets, not actual spend. Used weekly report spend figures instead (more accurate).
- 4 portfolios missing from business.md stage definitions (Princess Lacing, Needlepoint, Punch Needle, Ballerina).

**Lesson learned:**
- Use weekly PPC summary for actual spend/sales/ACoS — campaign API only gives budget caps, not real spend.
- Rank radar `list_rank_radars` returns slightly different top10 counts than market intel snapshot (Cat & Hat 19 vs 18) — DataDive updates daily, use fresh call.
- First run has no day-over-day comparison. Future runs should compare against previous snapshot.

**Tokens/cost:** ~25K tokens, 0 API cost (no Apify, no reports)

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
