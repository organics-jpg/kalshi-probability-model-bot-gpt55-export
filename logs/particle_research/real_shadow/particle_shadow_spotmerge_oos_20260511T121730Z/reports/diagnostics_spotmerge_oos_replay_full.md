# Replay Diagnostics

- source_report: `logs\particle_research\real_shadow\particle_shadow_spotmerge_oos_20260511T121730Z\reports\spotmerge_oos_replay_full.json`
- candidate_count: 663
- selected_count: 649
- total_counterfactual_pnl_cents: -4638.0000
- particle_brier_minus_market_brier: 0.045778
- particle_brier_minus_current_brier: 0.041431
- particle_logloss_minus_market_logloss: 0.132385
- particle_logloss_minus_current_logloss: 0.124312
- selected_yes_count: 4
- selected_yes_pnl_cents: 97.0000
- selected_no_count: 645
- selected_no_pnl_cents: -4735.0000

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

### KXBTC15M-26MAY110845-45

- candidate_count: 107
- selected_count: 105
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 6007.0000
- mean_particle_minus_market: -0.075294
- mean_particle_minus_current: -0.057006
- yes_selected: 1, pnl=-53.0000, win_rate=0.0000
- no_selected: 104, pnl=6060.0000, win_rate=1.0000

## EV Buckets

- ev_rank_1_of_5: candidates=132, selected=132, avg_pred_ev=23.2947, pnl=-1877.0000, avg_pnl=-14.2197, win_rate=0.0000
- ev_rank_2_of_5: candidates=133, selected=133, avg_pred_ev=13.9065, pnl=-2037.0000, avg_pnl=-15.3158, win_rate=0.0526
- ev_rank_3_of_5: candidates=132, selected=132, avg_pred_ev=10.7402, pnl=-679.0000, avg_pnl=-5.1439, win_rate=0.1288
- ev_rank_4_of_5: candidates=133, selected=133, avg_pred_ev=7.6217, pnl=258.0000, avg_pnl=1.9398, win_rate=0.2481
- ev_rank_5_of_5: candidates=133, selected=119, avg_pred_ev=2.8719, pnl=-303.0000, avg_pnl=-2.5462, win_rate=0.4202

## Worst Decisions

- KXBTC15M-26MAY110845-45 2026-05-11T12:32:06.638230+00:00 side=yes pnl=-53.0 particle=0.5565 market=0.525 current=0.587233
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:34.146815+00:00 side=no pnl=-52.0 particle=0.457 market=0.485 current=0.423661
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:44.259241+00:00 side=no pnl=-49.0 particle=0.4705 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:45.265515+00:00 side=no pnl=-49.0 particle=0.4925 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:46.280243+00:00 side=no pnl=-49.0 particle=0.475 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:47.327358+00:00 side=no pnl=-49.0 particle=0.488 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:48.329389+00:00 side=no pnl=-49.0 particle=0.468 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:49.514816+00:00 side=no pnl=-49.0 particle=0.484 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:50.534883+00:00 side=no pnl=-49.0 particle=0.481 market=0.515 current=0.438034
- KXBTC15M-26MAY110830-30 2026-05-11T12:17:51.624122+00:00 side=no pnl=-49.0 particle=0.4715 market=0.515 current=0.438034
