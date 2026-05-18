# arXiv Remaining Ideas

Research-only diagnostics for the Truffle ideas not fully covered in the earlier probes. These are candidate filters and monitors over recorded v28 data, not live-trading changes.

- Generated UTC: `2026-05-08T01:14:23.404187+00:00`
- Matched trades: `632`
- Detailed feature matches: `632`

## S-CRC Proxies

| variant | accepted | W/L | PnL | avg/entry | accepted/base | rejected-base PnL | delta vs base |
|---|---:|---:|---:|---:|---:|---:|---:|
| singleton_only_no_lower_edge | 79 | 42/36 (+1 flat) | $8.94 | 11.3c | 37.8% | $15.91 | -1,591.0c |
| singleton_gap_lower_edge_ge_0 | 15 | 5/10 | $-1.09 | -7.3c | 7.2% | $25.94 | -2,594.0c |
| singleton_gap_lower_edge_ge_0_lossrate_le_52pct | 15 | 5/10 | $-1.09 | -7.3c | 7.2% | $25.94 | -2,594.0c |
| singleton_gap_lower_edge_ge_2_lossrate_le_52pct | 10 | 2/8 | $-1.50 | -15.0c | 4.8% | $26.35 | -2,635.0c |

## Online Model Selection

| variant | entries | W/L | PnL | avg/entry | switches | choices |
|---|---:|---:|---:|---:|---:|---|
| oms_warm80_win60_hist15_mean_gt_0 | 306 | 140/157 (+9 flat) | $24.63 | 8.0c | 142 | brownian_fpt_current:93, consensus_gap_robust_rank1:62, depth_decay_current:85, hybrid_fpt_depth_robust_rank1:66 |
| oms_warm100_win90_hist20_mean_gt_0 | 297 | 135/153 (+9 flat) | $23.77 | 8.0c | 141 | brownian_fpt_current:93, consensus_gap_robust_rank1:60, depth_decay_current:86, hybrid_fpt_depth_robust_rank1:58 |
| oms_warm120_win120_hist25_mean_gt_1 | 285 | 128/148 (+9 flat) | $21.83 | 7.7c | 124 | brownian_fpt_current:96, depth_decay_current:90, consensus_gap_robust_rank1:63, hybrid_fpt_depth_robust_rank1:36 |

## Regime Monitors

- Exchangeability power martingale crossings: `0`, max capital `1.15`.
- WATCH-style EWMA miss triggers: `21`.
- Hybrid post-exchangeability-trigger median next-window PnL: `n/a`.
- Hybrid post-WATCH-trigger median next-window PnL: `120.0c`.

## Fillability And Depth Decay

- Entry submit rows: `999`; filled any: `569`; zero-fill: `430`.
- Queue-reactive proxy Spearman vs fill-any: `0.201`.
- Cross-sectional log(depth) vs log(seconds-to-close) slope: `0.095` over `999` rows.
- Within-market median depth-decay slope: `-0.226` across `154` markets.
- Share of market slopes in Dubach-like 0.55 +/- 0.20 band: `5.8%`.

| depth ratio bin | entries | fill-any | avg fill fraction |
|---|---:|---:|---:|
| <1 | 15 | 33.3% | 33.3% |
| 1-3 | 80 | 40.0% | 39.4% |
| 3-8 | 97 | 48.5% | 47.9% |
| 8-20 | 188 | 52.1% | 51.3% |
| >=20 | 619 | 62.5% | 62.5% |

## FPT And Jump Sanity

- Rows with Brownian terminal probability: `632`.
- Rows with jump-adjusted terminal probability: `80`.

| model | rows | Brier | log loss |
|---|---:|---:|---:|
| v28_side_probability | 630 | 0.1814 | 0.5753 |
| brownian_terminal | 630 | 0.1712 | 0.5274 |
| jump_adjusted_terminal | 80 | 0.1322 | 0.4366 |

## Imprecise Probability Proxy

- Width/PnL Spearman: `-0.047`.
- Low-width PnL: `$5.71` from `315` rows.
- High-width PnL: `$7.42` from `315` rows.
- Robust hybrid base: `$24.85` from `209` rows.
- Robust hybrid with lower interval edge >= 0: `$1.35` from `27` rows; delta `-2,350.0c`.

## Read

- S-CRC and imprecise-probability filters are useful only if they improve risk without deleting the sample down to a tiny retrospective island.
- Online model selection is useful only if it survives frozen forward shadowing; this report uses retrospective shadow labels.
- The queue/fillability section is the most directly operational because it includes zero-fill entry submits, not only filled trades.
- None of these diagnostics should promote a strategy without a fresh forward shadow registry.
