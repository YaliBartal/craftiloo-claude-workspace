---
name: niche-category-analysis
description: Deep-dive analysis of a new Amazon niche/category — competitors, market share, pricing, keywords, review insights, gaps, and viability assessment
triggers:
  - niche analysis
  - category analysis
  - explore a niche
  - new niche
  - niche research
  - category research
  - market opportunity
  - should I enter this niche
output_location: outputs/research/niche-analysis/
---

# Niche Category Analysis

## Purpose

Provide a comprehensive "feel" for an Amazon niche before committing to product development. Answer the core question: **Is this niche worth entering, and if so, how?**

This skill delivers:
- Who dominates and their estimated market share
- Average selling price and price distribution
- Main search keywords driving the niche
- Competitor strengths and weaknesses (from real reviews)
- Gaps and opportunities for new products
- Overall viability assessment with a go/no-go recommendation

---

## When to Use

- Exploring a **new product category** you're not currently in
- Evaluating whether to **expand into an adjacent niche**
- Getting a **data-driven feel** for a market before investing time/money
- Comparing **multiple niches** to decide where to focus

---

## Input Requirements

### Phase 0: Gather Input (MANDATORY — do NOT skip)

**Ask the user for:**

1. **Niche keyword(s)** — The main search term(s) that define this niche
   - Example: "diamond painting kits", "crochet kits for beginners", "paint by numbers for adults"
   - Accept 1-3 keywords. The first is the PRIMARY keyword.

2. **Category context** (optional) — Any specific angle they're interested in
   - Example: "kids version", "premium end", "beginner-friendly"

3. **Known competitors** (optional) — Any specific ASINs or brands they already know about

**Do NOT proceed without at least one niche keyword.**

---

## Execution Flow

### Phase 1: Market Landscape Discovery
**Goal:** Identify who's in the niche and how big it is.

#### Step 1.1: Search Amazon for Top Products

Use the Amazon search scraper to find the top products for each niche keyword.

**MCP Tool:** `igview-owner/amazon-search-scraper`

```json
{
  "keyword": "{primary-niche-keyword}",
  "pages": 2,
  "amazon_domain": "www.amazon.com"
}
```

- Run for the primary keyword (2 pages = ~48 results)
- Run for each additional keyword (1 page each)
- Deduplicate results by ASIN

#### Step 1.2: Identify Top 15 Competitors

From search results, select the **top 15 products** based on:
1. Organic rank position (top of search = more relevant)
2. Review count (social proof / market presence)
3. BSR (actual sales velocity)

Exclude:
- Sponsored-only products with no organic presence
- Products clearly outside the niche (wrong category)
- Variation duplicates (keep the parent/best-selling variation)

#### Step 1.3: Scrape Product Details

**MCP Tool:** `junglee/amazon-product-scraper`
**Fallback:** `saswave/amazon-product-scraper`

```json
{
  "asins": ["{top-15-asins}"],
  "amazon_domain": "www.amazon.com"
}
```

**Batching rules:**
- Max 5 ASINs per call
- Use async mode
- Timeout after 3 minutes — use whatever data you have

**Extract for each product:**
- ASIN
- Title
- Brand
- Price (current, was-price if available)
- BSR (main category + subcategory)
- Rating (stars)
- Review count
- Main image URL
- Bullet points (first 3)
- Date first available (if shown)
- Category breadcrumb
- Coupon/deal (if active)
- Number of variations

#### Step 1.4: Estimate Market Share

**BSR-to-Sales Estimation Table (monthly units):**

| BSR Range (Toys & Games) | Est. Monthly Units |
|---|---|
| 1-100 | 10,000+ |
| 100-500 | 3,000-10,000 |
| 500-2,000 | 1,000-3,000 |
| 2,000-5,000 | 500-1,000 |
| 5,000-15,000 | 150-500 |
| 15,000-50,000 | 50-150 |
| 50,000-100,000 | 15-50 |
| 100,000+ | <15 |

| BSR Range (Arts, Crafts & Sewing) | Est. Monthly Units |
|---|---|
| 1-100 | 6,000+ |
| 100-500 | 2,000-6,000 |
| 500-2,000 | 700-2,000 |
| 2,000-5,000 | 300-700 |
| 5,000-15,000 | 100-300 |
| 15,000-50,000 | 30-100 |
| 50,000-100,000 | 10-30 |
| 100,000+ | <10 |

**Calculate for each product:**
- Estimated monthly units (from BSR)
- Estimated monthly revenue (units x price)
- Market share % (product revenue / total niche revenue)

**Calculate niche-level metrics:**
- Total estimated monthly revenue
- Total estimated monthly units
- Top 3 market share concentration (% held by top 3)
- Average review count
- Average rating

---

### Phase 2: Pricing Analysis
**Goal:** Understand the price landscape and find gaps.

#### Step 2.1: Price Distribution

Calculate:
- **Average Selling Price (ASP)** — weighted by estimated units
- **Median price**
- **Price range** (min to max)
- **Price clusters** — group products into natural price tiers
  - Budget tier: bottom 25%
  - Mid tier: middle 50%
  - Premium tier: top 25%

#### Step 2.2: Price-to-Value Mapping

For each price tier, note:
- What do you GET at this price? (contents, quality signals)
- How many reviews/ratings at this tier?
- Any price points with NO products? (potential gap)

---

### Phase 3: Keyword Research
**Goal:** Map the search landscape for this niche.

#### Step 3.1: Extract Keywords from Competitor Titles

Parse all 15 competitor titles and extract:
- Recurring keyword phrases (2-4 word combinations)
- Frequency of each phrase across titles
- Position in title (front-loaded = higher priority)

#### Step 3.2: Amazon Autocomplete / Related Searches

Use web search to find Amazon autocomplete suggestions for:
- Primary niche keyword
- Primary keyword + "for" (age/audience variations)
- Primary keyword + "kit" / "set" / "bundle"

#### Step 3.3: Keyword Mapping

Create a keyword map:

| Keyword | Frequency in Titles | Est. Competition | Notes |
|---|---|---|---|
| {keyword} | X/15 titles | High/Med/Low | {observation} |

**Competition assessment:**
- **High:** 10+ of top 15 use this keyword, dominant brands present
- **Medium:** 5-9 of top 15 use it
- **Low:** <5 use it, potential opportunity

---

### Phase 4: Competitor Review Deep Dive
**Goal:** Understand what customers love, hate, and wish for.

#### Step 4.1: Select Review Targets

Pick the **top 5 competitors** for review scraping based on:
1. Highest market share (top 2-3)
2. Highest rated (1-2 that customers love)
3. Most reviewed (social proof leaders)

#### Step 4.2: Scrape Reviews

**MCP Tool:** `junglee/amazon-reviews-scraper`
**Fallback:** `epctex/amazon-reviews-scraper`

```json
{
  "productUrls": [
    "https://www.amazon.com/dp/{ASIN1}",
    "https://www.amazon.com/dp/{ASIN2}"
  ],
  "maxReviews": 50,
  "sort": "recent"
}
```

**Rules:**
- Max 50 reviews per product (cost control)
- Max 5 ASINs per batch call
- Use async mode
- Sort by "recent" to get current sentiment
- Timeout after 3 minutes

#### Step 4.3: Analyze Reviews

For each competitor, extract:

**Praise Themes** (what customers love):
- Theme name
- Frequency (how many reviews mention it)
- Representative quotes (2-3 best)
- Strength rating: Strong / Moderate / Weak

**Complaint Themes** (what customers hate):
- Theme name
- Frequency
- Representative quotes (2-3 most telling)
- Severity: Critical / Moderate / Minor
- Is this fixable by a new entrant? Yes/No

**Feature Requests** (what customers wish for):
- Request description
- Frequency
- Is anyone fulfilling this? Yes/No

**Common Q&A Themes:**
- What questions do customers ask repeatedly?
- What concerns come up before purchase?

#### Step 4.4: Cross-Competitor Pattern Analysis

Aggregate across ALL scraped competitors:
- **Universal praises** — things ALL top products do well (table stakes)
- **Universal complaints** — pain points NO ONE has solved (biggest opportunities)
- **Differentiators** — things only 1-2 products do (competitive advantages)
- **Polarizing features** — loved by some, hated by others (positioning decision)

---

### Phase 5: Gap Analysis & Opportunities
**Goal:** Identify concrete opportunities for a new product.

#### Step 5.1: Product Gaps

Based on all data collected, identify:

1. **Price gaps** — Underserved price points with demand but no supply
2. **Feature gaps** — Things customers want that no one offers
3. **Quality gaps** — Common quality complaints that could be solved
4. **Audience gaps** — Underserved customer segments (age, skill level, use case)
5. **Listing gaps** — Poor images, weak bullets, missing A+ content among leaders
6. **Bundling gaps** — Missing accessories or complementary items

#### Step 5.2: Barrier Assessment

For each gap, assess:
- **Difficulty to exploit:** Easy / Medium / Hard
- **Investment required:** Low / Medium / High
- **Competitive moat:** Can competitors copy quickly? Yes/No
- **Demand signal strength:** Strong / Moderate / Weak

#### Step 5.3: Opportunity Ranking

Rank opportunities by:
1. Demand signal strength (from reviews + search volume)
2. Ease of execution
3. Defensibility (can you maintain an advantage?)
4. Revenue potential

---

### Phase 6: Niche Viability Assessment
**Goal:** Go/No-Go recommendation with reasoning.

#### Viability Scorecard

Rate each factor 1-5:

| Factor | Score | Notes |
|---|---|---|
| **Market Size** | /5 | Est. monthly revenue of niche |
| **Competition Intensity** | /5 | 5 = low competition = good |
| **Price Opportunity** | /5 | Room for profitable pricing |
| **Differentiation Potential** | /5 | Can you stand out? |
| **Customer Pain Points** | /5 | Unresolved complaints = opportunity |
| **Keyword Accessibility** | /5 | Can you rank for key terms? |
| **Alignment with Brand** | /5 | Fits Craftiloo's strengths? |
| **TOTAL** | /35 | |

**Scoring Guide:**
- **28-35:** Strong opportunity — move forward
- **20-27:** Moderate opportunity — proceed with caution, address weak areas
- **14-19:** Weak opportunity — significant challenges, consider alternatives
- **<14:** Pass — too many barriers

#### Final Recommendation

Provide a clear **GO / CONDITIONAL GO / NO-GO** with:
- Top 3 reasons supporting the recommendation
- Top 3 risks/challenges
- Suggested product positioning (if GO)
- Suggested price point (if GO)
- Suggested differentiation angle (if GO)
- Estimated time to first sale (if GO)

---

## Output Structure

### File Organization

```
outputs/research/niche-analysis/
├── briefs/                           # Main analysis reports
│   └── {niche-slug}-niche-analysis-YYYY-MM-DD.md
├── data/
│   └── YYYY-MM-DD/                   # Raw scraped data
│       ├── search-results-{keyword}-YYYY-MM-DD.json
│       ├── products-{niche-slug}-YYYY-MM-DD.json
│       └── reviews-{ASIN}-YYYY-MM-DD.json
├── snapshots/                        # For future comparison
│   └── {niche-slug}-snapshot-YYYY-MM-DD.json
└── README.md
```

### Brief Report Format

```markdown
# {Niche Name} — Category Niche Analysis
**Date:** YYYY-MM-DD
**Primary Keyword:** {keyword}
**Verdict:** GO / CONDITIONAL GO / NO-GO

---

## Executive Summary
{2-3 sentence overview: market size, competition level, key opportunity}

---

## Market Landscape

### Niche Overview
| Metric | Value |
|---|---|
| Est. Monthly Revenue | ${X} |
| Est. Monthly Units | {X} |
| Number of Competitors (top 2 pages) | {X} |
| Average Selling Price (ASP) | ${X} |
| Median Price | ${X} |
| Price Range | ${min} - ${max} |
| Avg Rating (top 15) | {X} stars |
| Avg Review Count (top 15) | {X} |
| Top 3 Market Share | {X}% |

### Top 15 Competitors

| # | Brand | ASIN | Price | BSR | Rating | Reviews | Est. Monthly Units | Est. Revenue | Market Share |
|---|---|---|---|---|---|---|---|---|---|
| 1 | {brand} | {asin} | ${price} | {bsr} | {rating} | {reviews} | {units} | ${rev} | {share}% |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### Market Concentration
- **Top 3 hold {X}%** of estimated revenue
- {Observation about market concentration — monopoly? fragmented? etc.}

---

## Pricing Analysis

### Price Tiers
| Tier | Price Range | # Products | Avg Rating | Avg Reviews | Notes |
|---|---|---|---|---|---|
| Budget | ${X}-${X} | {n} | {rating} | {reviews} | {what you get} |
| Mid | ${X}-${X} | {n} | {rating} | {reviews} | {what you get} |
| Premium | ${X}-${X} | {n} | {rating} | {reviews} | {what you get} |

### Price Gaps
{Identify underserved price points or value propositions}

---

## Keyword Landscape

### Primary Keywords
| Keyword | In X/15 Titles | Competition | Opportunity |
|---|---|---|---|
| {keyword} | {X}/15 | High/Med/Low | {note} |

### Long-tail Opportunities
{Keywords with lower competition that could drive traffic}

---

## Customer Voice (Review Analysis)

### What Customers LOVE (Table Stakes)
{Things all top products do well — you MUST match these}

| Theme | Frequency | Representative Quote |
|---|---|---|
| {theme} | {X} mentions | "{quote}" |

### What Customers HATE (Opportunities)
{Recurring complaints — your chance to differentiate}

| Theme | Frequency | Severity | Fixable? | Representative Quote |
|---|---|---|---|---|
| {theme} | {X} mentions | Critical/Moderate/Minor | Yes/No | "{quote}" |

### What Customers WISH FOR (Unmet Needs)
| Request | Frequency | Anyone Doing It? |
|---|---|---|
| {request} | {X} mentions | Yes/No |

### Competitor Strengths & Weaknesses Matrix

| Competitor | Key Strengths | Key Weaknesses | Rating | Reviews |
|---|---|---|---|---|
| {brand} (ASIN) | {strengths} | {weaknesses} | {rating} | {count} |

---

## Gap Analysis & Opportunities

### Identified Opportunities (Ranked)

#### 1. {Opportunity Name}
- **Type:** Price / Feature / Quality / Audience / Listing / Bundle
- **Demand Signal:** Strong / Moderate / Weak
- **Difficulty:** Easy / Medium / Hard
- **Investment:** Low / Medium / High
- **Defensible:** Yes / No
- **Details:** {2-3 sentences explaining the opportunity}

#### 2. {Opportunity Name}
...

---

## Viability Scorecard

| Factor | Score | Reasoning |
|---|---|---|
| Market Size | {X}/5 | {why} |
| Competition Intensity | {X}/5 | {why} |
| Price Opportunity | {X}/5 | {why} |
| Differentiation Potential | {X}/5 | {why} |
| Customer Pain Points | {X}/5 | {why} |
| Keyword Accessibility | {X}/5 | {why} |
| Brand Alignment | {X}/5 | {why} |
| **TOTAL** | **{X}/35** | |

---

## Recommendation

**Verdict: {GO / CONDITIONAL GO / NO-GO}**

### Why
1. {Reason 1}
2. {Reason 2}
3. {Reason 3}

### Risks
1. {Risk 1}
2. {Risk 2}
3. {Risk 3}

### If Proceeding
- **Suggested positioning:** {how to position the product}
- **Target price point:** ${X}
- **Differentiation angle:** {what makes you different}
- **Must-have features:** {non-negotiables based on reviews}
- **Next steps:** {what to do next — product development, listing, etc.}

---

*Generated by Niche Category Analysis skill — {date}*
```

### Snapshot Format (JSON)

Save for future comparison:

```json
{
  "niche": "{niche-name}",
  "date": "YYYY-MM-DD",
  "primary_keyword": "{keyword}",
  "metrics": {
    "est_monthly_revenue": 0,
    "est_monthly_units": 0,
    "avg_selling_price": 0,
    "median_price": 0,
    "avg_rating": 0,
    "avg_reviews": 0,
    "top_3_concentration": 0,
    "competitor_count": 0
  },
  "top_competitors": [
    {
      "asin": "",
      "brand": "",
      "title": "",
      "price": 0,
      "bsr": 0,
      "rating": 0,
      "reviews": 0,
      "est_monthly_units": 0,
      "est_monthly_revenue": 0,
      "market_share": 0
    }
  ],
  "keywords": [
    {
      "keyword": "",
      "frequency_in_titles": 0,
      "competition": "High/Med/Low"
    }
  ],
  "viability_score": 0,
  "verdict": "GO/CONDITIONAL GO/NO-GO"
}
```

---

## Efficiency & Cost Controls

| Constraint | Limit |
|---|---|
| Max ASINs scraped (products) | 15 |
| Max ASINs scraped (reviews) | 5 |
| Max reviews per ASIN | 50 |
| Max keyword searches | 5 |
| Apify batch size | 5 ASINs per call |
| Timeout per scrape call | 3 minutes |
| Total token budget | <80K |
| Total API cost target | <$0.25 |

**If a scrape times out:** Use whatever data was collected. Note gaps in the report. Do NOT retry automatically — ask user first.

**If a scrape fails entirely:** Skip that ASIN, note it in the report, continue with remaining data.

---

## Error Handling

| Error | Action |
|---|---|
| No search results for keyword | Ask user to refine keyword, suggest alternatives |
| Fewer than 5 products found | Warn: niche may be too narrow. Proceed with available data |
| Scraper returns no data for ASIN | Skip, note in report, use remaining products |
| All scrapers fail | STOP. Report error. Ask user to try later |
| Reviews scraper returns <10 reviews | Note low review count, analysis may be thin |
| Timeout on batch | Use partial data, note which ASINs are missing |
| API cost exceeds $0.25 | STOP further scraping. Work with data collected |

---

## Integration with Other Skills

| This skill provides... | To... |
|---|---|
| Competitor ASINs + keywords | **Daily Market Intel** (add to tracking) |
| Customer language from reviews | **Listing Creator** (bullet copy) |
| Competitor weaknesses | **Image Planner** (visual differentiation) |
| Keyword map | **Negative Keyword Generator** (irrelevant terms) |
| Review themes | **Customer Review Analyzer** (ongoing monitoring) |

**After a GO verdict, suggest:**
1. Add top competitors to `context/competitors.md`
2. Add niche keywords to `context/search-terms.md`
3. Run **Listing Creator** for the new product concept
4. Run **Image Planner** based on competitor image analysis

---

## Pre-Execution Checklist

Before starting, confirm:
- [ ] User provided at least 1 niche keyword
- [ ] Keyword makes sense as an Amazon search term
- [ ] User understands this will use Apify credits (~$0.15-0.25)
- [ ] Output folder exists or will be created

---

## Execution Order Summary

1. **Gather input** — Keyword(s), context, known competitors
2. **Search Amazon** — Find top products for the niche keyword(s)
3. **Identify top 15** — Select most relevant competitors
4. **Scrape product data** — Price, BSR, ratings, reviews count, bullets
5. **Estimate market share** — BSR-to-sales conversion
6. **Analyze pricing** — Tiers, gaps, ASP
7. **Extract keywords** — From titles, autocomplete, related searches
8. **Scrape reviews** — Top 5 competitors, 50 reviews each
9. **Analyze reviews** — Praise, complaints, wishes, patterns
10. **Identify gaps** — Price, feature, quality, audience, listing, bundle
11. **Score viability** — 7-factor scorecard
12. **Generate report** — Full brief with recommendation
13. **Save snapshot** — JSON for future comparison
14. **Present summary** — Key findings to user
15. **Suggest next steps** — If GO, recommend follow-up actions
