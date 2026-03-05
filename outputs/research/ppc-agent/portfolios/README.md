# Portfolio Trackers

One JSON file per portfolio — the complete operational memory for each portfolio.

## Purpose

Each tracker is the **single source of truth** for what the PPC agent knows about a portfolio:
- Goals and targets
- Baseline metrics (before agent started making changes)
- Every change made (with before/after values)
- What's planned next
- Which skills have been run
- Whether things are improving

## Structure

```
portfolios/
├── README.md                       # This file
├── fairy-family.json               # Seeded from deep dive data
├── fuse-beads.json                 # Seeded from deep dive data
├── cross-embroidery-kits.json      # Seeded from deep dive data
├── 4-flowers-embroidery.json       # Skeleton (filled on first deep dive)
├── catch-all-auto.json
├── shield-all.json
├── embroidery-for-kids.json
├── cross-stitch-backpack-charms.json
├── cat-and-hat-knitting.json
├── latch-hook-pillow.json
├── bunny-knitting-loom-kit.json
├── latch-hook-kits.json
├── dessert-family.json
├── biggie-beads.json
└── stitch-dictionary-all.json
```

## Tracker JSON Sections

| Section | Purpose |
|---------|---------|
| `portfolio` | Identity — name, ID, slug, stage, hero ASINs, keywords |
| `goals` | ACoS/CVR targets, rank targets, budget envelope, strategic notes |
| `baseline` | Write-once metrics snapshot from before changes started |
| `latest_metrics` | Most recent metrics + delta vs baseline |
| `metric_history[]` | Time-series snapshots (max 90 entries, 3 months) |
| `change_log[]` | Every API change made — category, old/new values, status |
| `pending_actions[]` | Queued work with priority and due dates |
| `scheduled_reviews[]` | Upcoming re-check dates |
| `skills_run[]` | Log of skill executions with results |
| `improvement_assessment` | Is this portfolio improving? Trend + confidence + verdict |

## Naming Convention

File: `{portfolio-slug}.json` (kebab-case from portfolio name)

## Who Reads/Writes

- **ppc-portfolio-action-plan** — creates tracker, sets baseline, writes all sections
- **ppc-daily-health** — updates latest_metrics + metric_history for all portfolios
- **ppc-bid-recommender** — writes change_log for bid changes
- **ppc-search-term-harvester** — writes change_log for negatives
- **ppc-portfolio-summary** — updates latest_metrics + metric_history
- **ppc-agent** (orchestrator) — reads all trackers for cadence overview
