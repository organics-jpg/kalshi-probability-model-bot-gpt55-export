# Replay Diagnostics

- source_report: `logs\particle_research\real_shadow\particle_shadow_spotmerge_oos_20260511T121730Z\reports\spotmerge_oos_replay_resolved_subset.json`
- candidate_count: 556
- selected_count: 544
- total_counterfactual_pnl_cents: -10645.0000
- particle_brier_minus_market_brier: 0.071488
- particle_brier_minus_current_brier: 0.063263
- particle_logloss_minus_market_logloss: 0.193115
- particle_logloss_minus_current_logloss: 0.178422
- selected_yes_count: 3
- selected_yes_pnl_cents: 150.0000
- selected_no_count: 541
- selected_no_pnl_cents: -10795.0000

## Markets

### KXBTC15M-26MAY110830-30

- candidate_count: 556
- selected_count: 544
- settlement_result_yes: True
- total_counterfactual_pnl_cents: -10645.0000
- mean_particle_minus_market: -0.137686
- mean_particle_minus_current: -0.130721
- yes_selected: 3, pnl=150.0000, win_rate=1.0000
- no_selected: 541, pnl=-10795.0000, win_rate=0.0000

## EV Buckets

- ev_rank_1_of_5: candidates=111, selected=111, avg_pred_ev=24.1664, pnl=-1401.0000, avg_pnl=-12.6216, win_rate=0.0000
- ev_rank_2_of_5: candidates=111, selected=111, avg_pred_ev=15.3212, pnl=-2313.0000, avg_pnl=-20.8378, win_rate=0.0000
- ev_rank_3_of_5: candidates=111, selected=111, avg_pred_ev=11.6441, pnl=-1982.0000, avg_pnl=-17.8559, win_rate=0.0000
- ev_rank_4_of_5: candidates=111, selected=111, avg_pred_ev=8.8739, pnl=-1520.0000, avg_pnl=-13.6937, win_rate=0.0000
- ev_rank_5_of_5: candidates=112, selected=100, avg_pred_ev=3.7899, pnl=-3429.0000, avg_pnl=-34.2900, win_rate=0.0300

## Worst Decisions

- KXBTC15M-26MAY110830-30 2026-05-11T12:17:34.146815+00:00 side=no pnl=-52.0 particle=0.457 market=0.485 current=0.423661
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:44.259241+00:00 side=no pnl=-49.0 particle=0.4705 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:45.265515+00:00 side=no pnl=-49.0 particle=0.4925 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:46.280243+00:00 side=no pnl=-49.0 particle=0.475 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:47.327358+00:00 side=no pnl=-49.0 particle=0.488 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:48.329389+00:00 side=no pnl=-49.0 particle=0.468 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:49.514816+00:00 side=no pnl=-49.0 particle=0.484 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:50.534883+00:00 side=no pnl=-49.0 particle=0.481 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:51.624122+00:00 side=no pnl=-49.0 particle=0.4715 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:52.628295+00:00 side=no pnl=-49.0 particle=0.467 market=0.515 current=0.438034
