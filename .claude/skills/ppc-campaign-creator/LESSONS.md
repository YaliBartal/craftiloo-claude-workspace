# PPC Campaign Creator — Lessons Learned

## Run Log

*(New entries go at the TOP)*

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
