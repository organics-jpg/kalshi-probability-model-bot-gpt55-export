# Paired Sidecar Blend Failure Analysis

- generated_utc: `2026-05-18T18:29:56Z`
- rows: `1410`
- markets: `68`
- promotion_allowed: `False`
- promotion_safe: `False`
- conclusion: Post-hoc diagnostic only: promotion remains blocked. blend_v28_online_lr010_w15 market-equal Brier delta vs candle_brownian is -0.002357 and logloss delta is 0.001563 (negative is better; mixed signs block promotion). Worst selected-PnL market for the focus blend is KXBTC15M-26MAY120315-15 at -783.0c. Best post-hoc slice candidate is v28/time_to_close_band=600s_plus with 34/54 positive markets; it must be predeclared before fresh shadow validation.

## Model summaries

| model | brier | logloss | market_eq_brier | selected_pnl_c | top_ev_pnl_c | pos_selected_mkts | pos_top_mkts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| candidate_raw | 0.273550 | 0.914425 | 0.270622 | 2108.1 | -431.7 | 33/68 | 13/68 |
| v28 | 0.210488 | 0.619911 | 0.214123 | 4906.0 | 39.7 | 39/68 | 38/68 |
| market_side_ask | 0.211369 | 0.605672 | 0.215392 | 1758.6 | 1758.6 | 9/68 | 9/68 |
| candle_brownian | 0.216045 | 0.619132 | 0.215362 | 85.0 | 3393.4 | 21/68 | 22/68 |
| tick_brownian | 0.215544 | 0.618156 | 0.214632 | -788.0 | 2649.4 | 20/68 | 21/68 |
| online_logit_candidate_lr010_row | 0.259119 | 0.731906 | 0.247667 | 1172.6 | 181.4 | 28/68 | 23/68 |
| blend_v28_online_lr010_w10 | 0.210843 | 0.614538 | 0.213136 | 3741.4 | 595.7 | 34/68 | 31/68 |
| blend_v28_online_lr010_w25 | 0.213254 | 0.616184 | 0.213465 | 4059.8 | 781.1 | 32/68 | 30/68 |
| blend_market_online_lr010_w15 | 0.211350 | 0.607283 | 0.213789 | 1172.6 | 181.4 | 28/68 | 23/68 |
| blend_market_online_lr010_w05 | 0.211081 | 0.605561 | 0.214605 | 1172.6 | 181.4 | 28/68 | 23/68 |
| blend_v28_online_lr010_w15 | 0.211396 | 0.614134 | 0.213005 | 3820.8 | 1380.7 | 33/68 | 31/68 |
| online_logit_candidate_lr003_row | 0.257978 | 0.747124 | 0.251653 | 1998.8 | -957.5 | 28/68 | 22/68 |

## Baseline deltas

Negative Brier/logloss deltas are better. Positive PnL deltas are better.

| model | baseline | row_brier_d | row_logloss_d | row_top_ev_pnl_d_c | mkt_eq_brier_d | mkt_eq_logloss_d | mkt_eq_top_ev_pnl_d_c |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| candidate_raw | v28 | 0.063062 | 0.294514 | -471.4 | 0.056500 | 0.269567 | -44.8 |
| candidate_raw | market_side_ask | 0.062181 | 0.308753 | -2190.3 | 0.055231 | 0.284907 | -26.4 |
| candidate_raw | candle_brownian | 0.057504 | 0.295293 | -3825.1 | 0.055260 | 0.283038 | -21.3 |
| v28 | market_side_ask | -0.000881 | 0.014239 | -1718.9 | -0.001269 | 0.015340 | 18.3 |
| v28 | candle_brownian | -0.005557 | 0.000779 | -3353.7 | -0.001239 | 0.013471 | 23.5 |
| market_side_ask | v28 | 0.000881 | -0.014239 | 1718.9 | 0.001269 | -0.015340 | -18.3 |
| market_side_ask | candle_brownian | -0.004676 | -0.013460 | -1634.8 | 0.000030 | -0.001870 | 5.2 |
| candle_brownian | v28 | 0.005557 | -0.000779 | 3353.7 | 0.001239 | -0.013471 | -23.5 |
| candle_brownian | market_side_ask | 0.004676 | 0.013460 | 1634.8 | -0.000030 | 0.001870 | -5.2 |
| tick_brownian | v28 | 0.005055 | -0.001755 | 2609.7 | 0.000509 | -0.014904 | -29.2 |
| tick_brownian | market_side_ask | 0.004174 | 0.012484 | 890.8 | -0.000760 | 0.000436 | -10.9 |
| tick_brownian | candle_brownian | -0.000502 | -0.000976 | -744.0 | -0.000730 | -0.001433 | -5.7 |
| online_logit_candidate_lr010_row | v28 | 0.048631 | 0.111995 | 141.7 | 0.033544 | 0.070301 | -25.2 |
| online_logit_candidate_lr010_row | market_side_ask | 0.047750 | 0.126234 | -1577.2 | 0.032275 | 0.085641 | -6.9 |
| online_logit_candidate_lr010_row | candle_brownian | 0.043074 | 0.112774 | -3212.0 | 0.032305 | 0.083772 | -1.7 |
| blend_v28_online_lr010_w10 | v28 | 0.000355 | -0.005373 | 556.0 | -0.000987 | -0.009632 | -12.3 |
| blend_v28_online_lr010_w10 | market_side_ask | -0.000526 | 0.008866 | -1162.9 | -0.002255 | 0.005708 | 6.1 |
| blend_v28_online_lr010_w10 | candle_brownian | -0.005202 | -0.004594 | -2797.7 | -0.002226 | 0.003839 | 11.2 |
| blend_v28_online_lr010_w25 | v28 | 0.002766 | -0.003727 | 741.4 | -0.000658 | -0.013361 | -0.2 |
| blend_v28_online_lr010_w25 | market_side_ask | 0.001885 | 0.010512 | -977.5 | -0.001927 | 0.001979 | 18.1 |
| blend_v28_online_lr010_w25 | candle_brownian | -0.002791 | -0.002949 | -2612.3 | -0.001897 | 0.000110 | 23.3 |
| blend_market_online_lr010_w15 | v28 | 0.000862 | -0.012628 | 141.7 | -0.000334 | -0.018157 | -25.2 |
| blend_market_online_lr010_w15 | market_side_ask | -0.000019 | 0.001611 | -1577.2 | -0.001603 | -0.002817 | -6.9 |
| blend_market_online_lr010_w15 | candle_brownian | -0.004695 | -0.011849 | -3212.0 | -0.001573 | -0.004686 | -1.7 |
| blend_market_online_lr010_w05 | v28 | 0.000593 | -0.014350 | 141.7 | 0.000482 | -0.016931 | -25.2 |
| blend_market_online_lr010_w05 | market_side_ask | -0.000288 | -0.000111 | -1577.2 | -0.000787 | -0.001590 | -6.9 |
| blend_market_online_lr010_w05 | candle_brownian | -0.004964 | -0.013571 | -3212.0 | -0.000757 | -0.003460 | -1.7 |
| blend_v28_online_lr010_w15 | v28 | 0.000908 | -0.005777 | 1341.0 | -0.001118 | -0.011908 | -12.5 |
| blend_v28_online_lr010_w15 | market_side_ask | 0.000027 | 0.008462 | -377.9 | -0.002387 | 0.003433 | 5.8 |
| blend_v28_online_lr010_w15 | candle_brownian | -0.004649 | -0.004998 | -2012.7 | -0.002357 | 0.001563 | 11.0 |
| online_logit_candidate_lr003_row | v28 | 0.047490 | 0.127213 | -997.2 | 0.037530 | 0.088670 | -26.7 |
| online_logit_candidate_lr003_row | market_side_ask | 0.046609 | 0.141453 | -2716.1 | 0.036261 | 0.104010 | -8.4 |
| online_logit_candidate_lr003_row | candle_brownian | 0.041933 | 0.127992 | -4350.9 | 0.036291 | 0.102141 | -3.2 |

## Worst focus-blend markets

| model | market | rows | selected_count | selected_pnl_c | top_ev_pnl_c | selected_delta_vs_v28_c |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| blend_v28_online_lr010_w15 | KXBTC15M-26MAY120315-15 | 18 | 9 | -783.0 | -348.0 | 0.0 |
| blend_v28_online_lr010_w15 | KXBTC15M-26MAY120730-30 | 18 | 9 | -648.0 | -288.0 | 0.0 |
| blend_v28_online_lr010_w15 | KXBTC15M-26MAY120215-15 | 48 | 17 | -634.0 | -426.0 | 62.0 |
| blend_v28_online_lr010_w15 | KXBTC15M-26MAY120130-30 | 64 | 32 | -600.0 | -197.0 | 0.0 |
| blend_v28_online_lr010_w15 | KXBTC15M-26MAY120845-45 | 18 | 8 | -536.0 | -356.0 | 265.0 |
| blend_v28_online_lr010_w15 | KXBTC15M-26MAY120145-45 | 48 | 24 | -476.0 | -248.5 | 0.0 |
| blend_v28_online_lr010_w15 | KXBTC15M-26MAY122115-15 | 18 | 9 | -459.0 | -204.0 | 0.0 |
| blend_v28_online_lr010_w15 | KXBTC15M-26MAY121715-15 | 18 | 9 | -432.0 | -192.0 | 0.0 |
| blend_v28_online_lr010_w15 | KXBTC15M-26MAY122045-45 | 18 | 9 | -414.0 | -184.0 | 0.0 |
| blend_v28_online_lr010_w15 | KXBTC15M-26MAY121345-45 | 18 | 9 | -396.0 | -176.0 | 0.0 |
| blend_v28_online_lr010_w15 | KXBTC15M-26MAY121445-45 | 18 | 9 | -396.0 | -176.0 | 0.0 |
| blend_v28_online_lr010_w15 | KXBTC15M-26MAY121645-45 | 18 | 9 | -378.0 | -168.0 | 0.0 |

## Post-hoc slice candidates

These are not promotion evidence. They are only candidates for fresh predeclared shadow tests.

| model | slice | bucket | rows | markets | selected_count | selected_pnl_c | top_ev_pnl_c | positive_markets |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v28 | time_to_close_band | 600s_plus | 976 | 54 | 470 | 5121.1 | 318.0 | 34/54 |

## Slice rows

The JSON report contains all slice rows. This markdown shows the 20 strongest positive selected-PnL rows with at least 50 denominator rows.

| model | slice | bucket | rows | markets | brier | selected_pnl_c | top_ev_pnl_c | positive_selected_mkts |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v28 | time_to_close_band | 600s_plus | 976 | 54 | 0.238680 | 5121.1 | 318.0 | 34/54 |
| blend_v28_online_lr010_w25 | time_to_close_band | 600s_plus | 976 | 54 | 0.233631 | 4707.7 | 1851.4 | 29/54 |
| v28 | side | no | 705 | 68 | 0.210488 | 4639.2 | -29.3 | 31/68 |
| v28 | spot_age_band | 0000_0500ms | 932 | 48 | 0.202729 | 4514.8 | 1330.0 | 27/48 |
| blend_v28_online_lr010_w15 | time_to_close_band | 600s_plus | 976 | 54 | 0.235005 | 4379.7 | 2183.0 | 29/54 |
| v28 | ask_band | 20_40 | 277 | 30 | 0.230134 | 4371.0 | 1635.0 | 10/30 |
| v28 | spot_delta_abs_bps_band | 00_01bps | 1144 | 54 | 0.214884 | 4264.0 | 189.7 | 31/54 |
| blend_v28_online_lr010_w25 | side | no | 705 | 68 | 0.213213 | 4107.2 | 679.8 | 30/68 |
| blend_v28_online_lr010_w10 | ask_band | 20_40 | 277 | 30 | 0.230728 | 4087.0 | 1678.0 | 10/30 |
| blend_v28_online_lr010_w10 | time_to_close_band | 600s_plus | 976 | 54 | 0.236015 | 3972.3 | 1208.0 | 30/54 |
| blend_v28_online_lr010_w25 | spot_delta_abs_bps_band | 00_01bps | 1144 | 54 | 0.215800 | 3883.8 | 1105.1 | 26/54 |
| blend_v28_online_lr010_w10 | side | no | 705 | 68 | 0.210820 | 3804.1 | 427.7 | 30/68 |
| blend_v28_online_lr010_w15 | ask_band | 20_40 | 277 | 30 | 0.231337 | 3667.0 | 2118.0 | 11/30 |
| v28 | market_v28_disagreement_band | 00_05pp | 689 | 38 | 0.185136 | 3660.3 | 0.0 | 22/38 |
| blend_v28_online_lr010_w15 | side | no | 705 | 68 | 0.211365 | 3571.2 | 1270.7 | 29/68 |
| blend_v28_online_lr010_w15 | spot_delta_abs_bps_band | 00_01bps | 1144 | 54 | 0.214606 | 3538.8 | 1239.7 | 26/54 |
| blend_v28_online_lr010_w10 | spot_age_band | 0000_0500ms | 932 | 48 | 0.203655 | 3527.7 | 1314.5 | 23/48 |
| blend_v28_online_lr010_w15 | spot_age_band | 0000_0500ms | 932 | 48 | 0.204492 | 3433.1 | 1884.5 | 22/48 |
| online_logit_candidate_lr010_row | time_to_close_band | 600s_plus | 976 | 54 | 0.250765 | 3407.7 | 1458.7 | 27/54 |
| blend_market_online_lr010_w15 | time_to_close_band | 600s_plus | 976 | 54 | 0.240517 | 3407.7 | 1458.7 | 27/54 |
