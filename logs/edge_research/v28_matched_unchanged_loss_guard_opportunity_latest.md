# v28 Matched-Unchanged Loss Guard Opportunity

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T13:33:51.425496+00:00`
- Freeze UTC: `2026-05-07T09:30:07.471830+00:00`
- Rule: `{'abs_d_sigma_max': 0.888798, 'eligible_depth_max': 326.6, 'exit_cents_min': 51.0, 'exit_p_hold_min': 0.718799}`
- Post-freeze scored rows: `4`
- Selected rows: `0`
- Near-miss rows: `3`
- Post current/hold/delta: `84.000000/192.000000/108.000000c`
- Selected hold delta: `0c`
- Near-miss hold delta: `48.000000c`
- Fail reasons: `{'abs_d_sigma_above_max': 3, 'eligible_depth_above_max': 3, 'exit_p_hold_below_min': 1, 'missing_exit_cents': 1, 'missing_exit_p_hold': 1}`
- Blockers: `post_rows_lt_30, selected_rows_lt_30, rule_has_not_fired, selected_delta_not_positive`

## Interpretation

- Research-only opportunity audit; no live bot logic changes or orders.
- Post-freeze has 4 scored rows and 0 selected rows. This is still a no-fire watch, not a failed positive/negative rule.
- Near-miss rows with one or two failed rule gates: 3, combined hold delta 48.0c.

## Near Misses

| market | side/result | current | hold | delta | exit | p_hold | abs d | depth | failed gates |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| `KXBTC15M-26MAY070745-45` | yes/yes | 34.000000 | 64.000000 | 30.000000 | exit_trigger@85.000000 | 0.821701 | 1.081343 | 1155.700000 | abs_d_sigma_above_max, eligible_depth_above_max |
| `KXBTC15M-26MAY070830-30` | no/no | 18.000000 | 36.000000 | 18.000000 | exit_trigger@91.000000 | 0.825354 | 0.951073 | 1230.200000 | abs_d_sigma_above_max, eligible_depth_above_max |
| `KXBTC15M-26MAY070830-30` | no/no | 46.000000 | 46.000000 | 0.000000 | @None | None | 0.865277 | 10.000000 | missing_exit_cents, missing_exit_p_hold |
