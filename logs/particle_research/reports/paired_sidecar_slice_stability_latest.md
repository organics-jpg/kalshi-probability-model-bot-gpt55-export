# Paired Sidecar Slice Stability

- generated_utc: `2026-05-18T18:30:20+00:00`
- promotion_allowed: `False`
- row_count: `5`
- particle_like_count: `3`
- stability_screen_pass_count: `0`
- particle_like_stability_screen_pass_count: `0`
- most_concentrated_hypothesis_id: `blend_v28_w15_candidate_v28_gap_05_15pp_v1`
- most_concentrated_abs_market_pnl_share: `0.161613`

## Rows

| hypothesis | model | markets | pos/neg | pnl c | top EV c | pos frac | mean c | stdev c | worst market | worst c | best c | max abs share | dPnL vs v28 | dTopEV vs v28 | dBrier | dLogloss | warnings | pass |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `blend_v28_w05_time_gt_600s_v1` | `blend_v28_online_lr010_w05` | `21` | `10` / `8` | `1460.0` | `245.0` | `0.476` | `69.5` | `398.9` | `KXBTC15M-26MAY122115-15` | `-472.5` | `697.5` | `0.099` | `-56.500000` | `-269.000000` | `0.000368` | `0.001691` | `low_positive_market_fraction, worse_or_equal_selected_vs_v28, worse_or_equal_top_ev_vs_v28, worse_or_equal_brier_vs_v28, worse_or_equal_logloss_vs_v28` | `False` |
| `blend_v28_w15_candidate_v28_gap_05_15pp_v1` | `blend_v28_online_lr010_w15` | `14` | `6` / `6` | `-31.7` | `-38.2` | `0.429` | `-2.3` | `56.5` | `KXBTC15M-26MAY122115-15` | `-105.0` | `77.5` | `0.162` | `-25.000000` | `-122.000000` | `0.000100` | `0.000645` | `underpowered_markets, nonpositive_selected_pnl, nonpositive_top_ev_pnl, low_positive_market_fraction, worse_or_equal_selected_vs_v28, worse_or_equal_top_ev_vs_v28, worse_or_equal_brier_vs_v28, worse_or_equal_logloss_vs_v28` | `False` |
| `blend_v28_w20_time_gt_600s_v1` | `blend_v28_online_lr010_w20` | `24` | `9` / `15` | `450.5` | `-179.0` | `0.375` | `18.8` | `368.2` | `KXBTC15M-26MAY122115-15` | `-472.5` | `697.5` | `0.095` | `-1289.200000` | `-906.200000` | `0.003889` | `0.014658` | `nonpositive_top_ev_pnl, low_positive_market_fraction, worse_or_equal_selected_vs_v28, worse_or_equal_top_ev_vs_v28, worse_or_equal_brier_vs_v28, worse_or_equal_logloss_vs_v28` | `False` |
| `v28_control_candidate_v28_gap_05_15pp_v1` | `v28` | `14` | `6` / `6` | `-6.7` | `83.8` | `0.429` | `-0.5` | `57.4` | `KXBTC15M-26MAY122115-15` | `-105.0` | `77.5` | `0.156` | `0.000000` | `0.000000` | `0.000000` | `0.000000` | `underpowered_markets, nonpositive_selected_pnl, low_positive_market_fraction` | `False` |
| `v28_control_time_gt_600s_v1` | `v28` | `21` | `10` / `7` | `1516.5` | `514.0` | `0.476` | `72.2` | `402.6` | `KXBTC15M-26MAY122115-15` | `-472.5` | `697.5` | `0.097` | `0.000000` | `0.000000` | `0.000000` | `0.000000` | `low_positive_market_fraction` | `False` |

## Conclusion

No particle-like lock passes the market-stability screen; keep all locks shadow-only.

This report is diagnostic only and never authorizes live trading.
