# v28 Boundary-Clock Feature-Gate Frontier Runway

Research-only audit; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:27:37.813615+00:00`
- Frontier generated UTC: `2026-05-11T02:00:45.985877+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- This is a runway audit of the current frontier row, not a promotion candidate or threshold search.
- post_feature_freeze_entry: best frontier raw03_recross60_abs85_ask35 is 52/82 entries, net 514.0c, reconstructed share 0.1346153846153846; needs 38 clean selected row(s) for coverage, 0 for source, 0 settled row(s) for sample, and 0.0c for a three-full-loss cushion.
- post_feature_freeze_bridge: best frontier raw03_recross60_abs85_ask35 is 52/82 entries, net 514.0c, reconstructed share 0.1346153846153846; needs 38 clean selected row(s) for coverage, 0 for source, 0 settled row(s) for sample, and 0.0c for a three-full-loss cushion.

## Runway

| lane | rule | entries/den | settled | W/L | net c | recon | blockers | clean rows for cov | clean rows for source | rows for sample | net c for cushion | clean rows all gates at avg | projected cov | projected recon | projected net c |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| post_feature_freeze_entry | raw03_recross60_abs85_ask35 | 52/82 | 52 | 48/4 | 514.000000 | 0.134615 | coverage_too_low | 38 | 0 | 0 | 0.000000 | 38 | 75.000000 | 0.077778 | 889.615385 |
| post_feature_freeze_bridge | raw03_recross60_abs85_ask35 | 52/82 | 52 | 48/4 | 514.000000 | 0.134615 | coverage_too_low | 38 | 0 | 0 | 0.000000 | 38 | 75.000000 | 0.077778 | 889.615385 |
