# Shield All Portfolio — Deep Dive Brief
**Date:** 2026-03-05
**Portfolio ID:** 226460450341570
**Stage:** General (Defensive/Shield)

---

## Summary

First-ever deep dive on the Shield All portfolio. This is a **defensive portfolio** — Product Targeting campaigns bid on Craftiloo's own ASINs to prevent competitor ads from appearing on our product pages. Also includes a brand defense campaign for the "craftiloo" brand name.

**30d Baseline (pre-changes):** $899 spend, $3,245 sales, **27.7% ACoS**, 141 orders, 13.0% CVR

---

## Portfolio Structure

| Campaign | Type | Status (before) | Budget | 30d Spend | 30d ACoS | TOS-IS |
|----------|------|-----------------|--------|-----------|----------|--------|
| shield product - cross stitch kits | PT (ASIN_SAME_AS) | ENABLED | $8/d | $410 | 34.5% | **7.5%** |
| shield product - latch hook kits | PT (ASIN_SAME_AS) | ENABLED | $8/d | $251 | 25.4% | 16.3% |
| shield brand name - manual and broad | Keyword (craftiloo) | ENABLED | $10/d | $185 | 20.4% | 89-99% |
| shield product - latch hook pillow | PT (ASIN_SAME_AS) | ENABLED | $10/d | $53 | 33.0% | 11-19% |
| shield product - bunny knitting | PT | **PAUSED** | $2/d | — | — | — |
| shield product - embroidery for kids | PT | **PAUSED** | $1/d | — | — | — |
| shield product - dessert sewing | PT | **PAUSED** | $10/d | — | — | — |
| shield product - fairy sewing exact | PT | **PAUSED** | $2/d | — | — | — |
| shield product - mini fuse beads | PT | **PAUSED** | $2/d | — | — | — |
| shield product - cross and embroidery | PT | **PAUSED** | $15/d | — | — | — |
| shield product - cat knitting | PT | **PAUSED** | $7/d | — | — | — |

## Key Findings

1. **Cross stitch kits TOS-IS at 7.5%** — competitors own 92.5% of our product page
2. **7 campaigns paused** — every product without an active shield is defenseless
3. **Brand defense excellent** — "craftiloo" EXACT and PHRASE getting 89-99% TOS-IS
4. **Brand BROAD keyword paused** — leaving gap in brand coverage
5. **Latch hook pillow TOS-IS 11-19%** — low bids not winning page placement

## Actions Taken (14 API calls, 0 errors)

### Batch 1: Adjust ENABLED Campaigns
| Action | Before | After |
|--------|--------|-------|
| Cross stitch kits TOS | 10% | **47%** |
| Latch hook kits TOS | 85% | **47%** |
| Brand BROAD keyword | PAUSED | **ENABLED** ($0.56) |
| Latch hook pillow target bids | $0.40 / $0.46 | **$0.52 / $0.58** |

### Batch 2: Re-enable 7 PAUSED Campaigns (Conservative)
All at **$2/day budget** with **50%+ TOS reductions**:

| Campaign | Original TOS | New TOS | Other Modifiers |
|----------|-------------|---------|-----------------|
| Bunny knitting | 101% | **47%** | — |
| Embroidery for kids | 74% (PP 77%) | **37%** (PP 37%) | — |
| Dessert sewing | 204% | **97%** | — |
| Fairy sewing exact | 111% | **53%** | — |
| Mini fuse beads | 208% (ROS 56%, PP 26%) | **97%** (ROS 27%, PP 13%) | — |
| Cross and embroidery | 121% | **57%** | — |
| Cat knitting | 73% | **37%** | — |

### Batch 3: Reduce High Bids
| Campaign | Target | Before | After |
|----------|--------|--------|-------|
| Dessert sewing | 394529267573327 | $0.93 | **$0.47** |
| Cross-embroidery | 450665148739845 (B0F8QZZQQM) | $0.71 | **$0.43** |
| Cat knitting | 363833412264890 | $0.68 | **$0.43** |

## Safeguards in Place
- All re-enabled campaigns capped at **$2/day** (max burn: $14/day total)
- **50%+ TOS cuts** from original values
- **High bids capped** at $0.43-$0.47
- **7-day review gate** (2026-03-12): ACoS >45% on any re-enabled campaign → flag for pause

## Pending Actions
| ID | Priority | Action | Due |
|----|----------|--------|-----|
| sa-001 | P1 | 7-day review: check 7 re-enabled campaigns (ACoS >45% → pause) | Mar 12 |
| sa-002 | P2 | Verify cross stitch kits TOS-IS improved from 7.5% | Mar 12 |
| sa-003 | P3 | Check brand BROAD keyword capturing additional searches | Mar 12 |
