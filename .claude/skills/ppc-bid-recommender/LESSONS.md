# Bid Recommender — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`, `context/ppc-rules.md`, `context/tooling-workarounds.md`
> Run log archive → `outputs/research/ppc-agent/run-logs/`

## Skill-Specific Lessons

1. ALWAYS read portfolio trackers BEFORE presenting recommendations — initial brief may include items already handled today
2. `list_sp_campaigns` API data can be stale if other sessions made changes earlier same day — cross-reference with portfolio tracker `change_log` as source of truth
3. Campaigns not found in ENABLED modifiers list are likely already PAUSED — check before recommending pauses

## Known Issues

### 1. Placement report missing `placementClassification` field
Core capability (Step 4b Placement Health Classification) needs per-placement ACoS data. Workaround: infer from campaign naming patterns.

### 2. API modifier data can be stale within same day
Princess Lacing showed 262% when tracker said 148%. Always cross-reference API values with tracker `change_log`.

## Repeat Errors

_None yet._

## Resolved Issues

_None yet._

## Recent Runs (last 3)

### Run: 2026-03-05
**Result:** Success — 121 campaigns analyzed, 8 TOS decreases applied, 0 errors
**Key outcome:** -$86/week estimated savings. 8 items skipped (already handled today or paused). Affected: Needlepoint, Bunny Knitting, Fairy Family, Cat & Hat.
