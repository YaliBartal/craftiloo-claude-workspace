# DEPRECATED — Product Listing Development

**Deprecated:** 2026-03-10
**Replaced by:** `.claude/skills/listing-manager/`

## Why

The product-listing-development skill was an orchestrator that combined listing-creator + image-planner with shared research for new products. It has been absorbed into **listing-manager**, which handles:

1. **New products** (what this skill did) — shared research + listing + images
2. **Existing products** (what this skill couldn't do) — audit + optimize + push + AB measurement
3. **Iteration** (what this skill couldn't do) — re-optimize after AB analysis shows negative results

The shared research efficiency (no duplicate API calls for listing + images) is preserved in listing-manager's NEW_PRODUCT flow.

## Migration

All routing that pointed to `product-listing-development` now points to `listing-manager`:
- "Full listing" / "Launch product" / "Listing + images" → listing-manager
- "Create a listing" / "New listing" → listing-manager

## Files Kept for Reference

- `SKILL.md` — Original skill instructions (shared research logic ported to listing-manager)
- `LESSONS.md` — Run history (0 runs logged)
