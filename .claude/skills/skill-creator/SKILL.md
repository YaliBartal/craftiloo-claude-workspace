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

## What This Does

Creates new project-specific skills in `.claude/skills/[skill-name]/`

---

## Process

### 1. Understand the Skill
Ask:
- **What should this skill do?** (input → output)
- **When would you use it?** (trigger phrases)
- **What's the expected output?** (file type, location)

### 2. Create the Skill

Create folder: `.claude/skills/[skill-name]/`

Create `SKILL.md` with this structure:

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

## What This Does
[One sentence description]

---

## Process
[Step-by-step instructions for Claude]

---

## Output
- **Format:** [file type]
- **Location:** [outputs/research/ or outputs/data/]
```

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
