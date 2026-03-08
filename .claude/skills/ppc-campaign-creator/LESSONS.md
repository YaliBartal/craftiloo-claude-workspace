# PPC Campaign Creator — Lessons Learned

## Run Log

*(New entries go at the TOP)*

### Run: 2026-03-05 (Biggie Beads — 2 MK campaigns from PROMOTE candidates)
**Result:** Success

**Campaigns created:** 2
**Keywords added:** 4
**Product ads:** 2 (B07D6D95NG / O9-70DP-C5J6)

**What happened:**
- Created 2 MK EXACT campaigns from search term harvest PROMOTE candidates
- Campaign 1: "biggie beads - SPM MK large perler TOS" — "large perler beads" $0.78 + "big perler beads" $0.83, TOS 143%, PP 31%, ROS 14%, $12/d
- Campaign 2: "biggie beads - SPM MK large fuse TOS" — "large fuse beads" $0.72 + "jumbo perler beads" $0.68, TOS 137%, PP 27%, ROS 12%, $10/d
- User chose NOT to negate these terms from broad/auto campaigns — wants both running simultaneously

**What didn't work:**
- First campaign create attempt failed with HTTP 400 — `startDate` format must be `YYYY-MM-DD` (ISO), NOT `YYYYMMDD`. Fixed on retry.
- Product ad creation failed initially — Amazon Ads API v3 requires `sku` field alongside `asin`. Had to look up SKU from Seller Board 7d report.

**Lesson learned:**
- **startDate format is `YYYY-MM-DD`** — not `YYYYMMDD`. Amazon Ads API rejects the compact format.
- **Product ads need SKU field** — `manage_sp_product_ads` requires `{"asin": "...", "sku": "..."}`, not just ASIN. Get SKU from Seller Board 7d report or FBA inventory.
- **PP/ROS at creation is fine when user specifies it.** Known Issue #3 (TOS-only at creation) is a default rule, but user explicitly requested PP/ROS modifiers — follow user intent.
- **User may choose not to isolate traffic.** Don't assume negatives should be applied — always ask.

**Tokens/cost:** ~15K tokens (continuation from deep dive session)

---

## Known Issues

### 1. RULE: Never pause a campaign based on a single week of zero conversions
**Impact:** HIGH — Premature pausing kills campaigns that may just be in a rough patch.
**Rule:** Always check a longer timeframe (minimum 30 days, ideally 60 days) before recommending a pause. Only recommend pausing if the campaign shows sustained poor performance over the longer timeframe.

### 2. RULE: Never use round/organized bid amounts
**Impact:** MEDIUM — Amazon's algorithm may treat round numbers differently. Always use irregular amounts (e.g., $0.73 not $0.70, -31% not -30%).

### 3. RULE: TOS-only placement bids at creation
**Impact:** HIGH — Only set PLACEMENT_TOP modifier when creating campaigns. Never add Product Pages or Rest of Search modifiers at creation time. Those are added later by the Bid Recommender based on performance data.

---

## Repeat Errors

*(Track errors that happen more than once)*

---

## Resolved Issues

*(Issues that have been fixed — keep for reference)*
