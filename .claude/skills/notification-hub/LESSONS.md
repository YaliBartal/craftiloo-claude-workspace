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

### Run: 2026-03-12 (ppc-daily-health)
**Result:** Success
**Calling skill:** ppc-daily-health

**What happened:**
- Posted ppc-daily-health summary to `#claude-morning-brief` (workspace: craft)
- 1 RED (Needlepoint), 11 YELLOW, 5 GREEN. CS Backpack Charms upgraded RED→GREEN (stock resolved)
- Big review day flag: 9 portfolios due today
- Skipped #claude-alerts per user efficiency instructions

**What didn't work:**
- Nothing

**Lesson learned:**
- User may specify wrong channel (ppc-updates) but recipe routing (morning-brief) is canonical — always follow LESSONS.md lesson #1

---

### Run: 2026-03-12
**Result:** Success
**Calling skill:** daily-market-intel

**What happened:**
- Posted daily-market-intel summary to `#claude-morning-brief` (workspace: craft)
- Noted SB stale data + 5 alerts (OOS, crisis, low stock, SB 401)
- Skipped #claude-alerts per user efficiency instructions

**What didn't work:**
- Nothing

**Lesson learned:**
- When SB data is stale, note it clearly inline rather than omitting the section

### Run: 2026-03-11 (Refresh)
**Result:** Success
**Calling skill:** ppc-daily-health (2nd run today)

**What happened:**
- Posted ppc-daily-health refresh summary to `#claude-morning-brief` (workspace: craft)
- 2 RED flags: CS Backpack Charms stock crisis + Needlepoint PAUSED campaigns
- Skipped #claude-alerts per user efficiency instructions

**What didn't work:**
- Nothing

**Lesson learned:**
- On re-runs same day, label message as "(Refresh)" so it's clear it's a second post

