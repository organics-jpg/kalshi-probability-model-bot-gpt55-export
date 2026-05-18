# v28 Frozen Exit Reduce Drift-Guard Watch

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:07:56.371776+00:00`
- Guard freeze UTC: `2026-05-07T02:30:19.536047+00:00`
- Base reduce freeze UTC: `2026-05-06T06:33:56.987999+00:00`

## Interpretation

- This is a frozen research watch only; it does not change live exits.
- Diagnostic rows reuse the old reduce-suppression freeze only to classify the mechanism.
- Only post_drift_guard_birth rows after this probe's own freeze timestamp count as forward evidence.
- Best diagnostic policy is two_regime_drift_guard with delta 515.0c and blockers ['suppressed_decisions_lt_30', 'suppressed_losers_present', 'suppressed_loss_control_cost_negative'].
- Best post-birth policy is high_p_favorable_fv with 40 settled rows, 1 suppressions, delta 46.0c, and blockers ['suppressed_decisions_lt_30'].

## Diagnostic Since Base Reduce Freeze

| policy | settled | suppressed | W/L suppressed | current c | candidate c | delta c | suppressed delta c | loss cost c | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `two_regime_drift_guard` | 132 | 13 | 12/1 | 721.000000 | 1236.000000 | 515.000000 | 515.000000 | -146.000000 | 12 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| `entry_band_moderate_drawdown` | 132 | 11 | 10/1 | 721.000000 | 1105.000000 | 384.000000 | 384.000000 | -146.000000 | 11 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| `diagnostic_blanket_p75_control` | 132 | 25 | 20/5 | 721.000000 | 1058.000000 | 337.000000 | 337.000000 | -730.000000 | 10 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| `high_p_favorable_fv` | 132 | 5 | 5/0 | 721.000000 | 998.000000 | 277.000000 | 277.000000 | 0 | 9 | suppressed_decisions_lt_30 |
| `mid_p_moderate_drawdown` | 132 | 8 | 7/1 | 721.000000 | 959.000000 | 238.000000 | 238.000000 | -146.000000 | 9 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |

## Strict Post Drift-Guard Birth

| policy | settled | suppressed | W/L suppressed | current c | candidate c | delta c | suppressed delta c | loss cost c | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `high_p_favorable_fv` | 40 | 1 | 1/0 | 510.000000 | 556.000000 | 46.000000 | 46.000000 | 0 | 5 | suppressed_decisions_lt_30 |
| `two_regime_drift_guard` | 40 | 4 | 3/1 | 510.000000 | 510.000000 | 0.000000 | 0.000000 | -146.000000 | 5 | suppressed_decisions_lt_30, suppressed_delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative |
| `diagnostic_blanket_p75_control` | 40 | 8 | 6/2 | 510.000000 | 504.000000 | -6.000000 | -6.000000 | -304.000000 | 5 | suppressed_decisions_lt_30, suppressed_delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative |
| `entry_band_moderate_drawdown` | 40 | 3 | 2/1 | 510.000000 | 464.000000 | -46.000000 | -46.000000 | -146.000000 | 4 | suppressed_decisions_lt_30, suppressed_delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative |
| `mid_p_moderate_drawdown` | 40 | 3 | 2/1 | 510.000000 | 464.000000 | -46.000000 | -46.000000 | -146.000000 | 4 | suppressed_decisions_lt_30, suppressed_delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative |

## Best Post-Birth Suppressed Rows

| market | side | result | exit_ts | p_hold | drawdown | current c | hold c | delta c | worst mark |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY071315-15 | yes | yes | 2026-05-07T17:10:38.168558+00:00 | 0.798341 | -0.834147 | -6.000000 | 40.000000 | 46.000000 | 28 |
