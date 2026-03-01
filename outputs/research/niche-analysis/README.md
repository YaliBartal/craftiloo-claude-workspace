# Niche Category Analysis

Comprehensive niche/category research for evaluating new Amazon product opportunities.

## Data Sources

| Priority | Source | What It Provides |
|----------|--------|-----------------|
| **1st** | DataDive (Jungle Scout) | Competitor sales/revenue actuals, keywords with search volumes, ranking juice scores, keyword roots |
| **2nd** | Amazon SP-API | Real-time pricing, first-party BSR/category data, catalog search |
| **3rd** | Seller Board | Our own profit data (if already in niche) |
| **Fallback** | Apify | Review scraping, product data if MCP sources fail |

## Folder Structure

```
niche-analysis/
├── briefs/                          # Main analysis reports (read these first)
│   └── {niche-slug}-niche-analysis-YYYY-MM-DD.md
├── data/
│   └── YYYY-MM-DD/                  # Date-stamped subfolders
│       ├── datadive-competitors-{niche-slug}-YYYY-MM-DD.json
│       ├── datadive-keywords-{niche-slug}-YYYY-MM-DD.json
│       ├── datadive-roots-{niche-slug}-YYYY-MM-DD.json
│       ├── datadive-ranking-juice-{niche-slug}-YYYY-MM-DD.json
│       ├── sp-api-pricing-{niche-slug}-YYYY-MM-DD.json
│       ├── sp-api-catalog-{niche-slug}-YYYY-MM-DD.json
│       └── reviews-{ASIN}-YYYY-MM-DD.json
├── snapshots/                       # Historical metrics for trend comparison
│   └── {niche-slug}-snapshot-YYYY-MM-DD.json
└── README.md                        # This file
```

## File Naming Conventions

| File Type | Format | Example |
|-----------|--------|---------|
| Analysis brief | `{niche-slug}-niche-analysis-YYYY-MM-DD.md` | `quilt-kit-kids-niche-analysis-2026-02-23.md` |
| DataDive competitors | `datadive-competitors-{niche-slug}-YYYY-MM-DD.json` | `datadive-competitors-quilt-kit-kids-2026-02-23.json` |
| DataDive keywords | `datadive-keywords-{niche-slug}-YYYY-MM-DD.json` | `datadive-keywords-quilt-kit-kids-2026-02-23.json` |
| DataDive roots | `datadive-roots-{niche-slug}-YYYY-MM-DD.json` | `datadive-roots-quilt-kit-kids-2026-02-23.json` |
| DataDive ranking juice | `datadive-ranking-juice-{niche-slug}-YYYY-MM-DD.json` | `datadive-ranking-juice-quilt-kit-kids-2026-02-23.json` |
| SP-API pricing | `sp-api-pricing-{niche-slug}-YYYY-MM-DD.json` | `sp-api-pricing-quilt-kit-kids-2026-02-23.json` |
| SP-API catalog | `sp-api-catalog-{niche-slug}-YYYY-MM-DD.json` | `sp-api-catalog-quilt-kit-kids-2026-02-23.json` |
| Review data | `reviews-{ASIN}-YYYY-MM-DD.json` | `reviews-B072JH19F8-2026-02-23.json` |
| Snapshot | `{niche-slug}-snapshot-YYYY-MM-DD.json` | `quilt-kit-kids-snapshot-2026-02-23.json` |

## What Each Folder Contains

| Folder | Purpose | When to Look Here |
|--------|---------|-------------------|
| `briefs/` | Full niche analysis with GO/NO-GO verdict | Start here — this is the main output |
| `data/` | Raw JSON from MCP services + Apify | When you need to dig into raw numbers |
| `snapshots/` | Metrics saved for future comparison | When re-analyzing a niche later to see changes |

## Historical Runs

| Date | Niche | Method | Verdict | Brief |
|------|-------|--------|---------|-------|
| 2026-02-22 | quilt-kit-kids | Apify + BSR tables | CONDITIONAL GO (26/35) | `briefs/quilt-kit-kids-niche-analysis-2026-02-22.md` |
| 2026-02-23 | quilt-kit-kids | DataDive + SP-API (reused Feb 22 reviews) | CONDITIONAL GO (30/40) | `briefs/quilt-kit-kids-niche-analysis-2026-02-23.md` |
| 2026-02-26 | loom-knitting-kit-kids | DataDive + SP-API + Seller Board + Apify (partial reviews) | CONDITIONAL GO (32/40) | `briefs/loom-knitting-kit-kids-niche-analysis-2026-02-26.md` |

## Skill Location

`.claude/skills/niche-category-analysis/SKILL.md`
