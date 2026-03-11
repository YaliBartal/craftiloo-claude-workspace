# Customer Review Analyzer — Lessons & Issues

> Cross-skill knowledge → `context/api-patterns.md`
> Run log archive → `outputs/research/competitor-analysis/run-logs/`

## Skill-Specific Lessons

1. `junglee/amazon-reviews-scraper` caps at ~8 reviews (1 page) — do NOT rely for 50+ reviews
2. For 50 reviews, run junglee with explicit page URLs: `?pageNumber=2&sortBy=recent` up to page 6
3. Best paid option: `axesso_data` at $0.00075/review (50 reviews x 2 ASINs = $0.075)
4. Patterns from 8 reviews are suggestive, not statistically reliable

## Known Issues

### 1. junglee scraper hard-capped at ~8 reviews
`maxReviews` ignored. Same with/without residential proxy. Workaround: explicit page URLs.

### 2. axesso maxPages parameter non-functional
`maxPages: 5` returns same as `maxPages: 1`. Same page-by-page workaround.

### 3. epctex scraper requires paid rental
Cannot use without subscribing. Remove from fallback lists.

### 4. web_wanderer returned 0 results
Possible anti-bot block or wrong input format. Needs retry with full review URL format.

## Repeat Errors

_None yet._

## Resolved Issues

_None yet._

## Recent Runs (last 3)

### Run: 2026-02-26
**Result:** Partial — 16 reviews collected (8 per ASIN) instead of target 100
**Key outcome:** Hapinest 4.5/5 (426 ratings), CFK 4.6/5 (3336 ratings). All 4 scraper actors tested.
