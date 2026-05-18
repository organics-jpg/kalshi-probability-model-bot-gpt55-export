# v28 Frozen Recross-Escape Probability Calibration

Forward-only fixed-row FV calibration for the recross-escape challenger.

- Source freeze timestamp UTC: `2026-05-06T00:57:12.867086+00:00`
- Source forward denominator: `146`
- Policy: `p52_recross_escape_opp240_oppedge5_keep`
- Entries/settled: `143/143`

| probability | entries | settled | W/L | avg p | brier | brier d | logloss | logloss d | ece | ece d |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| raw_probability | 143 | 143 | 84/59 | 0.648438 | 0.220043 | 0.000000 | 0.621369 | 0.000000 | 0.095131 | 0.000000 |
| logit110_probability | 143 | 143 | 84/59 | 0.659965 | 0.221025 | 0.000982 | 0.622107 | 0.000738 | 0.096492 | 0.001361 |
| logit125_probability | 143 | 143 | 84/59 | 0.676211 | 0.223147 | 0.003104 | 0.625062 | 0.003693 | 0.113421 | 0.018289 |
| conservative_mode_probability | 143 | 143 | 84/59 | 0.674777 | 0.224016 | 0.003972 | 0.627518 | 0.006149 | 0.110918 | 0.015787 |
| plus03_probability | 143 | 143 | 84/59 | 0.678413 | 0.224605 | 0.004561 | 0.628775 | 0.007406 | 0.114695 | 0.019563 |
| mode_calibrated_probability | 143 | 143 | 84/59 | 0.686385 | 0.226164 | 0.006121 | 0.631379 | 0.010011 | 0.122081 | 0.026950 |
| plus05_probability | 143 | 143 | 84/59 | 0.698267 | 0.228642 | 0.008599 | 0.636169 | 0.014801 | 0.133718 | 0.038587 |
