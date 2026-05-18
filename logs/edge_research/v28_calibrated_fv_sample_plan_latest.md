# v28 Calibrated FV Sample Plan

Forward-evidence runway for raw-entry FV overlays.

- Candidate: `v28_raw_entry_fv_overlay_bakeoff`
- Freeze timestamp UTC: `2026-05-05T23:30:17.615882+00:00`
- Readiness blockers: `forward_coverage_too_high, forward_bucket_failure, forward_path_contradiction_loss`

## Current Forward Evidence

- Denominator/selected/settled/pending: `152/150/150/0`
- Coverage: `98.684211`
- W/L and net: `83/67` / `-1009.000000c`
- Best overlay now: `book_probability`
- Best overlay Brier/logloss delta vs raw: `-0.012290` / `-0.022481`
- +5pp Brier/logloss delta vs raw: `0.009704` / `0.018232`

## Raw-Entry FV Overlay Bakeoff

- Freeze timestamp UTC: `2026-05-05T23:30:17.615882+00:00`
- Forward denominator/entry rows: `152/150`
- Current best overlay by frozen Brier: `book_probability`

| overlay | entries | settled | coverage | brier | brier d | logloss | logloss d | avg p | win rate | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| book_probability | 150 | 150 | 98.684211 | 0.217809 | -0.012290 | 0.622464 | -0.022481 | 0.560733 | 0.553333 | coverage_too_high, bucket_brier_not_better_than_raw |
| noise_shrink_light_probability | 150 | 150 | 98.684211 | 0.227417 | -0.002682 | 0.639833 | -0.005112 | 0.608259 | 0.553333 | coverage_too_high, bucket_brier_not_better_than_raw |
| raw_probability | 150 | 150 | 98.684211 | 0.230099 | 0.000000 | 0.644945 | 0.000000 | 0.625408 | 0.553333 | coverage_too_high |
| entry_conditioned_logit125_p60_only_probability | 150 | 150 | 98.684211 | 0.233080 | 0.002981 | 0.649460 | 0.004515 | 0.644022 | 0.553333 | coverage_too_high, brier_not_better_than_raw, bucket_brier_not_better_than_raw |
| entry_conditioned_logit125_probability | 150 | 150 | 98.684211 | 0.233443 | 0.003344 | 0.650140 | 0.005195 | 0.649566 | 0.553333 | coverage_too_high, brier_not_better_than_raw, bucket_brier_not_better_than_raw |
| entry_conditioned_plus03_probability | 150 | 150 | 98.684211 | 0.235324 | 0.005224 | 0.654401 | 0.009456 | 0.655383 | 0.553333 | coverage_too_high, brier_not_better_than_raw, bucket_brier_not_better_than_raw |

## Remaining Runway

- Settled selected rows still needed for 30: `0`
- Additional selected rows after current pending rows needed for 30: `0`
- Misses needed to bring current high coverage down to <=90%: `15`
- Miss budget after reaching 30 selected before coverage <70%: `62`

## Path/RMT Candidate Runway

- Current best target-coverage path policy: `selective_rmt_memory_gap_wait240_rmtedge02_or_opp`
- Entries/settled: `132/132`
- Actual/simulated entries: `13/119`; simulated share `0.901515`
- Coverage/net/Brier: `86.842105` / `-380.000000c` / `0.228359`
- Calibration deltas Brier/logloss: `0.007789` / `0.014568`
- Settled rows still needed for 30: `0`
- Additional actual entries needed for simulated share <=35%: `208`

## Early Warnings

- forward Brier delta turns nonnegative after at least 5 settled rows
- forward logloss delta turns nonnegative after at least 5 settled rows
- any eligible physics bucket with at least 5 settled rows has nonnegative Brier delta
- coverage remains above 90% after denominator is large enough to be meaningful
- coverage falls below 70% before 30 settled selected rows
