# Replay Diagnostics

- source_report: `logs\particle_research\real_shadow\particle_spot_rv_terminal_oos_RVTERMLOCK001\reports\passive_particle_replay_locked_oos.json`
- candidate_count: 4512
- selected_count: 4379
- total_counterfactual_pnl_cents: -2384.0000
- particle_brier_minus_market_brier: 0.039006
- particle_brier_minus_current_brier: 0.044647
- particle_logloss_minus_market_logloss: 0.130531
- particle_logloss_minus_current_logloss: 0.142090
- selected_yes_count: 2708
- selected_yes_pnl_cents: -49192.0000
- selected_no_count: 1671
- selected_no_pnl_cents: 46808.0000

## Markets

### KXBTC15M-26MAY112000-00

- candidate_count: 402
- selected_count: 402
- settlement_result_yes: False
- total_counterfactual_pnl_cents: -5078.0000
- mean_particle_minus_market: 0.259718
- mean_particle_minus_current: 0.217971
- yes_selected: 402, pnl=-5078.0000, win_rate=0.0000
- no_selected: 0, pnl=0.0000, win_rate=0.0000

### KXBTC15M-26MAY112015-15

- candidate_count: 712
- selected_count: 692
- settlement_result_yes: False
- total_counterfactual_pnl_cents: -4791.0000
- mean_particle_minus_market: 0.152192
- mean_particle_minus_current: 0.169174
- yes_selected: 596, pnl=-10048.0000, win_rate=0.0000
- no_selected: 96, pnl=5257.0000, win_rate=1.0000

### KXBTC15M-26MAY112030-30

- candidate_count: 767
- selected_count: 738
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 4705.0000
- mean_particle_minus_market: 0.100140
- mean_particle_minus_current: 0.114596
- yes_selected: 523, pnl=-7543.0000, win_rate=0.0000
- no_selected: 215, pnl=12248.0000, win_rate=1.0000

### KXBTC15M-26MAY112045-45

- candidate_count: 790
- selected_count: 725
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 14052.0000
- mean_particle_minus_market: 0.003051
- mean_particle_minus_current: 0.021738
- yes_selected: 343, pnl=-9894.0000, win_rate=0.0000
- no_selected: 382, pnl=23946.0000, win_rate=1.0000

### KXBTC15M-26MAY112100-00

- candidate_count: 765
- selected_count: 765
- settlement_result_yes: True
- total_counterfactual_pnl_cents: -9784.0000
- mean_particle_minus_market: -0.239113
- mean_particle_minus_current: -0.241186
- yes_selected: 0, pnl=0.0000, win_rate=0.0000
- no_selected: 765, pnl=-9784.0000, win_rate=0.0000

### KXBTC15M-26MAY112115-15

- candidate_count: 705
- selected_count: 692
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 9854.0000
- mean_particle_minus_market: 0.059916
- mean_particle_minus_current: 0.081862
- yes_selected: 479, pnl=-5287.0000, win_rate=0.0000
- no_selected: 213, pnl=15141.0000, win_rate=1.0000

### KXBTC15M-26MAY112130-30

- candidate_count: 371
- selected_count: 365
- settlement_result_yes: False
- total_counterfactual_pnl_cents: -11342.0000
- mean_particle_minus_market: 0.103023
- mean_particle_minus_current: 0.141222
- yes_selected: 365, pnl=-11342.0000, win_rate=0.0000
- no_selected: 0, pnl=0.0000, win_rate=0.0000

## EV Buckets

- ev_rank_1_of_5: candidates=902, selected=902, avg_pred_ev=27.6045, pnl=-5493.0000, avg_pnl=-6.0898, win_rate=0.0011
- ev_rank_2_of_5: candidates=902, selected=902, avg_pred_ev=21.5392, pnl=-4047.0000, avg_pnl=-4.4867, win_rate=0.0610
- ev_rank_3_of_5: candidates=903, selected=903, avg_pred_ev=16.4167, pnl=3237.0000, avg_pnl=3.5847, win_rate=0.2171
- ev_rank_4_of_5: candidates=902, selected=901, avg_pred_ev=9.9323, pnl=3864.0000, avg_pnl=4.2886, win_rate=0.3585
- ev_rank_5_of_5: candidates=903, selected=771, avg_pred_ev=2.8701, pnl=55.0000, avg_pnl=0.0713, win_rate=0.4293

## Worst Decisions

- KXBTC15M-26MAY112045-45 2026-05-12T00:38:33.782939+00:00 side=yes pnl=-51.0 particle=0.5255 market=0.505 current=0.535905
- KXBTC15M-26MAY112030-30 2026-05-12T00:16:53.261784+00:00 side=yes pnl=-50.0 particle=0.522 market=0.495 current=0.490527
- KXBTC15M-26MAY112045-45 2026-05-12T00:35:42.057550+00:00 side=yes pnl=-50.0 particle=0.5145 market=0.495 current=0.528645
- KXBTC15M-26MAY112045-45 2026-05-12T00:38:31.711686+00:00 side=yes pnl=-50.0 particle=0.5255 market=0.495 current=0.535905
- KXBTC15M-26MAY112045-45 2026-05-12T00:35:45.095907+00:00 side=yes pnl=-49.0 particle=0.512 market=0.485 current=0.528645
- KXBTC15M-26MAY112015-15 2026-05-12T00:02:38.024435+00:00 side=yes pnl=-48.0 particle=0.5255 market=0.475 current=0.498372
- KXBTC15M-26MAY112015-15 2026-05-12T00:04:30.762313+00:00 side=yes pnl=-48.0 particle=0.521 market=0.475 current=0.530772
- KXBTC15M-26MAY112015-15 2026-05-12T00:04:32.813022+00:00 side=yes pnl=-48.0 particle=0.5055 market=0.475 current=0.530772
- KXBTC15M-26MAY112015-15 2026-05-12T00:04:33.815221+00:00 side=yes pnl=-48.0 particle=0.5115 market=0.47 current=0.530772
- KXBTC15M-26MAY112045-45 2026-05-12T00:39:49.009097+00:00 side=yes pnl=-48.0 particle=0.495 market=0.465 current=0.453713
