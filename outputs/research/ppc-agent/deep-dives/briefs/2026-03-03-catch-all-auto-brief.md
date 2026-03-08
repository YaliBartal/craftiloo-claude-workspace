# .Catch All Auto — Portfolio Action Plan
**Date:** 2026-03-03
**Stage:** General | **ACoS Target:** N/A (catch-all) | **Red Flag:** >40%
**Last Action Plan:** First run
**Data Sources:** Weekly PPC snapshot (Mar 1, 2d old), live campaign data (Mar 3), Seller Board 7d, negative keyword audit. Campaign/search term/placement reports stuck in PENDING (Amazon API known issue — fell back to snapshot).

---

## Executive Summary

**Health Score: 7/10** — Top-performing portfolio (26.3% ACoS, 140 orders, $3.2K sales/week) but harboring a **critical structural gap**: 3 of 6 campaigns (representing $250/day in budget) have **ZERO negative keywords**, while the older 3 campaigns have 215-450 negatives each. This means the newer high-budget campaigns are spending on terms already known to be wasteful or handled by dedicated portfolio campaigns. Fixing the negative keyword gap is the single highest-impact action.

**Key findings:**
1. **Negative keyword gap** — Campaigns 4, 5, 6 have 0 negatives vs 215-450 on campaigns 1-3
2. **Paused product still advertised** — Dessert Family ASIN (B096MYBLS1) in 2 campaigns despite portfolio being paused
3. **Budget over-allocation** — $355/day budget but only ~$121/day actual spend (34% utilization)
4. **Strong performance** — #1 revenue portfolio, healthy ACoS, highest order volume

---

## ASINs in This Portfolio

This is a **catch-all portfolio** — campaigns contain 18-41 ASINs each covering the entire Craftiloo + Shinshin catalog. Not product-specific, so no hero ASIN classification applies.

**ASIN count per campaign:**
| Campaign | ASINs |
|----------|-------|
| auto 0.39 | 27 |
| auto 0.49 | 24 |
| auto 0.29 | 35 |
| auto NGO (old) | 18 |
| auto 0.15 | 36 |
| auto 0.19 | 41 |

**Note:** B096MYBLS1 (Dessert Family) is in campaigns 5 and 6 but the Dessert portfolio is fully PAUSED (OOS since Mar 2). Should be removed.

---

## 7-Day Performance Overview (from Weekly Snapshot, Feb 20-26)

| Metric | Value | Account Avg | Status |
|--------|-------|-------------|--------|
| **Spend** | $844.89 | $5,291 total | 16.0% of account spend |
| **Sales** | $3,209.72 | $14,125 total | 22.7% of account sales |
| **ACoS** | 26.3% | 37.5% | EFFICIENT |
| **Orders** | 140 | 581 total | 24.1% of account orders |
| **CVR** | est. ~8% | 7.8% | ABOVE AVERAGE |
| **CPC** | est. ~$0.35 | $0.70 | LOW (by design — low bids) |
| **ROAS** | 3.80x | 2.67x | STRONG |
| **Daily Spend** | ~$121/day | — | — |
| **Budget Utilization** | ~34% | — | UNDERUTILIZING |

**Status: TOP PERFORMER** — Best revenue portfolio in the account. Low CPC + decent conversion = efficient spend.

---

## Campaign-by-Campaign Breakdown

| # | Campaign | Bid | Budget | TOS% | ROS% | PP% | ASINs | Negatives | Started | Status |
|---|----------|-----|--------|------|------|-----|-------|-----------|---------|--------|
| 1 | auto 0.39 | $0.39 | $20/d | 13% | 21% | — | 27 | 215 | Mar 2023 | MATURE |
| 2 | auto 0.49 | $0.49 | $25/d | — | — | 3% | 24 | 450 | Mar 2023 | MATURE |
| 3 | auto 0.29 | $60/d | $0.29 | 25% | 15% | — | 35 | 434 | Mar 2023 | MATURE |
| 4 | auto NGO (old) | ? | $50/d | 70% | — | 20% | 18 | **0** | Mar 2024 | **GAP** |
| 5 | auto 0.15 | $0.15 | $100/d | 19% | — | — | 36 | **0** | Nov 2025 | **GAP** |
| 6 | auto 0.19 | $0.19 | $100/d | 21% | — | — | 41 | **0** | Nov 2025 | **GAP** |

**Total Budget:** $355/day | **Actual Spend:** ~$121/day | **Utilization:** ~34%

**Budget Usage (today as of ~9 AM):**
| Campaign | Budget | Used Today | % |
|----------|--------|------------|---|
| auto 0.39 | $20 | $0.49 | 2.4% |
| auto 0.49 | $25 | $0.00 | 0.0% |
| auto 0.29 | $60 | $0.26 | 0.4% |
| auto NGO (old) | $50 | $0.82 | 1.6% |
| auto 0.15 | $100 | $0.12 | 0.1% |
| auto 0.19 | $100 | $0.15 | 0.2% |

---

## Campaign Structure Audit

| Type | Required | Found | Status |
|------|----------|-------|--------|
| Auto | 1+ | 6 | **EXCESS** — 6 Auto campaigns is unusual |
| Broad | 0 | 0 | N/A — catch-all doesn't need Broad |
| SK | 0 | 0 | N/A — catch-all doesn't need SK |
| MK | 0 | 0 | N/A — catch-all doesn't need MK |
| PT | 0 | 0 | N/A |

**Commentary:** The 6-Auto structure is an intentional **bid tiering strategy** — different bid levels ($0.15, $0.19, $0.29, $0.39, $0.49, + NGO) with different placement modifiers capture traffic at various price points. This is a valid approach for a catch-all. The issue isn't the number of campaigns — it's the inconsistent negative keyword coverage.

---

## TOS Strategy Audit

| Campaign | TOS% | Effective TOS Bid | PP% | ROS% | Strategy |
|----------|------|-------------------|-----|------|----------|
| auto 0.39 | 13% | ~$0.44 | — | 21% | **ROS-heavy** — favors rest-of-search |
| auto 0.49 | — | $0.49 | 3% | — | **PP-only** — product pages |
| auto 0.29 | 25% | ~$0.36 | — | 15% | **Balanced** — slight TOS lean |
| auto NGO (old) | 70% | high | 20% | — | **TOS-dominant** — aggressive top |
| auto 0.15 | 19% | ~$0.18 | — | — | **Low-cost TOS** — budget discovery |
| auto 0.19 | 21% | ~$0.23 | — | — | **Low-cost TOS** — budget discovery |

**Assessment:** Good placement diversification across campaigns. NGO campaign handles aggressive TOS, 0.49 handles PP, others split between TOS and ROS. The strategy creates a bid ladder.

---

## Negative Keyword Analysis (CRITICAL FINDING)

### Coverage Gap

| Campaign | Negatives | Status |
|----------|-----------|--------|
| auto 0.39 (Mar 2023) | 215 | Mature, well-maintained |
| auto 0.49 (Mar 2023) | 450 | Most extensive negation |
| auto 0.29 (Mar 2023) | 434 | Well-maintained |
| auto NGO (old) (Mar 2024) | **0** | **UNPROTECTED** |
| auto 0.15 (Nov 2025) | **0** | **UNPROTECTED** |
| auto 0.19 (Nov 2025) | **0** | **UNPROTECTED** |

**Impact:** The 3 campaigns with 0 negatives have a combined $250/day budget. They're receiving traffic for terms that the older campaigns have already identified as wasteful:
- Competitor brand terms (aquabeads, hama, etc.)
- Category terms handled by dedicated portfolios (cross stitch, fuse beads, latch hook, etc.)
- Irrelevant terms (jewelry making, fairy garden, etc.)

**The purpose of negatives in catch-all campaigns** is to prevent overlap with dedicated portfolio campaigns. Without negatives, these campaigns cannibalize spending from portfolios like Fuse Beads, Cross Stitch Hero, Fairy Family, etc. — competing against their own dedicated campaigns.

### Negative keyword themes in mature campaigns (1-3):
- **Portfolio-specific terms** negated: cross stitch, embroidery, fuse beads, latch hook, perler beads, mini beads, melty beads, punch needle, needlepoint, sewing kit, etc.
- **Competitor brands** negated: aquabeads, hama, qixels, the woobles, etc.
- **Irrelevant terms** negated: jewelry making, fairy garden, aqua beads, rice beads, etc.
- **ASIN-level negatives**: competitor ASINs (B0xxxxx format)

---

## Seller Board Context (7-day, Amazon.com only)

The catch-all portfolio covers the entire catalog. From Seller Board, top-selling ASINs this week:

| ASIN | Product | 7d Organic Sales | 7d PPC Sales | Organic Ratio |
|------|---------|-----------------|-------------|---------------|
| B09THLVFZK | Mini Fuse Beads 24K | $890+ | $330+ | ~73% |
| B08DDJCQKF | Cross Stitch Backpack Charms | $640+ | $400+ | ~62% |
| B09WQSBZY7 | Fairy Sewing Kit | $505+ | $330+ | ~60% |
| B07D6D95NG | Biggie Beads 1500 | $275+ | $200+ | ~58% |
| B09X55KL2C | 10 Embroidery Kit | $336+ | $144+ | ~70% |
| B0F8R652FX | Latch Hook Rainbow Heart | $175+ | $250+ | ~41% |

**Overall account:** 70.3% organic ratio, 18.8% TACoS, 17.8% margin.

---

## Structural Issues Summary

### 1. Negative Keyword Gap (CRITICAL)
**Root cause:** Campaigns 4-6 were created without copying the negative keyword lists from the mature campaigns 1-3. This is likely an oversight from when campaigns were added (Mar 2024 and Nov 2025).
**Downstream impact:** These campaigns receive wasteful traffic on terms already negated in older campaigns. They also cannibalize dedicated portfolio campaigns by bidding on their terms (cross stitch, fuse beads, etc.).

### 2. Paused Product Still Advertised
**Root cause:** Dessert Family (B096MYBLS1) was paused across its portfolio on Mar 2 (OOS, 5 units stock). But the ASIN is still active in catch-all campaigns 5 and 6.
**Downstream impact:** Small — Amazon won't show ads for OOS ASINs effectively, but it adds noise and could trigger impressions if stock is briefly available.

### 3. Budget Over-Allocation
**Root cause:** $355/day budget but only ~$121/day actual spend. The low bids ($0.15-$0.49) naturally limit spend.
**Downstream impact:** Low — no money is wasted (Amazon doesn't spend more than needed). But the inflated budgets mask the true cost structure and make budget tracking harder.

### 4. No Search Term Visibility (data gap)
**Root cause:** Amazon Ads API reports stuck in PENDING. Without search term data, can't identify specific wasteful terms or promotion candidates within the catch-all.
**Downstream impact:** Moderate — we're flying blind on what the 3 unprotected campaigns are actually spending on. Recommend re-running search term harvest in 1-2 days.

---

## Action Plan — 5 Items (Impact-Ranked)

### P1 — Critical (2 items, est. $50-100/week savings)

| # | Score | Category | Action | Campaign | Current | Proposed | Est. Weekly Impact | Confidence |
|---|-------|----------|--------|----------|---------|----------|-------------------|------------|
| 1 | 88 | NEGATE_SEARCH_TERM | Copy negative keywords from campaigns 1-3 to campaign 4 (NGO old) | auto NGO (274→352) | 0 negatives | ~200+ negatives | -$20-40/wk waste reduction | HIGH — 3yr proven negative list |
| 2 | 85 | NEGATE_SEARCH_TERM | Copy negative keywords from campaigns 1-3 to campaigns 5+6 (0.15 & 0.19) | auto 0.15 + 0.19 | 0 negatives | ~200+ negatives each | -$30-60/wk waste reduction | HIGH — 3yr proven negative list |

**P1 rationale:** The catch-all's entire value proposition is capturing long-tail terms that don't have dedicated campaigns. Without negatives, the unprotected campaigns spend on short-head terms that ARE handled by dedicated campaigns — essentially paying twice for the same traffic. The mature campaigns' negative lists represent 3 years of optimization. Copying them to the newer campaigns is the single highest-impact, highest-confidence action available.

**Implementation approach for Items 1-2:**
- Extract the **union** of all ENABLED negatives from campaigns 1, 2, and 3
- Deduplicate
- Apply as NEGATIVE_EXACT to campaigns 4, 5, and 6
- Batch in groups of 100 per API call (Amazon limit)
- Focus on the **most common/important negatives** that appear in at least 2 of 3 campaigns for maximum confidence

### P2 — Optimization (2 items)

| # | Score | Category | Action | Campaign | Current | Proposed | Est. Weekly Impact | Confidence |
|---|-------|----------|--------|----------|---------|----------|-------------------|------------|
| 3 | 52 | KEYWORD_PAUSE | Remove Dessert ASIN B096MYBLS1 from campaigns 5+6 | auto 0.15 + 0.19 | ASIN active in ad group | Remove product ad | Minimal — prevents confusion | MEDIUM |
| 4 | 48 | BUDGET_DECREASE | Right-size budgets to match actual spend | all 6 | $355/day total | ~$180/day total | No $ savings (spend stays same) | MEDIUM |

**Item 3 detail:** Remove B096MYBLS1 (Dessert Family sewing kit) from campaigns 5 and 6 product ads. Portfolio is paused, product is OOS. Low impact but good hygiene.

**Item 4 detail:** Current budgets are ~3x actual spend. Could reduce: auto 0.39 $20→$15, auto 0.49 $25→$15, auto 0.29 $60→$40, auto NGO $50→$30, auto 0.15 $100→$40, auto 0.19 $100→$40. This doesn't save money (spend is bid-limited, not budget-limited) but makes reporting cleaner. **Only do this if you want tighter budget control — skip if you prefer budget headroom.**

### P3 — Maintenance (1 item)

| # | Score | Category | Action | Campaign | Current | Proposed | Est. Weekly Impact | Confidence |
|---|-------|----------|--------|----------|---------|----------|-------------------|------------|
| 5 | 35 | CAMPAIGN_CONSOLIDATE | Consider merging campaigns 5+6 (nearly identical bids $0.15/$0.19) | auto 0.15 + 0.19 | 2 separate campaigns | 1 combined campaign | Reduces management overhead | LOW — needs more data first |

**Item 5 detail:** Campaigns 5 (bid $0.15) and 6 (bid $0.19) have nearly identical TOS modifiers (19% vs 21%), similar ASIN sets (36 vs 41), same start date (Nov 2025), and both have 0 negatives. A $0.04 bid difference may not justify two separate campaigns. However, **do not consolidate without first running search term reports** to understand if they're capturing different traffic patterns. Flag for P4 monitoring.

### P4 — Monitor Only (2 items)
- **Re-run search term reports in 1-2 days** — The 30d campaign and 14d search term reports were stuck today. Need this data to identify specific wasteful terms in the unprotected campaigns, especially what terms campaigns 4-6 are spending on that campaigns 1-3 have already negated.
- **Evaluate ASIN overlap** — Each campaign has different ASIN sets (18-41). May want to standardize which ASINs are in which campaigns. Needs more data before acting.

### Dependencies
- Item 2 depends on Item 1: same approach, just applied to 2 more campaigns
- Item 5 depends on search term data from P4

---

## Your Call

**5 actions identified across 4 priorities.**

| Option | Description |
|--------|-------------|
| **Approve all P1** | Execute 2 critical items — copy negatives to 3 unprotected campaigns |
| **Approve P1 + P2** | Execute 4 items — negatives + ASIN cleanup + budget right-sizing |
| **Approve specific** | "approve 1, 3" (by item number) |
| **Modify** | "change item 4 budget to X" (I'll adjust and confirm) |
| **Save brief only** | No API changes — save analysis for reference |

**Execution mode:**
| Mode | Description |
|------|-------------|
| **Step-by-step** (default) | I confirm each action before executing, show result, then ask about next |
| **Auto-execute** | I run all approved items in sequence, report results at the end |

**Note on Item 1+2 (negative keyword copy):** This involves applying 200-400+ negative keywords per campaign across 3 campaigns. I'll batch them in groups of 100 per API call. The negatives I'll copy are the ENABLED NEGATIVE_EXACT terms that appear in at least 2 of the 3 mature campaigns (highest confidence). Want me to proceed?
