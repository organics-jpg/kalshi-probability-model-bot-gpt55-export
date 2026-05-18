# v28 Confidence-Shrink Schedule Bakeoff

Research-only fixed-entry FV calibration check.

- Freeze timestamp UTC: `2026-05-06T15:10:49.288038+00:00`
- Entry policy: `raw_v28_p50_edge0_fixed_selection`
- Forward denominator: `89`
- Hypothesis: Raw v28 direction may be useful while its probability magnitude is too hot. Compare non-fitted shrink schedules before promoting any new FV overlay.

## Forward Ranking

| rank | overlay | entries | settled | W/L | coverage | brier | d brier | logloss | d logloss | avg p | win rate | net c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | noise_shrink_light | 88 | 88 | 49/39 | 98.876404 | 0.219452 | -0.001853 | 0.622180 | -0.003116 | 0.607219 | 0.556818 | -247.000000 | none |
| 2 | phi_quarter_shrink_to50 | 88 | 88 | 49/39 | 98.876404 | 0.221201 | -0.000104 | 0.625837 | 0.000542 | 0.609634 | 0.556818 | -247.000000 | logloss_not_better_than_raw |
| 3 | raw_probability | 88 | 88 | 49/39 | 98.876404 | 0.221305 | 0.000000 | 0.625296 | 0.000000 | 0.623808 | 0.556818 | -247.000000 | none |
| 4 | noise_shrink_full | 88 | 88 | 49/39 | 98.876404 | 0.221597 | 0.000292 | 0.630894 | 0.005598 | 0.582868 | 0.556818 | -247.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 5 | phi_half_shrink_to50 | 88 | 88 | 49/39 | 98.876404 | 0.221651 | 0.000346 | 0.627322 | 0.002026 | 0.599143 | 0.556818 | -247.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 6 | const_shrink_090 | 88 | 88 | 49/39 | 98.876404 | 0.221711 | 0.000406 | 0.628553 | 0.003257 | 0.611427 | 0.556818 | -247.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 7 | noise_shrink_rmt_recency | 88 | 88 | 49/39 | 98.876404 | 0.222632 | 0.001328 | 0.632621 | 0.007326 | 0.598215 | 0.556818 | -247.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 8 | const_shrink_080 | 88 | 88 | 49/39 | 98.876404 | 0.222665 | 0.001360 | 0.632560 | 0.007265 | 0.599046 | 0.556818 | -247.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 9 | const_shrink_070 | 88 | 88 | 49/39 | 98.876404 | 0.224166 | 0.002861 | 0.637314 | 0.012018 | 0.586665 | 0.556818 | -247.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |

## Discovery Context

| rank | overlay | entries | settled | W/L | coverage | brier | d brier | logloss | d logloss | avg p | win rate | net c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | noise_shrink_light | 172 | 172 | 101/71 | 100.000000 | 0.222492 | -0.001502 | 0.629353 | -0.002544 | 0.609583 | 0.587209 | -81.000000 | none |
| 2 | phi_quarter_shrink_to50 | 172 | 172 | 101/71 | 100.000000 | 0.223604 | -0.000391 | 0.631424 | -0.000473 | 0.610948 | 0.587209 | -81.000000 | none |
| 3 | phi_half_shrink_to50 | 172 | 172 | 101/71 | 100.000000 | 0.223828 | -0.000167 | 0.632222 | 0.000325 | 0.599665 | 0.587209 | -81.000000 | logloss_not_better_than_raw |
| 4 | raw_probability | 172 | 172 | 101/71 | 100.000000 | 0.223995 | 0.000000 | 0.631897 | 0.000000 | 0.626302 | 0.587209 | -81.000000 | none |
| 5 | const_shrink_090 | 172 | 172 | 101/71 | 100.000000 | 0.224046 | 0.000051 | 0.634038 | 0.002141 | 0.613672 | 0.587209 | -81.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 6 | noise_shrink_full | 172 | 172 | 101/71 | 100.000000 | 0.224366 | 0.000372 | 0.636721 | 0.004825 | 0.585108 | 0.587209 | -81.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 7 | const_shrink_080 | 172 | 172 | 101/71 | 100.000000 | 0.224664 | 0.000669 | 0.637088 | 0.005191 | 0.601042 | 0.587209 | -81.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 8 | noise_shrink_rmt_recency | 172 | 172 | 101/71 | 100.000000 | 0.225193 | 0.001199 | 0.638134 | 0.006238 | 0.600378 | 0.587209 | -81.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 9 | const_shrink_070 | 172 | 172 | 101/71 | 100.000000 | 0.225848 | 0.001853 | 0.641009 | 0.009112 | 0.588411 | 0.587209 | -81.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |

## Discovery Buckets

| bucket | entries | settled | W/L | net c | phi penalty | raw brier | best brier | best overlay |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| all | 172 | 172 | 101/71 | -81.000000 | 2.340116 | 0.223995 | 0.222492 | noise_shrink_light |
| away_from_strike | 80 | 80 | 54/26 | -104.000000 | 0.712500 | 0.194381 | 0.192035 | noise_shrink_light |
| edge_ge_4pp | 76 | 76 | 44/32 | 315.000000 | 1.526316 | 0.213927 | 0.211806 | noise_shrink_light |
| edge_lt_4pp | 96 | 96 | 57/39 | -396.000000 | 2.984375 | 0.231965 | 0.230952 | noise_shrink_light |
| high_recross | 105 | 105 | 56/49 | -305.000000 | 3.376190 | 0.253546 | 0.251485 | phi_half_shrink_to50 |
| lower_recross | 67 | 67 | 45/22 | 224.000000 | 0.716418 | 0.177683 | 0.176592 | noise_shrink_light |
| near_strike | 92 | 92 | 47/45 | 23.000000 | 3.755435 | 0.249746 | 0.248908 | phi_half_shrink_to50 |
| phi_heavy_noise | 92 | 92 | 48/44 | 229.000000 | 3.804348 | 0.247679 | 0.247342 | noise_shrink_light |
| raw_p_50_60 | 87 | 87 | 46/41 | 419.000000 | 3.862069 | 0.245967 | 0.245967 | raw_probability |
| raw_p_60_plus | 85 | 85 | 55/30 | -500.000000 | 0.782353 | 0.201505 | 0.198266 | noise_shrink_light |
