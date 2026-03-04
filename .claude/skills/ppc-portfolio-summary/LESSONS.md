# Portfolio Performance Summary — Lessons Learned

## Run Log

*(New entries go at the TOP)*

### Run: 2026-03-02 (Deep Dive — Fuse Beads)
**Result:** Success

**Portfolio:** Fuse Beads (195178133158684)
**Campaigns analyzed:** 14 ENABLED, 35 PAUSED
**Keywords:** 35 enabled across 10 campaigns
**Search terms:** 278 (7d)
**Rank keywords:** 18 tracked

**What happened:**
- Full deep dive on Fuse Beads per user request. Pulled campaign list, all keywords, all targets, rank radar, seller board, search terms.
- Used background agents to pull keywords (14 campaigns) and targets (3 PT campaigns) in parallel — efficient.
- Identified 3 critical issues: SK fuse beads bleeding (119.5% ACoS), "fuse beads" rank dropped #4→#10, "perler beads bulk" rank collapsed #20→#40.
- Built full action plan with 9 prioritized items.

**What didn't work:**
- 14-day search term report didn't have campaignId field for filtering (different JSON schema than 7d). Used 7d only.
- Campaign list for ALL state returned 200 ARCHIVED first (API paginates by state). Had to make 2 separate calls for ENABLED and PAUSED.

**Lesson learned:**
- For portfolio deep dives, always call ENABLED and PAUSED separately — never ALL (200 ARCHIVED campaigns clog the response).
- Background agents for keyword/target pulls work well — saves time vs sequential calls.
- 7-day search term data is sufficient for pattern identification; 30-day needed only for negation decisions.
- Portfolio with strong organic (78% organic ratio) needs PPC focused on rank defense, not volume generation.

**Tokens/cost:** ~65K tokens (deep dive justified for top-spend portfolio)

### Run: 2026-03-02
**Result:** Success

**Portfolios analyzed:** 18
**Red flags:** 6 (Princess Lacing, 4 Flowers, Embroidery for Kids, Needlepoint, Bunny Knitting, Dessert Family)
**Structural gaps:** 11 portfolios missing required types (9 missing Broad — systemic gap)
**Dormant campaigns:** ~31 LOW BID across 5 portfolios
**New campaigns this week:** 0 (SOP violation flagged)

**What happened:**
- First run of this skill. Campaign report stuck in PENDING >2min — used 1-day-old weekly snapshot for metrics (per error handling protocol).
- Live campaign list (152 ENABLED) pulled successfully for structure audit.
- Classified all 152 campaigns by type using name pattern matching.
- Identified systemic Broad campaign gap across account.

**What didn't work:**
- `create_ads_report(sp_campaigns, LAST_7_DAYS)` stuck in PENDING indefinitely. Amazon API issue — not server-side.
- Some portfolio name mismatches between weekly snapshot display names and API portfolio names (e.g., "Cross Stitch Hero" vs "Cross stitch backpack charms").
- Bunny Knitting shows 0 ENABLED campaigns in portfolio but weekly snapshot shows $56 spend — campaigns may be assigned to wrong portfolio ID or unassigned.

**Lesson learned:**
- Always have fallback to weekly snapshot data when campaign reports are slow.
- Build a persistent portfolio name mapping (API name -> display name) to avoid mismatches.
- Campaign type classification by name works ~90% but "TOS" campaigns without SK/MK prefix are ambiguous — defaulted to SK.
- The Broad campaign gap is the #1 structural finding — worth making this a standard check.

**Tokens/cost:** ~35K tokens

---

## Known Issues

### 1. RULE: Never pause a campaign based on a single week of zero conversions
**Impact:** HIGH — Premature pausing kills campaigns that may just be in a rough patch.
**Rule:** Always check a longer timeframe (minimum 30 days, ideally 60 days) before recommending a pause. Only recommend pausing if the campaign shows sustained poor performance over the longer timeframe.

### 2. RULE: Never use round/organized bid amounts
**Impact:** MEDIUM — Predictable bid patterns reduce competitiveness in Amazon's auction dynamics.
**Rule:** When lowering or placing bids, never use clean percentages like -30%, -50%. Always use slightly irregular amounts like -31%, -48%, -52%, -27%.

### 5. RULE: Never negate a search term based on a single week of zero conversions
**Impact:** HIGH — Premature negation kills search terms that may convert in other weeks.
**Rule:** Always check a minimum 30-day window of data before recommending a search term for negation. A search term with zero orders in one week might convert in other weeks. Only recommend negating if the search term shows sustained zero conversions AND is clearly irrelevant to the product over the full 30-day window.

### 3. Campaign report can get stuck in PENDING
**Impact:** MEDIUM — Blocks fresh data pull but fallback exists.
**Workaround:** After 2 minutes, fall back to most recent weekly snapshot data. Note the staleness in the report header.

### 4. Systemic Broad campaign gap
**Impact:** HIGH — 9 of 18 portfolios missing Broad campaigns. Limits keyword discovery and harvesting.
**Action:** Flag this every run until resolved. Consider creating a batch Broad campaign creation task.

---

## Repeat Errors

*(Issues that have occurred 2+ times — MUST be surfaced to user)*

---

## Resolved Issues

*(Previously known issues that have been fixed)*
