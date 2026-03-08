# Search Term Harvester — Lessons Learned

## Run Log

*(New entries go at the TOP)*

### Run: 2026-03-05 (Full account harvest — first account-wide run)
**Result:** Success

**Terms analyzed:** 10,193 unique (13,503 raw rows, 30-day window)
**P1 negatives identified:** 46 raw → 13 safe after safety checks ($267 spend)
**P2 negatives identified:** 102 raw → 11 safe ($77 spend)
**Protected terms saved:** 22 terms ($662 spend) correctly removed from negate list
**Actual negatives applied:** 19 terms × 72 campaign-level entries, 0 errors
**Promote candidates:** 10 new terms without SK campaigns (top: "cross stitch kits for beginners" 35 orders/24% ACoS)
**Estimated monthly savings:** ~$82/month ($353/30d waste)

**What happened:**
- Requested fresh 14-day report but Amazon Ads API stuck PENDING >3 min (known issue). Fell back to existing 30-day report from Mar 3 — actually better for 30-day negation rule.
- Python classification script processed 13,503 rows, aggregated to 10,193 unique terms, mapped to portfolios via campaign list.
- Safety cross-reference was the hero: 22 protected terms ($662) would have been wrongly negated. Includes "embroidery for beginners" ($154), "lacing cards for kids ages 3-5" ($64), "toddler sewing kit" ($64).
- User approved all 13 P1, top 3 flagged + needlepoint pouch, and top 2 P2 (craft kits + 1 ASIN).
- Single API call applied all 72 campaign-level negatives with 0 errors.

**What didn't work:**
- Amazon Ads API 14-day search term report stuck PENDING for 3+ minutes. 6th occurrence of report generation delay.
- Some campaigns unmapped to portfolios (appear as "Unmapped" — likely PAUSED campaigns not in ENABLED campaign list).

**Lesson learned:**
- **30-day fallback data is actually superior for search term harvesting.** The 30-day rule means we need 30d data anyway — requesting 14d is suboptimal. Next run: request 30-day report directly, or reuse recent 30d data if <3 days old.
- **Python batch processing is essential at scale.** 13,503 rows cannot be analyzed inline. The classify_terms.py + safety_check.py pipeline works well.
- **Protected term safety net is critical.** 22 terms / $662 saved from false negation in a single run. Without it, we'd be negating our own target keywords.
- **Most waste is in Catch All Auto campaigns.** 10 of 13 P1 negates targeted catch-all auto campaigns. Consider a dedicated catch-all cleanup pass.
- **Campaign-level negatives batch well.** 72 entries in a single API call, 0 errors. No need to split into smaller batches under 100.

**Tokens/cost:** ~35K tokens, 0 fresh API reports (used cached 30d data)

**PROMOTE follow-up (same session):**
- Deep audit of all 8 promote candidates against existing campaign keywords (pulled keywords from 20 campaigns)
- **6 of 8 already fully covered** with EXACT match in existing SK/MK campaigns
- **2 gaps found and filled:**
  - "embroidery for kids" → added as EXACT ($0.39) to MK exact campaign 381587421028993
  - "cross stitch for kids 8-12" → new SK campaign created (270472026768698, $0.47, 86% TOS, $10/day)
- **1 reactivation:** SK campaign 309035836424147 renamed + enabled "cross stitch kits for beginners" at $0.36, TOS 13%, $7/day budget. Paused duplicate "cross stitch kits" keyword (covered elsewhere).
- **Lesson:** Always verify existing keyword coverage before creating new campaigns. 75% of promote candidates were already targeted — would have created redundant campaigns without checking.

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

### 1. Amazon Ads API report generation stuck PENDING (x6)
**Impact:** MEDIUM — Delays harvest start by 3+ minutes, sometimes 30-60 min.
**Workaround:** Fall back to cached 30-day data if <3 days old. Save report IDs and re-check later. Do NOT create duplicate reports.

---

## Resolved Issues

*(Previously known issues that have been fixed)*
