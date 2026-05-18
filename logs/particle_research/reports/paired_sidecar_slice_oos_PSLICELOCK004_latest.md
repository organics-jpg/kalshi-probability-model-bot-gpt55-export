# Paired Sidecar Slice OOS Report

- generated_utc: `2026-05-13T02:02:11+00:00`
- hypothesis_id: `blend_v28_w15_candidate_v28_gap_05_15pp_v1`
- evaluation_scope: `locked_forward_shadow`
- locked_after_utc: `2026-05-12T18:23:29+00:00`
- model: `blend_v28_online_lr010_w15`
- slice: `candidate_v28_disagreement_band=05_15pp`
- promotion_allowed: `False`
- promotion_safe: `False`
- fresh_candidate_rows / markets: `342` / `19`
- slice_rows / markets: `35` / `14`
- selected_count: `14`
- selected_pnl_cents: `-31.7`
- top_ev_bucket_pnl_cents: `67.8`

## Gate Results

| gate | passed |
| --- | ---: |
| enough_fresh_candidate_rows | `True` |
| enough_fresh_markets | `False` |
| enough_slice_rows | `False` |
| enough_slice_markets | `False` |
| enough_selected | `False` |
| positive_selected_pnl | `False` |
| positive_avg_pnl | `False` |
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
| blend_v28_online_lr010_w15 | 35 | 14 | 0.219018 | 0.618332 | 14 | -31.7 | 67.8 | 0.061380 | 6/14 | 3/14 |
| v28 | 35 | 14 | 0.217766 | 0.613796 | 16 | -6.7 | -64.2 | 0.074953 | 6/14 | 2/14 |
| market_side_ask | 35 | 14 | 0.218066 | 0.620411 | 0 | 0.0 | -10.5 | -0.040705 | 0/14 | 4/14 |
| candle_brownian | 35 | 14 | 0.228652 | 0.649417 | 15 | -119.2 | 143.8 | 0.054596 | 4/14 | 3/14 |

## Notes

- Rows at or before locked_after_utc are excluded from every gate. The slice can only clear on fresh paired sidecar live-shadow rows.
- This report is research-only and cannot place orders or mutate live strategy state.
