# v28 Recross-Escape Probability Calibration

Fixed-row probability calibration for the p52 recross-escape candidate. This scores FV accuracy only; P&L is unchanged.

- Policy: `p52_recross_escape_opp240_oppedge5_keep`
- Entries/settled: `169/169`

## Scorecard

| probability | count | W/L | avg p | brier | brier d | logloss | logloss d | ece | ece d |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| raw_probability | 169 | 106/63 | 0.651700 | 0.214961 | 0.000000 | 0.612423 | 0.000000 | 0.059189 | 0.000000 |
| logit110_probability | 169 | 106/63 | 0.663273 | 0.215507 | 0.000546 | 0.612747 | 0.000324 | 0.047343 | -0.011846 |
| logit125_probability | 169 | 106/63 | 0.679498 | 0.216942 | 0.001981 | 0.615170 | 0.002746 | 0.061413 | 0.002224 |
| plus03_probability | 169 | 106/63 | 0.681679 | 0.217330 | 0.002369 | 0.616109 | 0.003685 | 0.064719 | 0.005530 |
| conservative_mode_probability | 169 | 106/63 | 0.677537 | 0.217603 | 0.002642 | 0.617007 | 0.004584 | 0.060458 | 0.001269 |
| mode_calibrated_probability | 169 | 106/63 | 0.689489 | 0.218781 | 0.003820 | 0.619920 | 0.007497 | 0.070253 | 0.011065 |
| plus05_probability | 169 | 106/63 | 0.701556 | 0.219906 | 0.004945 | 0.621243 | 0.008820 | 0.081584 | 0.022395 |

## Best By Mode

- `base`: count `131`, W/L `84/47`, avg p `0.673267`, brier `0.205384`
- `danger_follow_opposite`: count `8`, W/L `5/3`, avg p `0.704727`, brier `0.246300`
- `danger_keep_high_edge`: count `4`, W/L `2/2`, avg p `0.538735`, brier `0.241079`
- `danger_no_opposite_keep`: count `26`, W/L `15/11`, avg p `0.544103`, brier `0.249555`

## Lift Plateau

- Best lift: `-0.020000` with Brier `0.214382`
- Improving lifts vs raw: `[-0.04, -0.03, -0.02, -0.01]`

| lift | avg p | brier | brier d | logloss | logloss d |
|---:|---:|---:|---:|---:|---:|
| -0.050000 | 0.601700 | 0.215013 | 0.000052 | 0.615213 | 0.002790 |
| -0.030000 | 0.621700 | 0.214392 | -0.000569 | 0.612845 | 0.000421 |
| 0.000000 | 0.651700 | 0.214961 | 0.000000 | 0.612423 | 0.000000 |
| 0.030000 | 0.681679 | 0.217330 | 0.002369 | 0.616109 | 0.003685 |
| 0.050000 | 0.701556 | 0.219906 | 0.004945 | 0.621243 | 0.008820 |
| 0.070000 | 0.721319 | 0.223275 | 0.008314 | 0.628919 | 0.016496 |
| 0.100000 | 0.750628 | 0.229804 | 0.014843 | 0.647061 | 0.034637 |
| 0.150000 | 0.797382 | 0.244188 | 0.029227 | 0.744260 | 0.131836 |

## Plus05 Jackknife

- Slices: `169`
- Brier improved slices: `0`
- Logloss improved slices: `0`
- Worst Brier delta: `0.005244`
- Worst logloss delta: `0.009418`
