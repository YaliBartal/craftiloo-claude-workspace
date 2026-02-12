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

Scrapes competitor Amazon product images, analyzes their visual strategy, and creates a detailed image plan for your product listing — including order, content, text overlays, and customer questions each image should answer.

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
2. **Competitor ASINs** — 3-5 top competitor product ASINs to analyze
3. **Our product's key differentiators** — What makes our product unique?

---

## Process

### Step 1: Scrape Competitor Images

For each competitor ASIN:
1. Use Apify Amazon scraper to get product page data
2. Extract all product images (main + gallery)
3. Note image order (position 1-7+)
4. Save image URLs and metadata

### Step 2: Analyze Each Competitor's Image Strategy

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

### Step 3: Identify Customer Questions

From competitor analysis, extract:
- What questions are ALL competitors answering?
- What questions are SOME answering (opportunity)?
- What questions are NONE answering (gap/opportunity)?

Cross-reference with:
- Product reviews (common complaints/praise)
- Q&A section patterns
- Rufus-style customer queries

### Step 4: Create Image Plan

Generate comprehensive plan with this structure for EACH image position:

```markdown
## Image [#]: [Title]

**Image Type:** [Main/Lifestyle/Infographic/Comparison/etc.]

**Primary Focus:** [What's the main thing shown?]

**Customer Question Answered:** "[The question this image answers]"

**How Competitors Answer This:**
- Competitor A: [Their approach]
- Competitor B: [Their approach]

**Our Approach:**
[How we'll do it — same, better, or different]

**Visual Elements:**
- Background: [White/Lifestyle scene/Solid color]
- Product position: [Center/Left/Right/In-use]
- Props/Context: [What else is in the frame]

**Text Overlay:**
- Headline: "[Exact text]"
- Supporting text: "[If any]"
- Callouts: [Icon + text callouts]

**Key Differentiator Shown:** [Which of our USPs does this highlight?]

**Photography/Design Notes:**
[Specific instructions for photographer or designer]
```

### Step 5: Create Summary Brief

Create executive summary:
- Total images recommended (typically 7)
- Image sequence logic (why this order)
- Key differentiators highlighted across images
- Gaps in competitor coverage we're exploiting
- Quick reference table

---

## Output

### Primary Output: Image Plan Brief
- **Format:** Markdown
- **Location:** `outputs/research/image-plans/briefs/{product-slug}-image-plan-YYYY-MM-DD.md`
- **Contains:** Full image plan with all positions detailed

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

## Executive Summary

**Recommended Image Count:** [#]

**Image Sequence:**
1. [Image 1 title] — [purpose]
2. [Image 2 title] — [purpose]
...

**Key Strategy:**
[2-3 sentences on our overall image strategy]

**Competitor Gaps We're Exploiting:**
- [Gap 1]
- [Gap 2]

---

## Quick Reference

| # | Type | Focus | Question Answered | Text |
|---|------|-------|-------------------|------|
| 1 | Main | Product | What is it? | None |
| 2 | ... | ... | ... | ... |

---

## Detailed Image Plans

[Full breakdown for each image position]

---

## Competitor Analysis Summary

| Competitor | ASIN | Strengths | Weaknesses |
|------------|------|-----------|------------|
| ... | ... | ... | ... |

---

## Next Steps

1. [ ] Share with photographer/designer
2. [ ] Source props for lifestyle shots
3. [ ] Create text overlay designs
4. [ ] Schedule photo shoot
```

---

## Example Run

**User:** "Create an image plan for our new cross-stitch kit"

**Claude:**
1. Asks for competitor ASINs (or offers to find top competitors)
2. Scrapes 3-5 competitor product pages
3. Analyzes all their images
4. Identifies patterns and gaps
5. Creates detailed 7-image plan
6. Outputs brief to `outputs/research/image-plans/briefs/cross-stitch-kit-image-plan-2026-02-11.md`
