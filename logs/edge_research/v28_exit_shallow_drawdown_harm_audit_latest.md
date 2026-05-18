# v28 Exit Shallow-Drawdown Harm Audit

Research-only diagnostic; no live bot changes or orders.

- Generated UTC: `2026-05-07T05:53:46.984573+00:00`
- Base reduce freeze UTC: `2026-05-06T06:33:56.987999+00:00`
- Denominator rows: `99`
- Base selected/helpful/harmful: `25/23/2`
- Base selected delta: `1149.000c`

## Interpretation

- Diagnostic only; every rule here was chosen after seeing known outcomes.
- Clean child rules are candidates for separate frozen watches only if the physical mechanism is defensible.
- Promotion still requires strict post-freeze rows, positive delta, no harmful loss-control cost, and enough cushion.

## Best Clean Child Rule

| field | value |
|---|---:|
| rule | `duration_sec le 52` |
| selected | 16 |
| helpful/harmful | 16/0 |
| selected delta c | 1031.000 |
| total delta c | 1031.000 |
| loss cost c | 0 |
| blockers | `diagnostic_prefreeze` |

## Best Tradeoff Child Rule

| field | value |
|---|---:|
| rule | `duration_sec le 52` |
| selected | 16 |
| helpful/harmful | 16/0 |
| selected delta c | 1031.000 |
| total delta c | 1031.000 |
| loss cost c | 0 |
| blockers | `diagnostic_prefreeze` |

## Top Clean Child Rules

| rule | selected | helpful | harmful | selected delta c | total delta c | reasons |
|---|---:|---:|---:|---:|---:|---|
| `duration_sec le 52` | 16 | 16 | 0 | 1031.000 | 1031.000 | {'mushroom_v28_probability_reduce': 13, 'mushroom_v28_probability_collapse_full': 3} |
| `duration_sec le 52 and exit_cents ge 50` | 16 | 16 | 0 | 1031.000 | 1031.000 | {'mushroom_v28_probability_reduce': 13, 'mushroom_v28_probability_collapse_full': 3} |
| `duration_sec le 52 and exit_cents le 80` | 16 | 16 | 0 | 1031.000 | 1031.000 | {'mushroom_v28_probability_reduce': 13, 'mushroom_v28_probability_collapse_full': 3} |
| `duration_sec le 52 and entry_depth ge 2` | 16 | 16 | 0 | 1031.000 | 1031.000 | {'mushroom_v28_probability_reduce': 13, 'mushroom_v28_probability_collapse_full': 3} |
| `duration_sec le 52 and exit_cents le 75` | 15 | 15 | 0 | 985.000 | 985.000 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_collapse_full': 3} |
| `duration_sec le 52 and entry_cents le 80` | 15 | 15 | 0 | 979.000 | 979.000 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_collapse_full': 3} |
| `duration_sec le 52 and exit_sigma_t_dollars le 150` | 15 | 15 | 0 | 961.000 | 961.000 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_collapse_full': 3} |
| `exit_cents le 70` | 13 | 13 | 0 | 928.000 | 928.000 | {'mushroom_v28_probability_reduce': 10, 'mushroom_v28_probability_collapse_full': 3} |
| `exit_cents le 70 and entry_cents le 80` | 13 | 13 | 0 | 928.000 | 928.000 | {'mushroom_v28_probability_reduce': 10, 'mushroom_v28_probability_collapse_full': 3} |
| `exit_cents le 70 and entry_depth ge 2` | 13 | 13 | 0 | 928.000 | 928.000 | {'mushroom_v28_probability_reduce': 10, 'mushroom_v28_probability_collapse_full': 3} |
| `duration_sec le 52 and entry_abs_d_sigma le 1` | 14 | 14 | 0 | 913.000 | 913.000 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_collapse_full': 2} |
| `entry_seconds_to_close le 596` | 14 | 14 | 0 | 883.000 | 883.000 | {'mushroom_v28_probability_reduce': 12, 'mushroom_v28_probability_collapse_full': 2} |

## Harmful Base Examples

| market | side | result | reason | current | hold | delta | p_hold | drawdown | entry | exit | duration |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY060700-00 | no | yes | mushroom_v28_probability_reduce | -8.000 | -168.000 | -160.000 | 0.800 | 4.040 | 84 | 80 | 113.345 |
| KXBTC15M-26MAY060900-00 | yes | no | mushroom_v28_probability_reduce | -10.000 | -156.000 | -146.000 | 0.790 | -0.999 | 78 | 73 | 56.623 |
