# Paired Sidecar Slice Lock Comparison

- generated_utc: `2026-05-18T18:30:17+00:00`
- promotion_allowed: `False`
- report_count: `5`
- promotion_safe_count: `0`
- particle_like_count: `3`
- particle_edge_candidate_count: `0`
- best_selected_pnl_hypothesis_id: `v28_control_time_gt_600s_v1`
- best_selected_pnl_cents: `1516.5`
- best_v28_brier_delta_hypothesis_id: `v28_control_candidate_v28_gap_05_15pp_v1`
- best_v28_brier_delta: `0.000000`

## Rows

| hypothesis | model | rows/markets | selected | pnl c | top EV c | Brier | logloss | dBrier vs v28 | dLogloss vs v28 | dPnL vs v28 | particle edge | safe |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `blend_v28_w20_time_gt_600s_v1` | `blend_v28_online_lr010_w20` | `432` / `24` | `177` | `450.5` | `448.5` | `0.220332` | `0.621517` | `0.003889` | `0.014658` | `-1289.200000` | `False` | `False` |
| `blend_v28_w05_time_gt_600s_v1` | `blend_v28_online_lr010_w05` | `378` / `21` | `144` | `1460.0` | `355.0` | `0.241920` | `0.667182` | `0.000368` | `0.001691` | `-56.500000` | `False` | `False` |
| `v28_control_time_gt_600s_v1` | `v28` | `378` / `21` | `153` | `1516.5` | `748.0` | `0.241552` | `0.665491` | `` | `` | `` | `False` | `False` |
| `blend_v28_w15_candidate_v28_gap_05_15pp_v1` | `blend_v28_online_lr010_w15` | `35` / `14` | `14` | `-31.7` | `67.8` | `0.219018` | `0.618332` | `0.001253` | `0.004535` | `-25.000000` | `False` | `False` |
| `v28_control_candidate_v28_gap_05_15pp_v1` | `v28` | `35` / `14` | `16` | `-6.7` | `-64.2` | `0.217766` | `0.613796` | `0.000000` | `0.000000` | `0.000000` | `False` | `False` |

## Conclusion

Positive locked-slice PnL exists, but no particle-like lock beats v28 on Brier, log-loss, selected PnL, top-EV PnL, and promotion gates. Positive rows: blend_v28_w20_time_gt_600s_v1, blend_v28_w05_time_gt_600s_v1, v28_control_time_gt_600s_v1.

This report is diagnostic only and never authorizes live trading.
