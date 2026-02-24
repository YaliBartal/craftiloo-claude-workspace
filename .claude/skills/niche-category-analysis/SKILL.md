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

## ⚠️ BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/niche-category-analysis/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"⚠️ Repeat issue (×N): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## Purpose

Provide a comprehensive "feel" for an Amazon niche before committing to product development. Answer the core question: **Is this niche worth entering, and if so, how?**

This skill delivers:
- Who dominates and their estimated market share
- Average selling price and price distribution
- Main search keywords with **real search volumes** driving the niche
- Competitor strengths and weaknesses (from real reviews)
- **Listing optimization scores** showing who has weak listings (opportunity)
- Gaps and opportunities for new products
- Overall viability assessment with a go/no-go recommendation

---

## Data Source Hierarchy

This skill uses **3 MCP services** as primary data sources. Apify scraping is the **fallback only**.

| Priority | Source | What It Provides |
|----------|--------|-----------------|
| **1st** | **DataDive** | Competitor sales/revenue (Jungle Scout), keywords with search volumes, ranking juice scores, keyword roots |
| **2nd** | **Amazon SP-API** | Real-time pricing, first-party BSR/category data, catalog search |
| **3rd** | **Seller Board** | Our own profit data if we're already in this niche |
| **Fallback** | **Apify** | Review scraping (still needed), product data if MCP sources fail |

**Key upgrade:** Sales estimates come from **Jungle Scout actuals** (via DataDive), NOT BSR lookup tables. Keyword data includes **real search volumes**, not title-frequency guessing.

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

2. **Seed ASIN** (recommended) — A known top product in the niche
   - This enables DataDive's `create_niche_dive` for automatic competitor discovery
   - If the user doesn't have one, we'll find one via SP-API catalog search

3. **Category context** (optional) — Any specific angle they're interested in
   - Example: "kids version", "premium end", "beginner-friendly"

4. **Known competitors** (optional) — Any specific ASINs or brands they already know about

5. **Are we already in this niche?** (ask) — If yes, we pull Seller Board profit data for context

**Do NOT proceed without at least one niche keyword.**

---

## Execution Flow

### Phase 1: Market Landscape Discovery
**Goal:** Identify who's in the niche and how big it is.

#### Step 1.1: Check for Existing DataDive Niche

First, check if this niche already exists in DataDive:

**MCP Tool:** `list_niches` (DataDive)

- Scan the niche list for a matching or similar niche
- If found → use the existing `nicheId` and skip to Step 1.3
- If not found → proceed to Step 1.2

#### Step 1.2: Discover Competitors (Two Paths)

**Path A: Seed ASIN provided → DataDive Niche Dive**

**MCP Tool:** `get_profile` (DataDive) — check token balance first

⚠️ `create_niche_dive` **consumes DataDive tokens**. Before running:
1. Check balance with `get_profile`
2. **Ask user for approval:** _"Creating a niche dive costs DataDive tokens. Current balance: {X}. Proceed?"_
3. Only proceed with explicit approval

**MCP Tool:** `create_niche_dive` (DataDive)
```json
{
  "seed_asin": "{ASIN}"
}
```

- Returns a `dive_id`
- Poll `get_niche_dive_status` every 30 seconds until complete (max 5 minutes)
- On success → get the new `nicheId` from results

**Path B: No seed ASIN → SP-API Catalog Search + Manual Discovery**

**MCP Tool:** `search_catalog` (SP-API)
```json
{
  "keywords": "{primary-niche-keyword}",
  "marketplace": "US",
  "max_results": 20
}
```

- Search for primary keyword
- Identify the top-selling ASIN from results (highest review count + lowest BSR)
- Use that ASIN as seed for Path A, OR proceed with SP-API data only

#### Step 1.3: Pull Competitor Data from DataDive

**MCP Tool:** `get_niche_competitors` (DataDive)
```json
{
  "niche_id": "{nicheId}",
  "page_size": 50
}
```

**This replaces BSR guessing tables.** DataDive returns Jungle Scout-powered:
- ASIN, BSR, **actual sales estimates**, **actual revenue estimates**
- Price, rating, review count
- P1 keywords count, advertised keywords count

Select **top 15 competitors** based on:
1. Revenue estimate (highest = most relevant)
2. Review count (social proof)
3. Organic relevance to the niche keyword

Exclude:
- Products clearly outside the niche (wrong category)
- Variation duplicates (keep parent/best-selling variation)

#### Step 1.4: Enrich with SP-API First-Party Data

For the top 15 competitors, pull first-party Amazon data:

**MCP Tool:** `get_catalog_item` (SP-API) — for each ASIN
```json
{
  "asin": "{ASIN}",
  "marketplace": "US"
}
```

**Extract:**
- Official title, brand, category breadcrumb
- First-party BSR + category
- Images, dimensions
- Date first available (if available)

**Batching:** Run 3-5 `get_catalog_item` calls in parallel. Don't exceed 15 total.

#### Step 1.5: Calculate Market Metrics

Using **DataDive's actual sales/revenue data** (not BSR estimates):

**Per product:**
- Monthly units sold (from DataDive)
- Monthly revenue (from DataDive)
- Market share % (product revenue / total niche revenue)

**Niche-level metrics:**
- Total estimated monthly revenue
- Total estimated monthly units
- Top 3 market share concentration (% held by top 3)
- Average review count
- Average rating
- Revenue per review (maturity indicator)

#### Step 1.6: Internal Context (If Already in Niche)

If user confirmed they're already in this niche:

**MCP Tool:** `get_sales_detailed_report` (Seller Board)

- Pull our actual profit data for products in this category
- Note our current position: revenue, units, profit margin, ACOS
- Use as baseline for "what we know" vs competitor estimates

---

### Phase 2: Pricing Analysis
**Goal:** Understand the price landscape and find gaps.

#### Step 2.1: Real-Time Pricing from SP-API

**MCP Tool:** `get_competitive_pricing` (SP-API) — for top 15
```json
{
  "asin": "{ASIN}",
  "marketplace": "US"
}
```

**Extract for each:**
- Current landed price (price + shipping)
- Listing price vs sale price
- Buy Box price and who holds it
- Number of competing offers

**Batching:** Run 3-5 calls in parallel.

#### Step 2.2: Price Distribution

Calculate from real-time pricing data:
- **Average Selling Price (ASP)** — weighted by estimated units (from DataDive)
- **Median price**
- **Price range** (min to max)
- **Price clusters** — group products into natural price tiers
  - Budget tier: bottom 25%
  - Mid tier: middle 50%
  - Premium tier: top 25%

#### Step 2.3: Price-to-Value Mapping

For each price tier, note:
- What do you GET at this price? (contents, quality signals)
- How many reviews/ratings at this tier?
- Revenue concentration by tier
- Any price points with NO products? (potential gap)
- Buy Box ownership patterns (3P sellers undercutting?)

---

### Phase 3: Keyword Research
**Goal:** Map the search landscape with real search volume data.

#### Step 3.1: Master Keyword List from DataDive

**MCP Tool:** `get_niche_keywords` (DataDive)
```json
{
  "niche_id": "{nicheId}",
  "page_size": 200
}
```

**This replaces title-keyword extraction.** Returns:
- Keyword phrases with **actual search volumes**
- Relevancy classification: **Core / Related / Outlier**
- Organic rank data for each competitor
- Sponsored rank data

**Process:**
- Sort by search volume (highest first)
- Group by relevancy (Core → Related → Outlier)
- Identify keywords where NO competitor ranks in top 10 (ranking gaps)
- Identify keywords where only 1-2 competitors rank (low-competition)

#### Step 3.2: Keyword Roots Analysis

**MCP Tool:** `get_niche_roots` (DataDive)
```json
{
  "niche_id": "{nicheId}",
  "page_size": 100
}
```

**Returns:** Root words with frequency + broad search volume

**Use for:**
- Understanding the keyword landscape structure
- Identifying root themes (material types, use cases, audience segments)
- Finding underrepresented roots (potential positioning angles)

#### Step 3.3: Keyword Map (Enhanced)

Create a keyword map with real data:

| Keyword | Search Volume | Relevancy | Top Organic Rank | # Ranking | Opportunity |
|---|---|---|---|---|---|
| {keyword} | {volume}/mo | Core/Related | #{rank} | X/15 | {assessment} |

**Opportunity assessment (data-driven):**
- **High opportunity:** SV > 1,000 + fewer than 3 competitors in top 10
- **Medium opportunity:** SV > 500 + fewer than 5 competitors in top 10
- **Low opportunity:** SV < 500 OR 10+ competitors ranking
- **Long-tail gold:** SV 200-1,000 + 0-1 competitors ranking

#### Step 3.4: Search Volume Summary

| Metric | Value |
|---|---|
| Total niche search volume (Core keywords) | {X}/mo |
| Total niche search volume (Core + Related) | {X}/mo |
| # Core keywords | {X} |
| # Related keywords | {X} |
| # Outlier keywords (exclude from strategy) | {X} |
| Avg search volume per Core keyword | {X}/mo |
| Top keyword by volume | {keyword} ({volume}/mo) |

---

### Phase 4: Competitor Review Deep Dive
**Goal:** Understand what customers love, hate, and wish for.

#### Step 4.1: Select Review Targets

Pick the **top 5 competitors** for review scraping based on:
1. Highest revenue (top 2-3 from DataDive data)
2. Highest rated (1-2 that customers love)
3. Most reviewed (social proof leaders)

#### Step 4.2: Scrape Reviews

**MCP Tool:** `junglee/amazon-reviews-scraper` (Apify)
**Fallback:** `epctex/amazon-reviews-scraper` (Apify)

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

### Phase 5: Listing & Ranking Gap Analysis
**Goal:** Find weak listings and ranking opportunities.

#### Step 5.1: Ranking Juice Scores

**MCP Tool:** `get_niche_ranking_juices` (DataDive)
```json
{
  "niche_id": "{nicheId}",
  "page_size": 50
}
```

**Returns per competitor:**
- Title optimization score
- Bullet points optimization score
- Description optimization score
- Overall listing quality score

**Analyze:**
- Which top-revenue competitors have **low listing scores**? → They're winning despite weak listings (vulnerable to a well-optimized entrant)
- Which competitors have **high listing scores but low sales**? → Good listing ≠ product-market fit
- Average listing score across niche → Higher = harder to differentiate on copy alone

#### Step 5.2: Product Gaps

Based on all data collected, identify:

1. **Price gaps** — Underserved price points with demand but no supply
2. **Feature gaps** — Things customers want that no one offers
3. **Quality gaps** — Common quality complaints that could be solved
4. **Audience gaps** — Underserved customer segments (age, skill level, use case)
5. **Listing gaps** — Low Ranking Juice scores among top sellers = copy opportunity
6. **Keyword gaps** — High-SV keywords where no one ranks well
7. **Bundling gaps** — Missing accessories or complementary items

#### Step 5.3: Barrier Assessment

For each gap, assess:
- **Difficulty to exploit:** Easy / Medium / Hard
- **Investment required:** Low / Medium / High
- **Competitive moat:** Can competitors copy quickly? Yes/No
- **Demand signal strength:** Strong / Moderate / Weak
- **Data confidence:** High (Jungle Scout actual) / Medium (SP-API first-party) / Low (estimated)

#### Step 5.4: Opportunity Ranking

Rank opportunities by:
1. Demand signal strength (from search volumes + review frequency)
2. Ease of execution
3. Defensibility (can you maintain an advantage?)
4. Revenue potential (from actual competitor revenue data)

---

### Phase 6: Niche Viability Assessment
**Goal:** Go/No-Go recommendation with reasoning.

#### Viability Scorecard

Rate each factor 1-5:

| Factor | Score | Notes |
|---|---|---|
| **Market Size** | /5 | Based on DataDive actual revenue data |
| **Competition Intensity** | /5 | 5 = low competition = good |
| **Price Opportunity** | /5 | Room for profitable pricing (SP-API real pricing) |
| **Differentiation Potential** | /5 | Review gaps + listing gaps + keyword gaps |
| **Customer Pain Points** | /5 | Unresolved complaints = opportunity |
| **Keyword Accessibility** | /5 | Real search volumes + ranking gaps from DataDive |
| **Listing Quality Gap** | /5 | Low Ranking Juice scores = weak competitors |
| **Alignment with Brand** | /5 | Fits Craftiloo's strengths? |
| **TOTAL** | /40 | |

**Scoring Guide:**
- **32-40:** Strong opportunity — move forward
- **24-31:** Moderate opportunity — proceed with caution, address weak areas
- **16-23:** Weak opportunity — significant challenges, consider alternatives
- **<16:** Pass — too many barriers

#### Data Confidence Rating

Rate overall data quality:

| Source | Available? | Confidence |
|---|---|---|
| DataDive competitor data | Yes/No | High (Jungle Scout) / N/A |
| DataDive keyword data | Yes/No | High (real SV) / N/A |
| SP-API pricing | Yes/No | High (first-party) / N/A |
| SP-API catalog | Yes/No | High (first-party) / N/A |
| Seller Board (own data) | Yes/No | High (actual) / N/A |
| Review data | Yes/No | Medium (sample) / N/A |

**Overall confidence:** High / Medium / Low — state what data is missing and how it affects the recommendation.

#### Final Recommendation

Provide a clear **GO / CONDITIONAL GO / NO-GO** with:
- Top 3 reasons supporting the recommendation
- Top 3 risks/challenges
- Suggested product positioning (if GO)
- Suggested price point (if GO)
- Suggested differentiation angle (if GO)
- Top 5 keywords to target (with search volumes)
- Estimated time to first sale (if GO)

---

## Output Structure

### File Organization

```
outputs/research/niche-analysis/
├── briefs/                           # Main analysis reports
│   └── {niche-slug}-niche-analysis-YYYY-MM-DD.md
├── data/
│   └── YYYY-MM-DD/                   # Raw data
│       ├── datadive-competitors-{niche-slug}-YYYY-MM-DD.json
│       ├── datadive-keywords-{niche-slug}-YYYY-MM-DD.json
│       ├── datadive-roots-{niche-slug}-YYYY-MM-DD.json
│       ├── datadive-ranking-juice-{niche-slug}-YYYY-MM-DD.json
│       ├── sp-api-pricing-{niche-slug}-YYYY-MM-DD.json
│       ├── sp-api-catalog-{niche-slug}-YYYY-MM-DD.json
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
**Data Confidence:** High / Medium / Low

---

## Executive Summary
{2-3 sentence overview: market size, competition level, key opportunity}

**Data sources used:** DataDive (Jungle Scout) ✅/❌ | SP-API ✅/❌ | Seller Board ✅/❌ | Apify (reviews) ✅/❌

---

## Market Landscape

### Niche Overview
| Metric | Value | Source |
|---|---|---|
| Est. Monthly Revenue | ${X} | DataDive (Jungle Scout) |
| Est. Monthly Units | {X} | DataDive (Jungle Scout) |
| Number of Competitors Analyzed | {X} | DataDive |
| Average Selling Price (ASP) | ${X} | SP-API |
| Median Price | ${X} | SP-API |
| Price Range | ${min} - ${max} | SP-API |
| Avg Rating (top 15) | {X} stars | DataDive |
| Avg Review Count (top 15) | {X} | DataDive |
| Top 3 Market Share | {X}% | DataDive |
| Total Niche Search Volume (Core) | {X}/mo | DataDive |

### Top 15 Competitors

| # | Brand | ASIN | Price | BSR | Rating | Reviews | Monthly Units | Monthly Revenue | Market Share | Listing Score |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | {brand} | {asin} | ${price} | {bsr} | {rating} | {reviews} | {units} | ${rev} | {share}% | {score}/100 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

*Sales data: Jungle Scout estimates via DataDive. Pricing: Amazon SP-API. Listing Score: DataDive Ranking Juice.*

### Market Concentration
- **Top 3 hold {X}%** of estimated revenue
- {Observation about market concentration — monopoly? fragmented? etc.}

---

## Pricing Analysis

### Price Tiers
| Tier | Price Range | # Products | Avg Rating | Avg Reviews | Revenue Share | Notes |
|---|---|---|---|---|---|---|
| Budget | ${X}-${X} | {n} | {rating} | {reviews} | {X}% | {what you get} |
| Mid | ${X}-${X} | {n} | {rating} | {reviews} | {X}% | {what you get} |
| Premium | ${X}-${X} | {n} | {rating} | {reviews} | {X}% | {what you get} |

*Pricing from SP-API `get_competitive_pricing` — reflects current Buy Box prices.*

### Price Gaps
{Identify underserved price points or value propositions}

---

## Keyword Landscape

### Search Volume Summary
| Metric | Value |
|---|---|
| Total Core keyword search volume | {X}/mo |
| Total Core + Related search volume | {X}/mo |
| # Core keywords | {X} |
| # Related keywords | {X} |
| Top keyword | {keyword} ({volume}/mo) |

### Top 20 Keywords by Search Volume
| Keyword | Search Volume | Relevancy | Best Rank in Niche | # Competitors Ranking | Opportunity |
|---|---|---|---|---|---|
| {keyword} | {volume}/mo | Core | #{rank} | {X}/15 | High/Med/Low |

*Data: DataDive Master Keyword List with real search volumes.*

### Keyword Root Themes
| Root | Frequency | Broad Search Volume | Theme |
|---|---|---|---|
| {root} | {X} | {volume} | {what it represents} |

### Ranking Gaps (High-Value)
{Keywords with SV > 500 where fewer than 3 competitors rank in top 10}

### Long-tail Opportunities
{Keywords SV 200-1,000 with 0-1 competitors ranking}

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

| Competitor | Key Strengths | Key Weaknesses | Rating | Reviews | Listing Score |
|---|---|---|---|---|---|
| {brand} (ASIN) | {strengths} | {weaknesses} | {rating} | {count} | {score}/100 |

---

## Listing & Ranking Opportunities

### Ranking Juice Analysis
| Competitor | Title Score | Bullets Score | Description Score | Overall | Revenue | Vulnerability |
|---|---|---|---|---|---|---|
| {brand} | {X} | {X} | {X} | {X}/100 | ${rev}/mo | High/Med/Low |

*High vulnerability = high revenue + low listing score — winning despite poor optimization.*

### Most Vulnerable Competitors
{Top sellers with weak listings — entering with optimized copy could capture share}

---

## Gap Analysis & Opportunities

### Identified Opportunities (Ranked)

#### 1. {Opportunity Name}
- **Type:** Price / Feature / Quality / Audience / Listing / Keyword / Bundle
- **Demand Signal:** Strong / Moderate / Weak
- **Data Source:** {what data supports this — SV, review count, ranking gap, etc.}
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
| Market Size | {X}/5 | {why — cite actual revenue from DataDive} |
| Competition Intensity | {X}/5 | {why} |
| Price Opportunity | {X}/5 | {why — cite SP-API pricing data} |
| Differentiation Potential | {X}/5 | {why — cite review gaps + listing gaps} |
| Customer Pain Points | {X}/5 | {why — cite review analysis} |
| Keyword Accessibility | {X}/5 | {why — cite search volumes + ranking gaps} |
| Listing Quality Gap | {X}/5 | {why — cite Ranking Juice scores} |
| Brand Alignment | {X}/5 | {why} |
| **TOTAL** | **{X}/40** | |

### Data Confidence
| Source | Used? | Notes |
|---|---|---|
| DataDive competitors | ✅/❌ | {notes} |
| DataDive keywords | ✅/❌ | {notes} |
| DataDive ranking juice | ✅/❌ | {notes} |
| SP-API pricing | ✅/❌ | {notes} |
| SP-API catalog | ✅/❌ | {notes} |
| Seller Board | ✅/❌ | {notes} |
| Apify reviews | ✅/❌ | {notes} |

---

## Recommendation

**Verdict: {GO / CONDITIONAL GO / NO-GO}**

### Why
1. {Reason 1 — cite data}
2. {Reason 2 — cite data}
3. {Reason 3 — cite data}

### Risks
1. {Risk 1}
2. {Risk 2}
3. {Risk 3}

### If Proceeding
- **Suggested positioning:** {how to position the product}
- **Target price point:** ${X} (based on SP-API gap analysis)
- **Differentiation angle:** {what makes you different}
- **Must-have features:** {non-negotiables based on reviews}
- **Top 5 target keywords:** {keyword (SV)} — from DataDive
- **Weakest competitor to displace:** {brand/ASIN — low listing score, moderate revenue}
- **Next steps:** {what to do next — product development, listing, etc.}

---

*Generated by Niche Category Analysis skill — {date}*
*Data sources: DataDive (Jungle Scout) | Amazon SP-API | Seller Board | Apify*
```

### Snapshot Format (JSON)

Save for future comparison:

```json
{
  "niche": "{niche-name}",
  "date": "YYYY-MM-DD",
  "primary_keyword": "{keyword}",
  "data_sources": {
    "datadive": true,
    "sp_api": true,
    "seller_board": false,
    "apify_reviews": true
  },
  "metrics": {
    "est_monthly_revenue": 0,
    "est_monthly_units": 0,
    "avg_selling_price": 0,
    "median_price": 0,
    "avg_rating": 0,
    "avg_reviews": 0,
    "top_3_concentration": 0,
    "competitor_count": 0,
    "total_core_search_volume": 0,
    "core_keyword_count": 0,
    "related_keyword_count": 0,
    "avg_listing_score": 0
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
      "monthly_units": 0,
      "monthly_revenue": 0,
      "market_share": 0,
      "listing_score": 0,
      "data_source": "datadive"
    }
  ],
  "keywords": [
    {
      "keyword": "",
      "search_volume": 0,
      "relevancy": "Core/Related/Outlier",
      "best_organic_rank": 0,
      "competitors_ranking": 0,
      "opportunity": "High/Med/Low"
    }
  ],
  "keyword_roots": [
    {
      "root": "",
      "frequency": 0,
      "broad_search_volume": 0
    }
  ],
  "viability_score": 0,
  "viability_max": 40,
  "verdict": "GO/CONDITIONAL GO/NO-GO",
  "data_confidence": "High/Medium/Low"
}
```

---

## Efficiency & Cost Controls

| Constraint | Limit |
|---|---|
| DataDive API calls | Minimal — reuse existing niches when possible |
| SP-API catalog calls | Max 15 (one per competitor) |
| SP-API pricing calls | Max 15 (one per competitor) |
| Niche Dive creation | **Requires user approval** (costs tokens) |
| Max ASINs scraped (reviews) | 5 via Apify |
| Max reviews per ASIN | 50 |
| Apify batch size | 5 ASINs per call |
| Timeout per scrape call | 3 minutes |
| Total token budget | <80K |
| Total API cost target | <$0.25 (Apify only; MCP calls are free) |

**If a DataDive call fails:** Fall back to SP-API data. If SP-API also fails, fall back to Apify scraping + BSR estimation (legacy mode). Note degraded data confidence in report.

**If SP-API rate-limited:** Wait 2 seconds and retry once. If still failing, skip and note in report.

**If a review scrape times out:** Use whatever data was collected. Note gaps in the report. Do NOT retry automatically — ask user first.

---

## Fallback: Legacy Mode (No DataDive Data)

If DataDive niche doesn't exist AND user declines to create a niche dive:

1. Use SP-API `search_catalog` to find competitors
2. Use SP-API `get_catalog_item` for BSR + category data
3. Use SP-API `get_competitive_pricing` for pricing
4. **Fall back to BSR estimation tables** for sales (see below)
5. Extract keywords from titles instead of DataDive keyword data
6. Skip Ranking Juice analysis (not available without DataDive)
7. **Mark report as "Limited Data Mode"** and note which sections are estimates

### BSR-to-Sales Estimation Table (LEGACY FALLBACK ONLY)

⚠️ **Use ONLY when DataDive data is unavailable.** Jungle Scout actuals are far more accurate.

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

---

## Error Handling

| Error | Action |
|---|---|
| DataDive niche not found | Offer to create niche dive (with token cost warning) OR fall back to SP-API + Apify |
| DataDive niche dive fails | Fall back to SP-API + Apify legacy mode |
| DataDive API key invalid | STOP. Ask user to check DATADIVE_API_KEY in .env |
| SP-API rate limited | Wait 2s, retry once. If still fails, skip and note |
| SP-API auth expired | STOP. Ask user to re-authorize app in Seller Central |
| No search results for keyword | Ask user to refine keyword, suggest alternatives |
| Fewer than 5 products found | Warn: niche may be too narrow. Proceed with available data |
| Reviews scraper returns <10 reviews | Note low review count, analysis may be thin |
| All data sources fail | STOP. Report error. Ask user to try later |
| Timeout on batch | Use partial data, note which ASINs are missing |
| DataDive token balance low | Warn user, suggest using existing niche or SP-API fallback |

---

## Integration with Other Skills

| This skill provides... | To... |
|---|---|
| Competitor ASINs + actual revenue | **Daily Market Intel** (add to tracking with real baselines) |
| Keywords with search volumes | **Listing Creator** (prioritize by SV, not guessing) |
| Customer language from reviews | **Listing Creator** (bullet copy) |
| Competitor weaknesses + listing scores | **Image Planner** (visual differentiation) |
| Keyword map with SV + relevancy | **Negative Keyword Generator** (data-driven irrelevant terms) |
| Review themes | **Customer Review Analyzer** (ongoing monitoring) |
| Ranking Juice gaps | **Listing Optimizer** (baseline for new listings) |

**After a GO verdict, suggest:**
1. Add top competitors to `context/competitors.md`
2. Add niche keywords (with search volumes) to `context/search-terms.md`
3. Run **Listing Creator** for the new product concept (pass DataDive nicheId for keyword data)
4. Run **Image Planner** based on competitor image analysis
5. Set up a **Rank Radar** in DataDive for the seed ASIN to track rankings over time

---

## Pre-Execution Checklist

Before starting, confirm:
- [ ] User provided at least 1 niche keyword
- [ ] Keyword makes sense as an Amazon search term
- [ ] Check if DataDive niche already exists (free) before creating new one (costs tokens)
- [ ] If niche dive needed — user approved token spend
- [ ] Output folder exists or will be created

---

## Execution Order Summary

1. **Gather input** — Keyword(s), seed ASIN, context, known competitors, already-in-niche?
2. **Check DataDive** — Does niche exist? If yes, use it. If no, offer niche dive or SP-API fallback
3. **Pull competitor data** — `get_niche_competitors` (DataDive) → actual sales/revenue
4. **Enrich with SP-API** — `get_catalog_item` for first-party details on top 15
5. **Calculate market metrics** — Using Jungle Scout actuals, not BSR tables
6. **Pull Seller Board data** — If already in niche, add internal context
7. **Analyze pricing** — `get_competitive_pricing` (SP-API) for real-time Buy Box data
8. **Pull keyword data** — `get_niche_keywords` + `get_niche_roots` (DataDive) with real search volumes
9. **Map keyword landscape** — Ranking gaps, long-tail opportunities, root themes
10. **Pull listing scores** — `get_niche_ranking_juices` (DataDive) for optimization gaps
11. **Scrape reviews** — Top 5 competitors via Apify, 50 reviews each
12. **Analyze reviews** — Praise, complaints, wishes, patterns
13. **Identify gaps** — Price, feature, quality, audience, listing, keyword, bundle
14. **Score viability** — 8-factor scorecard (now includes Listing Quality Gap)
15. **Rate data confidence** — Which sources were available and used
16. **Generate report** — Full brief with data-sourced recommendation
17. **Save snapshot** — Enhanced JSON for future comparison
18. **Present summary** — Key findings to user
19. **Suggest next steps** — If GO, recommend follow-up actions with specific DataDive nicheId

---

## ⚠️ AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/niche-category-analysis/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Goals:**
- [ ] Goal 1
- [ ] Goal 2

**Result:** ✅ Success / ⚠️ Partial / ❌ Failed

**Data sources used:** DataDive ✅/❌ | SP-API ✅/❌ | Seller Board ✅/❌ | Apify ✅/❌

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
