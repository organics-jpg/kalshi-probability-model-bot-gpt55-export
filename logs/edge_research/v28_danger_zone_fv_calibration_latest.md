# v28 Danger-Zone FV Calibration

- Surface: `actual_v28_approved_entries_only`
- Rows/markets: `173/107`
- Best overlay: `danger_to_book`

## Current Read

- Best danger-zone FV overlay is danger_to_book with Brier/logloss deltas -0.011340997078595372/-0.0661185329043299.
- Danger-zone rows are 12/173 with gross -322.0c.
- Discovery-only: any useful overlay needs a frozen forward validator before promotion.

## Ranking

| rank | overlay | settled | W/L | avg p | win rate | brier | d brier | logloss | d logloss | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `danger_to_book` | 173 | 146/27 | 0.860598 | 0.843931 | 0.122293 | -0.011341 | 0.407138 | -0.066119 | none |
| 2 | `danger_cap_gap15` | 173 | 146/27 | 0.871003 | 0.843931 | 0.123177 | -0.010457 | 0.409887 | -0.063369 | none |
| 3 | `danger_cap_gap20` | 173 | 146/27 | 0.873591 | 0.843931 | 0.124268 | -0.009366 | 0.413570 | -0.059686 | none |
| 4 | `danger_halfway_to_book` | 173 | 146/27 | 0.872243 | 0.843931 | 0.125208 | -0.008426 | 0.413863 | -0.059394 | none |
| 5 | `book_probability` | 173 | 146/27 | 0.777341 | 0.843931 | 0.128817 | -0.004817 | 0.424602 | -0.048654 | none |
| 6 | `danger_haircut_10pp` | 173 | 146/27 | 0.876951 | 0.843931 | 0.130121 | -0.003513 | 0.427627 | -0.045630 | none |
| 7 | `raw_probability` | 173 | 146/27 | 0.883888 | 0.843931 | 0.133634 | 0.000000 | 0.473256 | 0.000000 | none |

## Buckets

| bucket | rows | W/L | win rate | avg raw p | avg book p | actual c | hold c |
|---|---:|---:|---:|---:|---:|---:|---:|
| `danger_zone` | 12 | 7/5 | 0.583333 | 0.886589 | 0.550833 | -322.000000 | 78.000000 |
| `not_danger_zone` | 161 | 139/22 | 0.863354 | 0.883686 | 0.794224 | 1145.000000 | 2226.000000 |
| `same_side_reentry` | 57 | 49/8 | 0.859649 | 0.875996 | 0.776491 | 291.000000 | 948.000000 |
| `raw_book_gap_gt30` | 5 | 2/3 | 0.400000 | 0.915795 | 0.374000 | -94.000000 | 26.000000 |
