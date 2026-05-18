# v28 Source-Aware FV Overlay Validator

Scores FV overlays on approved entries plus the frozen target-coverage forward slice.

- Rows/settled: `285/285`
- Approved/rejected settled: `180/105`
- Simulated share: `0.368421`
- Best overlay: `book_probability`
- Evidence blockers: `simulated_share_gt_35pct`

## Current Read

- Best combined FV overlay is book_probability with Brier delta -0.008784259450245635 and logloss delta -0.04014041423512027.
- Evidence mix is 180 approved settled rows and 105 target/rejected settled rows.
- Simulated/rejected share is 36.84%.

## Ranking

| rank | overlay | settled | W/L | avg p | win rate | cal err | brier | d brier | logloss | d logloss | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `book_probability` | 285 | 210/75 | 0.696982 | 0.736842 | 0.039860 | 0.159476 | -0.008784 | 0.492900 | -0.040140 | none |
| 2 | `source_aware_approved_book_target_raw` | 285 | 210/75 | 0.726412 | 0.736842 | 0.010430 | 0.166072 | -0.002189 | 0.506323 | -0.026717 | none |
| 3 | `source_aware_approved_book_target_logit125_p60_only` | 285 | 210/75 | 0.735322 | 0.736842 | 0.001520 | 0.167782 | -0.000479 | 0.509664 | -0.023376 | none |
| 4 | `raw_probability` | 285 | 210/75 | 0.793453 | 0.736842 | -0.056610 | 0.168261 | 0.000000 | 0.533040 | 0.000000 | none |
| 5 | `source_aware_approved_book_target_plus05` | 285 | 210/75 | 0.744833 | 0.736842 | -0.007991 | 0.170452 | 0.002191 | 0.515312 | -0.017728 | brier_not_better_than_raw |
| 6 | `entry_conditioned_logit125_p60_only_probability` | 285 | 210/75 | 0.828318 | 0.736842 | -0.091476 | 0.172620 | 0.004359 | 0.560481 | 0.027441 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 7 | `entry_conditioned_plus05_probability` | 285 | 210/75 | 0.842803 | 0.736842 | -0.105961 | 0.175956 | 0.007695 | 0.616476 | 0.083436 | brier_not_better_than_raw, logloss_not_better_than_raw |

## Best Overlay By Source

| source | rows | W/L | avg p | win rate | cal err | brier | logloss |
|---|---:|---:|---:|---:|---:|---:|---:|
| approved_entry | 180 | 153/27 | 0.778722 | 0.850000 | 0.071278 | 0.125333 | 0.416278 |
| rejected_actionable | 105 | 57/48 | 0.556857 | 0.542857 | -0.014000 | 0.218009 | 0.624252 |
