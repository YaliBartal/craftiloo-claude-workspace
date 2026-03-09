---
name: notification-hub
description: Utility skill -- posts Slack summaries and threshold alerts after skill runs
triggers:
  - test notifications
  - notification test
  - check notifications
output_location: N/A
---

# Notification & Alerting Hub

**USE WHEN** triggered directly with "test notifications" to verify channel connectivity, OR called by other skills at the end of their run via a recipe reference.

**This is a UTILITY skill.** It is not meant to run standalone analysis. Other skills call specific recipes from this file to post Slack summaries and threshold alerts after each run.

---

## BEFORE YOU START -- Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/notification-hub/LESSONS.md`
2. Check **Known Issues** -- plan around these
3. Check **Repeat Errors** -- if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## Configuration

Read `context/notification-config.json` for:
- **Channel routing** -- which Slack channel each recipe posts to
- **Alert thresholds** -- when to escalate to `#claude-alerts`
- **Workspace** -- which Slack workspace to use (default: `craft`)
- **Enabled flag** -- if `false`, skip all notifications silently

If the config file doesn't exist or `enabled` is `false`, skip notifications and log "Notifications disabled or config missing" in the calling skill's run log.

---

## Channel Architecture

| Channel | Purpose | Fed By |
|---------|---------|--------|
| `#claude-morning-brief` | Daily pulse -- market intel + PPC health combined | daily-market-intel, ppc-daily-health, daily-prep |
| `#claude-ppc-updates` | All PPC execution results | ppc-bid-recommender, ppc-search-term-harvester, ppc-portfolio-action-plan, ppc-campaign-creator, keyword-rank-optimizer, ppc-monthly-review, ppc-tacos-optimizer, weekly-ppc-analysis, negative-keyword-generator, ppc-portfolio-summary |
| `#claude-product-updates` | Listings, images, reviews, niche research, brand analytics | listing-creator, listing-optimizer, listing-ab-analyzer, image-planner, product-listing-development, customer-review-analyzer, niche-category-analysis, brand-analytics-weekly |
| `#claude-competitor-watch` | Competitive intelligence | competitor-price-serp-tracker |
| `#claude-alerts` | Cross-cutting threshold breaches from ANY skill | Any skill that triggers a threshold |

---

## Slack Formatting Rules

**All recipes MUST follow these rules:**

- **Max 2000 chars** per message (readability cap -- Slack limit is 4000 but long messages get ignored)
- **Status emojis** as visual anchors: :large_green_circle: :large_yellow_circle: :red_circle: :fire: :white_check_mark: :warning:
- **Bold section headers** with `*text*` (Slack markdown)
- **Bullets** for lists -- never tables (they render poorly in Slack)
- **Thread replies** for detail overflow -- main message = summary, thread = per-item detail
- If message exceeds 2000 chars: post summary in main message, details as thread reply
- Use `\n` for line breaks, not markdown paragraph breaks

---

## Alert Escalation Rules

Any recipe can escalate to `#claude-alerts` when thresholds from `notification-config.json` are breached:

| Condition | Threshold Key | Default |
|-----------|--------------|---------|
| RED portfolio status | (always) | Any RED |
| ACoS > red flag (Scaling) | `ppc_acos_red_scaling` | 50% |
| ACoS > red flag (Launch) | `ppc_acos_red_launch` | 80% |
| Stock OOS or critical | `stock_days_critical` | <3 days |
| Revenue drop WoW | `revenue_drop_wow_pct` | >30% |
| Competitor price undercut | `competitor_price_drop_pct` | >20% |
| Hero keyword rank drop | `hero_rank_drop_positions` | >5 positions |
| Listing score critical | `listing_score_critical` | <30/100 |
| Quality flag (CRITICAL/HIGH) | (always) | Any CRITICAL/HIGH |
| Niche GO verdict | `niche_go_score_min` | Score >32 |
| Skill overdue | `overdue_days_alert` | >3 days |
| Listing push rejection | (always) | Any rejection |

**Alert format for `#claude-alerts`:**
```
:warning: *ALERT* -- {Source Skill}

{One-line description of what triggered the alert}
{Recommended action}
```

---

## Error Handling

- **Slack MCP unavailable** -> skip notification, log "Slack notification skipped -- MCP unavailable" in calling skill's LESSONS.md run log
- **Channel doesn't exist** -> log "Channel #{name} not found -- create it or update notification-config.json", don't fail parent skill
- **Message too long** -> truncate with "... _(see full report in outputs/)_"
- **Rate limited** -> log warning, don't retry, don't fail parent skill
- **NEVER let a notification failure cause the parent skill to fail**

---

## Test Mode

When triggered directly with "test notifications" or "notification test":

1. Read `context/notification-config.json`
2. For each configured channel, attempt: `post_message(workspace, channel, ":white_check_mark: *Notification Hub Test* -- Channel connected successfully.")`
3. Report success/failure per channel to the user
4. If any channel fails, show the error and suggest fixes

---

## Notification Recipes

---

### Recipe: daily-market-intel

**Channel:** `#claude-morning-brief`
**Input:** Read today's market intel brief + snapshot from `outputs/research/market-intel/`
**Format:**
```
*Market Intel* -- {YYYY-MM-DD}

*Revenue:* ${X} (7d) | *Profit:* ${X} | *Margin:* {X}%
*Ad Spend:* ${X} | *TACoS:* {X}% | *Organic:* {X}%

*Top Movers:*
:fire: {Product} BSR {X} ({delta}%) -- {context}
:chart_with_downwards_trend: {Product} BSR {X} ({delta}%) -- {context}

*Stock Alerts:*
:red_circle: {ASIN} OOS -- {impact}
:warning: {Product} <{N} days remaining
```
**Alert escalation:** Stock OOS -> `#claude-alerts`. Revenue drop >{revenue_drop_wow_pct}% WoW -> `#claude-alerts`.

---

### Recipe: ppc-daily-health

**Channel:** `#claude-morning-brief` (posts as thread reply to market-intel if both run same day, otherwise standalone)
**Input:** Read today's `*-health-snapshot.json` from `outputs/research/ppc-agent/daily-health/`
**Thread logic:** Check if a market-intel message was posted to `#claude-morning-brief` today. If yes, reply in that thread. If no, post standalone.
**Format:**
```
*PPC Health* -- {YYYY-MM-DD}

*Account:* {N} campaigns | ${X}/day budget | {+/-N} top-10 net

:large_green_circle: GREEN ({N}): {portfolio names}
:large_yellow_circle: YELLOW ({N}): {portfolio names}
:red_circle: RED ({N}): {portfolio name} ({reason}), ...

*:fire: Headline:* {top headline from brief}

*Due today:*
- {action 1}
- {action 2}
```
**Alert escalation:** Any RED portfolio -> `#claude-alerts` with portfolio name + issue + recommended action.

---

### Recipe: daily-prep

**Channel:** `#claude-morning-brief` (only if stock alerts found)
**Input:** Read daily-prep output
**Format:** Only post if stock alerts exist -- short stock alert message. Don't post full daily prep (it's interactive, not summary-worthy).
**Alert escalation:** OOS products -> `#claude-alerts`.

---

### Recipe: competitor-price-serp-tracker

**Channel:** `#claude-competitor-watch`
**Input:** Read weekly brief + snapshot from `outputs/research/competitor-tracker/`
**Format:**
```
*Competitor Weekly* -- {YYYY-MM-DD}

*Tracked:* {N} competitors | {N} keywords | {N} categories

:red_circle: HIGH:
- {Brand} undercut by {X}% on {category}
- Deal badge detected: {ASIN}

:large_yellow_circle: MEDIUM:
- {N} new ASINs in top 10
- {Brand} +{N} reviews this week

*Price gap:* Our avg ${X} vs competitor avg ${X}
*SERP:* Our avg pos {X} vs competitor avg {X}
```
**Alert escalation:** HIGH severity alerts -> `#claude-alerts`.

---

### Recipe: listing-creator

**Channel:** `#claude-product-updates`
**Input:** Read listing brief from `outputs/research/listings/`
**Format:**
```
:white_check_mark: *New Listing Ready* -- {Product Name}

*Title:* {first 80 chars}...
*Keywords:* {count} targeted | *Competitors analyzed:* {count}
*Q&A coverage:* {X}/{Y} customer questions addressed

:memo: Full listing -> Notion: {page title}
```

---

### Recipe: listing-optimizer

**Channel:** `#claude-product-updates`
**Input:** Read listing audit brief from `outputs/research/listing-optimizer/`
**Format:**
```
:bar_chart: *Listing Audit* -- {Product Name}

*Ranking Juice:* Title {X}/100 | Bullets {X}/100 | Desc {X}/100
*vs Competitor Avg:* Title {X}/100 | Bullets {X}/100
*Gap:* {biggest gap area} ({our score} vs {competitor avg})

*Quick wins:*
- {Top recommendation}
- {Second recommendation}

{If pushed:} :white_check_mark: Pushed to Amazon -- verify in {X} days
```
**Alert escalation:** Push rejection -> `#claude-alerts`. Score <{listing_score_critical}/100 on any dimension -> `#claude-alerts`.

---

### Recipe: image-planner

**Channel:** `#claude-product-updates`
**Input:** Read image plan brief from `outputs/research/image-plans/`
**Format:**
```
:frame_with_picture: *Image Plan Ready* -- {Product Name}

*Images:* 7 planned | *Copy options:* {N} alternatives per image
*Competitive gaps exploited:* {top 1-2 gaps}
*Designer brief:* Ready (copy table format)

:memo: Full plan -> {output file path}
```

---

### Recipe: product-listing-development

**Channel:** `#claude-product-updates`
**Input:** Read orchestrator output from `outputs/research/product-launch/`
**Format:**
```
:rocket: *Product Launch Package Complete* -- {Product Name}

:white_check_mark: Listing: Title + 5 bullets + backend keywords
:white_check_mark: Image Plan: 7 images with copy + designer brief
:white_check_mark: Research: {N} competitors + {N} keywords + {N} reviews analyzed

:memo: Everything -> Notion: {page title}
```

---

### Recipe: customer-review-analyzer

**Channel:** `#claude-product-updates`
**Input:** Read review analysis brief + snapshot from `outputs/research/review-analysis/`
**Format:**
```
:speech_balloon: *Review Analysis* -- {Product Name}

*Reviews analyzed:* {N} | *Satisfaction:* {X}%
*Rating:* {X} stars ({trend vs previous if exists})

*Quality flags:*
:red_circle: {CRITICAL/HIGH issue + frequency}
:large_yellow_circle: {MEDIUM issue + frequency}

*Competitive insight:*
- {Top competitive finding}

*Listing language found:*
- "{exact customer phrase}" (mentioned {N}x)
```
**Alert escalation:** CRITICAL/HIGH quality flags -> `#claude-alerts`.

---

### Recipe: niche-category-analysis

**Channel:** `#claude-product-updates`
**Input:** Read niche analysis brief from `outputs/research/niche-analysis/`
**Format:**
```
:mag: *Niche Analysis* -- {Niche Name}

*Verdict:* {GO / CONDITIONAL GO / NO-GO} ({score}/40)
*Market:* ${X}K/month | {N} competitors | {concentration}
*Price opportunity:* {gap description}
*Top differentiator:* {strongest angle}

{If GO:} :large_green_circle: Recommended positioning: {1-line summary}
{If NO-GO:} :red_circle: Pass -- {1-line reason}
```
**Alert escalation:** GO verdict with score >{niche_go_score_min} -> `#claude-alerts` (opportunity alert).

---

### Recipe: weekly-ppc-analysis

**Channel:** `#claude-ppc-updates`
**Input:** Read weekly analysis summary from `outputs/research/ppc-weekly/`
**Format:**
```
:bar_chart: *Weekly PPC Report* -- {date range}

*Spend:* ${X} ({WoW trend}) | *Sales:* ${X} ({WoW trend})
*ACoS:* {X}% ({WoW delta}) | *ROAS:* {X}

*Top campaigns:* {top 3 by spend with ACoS}
*Worst campaigns:* {bottom 3 by ACoS}
*Search terms:* {N} new converting | {N} flagged for negation
```

---

### Recipe: ppc-bid-recommender

**Channel:** `#claude-ppc-updates`
**Input:** Read bid recommendation output
**Format:**
```
:dart: *Bid Recommendations* -- {Portfolio Name}

*Changes proposed:* {N} keywords
- Increase: {N} ({reason summary})
- Decrease: {N} ({reason summary})
- Pause: {N}

{If applied:} :white_check_mark: Applied via API
{If pending:} :hourglass_flowing_sand: Awaiting approval
```

---

### Recipe: ppc-search-term-harvester

**Channel:** `#claude-ppc-updates`
**Input:** Read harvest output
**Format:**
```
:ear_of_rice: *Search Term Harvest* -- {Portfolio Name}

*Processed:* {N} search terms
- NEGATE: {N} terms ({top 2 examples})
- PROMOTE: {N} terms ({top 2 examples})
- DISCOVER: {N} terms ({top 2 examples})

{If applied:} :white_check_mark: Negatives applied, promotions queued
```

---

### Recipe: ppc-portfolio-action-plan

**Channel:** `#claude-ppc-updates`
**Input:** Read action plan output
**Format:**
```
:clipboard: *Portfolio Action Plan* -- {Portfolio Name}

*Health:* {score}/10 | *Stage:* {stage} | *ACoS:* {X}%

*Actions ({N} total):*
:red_circle: P1: {top P1 action}
:large_yellow_circle: P2: {top P2 action}
:large_green_circle: P3: {count} monitoring items

{If executed:} :white_check_mark: {N} actions applied | {N} pending
*Next review:* {date}
```

---

### Recipe: ppc-campaign-creator

**Channel:** `#claude-ppc-updates`
**Input:** Read campaign creation output
**Format:**
```
:new: *Campaigns Created* -- {Portfolio Name}

*New campaigns:* {N} | *Ad groups:* {N} | *Keywords:* {N}
- {Campaign 1 name} (${budget}/day)
- {Campaign 2 name} (${budget}/day)

*Total new daily budget:* ${X}
*Review gate:* {date} (7-day check)
```

---

### Recipe: ppc-portfolio-summary

**Channel:** `#claude-ppc-updates`
**Input:** Read portfolio summary output
**Format:**
```
:bar_chart: *Portfolio Summary* -- {Portfolio Name}

*Stage:* {stage} | *Health:* {classification}
*Campaigns:* {N} enabled | *Budget:* ${X}/day
*ACoS:* {X}% | *Structure:* {audit findings summary}

{If issues found:} :warning: {top structural issue}
```

---

### Recipe: keyword-rank-optimizer

**Channel:** `#claude-ppc-updates`
**Input:** Read rank optimizer brief from `outputs/research/ppc-agent/rank-optimizer/`
**Format:**
```
:chart_with_upwards_trend: *Rank vs Spend Optimizer*

*Efficiency score:* {X}% ({delta vs last run})

:money_with_wings: *Wasting:* ${X}/week on {N} keywords (zero rank movement)
:moneybag: *Reducible:* ${X}/week on {N} keywords (already top 10)
:shield: *Protect:* {N} hero keywords dropping -- bid defense needed
:dart: *Redirect:* {N} untargeted keywords ({total SV}/month)
```
**Alert escalation:** Protect alerts (hero keywords dropping >{hero_rank_drop_positions} positions) -> `#claude-alerts`.

---

### Recipe: ppc-monthly-review

**Channel:** `#claude-ppc-updates`
**Input:** Read monthly review output
**Format:**
```
:calendar: *Monthly PPC Review* -- {Month}

*Total spend:* ${X} | *Total sales:* ${X} | *ACoS:* {X}%
*vs Last Month:* Spend {delta} | Sales {delta} | ACoS {delta}

*Stage transitions:* {any portfolio stage changes}
*Budget reallocation:* {summary of shifts}
*Top 3 wins:* {brief list}
*Top 3 concerns:* {brief list}
```

---

### Recipe: ppc-tacos-optimizer

**Channel:** `#claude-ppc-updates`
**Input:** Read TACoS optimizer output
**Format:**
```
:bar_chart: *TACoS Scorecard*

*Account TACoS:* {X}% (grade: {A/B/C/D/F})
*Organic momentum:* {X}% of revenue

*By portfolio:*
:large_green_circle: {Portfolio}: TACoS {X}% (target {X}%)
:red_circle: {Portfolio}: TACoS {X}% -- profit concern

*Profit reality:* {1-line summary}
```

---

### Recipe: ppc-agent-cadence

**Channel:** `#claude-alerts` (only if items >{overdue_days_alert} days overdue)
**Input:** Read `agent-state.json` overdue items
**Format:**
```
:alarm_clock: *Overdue Skills*

- Weekly PPC Analysis: {N} days overdue
- Search Term Harvest: {N} days overdue
- {etc.}

Run these to keep data fresh.
```

---

### Recipe: negative-keyword-generator

**Channel:** `#claude-ppc-updates`
**Input:** Read negative keyword output
**Format:**
```
:no_entry_sign: *Negative Keywords Generated* -- {scope}

*Total negatives:* {N} | *Categories:* {N}
- Irrelevant terms: {N}
- Cross-product cannibalization: {N}
- Brand terms: {N}

{If applied:} :white_check_mark: Applied to {N} campaigns
```

---

### Recipe: listing-ab-analyzer

**Channel:** `#claude-product-updates`
**Input:** Read AB analysis from `outputs/research/listing-optimizer/ab-tests/`
**Format:**
```
:test_tube: *Listing Change Analysis* -- {Product Name}

*Changed:* {what} on {date}
*Verdict:* {POSITIVE/NEGATIVE/NEUTRAL/INCONCLUSIVE}
*Revenue impact:* +/-${X}/month
*Confidence:* {High/Medium/Low}

*Key metrics:*
- CTR: {before}% -> {after}% ({delta})
- Cart Rate: {before}% -> {after}% ({delta})
- Purchases: {before}/wk -> {after}/wk ({delta}%)

*Recommendation:* {KEEP/REVERT/ITERATE/MONITOR}
```
**Alert escalation:** NEGATIVE verdict with High confidence -> `#claude-alerts`. Monthly revenue impact > -$100/month -> `#claude-alerts`.

---

### Recipe: brand-analytics-weekly

**Channel:** `#claude-product-updates`
**Input:** Read BA weekly digest + snapshot from `outputs/research/brand-analytics/`
**Format:**
```
:mag: *Brand Analytics Weekly* -- {date range}

*Organic search:* {impressions_wow_pct}% impressions | {clicks_wow_pct}% clicks | {purchases_wow_pct}% purchases

*Click share:*
:chart_with_upwards_trend: Gaining: {N} keywords ({top keyword +X pts})
:chart_with_downwards_trend: Losing: {N} keywords ({top keyword -X pts})

*Alerts:*
- Funnel problems: {N} keywords
- Competitor movements: {N} keywords
- New opportunities: {N} keywords

*Loyalty:* {top insight from repeat purchase data}

:memo: Full digest -> outputs/research/brand-analytics/briefs/
```
**Alert escalation:** Hero keyword losing >5% click share -> `#claude-alerts`. Competitor gaining >10% click share on hero keyword -> `#claude-alerts`. Organic purchases dropping >20% WoW -> `#claude-alerts`.

---

## AFTER EVERY RUN -- Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/notification-hub/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Result:** Success / Partial / Failed
**Calling skill:** {which skill triggered this}

**What happened:**
- (Channels posted to, alerts escalated)

**What didn't work:**
- (Any channel failures, formatting issues)

**Lesson learned:**
- (What to do differently)
```

### 2. Update Issue Tracking

| Situation | Action |
|-----------|--------|
| New problem | Add to **Known Issues** |
| Known Issue happened again | Move to **Repeat Errors**, increment count, **tell the user** |
| Fixed a Known Issue | Move to **Resolved Issues** |
