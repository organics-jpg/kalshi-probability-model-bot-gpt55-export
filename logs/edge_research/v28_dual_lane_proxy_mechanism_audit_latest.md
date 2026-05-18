# v28 Dual-Lane Proxy Mechanism Audit

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:46:04.480213+00:00`
- Preview generated UTC: `2026-05-11T03:44:26.910756+00:00`
- Freeze UTC/local: `2026-05-07T13:00:17.363339+00:00` / `2026-05-07T09:00:17.363339-04:00`
- Live baseline: `-256c ($-2.56)`

## Mechanism Read

- `sidecar_live_shadow_shape_is_constructive`
- `primary_proxy_is_all_source_quality_risk`
- `primary_proxy_is_below_sidecar_distance_band`
- `do_not_use_primary_proxy_as_live_ready_evidence`
- `own_freeze_strict_rows_remain_authoritative`

## Summary

| lane preview | entries | settled | W/L | net | avg raw edge | avg abs d | avg recross | avg ask | source counts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| sidecar exact observable | 12 | 12 | 11/1 | 304c ($3.04) | 0.083 | 0.923 | 0.369 | 0.764 | `{'approved_entry': 12}` |
| primary sizing-pocket proxy | 16 | 16 | 4/12 | -40c ($-0.40) | -0.019 | 0.652 | 0.456 | 0.263 | `{'rejected_actionable': 16}` |

## Realized PnL Sign

| lane preview | settlement W/L | PnL W/L/flat | read |
|---|---:|---:|---|
| sidecar exact observable | 11/1 | 10/2/0 | exit policy can make realized PnL differ from settlement direction |
| primary sizing-pocket proxy | 4/12 | 4/12/0 | source-quality and FV-risk proxy only |

## Primary Proxy Failure Flags

| flag | rows | share |
|---|---:|---:|
| `cheap_low_ask` | 16 | 100.00% |
| `low_distance_confidence` | 16 | 100.00% |
| `sidecar_missing_abs_d_lt_085` | 16 | 100.00% |
| `source_quality` | 16 | 100.00% |
| `cheap_side_penalty_negative` | 15 | 93.75% |
| `sidecar_missing_raw_edge_lt_05` | 14 | 87.50% |
| `negative_fv_edge` | 11 | 68.75% |
| `high_recross` | 3 | 18.75% |
| `sidecar_missing_recross_gt_60` | 3 | 18.75% |
| `weak_fv_edge` | 3 | 18.75% |

## Primary Proxy Rows

| market | source | side | won | net | raw | adjusted | recross | abs d | ask | flags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY070915-15` | rejected_actionable | yes | False | -52c ($-0.52) | -0.063 | -0.161 | 0.520 | 0.677 | 0.260 | source_quality, negative_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05 |
| `KXBTC15M-26MAY070930-30` | rejected_actionable | no | False | -52c ($-0.52) | -0.052 | -0.150 | 0.486 | 0.629 | 0.260 | source_quality, negative_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05 |
| `KXBTC15M-26MAY070945-45` | rejected_actionable | yes | False | -64c ($-0.64) | -0.124 | -0.207 | 0.532 | 0.682 | 0.320 | source_quality, negative_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05 |
| `KXBTC15M-26MAY071000-00` | rejected_actionable | yes | False | -44c ($-0.44) | -0.016 | -0.124 | 0.150 | 0.663 | 0.220 | source_quality, negative_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05 |
| `KXBTC15M-26MAY071015-15` | rejected_actionable | yes | True | 152c ($1.52) | -0.012 | -0.114 | 0.418 | 0.611 | 0.240 | source_quality, negative_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05 |
| `KXBTC15M-26MAY071030-30` | rejected_actionable | yes | False | -50c ($-0.50) | -0.051 | -0.151 | 0.728 | 0.684 | 0.250 | source_quality, negative_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, high_recross, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05, sidecar_missing_recross_gt_60 |
| `KXBTC15M-26MAY071045-45` | rejected_actionable | yes | False | -60c ($-0.60) | -0.074 | -0.161 | 0.656 | 0.634 | 0.300 | source_quality, negative_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, high_recross, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05, sidecar_missing_recross_gt_60 |
| `KXBTC15M-26MAY071100-00` | rejected_actionable | no | True | 166c ($1.66) | 0.036 | -0.084 | 0.345 | 0.685 | 0.170 | source_quality, weak_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05 |
| `KXBTC15M-26MAY071115-15` | rejected_actionable | no | False | -30c ($-0.30) | 0.029 | -0.096 | 0.114 | 0.730 | 0.150 | source_quality, weak_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05 |
| `KXBTC15M-26MAY071130-30` | rejected_actionable | yes | False | -54c ($-0.54) | -0.036 | -0.131 | 0.593 | 0.605 | 0.270 | source_quality, negative_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05 |
| `KXBTC15M-26MAY071145-45` | rejected_actionable | no | False | -56c ($-0.56) | -0.089 | -0.182 | 0.729 | 0.675 | 0.280 | source_quality, negative_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, high_recross, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05, sidecar_missing_recross_gt_60 |
| `KXBTC15M-26MAY071215-15` | rejected_actionable | yes | False | -44c ($-0.44) | 0.005 | -0.103 | 0.235 | 0.628 | 0.220 | source_quality, weak_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05 |
| `KXBTC15M-26MAY071230-30` | rejected_actionable | yes | True | 148c ($1.48) | -0.027 | -0.124 | 0.561 | 0.607 | 0.260 | source_quality, negative_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05 |
| `KXBTC15M-26MAY071300-00` | rejected_actionable | yes | False | -32c ($-0.32) | 0.069 | -0.053 | 0.147 | 0.619 | 0.160 | source_quality, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, sidecar_missing_abs_d_lt_085 |
| `KXBTC15M-26MAY071315-15` | rejected_actionable | yes | True | 74c ($0.74) | 0.120 | 0.115 | 0.557 | 0.615 | 0.630 | source_quality, low_distance_confidence, cheap_low_ask, sidecar_missing_abs_d_lt_085 |
| `KXBTC15M-26MAY071330-30` | rejected_actionable | yes | False | -42c ($-0.42) | -0.016 | -0.126 | 0.528 | 0.684 | 0.210 | source_quality, negative_fv_edge, cheap_side_penalty_negative, low_distance_confidence, cheap_low_ask, sidecar_missing_abs_d_lt_085, sidecar_missing_raw_edge_lt_05 |
