# Universal Organization & Efficiency Standards

**APPLIES TO:** All skills, all outputs, all work performed by Claude

---

## 📁 File Organization Hierarchy

**Every output must follow this structure:**

```
outputs/
├── {project-type}/              # e.g., research, data, reports, automation
│   ├── {specific-area}/         # e.g., market-intel, competitor-analysis
│   │   ├── briefs/              # Main outputs (USER READS THESE FIRST)
│   │   │   └── YYYY-MM-DD-{time}.md
│   │   ├── reports/             # Detailed analysis
│   │   │   ├── products/        # Subfolders by type
│   │   │   └── competitors/
│   │   ├── data/                # Raw data files
│   │   │   ├── products/        # Subfolders by type
│   │   │   ├── competitors/
│   │   │   └── search/
│   │   ├── snapshots/           # Historical comparison data
│   │   │   └── YYYY-MM-DD-{time}.json
│   │   ├── scripts/             # Automation scripts ONLY
│   │   │   └── {action}_{subject}.py
│   │   └── README.md            # Required folder guide
```

---

## 📖 Naming Conventions (STRICT)

### Date-Based Outputs
**Format:** `YYYY-MM-DD-{descriptor}.ext`

**Examples:**
- `2026-02-09-morning-brief.md`
- `2026-02-09-evening-check.md`
- `2026-02-09-weekly-summary.md`

### Subject-Based Outputs
**Format:** `{subject-slug}-YYYY-MM-DD.ext`

**Examples:**
- `cross-stitch-analysis-2026-02-09.md`
- `competitor-report-2026-02-09.md`
- `embroidery-deep-dive-2026-02-09.md`

### Data Files
**Format:** `{type}-{subject}-YYYY-MM-DD.json`

**Examples:**
- `product-cross-stitch-2026-02-09.json`
- `competitors-embroidery-2026-02-09.json`
- `search-results-fuse-beads-2026-02-09.json`

### Snapshots
**Format:** `YYYY-MM-DD-{time}.json`

**Examples:**
- `2026-02-09-morning.json`
- `2026-02-09-evening.json`
- `2026-02-09-weekly.json`

### Scripts
**Format:** `{action}_{subject}.py`

**Examples:**
- `generate_report.py`
- `process_data.py`
- `scrape_products.py`

---

## ✅ Efficiency Targets

**Every operation should meet:**

| Metric | Target | Why |
|--------|--------|-----|
| **Token usage** | <80,000 tokens | Cost efficiency, context management |
| **API cost** | <$0.20 per run | Budget-friendly automation |
| **Execution time** | <5 minutes | Fast feedback loop |
| **File count** | Minimal (1-3 main files) | Easy to navigate |
| **Folder depth** | Max 3 levels | User can find things quickly |

---

## ❌ Forbidden Practices

**NEVER:**
1. ❌ Dump files in root folders (use subfolders)
2. ❌ Mix scripts with output files in same folder
3. ❌ Create temp files without cleanup
4. ❌ Use ambiguous names:
   - `output.json` → ❌
   - `data.txt` → ❌
   - `test.py` → ❌
   - `temp.md` → ❌
5. ❌ Create 25+ files in one folder without subfolders
6. ❌ Use inconsistent naming (some with dates, some without)
7. ❌ Put scripts outside `scripts/` folder
8. ❌ Create duplicate files with confusing names

---

## 📊 Standard Output Structure

**Every skill run should create:**

### Minimum (Always)
- ✅ 1 main output file in `briefs/` or appropriate folder
- ✅ 1 README.md in root of output location (if first run)

### Optional (If Needed)
- 📄 Detailed reports in `reports/` subfolders
- 💾 Raw data files in `data/` subfolders
- 📸 Snapshot files in `snapshots/` (for historical comparison)
- 🔧 Scripts in `scripts/` folder

### Never
- ❌ Temporary files left in root
- ❌ Multiple versions of same file
- ❌ Unorganized data dumps

---

## 📋 README Requirements

**Every major output folder MUST have a README.md with:**

1. **Folder Purpose** - What this folder contains
2. **Folder Structure** - ASCII tree diagram
3. **Naming Conventions** - Format used in this folder
4. **What Goes Where** - Table showing file types → locations
5. **Daily Workflow** - How user interacts with outputs (if applicable)
6. **Cleanup Policy** - What to keep, what to archive

**Template:**
```markdown
# {Folder Name}

## 🚀 Quick Start
[How to use this folder]

## 📁 Folder Structure
[ASCII tree showing organization]

## 📖 File Naming Conventions
[Table of formats used]

## 🎯 What Goes Where
[Table mapping needs to folders]

## 🔄 Daily Workflow
[How user interacts with outputs]

## 📊 Efficiency Standards
[Targets for this specific workflow]

## 🗑️ Cleanup Policy
[What to keep, what to delete]
```

---

## 🎯 User Experience Standards

**User must be able to:**
1. ✅ **See what you're doing** by looking at folder structure
2. ✅ **Find outputs easily** by following logical hierarchy
3. ✅ **Understand file purpose** from name alone
4. ✅ **Navigate without asking** (self-documenting structure)
5. ✅ **Feel organized** (no chaos, no confusion)

---

## 📝 Skill-Specific Standards

**Each skill should define:**
- Specific folder structure for its outputs
- Naming patterns for its file types
- Efficiency targets specific to its operations
- Cleanup policies for its data

**But all skills must:**
- Follow the universal naming conventions above
- Maintain clean folder organization
- Never dump files in root
- Always create READMEs for major output folders

---

## 🔄 Enforcement

**These standards are enforced in:**
1. `CLAUDE.md` - Main project instructions
2. `.claude/skills/skill-creator/SKILL.md` - New skills inherit standards
3. `.claude/STANDARDS.md` - This file (single source of truth)
4. Individual skill `SKILL.md` files - Specific implementations

**When creating new skills:**
- Copy organization section from this file
- Customize for specific use case
- Maintain same principles and structure

---

## 📚 Examples

### Good Example: Market Intelligence
```
outputs/research/market-intel/
├── briefs/
│   ├── 2026-02-09-morning.md       ← User reads this
│   └── 2026-02-10-morning.md
├── reports/
│   ├── products/
│   │   └── cross-stitch-girls-2026-02-09.md
│   └── competitors/
│       └── cross-stitch-2026-02-09.md
├── data/
│   ├── products/
│   │   └── product-cross-stitch-2026-02-09.json
│   └── competitors/
│       └── competitors-cross-stitch-2026-02-09.json
├── snapshots/
│   └── 2026-02-09-morning.json
├── scripts/
│   └── generate_report.py
└── README.md
```

### Bad Example (DON'T DO THIS)
```
outputs/research/market-intel/
├── output.json                     ❌ Ambiguous name
├── data.json                       ❌ Ambiguous name
├── competitor_data_final.json      ❌ No date
├── competitor_data_final2.json     ❌ Duplicates
├── temp.json                       ❌ Temp file
├── script.py                       ❌ Script in root
├── generate.py                     ❌ Script in root
├── morning_report.md               ❌ No date
├── report_2.md                     ❌ Ambiguous
└── cross-stitch.md                 ❌ No date, unclear type
```

---

## 🎯 Quick Checklist

Before completing any task, verify:

- [ ] Files organized in logical folders (not root dump)
- [ ] Names follow YYYY-MM-DD-{descriptor} or {subject}-YYYY-MM-DD format
- [ ] Scripts are in `scripts/` folder
- [ ] Main output is clearly identifiable (in `briefs/` or obvious location)
- [ ] README exists for the output folder (if first time)
- [ ] No temp files left behind
- [ ] No ambiguous names (output.json, data.txt, etc.)
- [ ] Folder structure is self-documenting
- [ ] User can navigate without asking

---

*Version: 1.0*
*Last Updated: 2026-02-09*
*Applies to: All skills, all work*
