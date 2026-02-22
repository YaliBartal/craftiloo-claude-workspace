# PPC Portfolio Review (Archived)

**Status:** Archived — this skill was merged into `weekly-ppc-analysis` on 2026-02-19.

Historical portfolio analysis reports from the standalone PPC review skill. New PPC analysis goes to `ppc-weekly/`.

## Folder Structure

```
ppc-review/
├── input/      # DROP CSV EXPORTS HERE — skill auto-detects them
├── briefs/     # Portfolio analysis reports (read these first)
├── data/       # Archived CSV exports (moved from input after analysis)
└── README.md   # This file
```

## File Naming

| Type | Format | Example |
|------|--------|---------|
| Analysis reports | `{portfolio-slug}-review-YYYY-MM-DD.md` | `cross-girl-review-2026-02-17.md` |
| Archived exports | `{portfolio-slug}-export-YYYY-MM-DD.csv` | `cross-girl-export-2026-02-17.csv` |

## How to Use

1. Export campaign data from Seller Central (last 7 days, exclude last 2 days)
2. Save the CSV into the `input/` folder
3. Say "ppc review" or "analyze portfolio" — the skill picks up the file automatically
4. Review the generated report in `briefs/`
5. The CSV gets archived to `data/` and `input/` is cleared for next time

## What Each Report Contains

- Portfolio overview (totals, ACoS, ROAS, stage assessment)
- Prioritized action to-do list (P1/P2/P3)
- Campaign-by-campaign analysis with flags
- Structure check (missing campaign types)
- Summary with quick wins
