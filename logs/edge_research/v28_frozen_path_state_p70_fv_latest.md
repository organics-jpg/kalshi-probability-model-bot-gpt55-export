# v28 Frozen Path-State p70 FV

- Freeze timestamp UTC: `2026-05-06T05:07:19.935392+00:00`
- Entry policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Variant: `path_state_guarded_p70_logit125`
- Future entries/settled/denominator: `94/94/129`
- Future coverage: `72.868217`

## Current Read

- Future rows are frozen from this script's timestamp: 94 entries over 129 markets.
- Best future variant is hard_p70_logit125 with Brier/logloss deltas -0.00034938015785207336/-0.0033345342070059715.
- Pre-freeze diagnostic path-state Brier/logloss deltas are -0.003021153156380292/-0.013218951584094444; this is not promotion evidence.
- Use this as a path/state confirmation monitor, not a live rule, until it earns forward sample size.

## Ranking

| rank | variant | rows | adjusted | W/L | net c | brier mean | brier p95 | logloss mean | logloss p95 | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `hard_p70_logit125` | 94 | 23 | 52/42 | -541.000000 | -0.000349 | 0.002462 | -0.003335 | 0.004591 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 2 | `path_state_guarded_p70_logit125` | 94 | 13 | 52/42 | -541.000000 | -0.000211 | 0.001753 | -0.002382 | 0.002919 | brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative |
| 3 | `raw_probability` | 94 | 0 | 52/42 | -541.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | none |

## Future Action Rollups

| action | rows | adjusted | W/L | brier d sum | logloss d sum | net c |
|---|---:|---:|---:|---:|---:|---:|
| raw_below_p70 | 71 | 0 | 33/38 | 0.000000 | 0.000000 | -879.000000 |
| sharpen_strong_book_discount | 13 | 13 | 11/2 | -0.019832 | -0.223884 | 245.000000 |
| keep_raw_unearned_confirmation | 8 | 0 | 7/1 | 0.000000 | 0.000000 | 189.000000 |
| keep_raw_low_confirmation_thin_mid_geometry | 2 | 0 | 1/1 | 0.000000 | 0.000000 | -96.000000 |

## Pre-Freeze Diagnostic

- Entries/settled: `31/31`
- Brier/logloss mean delta: `-0.003021/-0.013219`

| action | rows | adjusted | W/L | brier d sum | logloss d sum | net c |
|---|---:|---:|---:|---:|---:|---:|
| raw_below_p70 | 16 | 0 | 11/5 | 0.000000 | 0.000000 | 493.000000 |
| sharpen_strong_book_discount | 7 | 7 | 7/0 | -0.083459 | -0.358422 | 176.000000 |
| keep_raw_unearned_confirmation | 5 | 0 | 4/1 | 0.000000 | 0.000000 | 0.000000 |
| keep_raw_low_confirmation_thin_mid_geometry | 2 | 0 | 1/1 | 0.000000 | 0.000000 | -116.000000 |
| sharpen_deep_geometry | 1 | 1 | 1/0 | -0.010197 | -0.051365 | 32.000000 |
