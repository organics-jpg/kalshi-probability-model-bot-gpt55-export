# v28 Hybrid/Boundary Entry Stack Source Stress

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T00:48:30.421404+00:00`
- Stack generated UTC: `2026-05-10T02:42:45.995846+00:00`
- Stack freeze UTC: `2026-05-06T15:37:04.750154+00:00`

## Interpretation

- This is the formal source-stress audit for the combined stack; it is not promotion evidence by itself.
- diagnostic_existing_target_window: all_three_with_boundary_fv_edge_approved_first_hybrid_edge_repair has 114 settled, coverage 75.0%, net 803.0c, reconstructed share 0.5; needs 49 clean rows for source, 0 rows for sample, and 0.0c for cushion; blockers ['reconstructed_share_gt_35pct'].
- post_stack_freeze_window: hybrid_veto_plus_boundary_clock_approved_only_hybrid_edge_repair has 41 settled, coverage 47.12643678160919%, net 312.0c, reconstructed share 0.7073170731707317; needs 42 clean rows for source, 0 rows for sample, and 0.0c for cushion; blockers ['reconstructed_share_gt_35pct'].

## Lanes

| window | candidate | settled | coverage | net c | W/L | recon share | approved/recon | source rows needed | sample rows needed | cushion c needed | max full losses positive | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| diagnostic_existing_target_window | all_three_with_boundary_fv_edge_approved_first_hybrid_edge_repair | 114 | 75.000000 | 803.000000 | 83/31 | 0.500000 | 57/57 | 49 | 0 | 0.000000 | 8 | reconstructed_share_gt_35pct |
| post_stack_freeze_window | hybrid_veto_plus_boundary_clock_approved_only_hybrid_edge_repair | 41 | 47.126437 | 312.000000 | 27/14 | 0.707317 | 12/29 | 42 | 0 | 0.000000 | 3 | reconstructed_share_gt_35pct |

## Source Split: diagnostic_existing_target_window

| source | rows | W/L | net c | avg c |
|---|---:|---:|---:|---:|
| approved_entry | 57 | 49/8 | 537.000000 | 9.421053 |
| rejected_actionable | 57 | 34/23 | 266.000000 | 4.666667 |

## Source Split: post_stack_freeze_window

| source | rows | W/L | net c | avg c |
|---|---:|---:|---:|---:|
| approved_entry | 12 | 10/2 | 55.000000 | 4.583333 |
| rejected_actionable | 29 | 17/12 | 257.000000 | 8.862069 |
