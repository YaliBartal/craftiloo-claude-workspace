# PPC Agent — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`, `context/ppc-rules.md`, `context/tooling-workarounds.md`
> Run log archive → `outputs/research/ppc-agent/run-logs/`

## Skill-Specific Lessons

1. **Portfolio tracker updates are MANDATORY** after any change — update both `agent-state.json` AND portfolio `.json` tracker immediately after API calls succeed
2. Summary objects are the right pattern for large arrays — recompute in Step 8a after every skill run
3. Don't create state fields for skills that haven't run yet (e.g., `organic_momentum` was dead from day 1)
4. Always validate JSON after Python script writes (Unicode/encoding issues on Windows)
5. Seller Board 30d data maps cleanly to portfolios via sku-asin-mapping.json — schedule as monthly revenue tier refresh
6. Every sub-skill completion must post its notification-hub recipe to Slack (`#claude-ppc-updates` / `#claude-alerts`)
7. The agent was "fire-and-forget" — Action Validator (Step 3d) closes the feedback loop by comparing fresh data against change_log before-values
8. Campaign Lifecycle Tracker prevents new campaigns from being forgotten (5 phases: AWAITING_ENABLE → RAMPING → EARLY → ESTABLISHED → GRADUATED)
9. Stale action hygiene: P1 >7d re-validate, P2 >14d re-validate, P3 >21d auto-expire, P4 >30d auto-expire
10. When stock <10 units with no Buy Box, PPC is pure waste — pause immediately

## Known Issues

_None skill-specific — cross-skill issues in context/ files._

## Repeat Errors

_None yet._

## Resolved Issues

_None yet._

## Recent Runs (last 3)

### Run: 2026-03-10 (v2.2 — Phases C+D+E)
**Result:** Success — Revenue tiers bootstrapped (T1=11, T2=2, T3=4), removed dead `organic_momentum` field, added listing change tracking
**Key outcome:** agent-state.json 60K→38K bytes (36%), SKILL.md 1083→845 lines (22%)

### Run: 2026-03-10 (v2.2 — Phases 1-3)
**Result:** Success — Action Validator, Campaign Lifecycle Tracker, Stale Action Hygiene added
**Key outcome:** System moved from open-loop to closed-loop (changes are now validated)

### Run: 2026-03-09 (v2.1)
**Result:** Success — Revenue-weighted portfolio rotation + optimization scan protocol
