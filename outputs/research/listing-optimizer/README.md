# Listing Optimizer / Audit

**Purpose:** Audit existing Craftiloo Amazon listings against competitors and produce rewrite recommendations.

## Folder Structure

```
listing-optimizer/
├── briefs/         # Audit reports and portfolio scans
├── rewrites/       # AI Copywriter output + rewrite suggestions
│   └── YYYY-MM-DD/ # Date-stamped rewrite batches
├── snapshots/      # Historical optimization scores for trend tracking
└── README.md       # This file
```

## File Naming Conventions

| File Type | Format | Example |
|-----------|--------|---------|
| Single audit report | `{product-slug}-listing-audit-YYYY-MM-DD.md` | `fairy-sewing-listing-audit-2026-02-23.md` |
| Portfolio scan report | `portfolio-scan-YYYY-MM-DD.md` | `portfolio-scan-2026-02-23.md` |
| AI Copywriter output | `{product-slug}-rewrites-YYYY-MM-DD.md` | `fairy-sewing-rewrites-2026-02-23.md` |
| Snapshot (single) | `{slug}-snapshot-YYYY-MM-DD.json` | `fairy-sewing-snapshot-2026-02-23.json` |
| Snapshot (portfolio) | `portfolio-snapshot-YYYY-MM-DD.json` | `portfolio-snapshot-2026-02-23.json` |

## What Goes Where

| Folder | Contents | When Created |
|--------|----------|--------------|
| `briefs/` | Main readable audit reports | Every run |
| `rewrites/` | AI-generated listing alternatives (4 modes) | Single Audit only |
| `snapshots/` | JSON data for trend tracking across runs | Every run |

## Two Modes

1. **Single Product Audit** — Deep audit of one ASIN with full rewrite recommendations
2. **Portfolio Scan** — Quick health check across all 13 hero products

## Data Sources

- DataDive (Ranking Juice, Master Keyword List, Roots, Rank Radar, AI Copywriter)
- Seller Board (CVR, sessions, revenue, profit)
- Apify (listing copy scraping — Single Audit only)

## Trigger

Say: "listing audit", "audit listing", "listing optimizer", "portfolio scan", "listing health"
