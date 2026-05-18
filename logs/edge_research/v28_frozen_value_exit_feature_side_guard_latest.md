# v28 Frozen Value Exit Feature-Side Guard

Research-only frozen watch. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:55:00.957220+00:00`
- Freeze UTC: `2026-05-07T07:42:49.442068+00:00`
- Candidate: `value_only_gap15_or_p75_feature_gate_same_side`
- Rule: `Apply the value_only_gap15_or_p75 exit suppression only when the feature-gate selected side for the same market equals the live position side.`

## Interpretation

- Research-only frozen watch; no live bot changes or orders.
- Post-birth has 33 rows, feature-side-guard net 388.0c, W/L 21/12.
- The guard is observable, but evidence starts from this watch timestamp and cannot promote until forward rows settle.

## Lanes

| lane | rows | current c | value-only c | guarded c | guarded delta current c | guarded delta value c | guarded W/L | guarded suppressed | guarded sup W/L | guarded sup loser cost c | value-only suppressed | value-only loser cost c | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_prefreeze_context` | 87 | 277.00 | 327.00 | 383.00 | 106.00 | 56.00 | 49/38 | 10 | 10/0 | 0 | 25 | -180.00 | 3 | exit_overlap_only, not_live_bot_logic |
| `post_feature_side_guard_birth` | 33 | 450.00 | 460.00 | 388.00 | -62.00 | -72.00 | 21/12 | 9 | 8/1 | -170.00 | 12 | -170.00 | 3 | exit_overlap_only, not_live_bot_logic |

## Suppressed-Loser Attribution

The guarded suppressed-loser fields count only exits actually suppressed by the feature-side guard. The value-only fields preserve the parent value-exit diagnostic that the guard is filtering.
