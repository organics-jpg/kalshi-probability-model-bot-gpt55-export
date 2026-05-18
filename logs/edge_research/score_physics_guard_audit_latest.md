# Score Physics Guard Audit

Generated UTC: `20260504_135926Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Tests a small, predeclared set of simple physics guards on high-coverage score/book priors.
- Strict diagnostic pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.

## Combined Read

| candidate | robust | combined net | OOS net | current/v21 net | current/v21 acc | current/v21 cov | min block+ | worst block |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `score_m60_edge_m5` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__touch_loss_rv_15m_le_0p95` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__touch_loss_rv_15m_le_0p9` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__touch_loss_rv_15m_le_0p85` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__touch_loss_rv_15m_le_0p8` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p25` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__brownian_p_rv_15m_ge_0p6` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__abs_book_rv15_gap_le_0p2` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__abs_book_rv15_gap_le_0p3` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__abs_book_rv15_gap_le_0p3` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__abs_book_rv15_gap_le_0p3` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__abs_book_rv15_gap_le_0p3` | False | 2317.0c | 988.0c | 1439.0c/878.0c | 76.07%/76.32% | 95.61%/85.97% | 54.55% | -248.0c |
| `score_m60_edge_m5__adverse_move_15m_le_50` | False | 2160.0c | 850.0c | 1426.0c/734.0c | 76.67%/76.34% | 94.04%/84.16% | 45.45% | -287.0c |
| `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__adverse_move_15m_le_50` | False | 2160.0c | 850.0c | 1426.0c/734.0c | 76.67%/76.34% | 94.04%/84.16% | 45.45% | -287.0c |
| `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__adverse_move_15m_le_50` | False | 2160.0c | 850.0c | 1426.0c/734.0c | 76.67%/76.34% | 94.04%/84.16% | 45.45% | -287.0c |
| `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__adverse_move_15m_le_50` | False | 2160.0c | 850.0c | 1426.0c/734.0c | 76.67%/76.34% | 94.04%/84.16% | 45.45% | -287.0c |
| `score_m60_edge_m5__rv_sigma_t_15m_le_100` | False | 2150.0c | 1551.0c | 1224.0c/926.0c | 77.37%/77.98% | 85.89%/76.02% | 45.45% | -252.0c |
| `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__rv_sigma_t_15m_le_100` | False | 2150.0c | 1551.0c | 1224.0c/926.0c | 77.37%/77.98% | 85.89%/76.02% | 45.45% | -252.0c |
| `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__rv_sigma_t_15m_le_100` | False | 2150.0c | 1551.0c | 1224.0c/926.0c | 77.37%/77.98% | 85.89%/76.02% | 45.45% | -252.0c |
| `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | False | 2150.0c | 1551.0c | 1224.0c/926.0c | 77.37%/77.98% | 85.89%/76.02% | 45.45% | -252.0c |
| `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__adverse_move_15m_le_50` | False | 2134.0c | 819.0c | 1442.0c/692.0c | 77.00%/76.34% | 94.04%/84.16% | 45.45% | -291.0c |
| `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | False | 2090.0c | 1314.0c | 1232.0c/858.0c | 77.74%/77.84% | 85.89%/75.57% | 45.45% | -252.0c |
| `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p6` | False | 2076.0c | 748.0c | 1398.0c/678.0c | 76.32%/75.66% | 95.30%/85.52% | 54.55% | -276.0c |
| `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55` | False | 2048.0c | 748.0c | 1351.0c/697.0c | 76.07%/75.66% | 95.61%/85.52% | 54.55% | -276.0c |
| `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__abs_book_rv15_gap_le_0p3` | False | 2048.0c | 748.0c | 1351.0c/697.0c | 76.07%/75.66% | 95.61%/85.52% | 54.55% | -276.0c |
| `score_m60__drift_p_5m_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | False | 1916.0c | 1479.0c | 1324.0c/592.0c | 77.66%/76.38% | 91.22%/90.05% | 45.45% | -276.0c |
| `score_m60__rv_sigma_t_15m_le_100` | False | 1884.0c | 1754.0c | 1062.0c/822.0c | 76.45%/77.23% | 91.85%/91.40% | 62.50% | -348.0c |
| `score_m60__touch_loss_rv_15m_le_0p9__rv_sigma_t_15m_le_100` | False | 1884.0c | 1754.0c | 1062.0c/822.0c | 76.45%/77.23% | 91.85%/91.40% | 62.50% | -348.0c |

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | median edge | coverage | all splits | OOS |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|
| current | `score_m60__drift_p_5m_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | 1324.0c/6.22% | 77.66%/91.22% | 552.0c | 309.0c | 463.0c | -3.6c | False | True | True |
| v21 | `score_m60__drift_p_5m_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | 592.0c/4.05% | 76.38%/90.05% | -115.0c | 552.0c | 155.0c | -3.0c | True | False | True |
| current | `score_m60__rv_sigma_t_15m_le_100` | 1062.0c/4.98% | 76.45%/91.85% | 141.0c | 365.0c | 556.0c | -3.9c | False | True | True |
| v21 | `score_m60__rv_sigma_t_15m_le_100` | 822.0c/5.56% | 77.23%/91.40% | -11.0c | 583.0c | 250.0c | -3.0c | True | False | True |
| current | `score_m60__touch_loss_rv_15m_le_0p9__rv_sigma_t_15m_le_100` | 1062.0c/4.98% | 76.45%/91.85% | 141.0c | 365.0c | 556.0c | -3.9c | False | True | True |
| v21 | `score_m60__touch_loss_rv_15m_le_0p9__rv_sigma_t_15m_le_100` | 822.0c/5.56% | 77.23%/91.40% | -11.0c | 583.0c | 250.0c | -3.0c | True | False | True |
| current | `score_m60_edge_m5` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__abs_book_rv15_gap_le_0p2` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5__abs_book_rv15_gap_le_0p2` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__abs_book_rv15_gap_le_0p3` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5__abs_book_rv15_gap_le_0p3` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__adverse_move_15m_le_50` | 1426.0c/6.61% | 76.67%/94.04% | 1215.0c | 172.0c | 39.0c | -2.5c | True | True | True |
| v21 | `score_m60_edge_m5__adverse_move_15m_le_50` | 734.0c/5.45% | 76.34%/84.16% | 95.0c | 452.0c | 187.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__abs_book_rv15_gap_le_0p3` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__abs_book_rv15_gap_le_0p3` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__adverse_move_15m_le_50` | 1426.0c/6.61% | 76.67%/94.04% | 1215.0c | 172.0c | 39.0c | -2.5c | True | True | True |
| v21 | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__adverse_move_15m_le_50` | 734.0c/5.45% | 76.34%/84.16% | 95.0c | 452.0c | 187.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | 1224.0c/6.13% | 77.37%/85.89% | 446.0c | 331.0c | 447.0c | -2.5c | False | True | True |
| v21 | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | 926.0c/7.61% | 77.98%/76.02% | 153.0c | 478.0c | 295.0c | -2.5c | False | True | True |
| current | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p6` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p6` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55` | 1351.0c/6.18% | 76.07%/95.61% | 1191.0c | 148.0c | 12.0c | -2.6c | True | True | True |
| v21 | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55` | 697.0c/5.12% | 75.66%/85.52% | 109.0c | 394.0c | 194.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__abs_book_rv15_gap_le_0p3` | 1351.0c/6.18% | 76.07%/95.61% | 1191.0c | 148.0c | 12.0c | -2.6c | True | True | True |
| v21 | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__abs_book_rv15_gap_le_0p3` | 697.0c/5.12% | 75.66%/85.52% | 109.0c | 394.0c | 194.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__adverse_move_15m_le_50` | 1442.0c/6.66% | 77.00%/94.04% | 1263.0c | 140.0c | 39.0c | -2.5c | True | True | True |
| v21 | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__adverse_move_15m_le_50` | 692.0c/5.12% | 76.34%/84.16% | 52.0c | 453.0c | 187.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | 1232.0c/6.14% | 77.74%/85.89% | 591.0c | 287.0c | 354.0c | -2.5c | False | True | True |
| v21 | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | 858.0c/7.07% | 77.84%/75.57% | 185.0c | 479.0c | 194.0c | -2.5c | False | True | True |
| current | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p6` | 1398.0c/6.41% | 76.32%/95.30% | 1238.0c | 148.0c | 12.0c | -2.6c | True | True | True |
| v21 | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p6` | 678.0c/4.98% | 75.66%/85.52% | 90.0c | 394.0c | 194.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__abs_book_rv15_gap_le_0p3` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__abs_book_rv15_gap_le_0p3` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__adverse_move_15m_le_50` | 1426.0c/6.61% | 76.67%/94.04% | 1215.0c | 172.0c | 39.0c | -2.5c | True | True | True |
| v21 | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__adverse_move_15m_le_50` | 734.0c/5.45% | 76.34%/84.16% | 95.0c | 452.0c | 187.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__rv_sigma_t_15m_le_100` | 1224.0c/6.13% | 77.37%/85.89% | 446.0c | 331.0c | 447.0c | -2.5c | False | True | True |
| v21 | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__rv_sigma_t_15m_le_100` | 926.0c/7.61% | 77.98%/76.02% | 153.0c | 478.0c | 295.0c | -2.5c | False | True | True |
| current | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p25` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p25` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__rv_sigma_t_15m_le_100` | 1224.0c/6.13% | 77.37%/85.89% | 446.0c | 331.0c | 447.0c | -2.5c | False | True | True |
| v21 | `score_m60_edge_m5__rv_sigma_t_15m_le_100` | 926.0c/7.61% | 77.98%/76.02% | 153.0c | 478.0c | 295.0c | -2.5c | False | True | True |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p8` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p8` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p85` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p85` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p95` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p95` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__abs_book_rv15_gap_le_0p3` | 1439.0c/6.61% | 76.07%/95.61% | 1139.0c | 192.0c | 108.0c | -2.7c | True | True | True |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__abs_book_rv15_gap_le_0p3` | 878.0c/6.45% | 76.32%/85.97% | 190.0c | 393.0c | 295.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__adverse_move_15m_le_50` | 1426.0c/6.61% | 76.67%/94.04% | 1215.0c | 172.0c | 39.0c | -2.5c | True | True | True |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__adverse_move_15m_le_50` | 734.0c/5.45% | 76.34%/84.16% | 95.0c | 452.0c | 187.0c | -2.5c | True | True | True |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__rv_sigma_t_15m_le_100` | 1224.0c/6.13% | 77.37%/85.89% | 446.0c | 331.0c | 447.0c | -2.5c | False | True | True |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__rv_sigma_t_15m_le_100` | 926.0c/7.61% | 77.98%/76.02% | 153.0c | 478.0c | 295.0c | -2.5c | False | True | True |

## Block Summary

| dataset | candidate | blocks | positive+coverage blocks | worst block |
|---|---|---:|---:|---:|
| current | `score_m60__drift_p_5m_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | 16 | 68.75% | -243.0c |
| current | `score_m60__rv_sigma_t_15m_le_100` | 16 | 62.50% | -348.0c |
| current | `score_m60__touch_loss_rv_15m_le_0p9__rv_sigma_t_15m_le_100` | 16 | 62.50% | -348.0c |
| current | `score_m60_edge_m5` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__abs_book_rv15_gap_le_0p2` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__abs_book_rv15_gap_le_0p3` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__adverse_move_15m_le_50` | 16 | 68.75% | -241.0c |
| current | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__abs_book_rv15_gap_le_0p3` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__adverse_move_15m_le_50` | 16 | 68.75% | -241.0c |
| current | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | 16 | 62.50% | -252.0c |
| current | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p6` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55` | 16 | 75.00% | -233.0c |
| current | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__abs_book_rv15_gap_le_0p3` | 16 | 75.00% | -233.0c |
| current | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__adverse_move_15m_le_50` | 16 | 68.75% | -241.0c |
| current | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | 16 | 62.50% | -252.0c |
| current | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p6` | 16 | 75.00% | -233.0c |
| current | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__abs_book_rv15_gap_le_0p3` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__adverse_move_15m_le_50` | 16 | 68.75% | -241.0c |
| current | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__rv_sigma_t_15m_le_100` | 16 | 62.50% | -252.0c |
| current | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p25` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__rv_sigma_t_15m_le_100` | 16 | 62.50% | -252.0c |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p8` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p85` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p95` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__abs_book_rv15_gap_le_0p3` | 16 | 75.00% | -221.0c |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__adverse_move_15m_le_50` | 16 | 68.75% | -241.0c |
| current | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__rv_sigma_t_15m_le_100` | 16 | 62.50% | -252.0c |
| v21 | `score_m60__drift_p_5m_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | 11 | 45.45% | -276.0c |
| v21 | `score_m60__rv_sigma_t_15m_le_100` | 11 | 63.64% | -271.0c |
| v21 | `score_m60__touch_loss_rv_15m_le_0p9__rv_sigma_t_15m_le_100` | 11 | 63.64% | -271.0c |
| v21 | `score_m60_edge_m5` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__abs_book_rv15_gap_le_0p2` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__abs_book_rv15_gap_le_0p3` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__adverse_move_15m_le_50` | 11 | 45.45% | -287.0c |
| v21 | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__abs_book_rv15_gap_le_0p3` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__adverse_move_15m_le_50` | 11 | 45.45% | -287.0c |
| v21 | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | 11 | 45.45% | -177.0c |
| v21 | `score_m60_edge_m5__brownian_p_rv_15m_ge_0p6` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55` | 11 | 54.55% | -276.0c |
| v21 | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__abs_book_rv15_gap_le_0p3` | 11 | 54.55% | -276.0c |
| v21 | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__adverse_move_15m_le_50` | 11 | 45.45% | -291.0c |
| v21 | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p55__rv_sigma_t_15m_le_100` | 11 | 45.45% | -215.0c |
| v21 | `score_m60_edge_m5__drift_p_5m_rv_15m_ge_0p6` | 11 | 54.55% | -276.0c |
| v21 | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__abs_book_rv15_gap_le_0p3` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__adverse_move_15m_le_50` | 11 | 45.45% | -287.0c |
| v21 | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p1__rv_sigma_t_15m_le_100` | 11 | 45.45% | -177.0c |
| v21 | `score_m60_edge_m5__margin_per_rv_sigma_15m_ge_0p25` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__rv_sigma_t_15m_le_100` | 11 | 45.45% | -177.0c |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p8` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p85` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p95` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__abs_book_rv15_gap_le_0p3` | 11 | 54.55% | -248.0c |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__adverse_move_15m_le_50` | 11 | 45.45% | -287.0c |
| v21 | `score_m60_edge_m5__touch_loss_rv_15m_le_0p9__rv_sigma_t_15m_le_100` | 11 | 45.45% | -177.0c |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask | median edge |
|---|---|---|---:|---:|---:|---:|---:|---:|
| v21 | `hazard45_touch80__margin_per_rv_sigma_15m_ge_0p5` | time=(-1.001, 600.0] | 66 | 43/23 | -785.0c | -11.9c | 76.0c | -15.3c |
| v21 | `book_margin__margin_per_rv_sigma_15m_ge_0p1__adverse_move_15m_le_50` | ask=(70.0, 80.0] | 52 | 32/20 | -765.0c | -14.7c | 74.0c | -2.5c |
| current | `book_margin__adverse_move_15m_le_10` | score=(0.625, 0.65] | 62 | 34/28 | -725.0c | -11.7c | 64.0c | -2.5c |
| v21 | `book_margin__brownian_p_rv_15m_ge_0p55__adverse_move_15m_le_50` | ask=(70.0, 80.0] | 54 | 34/20 | -717.0c | -13.3c | 74.0c | -2.5c |
| v21 | `book_margin__touch_loss_rv_15m_le_0p9__adverse_move_15m_le_50` | ask=(70.0, 80.0] | 54 | 34/20 | -717.0c | -13.3c | 74.0c | -2.5c |
| v21 | `book_margin__margin_per_rv_sigma_15m_ge_0p1` | ask=(70.0, 80.0] | 45 | 27/18 | -710.0c | -15.8c | 73.0c | -2.5c |
| v21 | `book_margin__margin_per_rv_sigma_15m_ge_0p1__abs_book_rv15_gap_le_0p3` | ask=(70.0, 80.0] | 45 | 27/18 | -710.0c | -15.8c | 73.0c | -2.5c |
| v21 | `book_margin__margin_per_rv_sigma_15m_ge_0p5` | time=(-1.001, 600.0] | 94 | 69/25 | -706.0c | -7.5c | 79.0c | -2.5c |
| v21 | `score_m60__margin_per_rv_sigma_15m_ge_0p5` | time=(-1.001, 600.0] | 94 | 69/25 | -706.0c | -7.5c | 79.0c | -3.9c |
| v21 | `book_margin__adverse_move_15m_le_50` | ask=(70.0, 80.0] | 51 | 32/19 | -688.0c | -13.5c | 74.0c | -2.5c |
| v21 | `book_margin__abs_book_rv15_gap_le_0p2` | ask=(70.0, 80.0] | 42 | 25/17 | -674.0c | -16.0c | 72.0c | -2.5c |
| v21 | `book_margin__touch_loss_rv_15m_le_0p85` | ask=(70.0, 80.0] | 51 | 32/19 | -665.0c | -13.0c | 73.0c | -2.5c |
| current | `book_margin__drift_p_5m_rv_15m_ge_0p55__abs_book_rv15_gap_le_0p3` | score=(0.625, 0.65] | 58 | 32/26 | -659.0c | -11.4c | 64.0c | -2.5c |
| current | `book_margin__adverse_move_15m_le_50` | score=(0.625, 0.65] | 64 | 36/28 | -659.0c | -10.3c | 64.0c | -2.5c |
| current | `book_margin__drift_p_5m_rv_15m_ge_0p55` | score=(0.625, 0.65] | 58 | 32/26 | -659.0c | -11.4c | 64.0c | -2.5c |
| current | `book_margin` | score=(0.625, 0.65] | 61 | 34/27 | -658.0c | -10.8c | 64.0c | -2.5c |
| v21 | `book_margin__brownian_p_rv_15m_ge_0p55__abs_book_rv15_gap_le_0p3` | ask=(70.0, 80.0] | 47 | 29/18 | -658.0c | -14.0c | 73.0c | -2.5c |
| v21 | `book_margin__touch_loss_rv_15m_le_0p9` | ask=(70.0, 80.0] | 47 | 29/18 | -658.0c | -14.0c | 73.0c | -2.5c |

## Read

- No physics-guard row clears the full robustness gate.
