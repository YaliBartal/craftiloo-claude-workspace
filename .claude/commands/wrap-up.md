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
