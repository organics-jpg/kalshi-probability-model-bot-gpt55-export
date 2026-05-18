# Paired Sidecar Slice OOS Report

- generated_utc: `2026-05-13T02:02:11+00:00`
- hypothesis_id: `blend_v28_w05_time_gt_600s_v1`
- evaluation_scope: `locked_forward_shadow`
- locked_after_utc: `2026-05-12T16:06:50+00:00`
- model: `blend_v28_online_lr010_w05`
- slice: `time_to_close_band=600s_plus`
- promotion_allowed: `False`
- promotion_safe: `False`
- fresh_candidate_rows / markets: `432` / `24`
- slice_rows / markets: `378` / `21`
- selected_count: `144`
- selected_pnl_cents: `1460.0`
- top_ev_bucket_pnl_cents: `355.0`

## Gate Results

| gate | passed |
| --- | ---: |
| enough_fresh_candidate_rows | `True` |
| enough_fresh_markets | `True` |
| enough_slice_rows | `True` |
| enough_slice_markets | `True` |
| enough_selected | `True` |
| positive_selected_pnl | `True` |
| positive_avg_pnl | `True` |
| positive_ev_rank | `True` |
| positive_top_ev_bucket | `True` |
| positive_selected_market_share | `False` |
| positive_top_ev_market_share | `False` |
| beats_baseline_brier | `False` |
| beats_baseline_logloss | `False` |
| beats_baseline_selected_pnl | `True` |
| locked_forward_scope | `True` |
| all_passed | `False` |

## Metrics

| model | rows | markets | brier | logloss | selected_count | selected_pnl_c | top_ev_pnl_c | ev_rank_corr | pos_selected_mkts | pos_top_mkts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| blend_v28_online_lr010_w05 | 378 | 21 | 0.241920 | 0.667182 | 144 | 1460.0 | 355.0 | 0.142425 | 10/21 | 4/21 |
| v28 | 378 | 21 | 0.241552 | 0.665491 | 153 | 1516.5 | 748.0 | 0.148303 | 10/21 | 5/21 |
| market_side_ask | 378 | 21 | 0.246910 | 0.685793 | 0 | 0.0 | -1352.0 | -0.032510 | 0/21 | 3/21 |
| candle_brownian | 378 | 21 | 0.232011 | 0.653749 | 162 | 459.0 | 2230.0 | 0.248841 | 7/21 | 5/21 |
| blend_v28_online_lr010_w20 | 378 | 21 | 0.243962 | 0.673952 | 165 | 621.5 | 821.0 | 0.112793 | 9/21 | 6/21 |

## Notes

- Rows at or before locked_after_utc are excluded from every gate. The slice can only clear on fresh paired sidecar live-shadow rows.
- This report is research-only and cannot place orders or mutate live strategy state.
