# v28 Boundary-Clock Source Stress

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T18:16:28.589597+00:00`

## Interpretation

- boundary_clock_repair_entry: 91 settled, coverage 75.20661157024793%, net -151.0c, reconstructed share 0.7142857142857143, clean rows needed for sample/source gate 95, blockers ['net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- boundary_clock_fv_entry_bridge: 90 settled, coverage 75.63025210084034%, net 229.0c, reconstructed share 0.7888888888888889, clean rows needed for sample/source gate 113, blockers ['reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- Boundary-clock remains promising but thin: one full-loss row can erase current positive PnL.

## Lane Summary

| lane | settled | coverage | net c | W/L | recon share | source counts | repair counts | clean rows to gate | full-loss cushion | blockers |
|---|---:|---:|---:|---:|---:|---|---|---:|---:|---|
| boundary_clock_repair_entry | 91 | 75.206612 | -151.000000 | 58/33 | 0.714286 | {'rejected_actionable': 65, 'approved_entry': 26} | {'approved_entry': 21, 'rejected_actionable': 19} | 95 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| boundary_clock_fv_entry_bridge | 90 | 75.630252 | 229.000000 | 55/35 | 0.788889 | {'rejected_actionable': 71, 'approved_entry': 19} | {'approved_entry': 14, 'rejected_actionable': 17} | 113 | 2 | reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

## boundary_clock_repair_entry Source Split

| slice | source | entries | settled | W/L | coverage | net c | avg c |
|---|---|---:|---:|---:|---:|---:|---:|
| candidate | approved_entry | 26 | 26 | 23/3 | 21.487603 | 244.000000 | 9.384615 |
| candidate | rejected_actionable | 65 | 65 | 35/30 | 53.719008 | -395.000000 | -6.076923 |
| repairs | approved_entry | 21 | 21 | 18/3 | 17.355372 | 146.000000 | 6.952381 |
| repairs | rejected_actionable | 19 | 19 | 9/10 | 15.702479 | -368.000000 | -19.368421 |
| removed | rejected_actionable | 38 | 38 | 18/20 | 31.404959 | -570.000000 | -15.000000 |

## boundary_clock_repair_entry Full-Loss Runway

| added full losses | stressed settled | stressed net c | still positive |
|---:|---:|---:|---|
| 1 | 92 | -251.000000 | False |
| 2 | 93 | -351.000000 | False |
| 3 | 94 | -451.000000 | False |
| 4 | 95 | -551.000000 | False |
| 5 | 96 | -651.000000 | False |

## boundary_clock_fv_entry_bridge Source Split

| slice | source | entries | settled | W/L | coverage | net c | avg c |
|---|---|---:|---:|---:|---:|---:|---:|
| candidate | approved_entry | 19 | 19 | 15/4 | 15.966387 | 7.000000 | 0.368421 |
| candidate | rejected_actionable | 71 | 71 | 40/31 | 59.663866 | 222.000000 | 3.126761 |
| repairs | approved_entry | 14 | 14 | 10/4 | 11.764706 | -91.000000 | -6.500000 |
| repairs | rejected_actionable | 17 | 17 | 9/8 | 14.285714 | -241.000000 | -14.176471 |
| removed | rejected_actionable | 28 | 28 | 13/15 | 23.529412 | -862.000000 | -30.785714 |

## boundary_clock_fv_entry_bridge Full-Loss Runway

| added full losses | stressed settled | stressed net c | still positive |
|---:|---:|---:|---|
| 1 | 91 | 129.000000 | True |
| 2 | 92 | 29.000000 | True |
| 3 | 93 | -71.000000 | False |
| 4 | 94 | -171.000000 | False |
| 5 | 95 | -271.000000 | False |
