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

## Known Issues

### 1. Seller Board 401 (x4+ consecutive)
Tokens expired since 2026-03-02. Fix: SB → Settings → Automation → Reports → regenerate URLs, update .env.
Also: `SELLERBOARD_SALES_DETAILED_7D` was never added to .env.

### 2. B08DDJCQKF has no Rank Radar configured
No rank trend data for #1 product. Needs DataDive setup.

### 3. B0DC69M3YD rank crisis ongoing (day 27+)
"embroidery kit" (218K SV) rank 77→92 and declining.

## Repeat Errors

### 1. Seller Board 401 (x4)
See Known Issue #1. Escalating — must fix.

## Resolved Issues

### 1. saswave BSR field null (2026-03-09)
Field is `bestsellerRanks[0].rank` (array, comma-formatted string). Resolved after field inspection.

## Recent Runs (last 3)

### Run: 2026-03-09
**Result:** Partial — 5/5 non-SB sources succeeded, SB 401 again
**Key outcome:** B08DDJCQKF stock at 73 (critical ~2-3 days). B0F8R652FX #1 + B08FYH13CL #2 on "latch hook kits for kids" (was #5+#17).

### Run: 2026-03-08
**Result:** Partial — 5/5 non-SB, SB 401. saswave BSR returned null (new field issue)
**Key outcome:** B09X55KL2C reclaimed #1 on "kids embroidery kit". B0F8DG32H5 lost knitting keywords off page.

### Run: 2026-03-05
**Result:** Partial — 5/5 non-SB, SB 401
**Key outcome:** B08DDJCQKF reclaimed #1 on "cross stitch kits for kids". B09WQSBZY7 +3 top-10.
