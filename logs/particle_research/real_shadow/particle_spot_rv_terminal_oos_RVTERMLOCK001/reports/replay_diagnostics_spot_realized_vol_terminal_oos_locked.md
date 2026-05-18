# Replay Diagnostics

- source_report: `logs\particle_research\real_shadow\particle_spot_rv_terminal_oos_RVTERMLOCK001\reports\materialized_spot_realized_vol_terminal_oos_locked.json`
- candidate_count: 4512
- selected_count: 4108
- total_counterfactual_pnl_cents: 17528.0000
- particle_brier_minus_market_brier: 0.005339
- particle_brier_minus_current_brier: 0.010980
- particle_logloss_minus_market_logloss: 0.044185
- particle_logloss_minus_current_logloss: 0.055743
- selected_yes_count: 2304
- selected_yes_pnl_cents: -33777.0000
- selected_no_count: 1804
- selected_no_pnl_cents: 51305.0000

## Markets

### KXBTC15M-26MAY112000-00

- candidate_count: 402
- selected_count: 402
- settlement_result_yes: False
- total_counterfactual_pnl_cents: -5078.0000
- mean_particle_minus_market: 0.160351
- mean_particle_minus_current: 0.118604
- yes_selected: 402, pnl=-5078.0000, win_rate=0.0000
- no_selected: 0, pnl=0.0000, win_rate=0.0000

### KXBTC15M-26MAY112015-15

- candidate_count: 712
- selected_count: 651
- settlement_result_yes: False
- total_counterfactual_pnl_cents: -4448.0000
- mean_particle_minus_market: 0.069547
- mean_particle_minus_current: 0.086530
- yes_selected: 567, pnl=-8962.0000, win_rate=0.0000
- no_selected: 84, pnl=4514.0000, win_rate=1.0000

### KXBTC15M-26MAY112030-30

- candidate_count: 767
- selected_count: 699
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 8231.0000
- mean_particle_minus_market: 0.035367
- mean_particle_minus_current: 0.049824
- yes_selected: 458, pnl=-4934.0000, win_rate=0.0000
- no_selected: 241, pnl=13165.0000, win_rate=1.0000

### KXBTC15M-26MAY112045-45

- candidate_count: 790
- selected_count: 671
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 21377.0000
- mean_particle_minus_market: -0.010453
- mean_particle_minus_current: 0.008235
- yes_selected: 225, pnl=-5139.0000, win_rate=0.0000
- no_selected: 446, pnl=26516.0000, win_rate=1.0000

### KXBTC15M-26MAY112100-00

- candidate_count: 765
- selected_count: 765
- settlement_result_yes: True
- total_counterfactual_pnl_cents: -9784.0000
- mean_particle_minus_market: -0.130509
- mean_particle_minus_current: -0.132582
- yes_selected: 0, pnl=0.0000, win_rate=0.0000
- no_selected: 765, pnl=-9784.0000, win_rate=0.0000

### KXBTC15M-26MAY112115-15

- candidate_count: 705
- selected_count: 671
- settlement_result_yes: False
- total_counterfactual_pnl_cents: 12179.0000
- mean_particle_minus_market: 0.014371
- mean_particle_minus_current: 0.036317
- yes_selected: 434, pnl=-3704.0000, win_rate=0.0000
- no_selected: 237, pnl=15883.0000, win_rate=1.0000

### KXBTC15M-26MAY112130-30

- candidate_count: 371
- selected_count: 249
- settlement_result_yes: False
- total_counterfactual_pnl_cents: -4949.0000
- mean_particle_minus_market: 0.025726
- mean_particle_minus_current: 0.063925
- yes_selected: 218, pnl=-5960.0000, win_rate=0.0000
- no_selected: 31, pnl=1011.0000, win_rate=1.0000

## EV Buckets

- ev_rank_1_of_5: candidates=902, selected=902, avg_pred_ev=16.0272, pnl=-4222.0000, avg_pnl=-4.6807, win_rate=0.0299
- ev_rank_2_of_5: candidates=902, selected=902, avg_pred_ev=10.6704, pnl=667.0000, avg_pnl=0.7395, win_rate=0.1330
- ev_rank_3_of_5: candidates=903, selected=903, avg_pred_ev=7.4144, pnl=9039.0000, avg_pnl=10.0100, win_rate=0.2802
- ev_rank_4_of_5: candidates=902, selected=900, avg_pred_ev=4.1051, pnl=7400.0000, avg_pnl=8.2222, win_rate=0.4133
- ev_rank_5_of_5: candidates=903, selected=501, avg_pred_ev=0.2284, pnl=4644.0000, avg_pnl=9.2695, win_rate=0.5329

## Worst Decisions

- KXBTC15M-26MAY112015-15 2026-05-12T00:03:31.900746+00:00 side=yes pnl=-57.0 particle=0.5914140074156478 market=0.565 current=0.642421
- KXBTC15M-26MAY112045-45 2026-05-12T00:35:35.994465+00:00 side=yes pnl=-57.0 particle=0.5845270109567298 market=0.565 current=0.628657
- KXBTC15M-26MAY112045-45 2026-05-12T00:39:03.581697+00:00 side=yes pnl=-57.0 particle=0.5852521665125032 market=0.565 current=0.633191
- KXBTC15M-26MAY112045-45 2026-05-12T00:39:01.536805+00:00 side=yes pnl=-56.0 particle=0.5850155226820751 market=0.555 current=0.633191
- KXBTC15M-26MAY112045-45 2026-05-12T00:39:02.549547+00:00 side=yes pnl=-56.0 particle=0.5851324750161552 market=0.555 current=0.633191
- KXBTC15M-26MAY112045-45 2026-05-12T00:39:04.591971+00:00 side=yes pnl=-56.0 particle=0.5853698113485593 market=0.555 current=0.633191
- KXBTC15M-26MAY112015-15 2026-05-12T00:03:32.905440+00:00 side=yes pnl=-55.0 particle=0.5913550594699393 market=0.545 current=0.642421
- KXBTC15M-26MAY112015-15 2026-05-12T00:03:33.905751+00:00 side=yes pnl=-55.0 particle=0.5912764871178929 market=0.545 current=0.642421
- KXBTC15M-26MAY112045-45 2026-05-12T00:38:32.777784+00:00 side=yes pnl=-51.0 particle=0.5205217002629126 market=0.505 current=0.535905
- KXBTC15M-26MAY112045-45 2026-05-12T00:38:33.782939+00:00 side=yes pnl=-51.0 particle=0.5205483439987546 market=0.505 current=0.535905
