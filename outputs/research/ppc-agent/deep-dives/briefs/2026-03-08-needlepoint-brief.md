# Needlepoint — Portfolio Action Plan (Deep Dive #2)
**Date:** 2026-03-08
**Stage:** Scaling | **ACoS Target:** 30% | **Red Flag:** >45% | **Break-Even ACoS:** 23.7%
**Last Action Plan:** 2026-03-05 (3 days ago — 9/10 actions executed)

---

## Executive Summary

**Health Score: 3/10** (unchanged from Mar 5 deep dive)

The Mar 5 structural fixes (MK broad negatives, dead ASIN removal, 2 new campaigns) have not yet turned this portfolio around. The weekly data (Feb 27–Mar 5) shows **~68-72% ACoS** ($140 spend, $204 sales, 11 orders across 10 campaigns). The portfolio remains well above the 30% target. The root cause is clear: **CVR of 5.0% (target 10%) is a listing/product problem, not a PPC problem.** No amount of bid optimization can fix a product that converts at half the expected rate.

> **Correction:** An earlier version cited 92% weekly ACoS. That was a bad aggregation in the weekly summary — the raw campaign report data shows 68.7% ACoS for the same period. Corrected 2026-03-09.

**5 key findings:**
1. **TOS placement is the #1 waste source** — 4 of 7 campaigns have TOS ACoS >75%. Auto TOS is 258.9% ACoS. MK broad TOS is 76.8%.
2. **"Other on-Amazon" is the best placement** — consistently converting at 18-38% ACoS across campaigns.
3. **MK broad still dominates** at 51.5% of spend ($294/$571) despite Mar 5 negatives. "kids needlepoint" BROAD is the only profitable targeting (23.2% ACoS).
4. **SK campaigns are dead** — 0-3.3% budget utilization today despite adequate bids. Traffic isolation hasn't driven traffic to them.
5. **Rank collapsing on 5 beginner keywords** — lost 9-33 positions in 7 days. "needlepoint kits" (15.6K SV) crashed from rank 19 → 101 over 28 days.

---

## ASINs in This Portfolio

| ASIN | Product | Role | Status |
|------|---------|------|--------|
| B09HVDNFMR | Needlepoint Kit Cat | Hero | Active |
| B09HVSLBS6 | Needlepoint Kit Dog | Hero | Active |
| B09HVCCNM2 | Needlepoint Kit Hearts | Secondary | Active |
| B09HVDYMDK | Needlepoint Kit Mermaid | Dead | PAUSED in all campaigns (Mar 5) |

**SKU mapping:**
- B09HVDNFMR → N7-TUSA-2329 (Cat)
- B09HVSLBS6 → KM-QL7C-QZMZ (Dog)
- B09HVCCNM2 → KL-L7KN-R85L (Hearts)

---

## 30-Day Performance Overview

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Spend | $571.43 | — | — |
| Sales | $994.82 | — | — |
| ACoS | **57.4%** | 30% | RED |
| Orders | 51 | — | — |
| CVR | **5.0%** | 10% | RED |
| CPC | $0.56 | — | — |
| ROAS | 1.74 | 3.33 | RED |
| Break-Even ACoS | 23.7% | — | Spending 2.4x break-even |

**vs Baseline (Mar 5):** ACoS 57.4% vs 56.7% (+0.7pp). No improvement.
**vs Last 7 Days (Feb 27–Mar 5):** ACoS 68.7% — still worsening vs 30d average.

---

## Campaign-by-Campaign Breakdown (30d, ranked by spend)

| # | Campaign | Type | 30d Spend | 30d Sales | ACoS | Orders | CVR | CPC | TOS% | Budget | Util% | Status |
|---|----------|------|-----------|-----------|------|--------|-----|-----|------|--------|-------|--------|
| 1 | MK broad and phrase | MK | $294.04 | $562.38 | 52.3% | 30 | 7.2% | $0.71 | 78% | $7/d | 92% | ABOVE TARGET |
| 2 | SPA auto | Auto | $150.53 | $232.66 | 64.7% | 11 | 3.2% | $0.44 | 0% | $5/d | 106% | BLEEDING |
| 3 | SK beginners | SK | $52.68 | $89.90 | 58.6% | 4 | 3.1% | $0.41 | 50% | $15/d | 1.7% | ABOVE TARGET |
| 4 | SK kids needlepoint | SK | $36.59 | $53.94 | 67.8% | 3 | 4.9% | $0.60 | 207% | $8/d | 0% | BLEEDING |
| 5 | SK kit for kids | SK | $17.13 | $19.98 | 85.7% | 1 | 3.0% | $0.52 | 101% | $8/d | 0% | BLEEDING |
| 6 | PT product targeting | PT | $16.42 | $35.96 | 45.6% | 2 | 6.1% | $0.50 | 41% | $8/d | 38% | ABOVE TARGET |
| 7 | SK pouch kit | SK | $4.04 | $0.00 | — | 0 | 0% | $0.45 | 157% | $8/d | 3.3% | DORMANT |

---

## TOS Strategy Audit (30d Placement Data)

| Campaign | TOS Spend | TOS ACoS | Detail Page ACoS | Other ACoS | TOS % of Spend | Health |
|----------|-----------|----------|-------------------|------------|----------------|--------|
| MK broad | $207.12 | **76.8%** | 39.1% | **22.0%** | 70% | TOS_BLEEDING |
| Auto | $46.55 | **258.9%** | N/A (0 orders) | **38.0%** | 31% | TOS_BLEEDING |
| SK beginners | $11.28 | **31.4%** | N/A (0 orders) | **30.6%** | 21% | TOS_EFFICIENT |
| SK kids | $22.13 | **123.1%** | 62.2% | **18.2%** | 60% | TOS_BLEEDING |
| SK kit for kids | $9.36 | **46.8%** | N/A (0 orders) | N/A (0 orders) | 55% | INSUFFICIENT_DATA |
| PT | $6.99 | **19.4%** | N/A (0 orders) | N/A (0 orders) | 43% | TOS_EFFICIENT |
| SK pouch | $2.51 | N/A | N/A | N/A | 62% | INSUFFICIENT_DATA |

**Pattern:** "Other on-Amazon" is the best placement across the portfolio (18-38% ACoS). TOS is the primary waste source. Detail Page is also waste in most campaigns.

---

## Portfolio Structure Health Score

### Campaign Type Inventory

| Type | Required | Found | Status | 30d Spend | % of Portfolio |
|------|----------|-------|--------|-----------|----------------|
| Auto | 1 | 1 | OK | $150.53 | 26.3% |
| MK Broad | 1 | 1 | OK | $294.04 | 51.5% |
| SK (exact) | ~3+ | 4 | OK | $110.44 | 19.3% |
| PT | 1 | 1 | OK | $16.42 | 2.9% |
| Shield | N/A | 0 | N/A | — | — |
| Low-bid Discovery | 0 | 0 | N/A | — | — |

### Spend Distribution Assessment

| Metric | Value | Benchmark | Status |
|--------|-------|-----------|--------|
| MK Broad % of total spend | **51.5%** | <30% ideal | CRITICAL |
| Auto % of total spend | **26.3%** | <20% ideal | WARNING |
| SK % of total spend | **19.3%** | >40% ideal | CRITICAL |
| Top 1 campaign % of spend | **51.5%** | <35% ideal | CRITICAL |

**Structure Health Grade: 4/10** — MK broad still dominates despite Mar 5 negatives. SK campaigns aren't capturing traffic.

---

## MK Broad Cannibalization Audit

| Metric | Value |
|--------|-------|
| MK Broad 30d Spend | $294.04 |
| MK Broad % of Portfolio | 51.5% |
| MK Broad ACoS | 52.3% |
| MK Broad Orders | 30 |

### MK Broad Keywords (current state)

| Keyword | Match | Bid | 30d Spend | 30d Sales | Orders | ACoS | CVR | Status |
|---------|-------|-----|-----------|-----------|--------|------|-----|--------|
| kids needlepoint | BROAD | $0.52 | $59.68 | $256.72 | 13 | **23.2%** | **20.0%** | STAR |
| needlepoint kit | BROAD | $0.33 | $166.02 | $251.72 | 14 | 66.0% | 5.5% | ABOVE TARGET |
| needlepoint kit for kids | BROAD | $0.51 | $16.02 | $17.98 | 1 | 89.1% | 5.6% | BLEEDING |
| needlepoint kits | BROAD | $0.33 | $52.32 | $35.96 | 2 | **145.5%** | 2.6% | BLEEDING |

**Mar 5 negatives status:** 6 NEGATIVE_EXACT added for SK isolation (kids needlepoint kit, needlepoint kit for kids, needlepoint kits for kids, needlepoint kits for beginners, stitch and zip needlepoint kits, beginner punch needle kit for kids). All confirmed active.

**Pending negation NOT YET EXECUTED:** "needlepoint pouch kit" (np-001 from Mar 5) — MK broad is still capturing this term ($10.53 spend, 2 orders, 29.3% ACoS) instead of the SK pouch kit campaign.

---

## Rank Radar Analysis (28d)

| # | Keyword | SV | Rank Now | 7d Ago | 28d Ago | Trend |
|---|---------|---:|--------:|-------:|--------:|-------|
| 1 | needlepoint kit | 24,095 | **29** | 27 | 25 | STABLE |
| 2 | **needlepoint kits** | **15,617** | **101** | 101 | **19** | **LOST** |
| 3 | needlepoint kits for beginners | 6,461 | 61 | 101 | 78 | OSCILLATING |
| 4 | needlepoint cards | 2,669 | 32 | 13 | 53 | CRITICAL (-19) |
| 5 | needlepoint for beginners | 2,258 | 101 | 90 | 101 | CRITICAL (-11) |
| 6 | needlepoint beginner kit | 1,927 | 78 | 69 | 86 | CRITICAL (-9) |
| 7 | needlepoint starter kit | 1,848 | 87 | 65 | 51 | CRITICAL (-22) |
| 8 | beginner needlepoint kit | 1,643 | 101 | 68 | 81 | CRITICAL (-33) |
| 9 | kids needlepoint kit | 948 | **12** | 13 | 14 | STABLE |
| 10 | needlepoint for kids | 897 | **11** | 9 | 18 | STABLE |
| 11 | bargello needlepoint kits | 1,002 | **16** | 21 | 27 | IMPROVING |

**Summary:** 50 keywords tracked, only 15 ranked. Kids keywords (rank 11-12) are the strongest. "needlepoint kits" (15.6K SV) is the biggest loss — completely fell off over 28 days. 5 beginner-related keywords are CRITICAL.

---

## Search Term Analysis (30d)

### Top Converters

| Search Term | Campaign | Clicks | Orders | ACoS | CVR |
|-------------|----------|--------|--------|------|-----|
| needlepoint kits for kids | MK broad | 8 | 4 | **11.9%** | 50.0% |
| embroidery for kids | MK broad | 1 | 3 | **1.0%** | — |
| needlepoint kits for beginners | SK beginners | 113 | 3 | 63.1% | 2.7% |
| kids needlepoint kit | SK kids | 56 | 3 | 60.7% | 5.4% |
| needlepoint pouch kit | MK broad | 20 | 2 | **29.3%** | 10.0% |
| needlepoint kits for kids | Auto | 5 | 2 | **6.1%** | 40.0% |
| needlepoint kit for kids | Auto | 2 | 2 | **3.5%** | 100% |
| b0d944gmkk (ASIN) | PT | 20 | 1 | 55.7% | 5.0% |

### Top Waste (30d, 0 orders)

| Search Term | Campaign | Clicks | Spend | Issue |
|-------------|----------|--------|-------|-------|
| needlepoint kit (phrase) | MK broad | 17 | $14.63 | Broad term, low intent |
| needlepoint kits (phrase) | MK broad | 14 | $11.71 | Plural variant, low CVR |
| needlepoint | Auto | 23 | $11.58 | Too broad |
| needlepoint kits for beginners | MK broad | 7 | $9.46 | Already isolated to SK |
| needlepoint kits for adults | Auto | 22 | $8.99 | Wrong audience |
| stitch and zip needlepoint kits | MK broad | 9 | $6.12 | Competitor brand |

---

## Structural Issues Summary

1. **CVR is 5.0% (target 10%)** — This is the root cause. Every campaign underperforms because the product doesn't convert. PPC optimization has diminishing returns until the listing/product is improved.

2. **TOS placement waste** — TOS consumes 40-70% of spend in most campaigns but converts at 75-259% ACoS. "Other on-Amazon" consistently converts 2-4x better.

3. **MK broad still 51.5% of spend** — Despite Mar 5 negatives, MK broad dominates because SK campaigns aren't capturing traffic (0-3.3% utilization).

4. **"needlepoint pouch kit" not cross-negated** (np-001 pending) — MK broad still captures this term, starving the SK pouch kit campaign.

5. **"needlepoint kits" rank collapse (19→101)** — Major keyword lost entirely. Related to reduced TOS spend and/or declining product relevance signals.

6. **5 beginner keywords in CRITICAL decline** — Lost 9-33 positions in 7 days. The bid cuts on Mar 5 may have accelerated this by reducing TOS visibility.

---

## Action Plan — 10 Items (Impact-Ranked)

### P1 — Critical (3 items, est. ~$60/month waste reduction)

| # | Score | Category | Action | Campaign | Current | Proposed |
|---|-------|----------|--------|----------|---------|----------|
| 1 | 82 | BID_DECREASE | Lower TOS modifier | MK broad | TOS 78% | TOS 33% |
| 2 | 73 | BID_DECREASE | Lower "needlepoint kits" BROAD bid | MK broad | $0.33 | $0.21 |
| 3 | 70 | NEGATE_SEARCH_TERM | Cross-negate "needlepoint pouch kit" in MK broad + Auto | MK broad + Auto | Not negated | NEGATIVE_EXACT |

**Item 1: MK Broad TOS 78% → 33%**
- **What:** Lower TOS modifier to shift spend away from expensive TOS placement toward efficient Other on-Amazon
- **Why:** TOS placement drives 70% of MK broad spend ($207/$294) at 76.8% ACoS. Other on-Amazon converts at 22.0% ACoS — 3.5x more efficient. Detail Page at 39.1% is also better.
- **30d Data:** $294.04 spend, $562.38 sales, 30 orders, 52.3% ACoS, 7.2% CVR
- **Before → After:** TOS 78% → 33%. Effective TOS bids: "kids needlepoint" $0.93→$0.69, "needlepoint kit" $0.59→$0.44
- **Expected impact:** ~$40-50/month waste reduction from TOS. Non-TOS placements maintain.
- **Risk:** May lose some TOS impressions on "needlepoint kit" (rank 29). But with 5% CVR, TOS visibility isn't converting to rank gains anyway.

**Item 2: "needlepoint kits" BROAD bid $0.33 → $0.21**
- **What:** Reduce bid on the worst-performing BROAD keyword in MK broad
- **Why:** 145.5% ACoS, $52.32 spend, only 2 orders in 30d. Matching to adult-oriented terms ("needlepoint kits for adults" 65%, "half stitch needlepoint kits" 64%). The "needlepoint kits for beginners" variant is already handled by the SK campaign.
- **30d Data:** $52.32 spend, $35.96 sales, 2 orders, 145.5% ACoS, 2.6% CVR
- **Before → After:** Bid $0.33 → $0.21 (-36%). Effective TOS: $0.59→$0.28
- **Expected impact:** ~$15-20/month waste reduction
- **Not pausing:** Has 2 orders/30d — consistent with "never pause based on single week" rule.

**Item 3: Cross-negate "needlepoint pouch kit" in MK broad + Auto**
- **What:** Execute pending action np-001 from Mar 5 — isolate traffic to SK pouch kit campaign
- **Why:** MK broad's "needlepoint kit" BROAD matches "needlepoint pouch kit" searches, stealing traffic from the dedicated SK campaign (3.3% utilization). In MK broad, "needlepoint pouch kit" converted at 29.3% ACoS (2 orders) — these should flow to SK instead.
- **30d Data:** MK broad captured $10.53 spend, $35.96 sales, 2 orders from "needlepoint pouch kit"
- **Before → After:** Add NEGATIVE_EXACT "needlepoint pouch kit" to MK broad + Auto
- **Expected impact:** Redirects ~$10/month traffic to SK pouch kit

### P2 — Optimization (4 items, est. ~$30/month impact)

| # | Score | Category | Action | Campaign | Current | Proposed |
|---|-------|----------|--------|----------|---------|----------|
| 4 | 62 | BID_DECREASE | Lower TOS modifier | SK kids needlepoint | TOS 207% | TOS 107% |
| 5 | 58 | NEGATE_SEARCH_TERM | Negate "needlepoint kits for adults" in Auto | Auto | Not negated | NEGATIVE_EXACT |
| 6 | 52 | BID_DECREASE | Remove ROS modifier on PT | PT | ROS 10% | ROS 0% |
| 7 | 48 | BID_DECREASE | Lower "needlepoint kit for kids" BROAD bid | MK broad | $0.51 | $0.37 |

**Item 4: SK kids needlepoint TOS 207% → 107%**
- **What:** Halve the TOS modifier — TOS is massively overpaying
- **Why:** TOS placement: $22.13 spend, 1 order, 123.1% ACoS. Other on-Amazon: $3.27, 1 order, 18.2% ACoS (excellent). Current effective TOS bid = $0.35 × 3.07 = $1.07. Proposed = $0.35 × 2.07 = $0.72.
- **30d Data:** $36.59 spend, $53.94 sales, 3 orders, 67.8% ACoS, 4.9% CVR
- **PP/ROS modifiers:** PP 33%, ROS 36% — keep these (Other on-Amazon is working)
- **Expected impact:** ~$8/month TOS waste reduction

**Item 5: Negate "needlepoint kits for adults" in Auto**
- **What:** Block adult-intent term from kids product Auto campaign
- **Why:** 22 clicks, $8.99 spend, 0 orders over 30d. "needlepoint for adults" EXACT is already negated but "needlepoint kits for adults" (different phrasing) leaks through.
- **Before → After:** Add NEGATIVE_EXACT "needlepoint kits for adults" to Auto
- **Expected impact:** ~$9/month waste elimination

**Item 6: PT Remove ROS 10% → 0%**
- **What:** Remove Rest of Search modifier on product targeting campaign
- **Why:** TOS is the only converting placement (19.4% ACoS, 2 orders). Other on-Amazon spent $9.11 with 0 orders. ROS modifier amplifies non-TOS waste.
- **30d Data:** $16.42 spend, $35.96 sales, 2 orders, 45.6% ACoS
- **Before → After:** Keep TOS 41%, PP 10%. Remove ROS 10% → 0%
- **Expected impact:** ~$3-4/month waste reduction

**Item 7: "needlepoint kit for kids" BROAD bid $0.51 → $0.37**
- **What:** Lower bid on MK broad keyword with 89.1% ACoS
- **Why:** 1 order from $16.02 spend in 30d. The EXACT term is negated (SK has it), so BROAD only catches variants. 5.6% CVR on variants = not profitable.
- **Before → After:** Bid $0.51 → $0.37 (-27%)
- **Expected impact:** ~$4/month waste reduction

### P3 — Maintenance (1 item)

| # | Score | Category | Action | When |
|---|-------|----------|--------|------|
| 8 | 35 | CAMPAIGN_SEED | Seed proactive negatives on SK pouch + PT campaigns | Next run |

### P4 — Monitor Only (2 items)

- **Rank collapse on "needlepoint kits" (15.6K SV)** — crashed 19→101 in 28 days. Cannot be recovered via PPC alone with 5% CVR. Monitor whether listing improvements reverse this. Re-evaluate in 14 days.
- **5 beginner keywords CRITICAL** — all lost 9-33 positions in 7 days. These keywords target adult beginners — our product is for kids. The rank loss may actually be Amazon correctly re-classifying us. Monitor but don't chase with PPC spend.

### LISTING AUDIT — CRITICAL RECOMMENDATION

**This portfolio cannot be fixed with PPC optimization alone.**

| Signal | Value | Why It Matters |
|--------|-------|----------------|
| CVR | 5.0% | Half of 10% target — product doesn't convert |
| Break-even ACoS | 23.7% | Portfolio at 57.4% = spending 2.4x break-even |
| Mar 5 fixes | ACoS worsened 56.8%→68.7% | Structural PPC fixes haven't turned it around yet |
| Rank collapse | "needlepoint kits" 19→101 | Amazon losing confidence in product relevance |
| 35/50 keywords unranked | 70% no organic visibility | Product isn't registering for most keywords |

**Recommendation:** Run the listing-optimizer skill on B09HVDNFMR (Cat) and B09HVSLBS6 (Dog). Focus areas:
1. **Title** — Does it clearly communicate "kids needlepoint kit"? Or is it too generic?
2. **Images** — Do they show the product in use by kids? Are they competitive?
3. **Bullets** — Do they address buyer concerns (grandparent/parent buying for kids)?
4. **Reviews** — How many? What rating? Any common complaints?
5. **Price** — Is it competitive vs KRAFUN/Louise Maelys?
6. **Product-market fit** — Is "needlepoint kit for kids" a viable niche or is this product struggling because kids don't want needlepoint?

---

## Files Saved
- Brief: `outputs/research/ppc-agent/deep-dives/briefs/2026-03-08-needlepoint-brief.md`
- Placement data: `outputs/research/ppc-agent/deep-dives/snapshots/2026-03-08-needlepoint-placements-30d.json`
