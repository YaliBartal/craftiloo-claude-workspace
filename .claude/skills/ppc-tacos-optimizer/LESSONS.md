# TACoS & Profit Optimizer — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`, `context/ppc-rules.md`, `context/tooling-workarounds.md`
> Run log archive → `outputs/research/ppc-agent/run-logs/`

## Skill-Specific Lessons

1. Always handle both string and dict formats when reading `hero_asins`/`secondary_asins` from portfolio trackers
2. SB 30d report returns ~2,000 rows — must save to file and parse from disk (never inline)
3. For 7d comparison, consider date-filtered 30d data instead of separate 7d API call
4. Break-even ACoS = margin %. Several ASINs have ACoS 2-4x margin, meaning every PPC sale loses money. Business works because organic (65%) generates profit

## Known Issues

### 1. Mixed ASIN formats in trackers
Some portfolio trackers store `hero_asins` as strings, others as dicts `{asin, product, role}`. Parse logic must handle both.

### 2. SB server needs restart for save_path
Added `save_path` param but requires restart. Workaround: fetch directly via httpx.

## Repeat Errors

_None yet._

## Resolved Issues

### 1. SB data truncation (2026-03-06)
`csv_to_summary()` capped at 100 rows. Added `save_path` parameter. ALWAYS use for reports >100 rows.
