# v28 Target-Coverage FV Fragility Audit

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Overlay: `book_probability`
- Rows/W/L: `112/64/48`
- Brier delta sum/mean: `-1.670226/-0.014913`
- Logloss delta sum/mean: `-3.022802/-0.026989`
- Negative/positive Brier rows: `48/64`
- Fragility flags: `none`

## Probability Buckets

| bucket | rows | W/L | brier sum | brier mean | logloss sum |
|---|---:|---:|---:|---:|---:|
| p50_60 | 36 | 17/19 | -0.890417 | -0.024734 | -1.963588 |
| p60_75 | 55 | 27/28 | -1.369520 | -0.024900 | -2.833676 |
| p75_plus | 21 | 20/1 | 0.589710 | 0.028081 | 1.774462 |

## Geometry Buckets

| bucket | rows | W/L | brier sum | brier mean | logloss sum |
|---|---:|---:|---:|---:|---:|
| strong_far_from_boundary | 21 | 20/1 | 0.589710 | 0.028081 | 1.774462 |
| strong_mid_geometry | 55 | 27/28 | -1.369520 | -0.024900 | -2.833676 |
| weak_but_wide_edge | 12 | 5/7 | -0.588345 | -0.049029 | -1.345287 |
| weak_other | 11 | 6/5 | 0.030515 | 0.002774 | 0.063333 |
| weak_turbulent_boundary | 13 | 6/7 | -0.332587 | -0.025584 | -0.681634 |

## Leave-One-Out Worst Cases

| removed market | removed brier d | remaining brier mean d | remaining logloss mean d |
|---|---:|---:|---:|
| KXBTC15M-26MAY062230-30 | -0.371146 | -0.011703 | -0.020135 |
| KXBTC15M-26MAY062100-00 | -0.330549 | -0.012069 | -0.020858 |
| KXBTC15M-26MAY061830-30 | -0.253088 | -0.012767 | -0.022330 |
| KXBTC15M-26MAY061745-45 | -0.240891 | -0.012877 | -0.022158 |
| KXBTC15M-26MAY070100-00 | -0.206638 | -0.013185 | -0.023135 |

## Biggest Help/Hurt

- Biggest helpers:
  - `KXBTC15M-26MAY062230-30` yes won `False` p `0.718015->0.380000` brier d `-0.371146`
  - `KXBTC15M-26MAY062100-00` no won `False` p `0.615588->0.220000` brier d `-0.330549`
  - `KXBTC15M-26MAY061830-30` yes won `False` p `0.553162->0.230000` brier d `-0.253088`
- Biggest hurts:
  - `KXBTC15M-26MAY070615-15` no won `True` p `0.610872->0.280000` brier d `0.366979`
  - `KXBTC15M-26MAY060945-45` no won `True` p `0.761891->0.500000` brier d `0.193304`
  - `KXBTC15M-26MAY061900-00` yes won `True` p `0.501794->0.340000` brier d `0.187391`
