# PPC Daily Health — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`, `context/ppc-rules.md`, `context/tooling-workarounds.md`
> Run log archive → `outputs/research/ppc-agent/run-logs/`

## Skill-Specific Lessons

1. Listing push + PPC restructuring = dramatic rank gains within 2-5 days (Fairy Family proof of concept: +9 top-10 keywords)
2. Campaign data from `list_sp_campaigns` returns JSON code blocks, not markdown tables — use regex to extract
3. Campaign API gives budgets but not actual spend — use weekly report ACoS figures instead
4. Day-over-day rank comparison adds significant value — catches drops that weekly comparison misses
5. 3-day gaps are acceptable for health checks but miss day-to-day volatility. Aim for daily when possible
6. Use weekly PPC summary for actual spend/sales/ACoS — campaign API only gives budget caps
7. Rank radar `list_rank_radars` returns slightly different top10 counts than market intel snapshot — DataDive updates daily, use fresh call

## Known Issues

_None skill-specific — cross-skill issues in context/ files._

## Repeat Errors

_None yet._

## Resolved Issues

_None yet._

## Recent Runs (last 3)

### Run: 2026-03-08
**Result:** Success — 173 campaigns, net +10 top-10 account-wide (222→232)
**Key outcome:** Fairy Sewing +9 top-10 keywords (biggest rank surge in account history). 6 GREEN, 7 YELLOW, 4 RED.

### Run: 2026-03-05
**Result:** Success — 156 campaigns, 9 GREEN, 4 YELLOW, 4 RED
**Key outcome:** Fairy Sewing +3 top-10 (deep dive changes working after 2 days). Mini Fuse Beads -2 (expected post-restructuring).

### Run: 2026-03-03
**Result:** Success — 155 campaigns, day-over-day comparison now working
**Key outcome:** Latch Hook Pencil Cases -4 top-10 (biggest drop, caught by daily comparison).
