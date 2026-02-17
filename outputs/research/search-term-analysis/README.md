# Search Term Analysis

Automated search term report analysis for PPC campaign optimization.

## Folder Structure

```
search-term-analysis/
├── input/     # DROP SEARCH TERM CSVs HERE — skill auto-detects
├── briefs/    # Analysis reports (negation lists, promotion candidates, discoveries)
├── data/      # Archived search term exports (moved from input/ after analysis)
└── README.md  # This guide
```

## How to Use

1. Export search term report from Seller Central (last 7 days, excl. last 2 days)
2. Save CSV to `input/` folder
3. Say "search term analysis" — Claude picks up the file automatically

## File Naming

| Type | Format | Example |
|------|--------|---------|
| Reports | `{portfolio-slug}-search-terms-YYYY-MM-DD.md` | `cross-girl-search-terms-2026-02-17.md` |
| Account-wide | `account-search-terms-YYYY-MM-DD.md` | `account-search-terms-2026-02-17.md` |
| Archived data | `{portfolio-slug}-st-export-YYYY-MM-DD.csv` | `cross-girl-st-export-2026-02-17.csv` |

## What You Get

- **P1 Negate list** — terms bleeding money, add as negatives today
- **P2 Negate list** — poor performers to review before negating
- **Promote list** — winners to graduate to exact/phrase campaigns
- **Discovery list** — new keyword opportunities from auto/broad
- **Estimated savings** — dollar amount recovered from negations
