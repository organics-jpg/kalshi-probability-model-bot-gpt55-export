# v28 Weak-Reversal Residual Repair

Research-only; no live bot changes and no orders.

## Interpretation

- Weak-reversal base net is -1020.0c at 75.0% coverage.
- Best residual repair is weak_reversal_skip_recross_65_80_repair_farthest_boundary with net -181.0c at 73.02631578947368% coverage.
- The repair improves damage if positive delta, but is still not live-promotable unless net becomes positive and forward-robust.
- Best leave-one-market worst net is -322.0c with 111 negative exclusions.
- This is discovery-only; any skip tag must be frozen before promotion.

## Ranked Variants

| policy | entries | settled | W/L | coverage | net c | delta c | skipped net | repair net | LOO worst | neg excl | repaired |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| weak_reversal_skip_recross_65_80_repair_farthest_boundary | 111 | 111 | 73/38 | 73.026316 | -181.000000 | 839.000000 | -1073.000000 | -236.000000 | -322.000000 | 111 | False |
| weak_reversal_skip_stc_gte850_repair_farthest_boundary | 102 | 102 | 62/40 | 67.105263 | -673.000000 | 347.000000 | -581.000000 | -236.000000 | -814.000000 | 102 | False |
| weak_reversal_skip_ask_55_65_repair_farthest_boundary | 103 | 103 | 63/40 | 67.763158 | -703.000000 | 317.000000 | -551.000000 | -236.000000 | -844.000000 | 103 | False |
| weak_reversal_skip_edge_5_8pp_no_repair_farthest_boundary | 114 | 114 | 68/46 | 75.000000 | -1014.000000 | 6.000000 | -152.000000 | -148.000000 | -1155.000000 | 114 | True |
| weak_reversal_skip_edge_5_8pp_rejected_repair_farthest_boundary | 114 | 114 | 68/46 | 75.000000 | -1089.000000 | -69.000000 | -77.000000 | -148.000000 | -1230.000000 | 114 | True |
| weak_reversal_skip_edge_5_8pp_repair_farthest_boundary | 114 | 114 | 65/49 | 75.000000 | -1204.000000 | -184.000000 | -87.000000 | -273.000000 | -1345.000000 | 114 | True |
