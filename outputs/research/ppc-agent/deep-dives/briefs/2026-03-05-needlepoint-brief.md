# Needlepoint — Portfolio Action Plan
**Date:** 2026-03-05
**Stage:** Scaling | **ACoS Target:** 30% | **Red Flag:** >50%
**Last Action Plan:** First run
**Bid Recommender Changes Today:** Auto TOS 55%→0%, MK broad TOS 131%→78%

---

## Executive Summary

**Health Score: 3/10 — Structural rebuild needed.**

1. **MK Broad is cannibalizing all 3 SK campaigns.** MK broad consumes 54% of portfolio spend ($301/30d) while SK campaigns combined get only 19% ($105/30d). The MK broad has ZERO negative keywords for the SK campaign terms, so it competes with its own exact-match campaigns and wins — driving up CPCs for both.
2. **Auto + MK Broad are budget-capped (100%+ utilization) while all 3 SK campaigns are starved (0-4.6% utilization).** The broad campaigns are eating all the budget before SK campaigns can get impressions.
3. **Portfolio ACoS is 56.7% vs 30% target** — nearly 2x over target. Every campaign is above target except one bright spot: "kids needlepoint" keyword at 28.5% ACoS in MK broad.
4. **Dead ASIN B09HVDYMDK (Mermaid)** returns 404 but is advertised in all 5 campaigns — wasting impressions.
5. **Missing campaign types:** No PT campaign, no dedicated "needlepoint pouch kit" SK despite strong conversion signal (22.6% ACoS, 13.3% CVR in MK broad).

**Root cause:** This portfolio was never properly traffic-isolated. The MK broad acts as a catch-all that starves the SK campaigns of their targeted traffic.

---

## ASINs in This Portfolio

| ASIN | Product | Role | BSR | Status |
|------|---------|------|-----|--------|
| B09HVDNFMR | Needlepoint Wallet Kit (Cat) | Hero | #96 Sewing Project Kits | Active |
| B09HVSLBS6 | Needlepoint Wallet Kit (Cat&Dog) | Secondary | #96 | Active |
| B09HVCCNM2 | Needlepoint Wallet Kit (Unicorn) | Secondary | #96 | Active |
| B09HVDYMDK | Needlepoint Wallet Kit (Mermaid) | Dead | 404 | **PAGE NOT FOUND** |

**SKUs:** N7-TUSA-2329 (Cat), KM-QL7C-QZMZ (Cat&Dog), KL-L7KN-R85L (Unicorn)

---

## 30-Day Performance Overview

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Spend** | $557.54 | — | — |
| **Sales** | $982.76 | — | — |
| **ACoS** | 56.7% | 30% | BLEEDING |
| **Orders** | 50 | — | — |
| **CVR** | 5.1% | 10% | BELOW TARGET |
| **CPC** | $0.57 | — | — |
| **ROAS** | 1.76 | 3.33 | BELOW TARGET |
| **Clicks** | 975 | — | — |
| **Impressions** | 70,082 | — | — |

---

## Campaign-by-Campaign Breakdown

| # | Campaign | Type | 30d Spend | 30d Sales | ACoS | Orders | CVR | CPC | TOS% | Budget | Util | Status |
|---|----------|------|-----------|-----------|------|--------|-----|-----|------|--------|------|--------|
| 1 | MK broad and phrase TOS | MK Broad | $301.03 | $562.30 | 53.5% | 30 | 7.2% | $0.73 | 78%* | $10/d | 102% | BLEEDING |
| 2 | SPA auto TOS | Auto | $151.52 | $216.68 | 69.9% | 10 | 2.9% | $0.44 | 0%* | $5/d | 100% | BLEEDING |
| 3 | SK needlepoint kits for beginners | SK | $53.02 | $129.86 | 40.8% | 6 | 4.7% | $0.42 | 50% | $15/d | 0% | ABOVE TARGET |
| 4 | SK kids needlepoint kit | SK | $34.84 | $53.94 | 64.6% | 3 | 5.3% | $0.61 | 207% | $8/d | 4.6% | BLEEDING |
| 5 | SK needlepoint kit for kids | SK | $17.13 | $19.98 | 85.7% | 1 | 3.0% | $0.52 | 101% | $8/d | 0% | BLEEDING |

*TOS changed today by bid recommender (MK broad 131%→78%, Auto 55%→0%)

**Key observation:** MK broad alone accounts for 54% of all portfolio spend. It gets 414 clicks vs only 217 clicks combined across all 3 SK campaigns. The SK campaigns are structurally starved.

---

## Portfolio Structure Health Score

### Campaign Type Inventory

| Type | Required | Found | Status | 30d Spend | % of Portfolio |
|------|----------|-------|--------|-----------|----------------|
| Auto | 1 | 1 | OK | $151.52 | 27.2% |
| MK Broad | 1 | 1 | OK (but OVER-DOMINANT) | $301.03 | 54.0% |
| SK (single keyword exact) | ~3+ | 3 | OK (count) | $104.99 | 18.8% |
| MK (root phrase) | ~2+ | 0 | MISSING | $0 | 0% |
| PT (product targeting) | 1 | 0 | **MISSING** | $0 | 0% |
| Shield | 1 | N/A | Covered by Shield All | — | — |
| Low-bid Discovery | 1-2 | 0 | MISSING | $0 | 0% |

### Spend Distribution Assessment

| Metric | Value | Benchmark | Status |
|--------|-------|-----------|--------|
| MK Broad % of total spend | 54.0% | <30% ideal, >40% = cannibalization risk | **CRITICAL** |
| Auto % of total spend | 27.2% | <20% ideal, >35% = too much auto reliance | **WARNING** |
| SK % of total spend | 18.8% | >40% ideal | **CRITICAL** |
| Top 1 campaign % of spend | 54.0% (MK broad) | <35% ideal, >50% = over-concentration | **CRITICAL** |
| Single-keyword campaigns | 3 SK | More = better precision | OK (count) |

### Campaign Gap Analysis

| Expected Campaign | Keyword / Target | Search Volume | Exists? | Action |
|-------------------|-----------------|---------------|---------|--------|
| SK "needlepoint pouch kit" | needlepoint pouch kit | ~300 | NO | CREATE (22.6% ACoS, 13.3% CVR in MK broad) |
| SK "half stitch needlepoint kits" | half stitch needlepoint kits | 1,425 | NO | MONITOR (47.6% ACoS, rank #4) |
| MK Root "needlepoint" | needlepoint + variants | ~2,000 | NO | LOW PRIORITY (generic root) |
| PT (product targeting) | Competitor ASINs | — | NO | CREATE |

### Structure Health Grade

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Campaign type completeness (PT missing, MK root missing) | 4/10 | 25% | 1.00 |
| Spend distribution balance (MK broad 54%, SK 19%) | 2/10 | 25% | 0.50 |
| Keyword coverage (top SV keywords have SK campaigns) | 6/10 | 25% | 1.50 |
| Single-targeting precision (3 SK campaigns — decent) | 6/10 | 15% | 0.90 |
| Negative keyword hygiene (SK = 0 negatives, cannibalizing) | 1/10 | 10% | 0.10 |
| **TOTAL** | | 100% | **4.0/10** |

---

## TOS Strategy Audit

| Campaign | TOS% | Eff TOS Bid | TOS Spend | TOS ACoS | PP Spend | PP ACoS | Other Spend | Other ACoS | Health |
|----------|------|-------------|-----------|----------|----------|---------|-------------|------------|--------|
| MK broad | 78%* | $0.58-$0.93 | $220.11 | 81.9% | $48.53 | 32.4% | $32.39 | 22.5% | TOS_BLEEDING |
| Auto | 0%* | $0.44 | $49.07 | 272.9% | $20.55 | 102.9% | $79.81 | 44.6% | ALL_BLEEDING |
| SK kids needlepoint kit | 207% | $1.07 | $21.26 | 118.2% | $9.84 | 54.7% | $3.74 | 20.8% | TOS_BLEEDING |
| SK NP kits for beginners | 50% | $0.48 | $11.88 | 33.0% | $23.65 | 59.2% | $17.49 | 32.4% | TOS_EFFICIENT_PP_BLEEDING |
| SK NP kit for kids | 101% | $0.81 | $9.36 | 46.9% | $4.97 | ∞ | $2.80 | ∞ | TOS_ONLY_PLACEMENT |

*Changed today by bid recommender

**Key findings:**
- MK broad: TOS is 73% of spend ($220/$301) at 81.9% ACoS while PP (32.4%) and Other (22.5%) are efficient. TOS cut from 131%→78% today was correct but may need further reduction.
- Auto: "Other on-Amazon" is the only productive placement (8 orders, 44.6% ACoS). TOS removal today was correct.
- SK kids needlepoint kit: TOS at 207% is very aggressive but campaign barely gets traffic (4.6% utilization). Issue is cannibalization, not bid level. **Hold TOS changes until negatives redirect traffic.**
- SK NP kits for beginners: TOS at 33.0% ACoS is actually at target. PP at 59.2% is bleeding. Campaign gets 0% utilization though. **Hold changes.**
- SK NP kit for kids: Too few orders (1 in 30d) for reliable placement analysis. **Hold changes.**

---

## Keyword Strategy Analysis

**Roots covered across campaigns:**
- "needlepoint kit" (MK broad BROAD + SK EXACT variants)
- "kids needlepoint" (MK broad BROAD)
- "needlepoint kits" (MK broad BROAD)

**Match type coverage:**

| Root | Auto | MK Broad | SK Exact | Coverage |
|------|------|----------|----------|----------|
| kids needlepoint kit | ✓ (loose) | ✓ (broad) | ✓ | FULL (but cannibalizing) |
| needlepoint kit for kids | ✓ (loose) | ✓ (broad) | ✓ | FULL (but cannibalizing) |
| needlepoint kits for beginners | ✓ (loose) | ✓ (broad) | ✓ | FULL (but cannibalizing) |
| needlepoint pouch kit | ✓ (loose) | ✓ (broad) | ✗ | GAP — no SK campaign |
| half stitch needlepoint kits | ✓ (loose) | ✓ (broad) | ✗ | GAP — no SK campaign |
| needlepoint for kids | ✗ | ✗ | ✗ | GAP — highest relevancy keyword |

**Total keywords:** 11 across 5 campaigns (8 in MK broad, 1 each in SK campaigns)
**Missing roots:** "needlepoint pouch kit" (converting at 22.6% ACoS), "needlepoint for kids" (SV 701, Rel 1.0, rank #10)

---

## Rank Radar Analysis (28-day trending)

| Keyword | SV | Rank Now | 7d Ago | Start | Trend | Alert |
|---------|-----|---------|--------|-------|-------|-------|
| needlepoint kits (generic) | 15,617 | 19 | 101 | 101 | **IMPROVING** | New top-20 entry |
| needlepoint kit (generic) | 24,095 | 25 | 101 | 20 | DECLINING | Was #20, now #25 |
| needlepoint (root) | 51,649 | 67 | 101 | 101 | IMPROVING | New ranking |
| needlepoint kits for beginners | 6,461 | 78 | 101 | 101 | IMPROVING | New ranking |
| needlepoint for beginners | 2,258 | 86 | 101 | 85 | STABLE | — |
| needlepoint cards | 2,669 | 71 | 101 | 49 | **DECLINING** | Was #49, now #71 |

**Note:** Most tracked keywords are adult-focused (needlepoint kits for adults, SV 61,222 — rank 101). Our product is kids-oriented so low relevancy on adult terms is expected.

**Niche-specific ranks (from DataDive niche keywords):**

| Keyword | SV | Our Rank | Relevancy | Status |
|---------|-----|---------|-----------|--------|
| half stitch needlepoint kits | 1,425 | #4 | 0.3 | STAR |
| needlepoint for kids | 701 | #10 | 1.0 | GOOD |
| kids needlepoint kit | 902 | #11 | 0.9 | GOOD |
| needlepoint kits for kids | 1,109 | #14 | 0.9 | DECENT |
| self finishing needlepoint | 1,168 | #24 | 0.3 | DECENT |
| kids needlepoint kits age 5-8 | 634 | #36 | 0.8 | NEEDS WORK |
| kids cross stitch kit | 1,845 | #46 | 0.6 | LOW |
| needlepoint kit for beginners | 1,491 | #47 | 0.3 | LOW |

---

## Search Term Analysis

### Top Converters (14d)

| Search Term | Campaign | Clicks | Orders | ACoS | CVR | Opportunity |
|-------------|----------|--------|--------|------|-----|-------------|
| kids needlepoint kit | SK (exact) | 33 | 3 | 33.2% | 9.1% | Near target — fix cannibalization |
| needlepoint pouch kit | MK broad | 15 | 2 | 22.6% | 13.3% | **PROMOTE → create SK campaign** |
| needlepoint kits for beginners | SK (exact) | 49 | 1 | 53.8% | 2.0% | CVR too low — fix with negatives first |
| half stitch needlepoint kits | MK broad | 15 | 1 | 47.6% | 6.7% | Monitor — rank #4 organically |
| needlepoint kits for kids | SK (exact) | 11 | 1 | 30.5% | 9.1% | At target — needs more traffic |
| needlepoint kits for adults | MK broad | 13 | 1 | 29.5% | 7.7% | Unexpected — adults buying kids kit |
| cross stitch kits | Auto | 8 | 1 | 9.1% | 12.5% | Different portfolio coverage |
| kids needlepoint kits age 8-12 | MK broad | 2 | 1 | 8.6% | 50.0% | Low volume but excellent CVR |
| bargello needlepoint kits | MK broad | 2 | 1 | 5.6% | 50.0% | Discovery — low volume |
| needlepoint craft bag kit | MK broad | 1 | 1 | 4.9% | 100.0% | Discovery — very low volume |

### Zero-Order Waste (14d, >$1 spend)

| Search Term | Campaign | Clicks | Spend | CPC | Relevance | Action |
|-------------|----------|--------|-------|-----|-----------|--------|
| needlepoint (generic) | Auto | 16 | $7.71 | $0.48 | Low — too broad | Monitor (Auto TOS now 0%) |
| needlepoint kits | MK broad | 8+11 | $12.69 | $0.47-0.94 | Medium | Monitor (MK TOS cut today) |
| stitch and zip needlepoint kits | MK broad | 9 | $6.12 | $0.68 | **IRRELEVANT — competitor brand** | **NEGATE** |
| needlepoint kits for beginners | MK broad | 4 | $5.44 | $1.36 | Cannibalizing SK | **NEGATE in MK broad** |
| kids needlepoint kit | MK broad | 5 | $5.15 | $1.03 | Cannibalizing SK | **NEGATE in MK broad** |
| needlepoint kit | Auto + MK broad | 16 | $9.80 | $0.42-1.04 | Medium — generic | Monitor |
| needlepoint craft kit | MK broad | 4 | $3.77 | $0.94 | Medium | Monitor |
| needlepoint kits for adults | Auto | 9 | $3.76 | $0.42 | Low — wrong audience | Monitor (1 order in MK broad) |
| needlepoint kit for kids | SK (exact!) | 7 | $2.57 | $0.37 | Zero orders in SK | **Investigate** (has 1 order in MK broad variant) |
| beginner punch needle kit | MK broad | 1 | $1.60 | $1.60 | **IRRELEVANT — wrong product** | **NEGATE** |
| needlepoint kits for children | MK broad | 2 | $1.59 | $0.80 | Relevant | Monitor (low volume) |

### Cannibalization Check

**12 terms appearing in 2+ campaigns — CRITICAL ISSUE:**

| Search Term | Campaigns | Impact |
|-------------|-----------|--------|
| **needlepoint kits for beginners** | Auto + MK broad + SK | Triple cannibalization — driving up CPC |
| **kids needlepoint kit** | MK broad + SK | MK broad stealing SK exact traffic |
| **needlepoint kit for kids** | MK broad + SK | MK broad stealing SK exact traffic |
| **needlepoint kits for kids** | MK broad + SK | MK broad stealing SK variant traffic |
| needlepoint kit | Auto + MK broad | Expected (generic term) |
| needlepoint kits | Auto + MK broad | Expected (generic term) |
| needlepoint pouch kit | Auto + MK broad | Expected (no SK exists) |
| needlepoint kits for adults | Auto + MK broad | Expected (no SK exists) |
| half stitch needlepoint kits | Auto + MK broad | Expected (no SK exists) |
| stitch and zip needlepoint kits | Auto + MK broad | Both should negate (competitor brand) |
| needlepoint pouch kits for beginners | Auto + MK broad | Expected (no SK exists) |
| beginner needlepoint kits for adults | Auto + MK broad | Expected (no SK exists) |

**The bolded 4 rows are the critical fix.** These are terms where a dedicated SK campaign exists but MK broad is competing with it — and winning due to higher effective bids and budget availability.

---

## MK Broad Cannibalization Audit

| Metric | Value |
|--------|-------|
| MK Broad 30d Spend | $301.03 |
| MK Broad % of Portfolio Spend | **54.0%** |
| MK Broad ACoS | 53.5% |
| MK Broad Orders | 30 |
| Overlapping SK Keywords | kids needlepoint kit, needlepoint kit for kids, needlepoint kits for kids, needlepoint kits for beginners |

**Cannibalization confirmed.** MK Broad is >30% of portfolio spend AND its search terms overlap with all 3 active SK campaigns. The broad match is competing with its own exact-match SK campaigns, driving up CPCs for both.

**Evidence:**
- "kids needlepoint kit" in MK broad: $5.15 spend, 0 orders (14d). Same term in SK: $17.90, 3 orders, 33.2% ACoS.
- "needlepoint kits for beginners" in MK broad: $8.59 spend (3 orders at $3.15 + 0 orders at $5.44). Same term in SK: $19.35, 1 order.
- MK broad pays $1.03-$1.36 CPC for cannibalizing terms. SK campaigns pay $0.37-$0.61 CPC. MK broad is overpaying.

---

## Structural Issues Summary

1. **MK Broad cannibalization (ROOT CAUSE #1):** MK broad has zero negative exact keywords for SK campaign terms. It competes with SK campaigns on every auction, usually wins (higher budget availability), and wastes spend at higher CPCs. This starves SK campaigns of traffic and inflates portfolio-wide ACoS.

2. **SK campaigns have zero negatives (ROOT CAUSE #2):** None of the 3 SK campaigns have any campaign-level negatives. While SK EXACT match is precise by nature, having negatives prevents edge-case matching and signals to Amazon's algorithm.

3. **Budget structure is inverted:** MK broad ($10/d, 102% util) gets more budget than any SK. But SK campaigns are dormant (0-4.6% util), suggesting the issue isn't budget — it's traffic routing. MK broad is capturing all traffic before SK campaigns get a chance.

4. **Dead ASIN advertised everywhere:** B09HVDYMDK (Mermaid variant) returns 404 from catalog API. It's included in all 5 campaigns' product ads, wasting impressions on a non-existent product page.

5. **No PT campaign:** Missing product targeting means no defensive positioning against competitors and no discovery via product page placements.

6. **TOS concentration on MK broad:** 73% of MK broad spend ($220/$301) goes to TOS at 81.9% ACoS. PP (32.4%) and Other (22.5%) are profitable but underfunded. The TOS cut today (131%→78%) will help but the fundamental issue is MK broad shouldn't be this dominant.

7. **Low CVR across portfolio (5.1% vs 10% target):** May indicate listing quality issue or wrong audience targeting. "needlepoint kits for adults" matching our kids product suggests some irrelevant traffic.

8. **Paused campaign cleanup needed:** 6 paused campaigns including legacy ones (SC INCR series, legacy manual/auto with very high TOS modifiers) that should be archived.

---

## Action Plan — 14 Items (Impact-Ranked)

### P1 — Critical (4 items, est. $35-50/week impact)

| # | Score | Category | Action | Campaign | 30d Evidence | Current | Proposed | Est. Weekly Impact |
|---|-------|----------|--------|----------|-------------|---------|----------|-------------------|
| 1 | 92 | NEGATE_SEARCH_TERM | Add negative exact in MK broad for all 3 SK terms | MK broad (400878727568208) | $301 spend, 30 orders, 53.5% ACoS. Cannibalizing terms: $8.59 waste on overlapping queries | 0 negatives for SK terms | Add 4 negative exact: "kids needlepoint kit", "needlepoint kit for kids", "needlepoint kits for kids", "needlepoint kits for beginners" | -$8-12/wk waste |
| 2 | 88 | NEGATE_SEARCH_TERM | Add negative exact in Auto for all 3 SK terms | Auto (372981829297208) | $151 spend, 10 orders, 69.9% ACoS. "needlepoint kits for beginners" confirmed in auto search terms | 153 existing negatives (but NOT these terms) | Add 4 negative exact: same 4 terms as Item 1 | -$3-5/wk waste |
| 3 | 78 | NEGATE_SEARCH_TERM | Negate irrelevant terms in MK broad | MK broad (400878727568208) | "stitch and zip needlepoint kits" $6.12/14d, 0 orders (competitor brand). "beginner punch needle kit for kids" $1.60/14d, 0 orders (wrong product) | No negatives for these terms | Add 2 negative exact: "stitch and zip needlepoint kits", "beginner punch needle kit for kids" | -$3-4/wk waste |
| 4 | 72 | NEGATE_SEARCH_TERM | Negate irrelevant terms in Auto | Auto (372981829297208) | "stitch and zip needlepoint kits" confirmed in auto. "beginner punch needle" likely matching | May already have some | Add 2 negative exact: same 2 terms as Item 3 | -$1-2/wk waste |

**P1 rationale:** The cannibalization negatives (Items 1-2) are the single most impactful structural fix for this portfolio. They redirect traffic from the cannibalizing broad campaigns to the dedicated SK campaigns, improving both ACoS and traffic quality. Items 3-4 stop spend on clearly irrelevant terms.

### P2 — Optimization (4 items, est. $10-20/week impact)

| # | Score | Category | Action | Campaign | 30d Evidence | Current | Proposed | Est. Weekly Impact |
|---|-------|----------|--------|----------|-------------|---------|----------|-------------------|
| 5 | 62 | BUDGET_DECREASE | Reduce MK broad daily budget | MK broad (400878727568208) | 102% utilization, 53.5% ACoS, $301/30d. Budget-capped and bleeding. After negatives (Items 1-3), lower spend cap to force discipline. | $10/d | $7/d | -$6-8/wk spend reduction |
| 6 | 58 | CAMPAIGN_CREATE | Create SK "needlepoint pouch kit" | New campaign | "needlepoint pouch kit" in MK broad: 15 clicks, 2 orders, 22.6% ACoS, 13.3% CVR (14d). Strong PROMOTE signal. | Does not exist | SK EXACT campaign, PAUSED | +$5-8/wk profitable spend |
| 7 | 52 | KEYWORD_PAUSE | Pause "needlepoint kits" PHRASE in MK broad | MK broad (400878727568208) | 0 impressions, 0 clicks over 30d. All 4 phrase-match keywords are dead weight (0 impressions each). | ENABLED (4 phrase keywords) | PAUSED | Cleanup — no spend impact |
| 8 | 48 | CAMPAIGN_PAUSE | Remove dead ASIN B09HVDYMDK from all campaigns | All 5 campaigns | 404 from catalog API. Mermaid variant — page not found. Wasting ad impressions on dead product. | Advertised in all 5 campaigns | Remove product ad from all | Improved impression quality |

### P3 — Maintenance (3 items)

| # | Score | Category | Action | Campaign | Current | Proposed | Est. Weekly Impact | Confidence |
|---|-------|----------|--------|----------|---------|----------|-------------------|------------|
| 9 | 38 | CAMPAIGN_CREATE | Create PT campaign for competitor targeting | New campaign | Missing campaign type | PT campaign targeting top competitor ASINs, PAUSED | Discovery channel | Medium |
| 10 | 35 | CAMPAIGN_ARCHIVE | Archive 6 legacy paused campaigns | 6 paused campaigns | PAUSED (legacy SC INCR + old manual/auto) | ARCHIVED | Cleanup | Medium |
| 11 | 30 | NEGATE_SEARCH_TERM | Cross-negate "needlepoint pouch kit" in MK broad + Auto | MK broad + Auto | Depends on Item 6 (SK creation) | Add negative exact if SK created | Traffic isolation | Medium |

### P4 — Monitor Only (3 items)

- **SK campaign performance after negatives** — Re-evaluate all 3 SK campaigns in 7-10 days once Items 1-2 redirect traffic. May need TOS adjustments based on new traffic patterns. SK kids needlepoint kit (TOS 207%) should see increased traffic and may need TOS reduction. SK needlepoint kits for beginners (TOS 50%) may need TOS increase.
- **Rank defense on "needlepoint kit" (SV 24,095)** — Rank dropped from #20 to #25 over 28 days. Not critical yet but watch for further decline. If drops below #30, consider BID_INCREASE on SK or targeted campaign.
- **"needlepoint kits for adults" conversion** — Got 1 order at 29.5% ACoS in MK broad (14d). Unexpected — adults buying a kids kit. Don't negate yet. Monitor for 30d to see if this is a real audience segment.

### Dependencies

- Item 5 (budget decrease) should execute AFTER Items 1-4 (negatives) — negatives first reduce wasted traffic, then budget cap limits remaining spend
- Item 11 depends on Item 6 — only negate "needlepoint pouch kit" in MK broad/Auto after SK campaign is created
- Item 8 (remove dead ASIN) is independent — can execute anytime

---

## Your Call

**14 actions identified across 4 priorities.**

| Option | Description |
|--------|-------------|
| **Approve all P1** | Execute 4 critical negation items now |
| **Approve P1 + P2** | Execute 8 critical + optimization items |
| **Approve specific** | "approve 1, 3, 5" (by item number) |
| **Modify** | "change item 5 budget to $8/d" (I'll adjust and confirm) |
| **Save brief only** | No API changes — save analysis for reference |

**Execution mode:**

| Mode | Description |
|------|-------------|
| **Step-by-step** (default) | I confirm each action before executing, show result, then ask about next |
| **Auto-execute** | I run all approved items in sequence, report results at the end |

What would you like to do?
