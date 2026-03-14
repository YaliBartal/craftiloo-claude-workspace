# Claude Code Best Practices — Research Notes
**Date:** 2026-03-14
**Purpose:** Summary of findings from top Claude Code community repos, mapped to Craftiloo workspace gaps

---

## Repos Analyzed

| Repo | Stars (approx) | Focus |
|------|---------------|-------|
| `affaan-m/everything-claude-code` | ~50K | Production-grade agent harness, hooks, memory, security |
| `hesreallyhim/awesome-claude-code` | High | Curated list of skills, hooks, tools, orchestrators |
| `ykdojo/claude-code-tips` | Moderate | 45 practical tips (voice, context, git, automation) |
| `rohitg00/awesome-claude-code-toolkit` | Growing | 135 agents, 121 plugins, 19 hooks, 42 commands |
| `FlorianBruniaux/claude-code-ultimate-guide` | Growing | Deep guide with security, methodologies, 204 templates |

---

## Critical Universal Findings

### 1. Context Pressure is the #1 Silent Killer of Output Quality
- **70%** context: precision degrades noticeably
- **85%** context: hallucinations increase
- **90%+**: erratic behavior
- Most users never know they've crossed these thresholds. Claude degrades silently.
- Fix: explicit compaction at logical breakpoints, not at auto-compaction (95%)

### 2. Every Serious Workspace Has Hooks — We Have Zero
- Hooks are lifecycle-event scripts (PreToolUse, PostToolUse, PreCompact, Stop)
- They run automatically with zero prompting needed
- Core uses: secret scanning, safety blocks, context reminders, pre-compact state saves
- Zero-hook workspaces have no automated safety net or lifecycle discipline

### 3. MCP Tool Schemas Consume Upfront Context
- Each MCP tool schema = ~50 tokens loaded into EVERY session turn
- We have 142 MCP tools across 9 servers
- 142 × 50 = 7,100 tokens burned before Claude does anything
- Fix: `ENABLE_TOOL_SEARCH=true` lazy-loads tool schemas on demand

### 4. Thinking Token Budget is 3x Over-Allocated by Default
- Default: 31,999 thinking tokens per response
- For data analysis / report writing: 10,000 is sufficient
- 68% token budget reduction with minimal quality impact for our use cases

### 5. Model Routing is Never Done Uniformly in Mature Workspaces
- Haiku: data fetching, simple verification (20x cheaper than Sonnet)
- Sonnet: analysis, synthesis, writing (current uniform choice)
- Opus: complex architectural reasoning (rarely needed in our domain)

---

## Key Concepts Worth Understanding

### Strategic Compaction (everything-claude-code)
Manual `/compact` at logical phase boundaries beats auto-compaction:
- Auto-compact fires at 95% (too late, mid-task)
- Manual compact between "data fetch" and "analysis" phases = full context for analysis
- Pattern: fetch → save to disk → compact → analyze saved files → compact → write output

### Iterative Retrieval Pattern (everything-claude-code)
Start context-lean, pull only what's needed, repeat. Prevents context ballooning.
Already partially how our Agent subagents work — could be made more explicit in skill design.

### Handoff Documents
Before any `/compact` or `/clear`, write a structured state file:
- Task status, files on disk, key findings, pending work, resume instructions
- The next session reads this instead of starting blind
- A `PreCompact` hook can automate creating the file shell

### Pre-Compact Hook Pattern
A hook that fires before auto-compaction:
1. Creates a handoff file structure
2. Tells Claude to populate it with current state
3. After compaction, Claude reads the handoff to continue
= Zero information loss across context boundaries

### The Ralph Pattern (autonomous completion)
Outer loop that runs a skill until marked complete or limit reached.
Our n8n automation approximates this. The improvement: circuit breaker (intelligent exit if stuck).

### Session-Start Context Loading
A hook that fires at session start to auto-load relevant context files.
We currently load context manually per skill — a session-start hook could do this automatically.

---

## What We're Already Doing Right (ahead of most users)

| Practice | Status |
|----------|--------|
| Custom skills system (28 skills) | ✅ Advanced |
| Living context files (api-patterns, ppc-rules, tooling-workarounds) | ✅ Advanced |
| LESSONS.md continuous improvement | ✅ Advanced |
| Run-log archiving | ✅ Advanced |
| n8n automation with scheduled skills | ✅ Advanced |
| Safety rules for money/live changes | ✅ Correct |
| 9 custom MCP servers | ✅ Advanced |
| Structured output organization | ✅ Good |

---

## Gaps Mapped to Implementation Phases

| Gap | Phase | Impact |
|-----|-------|--------|
| No hooks at all | Phase 3 | Critical — security + discipline |
| No context pressure protocol | Phase 2 | High — quality degradation |
| 142 tools loaded upfront | Phase 1 | High — 7K tokens freed/session |
| Thinking budget 3x too high | Phase 1 | Medium — cost reduction |
| No slash commands | Phase 4 | Medium — workflow discipline |
| No handoff system | Phase 5 | Medium — context continuity |
| No compact strategy in long skills | Phase 6 | High — analysis quality |
| Uniform Sonnet for all | Phase 7 | Medium — cost savings |
| No parallel automation (worktrees) | Phase 8 | Medium — speed |

---

## What NOT to Adopt (irrelevant to e-commerce ops domain)

- Language-specific agents (TypeScript, Python, Go, Rust)
- Code quality hooks (ESLint, Prettier, TypeScript type checking)
- TDD/BDD development workflows
- Docker/Kubernetes tooling agents
- CI/CD pipeline plugins
- Frontend optimization tools
- AgentShield security scanner (overkill for our context)
- Full instinct-based learning system (our LESSONS.md covers this adequately)

---

## Reference Links

- Implementation plan: `outputs/research/system-planning/2026-03-14-workspace-upgrade-implementation-plan.md`
- Key repos: everything-claude-code, awesome-claude-code (hesreallyhim), claude-code-tips (ykdojo)
