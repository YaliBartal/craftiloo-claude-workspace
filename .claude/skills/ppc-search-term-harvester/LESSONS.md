# Search Term Harvester — Lessons Learned

## Run Log

*(New entries go at the TOP)*

### Run: 2026-03-02 (Dessert Family — targeted harvest while paused)
**Result:** Success

**Terms analyzed:** 46 (Dessert portfolio only, 30-day window)
**P1 negatives identified:** 3 ($75.82 spend) — BUT 3/3 were protected sewing terms. Removed from negate list.
**Actual negatives applied:** 4 (hygiene terms: "no sew kits for kids", "sewing machine", competitor brand, "felt crafts")
**Promote candidates:** 0
**Bids lowered:** 2 keywords — SK ages 8-12 ($0.74→$0.61, -17.6%), SK beginner ($0.92→$0.73, -20.7%)
**Estimated weekly savings:** Minimal from negatives ($2.80/wk). Real savings from bid reduction (~$3-4/wk at relaunch).

**What happened:**
- Pulled 30-day search term report (13,715 total, filtered to 46 Dessert terms).
- Key finding: 37/46 terms (80%) are protected sewing keywords. Problem was stock collapse, not bad keywords.
- Applied 4 hygiene negatives to MK broad campaign. Lowered bids on 2 keeper campaigns with irregular amounts per rules.
- All 4 campaigns remain PAUSED. Changes prep for restock relaunch in ~2 weeks.

**What didn't work:**
- Initial classification flagged protected terms as P1 negates. Safety cross-reference caught this correctly.

**Lesson learned:**
- When a portfolio's ACoS is terrible but search terms are all legitimate/protected, the root cause is likely external (stock, Buy Box, listing issue) — not keyword selection. Don't negate good keywords just because the product can't convert.
- Always run protected term check BEFORE presenting negate list to user.

**Tokens/cost:** ~40K tokens, 1 Ads API report

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
