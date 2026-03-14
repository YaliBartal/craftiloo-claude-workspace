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
