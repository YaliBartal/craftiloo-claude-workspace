---
name: customer-review-analyzer
description: Scrapes and analyzes Amazon reviews for Craftiloo products and competitors, producing sentiment analysis, competitive insights, and actionable recommendations
triggers:
  - review analysis
  - analyze reviews
  - customer reviews
  - review insights
  - what are customers saying
  - review check
  - competitor reviews
  - sentiment analysis
output_location: outputs/research/review-analysis/
---

# Customer Review Analyzer

**USE WHEN** user says: "review analysis", "analyze reviews", "customer reviews", "review insights", "what are customers saying", "review check", "competitor reviews", "sentiment analysis"

---

## ⚠️ BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/customer-review-analyzer/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"⚠️ Repeat issue (×N): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

Scrapes Amazon product reviews via Apify and produces actionable intelligence from customer feedback across two modes:

1. **Single Product Deep Dive** — Analyzes one Craftiloo product + its top 3 competitors in depth
2. **Category Scan** — Quick sentiment scan across all Craftiloo products + competitors in a category

**Core outputs:**
- Complaint and praise theme extraction (grouped, quantified, with example quotes)
- Competitive review gap analysis (our strengths vs competitor strengths)
- Product improvement suggestions ranked by review frequency
- Listing optimization suggestions (customer language for bullets/images)
- PPC keyword insights (natural language customers use)
- Quality/safety flags (critical for kids products)
- Trend tracking via JSON snapshots (rating drift, review velocity, theme changes)

**Complements other skills:**
- **Listing Creator / Product Listing Development** — Review language feeds bullet copy and image text
- **Weekly PPC Analysis** — Customer vocabulary identifies new keyword opportunities
- **Negative Keyword Generator** — Review themes reveal irrelevant traffic patterns

---

## Organization & Efficiency Standards

### File Organization

```
outputs/research/review-analysis/
├── briefs/                # Analysis reports (what user reads)
├── data/                  # Raw review data (JSON from Apify)
│   └── YYYY-MM-DD/        # Date-stamped raw data folders
├── snapshots/             # Historical metrics for trend tracking
│   └── {slug}-snapshot-YYYY-MM-DD.json
└── README.md              # Folder guide
```

### Naming Conventions (STRICT)

| File Type | Format | Example |
|-----------|--------|---------|
| **Deep dive report** | `{product-slug}-review-analysis-YYYY-MM-DD.md` | `cross-stitch-girls-review-analysis-2026-02-20.md` |
| **Category scan report** | `{category-slug}-category-scan-YYYY-MM-DD.md` | `latch-hook-category-scan-2026-02-20.md` |
| **Raw review data** | `reviews-{ASIN}-YYYY-MM-DD.json` | `reviews-B08DDJCQKF-2026-02-20.json` |
| **Snapshot** | `{slug}-snapshot-YYYY-MM-DD.json` | `cross-stitch-girls-snapshot-2026-02-20.json` |

### Efficiency Targets

- **< 80K tokens** per analysis
- **< $0.20 Apify cost** per run
- **< 5 minutes** execution time
- **Max 50 reviews per ASIN** (most recent, sorted by date)
- **Max 5 ASINs per Apify call** (batch limit)

### Forbidden Practices

- Do NOT scrape reviews for ASINs not in `context/hero-products.md` or `context/competitors.md`
- Do NOT exceed 50 reviews per ASIN (cost and token control)
- Do NOT skip the context file check before scraping
- Do NOT combine reviews from different date ranges in one analysis
- Do NOT treat individual 1-star reviews as systemic issues without frequency data (3+ mentions = theme)
- Do NOT auto-flag quality issues without confirming them against `context/products.md` kit contents
- Do NOT run Category Scan mode on more than 8 ASINs total per run (cost ceiling)

---

## Input

### Required

1. **Mode selection** — Ask user: "Single Product Deep Dive or Category Scan?"
2. **Product or category selection:**
   - **Deep Dive:** Which product? (name, SKU, or ASIN from hero-products.md)
   - **Category Scan:** Which category? (Cross Stitch, Embroidery Kids, Embroidery Adults, Sewing, Latch Hook, Knitting, Fuse Beads, Lacing Cards, Needlepoint)

### Loaded Automatically

3. **Context files:**
   - `context/hero-products.md` — Our 13 hero product ASINs with specs
   - `context/products.md` — Full 76-product catalog with contents
   - `context/competitors.md` — 72 competitor ASINs by category with market context
   - `context/search-terms.md` — Tracked keywords by category
   - `context/business.md` — Brand context, target audience, competitor list

### How to Start

When skill triggers:
1. Ask: **"Single Product Deep Dive or Category Scan?"**
2. Based on mode:
   - **Deep Dive:** "Which product? (name, SKU, or ASIN)" then auto-select top 3 competitors from `context/competitors.md`
   - **Category Scan:** "Which category?" then list the relevant categories with product counts
3. Confirm the ASINs that will be scraped and estimated Apify cost before proceeding
4. Ask: **"Any specific concerns you want me to look for in reviews?"** (optional — adds custom theme tracking)

---

## Process

### Step 1: Load Context & Identify ASINs

1. Load `context/hero-products.md` — get our product ASINs and specs
2. Load `context/competitors.md` — get competitor ASINs for the selected product/category
3. Load `context/products.md` — get detailed kit contents (for verifying complaints against actual product)
4. Load `context/business.md` — get target audience info (grandparents buying for kids 6-12)
5. Load `context/search-terms.md` — get tracked keywords (for PPC keyword extraction later)

**Build ASIN list based on mode:**

| Mode | Our ASINs | Competitor ASINs | Total Max |
|------|-----------|------------------|-----------|
| **Deep Dive** | 1 (selected product) | Top 3 from `competitors.md` for that category (by estimated market share) | 4 |
| **Category Scan** | All hero products in that category (from `hero-products.md`) | Top 1-2 competitors per product (from `competitors.md`) | 8 max |

6. Show user the ASIN list and estimated cost:
   - Formula: {number of ASINs} x ~$0.03 per ASIN (estimated Apify review scraping cost)
   - Example: "4 ASINs x $0.03 = ~$0.12 estimated cost"
7. Confirm before proceeding

### Step 2: Load Previous Snapshot (for Trend Comparison)

1. Glob for `outputs/research/review-analysis/snapshots/{slug}-snapshot-*.json`
2. If snapshots exist:
   - Load the **most recent** snapshot
   - Note the date and how many days ago it was
   - Store previous data for trend comparison in Step 8
3. If no snapshots:
   - Note this is the first run (no trend comparison available)
   - First run will establish the baseline

### Step 3: Scrape Reviews via Apify

**Primary actor:** `junglee/amazon-reviews-scraper`

**Input format per batch:**
```json
{
  "productUrls": [
    { "url": "https://www.amazon.com/dp/{ASIN}" }
  ],
  "maxReviews": 50,
  "sort": "recent",
  "proxy": {
    "useApifyProxy": true,
    "apifyProxyGroups": ["RESIDENTIAL"]
  }
}
```

**Fallback actor** (if primary fails): `epctex/amazon-reviews-scraper`

**Fallback input:**
```json
{
  "startUrls": [
    "https://www.amazon.com/product-reviews/{ASIN}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&sortBy=recent"
  ],
  "maxItems": 50
}
```

**Batching rules:**
- Max 5 ASINs per Apify call
- Run in async mode: start run, then poll for results
- On timeout after 3 minutes: STOP, use data collected so far
- On actor failure: try fallback actor ONCE, then skip that ASIN and note in report

**Expected output fields per review:**

| Field | What It Contains | Used For |
|-------|------------------|----------|
| `reviewTitle` | Review headline | Theme extraction |
| `reviewBody` | Full review text | Sentiment analysis, theme extraction, quote extraction |
| `stars` | 1-5 rating | Sentiment distribution |
| `reviewDate` | Date posted | Recency filtering, trend tracking |
| `isVerifiedPurchase` | Boolean | Weight verified reviews higher |
| `reviewImages` | Array of image URLs | Photo review flag |
| `helpfulVotes` | Number | Weight heavily-voted reviews higher |

3. Save raw review data to: `outputs/research/review-analysis/data/YYYY-MM-DD/reviews-{ASIN}-YYYY-MM-DD.json`

### Step 4: Calculate Sentiment Distribution

For EACH scraped ASIN:

1. **Count reviews by star rating:**
   - 5-star count and percentage
   - 4-star count and percentage
   - 3-star count and percentage
   - 2-star count and percentage
   - 1-star count and percentage

2. **Calculate aggregate metrics:**

   | Metric | Formula |
   |--------|---------|
   | **Average rating** | Weighted average of star ratings |
   | **Satisfaction rate** | (5-star + 4-star) / total reviews |
   | **Dissatisfaction rate** | (1-star + 2-star) / total reviews |
   | **Photo review %** | Reviews with images / total reviews |
   | **Verified purchase %** | Verified purchases / total reviews |
   | **Avg helpful votes** | Sum of helpful votes / total reviews |

3. **Flag anomalies:**
   - Dissatisfaction rate > 20%: FLAG as quality concern
   - Photo review % > 30%: NOTE (photo reviews tend to be more detailed and influential)
   - Verified purchase % < 60%: NOTE (potential fake review concern)

### Step 5: Extract Review Themes

For EACH ASIN, read every review body and classify mentions into these theme categories. A single review can match multiple themes.

#### 5a. Complaint Themes (from 1-3 star reviews, and negative mentions in 4-star reviews)

| Theme Category | What to Look For | Keywords/Signals |
|----------------|------------------|------------------|
| **Missing/incomplete contents** | Items advertised but not in kit | "missing", "didn't include", "supposed to come with", "no needles", "short on" |
| **Instruction quality** | Confusing, unclear, too few steps | "confusing", "hard to follow", "no instructions", "unclear", "couldn't figure out" |
| **Material quality** | Thin fabric, tangling thread, dull colors | "cheap", "thin", "flimsy", "tangled", "faded", "broke", "ripped" |
| **Age appropriateness** | Too hard/easy for stated age range | "too hard for", "too easy", "frustrated", "needs adult help", "couldn't do it alone" |
| **Safety concerns** | Sharp edges, small parts, toxic materials | "sharp", "poked", "small parts", "choking", "hurt", "cut" |
| **Packaging/unboxing** | Damaged in shipping, poor presentation | "damaged", "crushed", "cheap packaging", "fell apart", "not gift-worthy" |
| **Value/price** | Overpriced for contents, not worth it | "overpriced", "not worth", "expected more", "too expensive", "ripoff" |
| **Size/scale** | Smaller/larger than expected | "tiny", "smaller than expected", "bigger than I thought", "can't tell from photos" |
| **Completion time** | Takes too long / too short | "took forever", "hours", "finished too quickly", "not enough to do" |
| **Durability** | Doesn't last, falls apart | "fell apart", "broke", "didn't last", "fragile" |

#### 5b. Praise Themes (from 4-5 star reviews)

| Theme Category | What to Look For | Keywords/Signals |
|----------------|------------------|------------------|
| **Gift success** | Gift-buying satisfaction, recipient reaction | "loved it", "perfect gift", "granddaughter loved", "birthday gift", "Christmas" |
| **Engagement/entertainment** | Kept child engaged, screen-free | "kept busy", "hours of fun", "screen-free", "occupied", "loved doing it" |
| **Ease of use** | Beginner-friendly, easy instructions | "easy to follow", "beginner", "figured it out", "clear instructions" |
| **Complete kit** | Everything included, nothing extra needed | "everything you need", "complete", "all included", "no extra purchases" |
| **Quality materials** | Good thread, sturdy components | "great quality", "sturdy", "good materials", "well-made" |
| **Educational value** | Learning skills, patience, fine motor | "learned", "fine motor", "patience", "educational", "new skill" |
| **Cute/appealing designs** | Design praise | "adorable", "cute", "love the designs", "beautiful" |
| **Repeat purchase** | Buying more, recommending | "buying again", "ordered another", "recommended to", "second time" |
| **Packaging/presentation** | Gift-worthy packaging | "beautiful box", "gift ready", "nice packaging", "presentation" |
| **Finished result** | Pride in completed project | "turned out great", "looks amazing", "proud of", "display" |

#### 5c. Feature Requests / "I wish" mentions

Scan for: "I wish", "would be nice if", "only complaint is", "suggestion", "needs", "should include", "if only"

#### 5d. Competitor Comparison Mentions

Scan for: "better than", "worse than", "compared to", "unlike [brand]", "switched from", competitor brand names from `context/business.md`

#### 5e. Gift-ability Mentions (critical for Craftiloo's buyer persona)

Scan for: "gift", "birthday", "Christmas", "grandchild", "grandson", "granddaughter", "niece", "nephew", "stocking stuffer", "party favor"

#### 5f. Age Appropriateness Mentions

Scan for: specific ages ("my 6 year old", "8 year old"), age range opinions ("too young", "too old", "perfect age"), grade level mentions ("first grader")

#### 5g. Photo Review Insights

Separately flag reviews that include images. These tend to be longer, more detailed, and show the actual finished result. Extract the review body from these for higher-weight analysis.

**For each theme, record:**
- Theme name
- Frequency count (how many reviews mention this)
- Percentage of total reviews
- 2-3 representative verbatim quotes (keep short, max 1 sentence each)
- Whether it came from verified purchase
- Average star rating of reviews mentioning this theme

**Minimum threshold for a theme to appear in the report:** 3+ mentions (2+ for safety/quality themes)

### Step 6: Competitive Review Gap Analysis (Deep Dive Mode Only)

Compare our product's review themes against each competitor's review themes:

**6a. Our Advantages (competitor complaints we DON'T have)**

For each competitor complaint theme:
- Check if we have the SAME complaint theme
- If we do NOT: This is our advantage — customers complain about this on competitor products but not ours
- Record: Competitor ASIN, complaint theme, frequency on competitor, our frequency (0 or low)

**6b. Our Gaps (competitor praise themes we DON'T have)**

For each competitor praise theme:
- Check if we have the SAME praise theme
- If we do NOT (or significantly less frequent): This is a gap — customers praise competitors for something we're not getting praised for
- Record: Competitor ASIN, praise theme, frequency on competitor, our frequency

**6c. Head-to-Head Theme Table**

Build a comparison matrix:

| Theme | Our Product | Competitor 1 | Competitor 2 | Competitor 3 | Advantage |
|-------|------------|-------------|-------------|-------------|-----------|
| {theme} | {sentiment + freq} | {sentiment + freq} | {sentiment + freq} | {sentiment + freq} | {who wins} |

### Step 7: Generate Actionable Outputs

#### 7a. Product Improvement Suggestions

Rank by complaint frequency (highest first):

| Priority | Suggestion | Based On | Frequency | Example Quote |
|----------|-----------|----------|-----------|---------------|
| P1 | {specific suggestion} | {complaint theme} | X mentions (Y%) | "{quote}" |

Rules:
- Only include suggestions backed by 3+ review mentions
- Cross-reference against `context/products.md` — if the complaint references something NOT in the kit, note it as "possible listing confusion" rather than a product issue
- Separate into: **Product changes** (manufacturing) vs **Listing fixes** (communication)

#### 7b. Listing Optimization Suggestions

Extract the exact natural language customers use in positive reviews:

| Customer Language | Where to Use | Frequency | Why |
|-------------------|-------------|-----------|-----|
| "{exact phrase from review}" | {Title/Bullet #/Image text} | {X} reviews | {rationale} |

Priority: Words/phrases that appear in 5+ positive reviews are highest priority for listing copy.

#### 7c. PPC Keyword Insights

From review text, extract search-relevant phrases customers naturally use:
- Cross-reference against `context/search-terms.md` — mark as "already tracked" or "new opportunity"
- Focus on phrases that indicate purchase intent: "I was looking for", "searched for", "wanted a", "needed a"

#### 7d. Customer Service FAQ Patterns

From question-type reviews and complaints, extract the top recurring questions:
- "Does it include...?"
- "Is it suitable for age...?"
- "How long does it take?"
- These map directly to FAQ answers and listing bullet content

#### 7e. Quality Control Flags

Any safety or quality mention that appears 3+ times (or any safety mention involving children):
- Flag severity: CRITICAL (safety), HIGH (quality defect), MEDIUM (cosmetic/minor)
- Flag includes: theme, frequency, example quotes, recommended action

### Step 8: Trend Comparison (if Previous Snapshot Exists)

If a previous snapshot was loaded in Step 2:

1. **Rating trend:**
   - Current average rating vs previous
   - Direction: Improving / Stable / Declining
   - Point change (e.g., 4.5 -> 4.4 = -0.1)

2. **Review velocity:**
   - Current total review count vs previous
   - New reviews since last snapshot
   - Pace: accelerating / steady / slowing

3. **Sentiment shift:**
   - Current satisfaction rate vs previous
   - Current dissatisfaction rate vs previous
   - Direction and magnitude

4. **Theme changes:**
   - New complaint themes that did not appear in previous snapshot
   - Complaint themes that resolved (appeared before, gone now)
   - Growing complaints (frequency increased)
   - Growing praise (frequency increased)

5. **Competitor movement:**
   - Competitor rating changes
   - Competitor review velocity changes
   - New competitor complaint themes (our opportunities)

If no previous snapshot: Note "First analysis — no trend data. This run establishes the baseline."

### Step 9: Save Snapshot

After generating the report:

1. Generate the snapshot JSON (see Snapshot JSON Format section)
2. Save to: `outputs/research/review-analysis/snapshots/{slug}-snapshot-YYYY-MM-DD.json`

### Step 10: Generate Report

Output the full analysis as a structured markdown report following the exact Output Format below.

Save to: `outputs/research/review-analysis/briefs/{slug}-review-analysis-YYYY-MM-DD.md` (deep dive) or `{slug}-category-scan-YYYY-MM-DD.md` (category scan)

### Step 11: Present Summary to User

After saving, present a concise summary:
- Mode run (Deep Dive / Category Scan)
- Products analyzed (count + names)
- Overall sentiment assessment (1 sentence)
- Top 3 actionable findings
- File location
- Trend note (if previous snapshot existed)

---

## Output Format

### Deep Dive Report Template

```markdown
# Review Analysis: {Product Name} — Deep Dive

**Date:** {YYYY-MM-DD}
**Product:** {Product name} ({ASIN})
**Category:** {Amazon category}
**Reviews Analyzed:** {X} ours + {Y} across {Z} competitors = {total} total
**Previous Snapshot:** {YYYY-MM-DD} (or "None — first run")

---

## Executive Summary

{2-3 sentences: Overall sentiment health, biggest finding, most urgent action. Be specific and blunt.}

**Sentiment Health:** {STRONG / HEALTHY / MIXED / CONCERNING / CRITICAL}
**Top Finding:** {1 sentence — the single most important insight}
**Most Urgent Action:** {1 sentence — what to do first}

---

## Sentiment Overview

### Our Product: {Product Name} ({ASIN})

| Metric | Value | vs Previous |
|--------|-------|-------------|
| Average Rating | {X.X} stars | {+/- X.X or "First run"} |
| Total Reviews (scraped) | {X} | — |
| Satisfaction Rate (4-5 star) | {X%} | {+/- X pp or "First run"} |
| Dissatisfaction Rate (1-2 star) | {X%} | {+/- X pp or "First run"} |
| Photo Review % | {X%} | — |
| Verified Purchase % | {X%} | — |

**Star Distribution:**

| Stars | Count | % |
|-------|-------|---|
| 5 star | {X} | {X%} |
| 4 star | {X} | {X%} |
| 3 star | {X} | {X%} |
| 2 star | {X} | {X%} |
| 1 star | {X} | {X%} |

### Competitor Comparison

| Product | ASIN | Avg Rating | Satisfaction % | Dissatisfaction % | Reviews Analyzed |
|---------|------|-----------|---------------|-------------------|-----------------|
| **{Our product}** | **{ASIN}** | **{X.X}** | **{X%}** | **{X%}** | **{X}** |
| {Competitor 1} | {ASIN} | {X.X} | {X%} | {X%} | {X} |
| {Competitor 2} | {ASIN} | {X.X} | {X%} | {X%} | {X} |
| {Competitor 3} | {ASIN} | {X.X} | {X%} | {X%} | {X} |

---

## Top Complaint Themes (Our Product)

| # | Theme | Frequency | % of Reviews | Avg Stars | Example Quote |
|---|-------|-----------|-------------|-----------|---------------|
| 1 | {theme} | {X} mentions | {X%} | {X.X} | "{verbatim quote}" |

**Quality/Safety Flags:**

| Severity | Theme | Frequency | Details | Action |
|----------|-------|-----------|---------|--------|
| {CRITICAL/HIGH/MEDIUM} | {theme} | {X} mentions | {detail} | {recommended action} |

---

## Top Praise Themes (Our Product)

| # | Theme | Frequency | % of Reviews | Avg Stars | Example Quote |
|---|-------|-----------|-------------|-----------|---------------|
| 1 | {theme} | {X} mentions | {X%} | {X.X} | "{verbatim quote}" |

**Gift-ability Mentions:**

| # | Context | Quote | Star Rating |
|---|---------|-------|-------------|
| 1 | {who buying for whom} | "{quote}" | {X} stars |

**Age Appropriateness Mentions:**

| # | Age/Range Mentioned | Sentiment | Quote |
|---|---------------------|-----------|-------|
| 1 | {age or range} | {Positive/Negative/Mixed} | "{quote}" |

---

## Feature Requests

| # | Request | Frequency | Example Quote |
|---|---------|-----------|---------------|
| 1 | {what customers want} | {X} mentions | "{quote}" |

---

## Competitive Review Gap Analysis

### Our Advantages (Competitor Complaints We Do NOT Have)

| # | Competitor | Their Complaint | Their Frequency | Our Status | Our Advantage |
|---|-----------|----------------|-----------------|------------|---------------|
| 1 | {name} ({ASIN}) | {complaint theme} | {X} mentions | Not present | {why this matters} |

### Our Gaps (Competitor Praise We Do NOT Have)

| # | Competitor | Their Praise | Their Frequency | Our Status | Gap to Close |
|---|-----------|-------------|-----------------|------------|-------------|
| 1 | {name} ({ASIN}) | {praise theme} | {X} mentions | {absent/low} | {what we could do} |

### Head-to-Head Theme Matrix

| Theme | Our Product | {Comp 1} | {Comp 2} | {Comp 3} | Winner |
|-------|------------|----------|----------|----------|--------|
| {theme} | {sentiment + freq} | {sentiment + freq} | {sentiment + freq} | {sentiment + freq} | {who wins} |

### Competitor Comparison Mentions in Reviews

| # | Direction | Quote | Source ASIN |
|---|-----------|-------|------------|
| 1 | {Better than / Worse than} {competitor} | "{quote}" | {ASIN reviewed} |

---

## Actionable Recommendations

### Product Improvements (Ranked by Review Frequency)

| Priority | Suggestion | Type | Frequency | Based On | Example Quote |
|----------|-----------|------|-----------|----------|---------------|
| P1 | {specific suggestion} | {Product/Listing} | {X} mentions | {theme} | "{quote}" |

### Listing Optimization (Customer Language to Use)

| # | Customer Language | Where to Use | Frequency | Why |
|---|-------------------|-------------|-----------|-----|
| 1 | "{exact phrase}" | {Title/Bullet #/Image text} | {X} reviews | {rationale} |

### PPC Keyword Insights

| # | Keyword/Phrase from Reviews | Already Tracked? | Closest Search Term Match | Action |
|---|---------------------------|-----------------|--------------------------|--------|
| 1 | "{phrase}" | {Yes/No} | {match from search-terms.md} | {Add to campaign / Already covered} |

### Customer Service FAQ Patterns

| # | Recurring Question | Frequency | Suggested Listing Answer |
|---|-------------------|-----------|-------------------------|
| 1 | {question pattern} | {X} mentions | {suggestion} |

---

## Trend Analysis

> Only include this section if a previous snapshot exists. If first run, replace with:
> "**First analysis run.** No previous data for comparison. This snapshot establishes the baseline for future trend tracking."

### Rating & Sentiment Trend

| Metric | Current | Previous ({date}) | Change | Direction |
|--------|---------|-------------------|--------|-----------|
| Average Rating | {X.X} | {X.X} | {+/- X.X} | {Improving/Stable/Declining} |
| Review Count | {X} | {X} | +{X} new | {Accelerating/Steady/Slowing} |
| Satisfaction Rate | {X%} | {X%} | {+/- X pp} | {direction} |
| Dissatisfaction Rate | {X%} | {X%} | {+/- X pp} | {direction} |

### Theme Changes Since Last Analysis

| Change Type | Theme | Previous | Current | Significance |
|-------------|-------|----------|---------|-------------|
| NEW complaint | {theme} | Not present | {X} mentions | {assessment} |
| RESOLVED complaint | {theme} | {X} mentions | Not present | {assessment} |
| GROWING complaint | {theme} | {X} mentions | {Y} mentions | {assessment} |
| GROWING praise | {theme} | {X} mentions | {Y} mentions | {assessment} |

---

## Data Notes

- **Source:** Apify {actor name}
- **ASINs scraped:** {list}
- **Reviews per ASIN:** {X} (most recent, sorted by date)
- **Missing data:** {any ASINs that failed, with reason}
- **Apify cost:** ~${X.XX}
- **Snapshot saved:** {filepath}
```

### Category Scan Report Template

Same structure as Deep Dive with these differences:
- Title: `# Category Scan: {Category Name} — {YYYY-MM-DD}`
- No competitive gap analysis section (too many products for deep comparison)
- All products in a single summary table rather than individual deep dives
- Complaint and praise themes aggregated across the category with per-product attribution
- Actionable recommendations grouped by product within the category
- If any product shows CONCERNING or CRITICAL sentiment: recommend a follow-up Deep Dive

---

## Snapshot JSON Format

```json
{
  "date": "YYYY-MM-DD",
  "mode": "deep_dive",
  "category": "Cross Stitch",
  "apify_actor": "junglee/amazon-reviews-scraper",
  "apify_cost_estimate": 0.12,
  "products": {
    "B08DDJCQKF": {
      "name": "Cross Stitch Kit - Girls",
      "brand": "CRAFTILOO",
      "is_ours": true,
      "reviews_analyzed": 50,
      "average_rating": 4.5,
      "star_distribution": {
        "5": 25,
        "4": 12,
        "3": 6,
        "2": 4,
        "1": 3
      },
      "satisfaction_rate": 0.74,
      "dissatisfaction_rate": 0.14,
      "photo_review_pct": 0.20,
      "verified_purchase_pct": 0.88,
      "newest_review_date": "2026-02-18",
      "oldest_review_date": "2026-01-05",
      "complaint_themes": {
        "missing_contents": {
          "frequency": 5,
          "pct_of_reviews": 0.10,
          "avg_stars": 2.2,
          "example_quote": "Expected 4 needles but only received 2"
        }
      },
      "praise_themes": {
        "gift_success": {
          "frequency": 15,
          "pct_of_reviews": 0.30,
          "avg_stars": 4.9,
          "example_quote": "My granddaughter absolutely loved this for her birthday"
        }
      },
      "feature_requests": [
        {
          "request": "More designs/patterns included",
          "frequency": 4,
          "example_quote": "Wish it came with more patterns to make"
        }
      ],
      "quality_flags": [
        {
          "severity": "MEDIUM",
          "theme": "thread tangling",
          "frequency": 3,
          "example_quote": "Thread kept tangling and my daughter got frustrated"
        }
      ],
      "gift_mentions": 15,
      "age_mentions": {
        "under_6": { "positive": 2, "negative": 3 },
        "6_to_8": { "positive": 8, "negative": 1 },
        "9_to_12": { "positive": 10, "negative": 0 },
        "adult_help_needed": 4
      },
      "competitor_comparison_mentions": [
        {
          "direction": "better_than",
          "competitor": "Kraftlab",
          "quote": "Much better quality than the Kraftlab kit we tried first"
        }
      ]
    }
  },
  "competitive_gaps": {
    "our_advantages": [
      {
        "competitor_asin": "B08YS42GPG",
        "their_complaint": "missing instructions",
        "their_frequency": 5,
        "our_frequency": 0
      }
    ],
    "our_gaps": [
      {
        "competitor_asin": "B08YS42GPG",
        "their_praise": "video tutorial included",
        "their_frequency": 8,
        "our_frequency": 1
      }
    ]
  },
  "ppc_keyword_insights": [
    {
      "phrase": "screen free activity for kids",
      "frequency": 5,
      "already_tracked": false,
      "closest_search_term": "screen free crafts"
    }
  ]
}
```

---

## Output Location

| Output | Location |
|--------|----------|
| **Deep Dive report** | `outputs/research/review-analysis/briefs/{product-slug}-review-analysis-YYYY-MM-DD.md` |
| **Category Scan report** | `outputs/research/review-analysis/briefs/{category-slug}-category-scan-YYYY-MM-DD.md` |
| **Raw review data** | `outputs/research/review-analysis/data/YYYY-MM-DD/reviews-{ASIN}-YYYY-MM-DD.json` |
| **Snapshot** | `outputs/research/review-analysis/snapshots/{slug}-snapshot-YYYY-MM-DD.json` |

---

## Cost & Token Budget Strategy

### Apify Cost Control

| Item | Cost Per Unit | Deep Dive (4 ASINs) | Category Scan (6-8 ASINs) |
|------|-------------|---------------------|--------------------------|
| Review scraping | ~$0.03/ASIN | ~$0.12 | ~$0.18-$0.24 |
| **Budget ceiling** | — | **$0.20** | **$0.20** |

**If Category Scan would exceed $0.20:**
- Reduce competitor ASINs: scrape only top 1 competitor per product instead of top 2
- Maximum 6 ASINs per Category Scan to stay under budget
- Tell user: "Reduced competitor coverage to stay within cost target"

### Token Budget Control

| Component | Estimated Tokens | Priority |
|-----------|-----------------|----------|
| Context file loading (5 files) | ~8K | Required |
| Raw review data (50 reviews x 4 ASINs) | ~30K | Required |
| Analysis and classification | ~15K | Required |
| Report generation | ~15K | Required |
| Trend comparison | ~5K | If snapshot exists |
| **Total estimated** | **~73K** | — |
| **Budget** | **80K** | — |

**If approaching token limit:**
1. Reduce reviews per ASIN from 50 to 30 (saves ~12K tokens)
2. Summarize rather than quote competitor reviews (saves ~5K tokens)
3. Defer PPC keyword insights and FAQ patterns to appendix (saves ~3K tokens)
4. Never cut: sentiment distribution, complaint themes, competitive gaps, quality flags

### Batching Strategy

- Max 50 reviews per ASIN, sorted by most recent
- Max 5 ASINs per Apify batch call
- Run batches sequentially (not parallel) to avoid rate limits
- Deep Dive: 1 batch of 4 ASINs
- Category Scan: 1-2 batches of up to 5 ASINs each

### When to Recommend a Follow-Up Run

- Category Scan reveals a product with >20% dissatisfaction rate — recommend Deep Dive
- Trend comparison shows growing complaint theme — recommend re-run in 14-30 days
- Review language reveals untapped keywords — recommend cross-referencing with Weekly PPC Analysis

---

## Integration with Other Skills

### With Listing Creator / Product Listing Development
- **Review language feeds listing copy:** Praise themes in exact customer words go into bullet points
- **Complaint themes inform bullet priority:** Most-asked questions from reviews drive which concerns to address in bullets
- **Handoff:** After review analysis, run listing creator with the "Customer Language" and "FAQ Patterns" sections as input

### With Weekly PPC Analysis
- **Review vocabulary reveals keywords:** Natural phrases customers use in reviews may be untapped PPC keywords
- **Review complaints explain low CVR:** If a campaign has low CVR, review complaints may explain why (listing doesn't match expectation)
- **Handoff:** Share PPC Keyword Insights table with weekly PPC analysis for keyword discovery

### With Negative Keyword Generator
- **Review themes identify irrelevant traffic:** If customers consistently say "this isn't a sewing machine kit", that validates negating "sewing machine"
- **Age appropriateness data refines age negatives:** If reviews confirm product works for ages 6+, validates negating "toddler"

### With Daily Market Intel
- **Review velocity correlates with BSR:** Faster review accumulation typically means higher sales velocity
- **Competitor review trends:** If a competitor's review sentiment is declining, this may explain BSR drops

### Recommended Workflow Sequence

| Scenario | Sequence |
|----------|----------|
| **New product launch** | 1. Review Analyzer (competitor reviews) -> 2. Product Listing Development (informed by review insights) -> 3. Negative Keyword Generator |
| **Listing optimization** | 1. Review Analyzer (our + competitor reviews) -> 2. Update listing bullets with customer language |
| **Monthly health check** | 1. Review Analyzer -> 2. Compare with previous snapshot -> 3. Feed findings to Weekly PPC Analysis |
| **Quality concern** | 1. Review Analyzer (Deep Dive, our product only) -> 2. Quality flags to product team |

---

## Execution Checklist

Before delivering the report, verify:

### Setup & Data Loading
- [ ] Mode confirmed (Deep Dive or Category Scan)
- [ ] Product/category identified and ASIN list built
- [ ] All context files loaded (hero-products, competitors, products, business, search-terms)
- [ ] ASIN list validated — every ASIN is in hero-products.md OR competitors.md
- [ ] Estimated cost shown to user and confirmed (<$0.20)
- [ ] Previous snapshot checked (loaded or noted as first run)

### Scraping
- [ ] Reviews scraped via Apify (primary actor, fallback if needed)
- [ ] Max 50 reviews per ASIN, sorted by most recent
- [ ] Max 5 ASINs per batch call
- [ ] Raw data saved to `data/YYYY-MM-DD/` folder
- [ ] Any scraping failures noted with reason

### Analysis
- [ ] Sentiment distribution calculated for every scraped ASIN
- [ ] Complaint themes extracted with frequency, percentage, and quotes (3+ mentions threshold)
- [ ] Praise themes extracted with frequency, percentage, and quotes (3+ mentions threshold)
- [ ] Feature requests captured
- [ ] Quality/safety flags identified (3+ mentions threshold, 2+ for safety)
- [ ] Gift-ability mentions tracked separately
- [ ] Age appropriateness mentions tracked separately
- [ ] Photo review insights noted
- [ ] Competitor comparison mentions captured

### Competitive Analysis (Deep Dive Only)
- [ ] Our advantages identified (competitor complaints we don't have)
- [ ] Our gaps identified (competitor praise we don't have)
- [ ] Head-to-head theme matrix built
- [ ] Competitor comparison mentions from reviews captured

### Actionable Outputs
- [ ] Product improvements ranked by frequency (not opinion)
- [ ] Improvements cross-referenced against products.md (listing issue vs product issue)
- [ ] Listing optimization suggestions include exact customer language
- [ ] PPC keyword insights cross-referenced against search-terms.md
- [ ] Customer service FAQ patterns identified
- [ ] Quality control flags include severity rating

### Trend & Snapshot
- [ ] Trend comparison included (or first-run note)
- [ ] Snapshot JSON saved to snapshots/ folder
- [ ] Snapshot includes all required fields

### Output & Housekeeping
- [ ] Report follows exact output format template
- [ ] Report saved to correct output location with correct filename
- [ ] Summary presented to user (mode, products, top 3 findings)
- [ ] Total Apify cost noted
- [ ] Token usage within 80K target

---

## Error Handling

| Issue | Response |
|-------|----------|
| User doesn't specify mode | Ask: "Single Product Deep Dive or Category Scan?" with brief explanation of each |
| Product ASIN not in hero-products.md or competitors.md | REFUSE to scrape. Say: "This ASIN is not in our tracked product or competitor list. Add it to the relevant context file first." |
| Apify primary actor fails | Try fallback actor (`epctex/amazon-reviews-scraper`) once. If that fails, skip that ASIN and note in report. |
| Apify timeout (>3 minutes per batch) | STOP immediately. Use whatever data was collected. Note in report: "{X} of {Y} ASINs scraped before timeout." |
| Apify returns 0 reviews for an ASIN | Note in report. Possible reasons: new product, restricted listing, or scraper limitation. Skip that ASIN in analysis. |
| Reviews are in non-English language | Skip non-English reviews. Note count of skipped reviews. |
| Estimated Apify cost exceeds $0.20 | STOP before scraping. Tell user: "This analysis would cost ~${X}. Reduce scope (fewer competitors) or confirm to proceed?" |
| Previous snapshot JSON is corrupted/malformed | Skip trend comparison. Note: "Previous snapshot unreadable — treating as first run." |
| Category has no competitors in competitors.md | Ask user for competitor ASINs, or offer to run with just our products. |
| Too many ASINs for Category Scan (>8) | Prioritize: hero products first, then top 1 competitor per product. Tell user what was trimmed. |
| Review scraper returns duplicate reviews | Deduplicate by review ID or review title + date combination before analysis. |
| Token budget tight (near 80K) | Prioritize: sentiment distribution + complaint themes + competitive gaps. Defer: full praise analysis, PPC insights, FAQ patterns to appendix. |
| User asks for a product not in any context file | Ask them to identify it. If it is a Craftiloo product missing from context, offer to add it. If it is unknown, refuse. |

---

## ⚠️ AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/customer-review-analyzer/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Goals:**
- [ ] Goal 1
- [ ] Goal 2

**Result:** ✅ Success / ⚠️ Partial / ❌ Failed

**What happened:**
- (What went according to plan)

**What didn't work:**
- (Any issues, with specifics)

**Is this a repeat error?** Yes/No — if yes, which one?

**Lesson learned:**
- (What to do differently next time)

**Tokens/cost:** ~XX K tokens
```

### 2. Update Issue Tracking

| Situation | Action |
|-----------|--------|
| New problem | Add to **Known Issues** |
| Known Issue happened again | Move to **Repeat Errors**, increment count, **tell the user** |
| Fixed a Known Issue | Move to **Resolved Issues** |

### 3. Tell the User

End your output with a **Lessons Update** note:
- What you logged
- Any repeat errors encountered
- Suggestions for skill improvement

**Do NOT skip this. The system only improves if every run is logged honestly.**
