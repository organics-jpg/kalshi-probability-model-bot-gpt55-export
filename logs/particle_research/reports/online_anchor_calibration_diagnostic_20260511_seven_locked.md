# Online Anchor Calibration Diagnostic

- run_count: 7
- spec_count: 12
- promotion_safe: False
- conclusion: No label-gated online anchor calibration clears strict locked-run probability and EV gates.

## Summary Rows

| spec | source | mode | runs | total_pnl_cents | raw_brier | cal_brier | raw_log_loss | cal_log_loss | positive_pnl | beats_raw | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all_runs |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| online_logit_market_particle75_lr003_marketlast | market_particle_75_25 | market_last | 7 | 158037.0000 | 0.191838 | 0.191845 | 0.552423 | 0.552446 | 6 | 2 | 4 | 4 | 4 | 3 | 3 | 0 | False |
| online_logit_brownian_lr003_marketlast | brownian | market_last | 7 | 173401.0000 | 0.196132 | 0.196134 | 0.571629 | 0.571624 | 6 | 4 | 4 | 3 | 3 | 7 | 4 | 0 | False |
| online_logit_particle_lr003_marketlast | particle | market_last | 7 | 172395.0000 | 0.196224 | 0.196227 | 0.571793 | 0.571791 | 6 | 4 | 3 | 3 | 3 | 6 | 4 | 0 | False |
| online_logit_brownian_market75_lr003_row | brownian_market_75_25 | row | 7 | 233752.0000 | 0.191867 | 0.203145 | 0.559577 | 0.582556 | 5 | 3 | 3 | 2 | 2 | 5 | 5 | 2 | False |
| online_logit_brownian_current75_lr003_row | brownian_current_75_25 | row | 7 | 234455.0000 | 0.191955 | 0.203579 | 0.559905 | 0.583409 | 5 | 3 | 2 | 2 | 2 | 5 | 5 | 1 | False |
| online_logit_brownian_particle75_lr003_row | brownian_particle_75_25 | row | 7 | 237053.0000 | 0.196134 | 0.206462 | 0.571630 | 0.592639 | 5 | 3 | 3 | 2 | 2 | 4 | 3 | 2 | False |
| online_logit_brownian_lr003_row | brownian | row | 7 | 236050.0000 | 0.196132 | 0.206478 | 0.571629 | 0.592658 | 5 | 3 | 3 | 2 | 2 | 4 | 3 | 2 | False |
| online_logit_particle_lr003_row | particle | row | 7 | 236716.0000 | 0.196224 | 0.206528 | 0.571793 | 0.592838 | 5 | 3 | 3 | 2 | 2 | 4 | 3 | 2 | False |
| online_logit_market_particle75_lr003_row | market_particle_75_25 | row | 7 | 175279.0000 | 0.191838 | 0.207269 | 0.552423 | 0.588876 | 5 | 2 | 2 | 3 | 2 | 4 | 5 | 1 | False |
| online_logit_market_lr003_row | market | row | 7 | 96523.0000 | 0.196066 | 0.211108 | 0.562869 | 0.601392 | 5 | 2 | 2 | 2 | 2 | 4 | 3 | 1 | False |
| online_logit_current_lr003_row | current | row | 7 | 88387.0000 | 0.195131 | 0.214145 | 0.563595 | 0.607929 | 5 | 3 | 2 | 3 | 3 | 5 | 4 | 2 | False |
| online_logit_brownian_lr010_row | brownian | row | 7 | 142215.0000 | 0.196132 | 0.266086 | 0.571629 | 0.760414 | 3 | 2 | 2 | 2 | 2 | 5 | 3 | 2 | False |
