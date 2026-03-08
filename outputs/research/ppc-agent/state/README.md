# PPC Agent State

Operational memory for the PPC Agent. **Not outputs** — these files persist and evolve across skill runs.

## Contents

| File | Purpose |
|------|---------|
| `agent-state.json` | Global cadence tracker, portfolio index, pending actions, upcoming reviews, applied changes |
| `{portfolio-slug}.json` | Per-portfolio tracker — goals, baseline, metrics, change log, pending actions, reviews |

## Who Reads/Writes

| Skill | Reads | Writes |
|-------|-------|--------|
| **ppc-agent** (orchestrator) | All files | agent-state.json (cadence, portfolio_index, pending, reviews) |
| **ppc-portfolio-action-plan** | Portfolio tracker + agent-state | Both (full tracker update + agent-state index) |
| **ppc-daily-health** | All trackers + agent-state | Both (latest_metrics, metric_history, health_status) |
| **ppc-bid-recommender** | Portfolio trackers + agent-state | Both (change_log, pending_actions) |
| **ppc-search-term-harvester** | Portfolio trackers + agent-state | Both (change_log, pending_actions) |
| **ppc-portfolio-summary** | agent-state | Neither (orchestrator handles updates) |

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

Portfolio trackers: `{portfolio-slug}.json` (kebab-case from portfolio name)
