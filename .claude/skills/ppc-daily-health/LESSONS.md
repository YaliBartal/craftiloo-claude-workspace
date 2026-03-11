# Daily PPC Health Check — Lessons Learned

## Run Log

*(New entries go at the TOP)*

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

### Run: 2026-03-08
**Result:** Success

**What happened:**
- Fourth daily health check. 173 ENABLED campaigns (up from 156 on Mar 5 — Shield All re-enables + new campaigns).
- 3-day gap since last check (Mar 5).
- **Fairy Sewing +9 top-10 keywords** — biggest rank surge in account history. Listing push (Mar 6) + PPC deep dive (Mar 3) combined effect.
- Net +10 top-10 account-wide (222→232). Best 3-day performance since tracking started.
- 5 listing pushes verified live (4 from Mar 6 + Princess Lacing pushed today).
- Fairy Family upgraded YELLOW→GREEN. Latch Hook Pillow -2 concerning but PP/ROS only 3 days old.
- 6 GREEN, 7 YELLOW, 4 RED, 1 PAUSED portfolios.

**What didn't work:**
- Campaign API result was JSON code blocks (not markdown table) — needed regex parsing instead of table parsing.
- No fresh weekly or market intel data — account-level financials unavailable. Weekly analysis 7 days overdue.

**Lesson learned:**
- Listing push + PPC restructuring is a 1-2 punch that can produce dramatic rank gains within 2-5 days. Fairy Family is proof of concept.
- Campaign data from list_sp_campaigns is returned as individual JSON code blocks, not a markdown table. Use regex `json\n(.*?)\n` to extract.
- 3-day gaps are acceptable for health checks but miss the day-to-day volatility. Aim for daily when possible.

**Tokens/cost:** ~30K tokens, 0 API cost

### Run: 2026-03-05
**Result:** Success

**What happened:**
- Third daily health check run. 156 ENABLED campaigns (up 1 from 155 on Mar 3).
- DataDive rank radars: 15 active. Day-over-day comparison vs Mar 3 snapshot (2-day gap, not 1-day).
- 9 GREEN, 4 YELLOW, 4 RED, 1 PAUSED portfolios. Same RED portfolios as Mar 3.
- Key rank movements: Fairy Sewing **+3 top-10** (best gainer — deep dive changes working), Latch Hook Pillow +2 (recovering), Latch Hook Pencil +1 (recovering from -4 drop).
- Concerning drops: Cat & Hat -2, Bunny Knitting -2, Mini Fuse Beads -2 (post-restructuring).
- 4 Flowers listing verification was due Mar 4 — flagged as OVERDUE.
- 13 pending actions carried forward. Net top-10 rank movement: -3 (222 vs 225).

**What didn't work:**
- Market intel data is 4 days old (Mar 1). Account pulse has stale Seller Board data. Need fresh market intel run.
- No fresh weekly PPC data — still using Feb 20-26 window for ACoS figures.

**Lesson learned:**
- 2-day gap in daily health checks makes rank comparison less precise but still valuable.
- Fairy Family deep dive changes (Mar 3) showing clear positive impact after 2 days (+3 top-10). This validates the TOS rebalancing approach.
- Mini Fuse Beads -2 after restructuring (TOS 895%→350%, budget $100→$25) — expected short-term rank loss while the new equilibrium forms. Monitor for stabilization by Mar 9.
- Cat & Hat Knitting had first rank decline (-2) after being "fastest improver" — may be natural fluctuation or competitor response.

**Tokens/cost:** ~25K tokens, 0 API cost (no Apify, no reports)

---

### Run: 2026-03-03
**Result:** Success

**What happened:**
- Second daily health check run. No new market intel snapshot (used Mar 1 data, 2 days old).
- 155 ENABLED campaigns (down from 163 — reflects Dessert Family pause + other cleanup from yesterday).
- DataDive rank radars: 15 active. Day-over-day comparison now working vs Mar 2 snapshot.
- 9 GREEN, 4 YELLOW, 4 RED, 1 PAUSED portfolios.
- Key rank movements: Latch Hook Pencil Cases -4 top-10 (biggest drop), Princess Lacing -2 (continuing decline), Mini Fuse Beads +2 (restructuring impact), 10 Embroidery +2, Bunny +2.
- Dessert and 4 Flowers each gained 1 top-10 keyword (slight recovery from crisis).
- 12 pending actions carried forward (7 from weekly, 5 from portfolio summary / daily health).

**What didn't work:**
- Market intel data is 2 days old. Account pulse section has no new data to compare. Should suggest running /daily-market-intel.
- Campaign API gives budgets but not actual spend — weekly report ACoS figures are still the best source.

**Lesson learned:**
- Day-over-day rank comparison (vs yesterday's snapshot) adds significant value — Latch Hook Pencil Cases -4 drop would have been missed without it.
- Campaign data file output format uses JSON code blocks (```json), not markdown tables. Parser script needed for extraction.
- Clean up temp parser scripts after use.

**Tokens/cost:** ~30K tokens, 0 API cost (no Apify, no reports)

---

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
