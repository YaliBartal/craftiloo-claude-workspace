# Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`, `context/ppc-rules.md`, `context/tooling-workarounds.md`

## Skill-Specific Lessons

1. ppc-daily-health recipe posts to `#claude-morning-brief`, NOT `#claude-ppc-updates` — always check recipe routing before posting
2. User instruction "Do NOT post to #claude-alerts" overrides the recipe's alert escalation rules
3. Keep message under 2000 chars — bullet format works well, skip tables entirely

## Known Issues

_None yet._

## Repeat Errors

_None yet._

## Resolved Issues

_None yet._

## Recent Runs (last 3)

### Run: 2026-03-11
**Result:** Success
**Calling skill:** ppc-daily-health

**What happened:**
- Posted ppc-daily-health summary to `#claude-morning-brief` (workspace: craft)
- Message posted under 2000 chars using bullet format
- Skipped #claude-alerts per user efficiency instructions

**What didn't work:**
- Nothing

**Lesson learned:**
- Recipe channel routing is canonical — ppc-daily-health → #claude-morning-brief, not #claude-ppc-updates
