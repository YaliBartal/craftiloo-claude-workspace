# Portfolio Action Plan Outputs

Single-portfolio deep dives with impact-ranked action plans and execution logs.

---

## Folder Structure

```
portfolio-action-plan/
  briefs/          # Deep dive analysis + action plan (user reads first)
  snapshots/       # Machine-readable portfolio state JSON
  action-logs/     # What was proposed, approved, executed, and results
  README.md        # This file
```

## Naming Conventions

| File Type | Format | Example |
|-----------|--------|---------|
| Brief | `YYYY-MM-DD-{portfolio-slug}-brief.md` | `2026-03-03-fuse-beads-brief.md` |
| Snapshot | `YYYY-MM-DD-{portfolio-slug}-snapshot.json` | `2026-03-03-fuse-beads-snapshot.json` |
| Action Log | `YYYY-MM-DD-{portfolio-slug}-action-log.json` | `2026-03-03-fuse-beads-action-log.json` |

## What Goes Where

| Folder | Contains | Format |
|--------|----------|--------|
| `briefs/` | Full deep dive analysis + action plan table + execution results summary | Markdown |
| `snapshots/` | Portfolio state at time of analysis (metrics, campaigns, structure, rank data) | JSON |
| `action-logs/` | Every action proposed, user decision, execution status, API responses | JSON |

## Daily Workflow

1. User says "deep dive {portfolio}" or "fix {portfolio}"
2. Skill runs analysis -> saves brief + snapshot
3. User approves actions -> skill executes -> saves action log
4. Agent-state updated with last run date + completed pending actions
