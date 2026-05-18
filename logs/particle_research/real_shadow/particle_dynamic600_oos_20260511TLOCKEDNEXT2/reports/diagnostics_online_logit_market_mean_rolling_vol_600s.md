# Replay Diagnostics

- source_report: `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\reports\materialized_online_logit_market_mean_rolling_vol_600s.json`
- candidate_count: 3414
- selected_count: 2690
- total_counterfactual_pnl_cents: 3298.0000
- particle_brier_minus_market_brier: 0.002128
- particle_brier_minus_current_brier: 0.002966
- particle_logloss_minus_market_logloss: -0.004081
- particle_logloss_minus_current_logloss: 0.009217
- selected_yes_count: 773
- selected_yes_pnl_cents: 41661.0000
- selected_no_count: 1917
- selected_no_pnl_cents: -38363.0000

## Markets

### KXBTC15M-26MAY110530-30

- candidate_count: 6
- selected_count: 6
- settlement_result_yes: False
- total_counterfactual_pnl_cents: -11.0000
- mean_particle_minus_market: 0.353681
- mean_particle_minus_current: 0.192751
- yes_selected: 6, pnl=-11.0000, win_rate=0.0000
- no_selected: 0, pnl=0.0000, win_rate=0.0000

### KXBTC15M-26MAY110545-45

- candidate_count: 848
- selected_count: 684
- settlement_result_yes: True
- total_counterfactual_pnl_cents: 33531.0000
- mean_particle_minus_market: 0.015495
- mean_particle_minus_current: 0.012155
- yes_selected: 526, pnl=39645.0000, win_rate=1.0000
- no_selected: 158, pnl=-6114.0000, win_rate=0.0000

### KXBTC15M-26MAY110600-00

- candidate_count: 816
- selected_count: 695
- settlement_result_yes: True
- total_counterfactual_pnl_cents: -11208.0000
- mean_particle_minus_market: -0.061293
- mean_particle_minus_current: -0.034473
- yes_selected: 75, pnl=3356.0000, win_rate=1.0000
- no_selected: 620, pnl=-14564.0000, win_rate=0.0000

### KXBTC15M-26MAY110615-15

- candidate_count: 783
- selected_count: 499
- settlement_result_yes: True
- total_counterfactual_pnl_cents: -11776.0000
- mean_particle_minus_market: -0.024443
- mean_particle_minus_current: -0.010356
- yes_selected: 60, pnl=2026.0000, win_rate=1.0000
- no_selected: 439, pnl=-13802.0000, win_rate=0.0000

### KXBTC15M-26MAY110630-30

- candidate_count: 712
- selected_count: 602
- settlement_result_yes: True
- total_counterfactual_pnl_cents: -8475.0000
- mean_particle_minus_market: -0.026439
- mean_particle_minus_current: -0.012850
- yes_selected: 5, pnl=190.0000, win_rate=1.0000
- no_selected: 597, pnl=-8665.0000, win_rate=0.0000

### KXBTC15M-26MAY110645-45

- candidate_count: 249
- selected_count: 204
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 1237.0000
- mean_particle_minus_market: -0.012843
- mean_particle_minus_current: 0.030265
- yes_selected: 101, pnl=-3545.0000, win_rate=0.0000
- no_selected: 103, pnl=4782.0000, win_rate=1.0000

## EV Buckets

- ev_rank_1_of_5: candidates=682, selected=682, avg_pred_ev=13.5776, pnl=8795.0000, avg_pnl=12.8959, win_rate=0.3651
- ev_rank_2_of_5: candidates=683, selected=683, avg_pred_ev=5.2576, pnl=-901.0000, avg_pnl=-1.3192, win_rate=0.2489
- ev_rank_3_of_5: candidates=683, selected=683, avg_pred_ev=2.4399, pnl=-2022.0000, avg_pnl=-2.9605, win_rate=0.2621
- ev_rank_4_of_5: candidates=683, selected=642, avg_pred_ev=0.7014, pnl=-2574.0000, avg_pnl=-4.0093, win_rate=0.2664
- ev_rank_5_of_5: candidates=683, selected=0, avg_pred_ev=-0.5971, pnl=0.0000, avg_pnl=0.0000, win_rate=0.0000

## Worst Decisions

- KXBTC15M-26MAY110545-45 2026-05-11T09:41:03.268592+00:00 side=no pnl=-94.0 particle=0.042559343543670185 market=0.065 current=0.04232
- KXBTC15M-26MAY110545-45 2026-05-11T09:41:04.295049+00:00 side=no pnl=-94.0 particle=0.0422230861158949 market=0.065 current=0.04232
- KXBTC15M-26MAY110545-45 2026-05-11T09:40:59.271045+00:00 side=no pnl=-93.0 particle=0.04386846258837698 market=0.075 current=0.04232
- KXBTC15M-26MAY110545-45 2026-05-11T09:41:00.269374+00:00 side=no pnl=-93.0 particle=0.043541611125337984 market=0.075 current=0.04232
- KXBTC15M-26MAY110545-45 2026-05-11T09:41:01.274690+00:00 side=no pnl=-93.0 particle=0.04321241160980387 market=0.075 current=0.04232
- KXBTC15M-26MAY110545-45 2026-05-11T09:41:02.259815+00:00 side=no pnl=-93.0 particle=0.042889772772648604 market=0.075 current=0.04232
- KXBTC15M-26MAY110545-45 2026-05-11T09:41:05.377968+00:00 side=no pnl=-93.0 particle=0.04186830186634792 market=0.07 current=0.04232
- KXBTC15M-26MAY110545-45 2026-05-11T09:40:57.272317+00:00 side=no pnl=-92.0 particle=0.044522631745585475 market=0.08 current=0.04232
- KXBTC15M-26MAY110545-45 2026-05-11T09:40:58.271846+00:00 side=no pnl=-92.0 particle=0.04419553101046128 market=0.085 current=0.04232
- KXBTC15M-26MAY110545-45 2026-05-11T09:41:30.302263+00:00 side=no pnl=-90.0 particle=0.07546232331149676 market=0.105 current=0.132288
