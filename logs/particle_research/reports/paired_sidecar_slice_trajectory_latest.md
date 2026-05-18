# Paired Sidecar Slice Trajectory

- generated_utc: `2026-05-18T18:30:23+00:00`
- promotion_allowed: `False`
- row_count: `5`
- particle_like_count: `3`
- trajectory_screen_pass_count: `0`
- particle_like_trajectory_screen_pass_count: `0`
- worst_recent_hypothesis_id: `blend_v28_w20_time_gt_600s_v1`
- worst_recent_selected_pnl_cents: `-215.0`

## Rows

| hypothesis | model | markets | total c | dTotal vs v28 | recent n | recent c | dRecent vs v28 | pos all/recent | max DD c | first | last | warnings | pass |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `blend_v28_w05_time_gt_600s_v1` | `blend_v28_online_lr010_w05` | `21` | `1460.0` | `-56.500000` | `5` | `-166.5` | `0.000000` | `10` / `2` | `1192.5` | `KXBTC15M-26MAY121230-30` | `KXBTC15M-26MAY122145-45` | `nonpositive_recent_pnl, nonpositive_total_delta_vs_v28, nonpositive_recent_delta_vs_v28` | `False` |
| `blend_v28_w15_candidate_v28_gap_05_15pp_v1` | `blend_v28_online_lr010_w15` | `14` | `-31.7` | `-25.000000` | `5` | `-71.0` | `0.000000` | `6` / `2` | `185.0` | `KXBTC15M-26MAY121445-45` | `KXBTC15M-26MAY122145-45` | `underpowered_markets, nonpositive_total_pnl, nonpositive_recent_pnl, nonpositive_total_delta_vs_v28, nonpositive_recent_delta_vs_v28` | `False` |
| `blend_v28_w20_time_gt_600s_v1` | `blend_v28_online_lr010_w20` | `24` | `450.5` | `-1289.200000` | `5` | `-215.0` | `-48.500000` | `9` / `2` | `1192.5` | `KXBTC15M-26MAY121130-30` | `KXBTC15M-26MAY122145-45` | `nonpositive_recent_pnl, nonpositive_total_delta_vs_v28, nonpositive_recent_delta_vs_v28, drawdown_large_vs_total_pnl` | `False` |
| `v28_control_candidate_v28_gap_05_15pp_v1` | `v28` | `14` | `-6.7` | `0.000000` | `5` | `-71.0` | `0.000000` | `6` / `2` | `185.0` | `KXBTC15M-26MAY121445-45` | `KXBTC15M-26MAY122145-45` | `underpowered_markets, nonpositive_total_pnl, nonpositive_recent_pnl` | `False` |
| `v28_control_time_gt_600s_v1` | `v28` | `21` | `1516.5` | `0.000000` | `5` | `-166.5` | `0.000000` | `10` / `2` | `1192.5` | `KXBTC15M-26MAY121230-30` | `KXBTC15M-26MAY122145-45` | `nonpositive_recent_pnl` | `False` |

## Conclusion

No particle-like lock passes the trajectory screen; keep all locks shadow-only.

This report is diagnostic only and never authorizes live trading.
