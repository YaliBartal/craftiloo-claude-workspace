# Listing Creator — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`, `context/tooling-workarounds.md`
> Run log archive → `outputs/research/listing-manager/run-logs/`

## Skill-Specific Lessons

1. Same-day audit → listing creator is the ideal workflow — audit identifies what's wrong, creator fixes it
2. Always count backend bytes before pushing — 249 limit is strict (not 250)
3. For products with refund issues, listing must EDUCATE wrong buyers, not just warn them — size comparison + pegboard incompatibility beats age warnings
4. A+ content overrides description — always ask about A+ before writing/pushing description
5. Competitor bullets are nearly as useful as Q&A for understanding customer concerns
6. Including individual age numbers (6, 7, 8, 9, 10, 11, 12) helps index for "ages 8-12" type searches
7. For Launch-stage products, keyword indexing > benefit copy in bullets
8. Category cross-indexing means adding keywords explicitly amplifies existing associations
9. Price premium must be justified through perceived value in bullets (gem stickers, counting practice, reusable box)
10. User wants brand name "Craftiloo" at title start — branding decision across portfolio

## Known Issues

### 1. Apify product scraper does not include customer Q&A
`saswave~amazon-product-scraper` returns product data but no Q&A. Use competitor bullets + web search instead.

### 2. Product catalog discrepancy — threader count
`products.md` says EK17 has "4 threaders" but `hero-products.md` says "2 needle threaders". Needs user verification.

## Repeat Errors

### 1. OneDrive EEXIST (x5)
See `context/tooling-workarounds.md`.

## Resolved Issues

_None yet._

## Recent Runs (last 3)

### Run: 2026-03-06 (e) — Latch Hook Pencil Cases
**Result:** Success — pushed live, ACCEPTED. Backend expanded 95→249 bytes (+162%). Removed competitor brand name.

### Run: 2026-03-06 (d) — Princess Lacing Cards
**Result:** Success — pushed live, ACCEPTED. 3 missing high-BSV roots now covered.

### Run: 2026-03-06 (c) — 10mm Big Fuse Beads
**Result:** Success — user chose educational Bullet 5 over compatibility. Backend 105→248 bytes.
