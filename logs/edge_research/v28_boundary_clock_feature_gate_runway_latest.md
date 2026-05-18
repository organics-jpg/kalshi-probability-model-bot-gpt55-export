# v28 Boundary-Clock Feature-Gate Runway

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T01:55:01.783078+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Refreshed live net: `-588c`

## Interpretation

- Feature-gate selection is observable-only; source labels remain audit-only.
- Best post-freeze lane post_feature_freeze_entry_raw03_recross70_abs075 has 64 settled row(s), 78.04878048780488% coverage, 307.0c net, reconstructed share 0.390625, and delta 895.0c versus refreshed live.
- It needs 8 future clean selected rows to satisfy sample/coverage/source gates under the all-future-selected runway assumption; average future net for a 3-full-loss cushion is -0.875c.
- No fully clean-source post-freeze feature-gate row is available yet.
- This is watch-only until >=30 settled forward rows, positive PnL, target coverage, source quality, full-loss cushion, and live readiness all pass.

## Post-Freeze Runway

| lane | candidate | settled/den | W/L | coverage | net c | delta live c | recon | approved-source cov | recon-source cov | cushion | future clean rows | avg c for cushion3 | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| post_feature_freeze_entry | post_feature_freeze_entry_raw03_recross70_abs075 | 64/82 | 42/22 | 78.048780 | 307.000000 | 895.000000 | 0.390625 | 86.666667 | 30.487805 | 3 | 8 | -0.875000 | reconstructed_share_gt_35pct |
| post_feature_freeze_bridge | post_feature_freeze_bridge_raw03_recross70_abs075 | 64/82 | 42/22 | 78.048780 | 307.000000 | 895.000000 | 0.390625 | 86.666667 | 30.487805 | 3 | 8 | -0.875000 | reconstructed_share_gt_35pct |
| post_feature_freeze_entry | post_feature_freeze_entry_raw05_recross60_abs085 | 55/82 | 39/16 | 67.073171 | 445.000000 | 1033.000000 | 0.272727 | 88.888889 | 18.292683 | 4 | 26 | -5.576923 | coverage_too_low |
| post_feature_freeze_bridge | post_feature_freeze_bridge_raw05_recross60_abs085 | 55/82 | 39/16 | 67.073171 | 445.000000 | 1033.000000 | 0.272727 | 88.888889 | 18.292683 | 4 | 26 | -5.576923 | coverage_too_low |
| post_feature_freeze_entry | post_feature_freeze_entry_raw05_recross60_abs085_ask65 | 47/82 | 42/5 | 57.317073 | 344.000000 | 932.000000 | 0.042553 | 100.000000 | 2.439024 | 3 | 58 | -0.758621 | coverage_too_low |
| post_feature_freeze_bridge | post_feature_freeze_bridge_raw05_recross60_abs085_ask65 | 47/82 | 42/5 | 57.317073 | 344.000000 | 932.000000 | 0.042553 | 100.000000 | 2.439024 | 3 | 58 | -0.758621 | coverage_too_low |
| post_feature_freeze_entry | post_feature_freeze_entry_raw07_recross60_abs085 | 38/82 | 29/9 | 46.341463 | 454.000000 | 1042.000000 | 0.210526 | 66.666667 | 9.756098 | 4 | 94 | -1.638298 | coverage_too_low |
| post_feature_freeze_bridge | post_feature_freeze_bridge_raw07_recross60_abs085 | 38/82 | 29/9 | 46.341463 | 454.000000 | 1042.000000 | 0.210526 | 66.666667 | 9.756098 | 4 | 94 | -1.638298 | coverage_too_low |

## Clean-Source Post-Freeze Runway

- No clean-source post-freeze rows yet.

## Diagnostic Reference

| lane | candidate | settled/den | W/L | coverage | net c | delta live c | recon | approved-source cov | recon-source cov | cushion | future clean rows | avg c for cushion3 | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| diagnostic_entry | diagnostic_entry_raw03_recross70_abs075 | 100/121 | 72/28 | 82.644628 | 725.000000 | 1313.000000 | 0.320000 | None | None | 7 | 0 | None | none |
| diagnostic_bridge | diagnostic_bridge_raw03_recross70_abs075 | 98/119 | 71/27 | 82.352941 | 717.000000 | 1305.000000 | 0.326531 | None | None | 7 | 0 | None | none |
| diagnostic_entry | diagnostic_entry_raw05_recross60_abs085 | 86/121 | 67/19 | 71.074380 | 859.000000 | 1447.000000 | 0.197674 | None | None | 8 | 19 | -29.421053 | coverage_too_low |
| diagnostic_bridge | diagnostic_bridge_raw05_recross60_abs085 | 84/119 | 66/18 | 70.588235 | 851.000000 | 1439.000000 | 0.202381 | None | None | 8 | 21 | -26.238095 | coverage_too_low |
| diagnostic_entry | diagnostic_entry_raw07_recross60_abs085 | 60/121 | 49/11 | 49.586777 | 836.000000 | 1424.000000 | 0.150000 | None | None | 8 | 123 | -4.357724 | coverage_too_low |
| diagnostic_bridge | diagnostic_bridge_raw07_recross60_abs085 | 58/119 | 48/10 | 48.739496 | 828.000000 | 1416.000000 | 0.155172 | None | None | 8 | 125 | -4.224000 | coverage_too_low |
| diagnostic_entry | diagnostic_entry_raw05_recross60_abs085_ask65 | 78/121 | 71/7 | 64.462810 | 775.000000 | 1363.000000 | 0.051282 | None | None | 7 | 51 | -9.313725 | coverage_too_low |
| diagnostic_bridge | diagnostic_bridge_raw05_recross60_abs085_ask65 | 76/119 | 69/7 | 63.865546 | 738.000000 | 1326.000000 | 0.052632 | None | None | 7 | 53 | -8.264151 | coverage_too_low |
