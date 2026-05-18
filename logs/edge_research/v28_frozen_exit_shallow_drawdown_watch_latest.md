# v28 Frozen Exit Shallow-Drawdown Watch

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T10:41:51.277504+00:00`
- Freeze UTC: `2026-05-07T05:50:24.685661+00:00`
- Source rounded rule: `fair_drawdown_cents le 5`

## Interpretation

- Research-only frozen watch; this does not change live exits or promote a candidate.
- Diagnostic lane uses rows after the older reduce-exit freeze only for mechanism context.
- Only post_shallow_drawdown_birth rows count as strict forward evidence.

## diagnostic_from_reduce_freeze

- Freeze UTC: `2026-05-06T06:33:56.987999+00:00`
- Strict forward: `False`
- Rows: `100`

| policy | settled | current c | candidate c | delta c | W/L current | W/L candidate | suppressed | helpful/harmful | loss cost c | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| shallow_drawdown_any_exit_lte5 | 100 | 289.000 | 1576.000 | 1287.000 | 55/45 | 74/26 | 57 | 52/3 | -486.000 | 15 | suppressed_losers_present, suppressed_loss_control_cost_negative, diagnostic_prefreeze |
| shallow_drawdown_reduce_or_collapse_lte5 | 100 | 289.000 | 1438.000 | 1149.000 | 55/45 | 75/25 | 25 | 23/2 | -306.000 | 14 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, diagnostic_prefreeze |
| shallow_drawdown_reduce_or_collapse_lte5_p_hold60 | 100 | 289.000 | 1340.000 | 1051.000 | 55/45 | 74/26 | 24 | 22/2 | -306.000 | 13 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, diagnostic_prefreeze |
| shallow_drawdown_reduce_only_lte5 | 100 | 289.000 | 1108.000 | 819.000 | 55/45 | 72/28 | 21 | 19/2 | -306.000 | 11 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, diagnostic_prefreeze |
| shallow_drawdown_collapse_only_lte5 | 100 | 289.000 | 619.000 | 330.000 | 55/45 | 58/42 | 4 | 4/0 | 0 | 6 | suppressed_decisions_lt_30, diagnostic_prefreeze |

## post_shallow_drawdown_birth

- Freeze UTC: `2026-05-07T05:50:24.685661+00:00`
- Strict forward: `True`
- Rows: `1`

| policy | settled | current c | candidate c | delta c | W/L current | W/L candidate | suppressed | helpful/harmful | loss cost c | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| shallow_drawdown_any_exit_lte5 | 1 | 18.000 | 36.000 | 18.000 | 1/0 | 1/0 | 1 | 1/0 | 0 | 0 | settled_lt_30, suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| shallow_drawdown_collapse_only_lte5 | 1 | 18.000 | 18.000 | 0.000 | 1/0 | 1/0 | 0 | 0/0 | 0 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| shallow_drawdown_reduce_only_lte5 | 1 | 18.000 | 18.000 | 0.000 | 1/0 | 1/0 | 0 | 0/0 | 0 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| shallow_drawdown_reduce_or_collapse_lte5 | 1 | 18.000 | 18.000 | 0.000 | 1/0 | 1/0 | 0 | 0/0 | 0 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |
| shallow_drawdown_reduce_or_collapse_lte5_p_hold60 | 1 | 18.000 | 18.000 | 0.000 | 1/0 | 1/0 | 0 | 0/0 | 0 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |

## Best Strict Forward

- Policy: `shallow_drawdown_any_exit_lte5`
- Settled/suppressed: `1/1`
- Delta: `18.000c`
- Blockers: `['settled_lt_30', 'suppressed_decisions_lt_30', 'full_loss_cushion_lt_3']`
