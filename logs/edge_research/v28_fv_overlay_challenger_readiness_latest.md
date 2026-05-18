# v28 FV Overlay Challenger Readiness

Forward-only readiness table for calibrated FV overlays on the fixed raw-v28 p50 entry surface.

- Entry surface: `v28_raw_p50_edge0_fixed_selection`
- Freeze timestamp UTC: `2026-05-05T23:30:17.615882+00:00`
- Forward denominator/entry rows: `152/150`
- Best forward overlay by current ranking: `book_probability`
- Any ready: `False`
- Path contradiction rows/losses: `44/35`

## Candidates

| overlay | ready | entries | settled | coverage | fwd brier d | fwd logloss d | disc brier d | disc logloss d | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| book_probability | False | 150 | 150 | 98.684211 | -0.012290 | -0.022481 | -0.006549 | -0.010476 | forward_coverage_too_high, forward_bucket_failure, forward_path_contradiction_loss |
| noise_shrink_light_probability | False | 150 | 150 | 98.684211 | -0.002682 | -0.005112 | -0.001502 | -0.002544 | forward_coverage_too_high, forward_bucket_failure, forward_path_contradiction_loss |
| raw_probability | False | 150 | 150 | 98.684211 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | forward_coverage_too_high, forward_path_contradiction_loss |
| entry_conditioned_logit125_p60_only_probability | False | 150 | 150 | 98.684211 | 0.002981 | 0.004515 | 0.002341 | 0.002945 | forward_coverage_too_high, forward_brier_not_better_than_raw, forward_logloss_not_better_than_raw, discovery_brier_not_better_than_raw, discovery_logloss_not_better_than_raw, forward_bucket_failure, forward_path_contradiction_loss |
| entry_conditioned_logit125_probability | False | 150 | 150 | 98.684211 | 0.003344 | 0.005195 | 0.002276 | 0.002762 | forward_coverage_too_high, forward_brier_not_better_than_raw, forward_logloss_not_better_than_raw, discovery_brier_not_better_than_raw, discovery_logloss_not_better_than_raw, forward_bucket_failure, forward_path_contradiction_loss |
| entry_conditioned_plus03_probability | False | 150 | 150 | 98.684211 | 0.005224 | 0.009456 | 0.003245 | 0.005231 | forward_coverage_too_high, forward_brier_not_better_than_raw, forward_logloss_not_better_than_raw, discovery_brier_not_better_than_raw, discovery_logloss_not_better_than_raw, forward_bucket_failure, forward_path_contradiction_loss |
| entry_conditioned_plus05_probability | False | 150 | 150 | 98.684211 | 0.009704 | 0.018232 | 0.006406 | 0.011122 | forward_coverage_too_high, forward_brier_not_better_than_raw, forward_logloss_not_better_than_raw, discovery_brier_not_better_than_raw, discovery_logloss_not_better_than_raw, forward_bucket_failure, forward_path_contradiction_loss |

## Physics Notes

- `book_probability`: Kalshi book-implied probability used as an external calibration anchor.
- `noise_shrink_light_probability`: Noise-floor shrinkage toward 50 in RMT/recross/stale states.
- `raw_probability`: Control. Raw v28 FV on the fixed broad p50 entry surface.
- `entry_conditioned_logit125_p60_only_probability`: Conditional conviction sharpening: keep weak 50-60% rows raw, sharpen only p>=60% rows.
- `entry_conditioned_logit125_probability`: Conviction sharpening: lift high-confidence rows more than weak rows without changing side.
- `entry_conditioned_plus03_probability`: Small posterior lift after executable raw edge clears.
- `entry_conditioned_plus05_probability`: Original posterior lift candidate; fresh rows suggest it over-lifts weak states.
