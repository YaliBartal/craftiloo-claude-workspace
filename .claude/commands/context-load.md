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
