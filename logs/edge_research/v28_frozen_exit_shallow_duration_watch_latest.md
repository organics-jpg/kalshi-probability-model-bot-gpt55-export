# v28 Frozen Exit Shallow-Duration Watch

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T10:41:52.456272+00:00`
- Freeze UTC: `2026-05-07T05:55:14.530870+00:00`
- Candidate: `shallow_drawdown_duration_lte52_reduce_or_collapse`
- Diagnostic origin: `duration_sec le 52` selected 16 with 16/0 helpful/harmful and 1031.0c.
- Physics: A shallow FV drawdown within roughly one minute of entry is more likely mark/path churn clipping a still-live thesis than true settlement-odds failure.

## Interpretation

- Research-only frozen watch; this does not change live exits or promote a candidate.
- Diagnostic lane confirms why the child was frozen, but does not count as promotion evidence.
- Strict post-birth rows must prove the rule with no harmful loss-control cost.

## diagnostic_from_reduce_freeze

- Freeze UTC: `2026-05-06T06:33:56.987999+00:00`
- Rows: `100`

| settled | current c | candidate c | delta c | W/L current | W/L candidate | suppressed | helpful/harmful | loss cost c | cushion | blockers |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 100 | 289.000 | 1320.000 | 1031.000 | 55/45 | 70/30 | 16 | 16/0 | 0 | 13 | suppressed_decisions_lt_30, diagnostic_prefreeze |

## post_shallow_duration_birth

- Freeze UTC: `2026-05-07T05:55:14.530870+00:00`
- Rows: `1`

| settled | current c | candidate c | delta c | W/L current | W/L candidate | suppressed | helpful/harmful | loss cost c | cushion | blockers |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 18.000 | 18.000 | 0.000 | 1/0 | 1/0 | 0 | 0/0 | 0 | 0 | settled_lt_30, suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |

## Best Strict Forward

- Settled/suppressed: `1/0`
- Delta: `0.000c`
- Blockers: `['settled_lt_30', 'suppressed_decisions_lt_30', 'delta_not_positive', 'full_loss_cushion_lt_3']`
