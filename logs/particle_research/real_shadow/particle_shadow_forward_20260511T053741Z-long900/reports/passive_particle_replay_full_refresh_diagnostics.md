# Replay Diagnostics

- source_report: `logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\reports\passive_particle_replay_full_refresh.json`
- candidate_count: 753
- selected_count: 676
- total_counterfactual_pnl_cents: -4876.0000
- particle_brier_minus_market_brier: 0.048476
- particle_brier_minus_current_brier: 0.033415
- particle_logloss_minus_market_logloss: 0.154074
- particle_logloss_minus_current_logloss: 0.095344
- selected_yes_count: 434
- selected_yes_pnl_cents: 4193.0000
- selected_no_count: 242
- selected_no_pnl_cents: -9069.0000

## Markets

### KXBTC15M-26MAY110145-45

- candidate_count: 333
- selected_count: 333
- settlement_result_yes: False
- total_counterfactual_pnl_cents: -1487.0000
- mean_particle_minus_market: 0.216848
- mean_particle_minus_current: 0.135558
- yes_selected: 333, pnl=-1487.0000, win_rate=0.0000
- no_selected: 0, pnl=0.0000, win_rate=0.0000

### KXBTC15M-26MAY110200-00

- candidate_count: 420
- selected_count: 343
- settlement_result_yes: True
- total_counterfactual_pnl_cents: -3389.0000
- mean_particle_minus_market: -0.047240
- mean_particle_minus_current: -0.022093
- yes_selected: 101, pnl=5680.0000, win_rate=1.0000
- no_selected: 242, pnl=-9069.0000, win_rate=0.0000

## EV Buckets

- ev_rank_1_of_5: candidates=150, selected=150, avg_pred_ev=24.4492, pnl=-641.0000, avg_pnl=-4.2733, win_rate=0.0000
- ev_rank_2_of_5: candidates=151, selected=151, avg_pred_ev=20.7076, pnl=-1386.0000, avg_pnl=-9.1788, win_rate=0.0000
- ev_rank_3_of_5: candidates=150, selected=150, avg_pred_ev=13.1457, pnl=-3129.0000, avg_pnl=-20.8600, win_rate=0.0200
- ev_rank_4_of_5: candidates=151, selected=151, avg_pred_ev=4.5864, pnl=834.0000, avg_pnl=5.5232, win_rate=0.4503
- ev_rank_5_of_5: candidates=151, selected=74, avg_pred_ev=0.0091, pnl=-554.0000, avg_pnl=-7.4865, win_rate=0.4054

## Worst Decisions

- KXBTC15M-26MAY110200-00 2026-05-11T05:46:46.876727+00:00 side=no pnl=-53.0 particle=0.4475 market=0.475 current=0.478275
- KXBTC15M-26MAY110200-00 2026-05-11T05:52:14.323392+00:00 side=no pnl=-53.0 particle=0.4515 market=0.475 current=0.458896
- KXBTC15M-26MAY110200-00 2026-05-11T05:52:15.509149+00:00 side=no pnl=-53.0 particle=0.453 market=0.475 current=0.458896
- KXBTC15M-26MAY110200-00 2026-05-11T05:46:51.910660+00:00 side=no pnl=-52.0 particle=0.467 market=0.485 current=0.478275
- KXBTC15M-26MAY110200-00 2026-05-11T05:52:09.157623+00:00 side=no pnl=-52.0 particle=0.463 market=0.485 current=0.601151
- KXBTC15M-26MAY110200-00 2026-05-11T05:52:10.182164+00:00 side=no pnl=-52.0 particle=0.463 market=0.485 current=0.458896
- KXBTC15M-26MAY110200-00 2026-05-11T05:47:01.020194+00:00 side=no pnl=-51.0 particle=0.4755 market=0.495 current=0.477663
- KXBTC15M-26MAY110200-00 2026-05-11T05:47:02.068315+00:00 side=no pnl=-51.0 particle=0.477 market=0.495 current=0.477663
- KXBTC15M-26MAY110200-00 2026-05-11T05:49:00.048455+00:00 side=no pnl=-50.0 particle=0.4895 market=0.505 current=0.51202
- KXBTC15M-26MAY110200-00 2026-05-11T05:47:30.387386+00:00 side=no pnl=-49.0 particle=0.493 market=0.515 current=0.510061
