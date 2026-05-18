# 90c Touch Stability Candidate Sweep

Research-only. This report searches for simple vetoes that improve 90c touch without relying on live order changes.

- Broad 90c hold trades: 579
- Native 90c hold trades: 63
- Native prior-v28-fair coverage: 57 / 63

## Broad Execution-Log Tier
| policy | entries | net c | avg c | LCB c | win rate | skipped L/W | days +/- | early c | late c | min day c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| veto_bad_fair_bands_and_ultra_early | 460 | 1640.0 | 3.57 | 1.49 | 0.946 | 20/99 | 11/2 | 1035.0 | 605.0 | -139.0 |
| veto_bad_fair_bands | 464 | 1576.0 | 3.40 | 1.30 | 0.944 | 19/96 | 11/2 | 953.0 | 623.0 | -139.0 |
| veto_fragile_fair_85_88_or_90_92 | 475 | 1475.0 | 3.11 | 0.98 | 0.941 | 17/87 | 11/2 | 843.0 | 632.0 | -139.0 |
| veto_fragile_fair_85_88 | 525 | 1325.0 | 2.52 | 0.42 | 0.935 | 11/43 | 11/2 | 768.0 | 557.0 | -121.0 |
| fair_ge88_and_not_ultra_early | 266 | 694.0 | 2.61 | -0.34 | 0.936 | 28/285 | 11/2 | 522.0 | 172.0 | -37.0 |
| veto_extreme_model_disagree | 568 | 812.0 | 1.43 | -0.75 | 0.924 | 2/9 | 11/2 | 575.0 | 237.0 | -112.0 |
| veto_ultra_early_touch | 574 | 766.0 | 1.33 | -0.84 | 0.923 | 1/4 | 11/2 | 538.0 | 228.0 | -112.0 |
| fair_buffer_ge92_only | 166 | 494.0 | 2.98 | -0.65 | 0.940 | 35/378 | 10/3 | 245.0 | 249.0 | -64.0 |
| base_90_touch_hold | 579 | 711.0 | 1.23 | -0.95 | 0.922 | 0/0 | 10/3 | 465.0 | 246.0 | -112.0 |
| late_window_le300 | 249 | 641.0 | 2.57 | -0.48 | 0.936 | 29/301 | 10/3 | 667.0 | -26.0 | -131.0 |

## Native Raw-Ticker Tier
| policy | entries | net c | avg c | LCB c | win rate | skipped L/W | days +/- | early c | late c | min day c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fair_ge88_and_not_ultra_early | 4 | 36.0 | 9.00 | 9.00 | 1.000 | 4/55 | 3/0 | 0.0 | 36.0 | 9.0 |
| fair_buffer_ge92_only | 3 | 27.0 | 9.00 | 9.00 | 1.000 | 4/56 | 3/0 | 0.0 | 27.0 | 9.0 |
| veto_fragile_fair_85_88 | 63 | 167.0 | 2.65 | -3.42 | 0.937 | 0/0 | 3/1 | 0.0 | 167.0 | -21.0 |
| base_90_touch_hold | 63 | 167.0 | 2.65 | -3.42 | 0.937 | 0/0 | 3/1 | 0.0 | 167.0 | -21.0 |
| veto_ultra_early_touch | 62 | 158.0 | 2.55 | -3.62 | 0.935 | 0/1 | 3/1 | 0.0 | 158.0 | -21.0 |
| veto_fragile_fair_85_88_or_90_92 | 62 | 158.0 | 2.55 | -3.62 | 0.935 | 0/1 | 3/1 | 0.0 | 158.0 | -30.0 |
| veto_extreme_model_disagree | 52 | 168.0 | 3.23 | -3.17 | 0.942 | 1/10 | 3/1 | 0.0 | 168.0 | -66.0 |
| veto_bad_fair_bands | 51 | 159.0 | 3.12 | -3.40 | 0.941 | 1/11 | 3/1 | 0.0 | 159.0 | -75.0 |
| veto_bad_fair_bands_and_ultra_early | 50 | 150.0 | 3.00 | -3.65 | 0.940 | 1/12 | 3/1 | 0.0 | 150.0 | -75.0 |
| late_window_le300 | 26 | -66.0 | -2.54 | -15.06 | 0.885 | 1/36 | 2/1 | 0.0 | -66.0 | -83.0 |

## Interpretation
- The highest broad PnL comes from vetoing fair < 50c and the empirical fragile fair bands 85-88c and 90-92c.
- The cleaner native tier is too small to prove the band rule, but it does not contradict the main idea that entry-time quality beats after-the-fact exits.
- The most trustworthy live candidate should be pre-registered as an entry/carry veto and then judged forward against plain 90c touch.
