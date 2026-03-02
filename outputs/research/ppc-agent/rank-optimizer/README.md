# Keyword Rank Optimizer Outputs

Outputs from the Keyword Rank Optimizer skill — cross-references PPC spend with organic keyword ranking.

## Folder Structure

```
rank-optimizer/
├── briefs/                         # Human-readable analysis reports
│   └── YYYY-MM-DD-rank-optimizer.md
├── snapshots/                      # Machine-readable data (persisted for trending)
│   └── YYYY-MM-DD/
│       ├── rank-spend-matrix.json  # Core cross-reference: keyword classifications + metrics
│       └── rank-radar-snapshot.json # Raw rank data (fills historical gap)
└── README.md                       # This file
```

## Naming Conventions

| File Type | Format |
|-----------|--------|
| Analysis briefs | `YYYY-MM-DD-rank-optimizer.md` |
| Rank-spend matrix | `rank-spend-matrix.json` (in dated subfolder) |
| Rank radar snapshot | `rank-radar-snapshot.json` (in dated subfolder) |

## Cadence

**Weekly** — runs after the Weekly PPC Analysis provides fresh targeting data.

## Key Data

- **rank-spend-matrix.json** — Every keyword classified as WASTING / REDUCE / PROTECT / MAINTAIN / REDIRECT / MONITOR with full PPC + rank metrics
- **rank-radar-snapshot.json** — Persisted rank data from DataDive. This is the critical gap fill — other PPC skills can read this for historical rank trending without re-fetching from DataDive.

## Data Flow

- **Reads from:** Weekly PPC snapshots (targeting report), DataDive Rank Radar (fresh), context/search-terms.md, context/business.md
- **Consumed by:** Bid Recommender (keyword waste signals), Weekly PPC Analysis (historical rank), Search Term Harvester (rank safety checks), Monthly Review (rank trending)
