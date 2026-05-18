# v28 Boundary-Clock Feature-Gate Coverage/Source Frontier

Research-only audit; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:00:45.985877+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- This is an audit surface only; source labels are not used for selection and no row is promotable from this scan.
- post_feature_freeze_entry: no observable rule clears net/coverage/source gates together; best Pareto row raw03_recross60_abs85_ask35 has 52/82 entries, coverage 63.41463414634146%, net 514.0c, recon 0.1346153846153846.
- post_feature_freeze_bridge: no observable rule clears net/coverage/source gates together; best Pareto row raw03_recross60_abs85_ask35 has 52/82 entries, coverage 63.41463414634146%, net 514.0c, recon 0.1346153846153846.

## post_feature_freeze_entry

- Future denominator: `82`
- Scanned observable variants: `144`

### Clean Broad Positive Rules

- None.

### Pareto Frontier

| rule | selected/den | W/L | coverage | net c | recon | cushion | tags | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| raw03_recross60_abs85_ask35 | 52/82 | 48/4 | 63.414634 | 514.000000 | 0.134615 | 5 | positive_net, source_clean | coverage_too_low |
| raw03_recross70_abs85_ask35 | 52/82 | 48/4 | 63.414634 | 514.000000 | 0.134615 | 5 | positive_net, source_clean | coverage_too_low |
| raw05_recross60_abs85_ask35 | 47/82 | 43/4 | 57.317073 | 471.000000 | 0.042553 | 4 | positive_net, source_clean | coverage_too_low |
| raw05_recross70_abs85_ask35 | 47/82 | 43/4 | 57.317073 | 471.000000 | 0.042553 | 4 | positive_net, source_clean | coverage_too_low |
| raw03_recross60_abs85_asknone | 62/82 | 43/19 | 75.609756 | 469.000000 | 0.354839 | 4 | target_coverage, positive_net | reconstructed_share_gt_35pct |
| raw03_recross70_abs85_asknone | 62/82 | 43/19 | 75.609756 | 469.000000 | 0.354839 | 4 | target_coverage, positive_net | reconstructed_share_gt_35pct |
| raw05_recross60_abs85_asknone | 55/82 | 39/16 | 67.073171 | 445.000000 | 0.272727 | 4 | positive_net, source_clean | coverage_too_low |
| raw05_recross70_abs85_asknone | 55/82 | 39/16 | 67.073171 | 445.000000 | 0.272727 | 4 | positive_net, source_clean | coverage_too_low |
| raw07_recross60_abs85_ask35 | 32/82 | 29/3 | 39.024390 | 397.000000 | 0.031250 | 3 | positive_net, source_clean | coverage_too_low |
| raw07_recross70_abs85_ask35 | 32/82 | 29/3 | 39.024390 | 397.000000 | 0.031250 | 3 | positive_net, source_clean | coverage_too_low |
| raw03_recross60_abs75_ask35 | 54/82 | 48/6 | 65.853659 | 392.000000 | 0.185185 | 3 | positive_net, source_clean | coverage_too_low |
| raw03_recross70_abs75_ask35 | 54/82 | 48/6 | 65.853659 | 392.000000 | 0.185185 | 3 | positive_net, source_clean | coverage_too_low |

### Top By Gate Sort

| rule | selected/den | W/L | coverage | net c | recon | cushion | tags | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| raw03_recross60_abs85_ask35 | 52/82 | 48/4 | 63.414634 | 514.000000 | 0.134615 | 5 | positive_net, source_clean | coverage_too_low |
| raw03_recross70_abs85_ask35 | 52/82 | 48/4 | 63.414634 | 514.000000 | 0.134615 | 5 | positive_net, source_clean | coverage_too_low |
| raw03_recross50_abs85_ask35 | 52/82 | 48/4 | 63.414634 | 489.000000 | 0.173077 | 4 | positive_net, source_clean | coverage_too_low |
| raw05_recross60_abs85_ask35 | 47/82 | 43/4 | 57.317073 | 471.000000 | 0.042553 | 4 | positive_net, source_clean | coverage_too_low |
| raw05_recross70_abs85_ask35 | 47/82 | 43/4 | 57.317073 | 471.000000 | 0.042553 | 4 | positive_net, source_clean | coverage_too_low |
| raw03_recross60_abs85_asknone | 62/82 | 43/19 | 75.609756 | 469.000000 | 0.354839 | 4 | target_coverage, positive_net | reconstructed_share_gt_35pct |
| raw03_recross70_abs85_asknone | 62/82 | 43/19 | 75.609756 | 469.000000 | 0.354839 | 4 | target_coverage, positive_net | reconstructed_share_gt_35pct |
| raw07_recross60_abs85_asknone | 38/82 | 29/9 | 46.341463 | 454.000000 | 0.210526 | 4 | positive_net, source_clean | coverage_too_low |
| raw07_recross70_abs85_asknone | 38/82 | 29/9 | 46.341463 | 454.000000 | 0.210526 | 4 | positive_net, source_clean | coverage_too_low |
| raw05_recross60_abs85_asknone | 55/82 | 39/16 | 67.073171 | 445.000000 | 0.272727 | 4 | positive_net, source_clean | coverage_too_low |
| raw05_recross70_abs85_asknone | 55/82 | 39/16 | 67.073171 | 445.000000 | 0.272727 | 4 | positive_net, source_clean | coverage_too_low |
| raw03_recross50_abs85_asknone | 62/82 | 43/19 | 75.609756 | 444.000000 | 0.387097 | 4 | target_coverage, positive_net | reconstructed_share_gt_35pct |

## post_feature_freeze_bridge

- Future denominator: `82`
- Scanned observable variants: `144`

### Clean Broad Positive Rules

- None.

### Pareto Frontier

| rule | selected/den | W/L | coverage | net c | recon | cushion | tags | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| raw03_recross60_abs85_ask35 | 52/82 | 48/4 | 63.414634 | 514.000000 | 0.134615 | 5 | positive_net, source_clean | coverage_too_low |
| raw03_recross70_abs85_ask35 | 52/82 | 48/4 | 63.414634 | 514.000000 | 0.134615 | 5 | positive_net, source_clean | coverage_too_low |
| raw05_recross60_abs85_ask35 | 47/82 | 43/4 | 57.317073 | 471.000000 | 0.042553 | 4 | positive_net, source_clean | coverage_too_low |
| raw05_recross70_abs85_ask35 | 47/82 | 43/4 | 57.317073 | 471.000000 | 0.042553 | 4 | positive_net, source_clean | coverage_too_low |
| raw03_recross60_abs85_asknone | 62/82 | 43/19 | 75.609756 | 469.000000 | 0.354839 | 4 | target_coverage, positive_net | reconstructed_share_gt_35pct |
| raw03_recross70_abs85_asknone | 62/82 | 43/19 | 75.609756 | 469.000000 | 0.354839 | 4 | target_coverage, positive_net | reconstructed_share_gt_35pct |
| raw05_recross60_abs85_asknone | 55/82 | 39/16 | 67.073171 | 445.000000 | 0.272727 | 4 | positive_net, source_clean | coverage_too_low |
| raw05_recross70_abs85_asknone | 55/82 | 39/16 | 67.073171 | 445.000000 | 0.272727 | 4 | positive_net, source_clean | coverage_too_low |
| raw07_recross60_abs85_ask35 | 32/82 | 29/3 | 39.024390 | 397.000000 | 0.031250 | 3 | positive_net, source_clean | coverage_too_low |
| raw07_recross70_abs85_ask35 | 32/82 | 29/3 | 39.024390 | 397.000000 | 0.031250 | 3 | positive_net, source_clean | coverage_too_low |
| raw03_recross60_abs75_ask35 | 54/82 | 48/6 | 65.853659 | 392.000000 | 0.185185 | 3 | positive_net, source_clean | coverage_too_low |
| raw03_recross70_abs75_ask35 | 54/82 | 48/6 | 65.853659 | 392.000000 | 0.185185 | 3 | positive_net, source_clean | coverage_too_low |

### Top By Gate Sort

| rule | selected/den | W/L | coverage | net c | recon | cushion | tags | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| raw03_recross60_abs85_ask35 | 52/82 | 48/4 | 63.414634 | 514.000000 | 0.134615 | 5 | positive_net, source_clean | coverage_too_low |
| raw03_recross70_abs85_ask35 | 52/82 | 48/4 | 63.414634 | 514.000000 | 0.134615 | 5 | positive_net, source_clean | coverage_too_low |
| raw03_recross50_abs85_ask35 | 52/82 | 48/4 | 63.414634 | 489.000000 | 0.173077 | 4 | positive_net, source_clean | coverage_too_low |
| raw05_recross60_abs85_ask35 | 47/82 | 43/4 | 57.317073 | 471.000000 | 0.042553 | 4 | positive_net, source_clean | coverage_too_low |
| raw05_recross70_abs85_ask35 | 47/82 | 43/4 | 57.317073 | 471.000000 | 0.042553 | 4 | positive_net, source_clean | coverage_too_low |
| raw03_recross60_abs85_asknone | 62/82 | 43/19 | 75.609756 | 469.000000 | 0.354839 | 4 | target_coverage, positive_net | reconstructed_share_gt_35pct |
| raw03_recross70_abs85_asknone | 62/82 | 43/19 | 75.609756 | 469.000000 | 0.354839 | 4 | target_coverage, positive_net | reconstructed_share_gt_35pct |
| raw07_recross60_abs85_asknone | 38/82 | 29/9 | 46.341463 | 454.000000 | 0.210526 | 4 | positive_net, source_clean | coverage_too_low |
| raw07_recross70_abs85_asknone | 38/82 | 29/9 | 46.341463 | 454.000000 | 0.210526 | 4 | positive_net, source_clean | coverage_too_low |
| raw05_recross60_abs85_asknone | 55/82 | 39/16 | 67.073171 | 445.000000 | 0.272727 | 4 | positive_net, source_clean | coverage_too_low |
| raw05_recross70_abs85_asknone | 55/82 | 39/16 | 67.073171 | 445.000000 | 0.272727 | 4 | positive_net, source_clean | coverage_too_low |
| raw03_recross50_abs85_asknone | 62/82 | 43/19 | 75.609756 | 444.000000 | 0.387097 | 4 | target_coverage, positive_net | reconstructed_share_gt_35pct |
