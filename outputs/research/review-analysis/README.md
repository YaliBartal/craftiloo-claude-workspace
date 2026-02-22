# Review Analysis

Customer review analysis outputs for Craftiloo and competitor products.

## Folder Structure

```
review-analysis/
├── briefs/                # Analysis reports (what you read first)
├── data/                  # Raw review data from Apify
│   └── YYYY-MM-DD/        # Date-stamped raw data
├── snapshots/             # Historical metrics for trend tracking
│   └── {slug}-snapshot-YYYY-MM-DD.json
└── README.md              # This file
```

## File Naming

| File Type | Format | Example |
|-----------|--------|---------|
| Deep dive report | `{product-slug}-review-analysis-YYYY-MM-DD.md` | `cross-stitch-girls-review-analysis-2026-02-20.md` |
| Category scan report | `{category-slug}-category-scan-YYYY-MM-DD.md` | `latch-hook-category-scan-2026-02-20.md` |
| Raw review data | `reviews-{ASIN}-YYYY-MM-DD.json` | `reviews-B08DDJCQKF-2026-02-20.json` |
| Snapshot | `{slug}-snapshot-YYYY-MM-DD.json` | `cross-stitch-girls-snapshot-2026-02-20.json` |

## What Goes Where

| Folder | Contains | When Created |
|--------|----------|-------------|
| **briefs/** | Formatted analysis reports you read and act on | Every skill run |
| **data/** | Raw JSON review data from Apify (archived for reference) | Every skill run |
| **snapshots/** | JSON metrics snapshots for week-over-week trend tracking | Every skill run |

## How to Use

1. Run the skill: say "review analysis", "analyze reviews", or "customer reviews"
2. Choose mode: **Deep Dive** (1 product + 3 competitors) or **Category Scan** (all products in a category)
3. Review the brief in `briefs/`
4. Snapshots accumulate automatically for trend comparison on future runs
