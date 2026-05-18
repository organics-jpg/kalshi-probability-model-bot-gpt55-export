# v28 Frozen Composite False-Conviction FV

- Freeze timestamp UTC: `2026-05-06T09:44:24.062007+00:00`
- Entry policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Target variant: `composite_false_conviction_full_to_book`
- Future entries/settled/denominator: `81/81/111`
- Coverage: `72.972973`
- Best variant: `composite_false_conviction_full_to_50`

## Current Read

- Frozen composite false-conviction FV has 81 entries over 111 future markets.
- It is calibration-only until enough future settled and adjusted rows exist.

## Ranking

| rank | variant | rows | adjusted | false-zone | W/L | net c | brier mean | brier p95 | logloss mean | logloss p95 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `composite_false_conviction_full_to_50` | 81 | 33 | 33 | 48/33 | 127.000000 | -0.005133 | 0.005990 | -0.010543 | 0.012113 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 2 | `composite_false_conviction_half_to_book` | 81 | 33 | 33 | 48/33 | 127.000000 | -0.000783 | 0.005930 | -0.001669 | 0.012314 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 3 | `composite_false_conviction_full_to_book` | 81 | 33 | 33 | 48/33 | 127.000000 | 0.001493 | 0.015262 | 0.002570 | 0.032047 | mean_brier_not_better, brier_interval_not_strictly_negative, mean_logloss_not_better, logloss_interval_not_strictly_negative |
| 4 | `raw_probability` | 81 | 0 | 33 | 48/33 | 127.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | adjusted_rows_lt_8 |
