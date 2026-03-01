# PPC Agent Outputs

Outputs from the PPC Agent orchestrator and its sub-skills.

## Folder Structure

```
ppc-agent/
├── agent-state.json           # Cadence tracker — when each task was last run
├── daily/                     # Daily PPC Health Checks
│   ├── YYYY-MM-DD-health-check.md
│   └── YYYY-MM-DD-health-snapshot.json
├── bids/                      # Bid Adjustment Recommendations
│   ├── YYYY-MM-DD-bid-recommendations.md
│   └── YYYY-MM-DD-bid-changes-applied.json
├── search-terms/              # Search Term Harvest Records
│   ├── YYYY-MM-DD-search-term-harvest.md
│   ├── YYYY-MM-DD-search-term-report.json   (raw API data)
│   └── YYYY-MM-DD-applied-actions.json
├── portfolio/                 # Portfolio Performance Summaries
│   ├── YYYY-MM-DD-portfolio-summary.md
│   └── YYYY-MM-DD-portfolio-snapshot.json
├── monthly/                   # Monthly Strategic Reviews
│   └── YYYY-MM-monthly-review.md
└── README.md                  # This file
```

## Naming Conventions

| File Type | Format |
|-----------|--------|
| Daily briefs | `YYYY-MM-DD-health-check.md` |
| Daily snapshots | `YYYY-MM-DD-health-snapshot.json` |
| Bid briefs | `YYYY-MM-DD-bid-recommendations.md` |
| Bid logs | `YYYY-MM-DD-bid-changes-applied.json` |
| Search term briefs | `YYYY-MM-DD-search-term-harvest.md` |
| Search term data | `YYYY-MM-DD-search-term-report.json` |
| Applied actions | `YYYY-MM-DD-applied-actions.json` |
| Portfolio briefs | `YYYY-MM-DD-portfolio-summary.md` |
| Portfolio snapshots | `YYYY-MM-DD-portfolio-snapshot.json` |
| Monthly reviews | `YYYY-MM-monthly-review.md` |

## Cadence

| Task | Frequency | Subfolder |
|------|-----------|-----------|
| Daily Health Check | Every morning | `daily/` |
| Search Term Harvest | Every 2-3 days | `search-terms/` |
| Bid Adjustments | Every 2-3 days | `bids/` |
| Portfolio Summary | Every 2-3 days | `portfolio/` |
| Monthly Review | Monthly | `monthly/` |

## Data Flow

- **Daily health checks** read from Market Intel snapshots (`../market-intel/snapshots/`)
- **Bid recommendations** read from Weekly PPC snapshots (`../ppc-weekly/snapshots/`)
- **Search term harvests** read from Negative Keyword Generator logs (`../negative-keywords/data/`)
- **Monthly reviews** read from all of the above
- **agent-state.json** is updated after every skill run
