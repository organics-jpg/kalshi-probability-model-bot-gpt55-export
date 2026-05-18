# v28 Composite False-Conviction Repair Robustness

Research-only leave-one-market-out audit.

## Interpretation

- Best robustness-ranked scorer is farthest_boundary with full net 133.0c and coverage 75.0%.
- Leave-one-market-out worst net is 69.0c; negative-net exclusions 0.
- This remains diagnostic; live use requires the frozen forward validator to mature.

## Scorers

| rank | scorer | full net c | full coverage | leaveouts | worst net c | worst delta c | worst coverage | neg net | cov fail | robust |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | farthest_boundary | 133.000000 | 75.000000 | 145 | 69.000000 | 603.000000 | 75.496689 | 0 | 0 | True |
| 2 | lowest_recross | 85.000000 | 75.000000 | 145 | -2.000000 | 555.000000 | 75.496689 | 2 | 0 | False |
| 3 | prob_edge_stability | 75.000000 | 75.000000 | 145 | -13.000000 | 545.000000 | 75.496689 | 5 | 0 | False |
| 4 | highest_raw_p | 31.000000 | 75.000000 | 145 | -60.000000 | 497.000000 | 75.496689 | 30 | 0 | False |

## Best Scorer Worst Leaveouts

| excluded market | candidate net c | delta c | coverage | W/L | repairs | danger |
|---|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070845-45 | 69.000000 | 781.000000 | 75.496689 | 79/35 | 53 | 50 |
| KXBTC15M-26MAY062200-00 | 71.000000 | 781.000000 | 75.496689 | 79/35 | 53 | 50 |
| KXBTC15M-26MAY060945-45 | 79.000000 | 781.000000 | 75.496689 | 79/35 | 53 | 50 |
| KXBTC15M-26MAY062000-00 | 79.000000 | 781.000000 | 75.496689 | 79/35 | 53 | 50 |
| KXBTC15M-26MAY051945-45 | 81.000000 | 781.000000 | 75.496689 | 79/35 | 53 | 50 |
