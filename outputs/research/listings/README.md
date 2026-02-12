# Listings Output Folder

> Generated Amazon product listings based on competitor analysis

---

## Folder Structure

```
listings/
├── briefs/                    # Final listings (COPY-PASTE READY)
│   └── {product-slug}-listing-YYYY-MM-DD.md
├── research/
│   ├── competitors/           # Competitor analysis reports
│   ├── keywords/              # Keyword research data
│   └── rufus/                 # Rufus Q&A analysis
├── data/                      # Raw scraped data (JSON)
└── README.md                  # This file
```

---

## Naming Conventions

| File Type | Format | Example |
|-----------|--------|---------|
| Final listing | `{product-slug}-listing-YYYY-MM-DD.md` | `cross-stitch-girls-listing-2026-02-11.md` |
| Research report | `{product-slug}-research-YYYY-MM-DD.md` | `cross-stitch-girls-research-2026-02-11.md` |
| Keyword data | `{product-slug}-keywords-YYYY-MM-DD.json` | `cross-stitch-girls-keywords-2026-02-11.json` |

---

## What Goes Where

| Content | Folder |
|---------|--------|
| Copy-paste ready listings | `briefs/` |
| Competitor title/bullet analysis | `research/competitors/` |
| Keyword lists and strategy | `research/keywords/` |
| Rufus question mapping | `research/rufus/` |
| Raw Apify scrape results | `data/` |

---

## Usage

Trigger with: `/listing-creator` or "create a listing for {product}"

The skill will:
1. Research competitors in your target niche
2. Analyze their titles, bullets, and keywords
3. Identify Rufus questions to answer
4. Generate optimized title, bullets, and backend keywords
5. Output copy-paste ready listing here
