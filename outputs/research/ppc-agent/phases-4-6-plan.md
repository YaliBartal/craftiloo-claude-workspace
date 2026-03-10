# PPC Agent — Phases 4-6 Implementation Plan

**Created:** 2026-03-10
**Status:** NOT IMPLEMENTED — saved for future sessions
**Prerequisites:** Phases 1-3 must be working in production first

---

## Phase 4: Competitive Response Integration (Effort: Medium, ~3 hours)

### Problem
The PPC agent operates in a vacuum — it doesn't know what competitors are doing. When a competitor drops price or launches aggressive PPC, we see the symptoms (ACoS spike, rank drop) but not the cause. The Competitor Price SERP Tracker skill exists but its data never flows into PPC decisions.

### Solution
Connect competitor intelligence to PPC decision-making:

1. **Data bridge from competitor-price-serp-tracker:** After each competitor tracking run, write a `competitor_alerts` section to the portfolio tracker with:
   - Price drops >10% on competing ASINs
   - New competitors entering page 1 for our hero keywords
   - BSR improvements on competitors (gaining sales velocity)

2. **PPC response rules in the chaining protocol (Step 4):**
   - Competitor price drop → flag in Daily Health → recommend defensive bid increase or listing price review
   - New competitor on page 1 → flag in Rank Optimizer → recommend TOS boost for affected keywords
   - Competitor BSR improving → flag in TACoS Optimizer → recommend evaluating whether to compete or pivot

3. **Integration points:**
   - Add `competitor_alerts` field to portfolio tracker schema
   - Add competitor check to Optimization Scan as check #8
   - Add chaining rule: competitor-price-serp-tracker → alerts found → auto-run Daily Health with context

### Files to modify
- `.claude/skills/ppc-agent/SKILL.md` — new chaining rules, scan check #8
- `.claude/skills/competitor-price-serp-tracker/SKILL.md` — add portfolio tracker write step
- Portfolio tracker schema — add `competitor_alerts` section
- Agent-state.json — add `last_competitor_check` timestamp

### Risks
- Competitor data may be stale (weekly cadence) — don't overreact to week-old data
- Not all portfolios have competitor tracking set up — graceful degradation needed
- Over-reaction to competitor moves can waste budget — always present as advisory, not auto-execute

---

## Phase 5: Budget Intelligence Layer (Effort: Medium-High, ~4 hours)

### Problem
Budget decisions are made locally (per-campaign) without portfolio-level or account-level context. The agent might increase budget on Campaign A without realizing Campaign B in the same portfolio has excess budget. Account-level daily spend cap isn't tracked, so there's no "budget headroom" awareness.

### Solution
Add cross-campaign and cross-portfolio budget intelligence:

1. **Portfolio budget dashboard (added to Portfolio Summary):**
   - Total portfolio daily budget vs actual spend (utilization %)
   - Campaign-level budget utilization heat map
   - Identify budget-starved campaigns (>90% utilization, losing impression share)
   - Identify over-allocated campaigns (<30% utilization, budget sitting idle)
   - Budget redistribution recommendations

2. **Account-level budget awareness:**
   - Track total account daily spend across all portfolios
   - Warn when total account spend approaches any known caps
   - Cross-portfolio rebalancing: if Portfolio A is under-spending and Portfolio B is budget-starved, recommend reallocation

3. **Budget forecasting (simple):**
   - Given current daily spend trajectory, forecast monthly PPC spend
   - Alert if forecast exceeds historical monthly averages by >20%
   - Tie to Seller Board profit data: "At current spend, projected monthly profit is X"

4. **Integration with campaign lifecycle:**
   - New campaigns in RAMPING phase should have budget monitored more closely
   - GRADUATED campaigns with consistently <50% utilization → recommend budget decrease

### Files to modify
- `.claude/skills/ppc-agent/SKILL.md` — budget intelligence in Smart Catch-Up, new scan check
- `.claude/skills/ppc-portfolio-summary/SKILL.md` — add budget dashboard section
- `.claude/skills/ppc-daily-health/SKILL.md` — add account-level spend monitoring
- Agent-state.json — add `account_budget` section with spend tracking

### Risks
- Budget data via `get_sp_campaign_budget_usage` is per-campaign — aggregation needed
- No Amazon API for account-level budget caps — must rely on user-set thresholds
- Budget redistribution across portfolios requires strategic judgment — always advisory

---

## Phase 6: Pattern Learning Engine (Effort: High, ~6 hours)

### Problem
The agent accumulates data (validation_history, metric_history, change_logs) but never analyzes it for patterns. Over weeks/months of operation, there should be enough data to answer: "What types of changes tend to work for this account?" and "Are there recurring patterns we can predict?"

### Solution
Build a lightweight pattern analysis layer that runs periodically (monthly or on-demand):

1. **Validation pattern analysis:**
   - Aggregate all `validation_history` across portfolios
   - Calculate success rates by change type (bid changes, TOS adjustments, negations, campaign creates)
   - Identify: "Bid decreases >30% tend to FAIL (0/5 success). Bid decreases 10-20% tend to WORK (8/12 success)."
   - Feed success rate data into bid recommender and portfolio action plan

2. **Seasonal pattern detection:**
   - Analyze `metric_history` across 90+ days of data
   - Detect recurring patterns: "ACoS always rises 2pp in first week of month (budget resets)"
   - Detect day-of-week patterns: "Weekend CPC is 15% lower — recommend higher weekend bids"
   - Flag counter-seasonal moves: "ACoS is rising but this is normal for March based on last year"

3. **Portfolio response profiles:**
   - Each portfolio develops a "personality" over time
   - "Needlepoint responds well to TOS increases but poorly to bid cuts"
   - "Biggie Beads is price-sensitive — bid changes have outsized impact"
   - Store as `response_profile` in portfolio tracker

4. **Reporting:**
   - Monthly pattern report showing: top 5 insights, change type success rates, seasonal flags
   - Integrated into Monthly Review skill output

### Files to modify
- `.claude/skills/ppc-agent/SKILL.md` — pattern analysis trigger in monthly review chain
- `.claude/skills/ppc-monthly-review/SKILL.md` — add pattern analysis section
- Portfolio tracker schema — add `response_profile` section
- New analysis logic in Monthly Review to aggregate cross-portfolio data

### Risks
- Insufficient data in early months — need minimum 30+ validated changes before patterns are meaningful
- Correlation ≠ causation — external factors (listing changes, seasonality, competitor moves) confound attribution
- Over-fitting: small sample sizes can produce false patterns — enforce minimum N thresholds
- Context window cost: reading all validation histories for 17 portfolios is expensive — need summarization strategy

### Prerequisites
- Phase 1 (Action Validator) must have been running for 4+ weeks with validated changes
- At least 50+ total validated changes across portfolios for statistical relevance
- Monthly Review skill must be functional and run at least once

---

## Implementation Order

**Phase 4 → Phase 5 → Phase 6** (each builds on the previous)

- Phase 4 can start once Phases 1-3 are validated in production (run the agent 2-3 times with the new protocols)
- Phase 5 can start independently of Phase 4 but benefits from competitor context
- Phase 6 requires minimum 4 weeks of validation data — earliest start: mid-April 2026

## Estimated Timeline
- Phase 4: 1 session (3 hours)
- Phase 5: 1-2 sessions (4 hours)
- Phase 6: 2 sessions (6 hours)
- Total: ~13 hours across 4-5 sessions
