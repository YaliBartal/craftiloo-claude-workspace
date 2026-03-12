# Daily Market Intel — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`, `context/tooling-workarounds.md`
> Run log archive → `outputs/research/market-intel/run-logs/`

## Skill-Specific Lessons

1. Parallel launch of all Apify runs (product + SERP) — all succeed in ~90 seconds
2. SP-API QuotaExceeded on pricing calls auto-retries successfully — no action needed
3. B08DDJCQKF inventory spikes (1,386→82 in one day) are FBA API anomalies — check BSR + keyword stability before flagging
4. DataDive niche data can be weeks old — always note freshness in reports
5. When user references a list they didn't send, proceed with DataDive data and note the gap
6. Always flag IP/trademark issues prominently when product concept uses brand names (Barbie, Disney)
7. kullaloo and Louise Maelys should be added to competitor tracking (flagged 7+ and 10+ days)
8. Apify axesso keyword scan: 20 keywords per run works well. saswave BSR: 31-33 ASINs per run
9. saswave BSR field confirmed: `bestsellerRanks[0].rank` (comma-formatted string). B004JIFCXO consistently has no BSR — product-level issue
10. saswave prices are in EUR — ignore price field, use SP-API for USD pricing
11. **Apify axesso 20-keyword scan WILL OVERFLOW the subagent context** — even with a simplified prompt, the agent hits "Prompt is too long" after accumulating 20 SERP result sets. Solution: either batch into ≤5 keywords per subagent (4 parallel agents) or process results inline within a single agent. Do NOT try to run all 20 in one subagent.

## Known Issues

### 1. Seller Board 401 (x4+ consecutive)
Tokens expired since 2026-03-02. Fix: SB → Settings → Automation → Reports → regenerate URLs, update .env.
Also: `SELLERBOARD_SALES_DETAILED_7D` was never added to .env.

### 2. B08DDJCQKF has no Rank Radar configured
No rank trend data for #1 product. Needs DataDive setup.

### 3. B0DC69M3YD rank crisis ongoing (day 29+)
"embroidery kit" keywords collapsing. "needlepoint kits for adults" (55K SV) fell 46→101 on Mar 12.

### 4. Apify axesso 20-keyword scan context overflow
Fails every time as a single subagent (×2). Must batch into ≤5 keywords per subagent.

## Repeat Errors

### 1. Seller Board 401 (x5)
See Known Issue #1. Escalating — must fix.

### 2. Apify axesso keyword scan context overflow (x2)
See Known Issue #4. Do NOT retry as single agent — batch into groups of 5.

## Resolved Issues

### 1. saswave BSR field null (2026-03-09)
Field is `bestsellerRanks[0].rank` (array, comma-formatted string). Resolved after field inspection.

### 2. B08DDJCQKF stock critical (2026-03-09)
Was 73 units. Restocked to 2,059 by 2026-03-12. Resolved.

## Recent Runs (last 3)

### Run: 2026-03-12
**Result:** Partial — SP-API ✅, Rank Radar ✅, DD Competitors ✅, Apify BSR ✅. Keyword SERP ❌ (context overflow x2), SB ❌ (401 x5)
**Key outcome:** B08DDJCQKF restocked (73→2,059) ✅. B0DC69M3YD crisis day 29+ deepening. B0F6YTG1CH BSR -23,809. 4/13 improving vs Mar 9. Mar 11 orders: 171/$2,383.

### Run: 2026-03-09
**Result:** Partial — 5/5 non-SB sources succeeded, SB 401 again
**Key outcome:** B08DDJCQKF stock at 73 (critical ~2-3 days). B0F8R652FX #1 + B08FYH13CL #2 on "latch hook kits for kids" (was #5+#17).

### Run: 2026-03-08
**Result:** Partial — 5/5 non-SB, SB 401. saswave BSR returned null (new field issue)
**Key outcome:** B09X55KL2C reclaimed #1 on "kids embroidery kit". B0F8DG32H5 lost knitting keywords off page.
