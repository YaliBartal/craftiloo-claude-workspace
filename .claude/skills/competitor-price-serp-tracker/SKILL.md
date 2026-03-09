---
name: competitor-price-serp-tracker
description: Weekly competitive intelligence -- scrapes competitor ASINs for price/BSR/reviews and tracks SERP positions for category keywords
triggers:
  - competitor tracker
  - competitor check
  - weekly competitors
  - competitor serp
  - price tracker
  - competitive intel
  - competitor scan
output_location: outputs/research/competitor-tracker/
cadence: weekly
---

# Competitor Price & SERP Tracker

**USE WHEN** user says: "competitor tracker", "competitor check", "weekly competitors", "competitive intel", "price tracker", "SERP tracker", "competitor scan"

**Cadence:** Weekly. Check `agent-state.json > last_competitor_tracker` before running. If <7 days since last run, tell the user and ask if they want to force-run.

---

## BEFORE YOU START -- Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/competitor-price-serp-tracker/LESSONS.md`
2. Check **Known Issues** -- plan around these
3. Check **Repeat Errors** -- if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

A **weekly competitive intelligence scan** that answers: "What are competitors doing that I need to respond to?"

Two data collection phases:
1. **Product scrape** -- All tracked competitor ASINs: price, BSR, reviews, rating, availability, deals
2. **SERP scrape** -- Top 10 keywords per category: who's ranking where on each keyword

Then: compare WoW, generate alerts, write PPC agent flags, produce a brief.

**Time saved:** Replaces manual competitor checks (~2 hrs/week)
**Token budget:** <80K tokens, <10 minutes execution
**Apify cost:** ~$4-5 per run

---

## Operating Rules

1. **Never alert on first run.** First run is baseline capture only. Brief says "Baseline captured -- alerts begin next week."
2. **Compare WoW, not absolute.** All deltas are vs last week's snapshot, not vs some fixed baseline.
3. **Unknown ASINs are flagged, not auto-added.** New ASINs found in SERP top 10 go to `unassigned_asins` in config for user review.
4. **Deduplicate before scraping.** Same ASIN in multiple categories = 1 scrape, tagged to all categories. Same keyword across categories = 1 SERP scrape, results tagged to all applicable categories.
5. **Flag expiry = 14 days.** If not renewed by next weekly run, competitive flags auto-expire.
6. **Cost cap.** If estimated Apify cost exceeds $8, log warning and suggest reducing keyword count.
7. **Always update agent-state.json** with `last_competitor_tracker` timestamp and `competitive_flags` section after every run.
8. **Always update portfolio tracker files** with `competitive_context` section for affected portfolios.

---

## Data Sources

| Source | Tool | What It Provides |
|--------|------|------------------|
| **Apify product scraper** | `run_actor` with `saswave~amazon-product-scraper` | Price, BSR, reviews, rating, availability per ASIN |
| **Apify SERP scraper** | `run_actor` with `axesso_data~amazon-search-scraper` | Search result positions for keywords (top 48) |
| **Config file** | Read `context/competitor-config.json` | ASINs, keywords, thresholds, category mappings |
| **Previous snapshot** | Read `outputs/research/competitor-tracker/snapshots/` | Last week's data for WoW comparison |
| **PPC agent state** | Read/write `outputs/research/ppc-agent/state/agent-state.json` | Cadence tracking + competitive flags |

---

## Step-by-Step Process

### Step 1: Load Config + Previous Data

1. Read `context/competitor-config.json` -- get all ASINs, keywords, thresholds
2. Read most recent file in `outputs/research/competitor-tracker/snapshots/` (last week's product data)
3. Read most recent file in `outputs/research/competitor-tracker/serp/` (last week's SERP data)
4. Read `outputs/research/competitor-tracker/trends.json` (rolling 12-week summary)
5. Read `outputs/research/ppc-agent/state/agent-state.json` (for cadence check + flag writing later)
6. Build deduplicated ASIN list (all `competitor_asins` across categories + `uncategorized_asins`)
7. Build deduplicated keyword list (all `keywords` across categories, noting which categories each keyword belongs to)

### Step 2: Scrape Competitor Product Data

1. Batch deduplicated ASINs into groups of 5
2. For each batch, call Apify MCP `run_actor` with `saswave~amazon-product-scraper`:
   - Input: `{"asins": ["B08T5QC9FS", ...], "amazon_domain": "www.amazon.com"}`
3. Poll with `get_run_status` until complete
4. Fetch results with `get_run_dataset`
5. Extract per ASIN:
   - `price` (float or null)
   - `bestsellerRanks` (array -- first entry = main BSR, second = subcategory)
   - `stars` (rating)
   - `reviewsCount`
   - `availability` (In Stock / Out of Stock)
   - `title`
   - Deal/coupon badges (if available in response)
6. Map each ASIN back to its category(ies) from config

**Launch Steps 2 and 3 in parallel** -- kick off all Apify runs for both product and SERP scrapes, then poll all together.

### Step 3: Scrape SERP Keyword Data

1. For each deduplicated keyword, call Apify MCP `run_actor` with `axesso_data~amazon-search-scraper`:
   - Input: `{"input": [{"keyword": "embroidery kit for kids", "country": "US"}]}`
2. Poll and fetch results
3. For each keyword result, classify every ASIN in the results:
   - **our_product** -- ASIN is in any category's `our_asins`
   - **tracked_competitor** -- ASIN is in any category's `competitor_asins`
   - **unknown** -- ASIN not in either set
4. For unknowns in top 10 positions: flag as potential new competitor
5. Record per keyword: our positions, competitor positions, unknown top-10 ASINs
6. Key fields from axesso results: `searchResultPosition` (0-indexed), `productDescription` (title), `price`, `productRating`, `countReview`, `sponsored` (bool)

### Step 4: Compare Week-over-Week + Generate Alerts

**If no previous snapshot exists (first run):** Skip this step entirely. Mark all data as baseline.

**If previous snapshot exists:**

For each product ASIN, compute:
- `price_change_pct` = (new_price - old_price) / old_price * 100
- `bsr_main_change_pct` = (new_bsr - old_bsr) / old_bsr * 100 (negative = improved)
- `reviews_added` = new_reviews - old_reviews
- `rating_change` = new_rating - old_rating
- `availability_changed` = new != old
- `deal_badge_new` = has deal now but didn't last week

For each keyword, compute position deltas per competitor.

Apply alert thresholds from config:

| Alert Type | Condition | Severity |
|------------|-----------|----------|
| PRICE_DROP | price_change_pct < -price_drop_pct | HIGH if >20%, MEDIUM if 10-20% |
| PRICE_INCREASE | price_change_pct > +price_increase_pct | LOW |
| REVIEW_SURGE | reviews_added > review_surge_per_week | MEDIUM |
| BSR_SURGE | bsr improved > bsr_improvement_pct | HIGH |
| BSR_DECLINE | bsr declined > bsr_decline_pct | LOW |
| NEW_ENTRANT | unknown ASIN in top N SERP | MEDIUM |
| SERP_JUMP | competitor jumped > serp_position_jump positions | MEDIUM |
| DEAL_DETECTED | new deal/coupon badge | HIGH |
| OOS_DETECTED | competitor went out of stock | LOW |
| RATING_DROP | rating dropped > rating_drop | LOW |

Sort alerts: HIGH first, then MEDIUM, then LOW.

### Step 5: Build Weekly Snapshot + Update Trends

1. Write `outputs/research/competitor-tracker/snapshots/YYYY-MM-DD-snapshot.json`
   - Contains: scrape_metadata, products (all ASIN data), wow_deltas, alerts, new_asins_detected
2. Write `outputs/research/competitor-tracker/serp/YYYY-MM-DD-serp.json`
   - Contains: scrape_metadata, keyword_results (positions per keyword)
3. Read `trends.json`, append this week's data:
   - Per-category summaries (avg price, avg BSR, avg SERP position, alert counts)
   - Per-ASIN weekly data points (price, bsr, reviews, rating)
4. If more than 12 weeks of data, drop the oldest week
5. Write updated `trends.json`

### Step 6: Write Competitive Flags to PPC Agent State

1. Read current `outputs/research/ppc-agent/state/agent-state.json`
2. Update `last_competitor_tracker` timestamp
3. Clear expired flags from `competitive_flags.flags` (expiry < today)
4. For each HIGH/MEDIUM alert:
   - Create or renew flag entry with 14-day expiry
   - Map to affected portfolio_slugs via config
   - Set `recommended_action` based on alert type
5. Update `competitive_flags.summary`
6. Write updated `agent-state.json`
7. For each affected portfolio, read its tracker file and update `competitive_context` section:
   - `active_flags` -- list of relevant flags
   - `price_landscape` -- our price vs competitor avg/min/max
   - `serp_health` -- our avg position vs competitor avg position

### Step 7: Generate Weekly Brief

Write `outputs/research/competitor-tracker/briefs/YYYY-MM-DD-weekly-brief.md`

**Brief sections:**

1. **Header** -- date, competitor count, keyword count, categories
2. **Alerts** -- HIGH and MEDIUM alerts in tables
3. **Price Landscape by Category** -- our price vs competitor avg/min, WoW trend arrows
4. **SERP Position Summary** -- our avg position vs competitor avg per category
5. **Biggest Movers** -- top competitors with largest WoW changes (price, BSR, reviews)
6. **New ASINs Detected** -- unknown ASINs found in top 10, with keywords and positions
7. **PPC Flags Written** -- summary of flags pushed to agent state
8. **Footer** -- data sources, Apify cost, runtime

### Step 8: Post Notifications

Read `.claude/skills/notification-hub/SKILL.md` → "Recipe: competitor-price-serp-tracker".
Follow those instructions to post a summary to Slack.
If Slack MCP is unavailable, skip and note in run log.

### Step 9: Update LESSONS.md

Standard post-run logging:
- Run date, goals, result (success/partial/fail)
- What worked, what didn't
- Any new issues discovered
- Apify cost and runtime

---

## Output File Schemas

See plan file for detailed JSON schemas:
- `snapshots/YYYY-MM-DD-snapshot.json` -- product data + WoW deltas + alerts
- `serp/YYYY-MM-DD-serp.json` -- keyword positions per ASIN
- `trends.json` -- rolling 12-week summary + per-ASIN time series

---

## PPC Agent Integration

### Flags written to agent-state.json

```json
"competitive_flags": {
  "last_updated": "YYYY-MM-DD",
  "flags": [
    {
      "id": "cf-001",
      "type": "PRICE_UNDERCUT",
      "severity": "HIGH",
      "portfolio_slugs": ["cross-embroidery-kits"],
      "category": "cross-stitch-kids",
      "competitor_asin": "B08T5QC9FS",
      "competitor_brand": "Pllieay",
      "message": "Pllieay undercut by 15%. Consider bid defense.",
      "recommended_action": "REVIEW_BIDS",
      "created": "YYYY-MM-DD",
      "expires": "YYYY-MM-DD+14d",
      "status": "active"
    }
  ],
  "summary": {
    "total_active_flags": 3,
    "portfolios_affected": ["cross-embroidery-kits", "fairy-family"]
  }
}
```

### Downstream skill consumption

| Skill | What It Reads | How It Uses It |
|-------|---------------|----------------|
| ppc-daily-health | `competitive_flags` (active) | "Competitive Alert" line in health brief |
| ppc-bid-recommender | flags with `REVIEW_BIDS` | Bid defense logic |
| ppc-portfolio-action-plan | portfolio `competitive_context` | Price landscape in deep dives |
| ppc-monthly-review | `trends.json` 12-week data | Monthly competitive narrative |

---

## Efficiency Standards

| Target | Limit |
|--------|-------|
| Token budget | <80K per run |
| Apify cost | ~$4-5 per run |
| Execution time | <10 minutes |
| File count per run | 3 new files (snapshot + serp + brief) + 2 updates (trends + agent-state) |
| Cadence | Weekly |
