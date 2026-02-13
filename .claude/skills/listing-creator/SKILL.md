---
name: listing-creator
description: Creates Amazon product listings based on competitor analysis, Rufus Q&A, top keywords, and Craftiloo product specs
triggers:
  - create a listing
  - new listing
  - listing for
  - make a listing
  - listing creator
  - amazon listing
  - write listing
output_location: outputs/research/listings/
---

# Listing Creator

**USE WHEN** user says: "create a listing", "new listing", "listing for", "make a listing", "listing creator", "amazon listing", "write listing"

---

## What This Does

Creates Amazon-optimized product listings by:
- **Researching** top competitors in the niche
- **Analyzing** competitor titles, bullets, and content
- **Identifying** Rufus questions customers are asking
- **Extracting** top keywords for the category
- **Generating** complete listing with title, bullets, and backend keywords
- **Including** product specifications from Craftiloo catalog

---

## Organization & Efficiency Standards

**CRITICAL: Follow these standards for EVERY run:**

### File Organization
```
outputs/research/listings/
├── briefs/              # Final listings (copy-paste ready)
├── research/            # Competitor and keyword research
│   ├── competitors/     # Competitor listing analysis
│   ├── keywords/        # Keyword research data
│   └── rufus/           # Rufus Q&A analysis
├── data/                # Raw scraped data
└── README.md            # Folder guide
```

### Naming Conventions (STRICT)
- **Final listings:** `{product-slug}-listing-YYYY-MM-DD.md`
- **Research reports:** `{product-slug}-research-YYYY-MM-DD.md`
- **Competitor analysis:** `{product-slug}-competitors-YYYY-MM-DD.md`
- **Q&A analysis:** `{product-slug}-qa-YYYY-MM-DD.md`
- **Keyword data:** `{product-slug}-keywords-YYYY-MM-DD.json`

### Efficiency Targets
- <80K tokens per run
- <$0.20 cost (if using paid APIs)
- <10 minutes end-to-end
- 1 final listing per run

---

## CRITICAL RULES

### US Market Standards (MANDATORY)
- **ALL measurements in inches** (not cm) - US market only
- **ALL weights in pounds/ounces** (not grams/kg)
- Convert from metric if needed (1 inch = 2.54 cm)
- Example: "6.3 inch hoop" NOT "16cm hoop"

### Keyword Research is #1 Priority
- **Primary keywords = HIGH SEARCH VOLUME terms** people actually type into Amazon
- Primary keywords are NOT descriptive phrases like "ages 8-12" or "beginner"
- Primary keywords ARE search terms like: "embroidery kit", "embroidery kit for kids", "craft kit for girls"
- **Front-load title with highest-volume keyword first**
- Research competitor titles to find what keywords rank

---

## Process

### Phase 0: Gather Required Information (BEFORE STARTING)

**STOP and ask user if missing:**
1. **Product SKU or name** - Which product from the catalog?
2. **Target niche keywords** - What do customers search for? (e.g., "embroidery kit for kids", "Barbie craft kit")
3. **Target age range** - What age is this product for?

**Do NOT proceed without niche keywords.** These drive the entire listing strategy.

### Phase 1: Understand the Product

**Required inputs from user:**
1. **Product SKU or name** from Craftiloo catalog (e.g., "CS01" or "Cross Stitch Backpack")
2. **Target niche/category** on Amazon (e.g., "kids cross stitch kit", "embroidery kit for beginners")
3. **Target age** (e.g., "8+", "ages 7-12")

**Load product specs from:**
- `context/products.md` - Get exact product details, contents, pricing
- `context/hero-products.md` - Get our ASIN, key selling points if it's a hero product
- **Convert all measurements to inches/pounds for US market**

### CRITICAL: Check Context Files Before Any Research

**ALWAYS check these context files BEFORE scraping or searching for competitors/keywords:**

| Context File | What It Contains | Use For |
|-------------|-----------------|---------|
| `context/competitors.md` | **Competitors by category with ASINs, market share, strengths/weaknesses** | Get competitor ASINs — DO NOT scrape for competitors if they exist here |
| `context/search-terms.md` | **Search terms by category with volume and relevance scores** | Get keyword data with ACTUAL search volume — use these instead of guessing |
| `context/hero-products.md` | **Our hero products with ASINs, contents, key selling points** | Get our own product ASIN and detailed info |
| `context/products.md` | **Full product catalog with specs, contents, dimensions** | Get exact kit contents, measurements, pricing |

**Lookup order:** Identify product category → check `context/competitors.md` for ASINs → check `context/search-terms.md` for keywords with volume → load product specs → only use Apify for data NOT in context files (reviews, Q&A, current pricing/BSR).

### Phase 2: Competitor Research

**First: Check `context/competitors.md`** for the product's category. If competitors with ASINs are listed, USE THOSE. Only scrape Apify for additional data not in context files.

If competitors are NOT in context files, use Apify Amazon scraper with search query:
```json
{
  "searchTerms": ["{target keyword}"],
  "country": "US",
  "maxResults": 10
}
```

**For each top competitor, extract:**
- **Title** - Full product title
- **Price** - Current selling price
- **BSR** - Best Seller Rank
- **Rating** - Star rating
- **Review count** - Total reviews
- **Bullets** - All 5 bullet points (if accessible)
- **A+ Content** - Key selling points from description

**Analyze patterns:**
- What keywords appear in EVERY title?
- What benefits are mentioned in bullets?
- What specifications are highlighted?
- What ages/skill levels are targeted?
- What "included" items are emphasized?

### Phase 3: Keyword Research (CRITICAL)

**UNDERSTAND: Primary keywords = what customers TYPE INTO AMAZON SEARCH**

These are NOT descriptive phrases. These ARE actual search queries with volume.

**Examples of PRIMARY keywords (high search volume):**
- "embroidery kit"
- "embroidery kit for kids"
- "craft kit for girls"
- "sewing kit for kids"
- "cross stitch kit"

**Examples of what are NOT primary keywords:**
- "ages 8-12" (descriptor, not a search term)
- "beginner" (qualifier, low volume alone)
- "screen-free activity" (benefit, not search term)
- "birthday gift" (intent, but low as primary)

**Primary keyword sources:**

1. **Competitor titles** - What keywords appear in TOP 3 BSR listings?
2. **Amazon autocomplete** - Type main term, see what Amazon suggests
3. **Amazon search results** - What keywords do #1-5 ranked products use?
4. **Category browse** - What's the category called?

**Build keyword list:**
- **Primary keywords** (3-5) - HIGHEST search volume, must be in title
- **Secondary keywords** (5-10) - Medium volume, in title or bullets
- **Long-tail keywords** (10-20) - Specific phrases, backend keywords

**Keyword priority for title (LEFT TO RIGHT):**
1. **Highest volume primary keyword** (e.g., "Embroidery Kit")
2. **Second highest volume** (e.g., "for Kids")
3. **Audience modifier** (e.g., "Girls")
4. **Age if relevant** (e.g., "Ages 8+")
5. **Brand/theme** (e.g., "Barbie")
6. **Contents/benefit** (e.g., "8 Projects, Complete Set")

### Phase 4: Competitor Q&A Scraping

**CRITICAL: Scrape actual customer questions from competitor listings.**

Rufus pulls from the same Q&A data - these are REAL questions customers ask.

**Use Apify to scrape Q&A sections:**

Option 1: `junglee/amazon-product-scraper` (includes Q&A)
```json
{
  "asins": ["B08T5QC9FS", "B0B7JHN4F1", "B0CM9JKNCC"],
  "country": "US"
}
```

Option 2: Dedicated Q&A scraper `epctex/amazon-questions-answers-scraper`
```json
{
  "startUrls": [
    "https://www.amazon.com/ask/questions/asin/B08T5QC9FS"
  ],
  "maxQuestions": 20
}
```

**For each top 3-5 competitor, extract:**
- All customer questions (sorted by votes/helpfulness)
- Seller answers
- Customer answers
- Question categories/themes

**Categorize questions by theme:**

| Theme | Example Questions |
|-------|-------------------|
| **Contents** | "What's included?", "Does it come with needles?" |
| **Age/Skill** | "Is this good for a 6 year old?", "Beginner friendly?" |
| **Safety** | "Are the needles sharp?", "Non-toxic materials?" |
| **Quality** | "Does the thread tangle easily?", "Good quality hoops?" |
| **Completion** | "How long does it take?", "How many projects?" |
| **Instructions** | "Are instructions easy to follow?", "Video tutorial?" |
| **Gift** | "Good birthday gift?", "Nice packaging?" |
| **Size** | "How big are finished projects?", "Hoop size?" |

**Save Q&A research to:** `outputs/research/listings/research/rufus/{product-slug}-qa-YYYY-MM-DD.md`

---

### Phase 5: Q&A → Bullet Mapping

**Take scraped questions and map to bullet answers:**

| Top Customer Questions | Answer in Bullet |
|------------------------|------------------|
| "What's included?" | "COMPLETE KIT INCLUDES: {exact list from products.md}" |
| "Good for beginners?" | "BEGINNER-FRIENDLY: Step-by-step illustrated instructions..." |
| "What age is this for?" | "AGES {X}-{Y}: Designed specifically for..." |
| "Are needles safe?" | "SAFE FOR KIDS: Plastic blunt-tip needles, non-toxic..." |
| "How long to complete?" | "QUICK WINS: Each project takes {X} hours..." |
| "Good gift?" | "GIFT-READY: Comes in beautiful packaging..." |

**Priority order for bullets:**
1. **Most-asked question** → Bullet 1 or 2
2. **Safety concerns** → Must address (especially for kids products)
3. **Contents/value** → Always include full kit contents
4. **Skill level** → Helps buyer confidence
5. **Gift appeal** → Helps conversion

---

### Phase 6: Generate Listing

---

## Output Format

### Final Listing Document

```markdown
# Amazon Listing: {Product Name}

**SKU:** {Craftiloo SKU}
**Target Category:** {Amazon category}
**Generated:** {YYYY-MM-DD}

---

## TITLE (200 characters max)

{Optimized title with primary keywords front-loaded}

---

## BULLET POINTS (5 bullets, ~500 chars each)

### Bullet 1: Main Value Proposition
{BENEFIT-FIRST hook + key differentiator}

### Bullet 2: What's Included
{COMPLETE KIT INCLUDES: detailed list from products.md}

### Bullet 3: Target Audience + Safety
{AGE/SKILL appropriate + safety features}

### Bullet 4: Experience/Activity Benefits
{Educational value, bonding, skill-building}

### Bullet 5: Quality + Gift Appeal
{Materials quality + gift-ready packaging}

---

## BACKEND KEYWORDS (249 bytes max)

```
{comma-separated keywords NOT in title, no duplicates, no brand names}
```

---

## RESEARCH SUMMARY

### Top Competitors Analyzed
| # | ASIN | Title | Price | BSR | Reviews | Rating |
|---|------|-------|-------|-----|---------|--------|
| 1 | B0XXXXXXX | {title} | ${price} | {bsr} | {count} | {stars} |

### Keyword Strategy
- **Primary:** {list}
- **Secondary:** {list}
- **Long-tail:** {list}

### Customer Q&A Analysis (Scraped from Competitors)

**Top Questions by Theme:**

| Theme | Question | Votes | Answered In |
|-------|----------|-------|-------------|
| Contents | "Does it include needles?" | 42 | Bullet 2 |
| Age | "Good for 7 year old?" | 38 | Bullet 3 |
| Safety | "Are needles sharp?" | 35 | Bullet 3 |
| Quality | "Is the thread good quality?" | 28 | Bullet 5 |
| Time | "How long to complete one?" | 24 | Bullet 4 |

**Questions Addressed in Listing:**
- [x] What's included? → Bullet 2
- [x] Beginner-friendly? → Bullet 1
- [x] Age appropriate? → Bullet 3
- [x] Safety? → Bullet 3
- [x] Time to complete? → Bullet 4
- [x] Instructions included? → Bullet 2
- [ ] Finished size? → (add if common question)

### Product Specs from Catalog
{Copy from products.md}

---

## COPY-PASTE READY

### Title
{exact title to paste}

### Bullets (plain text)
{bullet 1}
{bullet 2}
{bullet 3}
{bullet 4}
{bullet 5}

### Backend Keywords
{exact keywords to paste}
```

---

## Listing Rules & Best Practices

### Title Rules
- **200 character limit** (aim for 150-180)
- **Front-load** primary keyword
- **Include:** Product type, audience, age (if kids), key benefit
- **NO:** All caps (except brand), promotional claims, symbols
- **Pattern:** {Brand} {Primary Keyword} {Secondary Keyword} {For Audience} - {Key Benefit/Contents}

### Bullet Rules
- **Start with BENEFIT in CAPS** (e.g., "COMPLETE KIT INCLUDES:")
- **~500 characters each** (Amazon limit varies)
- **Lead with benefit**, then feature
- **Answer Rufus questions** naturally
- **Include keywords** but keep readable
- **ALL measurements in INCHES** (US market) - convert from cm if needed
- **ALL weights in POUNDS/OUNCES** - convert from grams if needed
- **NO:** HTML, special characters, promotional claims

### Backend Keyword Rules
- **249 bytes max** (not 250 - safe limit)
- **NO:** Brand names (yours or competitors)
- **NO:** Words already in title
- **NO:** Punctuation (except spaces and hyphens)
- **NO:** Repeated words
- **INCLUDE:** Synonyms, misspellings, Spanish terms, related searches
- **Space-separated** (not comma-separated in actual backend)

---

## Data Sources

| Source | What We Get | How |
|--------|-------------|-----|
| **context/products.md** | Product specs, contents, pricing | Local file |
| **Apify - Product Scraper** | Competitor listings, rankings, reviews, bullets | `junglee/amazon-product-scraper` |
| **Apify - Q&A Scraper** | Customer questions & answers from listings | `epctex/amazon-questions-answers-scraper` |
| **Apify - Search Scraper** | Top competitors for keyword | `junglee/amazon-search-scraper` |
| **Web Search** | Keyword trends, category patterns | WebSearch tool |

---

## Execution Checklist

When user triggers this skill:

**Setup:**
- [ ] Confirm product (SKU or name from catalog)
- [ ] Confirm target niche/category keywords
- [ ] Load product specs from `context/products.md`

**Research (Apify):**
- [ ] Search Amazon for top 5-7 competitors in niche
- [ ] Scrape competitor titles, bullets, prices, rankings
- [ ] **Scrape Q&A sections from top 3-5 competitors**
- [ ] Analyze keyword patterns from competitor titles

**Analysis:**
- [ ] Categorize Q&A by theme (contents, age, safety, etc.)
- [ ] Identify most-asked questions (by vote count)
- [ ] Map questions to bullet point answers
- [ ] Prioritize which questions MUST be answered

**Generation:**
- [ ] Generate optimized title (primary keywords first)
- [ ] Generate 5 bullets (answer top Q&A themes)
- [ ] Generate backend keywords (no title duplicates)

**Output:**
- [ ] Save Q&A research to `research/rufus/`
- [ ] Save competitor analysis to `research/competitors/`
- [ ] Save final listing to `briefs/`
- [ ] Present copy-paste ready output to user

---

## Example Workflow

**User:** "Create a listing for CS01 - the Cross Stitch Backpack for girls"

**Process:**

1. **Load CS01 specs** from products.md:
   - 5 plastic hoops, 4 needles, 5 designs, keychain clips, instructions, gift box

2. **Search Amazon:** "cross stitch kit for kids girls"

3. **Scrape top 5 competitors:**
   - Titles, bullets, prices, rankings
   - Get ASINs: B08T5QC9FS, B0B7JHN4F1, B0CM9JKNCC, etc.

4. **Scrape Q&A sections** from top 3 competitors:
   ```
   Top questions found:
   - "What age is this for?" (52 votes)
   - "Does it include everything needed?" (48 votes)
   - "Are the needles safe for kids?" (41 votes)
   - "How many projects can you make?" (35 votes)
   - "Is this good for beginners?" (32 votes)
   ```

5. **Analyze keyword patterns:**
   - "cross stitch kit for kids"
   - "beginner embroidery"
   - "girls craft kit"
   - "ages 8-12"

6. **Map Q&A to bullets:**
   | Question | Bullet | Answer |
   |----------|--------|--------|
   | Age range? | 3 | "AGES 6-12: Perfect for..." |
   | Everything included? | 2 | "COMPLETE KIT: 5 hoops, 4 needles..." |
   | Safe needles? | 3 | "SAFE: Blunt plastic needles..." |
   | How many projects? | 1 | "5 UNIQUE DESIGNS: Create..." |
   | Good for beginners? | 1 | "BEGINNER-FRIENDLY: Easy..." |

7. **Generate listing** with all research incorporated

---

## Error Handling

| Issue | Action |
|-------|--------|
| Product not found in catalog | Ask user to clarify or add to products.md |
| No competitors found | Broaden search terms, try category browse |
| Apify rate limit | Wait 60s, retry |
| **No Q&A found on listing** | Use generic category questions + review mining |
| **Q&A scraper fails** | Fall back to web search for common questions |
| Backend keywords > 249 bytes | Trim lowest-priority keywords |

---

## Tips for Best Results

1. **Be specific about target niche** - "kids cross stitch" vs "adult embroidery"
2. **Review competitors manually** if output looks off
3. **Test title in Amazon search** to see if it displays well
4. **A/B test** different title structures over time
5. **Update keywords** based on PPC search term reports

---

## Upload to Notion

**After generating the listing, upload it to Notion.**

### Notion Page ID (ALWAYS use this)

**Parent page:** "Product Listing Development"
**Page ID:** `30557318-d05c-806a-a94f-f5a439d94d10`
**URL:** https://www.notion.so/Product-Listing-Development-30557318d05c806aa94ff5a439d94d10

**ALWAYS create child pages under this parent page.** Do not ask the user which database to use.

### Search Before Creating

1. **Search for existing product page** using Notion MCP `notion-search` with the product name
2. **If page exists** → append the listing section to it (don't create a duplicate)
3. **If page doesn't exist** → create a new page

### Page Properties

When creating a new page or updating an existing one:

| Property | Type | Value |
|----------|------|-------|
| **Title** | Title | `{Product Name}` |
| **SKU** | Rich Text | `{SKU}` |
| **Status** | Select | `Draft` |
| **Date** | Date | `{YYYY-MM-DD}` |
| **Primary Keywords** | Rich Text | `{keyword1}, {keyword2}, ...` |
| **Has Listing** | Checkbox | `true` |

### Page Content (Listing Section)

Append these blocks to the page:

1. **Divider**
2. **Heading 2:** `Amazon Listing`
3. **Heading 3:** `Title`
4. **Quote block:** The optimized title (easy to copy)
5. **Paragraph:** Character count and keyword placement notes
6. **Heading 3:** `Bullet Points`
7. **Numbered list:** All 5 bullets (each with its theme label in bold)
8. **Heading 3:** `Backend Keywords`
9. **Code block:** Backend keywords (easy to copy, no formatting issues)
10. **Heading 3:** `Research Summary`
11. **Toggle:** `Competitor Analysis` → competitor comparison table
12. **Toggle:** `Keyword Strategy` → primary, secondary, long-tail keywords
13. **Toggle:** `Customer Q&A Analysis` → Q&A themes, top questions, which bullet addresses each

### Upload Rules

- **Search before creating** — never duplicate pages
- **Use quote blocks** for the title — visually distinct and easy to copy
- **Use code blocks** for backend keywords — prevents formatting issues
- **Use toggle blocks** for research sections — keeps the page scannable
- **Update `Has Listing` checkbox** to `true`
- **If an image plan already exists on the page**, append the listing section BEFORE the image plan section
- **Tell the user** what you did: "Uploaded listing to Notion page: {product name}" or "Added listing to existing Notion page for {product name}"

### Compatibility with Parent Skill

This Notion structure is **compatible with the Product Listing Development skill** (`product-listing-development`). Both skills use the same:
- Page properties (Title, SKU, Status, Date, checkboxes)
- Section structure (Listing section + Image Plan section)
- Database location (saved in `context/business.md`)

If the parent skill runs, it handles Notion upload for both. If this skill runs standalone, it creates/updates the page with just the listing section.

---

## Notes

- Run this skill ONCE per product variant
- Update listing based on PPC data after 30 days
- Competitor landscape changes - re-run quarterly
- Always verify character counts before pasting
