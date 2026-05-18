# Paired Sidecar Slice OOS Report

- generated_utc: `2026-05-13T02:02:11+00:00`
- hypothesis_id: `blend_v28_w20_time_gt_600s_v1`
- evaluation_scope: `locked_forward_shadow`
- locked_after_utc: `2026-05-12T14:44:16+00:00`
- model: `blend_v28_online_lr010_w20`
- slice: `time_to_close_band=600s_plus`
- promotion_allowed: `False`
- promotion_safe: `False`
- fresh_candidate_rows / markets: `504` / `28`
- slice_rows / markets: `432` / `24`
- selected_count: `177`
- selected_pnl_cents: `450.5`
- top_ev_bucket_pnl_cents: `448.5`

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
| blend_v28_online_lr010_w20 | 432 | 24 | 0.220332 | 0.621517 | 177 | 450.5 | 448.5 | 0.096980 | 9/24 | 6/24 |
| v28 | 432 | 24 | 0.216443 | 0.606858 | 171 | 1739.7 | 952.5 | 0.160666 | 12/24 | 6/24 |
| market_side_ask | 432 | 24 | 0.221970 | 0.628457 | 0 | 0.0 | -1369.5 | -0.044373 | 0/24 | 4/24 |
| candle_brownian | 432 | 24 | 0.214452 | 0.615696 | 189 | -130.5 | 2155.5 | 0.186108 | 7/24 | 5/24 |

## Notes

- Rows at or before locked_after_utc are excluded from every gate. The slice can only clear on fresh paired sidecar live-shadow rows.
- This report is research-only and cannot place orders or mutate live strategy state.
