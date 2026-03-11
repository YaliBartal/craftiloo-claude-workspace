# PPC Decision Rules

> Business rules for all PPC-related skills. Loaded by PPC agent and sub-skills.
> Last updated: 2026-03-11

---

## Hard Rules (Never Break)

1. **Never pause a campaign based on <30 days of data.** A week of zero conversions may be a rough patch, not a dead campaign. Check 30-60 day performance minimum before recommending a pause
2. **Never negate a search term based on <30 days of data.** A term with zero orders in one week may convert in others. Only negate if sustained zero conversions AND clearly irrelevant over the full 30-day window
3. **Never use round bid amounts.** Amazon's auction dynamics may treat predictable patterns differently. Use irregular amounts: -31% not -30%, $0.73 not $0.70, -48% not -50%
4. **Never make TOS/bid recommendations without 30d campaign performance data.** Structural analysis alone is misleading — 900% TOS on a dead campaign is cleanup, not emergency. 311% TOS on a 13.3% ACoS campaign is working perfectly
5. **Always pull placement data before making TOS recommendations.** Campaign-level ACoS hides placement-level efficiency. A campaign at 31.6% ACoS might have TOS at 32.3% (efficient) and "Other" at 81.5% (terrible)

## Analysis Rules

6. **Always verify portfolio stage before analysis.** Launch (rank velocity priority, 60%+ ACoS acceptable) vs Scaling (ACoS priority, 30% target) fundamentally changes every recommendation. Ask if unsure
7. **Always cross-validate aggregated portfolio totals against raw data.** Sum campaign-level spend/sales from the report file and compare to summary.json. Flag any discrepancy >2%
8. **Label exact date ranges on every weekly metric.** Never say "this week" — say "Feb 27-Mar 5" or "Mar 1-7". Calendar-aligned weeks only (not rolling LAST_7_DAYS)
9. **Always present per-campaign 30d metrics before asking for approval.** User requires spend, sales, ACoS, CVR, orders per campaign. Also per-placement breakdown (TOS/ROS/PP) for TOS change decisions

## User Preferences

10. **Don't negate converting terms even if cannibalizing.** When a search term converts profitably in MK broad AND has a dedicated SK campaign, user prefers boosting the SK rather than negating in MK broad. Preserves converting traffic as safety net
11. **Users may reject "pause" recommendations.** Always present pausing as optional, not default. User sees potential where data says otherwise — respect that
12. **PP/ROS modifier changes are "test runs."** Track placement-specific performance at 7-day re-check. If poor, user may want modifiers removed
13. **When user says campaigns were paused "for a reason"** — do NOT use original budgets/TOS. Cut everything 50%+ and use $2/d caps for re-enables

## Structural Patterns (Check Every Deep Dive)

14. **MK broad cannibalization is the #1 structural issue.** Confirmed on 5+ portfolios. When MK broad's effective TOS bid exceeds SK exact bids, MK broad wins auctions and SK campaigns starve. Fix: traffic isolation via negatives in MK broad
15. **Missing PP/ROS modifiers = invisible campaigns.** Likely the #1 cause of "dormant but ENABLED" campaigns. Check in every deep dive
16. **Zero negatives = immediate P1 action.** First thing checked in every portfolio. If zero negatives, flag before any other analysis
17. **PAUSED ad groups are an invisible killer.** Campaign-level checks show ENABLED, budget checks show allocation. Only ad-group-level query reveals the truth
18. **0% budget utilization is a DAILY snapshot, not structural.** Always cross-reference with 30d search term spend data before concluding campaigns are dead
19. **Budget-capped campaigns at good ACoS = easy win.** Always check utilization — highest-impact single changes are usually budget increases on efficient campaigns
20. **Organic rank dominance reduces TOS value.** If product ranks #1 organically, aggressive TOS pushes provide diminishing returns. Focus TOS on keywords where organic rank is weak (#4+)
