# v28 Micro Momentum Replay

- strategy_tag: `mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio_live`
- log_source_tag: `live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio`
- base matched trades: 14
- base net after fees: $-0.1200
- windows: 15s, 30s, 60s

## Filled-trade replay

| cap | kept | skipped | net after fees | delta | skipped pnl |
|---:|---:|---:|---:|---:|---:|
| 0.5c | 14 | 0 | $-0.1200 | $0.0000 | $0.0000 |
| 1.0c | 13 | 1 | $-0.1200 | $0.0000 | $0.0000 |
| 2.0c | 13 | 1 | $-0.1200 | $0.0000 | $0.0000 |
| 3.0c | 12 | 2 | $-0.1600 | $-0.0400 | $0.0400 |

## Skipped Trades At 3c Cap

| entry | market | side | pnl | edge | momentum | adjusted edge |
|---|---|---:|---:|---:|---:|---:|
| 2026-05-08 16:31:44 | `KXBTC15M-26MAY081645-45` | yes | $0.0000 | 3.830c | -1.000 | 0.830c |
| 2026-05-08 17:21:27 | `KXBTC15M-26MAY081730-30` | no | $0.0400 | 5.775c | -0.962 | 2.889c |

## Nearby Filter Diagnostics

| filter | setting | kept | skipped | net after fees | delta |
|---|---:|---:|---:|---:|---:|
| low-edge adverse | margin <= 5.0c, score < -0.25 | 10 | 4 | $0.0200 | $0.1400 |
| low-edge adverse | margin <= 5.0c, score < -0.5 | 11 | 3 | $-0.0400 | $0.0800 |
| hard floor | score >= -0.9 | 11 | 3 | $-0.1000 | $0.0200 |
| hard floor | score >= -0.75 | 11 | 3 | $-0.1000 | $0.0200 |
| hard floor | score >= 0.0 | 5 | 9 | $-0.1600 | $-0.0400 |
| low-edge adverse | margin <= 3.0c, score < -0.75 | 12 | 2 | $-0.1600 | $-0.0400 |
| low-edge adverse | margin <= 3.0c, score < -0.5 | 12 | 2 | $-0.1600 | $-0.0400 |
| low-edge adverse | margin <= 3.0c, score < -0.25 | 12 | 2 | $-0.1600 | $-0.0400 |

## Potential Adds

- rough add count at 3c cap: 0
- rough settlement-only net: $0.0000
- note: this is not full-policy PnL; it ignores real fill probability and exit behavior.
