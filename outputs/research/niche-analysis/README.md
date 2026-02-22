# Niche Category Analysis

Comprehensive niche/category research for evaluating new Amazon product opportunities.

## Folder Structure

```
niche-analysis/
├── briefs/              # Main analysis reports (read these first)
├── data/                # Raw scraped data
│   └── YYYY-MM-DD/      # Date-stamped subfolders
│       ├── search-results-{keyword}-YYYY-MM-DD.json
│       ├── products-{niche-slug}-YYYY-MM-DD.json
│       └── reviews-{ASIN}-YYYY-MM-DD.json
├── snapshots/           # Historical metrics for trend comparison
│   └── {niche-slug}-snapshot-YYYY-MM-DD.json
└── README.md            # This file
```

## File Naming

| File Type | Format | Example |
|-----------|--------|---------|
| Analysis brief | `{niche-slug}-niche-analysis-YYYY-MM-DD.md` | `diamond-painting-niche-analysis-2026-02-22.md` |
| Search data | `search-results-{keyword}-YYYY-MM-DD.json` | `search-results-diamond-painting-kits-2026-02-22.json` |
| Product data | `products-{niche-slug}-YYYY-MM-DD.json` | `products-diamond-painting-2026-02-22.json` |
| Review data | `reviews-{ASIN}-YYYY-MM-DD.json` | `reviews-B08QV9CMFQ-2026-02-22.json` |
| Snapshot | `{niche-slug}-snapshot-YYYY-MM-DD.json` | `diamond-painting-snapshot-2026-02-22.json` |

## What Each Folder Contains

| Folder | Purpose | When to Look Here |
|--------|---------|-------------------|
| `briefs/` | Full niche analysis with GO/NO-GO verdict | Start here — this is the main output |
| `data/` | Raw JSON from Amazon scraping | When you need to dig into raw numbers |
| `snapshots/` | Metrics saved for future comparison | When re-analyzing a niche later |

## Skill Location

`.claude/skills/niche-category-analysis/SKILL.md`
