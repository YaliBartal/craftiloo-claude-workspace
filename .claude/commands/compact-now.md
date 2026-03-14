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
