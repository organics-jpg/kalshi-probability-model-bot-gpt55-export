# Paired Sidecar Slice Retirement

- generated_utc: `2026-05-18T18:30:27+00:00`
- promotion_allowed: `False`
- row_count: `5`
- particle_like_count: `3`
- retire_count: `0`
- watchlist_count: `0`
- stability_blocked_count: `3`
- trajectory_blocked_count: `3`
- continue_shadow_count: `0`
- control_count: `2`
- candidate_for_broader_audit_count: `0`

## Rows

| hypothesis | model | rows/markets | selected | pnl c | top EV c | dPnL vs v28 | dBrier vs v28 | stability pass | trajectory pass | recent c | recent dPnL | warnings | recommendation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | --- | --- |
| `blend_v28_w20_time_gt_600s_v1` | `blend_v28_online_lr010_w20` | `432` / `24` | `177` | `450.5` | `448.5` | `-1289.200000` | `0.003889` | `False` | `False` | `-215.000000` | `-48.500000` | `nonpositive_top_ev_pnl, low_positive_market_fraction, worse_or_equal_selected_vs_v28, worse_or_equal_top_ev_vs_v28, worse_or_equal_brier_vs_v28, worse_or_equal_logloss_vs_v28, nonpositive_recent_pnl, nonpositive_total_delta_vs_v28, nonpositive_recent_delta_vs_v28, drawdown_large_vs_total_pnl` | `trajectory_blocked_shadow_only` |
| `blend_v28_w05_time_gt_600s_v1` | `blend_v28_online_lr010_w05` | `378` / `21` | `144` | `1460.0` | `355.0` | `-56.500000` | `0.000368` | `False` | `False` | `-166.500000` | `0.000000` | `low_positive_market_fraction, worse_or_equal_selected_vs_v28, worse_or_equal_top_ev_vs_v28, worse_or_equal_brier_vs_v28, worse_or_equal_logloss_vs_v28, nonpositive_recent_pnl, nonpositive_total_delta_vs_v28, nonpositive_recent_delta_vs_v28` | `trajectory_blocked_shadow_only` |
| `v28_control_time_gt_600s_v1` | `v28` | `378` / `21` | `153` | `1516.5` | `748.0` | `` | `` | `False` | `False` | `-166.500000` | `0.000000` | `low_positive_market_fraction, nonpositive_recent_pnl` | `control_reference_only` |
| `blend_v28_w15_candidate_v28_gap_05_15pp_v1` | `blend_v28_online_lr010_w15` | `35` / `14` | `14` | `-31.7` | `67.8` | `-25.000000` | `0.001253` | `False` | `False` | `-71.000000` | `0.000000` | `underpowered_markets, nonpositive_selected_pnl, nonpositive_top_ev_pnl, low_positive_market_fraction, worse_or_equal_selected_vs_v28, worse_or_equal_top_ev_vs_v28, worse_or_equal_brier_vs_v28, worse_or_equal_logloss_vs_v28, underpowered_markets, nonpositive_total_pnl, nonpositive_recent_pnl, nonpositive_total_delta_vs_v28, nonpositive_recent_delta_vs_v28` | `trajectory_blocked_shadow_only` |
| `v28_control_candidate_v28_gap_05_15pp_v1` | `v28` | `35` / `14` | `16` | `-6.7` | `-64.2` | `0.000000` | `0.000000` | `False` | `False` | `-71.000000` | `0.000000` | `underpowered_markets, nonpositive_selected_pnl, low_positive_market_fraction, underpowered_markets, nonpositive_total_pnl, nonpositive_recent_pnl` | `control_reference_only` |

## Conclusion

3 particle-like lock(s) are blocked by trajectory diagnostics and remain shadow-only.

This report is diagnostic only and never authorizes live trading.
