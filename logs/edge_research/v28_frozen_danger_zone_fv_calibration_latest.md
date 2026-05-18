# v28 Frozen Danger-Zone FV Calibration

- Freeze timestamp UTC: `2026-05-06T03:14:35.467881+00:00`
- Future rows/markets/danger rows: `142/84/8`
- Best overlay: `danger_to_book`

## Current Read

- Frozen danger-zone FV best overlay is danger_to_book with Brier/logloss deltas -0.004051658561887328/-0.05274815488405854.
- Future rows/danger rows: 142/8.

## Ranking

| rank | overlay | rows | W/L | avg p | win rate | brier | d brier | logloss | d logloss | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `danger_to_book` | 142 | 125/17 | 0.866937 | 0.880282 | 0.102836 | -0.004052 | 0.358718 | -0.052748 | none |
| 2 | `raw_probability` | 142 | 125/17 | 0.884479 | 0.880282 | 0.106888 | 0.000000 | 0.411466 | 0.000000 | none |
| 3 | `book_probability` | 142 | 125/17 | 0.781197 | 0.880282 | 0.111884 | 0.004996 | 0.385301 | -0.026165 | brier_not_better_than_raw |
