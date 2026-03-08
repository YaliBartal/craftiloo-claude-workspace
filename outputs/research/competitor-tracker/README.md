# Competitor Tracker Output

Weekly competitive intelligence data from the `competitor-price-serp-tracker` skill.

## Folder Structure

```
competitor-tracker/
  briefs/         Weekly markdown briefs (what you read first)
  snapshots/      Weekly JSON snapshots (product data + alerts)
  serp/           Weekly SERP position data (keyword rankings)
  trends.json     Rolling 12-week summary for trend analysis
  README.md       This file
```

## File Naming

| Type | Format | Example |
|------|--------|---------|
| Brief | `YYYY-MM-DD-weekly-brief.md` | `2026-03-07-weekly-brief.md` |
| Snapshot | `YYYY-MM-DD-snapshot.json` | `2026-03-07-snapshot.json` |
| SERP | `YYYY-MM-DD-serp.json` | `2026-03-07-serp.json` |

## Data Flow

1. Config: `context/competitor-config.json` (ASINs + keywords + thresholds)
2. Scrape: Apify product + SERP scrapers
3. Compare: WoW deltas against previous snapshot
4. Alert: Threshold-based alerts
5. Store: Snapshot + SERP + trends.json
6. Flag: Write competitive flags to PPC agent state
7. Brief: Human-readable weekly summary

## Consumed By

- **PPC Daily Health** -- reads competitive flags from agent-state.json
- **PPC Bid Recommender** -- factors competitive pressure into bid decisions
- **PPC Monthly Review** -- uses trends.json for competitive landscape narrative
