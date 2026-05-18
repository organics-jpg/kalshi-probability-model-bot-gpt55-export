# v28 False-Conviction Family Scorecard

Research-only; no live bot changes and no orders.

## Direction

- Lead with early boundary/high-recross false-conviction filtering, not broad FV sharpening.
- Best forward target-coverage evidence is false_conviction_fv_entry_bridge with settled 70, net 762.0c, coverage 75.26881720430107.
- Goldilocks edge is promising only as a diagnostic: 63.0c net at 75.40983606557377% coverage, but frozen future rows are 48.
- FV-entry bridge approved-only diagnostic support is 321.0c net on 70 settled rows; this is weaker than the all-source/reconstructed read and remains non-promotable.
- No false-conviction family candidate currently clears integrity gates.

## Candidates

| candidate | mode | settled | W/L | coverage | net c | delta c | recon share | loss cushion | pass | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `false_conviction_fv_entry_bridge` | `fv_bridge_diagnostic_plus_frozen` | 70 | 48/22 | 75.268817 | 762.000000 | 1172.000000 | 0.914286 | None | False | reconstructed_share_gt_35pct, full_loss_cushion_unknown |
| `early_no_boundary_decay_repair` | `frozen_forward_stress` | 85 | 56/29 | 75.221239 | 27.000000 | 84.000000 | 0.694118 | 0 | False | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `composite_false_conviction_repair` | `frozen_forward_stress` | 83 | 55/28 | 75.454545 | -84.000000 | -184.000000 | 0.662651 | 0 | False | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `goldilocks_edge_repair` | `diagnostic_plus_frozen` | 48 | 30/18 | 75.384615 | -90.000000 | -310.000000 | 0.938776 | 0 | False | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `false_conviction_approved_repair` | `frozen_forward_source_quality` | 70 | 45/25 | 75.268817 | -226.000000 | None | None | None | False | net_not_positive, source_mix_unknown, full_loss_cushion_unknown |
| `mid_edge_boundary_deception_repair` | `frozen_forward` | 84 | 50/34 | 75.000000 | -431.000000 | -486.000000 | None | None | False | net_not_positive, source_mix_unknown, full_loss_cushion_unknown |
| `target_loss_tag_repair` | `frozen_forward` | 86 | 50/36 | 75.438596 | -731.000000 | -588.000000 | None | None | False | net_not_positive, source_mix_unknown, full_loss_cushion_unknown |

## Diagnostic-Only Notes

- `false_conviction_fv_entry_bridge` diagnostic: settled `85`, net `304.000000c`, coverage `75.221239`, delta `782.000000c`, recon share `0.858824`.
  - label: `first_eligible_top75_escape_energy+escape_edge8_or_p70_or_far_edge4+false_zone_to_book`
  - calibration deltas: brier `-0.041738`, logloss `-0.093192`
  - source quality `diagnostic_approved_only`: settled `70`, net `321.000000c`, coverage `61.946903`, recon share `0.000000`, blockers `coverage_too_low`
  - source quality `diagnostic_all_sources`: settled `91`, net `-407.000000c`, coverage `80.530973`, recon share `0.912088`, blockers `net_not_positive, reconstructed_share_gt_35pct`
  - source quality `post_freeze_approved_only`: settled `51`, net `241.000000c`, coverage `54.838710`, recon share `0.000000`, blockers `coverage_too_low`
  - source quality `post_freeze_all_sources`: settled `75`, net `-765.000000c`, coverage `80.645161`, recon share `0.893333`, blockers `net_not_positive, reconstructed_share_gt_35pct`
  - warning: Bridge diagnostic is direction-only; post-freeze window must mature before promotion.
  - warning: Best diagnostic bridge row: first_eligible_top75_escape_energy+escape_edge8_or_p70_or_far_edge4+false_zone_to_book
- `goldilocks_edge_repair` diagnostic: settled `92`, net `63.000000c`, coverage `75.409836`, delta `495.000000c`, recon share `0.934783`.
  - warning: All avoided danger rows are reconstructed rejected-actionable rows so far.
  - warning: 39 repair rows are reconstructed.
  - warning: Two ordinary full losses would erase current positive net.
