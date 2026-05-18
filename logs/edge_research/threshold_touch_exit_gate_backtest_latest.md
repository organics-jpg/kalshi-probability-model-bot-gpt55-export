# Threshold Touch + FV/Boundary Exit Gate Backtest

Research-only. No live bot, order logic, thresholds, state, secrets, sizing, or orders are touched.

- Labeled finalized markets: 188
- Raw ticker events scanned: 58322
- Labeled markets with raw ticker events: 79
- Markets with selected predictor rows: 145
- Markets with any v28 rows: 188
- Predictor carrier: `v28s_boundary_monotonic_light_v001`
- Entry model: buy the first side whose raw top-of-book ask touches/crosses the threshold; entry price is fixed at the threshold.
- `strict_cross` requires an observed below-threshold quote before the touch.
- `include_left_censored` also includes markets where recording started after the side was already above the threshold; those rows are useful but optimistic.
- Candidate exit gates use the selected carrier only; v28/book exit gates use the full deduped v28 row stream.
- Exit gates are evaluated only after entry and before close using causal predictor rows.
- PnL is cents per one contract, fee-aware on entry and fee-aware on early exit.

## Key Include-Left-Censored Rows
| threshold | gate | entries | wins if held | losses if held | exits | exited winners | exited losers | net c | avg c | LCB c |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 80 | hold | 71 | 57 | 14 | 0 | 0 | 0 | -122.0 | -1.72 | -11.04 |
| 80 | candidate_fair_lt_75 | 71 | 57 | 14 | 13 | 9 | 4 | -131.0 | -1.85 | -10.07 |
| 80 | candidate_fair_lt_80 | 71 | 57 | 14 | 18 | 13 | 5 | -89.0 | -1.25 | -8.96 |
| 80 | candidate_fair_lt_85 | 71 | 57 | 14 | 22 | 17 | 5 | -142.0 | -2.00 | -9.64 |
| 80 | candidate_fair_lt_entry_minus_5 | 71 | 57 | 14 | 13 | 9 | 4 | -131.0 | -1.85 | -10.07 |
| 80 | candidate_fair_lt_80_or_bid_lt_entry_minus_10 | 71 | 57 | 14 | 18 | 13 | 5 | -89.0 | -1.25 | -8.96 |
| 80 | candidate_fair_lt_85_or_bid_lt_entry_minus_5 | 71 | 57 | 14 | 22 | 17 | 5 | -142.0 | -2.00 | -9.64 |
| 90 | hold | 63 | 59 | 4 | 0 | 0 | 0 | 167.0 | 2.65 | -3.42 |
| 90 | candidate_fair_lt_75 | 63 | 59 | 4 | 3 | 3 | 0 | 133.9 | 2.13 | -3.94 |
| 90 | candidate_fair_lt_80 | 63 | 59 | 4 | 5 | 5 | 0 | 102.9 | 1.63 | -4.44 |
| 90 | candidate_fair_lt_85 | 63 | 59 | 4 | 9 | 9 | 0 | 42.1 | 0.67 | -5.41 |
| 90 | candidate_fair_lt_entry_minus_5 | 63 | 59 | 4 | 9 | 9 | 0 | 42.1 | 0.67 | -5.41 |
| 90 | candidate_fair_lt_80_or_bid_lt_entry_minus_10 | 63 | 59 | 4 | 6 | 6 | 0 | 76.9 | 1.22 | -4.87 |
| 90 | candidate_fair_lt_85_or_bid_lt_entry_minus_5 | 63 | 59 | 4 | 10 | 10 | 0 | 21.1 | 0.33 | -5.75 |

## Top Configurations
| threshold | mode | gate | entries | wins if held | losses if held | exits | left censored | net c | avg c | LCB c |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 90 | include_left_censored | hold | 63 | 59 | 4 | 0 | 4 | 167.0 | 2.65 | -3.42 |
| 90 | include_left_censored | candidate_fair_lt_70 | 63 | 59 | 4 | 1 | 4 | 154.0 | 2.44 | -3.63 |
| 90 | include_left_censored | candidate_fair_lt_60 | 63 | 59 | 4 | 1 | 4 | 152.0 | 2.41 | -3.66 |
| 90 | strict_cross | hold | 60 | 56 | 4 | 0 | 0 | 140.0 | 2.33 | -4.03 |
| 90 | include_left_censored | candidate_fair_lt_75 | 63 | 59 | 4 | 3 | 4 | 133.9 | 2.13 | -3.94 |
| 90 | strict_cross | candidate_fair_lt_70 | 60 | 56 | 4 | 1 | 0 | 127.0 | 2.12 | -4.25 |
| 90 | strict_cross | candidate_fair_lt_60 | 60 | 56 | 4 | 1 | 0 | 125.0 | 2.08 | -4.28 |
| 90 | include_left_censored | v28_fair_lt_70 | 63 | 59 | 4 | 5 | 4 | 120.2 | 1.91 | -4.01 |
| 90 | include_left_censored | v28_fair_lt_60 | 63 | 59 | 4 | 5 | 4 | 118.2 | 1.88 | -4.05 |
| 90 | strict_cross | candidate_fair_lt_75 | 60 | 56 | 4 | 3 | 0 | 106.9 | 1.78 | -4.58 |
| 90 | include_left_censored | candidate_fair_lt_80 | 63 | 59 | 4 | 5 | 4 | 102.9 | 1.63 | -4.44 |
| 90 | include_left_censored | candidate_fair_lt_entry_minus_10 | 63 | 59 | 4 | 5 | 4 | 102.9 | 1.63 | -4.44 |
| 90 | include_left_censored | v28_fair_lt_75 | 63 | 59 | 4 | 7 | 4 | 100.1 | 1.59 | -4.32 |
| 90 | strict_cross | v28_fair_lt_70 | 60 | 56 | 4 | 5 | 0 | 93.2 | 1.55 | -4.65 |
| 90 | strict_cross | v28_fair_lt_60 | 60 | 56 | 4 | 5 | 0 | 91.2 | 1.52 | -4.69 |
| 90 | include_left_censored | bid_lt_entry_minus_15 | 63 | 59 | 4 | 5 | 4 | 87.2 | 1.38 | -4.66 |
| 90 | include_left_censored | v28_fair_lt_85 | 63 | 59 | 4 | 12 | 4 | 77.2 | 1.23 | -4.09 |
| 90 | include_left_censored | candidate_fair_lt_80_or_bid_lt_entry_minus_10 | 63 | 59 | 4 | 6 | 4 | 76.9 | 1.22 | -4.87 |
| 90 | strict_cross | candidate_fair_lt_80 | 60 | 56 | 4 | 5 | 0 | 75.9 | 1.26 | -5.10 |
| 90 | strict_cross | candidate_fair_lt_entry_minus_10 | 60 | 56 | 4 | 5 | 0 | 75.9 | 1.26 | -5.10 |
| 90 | strict_cross | v28_fair_lt_75 | 60 | 56 | 4 | 7 | 0 | 73.1 | 1.22 | -4.98 |
| 90 | include_left_censored | v28_fair_lt_80 | 63 | 59 | 4 | 9 | 4 | 69.1 | 1.10 | -4.82 |
| 90 | strict_cross | bid_lt_entry_minus_15 | 60 | 56 | 4 | 5 | 0 | 60.2 | 1.00 | -5.33 |
| 90 | include_left_censored | candidate_fair_lt_90 | 63 | 59 | 4 | 9 | 4 | 58.4 | 0.93 | -5.13 |

## Correctness Notes
- This is the intended threshold-touch framing, so 80/90 entry counts do not depend on FV approval.
- Entry counts can still be below all finalized labels because not every labeled market has raw ticker coverage or a causal touch timestamp.
- The include-left-censored rows answer the user's intuition that the market had already hit the threshold, but they are optimistic because the exact historical fill moment was not observed.
- A promotable live strategy would freeze this policy forward and judge it on live incoming markets, not on this diagnostic alone.
