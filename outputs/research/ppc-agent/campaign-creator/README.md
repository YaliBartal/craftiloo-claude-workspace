# PPC Campaign Creator — Output Folder

## Purpose

Stores campaign creation proposals, execution logs, and briefs from the PPC Campaign Creator skill.

## Folder Structure

```
campaign-creator/
├── README.md                              # This file
├── {YYYY-MM-DD}-campaigns-created.md      # Human-readable brief per run
└── {YYYY-MM-DD}-creation-log.json         # Machine-readable log per run
```

## File Naming

| File Type | Format | Example |
|-----------|--------|---------|
| Brief | `{YYYY-MM-DD}-campaigns-created.md` | `2026-03-02-campaigns-created.md` |
| Log | `{YYYY-MM-DD}-creation-log.json` | `2026-03-02-creation-log.json` |

## What Goes Where

- **Briefs** — Human-readable summary of proposed and created campaigns, approval decisions, and results
- **Logs** — Machine-readable JSON with campaign IDs, API responses, and status per step (used by other PPC skills for reference)

## Daily Workflow

This folder is populated on demand when the Campaign Creator skill runs. Not cadence-based — triggered by pending actions from Search Term Harvester, Rank Optimizer, or Portfolio Summary.
