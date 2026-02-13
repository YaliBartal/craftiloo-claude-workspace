---
name: image-planner
description: Analyzes competitor Amazon images and creates strategic image plans for new product listings
triggers:
  - image plan
  - plan my images
  - image strategy
  - listing images
  - product images
output_location: outputs/research/image-plans/
---

# Image Planner

**USE WHEN** user says: "image plan", "plan my images", "image strategy", "listing images", "product images"

---

## What This Does

Scrapes competitor Amazon product images, analyzes their visual strategy, mines customer reviews/Q&A for copy insights, and creates a detailed image plan — **leading with the exact text/copy for each image**, then layering in visual direction and competitive analysis.

---

## ⚡ Organization & Efficiency Standards

**CRITICAL: Follow these standards for EVERY run:**

### File Organization
```
outputs/research/image-plans/
├── briefs/              # Final image plans (what user reads first)
├── competitor-analysis/ # Breakdown of each competitor's images
├── data/                # Raw scraped image data
└── README.md            # Folder guide
```

### Naming Conventions (STRICT)
- **Briefs:** `{product-slug}-image-plan-YYYY-MM-DD.md`
- **Competitor analysis:** `{competitor-asin}-images-YYYY-MM-DD.md`
- **Data files:** `image-data-{product-slug}-YYYY-MM-DD.json`

### Efficiency Targets
- ✅ <80K tokens per run
- ✅ <$0.20 cost (if using paid APIs)
- ✅ <5 minutes execution
- ✅ Minimal file count
- ✅ Clean organization

### Forbidden
- ❌ Root folder dumps
- ❌ Scripts mixed with outputs
- ❌ Temp files without cleanup
- ❌ Ambiguous names

---

## Required Inputs

Before running, get from user:
1. **Product type** — What product are we creating images for?
2. **Competitor ASINs** — **CHECK CONTEXT FILES FIRST** (see below)
3. **Our product's key differentiators** — What makes our product unique?

### CRITICAL: Check Context Files Before Any Research

**ALWAYS check these context files BEFORE scraping or searching for competitors/keywords:**

| Context File | What It Contains | Use For |
|-------------|-----------------|---------|
| `context/competitors.md` | **Competitors by category with ASINs, market share, strengths/weaknesses** | Get competitor ASINs — DO NOT scrape for competitors if they exist here |
| `context/search-terms.md` | **Search terms by category with volume and relevance scores** | Get keyword data for Rufus-indexable image copy |
| `context/hero-products.md` | **Our hero products with ASINs, contents, key selling points** | Get our own product ASIN and detailed info |
| `context/products.md` | **Full product catalog with specs, contents, dimensions** | Get exact kit contents, measurements, pricing |

**Lookup order:** Identify product category → check `context/competitors.md` for ASINs → check `context/search-terms.md` for keywords → load product specs → only use Apify for data NOT in context files (reviews, Q&A, images).

---

## Process

### Step 1: Scrape Competitor Images

**First: Check `context/competitors.md`** for the product's category. Use those ASINs instead of searching.

For each competitor ASIN:
1. Use Apify Amazon scraper to get product page data
2. Extract all product images (main + gallery)
3. Note image order (position 1-7+)
4. Save image URLs and metadata

### Step 2: Mine Customer Reviews & Q&A

**CRITICAL STEP — This drives the copy.**

For our product AND competitors, extract:
- **Top praises** — What words/phrases do happy customers use?
- **Top complaints** — What worries buyers before purchasing?
- **Common questions** — What do people ask in Q&A / Rufus?
- **Emotional triggers** — What makes someone click "Buy"?
- **Gift buyer language** — How do gift purchasers describe the product?

Group findings into:
1. **Must-answer concerns** (address in images or lose the sale)
2. **Emotional hooks** (what makes buyers feel good about purchasing)
3. **Differentiators to highlight** (what we do that competitors don't)

### Step 3: Analyze Each Competitor's Image Strategy

For each competitor, analyze and document:

| Position | Image Type | Focus | Customer Question Answered | Text/Graphics |
|----------|------------|-------|---------------------------|---------------|
| 1 | Main/Hero | Product on white | "What does it look like?" | None (Amazon requirement) |
| 2 | ... | ... | ... | ... |

Identify patterns:
- **Common image types** (lifestyle, infographic, comparison, packaging, etc.)
- **Common order** (what comes first, second, etc.)
- **Key selling points highlighted**
- **Text overlay patterns**
- **Customer concerns addressed**
- **What NO competitor addresses** (gaps = opportunities)

### Step 4: Create Image Plan

**THE OUTPUT MUST BE STRUCTURED IN 3 LAYERS — from broad to detailed:**

#### Layer 1: Text/Copy Quick Reference (TOP OF DOCUMENT)
The very first thing in the brief. A scannable table showing:
- Image number
- Headline text (exact copy)
- Supporting text / callouts (exact copy)
- Customer question it answers

**This must be readable in 30 seconds.** A designer or photographer should be able to grab this table and know exactly what goes on each image.

#### Layer 2: Image-by-Image Detail
For EACH image position, provide:
- Image type and visual description
- ALL text/copy with exact wording
- Placement guidance (where text goes on the image)
- Customer insight driving this copy (why these words)
- Photography/design notes

#### Layer 3: Supporting Analysis
- Competitor breakdown
- Review insights that drove copy decisions
- Gaps exploited
- Implementation priority

### Step 5: Write the Copy

For each image, the text must be:
- **Derived from customer language** — Use the words customers actually use in reviews
- **Answering a specific question** — Every headline responds to a real buyer concern
- **Concise** — Headlines 3-6 words, supporting text 1 short sentence max
- **Benefit-focused** — Not features, benefits (not "pre-cut yarn" but "No Measuring Needed")
- **Mobile-readable** — Must be legible at thumbnail size

---

## Output

### Primary Output: Image Plan Brief
- **Format:** Markdown
- **Location:** `outputs/research/image-plans/briefs/{product-slug}-image-plan-YYYY-MM-DD.md`
- **Contains:** 3-layer structure (copy reference → detail → analysis)

### Supporting Files

**Competitor Analysis:**
- **Location:** `outputs/research/image-plans/competitor-analysis/`
- **Files:** One file per competitor ASIN analyzed

**Raw Data:**
- **Location:** `outputs/research/image-plans/data/`
- **Files:** JSON with scraped image URLs and metadata

---

## Output Template: Image Plan Brief

```markdown
# Image Plan: [Product Name]

**Date:** YYYY-MM-DD
**Product:** [Product name/type]
**Competitors Analyzed:** [# of competitors]

---

## 📋 Image Text/Copy At a Glance

> **Designer/photographer: Start here.** This table has everything you need to know about what text goes on each image.

| # | Image Purpose | Headline Text | Supporting Text / Callouts | Question It Answers |
|---|--------------|---------------|---------------------------|-------------------|
| 1 | Hero | *(none — Amazon rule)* | *(none)* | What does it look like? |
| 2 | [purpose] | **"[Exact headline]"** | [Callout 1] · [Callout 2] · [Callout 3] | [Question] |
| 3 | [purpose] | **"[Exact headline]"** | [Callout 1] · [Callout 2] | [Question] |
| ... | ... | ... | ... | ... |

### Copy Notes
- **Voice:** [Tone description — e.g., warm, parent-friendly, confident]
- **Key phrases from reviews:** "[phrase 1]", "[phrase 2]", "[phrase 3]"
- **Words customers use:** [list of actual customer vocabulary]
- **Concerns to address:** [list of must-answer worries]

---

## 🖼️ Image-by-Image Detail

### Image [#]: [Title]

**Image Type:** [Main/Lifestyle/Infographic/Comparison/etc.]
**Customer Question:** "[Question this image answers]"

**📝 Text on This Image:**
| Element | Exact Copy | Placement |
|---------|-----------|-----------|
| Headline | "[Text]" | [Top/Center/Bottom] |
| Supporting text | "[Text]" | [Below headline / corner] |
| Callout 1 | "[Text]" | [Near component / with arrow] |
| Callout 2 | "[Text]" | [Location] |
| Badge/icon | "[Text]" | [Corner / overlay] |

**Why this copy:** [1-2 sentences explaining which customer insight/review drives this text]

**Visual Elements:**
- Background: [description]
- Product position: [description]
- Props/Context: [description]

**Photography/Design Notes:**
[Specific instructions]

---

[Repeat for each image]

---

## 📊 Analysis & Insights

### Customer Review Insights (Copy Drivers)

**What Customers Praise (use this language):**
- [Quote/theme 1]
- [Quote/theme 2]

**What Customers Worry About (address in images):**
- [Concern 1]
- [Concern 2]

**Emotional Triggers (leverage in copy):**
- [Trigger 1]
- [Trigger 2]

### Competitor Image Analysis

| Competitor | ASIN | Images Used | Strengths | Weaknesses | Text Strategy |
|------------|------|------------|-----------|------------|---------------|
| ... | ... | ... | ... | ... | ... |

### Gaps We're Exploiting
- [Gap 1]
- [Gap 2]

---

## ✅ Next Steps

1. [ ] Review text/copy — approve or adjust wording
2. [ ] Brief designer with copy table + image details
3. [ ] Schedule photo shoot
4. [ ] Create text overlay mockups
5. [ ] A/B test and monitor
```

---

## Copy Writing Rules

**ALWAYS follow these when writing image text:**

### Tone: Informative, Not Kitschy

**Image text must read like the listing itself — factual, informative, keyword-rich.**

Amazon's Rufus AI reads and indexes image text. Cute slogans like "Easy as 1-2-3!" or "The Perfect Gift" add zero indexable value and waste image real estate. Instead, write text that:

- **Directly answers customer questions** — the way a listing bullet would
- **Contains searchable keywords** — terms customers type into Amazon search
- **States facts and benefits plainly** — no fluff, no exclamation marks, no marketing speak
- **Matches the listing voice** — if the bullets say "All-In-One Kit," the image says the same

### Rules

1. **Informative over catchy** — "Complete Kit — No Extra Supplies Needed" beats "Everything Included — Just Open & Craft!"
2. **Answer the question directly** — Each text block is a factual answer to a real customer concern, not a slogan
3. **Use listing language** — Match the tone and vocabulary of the product bullet points. If the listing says "Beginner-Friendly, No Sewing Skills Needed" the image should say the same, not a creative rewrite
4. **Keyword-aware** — Include terms Rufus can index: product type, age range, key features, materials. "Latch Hook Kit for Kids Ages 6+" is better than "Perfect for Young Crafters"
5. **Readable at thumbnail** — Must be legible on mobile. Keep text blocks concise but informative, not single-word slogans
6. **One topic per image** — Each image addresses ONE customer question with enough informative detail to fully answer it
7. **Gift buyer focus** — The buyer is often NOT the user. Text should inform the gift-buyer's decision: age suitability, what's included, skill level, what the result is
8. **No empty calories** — If a word doesn't inform, answer a question, or contain a keyword, cut it. "Fun" and "Amazing" waste space. "Screen-Free Activity That Builds Focus" does not

---

## Example Run

**User:** "Create an image plan for our new cross-stitch kit"

**Claude:**
1. Asks for competitor ASINs (or offers to find top competitors)
2. Scrapes 3-5 competitor product pages
3. **Mines customer reviews and Q&A for copy insights**
4. Analyzes all competitor images
5. **Writes exact text/copy for each image position**
6. Creates 3-layer brief (copy table → detail → analysis)
7. Outputs brief to `outputs/research/image-plans/briefs/cross-stitch-kit-image-plan-2026-02-12.md`
8. Uploads to Notion (or appends to existing product page)

---

## Upload to Notion

**After generating the image plan, upload it to Notion.**

### Notion Page ID (ALWAYS use this)

**Parent page:** "Product Listing Development"
**Page ID:** `30557318-d05c-806a-a94f-f5a439d94d10`
**URL:** https://www.notion.so/Product-Listing-Development-30557318d05c806aa94ff5a439d94d10

**ALWAYS create child pages under this parent page.** Do not ask the user which database to use.

### Search Before Creating

1. **Search for existing product page** using Notion MCP `notion-search` with the product name
2. **If page exists** → append the image plan section to it (don't create a duplicate)
3. **If page doesn't exist** → create a new page

### Page Properties

When creating a new page or updating an existing one:

| Property | Type | Value |
|----------|------|-------|
| **Title** | Title | `{Product Name}` |
| **SKU** | Rich Text | `{SKU}` |
| **Status** | Select | `Draft` |
| **Date** | Date | `{YYYY-MM-DD}` |
| **Competitors Analyzed** | Number | `{count}` |
| **Has Image Plan** | Checkbox | `true` |

### Page Content (Image Plan Section)

Append these blocks to the page:

1. **Divider**
2. **Heading 2:** `Image Plan`
3. **Heading 3:** `Copy At a Glance`
4. **Table block:** Image # | Purpose | Headline Text | Supporting Text | Question Answered
5. **Heading 3:** `Image-by-Image Detail`
6. **For each image position:** Toggle block titled `Image {#}: {Purpose}` containing:
   - All text/copy with placement guidance
   - Visual description
   - Photography/design notes
   - Customer insight driving the copy
7. **Heading 3:** `Competitor Image Analysis`
8. **Toggle:** `Competitor Breakdown` → competitor image strategy table
9. **Toggle:** `Review Insights Driving Copy` → customer language, concerns, emotional triggers

### Upload Rules

- **Search before creating** — never duplicate pages
- **Use toggle blocks** for image detail — keeps the page scannable
- **Use table blocks** for the copy-at-a-glance reference — easy for designers to scan
- **Update `Has Image Plan` checkbox** to `true`
- **If a listing already exists on the page**, append the image plan section AFTER the listing section
- **Tell the user** what you did: "Uploaded image plan to Notion page: {product name}" or "Added image plan to existing Notion page for {product name}"

### Compatibility with Parent Skill

This Notion structure is **compatible with the Product Listing Development skill** (`product-listing-development`). Both skills use the same:
- Page properties (Title, SKU, Status, Date, checkboxes)
- Section structure (Listing section + Image Plan section)
- Database location (saved in `context/business.md`)

If the parent skill runs, it handles Notion upload for both. If this skill runs standalone, it creates/updates the page with just the image plan section.
