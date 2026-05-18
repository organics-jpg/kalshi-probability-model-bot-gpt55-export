# v28 Feature-Gate Artifact Consistency Audit

Research-only consistency guardrail. No live bot changes or orders.

- Generated UTC: `2026-05-07T15:00:48.051403+00:00`
- Consistent for promotion discussion: `False`
- Blockers: `['broad_feature_gate_metrics_disagree', 'size_shrink_runway_metrics_disagree']`

## Interpretation

- Research-only audit; this does not score new rules, change live logic, or promote a candidate.
- Artifact consistency blockers: ['broad_feature_gate_metrics_disagree', 'size_shrink_runway_metrics_disagree'].
- Broad feature-gate mismatches: ['entries', 'settled', 'coverage_pct', 'net_cents', 'wins', 'losses', 'reconstructed_share'].
- Size-shrink runway mismatches: ['delta_vs_live_cents'].

## Broad Feature-Gate Row

| source | entries | settled | coverage | net c | W/L | recon share | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| `v28_boundary_clock_feature_gate_candidate_latest.json` | 54 | 42 | 75.000000 | 274.000000 | 26/16 | 0.370370 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `v28_boundary_clock_feature_gate_source_denominator_audit_latest.json` | 53 | 53 | 73.611111 | 365.000000 | 35/18 | 0.377358 | n/a |
| `v28_feature_gate_linked_source_runway_latest.json` | 53 | 53 | 74.647887 | 388.000000 | 35/18 | 0.377358 | coverage_too_low, reconstructed_share_gt_35pct |
| `v28_feature_gate_promotion_gap_audit_latest.json` | 54 | 42 | 75.000000 | 274.000000 | 26/16 | 0.370370 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

## Size-Shrink Row

| source | settled | coverage | weighted net c | delta vs live c | row recon share | blockers |
|---|---:|---:|---:|---:|---:|---|
| `v28_feature_gate_size_shrink_source_runway_latest.json` | 45 | 75.409836 | 369.000000 | -738.000000 | 0.413043 | row_reconstructed_share_gt_35pct |
| `v28_feature_gate_coverage_size_shrink_runway_latest.json` | 45 | 75.409836 | 369.000000 | -690.000000 | 0.413043 | row_reconstructed_share_gt_35pct |

## Mismatches

- Broad row mismatches: `[{'metric': 'entries', 'values': {'v28_boundary_clock_feature_gate_candidate_latest.json': 54, 'v28_boundary_clock_feature_gate_source_denominator_audit_latest.json': 53, 'v28_feature_gate_linked_source_runway_latest.json': 53, 'v28_feature_gate_promotion_gap_audit_latest.json': 54}}, {'metric': 'settled', 'values': {'v28_boundary_clock_feature_gate_candidate_latest.json': 42, 'v28_boundary_clock_feature_gate_source_denominator_audit_latest.json': 53, 'v28_feature_gate_linked_source_runway_latest.json': 53, 'v28_feature_gate_promotion_gap_audit_latest.json': 42}}, {'metric': 'coverage_pct', 'values': {'v28_boundary_clock_feature_gate_candidate_latest.json': 75.0, 'v28_boundary_clock_feature_gate_source_denominator_audit_latest.json': 73.61111111111111, 'v28_feature_gate_linked_source_runway_latest.json': 74.64788732394366, 'v28_feature_gate_promotion_gap_audit_latest.json': 75.0}}, {'metric': 'net_cents', 'values': {'v28_boundary_clock_feature_gate_candidate_latest.json': 274.0, 'v28_boundary_clock_feature_gate_source_denominator_audit_latest.json': 365.0, 'v28_feature_gate_linked_source_runway_latest.json': 388.0, 'v28_feature_gate_promotion_gap_audit_latest.json': 274.0}}, {'metric': 'wins', 'values': {'v28_boundary_clock_feature_gate_candidate_latest.json': 26, 'v28_boundary_clock_feature_gate_source_denominator_audit_latest.json': 35, 'v28_feature_gate_linked_source_runway_latest.json': 35, 'v28_feature_gate_promotion_gap_audit_latest.json': 26}}, {'metric': 'losses', 'values': {'v28_boundary_clock_feature_gate_candidate_latest.json': 16, 'v28_boundary_clock_feature_gate_source_denominator_audit_latest.json': 18, 'v28_feature_gate_linked_source_runway_latest.json': 18, 'v28_feature_gate_promotion_gap_audit_latest.json': 16}}, {'metric': 'reconstructed_share', 'values': {'v28_boundary_clock_feature_gate_candidate_latest.json': 0.37037037037037035, 'v28_boundary_clock_feature_gate_source_denominator_audit_latest.json': 0.37735849056603776, 'v28_feature_gate_linked_source_runway_latest.json': 0.37735849056603776, 'v28_feature_gate_promotion_gap_audit_latest.json': 0.37037037037037035}}]`
- Size-shrink mismatches: `[{'metric': 'delta_vs_live_cents', 'values': {'v28_feature_gate_size_shrink_source_runway_latest.json': -738.0, 'v28_feature_gate_coverage_size_shrink_runway_latest.json': -690.0}}]`
- Live-baseline mismatches: `[]`
