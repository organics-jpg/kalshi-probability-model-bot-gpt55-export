# Replay Diagnostics

- source_report: `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\reports\materialized_online_logit_market_mean_rolling_vol_600s.json`
- candidate_count: 3398
- selected_count: 2941
- total_counterfactual_pnl_cents: 39779.0000
- particle_brier_minus_market_brier: -0.014040
- particle_brier_minus_current_brier: -0.005734
- particle_logloss_minus_market_logloss: -0.030120
- particle_logloss_minus_current_logloss: -0.020706
- selected_yes_count: 714
- selected_yes_pnl_cents: -843.0000
- selected_no_count: 2227
- selected_no_pnl_cents: 40622.0000

## Markets

### KXBTC15M-26MAY110245-45

- candidate_count: 659
- selected_count: 523
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 6874.0000
- mean_particle_minus_market: -0.022435
- mean_particle_minus_current: -0.055266
- yes_selected: 216, pnl=-2931.0000, win_rate=0.0000
- no_selected: 307, pnl=9805.0000, win_rate=1.0000

### KXBTC15M-26MAY110300-00

- candidate_count: 814
- selected_count: 715
- settlement_result_yes: True
- total_counterfactual_pnl_cents: -11413.0000
- mean_particle_minus_market: -0.046414
- mean_particle_minus_current: 0.000721
- yes_selected: 130, pnl=7659.0000, win_rate=1.0000
- no_selected: 585, pnl=-19072.0000, win_rate=0.0000

### KXBTC15M-26MAY110315-15

- candidate_count: 756
- selected_count: 708
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 5583.0000
- mean_particle_minus_market: -0.023986
- mean_particle_minus_current: -0.017794
- yes_selected: 178, pnl=-513.0000, win_rate=0.0000
- no_selected: 530, pnl=6096.0000, win_rate=1.0000

### KXBTC15M-26MAY110330-30

- candidate_count: 803
- selected_count: 719
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 28874.0000
- mean_particle_minus_market: -0.042632
- mean_particle_minus_current: -0.004047
- yes_selected: 155, pnl=-3333.0000, win_rate=0.0000
- no_selected: 564, pnl=32207.0000, win_rate=1.0000

### KXBTC15M-26MAY110345-45

- candidate_count: 366
- selected_count: 276
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 9861.0000
- mean_particle_minus_market: -0.029198
- mean_particle_minus_current: -0.021027
- yes_selected: 35, pnl=-1725.0000, win_rate=0.0000
- no_selected: 241, pnl=11586.0000, win_rate=1.0000

## EV Buckets

- ev_rank_1_of_5: candidates=679, selected=679, avg_pred_ev=9.9122, pnl=12800.0000, avg_pnl=18.8513, win_rate=0.5287
- ev_rank_2_of_5: candidates=680, selected=680, avg_pred_ev=4.6157, pnl=11453.0000, avg_pnl=16.8426, win_rate=0.6515
- ev_rank_3_of_5: candidates=679, selected=679, avg_pred_ev=2.6547, pnl=8172.0000, avg_pnl=12.0353, win_rate=0.6701
- ev_rank_4_of_5: candidates=680, selected=680, avg_pred_ev=1.1431, pnl=5431.0000, avg_pnl=7.9868, win_rate=0.6250
- ev_rank_5_of_5: candidates=680, selected=223, avg_pred_ev=-0.4269, pnl=1923.0000, avg_pnl=8.6233, win_rate=0.4036

## Worst Decisions

- KXBTC15M-26MAY110300-00 2026-05-11T06:49:54.975838+00:00 side=no pnl=-74.0 particle=0.24230045727021685 market=0.265 current=0.245845
- KXBTC15M-26MAY110300-00 2026-05-11T06:49:55.981840+00:00 side=no pnl=-74.0 particle=0.24211994408336576 market=0.265 current=0.245845
- KXBTC15M-26MAY110300-00 2026-05-11T06:49:57.032988+00:00 side=no pnl=-74.0 particle=0.2419309262431105 market=0.265 current=0.245845
- KXBTC15M-26MAY110300-00 2026-05-11T06:49:58.069727+00:00 side=no pnl=-74.0 particle=0.241744093765863 market=0.265 current=0.245845
- KXBTC15M-26MAY110300-00 2026-05-11T06:49:59.081437+00:00 side=no pnl=-74.0 particle=0.24156138203355196 market=0.265 current=0.245845
- KXBTC15M-26MAY110300-00 2026-05-11T06:49:40.377916+00:00 side=no pnl=-73.0 particle=0.2515596934635261 market=0.275 current=0.257455
- KXBTC15M-26MAY110300-00 2026-05-11T06:49:53.941379+00:00 side=no pnl=-73.0 particle=0.24248568386670258 market=0.275 current=0.245845
- KXBTC15M-26MAY110300-00 2026-05-11T06:50:02.126910+00:00 side=no pnl=-73.0 particle=0.23823147890470978 market=0.275 current=0.241992
- KXBTC15M-26MAY110300-00 2026-05-11T06:49:48.712530+00:00 side=no pnl=-72.0 particle=0.2413174061876268 market=0.285 current=0.245845
- KXBTC15M-26MAY110300-00 2026-05-11T06:49:52.807100+00:00 side=no pnl=-72.0 particle=0.24268832774228566 market=0.285 current=0.245845
