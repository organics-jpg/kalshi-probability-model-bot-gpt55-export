# v28 Feature-Gate Cheap-Tail Quarantine

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T04:45:40.416935+00:00`
- Quarantine freeze UTC: `2026-05-06T22:43:55.071320+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- Core rules are judged as broad-entry candidates; cheap-tail rules are judged only as sidecars.
- Cheap-tail rows are not allowed to repair core coverage in this report.
- diagnostic_feature_window_entry: best core core_raw03_recross50_abs65_ask35 has 29 settled, coverage 68.18181818181819%, net 237.0c, blockers ['settled_lt_30', 'coverage_too_low', 'full_loss_cushion_lt_3']; best tail tail_raw05_recross50_abs85_asklt35 has 13 settled, net 39.0c, blockers ['settled_lt_30', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3', 'top_win_concentration_ge_50pct_net'].
- diagnostic_feature_window_bridge: best core core_raw03_recross50_abs65_ask35 has 21 settled, coverage 68.18181818181819%, net 210.0c, blockers ['settled_lt_30', 'coverage_too_low', 'full_loss_cushion_lt_3']; best tail tail_raw05_recross50_abs85_asklt35 has 13 settled, net 39.0c, blockers ['settled_lt_30', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3', 'top_win_concentration_ge_50pct_net'].
- post_quarantine_freeze_entry: best core core_raw03_recross50_abs65_ask35 has 14 settled, coverage 79.16666666666667%, net 155.0c, blockers ['settled_lt_30', 'full_loss_cushion_lt_3']; best tail tail_raw05_recross50_abs85_asklt35 has 6 settled, net -28.0c, blockers ['settled_lt_30', 'net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- post_quarantine_freeze_bridge: best core core_raw03_recross50_abs65_ask35 has 15 settled, coverage 79.16666666666667%, net 36.0c, blockers ['settled_lt_30', 'full_loss_cushion_lt_3', 'top_win_concentration_ge_50pct_net']; best tail tail_raw05_recross50_abs85_asklt35 has 6 settled, net -28.0c, blockers ['settled_lt_30', 'net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].

## diagnostic_feature_window_entry

### Core Rules

| rule | settled/den | W/L | coverage | net c | recon | cushion | top win | net ex top | ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `core_raw03_recross50_abs65_ask35` | 29/44 | 25/4 | 68.181818 | 237.000000 | 0.200000 | 2 | 56.000000 | 181.000000 | False | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |
| `core_raw05_recross60_abs085_ask65` | 24/44 | 21/3 | 56.818182 | 116.000000 | 0.040000 | 1 | 33.000000 | 83.000000 | False | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |
| `core_raw03_recross50_abs65_ask50` | 27/44 | 23/4 | 63.636364 | 115.000000 | 0.178571 | 1 | 37.000000 | 78.000000 | False | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |

### Cheap-Tail Sidecar Rules

| rule | settled/den | W/L | coverage | net c | recon | cushion | top win | net ex top | ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `tail_raw05_recross50_abs85_asklt35` | 13/44 | 1/12 | 29.545455 | 39.000000 | 1.000000 | 0 | 96.000000 | -57.000000 | False | settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3, top_win_concentration_ge_50pct_net |
| `tail_raw03_recross50_abs75_asklt35` | 17/44 | 1/16 | 38.636364 | 12.000000 | 1.000000 | 0 | 96.000000 | -84.000000 | False | settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3, top_win_concentration_ge_50pct_net |

## diagnostic_feature_window_bridge

### Core Rules

| rule | settled/den | W/L | coverage | net c | recon | cushion | top win | net ex top | ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `core_raw03_recross50_abs65_ask35` | 21/44 | 18/3 | 68.181818 | 210.000000 | 0.200000 | 2 | 56.000000 | 154.000000 | False | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |
| `core_raw05_recross60_abs085_ask65` | 16/44 | 14/2 | 56.818182 | 89.000000 | 0.040000 | 0 | 31.000000 | 58.000000 | False | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |
| `core_raw03_recross50_abs65_ask50` | 19/44 | 16/3 | 63.636364 | 88.000000 | 0.178571 | 0 | 37.000000 | 51.000000 | False | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3 |

### Cheap-Tail Sidecar Rules

| rule | settled/den | W/L | coverage | net c | recon | cushion | top win | net ex top | ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `tail_raw05_recross50_abs85_asklt35` | 13/44 | 1/12 | 29.545455 | 39.000000 | 1.000000 | 0 | 96.000000 | -57.000000 | False | settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3, top_win_concentration_ge_50pct_net |
| `tail_raw03_recross50_abs75_asklt35` | 17/44 | 1/16 | 38.636364 | 12.000000 | 1.000000 | 0 | 96.000000 | -84.000000 | False | settled_lt_30, reconstructed_share_gt_35pct, full_loss_cushion_lt_3, top_win_concentration_ge_50pct_net |

## post_quarantine_freeze_entry

### Core Rules

| rule | settled/den | W/L | coverage | net c | recon | cushion | top win | net ex top | ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `core_raw03_recross50_abs65_ask35` | 14/24 | 12/2 | 79.166667 | 155.000000 | 0.210526 | 1 | 56.000000 | 99.000000 | False | settled_lt_30, full_loss_cushion_lt_3 |
| `core_raw03_recross50_abs65_ask50` | 13/24 | 10/3 | 75.000000 | -9.000000 | 0.222222 | 0 | 37.000000 | -46.000000 | False | settled_lt_30, net_not_positive, full_loss_cushion_lt_3 |
| `core_raw05_recross60_abs085_ask65` | 11/24 | 9/2 | 66.666667 | 12.000000 | 0.062500 | 0 | 33.000000 | -21.000000 | False | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, top_win_concentration_ge_50pct_net |

### Cheap-Tail Sidecar Rules

| rule | settled/den | W/L | coverage | net c | recon | cushion | top win | net ex top | ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `tail_raw05_recross50_abs85_asklt35` | 6/24 | 0/6 | 25.000000 | -28.000000 | 1.000000 | 0 | -2.000000 | -26.000000 | False | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `tail_raw03_recross50_abs75_asklt35` | 10/24 | 0/10 | 41.666667 | -55.000000 | 1.000000 | 0 | -2.000000 | -53.000000 | False | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

## post_quarantine_freeze_bridge

### Core Rules

| rule | settled/den | W/L | coverage | net c | recon | cushion | top win | net ex top | ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `core_raw03_recross50_abs65_ask35` | 15/24 | 12/3 | 79.166667 | 36.000000 | 0.210526 | 0 | 56.000000 | -20.000000 | False | settled_lt_30, full_loss_cushion_lt_3, top_win_concentration_ge_50pct_net |
| `core_raw03_recross50_abs65_ask50` | 14/24 | 10/4 | 75.000000 | -128.000000 | 0.222222 | 0 | 37.000000 | -165.000000 | False | settled_lt_30, net_not_positive, full_loss_cushion_lt_3 |
| `core_raw05_recross60_abs085_ask65` | 11/24 | 8/3 | 66.666667 | -123.000000 | 0.062500 | 0 | 18.000000 | -141.000000 | False | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |

### Cheap-Tail Sidecar Rules

| rule | settled/den | W/L | coverage | net c | recon | cushion | top win | net ex top | ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `tail_raw05_recross50_abs85_asklt35` | 6/24 | 0/6 | 25.000000 | -28.000000 | 1.000000 | 0 | -2.000000 | -26.000000 | False | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| `tail_raw03_recross50_abs75_asklt35` | 10/24 | 0/10 | 41.666667 | -55.000000 | 1.000000 | 0 | -2.000000 | -53.000000 | False | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
