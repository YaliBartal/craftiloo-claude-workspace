# PPC Weekly Analysis

Weekly PPC analysis reports with week-over-week comparison.

## Folder Structure

```
ppc-weekly/
├── input/         # Drop 4 Seller Central CSV exports here
├── briefs/        # Weekly analysis reports
├── snapshots/     # Archived weekly data
│   └── YYYY-MM-DD/
│       ├── campaign-report.csv
│       ├── search-term-report.csv
│       ├── placement-report.csv
│       ├── targeting-report.csv
│       └── summary.json
├── data/          # Processed/intermediate data
└── README.md      # This file
```

## Weekly Workflow

1. Export 4 reports from Seller Central (last 7 days, excl. last 2):
   - Campaigns, Search Terms, Placements, Targets
2. Drop all 4 CSVs into `input/`
3. Run: "weekly ppc analysis"
4. Reports appear in `briefs/`, data archived to `snapshots/`

## Naming Conventions

| File Type | Format |
|-----------|--------|
| Weekly reports | `weekly-ppc-analysis-YYYY-MM-DD.md` |
| Snapshot folders | `YYYY-MM-DD/` |

## What Goes Where

| Folder | Contents |
|--------|----------|
| `input/` | Raw CSVs before processing (auto-cleaned after each run) |
| `briefs/` | Final analysis reports |
| `snapshots/` | Archived CSVs + summary.json per week |
| `data/` | Any intermediate processed files |
