# Craftiloo Workspace Upgrade — Implementation Plan
**Created:** 2026-03-14
**Based on:** Claude Code best practices research (everything-claude-code, awesome-claude-code, ykdojo tips, rohitg00 toolkit, Florian ultimate guide)
**Status tracker:** `.claude/projects/-home-yali-workspace/memory/project_workspace_upgrade.md`

---

## Baseline State (Before Upgrades)

- `settings.json`: permissions only — no hooks, no token config, no env vars
- `settings.local.json`: all 9 MCP servers permanently enabled = **142 tools loaded upfront every session**
- No `.claude/hooks/` directory — zero lifecycle hooks
- No `.claude/commands/` directory — zero slash commands
- No handoff system — context lost on every /clear
- Uniform `claude-sonnet-4-6` for all skills, including simple ones
- No context pressure protocol anywhere in CLAUDE.md
- Long skills (weekly-ppc, ppc-agent-tuesday) hitting 70%+ context with no strategy

---

## Phase 1 — Zero-Code Wins ✅
**Effort:** 30 min | **Files:** `settings.json`, `CLAUDE.md`

### 1A: settings.json
Add to `.claude/settings.json`:
```json
"env": {
  "ENABLE_TOOL_SEARCH": "true"
}
```
**Impact:** Lazy-loads MCP tool schemas on demand instead of upfront.
Frees 5,000–10,000 tokens per session (142 tools × ~50 tokens/schema = 7,100 tokens currently burned before Claude does anything).

**Note on maxThinkingTokens:** Research suggests setting this to 10,000 (from default 31,999 for 68% reduction). Exact settings.json key needs verification before adding. Keep as Phase 1 follow-up once confirmed valid.

### 1B: CLAUDE.md Context Management Protocol
Add new section "## Context Management Protocol" after Safety Rules section.
Contains: 70/85/90% threshold table, strategic compaction points, handoff requirement, efficiency rules.

---

## Phase 2 — Context Pressure Protocol
**Effort:** 20 min | **File:** `CLAUDE.md`
**(Merged into Phase 1 — done together)**

New section to add to CLAUDE.md (after Safety Rules):

```markdown
## Context Management Protocol

**Context pressure thresholds — output quality degrades sharply:**

| Context % | What's Happening | Required Action |
|-----------|-----------------|-----------------|
| 0–50% | Normal | Work freely |
| 50–70% | Minor slowdown | Prefer shorter outputs; use save_path |
| **70%** | **Precision drops** | **Run /compact at next logical break** |
| **85%** | **Hallucinations increase** | **Stop, /compact immediately** |
| **90%+** | **Erratic behavior** | **Write handoff → /clear → fresh session** |

**Strategic compaction in long skill runs:**
- After all API data fetched and saved to disk → compact before analysis
- After analysis written → compact before final report
- After failed approach → compact before retrying
- After reading large file batches → compact before acting

**Before /compact or /clear — always write a handoff:**
- File: `outputs/research/handoffs/YYYY-MM-DD-HHMM-[topic]-handoff.md`
- Must include: task status, key numbers, files written, pending work, resume instructions

**Context efficiency rules:**
- Never pass raw API data through context — use save_path for outputs >1KB
- Read only needed sections (use offset + limit params)
- Parallel API calls over sequential — batching cuts turns in half
- After fetching + saving all data: that's the right moment to compact
```

---

## Phase 3 — Hooks System
**Effort:** 2–3 hours | **New directory:** `.claude/hooks/`

### Hooks Configuration in settings.json

Add `"hooks"` key to `.claude/settings.json`:

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {"type": "command", "command": "bash /home/yali/workspace/.claude/hooks/secret-scanner.sh"},
        {"type": "command", "command": "bash /home/yali/workspace/.claude/hooks/block-md-creation.sh"}
      ]
    },
    {
      "matcher": "Read",
      "hooks": [
        {"type": "command", "command": "bash /home/yali/workspace/.claude/hooks/block-env-read.sh"}
      ]
    },
    {
      "matcher": "Bash",
      "hooks": [
        {"type": "command", "command": "bash /home/yali/workspace/.claude/hooks/bash-safety.sh"}
      ]
    }
  ],
  "PreCompact": [
    {
      "hooks": [
        {"type": "command", "command": "bash /home/yali/workspace/.claude/hooks/pre-compact-handoff.sh"}
      ]
    }
  ],
  "Stop": [
    {
      "hooks": [
        {"type": "command", "command": "bash /home/yali/workspace/.claude/hooks/session-end-reminder.sh"}
      ]
    }
  ]
}
```

### Hook Scripts

**1. secret-scanner.sh — PreToolUse on Write/Edit**
Scans content being written for API key value patterns (not variable names).
Blocks write with exit 2 if credential values detected.
Protects against our 71 API keys leaking into git-pushed outputs.

Key patterns to detect: `Atna|` (Sellerboard token structure), `amzn1.application-oa2-client.`,
`Atzr|` (Amazon access tokens), `xoxb-` (Slack bot tokens), `xoxp-` (Slack user tokens),
`ghp_` (GitHub tokens), `AKIA[0-9A-Z]{16}` (AWS access keys).

**2. block-env-read.sh — PreToolUse on Read**
Blocks direct reading of `.env`, `.key`, `.pem`, `credentials.json`.
Credentials already loaded into environment by skill-runner.py's load_env().
There is no legitimate reason for Claude to read the raw .env file directly.

**3. bash-safety.sh — PreToolUse on Bash**
Blocks: `rm -rf /`, `rm -rf *`, `rm -rf .`, `git push --force`, `git push -f`,
`git reset --hard`, `DROP TABLE`, `DELETE FROM WHERE 1`, `> .env`.
Catches catastrophic commands that could destroy our automation outputs or credentials.

**4. pre-compact-handoff.sh — PreCompact**
Creates timestamped file in `outputs/research/handoffs/` when auto-compaction fires.
Prints message telling Claude to populate it with current state.
After compaction, Claude reads handoff to continue without information loss.

**5. session-end-reminder.sh — Stop**
On session end, checks git status for LESSONS.md or run-log changes.
If output files were written but no LESSONS.md updated → prints reminder.
Enforces our mandatory post-run lessons discipline automatically.

**6. block-md-creation.sh — PreToolUse on Write**
Warns (does not block) when .md files are being created outside allowed locations.
Allowed: `outputs/research/`, `.claude/skills/`, `context/`, `outputs/research/handoffs/`, root `.md` files.
Warning only — informs Claude it may be violating file organization rules.

---

## Phase 4 — Slash Commands
**Effort:** 1 hour | **New directory:** `.claude/commands/`

### `/checkpoint` — Save mid-session progress
Creates handoff file at `outputs/research/handoffs/YYYY-MM-DD-HHMM-[task]-checkpoint.md`.
Includes: task status, files written, key findings, pending work, resume instructions.
Use: any time context climbs above 50% during interactive skill runs.

### `/wrap-up` — End-of-session housekeeping
Writes run log to `outputs/research/{area}/run-logs/`.
Updates skill LESSONS.md (recent runs, distilled lessons, repeat errors).
Confirms Slack notification was sent.
Use: after every interactive skill run.

### `/context-load` — Load relevant context for current task
Prompts for task type, then loads appropriate subset of context files.
Always: api-patterns.md, tooling-workarounds.md.
PPC tasks: + ppc-rules.md, portfolio-name-map.json summary.
Product tasks: + hero-products.md, sku-asin-mapping.json summary.
Competitive tasks: + competitors.md, search-terms.md.
After /clear: also checks handoffs/ for recent files.

### `/compact-now` — Compact with state preservation
Writes pre-compact handoff file first.
Then runs /compact.
After compaction, re-reads handoff to restore context.
Use: manual compact at any logical phase boundary.

### `/handoff` — Write structured handoff before ending session mid-task
Creates `outputs/research/handoffs/YYYY-MM-DD-HHMM-[task]-handoff.md`.
Full structure: task, status, data on disk, key findings, pending work, resume instructions, context notes.
Use: before ending a session when a task is incomplete.

---

## Phase 5 — Handoff System Infrastructure
**Effort:** 30 min | **New directory:** `outputs/research/handoffs/`

Create directory with `README.md` documenting:
- Purpose (context continuity between sessions)
- File naming: `YYYY-MM-DD-HHMM-[task-slug]-[type].md`
- Types: checkpoint, handoff, pre-compact
- Lifecycle: working documents, cleaned up monthly after task completion

---

## Phase 6 — Strategic Compaction in Long Skills
**Effort:** 1 hour | **Files:** 4 SKILL.md files

Add "Context Management Strategy" section to top of:
- `weekly-ppc-analysis/SKILL.md` (50 min, 80 turns)
- `ppc-agent/SKILL.md` → specifically for autonomous-tuesday (55 min, 80 turns)
- `brand-analytics-weekly/SKILL.md` (30 min, 40 turns)
- `ppc-monthly-review/SKILL.md` (35 min, 50 turns)

**3-phase pattern for each:**
- Phase 1: Fetch all data, save to disk via save_path → COMPACT
- Phase 2: Load from disk, analyze → COMPACT if >60%
- Phase 3: Write outputs, update LESSONS.md, notify Slack

**Why critical:** These skills start with 7K tokens already used (142 MCP schemas), then fetch multi-MB reports. They almost certainly hit 70%+ context mid-analysis, producing degraded second-half output. Strategic compaction means every analysis phase starts at ~10% context.

---

## Phase 7 — Model Routing
**Effort:** 1 hour | **Files:** `automation/config.yaml`, relevant SKILL.md files

### 7A: Automation Config
Move `competitor-price-serp-tracker` to Haiku (data collection, simple comparison):
```yaml
competitor-price-serp-tracker:
  model: claude-haiku-4-5-20251001
```
Monitor for 2 weeks before moving others.

### 7B: Subagent Guidance in SKILL.md Files
Add to skills that spawn Agent subagents:
- Data-fetching subagents → `model="claude-haiku-4-5-20251001"`
- Analysis subagents → `model="claude-sonnet-4-6"`
- Writing subagents → `model="claude-sonnet-4-6"`

Applies to: brand-analytics-weekly, customer-review-analyzer, listing-creator.

**Cost impact:** Haiku is ~20x cheaper than Sonnet per token. Even moving 20% of subagent turns to Haiku represents meaningful savings on 12+ automated runs/week.

---

## Phase 8 — Git Worktrees for Parallel Automation (Deferred)
**Effort:** 3–4 hours | **File:** `automation/skill-runner.py`

Current state: global lockfile prevents parallel skill runs. Monday pipeline (5 skills) runs ~2h15m sequentially.
Target state: each skill gets isolated worktree → true parallelism → ~45 min for full Monday pipeline.

Implementation in skill-runner.py:
- `run_with_worktree(config, skill_name, workspace)` function
- Creates branch `auto/{skill_name}/{date}` in temp path
- Runs skill in isolated worktree
- Merges back, removes worktree and branch
- Per-skill lockfiles instead of global lock

Deferred because: worktree merges need careful output path design (no two skills should write to same file). Validate phases 1-7 first.

---

## Phase 9 — Status Line (Deferred)
**Effort:** 1 hour | **File:** shell config

Show in terminal status bar: model, git branch, session cost, recent handoff.
Most valuable metric: context usage % (not currently accessible from shell).
Community tools with full context %: `ccstatusline`, `claude-code-statusline`, `claudia-statusline`.
Implement after core phases stable.

---

## Expected Total Impact

| Change | Measurable Impact |
|--------|------------------|
| ENABLE_TOOL_SEARCH | 7,100 tokens freed at session start — full context available immediately |
| maxThinkingTokens: 10K | ~68% reduction in thinking budget per response |
| Secret scanner hook | Prevents credential leakage into git-pushed files — 71 API keys protected |
| block-env-read hook | No accidental credential exposure through direct file reads |
| pre-compact hook | Zero information loss across context compaction events |
| session-end hook | LESSONS.md updated on 100% of skill runs (currently ~80%) |
| Context pressure protocol | Long skills maintain quality throughout — no degradation after turn 40 |
| Strategic compaction in long skills | Analysis phases always start at ~10% context, not accumulated 75% |
| /checkpoint + /compact-now | Resume any interrupted interactive session with zero information loss |
| Haiku for simple skills | ~20x cost reduction on those specific automated runs |
| Git worktrees (phase 8) | Monday pipeline: 2h15m → ~45min |

---

## Quick Reference — File Locations

```
.claude/
├── settings.json          ← Phase 1 (ENABLE_TOOL_SEARCH) + Phase 3 (hooks config)
├── hooks/                 ← Phase 3 (new directory)
│   ├── secret-scanner.sh
│   ├── block-env-read.sh
│   ├── bash-safety.sh
│   ├── pre-compact-handoff.sh
│   ├── session-end-reminder.sh
│   └── block-md-creation.sh
└── commands/              ← Phase 4 (new directory)
    ├── checkpoint.md
    ├── wrap-up.md
    ├── context-load.md
    ├── compact-now.md
    └── handoff.md

outputs/research/handoffs/ ← Phase 5 (new directory)
CLAUDE.md                  ← Phase 1+2 (context protocol section added)
automation/config.yaml     ← Phase 7 (model routing)
automation/skill-runner.py ← Phase 8 (worktrees, deferred)
```
