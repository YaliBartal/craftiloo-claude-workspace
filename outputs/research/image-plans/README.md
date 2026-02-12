# Image Plans

**Purpose:** Strategic image planning for Amazon product listings based on competitor analysis.

---

## Folder Structure

```
image-plans/
├── briefs/              # Final image plans (READ FIRST)
├── competitor-analysis/ # Breakdown of each competitor's images
├── data/                # Raw scraped image data (JSON)
└── README.md            # This file
```

---

## File Naming

| Type | Format | Example |
|------|--------|---------|
| **Briefs** | `{product-slug}-image-plan-YYYY-MM-DD.md` | `cross-stitch-kit-image-plan-2026-02-11.md` |
| **Competitor** | `{competitor-asin}-images-YYYY-MM-DD.md` | `B09XYZ123-images-2026-02-11.md` |
| **Data** | `image-data-{product-slug}-YYYY-MM-DD.json` | `image-data-cross-stitch-2026-02-11.json` |

---

## What Goes Where

| You have... | Put it in... |
|-------------|--------------|
| Final image plan for a product | `briefs/` |
| Analysis of a single competitor's images | `competitor-analysis/` |
| Raw scraped image URLs/metadata | `data/` |

---

## How to Use

Run `/image-planner` and provide:
1. Your product type
2. 3-5 competitor ASINs
3. Your product's key differentiators

Output: Complete image plan with recommendations for each image position.
