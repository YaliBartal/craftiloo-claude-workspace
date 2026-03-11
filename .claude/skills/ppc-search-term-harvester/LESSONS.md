# Search Term Harvester — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`, `context/ppc-rules.md`, `context/tooling-workarounds.md`
> Run log archive → `outputs/research/ppc-agent/run-logs/`

## Skill-Specific Lessons

1. 30-day data is actually superior for harvesting (30-day negation rule requires it) — request 30d directly, or reuse cached data if <3 days old
2. Python batch processing is essential at scale — 13,503 rows cannot be analyzed inline. classify_terms.py + safety_check.py pipeline works
3. Protected term safety net is critical — saved 22 terms / $662 from false negation in a single run
4. Most waste is in Catch All Auto campaigns — consider dedicated catch-all cleanup pass
5. Campaign-level negatives batch well — 72 entries in single API call, 0 errors (no need to split under 100)
6. Always verify existing keyword coverage before creating new PROMOTE campaigns — 75% of candidates were already targeted
7. When portfolio ACoS is terrible but terms are all legitimate/protected, root cause is external (stock, Buy Box, listing) — don't negate good keywords

## Known Issues

_None skill-specific — cross-skill issues in context/ files._

## Repeat Errors

### 1. Amazon Ads API report stuck PENDING (x6)
Delays harvest by 3+ min. Workaround: use cached 30d data. See `context/tooling-workarounds.md`.

## Resolved Issues

_None yet._

## Recent Runs (last 3)

### Run: 2026-03-05 (Full account harvest)
**Result:** Success — 10,193 unique terms, 19 negatives applied (72 campaign-level entries), 0 errors
**Key outcome:** ~$82/month savings. 22 protected terms saved from false negation ($662 spend). 2 keyword gaps filled + 1 campaign reactivated.

### Run: 2026-03-02 (Dessert Family)
**Result:** Success — 46 terms analyzed, 4 hygiene negatives applied, 2 bids lowered
**Key outcome:** 80% of terms were protected sewing keywords. Problem was stock collapse, not bad keywords.
