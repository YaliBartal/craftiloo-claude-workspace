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
