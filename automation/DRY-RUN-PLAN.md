# PPC Agent Autonomous — Dry Run & Validation Plan

**Created:** 2026-03-13
**Purpose:** Systematically test every component before going live. After this plan completes, the autonomous system should be proven end-to-end with no unknowns.

---

## Testing Principles

1. **REPORT ONLY throughout** — no API writes to Amazon until Layer 3 (Apply Actions), and even then only 1-2 low-risk items
2. **Test each layer independently** before combining
3. **Document every failure** — expected failures (we designed for them) vs unexpected failures (bugs)
4. **The user reviews output quality** at every layer before proceeding
5. **Fix-forward** — when a test fails, fix the issue, re-run that specific test, then continue

---

## Layer 1: Monday Pipeline Skills (Individual AUTONOMOUS Mode)

**Goal:** Confirm each of the 5 data collection skills produces correct structured JSON output in autonomous mode.

**How to run:** Manually invoke each skill in an interactive Claude session with "AUTONOMOUS" in the prompt. NOT through the automation runner — we want to see the full output and catch issues in real-time.

---

### Test 1A: Portfolio Summary — AUTONOMOUS

**Prompt:** "Run ppc-portfolio-summary in AUTONOMOUS mode. Save all outputs."

**Pass criteria:**

| Check | Expected | How to verify |
|-------|----------|---------------|
| Autonomous JSON exists | `portfolio-summaries/{date}-autonomous-summary.json` created | Check file exists on disk |
| All 17 portfolios present | `findings.portfolios` array has 17 entries | Count array length |
| Each portfolio has all fields | health, metrics_7d (spend/sales/acos/orders/cvr/cpc), anomalies, campaign_types, structure_complete, vs_weekly | Spot-check 3 portfolios |
| Health distribution sums to 17 | `health_distribution` values add up | Sum the counts |
| Normal brief also saved | `{date}-portfolio-summary.md` exists alongside | Check file |
| Normal snapshot also saved | `{date}-portfolio-snapshot.json` exists | Check file |
| LESSONS.md updated | Run log entry added | Read LESSONS.md |
| No user prompts occurred | Skill ran to completion without asking anything | Observe during run |
| No Slack posted | Slack step skipped | Observe during run |
| Token usage reasonable | <45K tokens | Note from session |

**Edge cases to verify:**
- [ ] Portfolios with null ID (bunny-knitting-loom-kit, stitch-dictionary-all) — should still appear with available data
- [ ] Campaign report PENDING — should fall back to weekly snapshot
- [ ] `errors[]` array populated if any portfolio failed

**Failure responses:**
- Missing portfolios → check portfolio mapping logic, may need to handle null IDs
- Fields missing → the autonomous output schema definition may not match what the skill produces
- Skill asked for user input → the AUTONOMOUS section wasn't followed, check prompt wording

---

### Test 1B: Search Term Harvester — AUTONOMOUS

**Prompt:** "Run ppc-search-term-harvester in AUTONOMOUS mode. Save all outputs."

**Pass criteria:**

| Check | Expected | How to verify |
|-------|----------|---------------|
| Autonomous JSON exists | `search-terms/{date}-autonomous-harvest.json` created | Check file |
| All portfolios with campaigns present | Every portfolio with active campaigns has an entry | Cross-reference with portfolio summary |
| Negate candidates have evidence | Each candidate has `evidence.weeks[]` with 4-week breakdown | Spot-check 5 candidates |
| Safety checks populated | `protected`, `has_organic_rank`, `previously_applied` fields present | Check 3 candidates |
| Promote candidates present | At least some portfolios have promote candidates | Review findings |
| Summary totals match | `summary.total_negate_p1` + `total_negate_p2` = sum across portfolios | Calculate |
| STOPPED before Step 8 | No "Review the lists above" prompt, no API writes | Observe during run |
| SQP skipped | No Brand Analytics calls made | Observe during run |
| Search term report saved to file | Raw report saved (too large for inline) | Check file |
| Brief MD saved | `{date}-search-term-harvest.md` exists | Check file |

**Edge cases to verify:**
- [ ] Search term report stuck PENDING — should save error and produce output with empty findings
- [ ] Portfolio with zero search term activity — should appear with `terms_analyzed: 0`
- [ ] Protected terms correctly excluded from negate candidates
- [ ] Previously applied negatives correctly de-duplicated

**Failure responses:**
- Skill applied negatives → CRITICAL: the AUTONOMOUS section didn't prevent Step 9 from running
- Missing portfolios → check campaign-to-portfolio mapping
- No negate candidates at all → may be correct if data is clean, but verify manually

---

### Test 1C: Bid Recommender — AUTONOMOUS

**Prompt:** "Run ppc-bid-recommender in AUTONOMOUS mode. Save all outputs."

**Pass criteria:**

| Check | Expected | How to verify |
|-------|----------|---------------|
| Autonomous JSON exists | `bids/{date}-autonomous-recommendations.json` created | Check file |
| All portfolios scanned | Every portfolio with enabled campaigns has an entry | Cross-reference |
| Recommendations have placement health | Each rec has `placement_health` classification | Spot-check 5 recs |
| Target CPC calculations present | `target_cpc_calculation` object with target_acos, aov, cvr, target_cpc | Spot-check 3 recs |
| Bid values are irregular | No round numbers like $0.50, $1.00, -30%, -50% | Scan recommendations |
| STOPPED before Step 7 | No "Review the recommendations" prompt, no API writes | Observe |
| Deal mode skipped | No "Which portfolios are running deals?" prompt | Observe |
| Summary breaks down by type | `by_type` has tos_decrease, tos_increase, etc. | Check JSON |
| On-hold campaigns listed | Campaigns with no change needed are in `on_hold` | Check per-portfolio |

**Edge cases to verify:**
- [ ] Campaign with no placement data — should classify as INSUFFICIENT_DATA
- [ ] Campaign below ACoS target — should NOT recommend TOS decrease (Top Performer Protection Rule)
- [ ] Campaign data >3 days old — should pull fresh reports
- [ ] DataDive unavailable — should proceed without rank context, note in data_quality_notes

**Failure responses:**
- Applied bid changes → CRITICAL: autonomous gate failed
- Round bid numbers → operating rules not enforced in autonomous mode
- Missing placement health → Step 4b not running properly

---

### Test 1D: Keyword Rank Optimizer — AUTONOMOUS

**Prompt:** "Run keyword-rank-optimizer in AUTONOMOUS mode. Save all outputs."

**Pass criteria:**

| Check | Expected | How to verify |
|-------|----------|---------------|
| Autonomous JSON exists | `rank-optimizer/{date}-autonomous-analysis.json` | Check file |
| Account-wide scope | Ran for all portfolios, not just one | Check portfolios array |
| 3 output files | autonomous-analysis.json + rank-spend-matrix.json + rank-radar-snapshot.json | Check all 3 |
| Classifications present | Each keyword has classification (WASTING/REDUCE/PROTECT/MAINTAIN/REDIRECT/MONITOR) | Spot-check |
| BA enrichment skipped | No SQP/SCP API calls | Observe |
| Keyword universe fetched | REDIRECT candidates populated from niche keywords | Check findings |
| STOPPED before Step 11 | No routing options presented | Observe |
| Efficiency score computed | `findings.efficiency_score` is a number 0-100 | Check |

**Edge cases to verify:**
- [ ] Portfolio with no rank radar — should appear with `keywords_tracked: 0` and note in data_quality_notes
- [ ] DataDive entirely unavailable — should save error, output what PPC data it has
- [ ] No weekly targeting report — should pull fresh sp_keywords report

**Failure responses:**
- Only analyzed 1 portfolio → scope detection defaulted to portfolio-specific instead of account-wide
- No rank-radar-snapshot saved → critical gap, other skills depend on this

---

### Test 1E: TACoS Optimizer — AUTONOMOUS

**Prompt:** "Run ppc-tacos-optimizer in AUTONOMOUS mode. Save all outputs."

**Pass criteria:**

| Check | Expected | How to verify |
|-------|----------|---------------|
| Autonomous JSON exists | `tacos-optimizer/{date}-autonomous-analysis.json` | Check file |
| All portfolios with ASIN mapping present | Portfolios with hero ASINs have full TACoS data | Cross-reference business.md |
| TACoS grades assigned | Each portfolio has grade A-F | Check |
| Momentum scores computed | Each portfolio has organic_momentum_score 0-100 | Check |
| Profit health classified | PROFITABLE/MARGINAL/BREAK_EVEN/LOSS_MAKING/SUBSIDY per portfolio | Check |
| ASIN flags present | Loss-making ASINs flagged with monthly impact | Check asin_flags array |
| Account summary validates | Account TACoS roughly matches Seller Board PPC marketing report | Compare |
| Scorecard MD saved | `{date}-tacos-scorecard.md` exists | Check file |
| Snapshot JSON saved | `{date}-tacos-snapshot.json` exists | Check file |

**Edge cases to verify:**
- [ ] Portfolio with no ASIN mapping — should be noted as "TACoS approximate"
- [ ] Seller Board data missing for some ASINs — should exclude and note
- [ ] New portfolio with no metric_history — should set target from stage defaults
- [ ] Seller Board report truncated — check if save_path was used (30d reports need it)

**Failure responses:**
- Seller Board unavailable → should save error output, not crash
- TACoS numbers wildly wrong → ASIN-to-portfolio mapping is broken

---

### Layer 1 Completion Criteria

**ALL 5 tests must pass before proceeding to Layer 2.** After all 5 pass:
- [ ] All 5 autonomous JSON files exist on disk
- [ ] No skill made any API writes
- [ ] No skill asked for user input
- [ ] Total time for all 5: note it (expect 15-25 min total)
- [ ] Total tokens for all 5: note it (expect 150-250K total)

---

## Layer 2: Tuesday Agent Session

**Goal:** Confirm the PPC Agent reads Monday's output correctly, cross-references findings, and produces a complete brief + action items JSON.

**Prerequisites:** Layer 1 complete (all 5 autonomous output files on disk).

### Test 2A: Tuesday Full Session

**Prompt:** "Read .claude/skills/ppc-agent/SKILL.md. Run in AUTONOMOUS Tuesday mode. REPORT ONLY — no API writes."

**Pass criteria — Phase 1 (Load):**

| Check | Expected | How to verify |
|-------|----------|---------------|
| Found all 5 Monday files | Agent mentions loading each file | Observe output |
| Noted any missing files | If rank-optimizer or TACoS are missing (biweekly), it notes them | Check brief |
| Loaded agent-state.json | References pending actions, reviews, watchlist | Check brief |
| Loaded daily health | References recent health snapshots | Check brief |
| Staleness check | If Monday data >3 days old, noted in brief | Check brief header |

**Pass criteria — Phase 2 (Validate):**

| Check | Expected | How to verify |
|-------|----------|---------------|
| First run: skipped correctly | "No previous actions to validate" or similar | Check brief Validations section |
| No unnecessary API calls | Only pulls data if there are applied actions to validate | Observe |

**Pass criteria — Phase 3 (Synthesize):**

| Check | Expected | How to verify |
|-------|----------|---------------|
| ALL 17 portfolios assessed | Dashboard table has 17 rows | Count rows in brief |
| 8-point checklist applied | Each portfolio assessment mentions budget, ACoS trend, search term quality, rank, organic, structure, pending, competitors | Read 3 assessments |
| Cross-reference patterns detected | At least 1-2 patterns from the 7 defined patterns | Check "Cross-Portfolio Patterns" section |
| Action items generated | At least some P1-P4 items from the combined analysis | Check Action Items section |
| De-duplication worked | No action items that duplicate existing `all_pending_actions` | Cross-check |
| Evidence standards met | Every P1/P2 action cites 30d+ data | Verify 3 items |
| Bid values irregular | No round numbers in any recommendation | Scan items |
| Priority assignment reasonable | P1 items are genuinely urgent, P4 items are genuinely low-priority | Judgment call |

**Pass criteria — Phase 4 (Output):**

| Check | Expected | How to verify |
|-------|----------|---------------|
| Brief saved to disk FIRST | `sessions/{date}-tuesday-brief.md` exists | Check file |
| Actions JSON saved | `sessions/{date}-tuesday-actions.json` exists | Check file |
| Actions JSON matches schema | Follows action-schema.json structure | Compare |
| Brief has all sections | Executive Summary, Validations, Dashboard, Patterns, Assessments, Action Items, Data Quality, Reasoning Log | Check file |
| Agent-state updated | `autonomous.session_log` has new entry, cadence_tracker updated | Read agent-state.json |
| Notion attempted | Agent tried to create Notion page (may fail if parent doesn't exist — that's OK) | Observe |
| Slack attempted | Agent tried to post notification (may post to test channel or skip) | Observe |

**Quality check (USER JUDGMENT — most important):**
- [ ] Read the full brief. Does the executive summary accurately capture the state of PPC?
- [ ] Do the portfolio assessments match your knowledge of each portfolio?
- [ ] Are the cross-reference patterns insightful or obvious/useless?
- [ ] Are the action items things a PPC worker would actually recommend?
- [ ] Is anything important missing that you'd expect to see?
- [ ] Is the brief too long? Too short? Right level of detail?

**Edge cases to verify:**
- [ ] What if one Monday file is missing? → Brief should note it, continue with available data
- [ ] What if agent-state has 38 pending actions? → Agent should reference them, not ignore them
- [ ] What if all portfolios are GREEN? → Agent should still assess all 17, note "no urgent issues, focus on optimization"

---

### Test 2B: Tuesday Session — Missing Monday Data

**Purpose:** Confirm graceful degradation when Monday pipeline partially failed.

**Setup:** Temporarily rename one or two Monday output files (e.g., rename the bid recommender output).

**Prompt:** Same as 2A.

**Pass criteria:**
- [ ] Agent notes which files are missing
- [ ] Brief still produced with available data
- [ ] Action items that would depend on missing data are downgraded or omitted
- [ ] Data Quality section clearly states what's missing

**After test:** Rename files back.

---

### Test 2C: Brief Quality Iteration

**Purpose:** If the brief from 2A needs improvements, iterate on the instructions.

**Process:**
1. User identifies specific quality issues (e.g., "assessments are too shallow" or "patterns section is empty")
2. We update the relevant section of Step 10 in the PPC Agent SKILL.md
3. Re-run Test 2A
4. Repeat until brief quality meets user expectations

**This may take 2-3 iterations.** That's expected and normal.

---

## Layer 3: Apply Actions (Interactive)

**Goal:** Confirm the "apply items from Tuesday" workflow reads the actions JSON correctly and executes safely.

**Prerequisites:** Layer 2 complete with a valid actions JSON on disk.

### Test 3A: Apply Low-Risk Items

**Choose 1-2 items from Tuesday's action list that are:**
- Low risk (a clear negation with 30d proof, or a small bid adjustment)
- Easily reversible
- On a non-critical portfolio

**Prompt:** "Apply item 1 from Tuesday's session"

**Pass criteria:**

| Check | Expected | How to verify |
|-------|----------|---------------|
| Found actions JSON | Agent loaded the correct file | Observe |
| Presented confirmation card | Shows current value, proposed value, evidence, risk | Observe |
| Waited for approval | Did NOT execute without asking | Observe |
| API call succeeded | Campaign/keyword updated | Verify in Amazon Ads console or via API |
| Actions JSON updated | Item status changed to "applied", applied_date set | Read JSON file |
| Portfolio tracker updated | change_log has new entry | Read tracker JSON |
| Upcoming review created | Validation scheduled for +7 days | Check agent-state |

**Edge cases to verify:**
- [ ] Say "skip" to an item → should mark as skipped, not applied
- [ ] Say "modify" → should present updated values for confirmation
- [ ] Reference items that don't exist ("apply item 99") → graceful error message

### Test 3B: Apply — Stale Data Check

**Purpose:** What if the action item's campaign was modified since Tuesday?

**Setup:** Manually change a bid or budget on a campaign that's in Tuesday's action items (via Amazon Ads console or another session).

**Prompt:** "Apply item {N} from Tuesday's session"

**Pass criteria:**
- [ ] Agent pulls current state before applying
- [ ] Notices the current value doesn't match what Tuesday recorded
- [ ] Warns: "Campaign state changed since Tuesday — current TOS is X% (was Y%). Still apply?"

---

## Layer 4: Friday Session

**Goal:** Confirm the Friday session validates applied actions and detects new anomalies.

**Prerequisites:** Layer 3 complete (at least 1-2 actions applied).

**Timing:** Ideally wait 2-3 days after applying actions. For a structural test, can run same day (validation will be INCONCLUSIVE, which is correct).

### Test 4A: Friday Check Session

**Prompt:** "Read .claude/skills/ppc-agent/SKILL.md. Run in AUTONOMOUS Friday mode. REPORT ONLY."

**Pass criteria:**

| Check | Expected | How to verify |
|-------|----------|---------------|
| Loaded daily health since Tuesday | References health snapshots from Wed/Thu/Fri | Check brief |
| Found Tuesday's actions JSON | References applied items | Check brief |
| Validation attempted | For each applied item, pulled fresh data | Check Validations section |
| Verdict assigned | Each validated item has WORKED/PARTIAL/FAILED/INCONCLUSIVE | Check |
| If same-day: INCONCLUSIVE | Correctly notes "too early to tell" | Check verdicts |
| Brief is shorter than Tuesday | No full 17-portfolio assessment, just anomalies + validations | Compare length |
| New anomalies detected | If daily health showed changes, they're noted | Check |
| Pending items reminder | Notes how many Tuesday items are still pending approval | Check |
| Disk output saved | `{date}-friday-brief.md` and `{date}-friday-actions.json` | Check files |

**Edge cases to verify:**
- [ ] No actions were applied since Tuesday → "No applied actions to validate" + focus on anomaly scan
- [ ] Daily health shows new RED portfolio → flagged prominently
- [ ] Tuesday's actions JSON is missing → graceful error, run anomaly scan only

---

## Layer 5: Notion Integration

**Goal:** Confirm briefs render correctly in Notion.

**Prerequisites:** Any brief file on disk (from Layer 2 or 4).

### Test 5A: Create Parent Page

**Prompt:** "Create a Notion page titled 'PPC Agent Sessions' at the top level. Note the page ID."

**Pass criteria:**
- [ ] Page created
- [ ] Page ID captured and can be stored for future use

### Test 5B: Push Tuesday Brief to Notion

**Prompt:** "Push the Tuesday brief at `outputs/research/ppc-agent/sessions/{date}-tuesday-brief.md` to Notion as a child page under PPC Agent Sessions."

**Pass criteria:**

| Check | Expected | How to verify |
|-------|----------|---------------|
| Child page created | Page title: "PPC Session — {date} (Tuesday)" | Check Notion |
| Content renders | Headers, tables, bullets, bold text all visible | Visual check |
| Tables readable | Portfolio dashboard table renders correctly | Visual check |
| Not truncated | Full brief content present (check last section) | Scroll to bottom |
| Link works | Notion URL is shareable | Click the link |

**Edge cases to verify:**
- [ ] Very long brief (200+ lines) → may need multiple content append calls
- [ ] Complex tables → may need formatting adjustment
- [ ] Notion MCP unavailable → should fail gracefully, disk file still exists

### Test 5C: Push Friday Brief

Same as 5B but with the shorter Friday brief. Confirms both formats render.

---

## Layer 6: Slack Integration

**Goal:** Confirm notification format is correct and goes to the right channel.

### Test 6A: Post Test Notification

**Prompt:** "Post this test message to Slack workspace 'craft', channel 'claude-ppc-updates':
`:robot_face: *PPC Agent Test* — Dry run notification. Ignore this.`"

**Pass criteria:**
- [ ] Message appears in #claude-ppc-updates
- [ ] Formatting renders correctly (emoji, bold)

### Test 6B: Full Notification from Agent Session

During Layer 2 or Layer 4 tests, verify the Slack notification:
- [ ] Posted to correct channel
- [ ] Contains health summary, action count, top concern
- [ ] Has Notion link (or disk path if Notion failed)
- [ ] Under 2000 characters

---

## Layer 7: End-to-End Integration

**Goal:** Run the full week cycle and confirm everything connects.

**This is the final test before going live.**

### Test 7A: Full Week Simulation

**Day 1 (simulate Monday):**
1. Run all 5 AUTONOMOUS skills sequentially (manual trigger)
2. Verify all 5 output files exist
3. Note total time and tokens

**Day 1 (simulate Tuesday):**
4. Run PPC Agent AUTONOMOUS Tuesday mode
5. Review the brief — quality check
6. Verify Notion page created
7. Verify Slack notification sent
8. Apply 2-3 action items interactively

**Day 2-3 (wait for data to accumulate):**
9. Daily health runs normally (already scheduled)

**Day 4 (simulate Friday):**
10. Run PPC Agent AUTONOMOUS Friday mode
11. Review brief — does validation work?
12. Verify Notion page created (Friday)
13. Verify Slack notification

### Test 7A Pass Criteria

| Check | Pass? |
|-------|-------|
| All Monday outputs produced correctly | |
| Tuesday brief covers all 17 portfolios | |
| Tuesday brief quality acceptable to user | |
| Action items are reasonable and well-evidenced | |
| Action items JSON follows schema | |
| Applied actions tracked in agent-state | |
| Friday validates applied actions | |
| Friday detects any new anomalies | |
| Notion pages readable and complete | |
| Slack notifications correct | |
| Agent-state cadence_tracker updated | |
| Agent-state session_log has 2 entries | |
| No data corruption in agent-state or trackers | |
| Total weekly token usage noted | |

### Test 7B: Failure Recovery

**Purpose:** Confirm the system handles a broken Monday gracefully.

**Setup:** Run only 3 of 5 Monday skills (skip search term harvester and rank optimizer).

**Run Tuesday agent session.**

**Pass criteria:**
- [ ] Agent notes 2 missing files
- [ ] Brief still produced with available data
- [ ] Action items that depend on search terms or rank data are absent or downgraded
- [ ] Data Quality section explains what's missing
- [ ] System doesn't crash or produce garbage

---

## Layer 8: Edge Case Scenarios

**Run these individually as needed, not necessarily in order.**

### Test 8A: Empty Findings

**Scenario:** All portfolios are GREEN, no search term waste, no bid recommendations, no rank issues.

**How to test:** Hard to simulate with real data. Instead, verify: does the agent produce a meaningful brief when there's nothing urgent? Does it still assess all 17 portfolios? Does it find optimization opportunities even in healthy portfolios?

### Test 8B: Massive Data

**Scenario:** Search term harvester found 200+ negation candidates.

**How to test:** Check if the agent handles this without running out of context. Does it summarize or enumerate every candidate?

### Test 8C: Conflicting Signals

**Scenario:** Portfolio summary says GREEN but TACoS optimizer says LOSS-MAKING.

**How to test:** Look for this naturally in the data (it may already exist). Check: does the agent catch the contradiction in cross-referencing?

### Test 8D: Previous Session Corruption

**Scenario:** The actions JSON from Tuesday is malformed.

**How to test:** Manually corrupt the JSON (add a syntax error). Run Friday session.

**Pass criteria:** Agent notes the error, skips validation, continues with anomaly scan.

### Test 8E: Agent-State Corruption

**Scenario:** agent-state.json has unexpected fields or missing expected fields.

**How to test:** Remove the `autonomous` section from agent-state.json. Run Tuesday session.

**Pass criteria:** Agent recreates the missing section or handles gracefully.

---

## Execution Timeline

| Day | What | Duration |
|-----|------|----------|
| **Day 1** | Layer 1: Tests 1A-1E (5 individual skills) | 2-3 hours |
| **Day 1** | Fix any Layer 1 failures, re-test | 1-2 hours |
| **Day 2** | Layer 2: Test 2A (Tuesday session) | 1 hour |
| **Day 2** | Test 2B (missing data) + 2C (quality iteration) | 1-2 hours |
| **Day 2** | Layer 5: Tests 5A-5B (Notion) | 30 min |
| **Day 2** | Layer 6: Tests 6A-6B (Slack) | 15 min |
| **Day 3** | Layer 3: Tests 3A-3B (apply actions) | 1 hour |
| **Day 5-6** | Layer 4: Test 4A (Friday session) | 1 hour |
| **Day 7** | Layer 7: Test 7A (end-to-end) | Full day |
| **Day 8** | Layer 7: Test 7B (failure recovery) | 1 hour |
| **Day 8** | Layer 8: Edge cases as needed | 1-2 hours |

**Total estimated testing time: 3-4 days spread over 8 calendar days** (waiting for data accumulation between Tuesday and Friday).

---

## Go-Live Criteria

**ALL of these must be true before activating automated scheduling:**

- [ ] All Layer 1 tests pass (5/5 skills produce correct autonomous output)
- [ ] Layer 2 brief quality approved by user
- [ ] Layer 3 apply workflow works correctly
- [ ] Layer 4 Friday validation works
- [ ] Layer 5 Notion integration works
- [ ] Layer 6 Slack notifications work
- [ ] Layer 7 end-to-end cycle completed successfully
- [ ] No data corruption observed in agent-state or portfolio trackers
- [ ] Token usage per week is acceptable
- [ ] User is confident the brief quality replaces manual PPC review

**After go-live:**
- Week 1: Automated Monday pipeline + manual Tuesday/Friday (user triggers and reviews)
- Week 2: If Week 1 is solid, automate Tuesday. Keep Friday manual.
- Week 3: Automate Friday. Full autonomous cycle.
- Week 4+: Monitor, tune, improve. Begin Phase 2 graduated autonomy planning.
