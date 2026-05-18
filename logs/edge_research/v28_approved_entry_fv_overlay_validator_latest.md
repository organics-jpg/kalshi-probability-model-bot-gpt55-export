# v28 Approved-Entry FV Overlay Validator

FV overlay calibration using only v28-approved entry rows.

- Rows/settled: `173/173`
- Best overlay: `book_probability`

## Current Read

- Best approved-entry overlay by Brier is book_probability with Brier delta -0.0048166936698150475.
- Raw approved-entry calibration error is -0.03995695953757228 with win rate 0.8439306358381503 and avg p 0.8838875953757226.

## Ranking

| rank | overlay | settled | W/L | avg p | win rate | cal err | brier | d brier | logloss | d logloss | gross c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `book_probability` | 173 | 146/27 | 0.777341 | 0.843931 | 0.066590 | 0.128817 | -0.004817 | 0.424602 | -0.048654 | 823.000000 | none |
| 2 | `noise_shrink_light_probability` | 173 | 146/27 | 0.875332 | 0.843931 | -0.031401 | 0.133088 | -0.000547 | 0.448422 | -0.024834 | 823.000000 | none |
| 3 | `raw_probability` | 173 | 146/27 | 0.883888 | 0.843931 | -0.039957 | 0.133634 | 0.000000 | 0.473256 | 0.000000 | 823.000000 | none |
| 4 | `entry_conditioned_plus03_probability` | 173 | 146/27 | 0.913558 | 0.843931 | -0.069628 | 0.136579 | 0.002945 | 0.527525 | 0.054269 | 823.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 5 | `entry_conditioned_logit125_probability` | 173 | 146/27 | 0.925186 | 0.843931 | -0.081255 | 0.138231 | 0.004597 | 0.514547 | 0.041291 | 823.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 6 | `entry_conditioned_logit125_p60_only_probability` | 173 | 146/27 | 0.925186 | 0.843931 | -0.081255 | 0.138231 | 0.004597 | 0.514547 | 0.041291 | 823.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 7 | `entry_conditioned_plus05_noise_attenuated_probability` | 173 | 146/27 | 0.931096 | 0.843931 | -0.087166 | 0.139050 | 0.005416 | 0.595783 | 0.122527 | 823.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 8 | `entry_conditioned_plus05_probability` | 173 | 146/27 | 0.932955 | 0.843931 | -0.089024 | 0.139365 | 0.005731 | 0.597935 | 0.124679 | 823.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
