# v28 Exit Clip Separator Opportunity

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T13:33:31.658932+00:00`
- Freeze UTC: `2026-05-07T04:04:23.876080+00:00`
- Rule: `For matched unchanged loss rows, flag rows with fair_drawdown_cents <= 10 and p_hold >= 0.60.`
- Post-freeze denominator rows: `2`
- Selected rows: `1`
- Selected helpful/harmful/unknown: `1/0/0`
- Selected known hold delta: `60c`
- Near-miss rows: `1`
- Near-miss helpful/harmful/unknown: `0/0/1`
- Near-miss known hold delta: `0c`
- Fail reasons: `{'p_hold_below_floor': 1, 'fair_drawdown_above_ceiling': 1}`
- Blockers: `post_rows_lt_30, selected_rows_lt_30, selected_delta_lt_300c`

## Interpretation

- Research-only opportunity and margin audit; no live bot logic changes or orders.
- The frozen rule has 2 post-freeze denominator rows and selected 1 row(s).
- Near misses with one or two failed gates: 1.
- Threshold variants are post-freeze diagnostics only; they do not create a new child freeze.

## Threshold Variants On Post-Freeze Rows

| variant | p floor | drawdown max | rows | known | helpful | harmful | unknown | known delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `frozen_rule` | 0.600000 | 10.000000 | 1 | 1 | 1 | 0 | 0 | 60c |
| `drawdown_lte_12p5_same_p` | 0.600000 | 12.500000 | 1 | 1 | 1 | 0 | 0 | 60c |
| `p_hold_ge_055_same_drawdown` | 0.550000 | 10.000000 | 1 | 1 | 1 | 0 | 0 | 60c |
| `drawdown_lte_12p5_p_hold_ge055` | 0.550000 | 12.500000 | 2 | 1 | 1 | 0 | 1 | 60c |

## Selected Rows

| market | side | current | hold | delta | p hold | p margin | drawdown | drawdown margin | exit | failure |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `KXBTC15M-26MAY070830-30` | no | -14c | 46c | 60c | 0.825354 | 0.225354 | -0.535395 | 10.535395 | mushroom_v28_exit_value_over_hold | exit_policy_cost |

## Near Misses

| market | side | current | hold | delta | p hold | p margin | drawdown | drawdown margin | failed gates | failure |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `KXBTC15M-26MAY070015-15` | no | -2c | n/a | n/a | 0.596562 | -0.003438 | 10.343815 | -0.343815 | p_hold_below_floor, fair_drawdown_above_ceiling | exited_unsettled |
