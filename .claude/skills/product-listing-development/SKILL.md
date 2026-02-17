---
name: product-listing-development
description: Orchestrates full product listing development — shared research, Amazon listing creation, and image planning in one efficient workflow
triggers:
  - product listing development
  - full listing
  - listing + images
  - launch product
  - develop listing
  - complete listing
output_location: outputs/research/product-launch/
---

# Product Listing Development

**USE WHEN** user says: "product listing development", "full listing", "listing + images", "launch product", "develop listing", "complete listing"

---

## What This Does

**Parent orchestrator** that combines listing creation and image planning into one efficient workflow:

1. Gathers all inputs **once**
2. Checks for **existing work** (skips what's already done)
3. Runs shared research **once** (competitors, reviews, Q&A, keywords)
4. Generates the **Amazon listing** (title, bullets, backend keywords)
5. Generates the **image plan** (copy table, image-by-image detail)
6. Uploads everything to **one Notion page**

**Saves ~50% of API calls** compared to running both skills separately.

---

## Organization & Efficiency Standards

### File Organization

```
outputs/research/product-launch/
├── {product-slug}/
│   ├── research/              # Shared research (used by both)
│   │   ├── competitors/       # Competitor analysis
│   │   ├── keywords/          # Keyword research
│   │   ├── rufus/             # Q&A analysis
│   │   └── reviews/           # Review mining
│   ├── listing/               # Listing output
│   │   └── {product-slug}-listing-YYYY-MM-DD.md
│   ├── image-plan/            # Image plan output
│   │   └── {product-slug}-image-plan-YYYY-MM-DD.md
│   └── README.md              # Product folder guide
├── README.md                  # Main folder guide
```

**ALSO saves copies to the individual skill output folders:**
- Listing → `outputs/research/listings/briefs/{product-slug}-listing-YYYY-MM-DD.md`
- Image plan → `outputs/research/image-plans/briefs/{product-slug}-image-plan-YYYY-MM-DD.md`

### Naming Conventions (STRICT)

- **Product folders:** `{product-slug}/` (e.g., `barbie-embroidery/`, `latch-hook-rainbow-heart/`)
- **Listings:** `{product-slug}-listing-YYYY-MM-DD.md`
- **Image plans:** `{product-slug}-image-plan-YYYY-MM-DD.md`
- **Research files:** `{type}-{product-slug}-YYYY-MM-DD.md`

### Efficiency Targets

- <200K tokens per full run (both outputs with all options and detail)
- <120K tokens if one output already exists
- <$0.30 cost per full run (Apify)
- <20 minutes end-to-end
- Minimal file count

---

## Step 0: Check for Existing Work (CRITICAL — DO THIS FIRST)

**Before doing ANY research or generation, check what already exists.**

Generate the product slug from the product name (e.g., "Barbie Embroidery Kit" → `barbie-embroidery`).

### Check these locations:

| What | Where to Check | Glob Pattern |
|------|---------------|--------------|
| **Existing listing** | `outputs/research/listings/briefs/` | `{product-slug}-listing-*.md` |
| **Existing image plan** | `outputs/research/image-plans/briefs/` | `{product-slug}-image-plan-*.md` |
| **Existing shared research** | `outputs/research/product-launch/{product-slug}/research/` | Any files in subfolders |

### Decision Matrix

| Listing? | Image Plan? | Research? | Action |
|----------|------------|-----------|--------|
| No | No | No | **Full run** — research + listing + image plan |
| No | No | Yes | **Skip research** — generate both from existing research |
| Yes | No | Any | **Image plan only** — read existing listing's research, generate image plan |
| No | Yes | Any | **Listing only** — read existing image plan's research, generate listing |
| Yes | Yes | Any | **Ask user** — "Both already exist from [dates]. Want to redo one or both?" |

### When reusing existing work:

1. **Read the existing brief** to extract research data (competitors analyzed, keywords, Q&A insights)
2. **Tell the user** what you found: "Found existing listing from 2026-02-11. Skipping listing generation. Running image plan only."
3. **Use the same competitor ASINs** from the existing brief for consistency
4. **If existing brief is >30 days old**, mention it: "Existing listing is from [date] — 45 days ago. Want to refresh the research?"

---

## Step 1: Gather ALL Inputs (Once)

**Collect everything both skills need in one conversation:**

| Input | Required By | Ask If Missing |
|-------|------------|----------------|
| **Product name/SKU** | Both | Always — load specs from `context/products.md` |
| **Target niche keywords** | Listing (primary), Images (secondary) | Always — these drive the entire strategy |
| **Target age range** | Both | Always |
| **Competitor ASINs** (3-5) | Both | **CHECK CONTEXT FILES FIRST** (see below) |
| **Product differentiators** | Images (primary), Listing (secondary) | Always — what makes this product unique? |

### CRITICAL: Check Context Files Before Any Research

**ALWAYS check these context files BEFORE scraping or searching for competitors/keywords:**

| Context File | What It Contains | Use For |
|-------------|-----------------|---------|
| `context/competitors.md` | **Competitors by category with ASINs, market share, strengths/weaknesses** | Get competitor ASINs — DO NOT scrape for competitors if they exist here |
| `context/search-terms.md` | **Search terms by category with volume and relevance scores** | Get keyword data — use these instead of guessing or scraping |
| `context/hero-products.md` | **Our hero products with ASINs, contents, key selling points** | Get our own product ASIN and detailed info |
| `context/products.md` | **Full product catalog with specs, contents, dimensions** | Get exact kit contents, measurements, pricing |

### Lookup Order

1. **Identify the product category** (e.g., "Embroidery Kits for Kids", "Latch Hook Kits")
2. **Load `context/competitors.md`** → Find the matching category section → Extract competitor brands, ASINs, market share, strengths/weaknesses
3. **Load `context/search-terms.md`** → Find the matching category section → Extract search terms with volume data
4. **Load `context/hero-products.md`** → Find our product → Get ASIN, contents, key selling points
5. **Load `context/products.md`** → Get exact specs, dimensions (convert to inches for US market), pricing
6. **Only use Apify** for data NOT in context files (e.g., current reviews, Q&A, images)

**Do NOT proceed without niche keywords and product info.**

---

## Step 2: Shared Research (Run Once, Used by Both)

**This research feeds BOTH the listing and the image plan. Run it ONCE.**

**IMPORTANT:** Most competitor and keyword data is already in the context files. Only scrape for what's missing (reviews, Q&A, images, current pricing/BSR).

### 2a. Competitor Scraping

**First: Check `context/competitors.md`** for the product's category. If competitors with ASINs are listed, USE THOSE. Only scrape Apify for additional data (reviews, Q&A, images, current pricing).

If competitors are NOT in context files, use Apify Amazon scraper to find top competitors:
```json
{
  "searchTerms": ["{target keyword}"],
  "country": "US",
  "maxResults": 10
}
```

For each of the top 5-7 competitors, extract:
- **Title, price, BSR, rating, review count** (listing needs these)
- **Bullet points and A+ content** (listing needs these)
- **All product images and image order** (image planner needs these)
- **ASIN** (both need for Q&A scraping)

**Save to:** `outputs/research/product-launch/{product-slug}/research/competitors/{product-slug}-competitors-YYYY-MM-DD.md`

### 2b. Customer Review Mining

For our product AND top 3-5 competitors, extract:
- **Top praises** — Words/phrases happy customers use
- **Top complaints** — What worries buyers before purchasing
- **Common questions** — What people ask in reviews
- **Emotional triggers** — What makes someone click "Buy"
- **Gift buyer language** — How gift purchasers describe the product

Group into:
1. **Must-answer concerns** (address in listing bullets AND images or lose the sale)
2. **Emotional hooks** (leverage in bullet copy AND image copy)
3. **Differentiators to highlight** (what we do that competitors don't)

**Save to:** `outputs/research/product-launch/{product-slug}/research/reviews/{product-slug}-reviews-YYYY-MM-DD.md`

### 2c. Q&A Scraping

Use Apify to scrape Q&A sections from top 3-5 competitor ASINs:

Option 1: `junglee/amazon-product-scraper` (includes Q&A)
```json
{
  "asins": ["{asin1}", "{asin2}", "{asin3}"],
  "country": "US"
}
```

Option 2: `epctex/amazon-questions-answers-scraper`
```json
{
  "startUrls": [
    "https://www.amazon.com/ask/questions/asin/{asin}"
  ],
  "maxQuestions": 20
}
```

Categorize by theme and note which output uses each:

| Theme | Example Questions | Used In Listing | Used In Images |
|-------|-------------------|-----------------|----------------|
| **Contents** | "What's included?" | Bullet 2 | What's Included image |
| **Age/Skill** | "Good for a 6 year old?" | Bullet 3 | How It Works image |
| **Safety** | "Are needles sharp?" | Bullet 3 | (if relevant) |
| **Quality** | "Good quality materials?" | Bullet 5 | (indirect) |
| **Completion** | "How long to complete?" | Bullet 4 | Process/Result image |
| **Instructions** | "Easy to follow?" | Bullet 1 | How It Works image |
| **Gift** | "Good birthday gift?" | Bullet 5 | Gift image |
| **Size/Result** | "How big is finished project?" | Bullets | Result image |

**Save to:** `outputs/research/product-launch/{product-slug}/research/rufus/{product-slug}-qa-YYYY-MM-DD.md`

### 2d. Keyword Research

**First: Check `context/search-terms.md`** for the product's category. This file has search terms with volume AND relevance scores. Use these as your primary keyword source.

Build keyword list from context files + competitor titles + Amazon autocomplete:

- **Primary keywords** (3-5) — Highest search volume, must be in title
- **Secondary keywords** (5-10) — Medium volume, in title or bullets
- **Long-tail keywords** (10-20) — Backend keywords

**Save to:** `outputs/research/product-launch/{product-slug}/research/keywords/{product-slug}-keywords-YYYY-MM-DD.md`

---

## Step 3: Generate Listing (With Alternatives)

**Use the shared research to generate the Amazon listing.**

Follow **ALL rules** from the listing-creator skill (`.claude/skills/listing-creator/SKILL.md`):

- **Title rules:** 200 chars max, front-load primary keyword
- **Bullet rules:** 5 bullets, ~500 chars each, CAPS benefit lead, answer top Q&A themes
- **Backend keyword rules:** 249 bytes max, no title duplicates
- **US market standards:** Inches, pounds/ounces
- **Q&A → Bullet mapping:** Most-asked questions drive bullet priority
- **Keyword priority in title:** Highest volume → left, lowest → right

### CRITICAL: Generate Multiple Options

**Do not generate just one version. Generate options so the user can choose:**

- **Titles:** 1 recommended + 2-3 alternatives (each prioritizing different keyword strategy)
- **Bullets:** 1 recommended set + 2-3 alternative phrasings per bullet (each emphasizing different customer angles)
- **Backend keywords:** 1 recommended set + overflow list for A/B testing

For each alternative, note:
- What it prioritizes differently
- Which customer segment it speaks to
- Which keyword strategy it favors

### Listing Output Structure

Use the full listing template from the listing-creator skill, including:
- Recommended title + alternative titles with character counts and keyword placement breakdowns
- 5 recommended bullets with theme labels + alternative phrasings per bullet
- Backend keywords + overflow options
- Full research data (competitors, keywords, Q&A mapping — not summarized)
- Keyword placement map showing where every keyword lands
- Copy-paste ready section (recommended version)

**Save to:**
1. `outputs/research/product-launch/{product-slug}/listing/{product-slug}-listing-YYYY-MM-DD.md`
2. `outputs/research/listings/briefs/{product-slug}-listing-YYYY-MM-DD.md` (copy)

---

## Step 4: Generate Image Plan (With Multiple Options Per Image)

**Use the shared research to generate the image plan.**

Follow **ALL rules** from the image-planner skill (`.claude/skills/image-planner/SKILL.md`):

- **3-layer structure:** Copy quick reference table → image-by-image detail → supporting analysis
- **Copy writing rules:** Informative, not kitschy. Rufus-indexable. Keyword-rich.
- **Customer review language drives copy** — use the words customers actually use
- **One topic per image** — each image answers ONE customer question
- **Mobile-readable text** — legible at thumbnail size
- **Match listing voice** — image text mirrors the bullet point tone and vocabulary

### CRITICAL: Generate Multiple Options Per Image

**For EACH image position (2-7), generate:**

- **1 recommended copy set** (headline + supporting text + callouts)
- **3-4 alternative copy options**, each targeting a different angle:
  - **Option A:** Focus on keyword/SEO angle (maximizes Rufus indexing)
  - **Option B:** Focus on emotional/gift-buyer angle (speaks to the purchaser's feelings)
  - **Option C:** Focus on practical/informational angle (answers the most common Q&A question for this topic)
  - **Option D (if applicable):** Focus on differentiation angle (highlights what competitors DON'T show)

For each option, include:
- Exact headline text
- Exact supporting text / callouts
- 1-2 sentence rationale (why this angle, what customer insight drives it)

**Also provide:**
- **2-3 visual approach options** per image (e.g., flat lay vs lifestyle vs infographic)
- **Prop and styling alternatives**
- **1-2 alternative image sequence orderings** for the full set

### Image Plan Output Structure

Use the full image plan template from the image-planner skill, including:
- Copy at a glance table — recommended version (the 30-second designer reference)
- Copy guidelines and review-driven language
- Image-by-image detail with ALL options (recommended + 3-4 alternatives per image)
- Full visual direction per image (background, props, lighting, color palette)
- Photography/design brief per image
- Competitor image analysis (what each competitor does at each position)
- Gaps exploited
- Alternative image sequence options

**Save to:**
1. `outputs/research/product-launch/{product-slug}/image-plan/{product-slug}-image-plan-YYYY-MM-DD.md`
2. `outputs/research/image-plans/briefs/{product-slug}-image-plan-YYYY-MM-DD.md` (copy)

---

## Step 5: Upload to Notion

### Notion Page ID (ALWAYS use this)

**Parent page:** "Product Listing Development"
**Page ID:** `30557318-d05c-806a-a94f-f5a439d94d10`
**URL:** https://www.notion.so/Product-Listing-Development-30557318d05c806aa94ff5a439d94d10

**ALWAYS create child pages under this parent page.** Do not ask the user which database to use — this is the permanent location.

### Notion Upload Philosophy

**Do NOT summarize. Upload the FULL detail.**

The Notion page is the single source of truth for this product's listing development. It should contain everything — all options, all research, all competitor data, all copy alternatives. The user should never need to open the local markdown files because Notion has it all.

- **Summary at the top** — a quick executive overview for scanning
- **Full detail below** — every option, every data point, every competitor insight
- **Multiple options per image** — so the user can pick and choose
- **Multiple title/bullet alternatives** — so the user has real choices
- **Complete research data** — not just conclusions, but the evidence behind them

### Notion Page Structure

**One page per product** in the target database.

#### Page Properties

| Property | Type | Value |
|----------|------|-------|
| **Title** | Title | `{Product Name}` |
| **SKU** | Rich Text | `{SKU}` |
| **Status** | Select | `Draft` |
| **Date** | Date | `{YYYY-MM-DD}` |
| **Competitors Analyzed** | Number | `{count}` |
| **Primary Keywords** | Rich Text | `{keyword1}, {keyword2}, ...` |
| **Has Listing** | Checkbox | `true/false` |
| **Has Image Plan** | Checkbox | `true/false` |

#### Page Content (Blocks)

Build the page content in this order:

---

**Section 1: Executive Summary (Quick Scan)**
- Heading 1: `{Product Name} — Listing Development`
- Callout block: Quick stats — SKU, date, competitors analyzed, primary keywords, what was generated
- Heading 3: `Strategic Summary`
- Bulleted list summarizing:
  - **Market position:** Where we sit vs competitors (price, rating, differentiation)
  - **Top 3 competitive advantages** we're leveraging
  - **Top 3 customer concerns** we're addressing
  - **Primary keyword strategy:** Which keywords we're targeting and why
  - **Image strategy in one line:** The narrative arc of our 7 images
  - **Key decision:** The single most important strategic choice made and why

---

**Section 2: Amazon Listing (Full Detail)**
- Divider
- Heading 2: `Amazon Listing`

- Heading 3: `Recommended Title`
- Quote block: The primary recommended title (easy to copy)
- Paragraph: Character count, keyword placement breakdown (which keyword sits where and why)

- Heading 3: `Alternative Title Options`
- Numbered list: 2-3 alternative title formulations, each with:
  - The full title text
  - Character count
  - Brief note on what this version prioritizes differently (e.g., "Leads with brand" vs "Leads with category keyword")

- Heading 3: `Bullet Points — Recommended`
- Numbered list: All 5 bullets, each with:
  - **Theme label in bold** (e.g., "Bullet 1: Complete Kit")
  - The full bullet text
  - Italic note: Which customer question(s) this bullet answers and the review/Q&A evidence

- Heading 3: `Bullet Points — Alternatives`
- Toggle for each bullet: `Bullet {#} Alternatives` containing:
  - 2-3 alternative phrasings for that bullet
  - Note on what each alternative emphasizes differently
  - Which customer segment each speaks to most

- Heading 3: `Backend Keywords`
- Code block: Recommended backend keywords (easy to copy)
- Paragraph: Byte count, what's excluded and why (already in title, brand names, etc.)
- Toggle: `Additional Backend Keyword Options` → overflow keywords to swap in if testing

- Heading 3: `Keyword Placement Map`
- Table block showing: Keyword | Location (Title/Bullet#/Backend) | Search Volume | Why This Placement

---

**Section 3: Image Plan (Full Detail with Options)**
- Divider
- Heading 2: `Image Plan`

- Heading 3: `Image Narrative Arc`
- Paragraph: 2-3 sentences explaining the story the 7 images tell in sequence — what the buyer's emotional journey is from Image 1 to Image 7

- Heading 3: `Copy At a Glance — Recommended`
- Table block: Image # | Purpose | Recommended Headline | Recommended Supporting Text | Question Answered

- Heading 3: `Image-by-Image Detail`
- For EACH image position, a Toggle block titled `Image {#}: {Purpose}` containing:

  **Recommended Copy:**
  - Table: Element | Exact Copy | Placement
  - (Headline, supporting text, callouts, badges — all with exact wording and position)

  **Alternative Copy Options (3-4 per image):**
  - **Option A:** Headline: "{text}" / Supporting: "{text}" — *Why: {rationale, e.g., "Emphasizes safety for anxious gift buyers"}*
  - **Option B:** Headline: "{text}" / Supporting: "{text}" — *Why: {rationale}*
  - **Option C:** Headline: "{text}" / Supporting: "{text}" — *Why: {rationale}*
  - (Each option targets a different angle, customer segment, or keyword emphasis)

  **Customer Insight Driving This Image:**
  - The specific review quotes, Q&A questions, or competitor gaps that justify this image
  - How many customers asked this question (vote counts if available)
  - What happens if we DON'T address this (lost sale scenario)

  **Visual Direction:**
  - Background: description
  - Product position: description
  - Props/Context: description
  - Color palette / mood notes
  - Lighting direction

  **Photography/Design Brief:**
  - Specific shot instructions
  - Styling and prop list
  - Text overlay placement mockup description (where text sits relative to product)
  - Mobile thumbnail check: what must be visible at small size

  **Competitor Comparison for This Image Position:**
  - What competitors show in this same slot
  - How our approach differs and why

- Heading 3: `Alternative Image Sequence`
- Toggle: `Alternative Image Order Options` containing:
  - 1-2 alternative orderings of the 7 images with rationale for each
  - Which ordering to A/B test first

---

**Section 4: Competitor Deep Dive (Full Data)**
- Divider
- Heading 2: `Competitor Analysis`

- Heading 3: `Competitor Overview`
- Table block: # | Brand | ASIN | Title | Price | BSR | Reviews | Rating | Key Strength | Key Weakness

- Heading 3: `Competitor-by-Competitor Breakdown`
- Toggle for EACH competitor: `{Brand} — {ASIN}` containing:
  - **Title:** Full title text
  - **Price:** Current price
  - **BSR & Rating:** Rank, stars, review count
  - **Bullet Points:** All 5 of their bullets (full text)
  - **Image Strategy:** What images they use in what order, text overlays
  - **Strengths:** What they do well (be specific — cite exact copy or image choices)
  - **Weaknesses:** Where they fall short (missed Q&A topics, poor images, weak bullets)
  - **What We're Doing Differently:** How our listing/images beat theirs on each weakness

- Heading 3: `Competitive Gaps We're Exploiting`
- Bulleted list: Each gap with evidence (e.g., "No competitor shows the finished result being used — 3 of 5 competitors only show kit contents")

---

**Section 5: Customer Research (Full Data)**
- Divider
- Heading 2: `Customer Research`

- Heading 3: `Q&A Analysis`
- Table block: Theme | Question | Source ASIN | Votes/Frequency | Addressed In (Bullet# / Image#)
- (Include ALL scraped questions, not just top ones)

- Heading 3: `Review Mining`
- Toggle: `Customer Praise Language` → bulleted list of exact quotes and phrases customers use when happy
- Toggle: `Customer Concern Language` → bulleted list of exact quotes and phrases from worried/negative reviews
- Toggle: `Gift Buyer Language` → how gift purchasers describe the product, what they value
- Toggle: `Emotional Triggers` → what makes someone click Buy (with evidence quotes)
- Toggle: `Customer Vocabulary Bank` → list of words/phrases customers naturally use (for copy reference)

- Heading 3: `Review-to-Copy Mapping`
- Table block: Customer Quote/Theme | Where We Used It | Copy We Wrote | Why This Wording

---

**Section 6: Keyword Strategy (Full Data)**
- Divider
- Heading 2: `Keyword Strategy`

- Heading 3: `Primary Keywords`
- Table block: Keyword | Search Volume | Where Placed (Title/Bullet/Backend) | Competitor Usage (how many of top 5 use it)

- Heading 3: `Secondary Keywords`
- Table block: Same structure

- Heading 3: `Long-Tail Keywords`
- Table block: Same structure

- Heading 3: `Keywords NOT Used (and Why)`
- Bulleted list: Keywords considered but excluded, with reason (e.g., "too broad", "low relevance", "already covered by primary")

### Notion Upload Process

1. **Search for existing page** with the product name using Notion MCP `notion-search`
2. **If page exists:**
   - Read existing page to check what sections are already there
   - Update page properties (date, checkboxes for what now exists)
   - If adding a missing section (e.g., image plan to a page that only had listing):
     - Append the new section blocks after the existing content
   - If replacing: Delete old content blocks first, then append fresh content
   - Tell user: "Updated existing Notion page for {product name}"
3. **If page doesn't exist:**
   - Create new page in the target database with all properties
   - Append all content blocks in order
   - Tell user: "Created new Notion page for {product name}" and share the URL

### Notion Upload Rules

- **Search before creating** — never duplicate pages
- **Use toggle blocks** for detailed sections — keeps the page scannable while preserving ALL data
- **Use quote blocks** for copy-paste content (title, keywords) — visually distinct and easy to grab
- **Use code blocks** for backend keywords — prevents formatting issues
- **Use table blocks** wherever data has multiple columns — easier to scan than paragraphs
- **Update checkboxes** (`Has Listing`, `Has Image Plan`) — so you can filter the database by completeness
- **Always update date** to the most recent generation date
- **NEVER truncate or summarize research** — if you scraped it, it goes on the page
- **Include all options** — multiple titles, bullet alternatives, image copy alternatives. Let the user choose

---

## Output Summary

After a full run, the user gets:

| Output | Location |
|--------|----------|
| **Listing brief** | `outputs/research/product-launch/{slug}/listing/` + `outputs/research/listings/briefs/` |
| **Image plan brief** | `outputs/research/product-launch/{slug}/image-plan/` + `outputs/research/image-plans/briefs/` |
| **Shared research** | `outputs/research/product-launch/{slug}/research/` |
| **Notion page** | Single page with listing + image plan + research |

---

## Error Handling

| Issue | Action |
|-------|--------|
| Product not in catalog | Ask user to clarify or add to `context/products.md` |
| No competitors found | Broaden search terms, try category browse |
| Apify rate limit | Wait 60s, retry once. If still fails, ask user |
| Notion database not found | Ask user for database ID/URL, save to `context/business.md` |
| Existing brief found | Show user what exists with date, ask what to regenerate |
| One output already exists | Skip it, run only the missing one (tell user) |
| Existing brief >30 days old | Mention age, suggest refreshing |
| Token budget exceeded | Stop, save progress, tell user what's remaining |

---

## Example Workflows

### Example 1: Full Run (Nothing Exists)

**User:** "Product listing development for the Barbie Embroidery Kit"

**Claude:**
1. Generates slug: `barbie-embroidery`
2. Checks existing work → nothing found
3. Gathers inputs: SKU BB01, target "embroidery kit for kids", ages 8+, differentiators (Barbie license, 8 designs)
4. Runs shared research (competitors, reviews, Q&A, keywords)
5. Generates listing (title, 5 bullets, backend keywords)
6. Generates image plan (7 images with copy)
7. Saves all files to both locations
8. Uploads to Notion as one page
9. **Result:** Complete product page with listing + images + research

### Example 2: Partial Run (Image Plan Exists)

**User:** "Full listing for the Latch Hook Rainbow Heart"

**Claude:**
1. Generates slug: `latch-hook-rainbow-heart`
2. Checks existing work:
   - Found: `latch-hook-rainbow-heart-image-plan-2026-02-12.md`
   - Not found: listing brief
3. Tells user: "Found existing image plan from 2026-02-12. I'll generate the listing only and reuse the competitor research."
4. Reads existing image plan to extract competitor ASINs and research insights
5. Runs listing-specific research (deeper keyword analysis, bullet-focused Q&A mapping)
6. Generates listing
7. Uploads BOTH listing + existing image plan to one Notion page
8. **Result:** ~50% less cost, same complete output

### Example 3: Both Exist

**User:** "Develop listing for Barbie Embroidery"

**Claude:**
1. Checks existing work:
   - Found: listing from 2026-02-11
   - Found: image plan from 2026-02-11
2. Tells user: "Both listing and image plan already exist from 2026-02-11. Options:"
   - A) Refresh both (full re-run with new research)
   - B) Refresh listing only
   - C) Refresh image plan only
   - D) Just upload both to Notion as-is
3. User picks → Claude executes only what's needed

---

## Execution Checklist

- [ ] Gather all inputs (product, keywords, age, ASINs, differentiators)
- [ ] Check for existing briefs (listing + image plan)
- [ ] Determine run mode (full / listing-only / images-only / ask user)
- [ ] Load product specs from `context/products.md`
- [ ] Run shared research — or load existing (competitors, reviews, Q&A, keywords)
- [ ] Generate listing (if needed) — follow listing-creator rules
- [ ] Generate image plan (if needed) — follow image-planner rules
- [ ] Save outputs to product-launch folder + individual skill folders
- [ ] Upload to Notion (single page with both sections)
- [ ] Present summary to user with file locations and Notion link
