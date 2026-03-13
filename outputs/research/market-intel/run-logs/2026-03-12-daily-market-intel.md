# Run Log: Daily Market Intel — 2026-03-12

## Result: Partial (4/6 sources live)

**Sources:** SP-API ✅ | Rank Radar ✅ | DD Competitors ✅ | Apify BSR ✅ | Apify Keywords ❌ (carried fwd Mar 9) | Seller Board ❌ (401 x5)

## Key Outcomes

- ✅ **B08DDJCQKF restocked**: 73 → 2,059 units. Stock crisis resolved.
- 🔴 **B096MYBLS1 OOS**: BSR 222K, listing suppressed. 0 inbound.
- 🔴 **B0DC69M3YD crisis day 29+**: Lost "needlepoint kits for adults" (55K SV) 46→101. BSR still 30K.
- 📈 **B0F6YTG1CH BSR -23,809**: 50,832→27,023. New product ramping.
- 📉 **B0F8DG32H5 BSR +7,325**: 24,706→32,031. "crochet loom" + "knitting kits" fell to rank 101.
- **Mar 11 orders**: 171 orders, 173 units, $2,383 shipped (incl. tax).
- **BSR trend**: 4 improving, 9 declining vs Mar 9 (3-day gap).

## Issues Encountered

1. Apify axesso keyword scan failed x2 (context overflow) — added to Repeat Errors, Known Issue added.
2. Seller Board 401 x5 — now Repeat Error.

## Lessons Added

- Apify axesso: must batch into ≤5 keywords per subagent. Do NOT run 20 in one call.
