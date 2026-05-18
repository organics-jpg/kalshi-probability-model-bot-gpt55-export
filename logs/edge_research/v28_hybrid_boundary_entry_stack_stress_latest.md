# v28 Hybrid/Boundary Entry Stack Stress

Research-only; no live bot changes or orders.

- Stack freeze UTC: `2026-05-06T15:37:04.750154+00:00`
- Source stack artifact: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_hybrid_boundary_entry_stack_latest.json`

## Interpretation

- Best diagnostic broad-positive variant is all_three_with_boundary_fv_edge_approved_first_hybrid_edge_repair with net 803.0c, coverage 75.0%, reconstructed share 0.5.
- Lowest-reconstructed broad-positive variant is all_three_with_boundary_fv_edge_approved_first_hybrid_edge_repair with net 803.0c and reconstructed share 0.5.
- No diagnostic broad-positive variant clears the strict <=35% reconstructed-share gate yet.
- Keep testing, but do not promote: the edge is promising and source-quality limited.

## Diagnostic Picks

| pick | candidate | settled | coverage | net c | recon share | loss cushion | blockers |
|---|---|---:|---:|---:|---:|---:|---|
| best_pnl | all_three_with_boundary_fv_edge_approved_first_hybrid_edge_repair | 114 | 75.000000 | 803.000000 | 0.500000 | 8 | reconstructed_share_gt_35pct |
| best_watch_source | None | None | None | None | None | None | none |
| lowest_recon | all_three_with_boundary_fv_edge_approved_first_hybrid_edge_repair | 114 | 75.000000 | 803.000000 | 0.500000 | 8 | reconstructed_share_gt_35pct |

## Post-Freeze Picks

| pick | candidate | settled | coverage | net c | recon share | loss cushion | blockers |
|---|---|---:|---:|---:|---:|---:|---|
| best_pnl | hybrid_veto_plus_boundary_clock_hybrid_edge_repair | 66 | 75.862069 | 173.000000 | 0.666667 | 1 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| best_watch_source | None | None | None | None | None | None | none |
| lowest_recon | all_three_with_boundary_fv_edge_hybrid_edge_repair | 66 | 75.862069 | 88.000000 | 0.636364 | 0 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

## Diagnostic Family Best

| family | candidate | settled | coverage | net c | recon share | blockers |
|---|---|---:|---:|---:|---:|---|
| all_three | all_three_with_boundary_fv_edge_approved_first_hybrid_edge_repair | 114 | 75.000000 | 803.000000 | 0.500000 | reconstructed_share_gt_35pct |
| early_no_plus_boundary_clock | early_no_plus_boundary_clock_approved_first_hybrid_edge_repair | 114 | 75.000000 | 731.000000 | 0.526316 | reconstructed_share_gt_35pct |
| hybrid_veto_plus_early_no | hybrid_veto_plus_early_no_approved_first_hybrid_edge_repair | 114 | 75.000000 | 596.000000 | 0.517544 | reconstructed_share_gt_35pct |
| hybrid_veto_plus_boundary_clock | hybrid_veto_plus_boundary_clock_approved_first_raw_clean_repair | 114 | 75.000000 | 307.000000 | 0.552632 | reconstructed_share_gt_35pct |

## Full-Loss Runway

| lane | added full losses | stressed settled | stressed net c | still positive |
|---|---:|---:|---:|---|
| best_pnl | 1 | 115 | 703.000000 | True |
| best_pnl | 2 | 116 | 603.000000 | True |
| best_pnl | 3 | 117 | 503.000000 | True |
| best_pnl | 4 | 118 | 403.000000 | True |
| best_pnl | 5 | 119 | 303.000000 | True |
| best_pnl | 6 | 120 | 203.000000 | True |
| best_pnl | 7 | 121 | 103.000000 | True |
