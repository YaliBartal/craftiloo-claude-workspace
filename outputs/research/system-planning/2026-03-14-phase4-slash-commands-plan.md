# Phase 4: Slash Commands — Full Implementation Plan
**Created:** 2026-03-14
**Status:** Ready to implement (Phase 3 hooks must be done first)
**Target directory:** `.claude/commands/`

---

## Overview

Slash commands are `.md` files in `.claude/commands/`. Each file is a prompt template invoked with `/command-name` during interactive sessions. They're manual, lightweight, and designed for session management — not full skill workflows.

**Commands to create:**

| Command | File | Purpose | When to use |
|---------|------|---------|-------------|
| `/checkpoint` | checkpoint.md | Save mid-session progress | Context >50%, stepping away mid-task |
| `/wrap-up` | wrap-up.md | End-of-session housekeeping | After every interactive skill run |
| `/context-load` | context-load.md | Load right context files | Session start, after /clear |
| `/compact-now` | compact-now.md | Preserve state + compact | Context ~65%, at phase boundaries |
| `/handoff` | handoff.md | Park session mid-task | Ending with work still incomplete |

---

## Command 1: `/checkpoint`

**File:** `.claude/commands/checkpoint.md`
**Argument:** Optional topic slug (e.g., `/checkpoint weekly-ppc`)

```markdown
Save the current session state to a checkpoint file.

Topic from argument: $ARGUMENTS (use "session" if empty)

Create file at: outputs/research/handoffs/YYYY-MM-DD-HHMM-[topic]-checkpoint.md
(Use real current date/time for YYYY-MM-DD-HHMM, use the argument as [topic])

Write this exact structure:

---
type: checkpoint
created: [current timestamp]
topic: [argument or "session"]
context_level: [estimate: light / moderate / heavy]
---

## Current Task
[Exact skill or workflow running — specific, not generic]

## Status
[Percentage complete, current phase name, last completed step]

## Data on Disk
[Every file written this session — full absolute paths, one per bullet]
-

## Key Findings
[Critical numbers and facts found so far — be precise and specific.
Example: "Cross Stitch portfolio ACoS 34% vs target 28%, spend +12% WoW"]

## Pending Work
[What still needs to happen, in priority order — numbered]
1.
2.
3.

## Resume Instructions
[Step-by-step for a fresh session to continue this exact task:]
1. Read this checkpoint file
2. Load these context files: [list them explicitly]
3. Read these data files from disk: [list full paths]
4. First action: [exact next step — specific enough to act on immediately]

## Context Notes
[API errors hit, workarounds used, rate limits encountered, anything not in data files]

After writing, confirm:
"✅ Checkpoint saved: [full file path]
 Context level: [light/moderate/heavy]
 To resume: read [filename] and follow resume instructions."
```

---

## Command 2: `/wrap-up`

**File:** `.claude/commands/wrap-up.md`
**Argument:** None needed (infers from conversation)

```markdown
Complete end-of-session housekeeping after a skill run.

First, identify what just ran. If clear from conversation, proceed. If not, ask:
"Which skill just completed, and what was the subject/portfolio/product?"

Complete ALL steps below in order:

---

**STEP 1: Write Run Log**

Determine output area from skill name:
- PPC skills (except weekly-ppc-analysis) → outputs/research/ppc-agent/run-logs/
- weekly-ppc-analysis → outputs/research/ppc-weekly/run-logs/
- daily-market-intel → outputs/research/market-intel/run-logs/
- listing-* → outputs/research/listing-manager/run-logs/
- brand-analytics-weekly → outputs/research/brand-analytics/run-logs/
- competitor-* → outputs/research/competitor-analysis/run-logs/
- Other: match to the skill's output_location from its SKILL.md

File: YYYY-MM-DD-{skill-name}-{subject}.md

Content (be thorough — this is the archive):
## Run: [Skill Name] — [Subject] — [Date]
**Duration:** [approximate] | **Status:** [success / partial / failed]

### What Was Done
[Step-by-step narrative]

### API Calls Made
[MCPs called, data fetched, errors encountered]

### Key Findings
[Specific numbers, patterns, decisions, recommendations]

### Files Written
[Every file created or updated, with full paths]

### Errors & Workarounds
[Issues hit, how resolved]

### Recommendations for Next Run
[What to check first, known issues to watch, what to do differently]

---

**STEP 2: Update LESSONS.md**

File: .claude/skills/{skill-name}/LESSONS.md

Rules:
- Add/update distilled lessons (max ~15 items total in the list)
- Update Recent Runs: add this run (4-5 lines), remove oldest if >3 entries
- If a Known Issue recurred: move to Repeat Errors section, increment count ×N
- If lesson applies across skills: add to context/api-patterns.md or
  context/tooling-workarounds.md instead of LESSONS.md

---

**STEP 3: Verify Slack Notification**

If this skill normally posts to Slack:
- If sent during the run: confirm "✓ Slack sent to #channel-name"
- If not sent: trigger notification-hub now for this skill's output

---

**STEP 4: Confirm Completion**

Print:
"✅ Wrap-up complete:
 - Run log:    [full path]
 - LESSONS.md: [path] — [N] total lessons, [N] recent runs listed
 - Slack:      [sent to #channel] / [not applicable]
 - Next run:   [one sentence from recommendations]"
```

---

## Command 3: `/context-load`

**File:** `.claude/commands/context-load.md`
**Argument:** None (asks or infers)

```markdown
Load the relevant context files for the current task.

First, determine task type. Ask "What are you working on?" if not clear from conversation.

Based on the answer, read and internalize these files:

---

**Always load (every task type):**
- context/api-patterns.md
- context/tooling-workarounds.md

**PPC / campaign management work:**
- context/ppc-rules.md
- context/portfolio-name-map.json
  → Summarize as: portfolio name | ID | stage | slug (do NOT dump full JSON)

**Product / listing work:**
- context/hero-products.md
- context/sku-asin-mapping.json
  → Summarize as: ASIN | product name | portfolio name (do NOT dump full JSON)

**Competitive / market analysis:**
- context/competitors.md
- context/search-terms.md

**Business background / broad context:**
- context/business.md

**After /clear or resuming an interrupted task:**
Check outputs/research/handoffs/ for .md files created in the last 24 hours.
List them with creation times. If any exist, read the most recent and say:
"Found handoff from [time]: [task description]. Ready to resume: [next step]."
If none exist: "No recent handoffs found — starting fresh."

---

After loading, confirm:
"Context loaded:
 - Always: api-patterns.md ✓, tooling-workarounds.md ✓
 - Task-specific: [list files loaded] ✓
 - Handoff: [filename found and read] / [none found]
 - Context level: [light / moderate] — estimated from file sizes
 Ready for [task type]."
```

---

## Command 4: `/compact-now`

**File:** `.claude/commands/compact-now.md`
**Argument:** None

```markdown
Compact context intelligently: preserve state first, then compact, then restore.

---

**STEP 1: Write Pre-Compact Handoff**

Create: outputs/research/handoffs/YYYY-MM-DD-HHMM-manual-compact.md

Content:
---
type: pre-compact-manual
created: [timestamp]
triggered_by: /compact-now command
---

## Task
[Current skill/task — exact]

## Phase at Compact Point
[Which phase just completed and why compacting now]
Example: "Data fetch complete. All 4 API reports saved to disk. Compacting before analysis."

## Data on Disk
[Every file written this session — full absolute paths]
-

## Key Findings
[Critical numbers and conclusions from work done so far — be complete and specific]

## Pending Work (in order)
1.
2.

## Resume Instructions
1. Read this file completely
2. Load context files: [list which]
3. Read data files from disk: [list paths from above]
4. First action: [exact next step]

---

**STEP 2: Confirm**

Print: "Handoff written: [full path]. About to compact context."

---

**STEP 3: Compact**

Run /compact now.

---

**STEP 4: Restore After Compact**

Immediately after compaction, re-read the handoff file.
Print: "Resumed from handoff [filename].
 Task: [task]. Phase: [next phase].
 Next action: [first pending item]."

Then continue the work from that next action.
```

---

## Command 5: `/handoff`

**File:** `.claude/commands/handoff.md`
**Argument:** Optional topic slug (e.g., `/handoff listing-creator-crossstitch`)

```markdown
Write a structured handoff document before ending a session mid-task.

Topic from argument: $ARGUMENTS (use "task" if empty)

Create: outputs/research/handoffs/YYYY-MM-DD-HHMM-[topic]-handoff.md

---
type: handoff
created: [timestamp]
topic: [topic]
status: in-progress
---

## Task
[Exact skill or workflow — what was being done and why it matters]

## Status at Handoff
[% complete / current phase / what's done / what's blocked if anything]

## Data on Disk
[Every file written during this task — full absolute paths, one per bullet.
Describe what each file contains so the next session knows what to load.]
-

## Key Findings
[Self-contained briefing — someone reading ONLY this file should understand what was found.
Include specific numbers, portfolio states, ASIN data, any conclusions reached so far.]

## Pending Work
[Everything still needed, numbered by priority]
1.
2.
3.

## Resume Instructions
[Exact step-by-step for the next session:]
1. Read this file completely
2. Load context files: [list them with paths]
3. Read data files from disk: [list paths]
4. Verify: [any conditions to check — e.g., "confirm Monday pipeline ran: check outputs/research/ppc-agent/state/agent-state.json"]
5. First action: [exact next prompt or step — specific enough to start immediately]

## Context Notes
[Everything not captured in data files:]
- API rate limits hit or expected
- Errors encountered and workarounds used
- Decisions made and why (reasoning, not just outcomes)
- Things that were surprising or unexpected
- What NOT to do (save future-you from repeating a mistake)

---

After writing, print:
"✅ Handoff written: [full path]
 This session is safely parked. Resume by reading the handoff at the start of next session."
```

---

## Command Interaction Flow

```
Session starts
    │
    ▼
/context-load          ← Load right context files, check for handoffs
    │
    ▼
[Work happens — skill runs, API calls, analysis]
    │
    ├── Context ~50% ──► /checkpoint [topic]    ← Save state, keep going
    │
    ├── Context ~65% ──► /compact-now           ← Preserve + compact + restore
    │
    └── Context ~85% ──► /handoff [topic]       ← Save state → /clear → fresh session
                              │
                              ▼
                         [New session]
                              │
                              ▼
                         /context-load           ← Reads recent handoff automatically
    │
    ▼
[Skill completes successfully]
    │
    ▼
/wrap-up               ← Run log + LESSONS.md + Slack confirm
```

---

## Implementation Steps

1. Create `.claude/commands/` directory (if not exists)
2. Write 5 command files from content above
3. Test each command in interactive session:
   - `/checkpoint test` → verify file at correct path with correct structure
   - `/wrap-up` → verify run log + LESSONS.md both updated
   - `/context-load` → verify correct files read for task type stated
   - `/compact-now` → verify handoff written before compact fires
   - `/handoff myproject` → verify structured handoff at correct path

---

## Notes

- Commands are interactive only — not invoked in automated `claude -p` runs
- Arguments via `$ARGUMENTS` are optional in all commands
- Commands complement hooks: hooks enforce automatically, commands give you manual control
- `/wrap-up` essentially formalizes what CLAUDE.md already requires after every skill run
- `/context-load` is the interactive equivalent of what skill files do with "Read LESSONS.md first"
