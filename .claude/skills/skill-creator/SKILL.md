---
name: skill-creator
description: Creates new project-specific skills with proper structure and routing
triggers:
  - create a skill
  - new skill
  - build a skill
  - make a skill for
  - I need a skill that
output_location: .claude/skills/[skill-name]/
---

# Skill Creator

**USE WHEN** user says: "create a skill", "new skill", "build a skill", "make a skill for", "I need a skill that"

---

## ⚠️ BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/skill-creator/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"⚠️ Repeat issue (×N): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

Creates new project-specific skills in `.claude/skills/[skill-name]/`

---

## ⚡ Organization Standards (ALWAYS Include in New Skills)

**Every skill MUST include organization standards in its SKILL.md.**

When creating a new skill, add this section after "What This Does":

```markdown
## ⚡ Organization & Efficiency Standards

**CRITICAL: Follow these standards for EVERY run:**

### File Organization
```
{output_location}/
├── briefs/          # Main outputs (what user reads first)
├── reports/         # Detailed analysis (subfolders by type)
├── data/            # Raw data files (subfolders by type)
├── snapshots/       # Historical/comparison data (if needed)
├── scripts/         # Automation scripts ONLY
└── README.md        # Folder guide
```

### Naming Conventions (STRICT)
- **Date-based:** `YYYY-MM-DD-{descriptor}.ext`
- **Subject-based:** `{subject-slug}-YYYY-MM-DD.ext`
- **Data files:** `{type}-{subject}-YYYY-MM-DD.json`

### Efficiency Targets
- ✅ <80K tokens per run
- ✅ <$0.20 cost (if using paid APIs)
- ✅ <5 minutes execution
- ✅ Minimal file count
- ✅ Clean organization

### Forbidden
- ❌ Root folder dumps
- ❌ Scripts mixed with outputs
- ❌ Temp files without cleanup
- ❌ Ambiguous names
```

---

## Process

### 1. Understand the Skill
Ask:
- **What should this skill do?** (input → output)
- **When would you use it?** (trigger phrases)
- **What's the expected output?** (file type, location)

### 2. Create the Skill

Create folder: `.claude/skills/[skill-name]/`

**Create TWO files:**

#### A. `SKILL.md` with this structure:

```markdown
---
name: [skill-name]
description: [One sentence - what this skill does]
triggers:
  - [trigger phrase 1]
  - [trigger phrase 2]
  - [trigger phrase 3]
output_location: [outputs/research/ or outputs/data/ or N/A]
---

# [Skill Name]

**USE WHEN** user says: "[trigger 1]", "[trigger 2]", "[trigger 3]"

---

## ⚠️ BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/[skill-name]/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"⚠️ Repeat issue (×N): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does
[One sentence description]

---

## Process
[Step-by-step instructions for Claude]

---

## Output
- **Format:** [file type]
- **Location:** [outputs/research/ or outputs/data/]

---

## ⚠️ AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/[skill-name]/LESSONS.md`.**

### 1. Write a Run Log Entry
Add a new entry at the **TOP** of the Run Log section (see LESSONS.md for format).

### 2. Update Issue Tracking
- New problem → **Known Issues**
- Known Issue again → **Repeat Errors** (increment count, tell user)
- Fixed issue → **Resolved Issues**

### 3. Tell the User
End output with a **Lessons Update** note.

**Do NOT skip this. The system only improves if every run is logged honestly.**
```

#### B. `LESSONS.md` with this structure:

```markdown
# Lessons Learned — [Skill Name]

> **Living document.** Claude MUST read this before every run and write to it after every run.

---

## How to Use This File

### Before Every Run
1. Read this entire file
2. Check **Known Issues** for active problems to avoid
3. Check **Repeat Errors** — if you hit the same issue again, flag it to the user immediately
4. Apply all lessons to your execution plan

### After Every Run
1. Add a new entry under **Run Log** using the template below
2. If something went wrong, add it to **Known Issues**
3. If a Known Issue happened again, move it to **Repeat Errors** and increment the count
4. If you solved a Known Issue, move it to **Resolved Issues**

---

## Run Log

_No runs logged yet._

---

## Known Issues

_None yet._

---

## Repeat Errors

_None yet._

---

## Resolved Issues

_None yet._
```

**BOTH files are required.** Never create a skill without LESSONS.md.

### 3. Update Routing

Add to `CLAUDE.md` Skill Routing table:

```markdown
| "[trigger phrase]" | → `.claude/skills/[skill-name]/` |
```

---

## Optional: Scripts

If the skill needs custom API calls or automation:
- Create `scripts/` subfolder
- Add Python/bash files as needed
- Reference in SKILL.md process

---

## Output Location

Skills are always saved to: `.claude/skills/[skill-name]/SKILL.md`

**Project-local only** — not global Claude skills.

---

## ⚠️ AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/skill-creator/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Goals:**
- [ ] Goal 1
- [ ] Goal 2

**Result:** ✅ Success / ⚠️ Partial / ❌ Failed

**What happened:**
- (What went according to plan)

**What didn't work:**
- (Any issues, with specifics)

**Is this a repeat error?** Yes/No — if yes, which one?

**Lesson learned:**
- (What to do differently next time)

**Tokens/cost:** ~XX K tokens
```

### 2. Update Issue Tracking

| Situation | Action |
|-----------|--------|
| New problem | Add to **Known Issues** |
| Known Issue happened again | Move to **Repeat Errors**, increment count, **tell the user** |
| Fixed a Known Issue | Move to **Resolved Issues** |

### 3. Tell the User

End your output with a **Lessons Update** note:
- What you logged
- Any repeat errors encountered
- Suggestions for skill improvement

**Do NOT skip this. The system only improves if every run is logged honestly.**
