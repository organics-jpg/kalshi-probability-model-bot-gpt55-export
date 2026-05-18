# Replay Diagnostics

- source_report: `logs\particle_research\real_shadow\particle_dynamic_oos_20260511TLOCKEDNEXT\reports\materialized_online_logit_market_mean_rolling_vol_600s.json`
- candidate_count: 3501
- selected_count: 2884
- total_counterfactual_pnl_cents: 39334.0000
- particle_brier_minus_market_brier: -0.016512
- particle_brier_minus_current_brier: -0.009221
- particle_logloss_minus_market_logloss: -0.028897
- particle_logloss_minus_current_logloss: -0.026466
- selected_yes_count: 635
- selected_yes_pnl_cents: -7925.0000
- selected_no_count: 2249
- selected_no_pnl_cents: 47259.0000

## Markets

### KXBTC15M-26MAY110415-15

- candidate_count: 534
- selected_count: 444
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 5014.0000
- mean_particle_minus_market: -0.030964
- mean_particle_minus_current: -0.003323
- yes_selected: 225, pnl=-3635.0000, win_rate=0.0000
- no_selected: 219, pnl=8649.0000, win_rate=1.0000

### KXBTC15M-26MAY110430-30

- candidate_count: 782
- selected_count: 726
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 31963.0000
- mean_particle_minus_market: -0.042601
- mean_particle_minus_current: -0.035053
- yes_selected: 129, pnl=-3659.0000, win_rate=0.0000
- no_selected: 597, pnl=35622.0000, win_rate=1.0000

### KXBTC15M-26MAY110445-45

- candidate_count: 781
- selected_count: 638
- settlement_result_yes: True
- total_counterfactual_pnl_cents: -6846.0000
- mean_particle_minus_market: -0.042998
- mean_particle_minus_current: -0.010879
- yes_selected: 25, pnl=732.0000, win_rate=1.0000
- no_selected: 613, pnl=-7578.0000, win_rate=0.0000

### KXBTC15M-26MAY110500-00

- candidate_count: 791
- selected_count: 621
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 17190.0000
- mean_particle_minus_market: -0.017836
- mean_particle_minus_current: -0.014751
- yes_selected: 197, pnl=-2661.0000, win_rate=0.0000
- no_selected: 424, pnl=19851.0000, win_rate=1.0000

### KXBTC15M-26MAY110515-15

- candidate_count: 613
- selected_count: 455
- settlement_result_yes: True
- total_counterfactual_pnl_cents: -7987.0000
- mean_particle_minus_market: -0.020576
- mean_particle_minus_current: -0.017398
- yes_selected: 59, pnl=1298.0000, win_rate=1.0000
- no_selected: 396, pnl=-9285.0000, win_rate=0.0000

## EV Buckets

- ev_rank_1_of_5: candidates=700, selected=700, avg_pred_ev=11.0899, pnl=15296.0000, avg_pnl=21.8514, win_rate=0.5000
- ev_rank_2_of_5: candidates=700, selected=700, avg_pred_ev=5.2411, pnl=11492.0000, avg_pnl=16.4171, win_rate=0.4300
- ev_rank_3_of_5: candidates=700, selected=700, avg_pred_ev=2.6410, pnl=9643.0000, avg_pnl=13.7757, win_rate=0.5529
- ev_rank_4_of_5: candidates=700, selected=700, avg_pred_ev=0.7905, pnl=1694.0000, avg_pnl=2.4200, win_rate=0.3371
- ev_rank_5_of_5: candidates=701, selected=84, avg_pred_ev=-0.6104, pnl=1209.0000, avg_pnl=14.3929, win_rate=0.5952

## Worst Decisions

- KXBTC15M-26MAY110430-30 2026-05-11T08:26:28.661272+00:00 side=yes pnl=-74.0 particle=0.7635704650807489 market=0.735 current=0.886509
- KXBTC15M-26MAY110430-30 2026-05-11T08:26:29.684344+00:00 side=yes pnl=-74.0 particle=0.7641115294529797 market=0.735 current=0.886509
- KXBTC15M-26MAY110430-30 2026-05-11T08:26:31.711693+00:00 side=yes pnl=-74.0 particle=0.7651934105049005 market=0.735 current=0.886509
- KXBTC15M-26MAY110430-30 2026-05-11T08:26:32.714069+00:00 side=yes pnl=-74.0 particle=0.7657331438776704 market=0.735 current=0.886509
- KXBTC15M-26MAY110430-30 2026-05-11T08:26:33.716587+00:00 side=yes pnl=-74.0 particle=0.7662761871406687 market=0.735 current=0.886509
- KXBTC15M-26MAY110430-30 2026-05-11T08:26:30.686559+00:00 side=yes pnl=-73.0 particle=0.7646447339842937 market=0.725 current=0.886509
- KXBTC15M-26MAY110415-15 2026-05-11T08:07:04.082259+00:00 side=yes pnl=-62.0 particle=0.6333834754337038 market=0.615 current=0.628262
- KXBTC15M-26MAY110415-15 2026-05-11T08:07:05.093652+00:00 side=yes pnl=-62.0 particle=0.6335200106892931 market=0.615 current=0.628262
- KXBTC15M-26MAY110415-15 2026-05-11T08:07:06.093546+00:00 side=yes pnl=-62.0 particle=0.6336554063523896 market=0.615 current=0.628262
- KXBTC15M-26MAY110415-15 2026-05-11T08:07:07.099794+00:00 side=yes pnl=-62.0 particle=0.6337319077659388 market=0.615 current=0.74535
