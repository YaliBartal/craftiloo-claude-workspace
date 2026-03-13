# Portfolio Summary — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`, `context/ppc-rules.md`, `context/tooling-workarounds.md`
> Run log archive → `outputs/research/ppc-agent/run-logs/`

## Skill-Specific Lessons

1. Always have fallback to weekly snapshot data when campaign reports are slow
2. Build a persistent portfolio name mapping (API name → display name) to avoid mismatches
3. Campaign type classification by name works ~90% but "TOS" campaigns without SK/MK prefix are ambiguous — default to SK
4. Systemic Broad campaign gap is a standard check — 9 of 18 portfolios missing Broad campaigns
5. For portfolio deep dives, always call ENABLED and PAUSED separately — never ALL (200 ARCHIVED clog the response)
6. Background agents for keyword/target pulls save time vs sequential calls
7. 7-day search term data sufficient for pattern identification; 30-day only for negation decisions
8. Portfolio with strong organic (78% organic ratio) needs PPC focused on rank defense, not volume generation

## Known Issues

### 1. Campaign report can get stuck in PENDING
After 2 min, fall back to most recent weekly snapshot data. Note staleness in report header.

### 2. Systemic Broad campaign gap
9 of 18 portfolios missing Broad campaigns. Flag every run until resolved.

## Repeat Errors

_None yet._

## Resolved Issues

_None yet._

## Recent Runs (last 3)

### Run: 2026-03-02 (Fuse Beads Deep Dive)
**Result:** Success — 14 ENABLED campaigns, 3 critical issues found
**Key outcome:** SK fuse beads bleeding 119.5% ACoS, "fuse beads" rank #4→#10, "perler beads bulk" #20→#40.

### Run: 2026-03-02
**Result:** Success — 18 portfolios analyzed, 6 red flags, 11 structural gaps
**Key outcome:** Systemic Broad campaign gap (9/18 portfolios). ~31 LOW BID dormant campaigns.
