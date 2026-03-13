# PPC Agent Sessions

Output folder for autonomous PPC Agent sessions (Tuesday, Friday, Monthly).

## Folder Structure

```
sessions/
  YYYY-MM-DD-tuesday-brief.md         # Human-readable session brief
  YYYY-MM-DD-tuesday-actions.json     # Machine-readable action items
  YYYY-MM-DD-friday-brief.md          # Friday check brief
  YYYY-MM-DD-friday-actions.json      # Friday action items (if any)
  YYYY-MM-DD-monthly-brief.md         # Monthly strategic review
  YYYY-MM-DD-monthly-actions.json     # Monthly action items
  archive/                            # Old session logs (auto-trimmed)
```

## File Naming

- **Briefs:** `YYYY-MM-DD-{type}-brief.md` where type = tuesday/friday/monthly
- **Action items:** `YYYY-MM-DD-{type}-actions.json`

## Action Items JSON Schema

Every session produces a machine-readable action items file alongside the brief.
The Tuesday agent session and interactive "apply items" workflow both read this file.

```json
{
  "session_date": "YYYY-MM-DD",
  "session_type": "tuesday/friday/monthly",
  "produced_by": "ppc-agent-autonomous",
  "actions": [
    {
      "id": "ACT-YYYY-MM-DD-NNN",
      "priority": "P1/P2/P3/P4",
      "type": "NEGATE_SEARCH_TERM/TOS_DECREASE/TOS_INCREASE/DEFAULT_BID_DECREASE/DEFAULT_BID_INCREASE/BUDGET_INCREASE/BUDGET_DECREASE/KEYWORD_PAUSE/CAMPAIGN_CREATE/CAMPAIGN_ENABLE",
      "portfolio": "portfolio-name",
      "portfolio_slug": "portfolio-slug",
      "portfolio_id": "12345",
      "campaign_id": "67890",
      "campaign_name": "Campaign Name",
      "description": "Human-readable description of the action",
      "params": {},
      "evidence": {
        "source_skill": "search-term-harvester/bid-recommender/rank-optimizer/etc",
        "source_file": "path to the Monday pipeline output that supports this",
        "period": "30d/14d/7d",
        "metrics": {}
      },
      "expected_impact": "Save ~$X/week or +$X/week profitable spend",
      "risk": "low/medium/high",
      "confidence": "high/medium/low",
      "status": "pending_approval",
      "applied_date": null,
      "applied_by": null,
      "validated_date": null,
      "validation_result": null
    }
  ],
  "validations": [
    {
      "action_id": "ACT-YYYY-MM-DD-NNN",
      "original_session": "YYYY-MM-DD",
      "applied_date": "YYYY-MM-DD",
      "validation_date": "YYYY-MM-DD",
      "before": {},
      "after": {},
      "verdict": "WORKED/PARTIAL/FAILED/INCONCLUSIVE",
      "notes": ""
    }
  ],
  "summary": {
    "total_actions": 0,
    "by_priority": {"p1": 0, "p2": 0, "p3": 0, "p4": 0},
    "total_validations": 0,
    "validation_results": {"worked": 0, "partial": 0, "failed": 0, "inconclusive": 0},
    "estimated_weekly_impact": 0
  }
}
```

## Lifecycle

1. **Monday pipeline** runs 5 skills, saves structured JSON outputs
2. **Tuesday agent** reads those outputs, cross-references, produces brief + actions.json
3. **User** reads Notion brief (or disk brief), decides which actions to approve
4. **User** runs agent interactively: "apply items 1 and 3 from Tuesday"
5. **Agent** reads actions.json, executes approved items, updates `applied_date`
6. **Friday agent** validates applied actions, produces validation scorecards

## Trim Rules

- Keep last 20 sessions in this folder
- Older briefs + action files move to `archive/`
- Trim happens at the end of every Tuesday session
