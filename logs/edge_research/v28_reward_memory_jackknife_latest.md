# v28 Reward-Memory Jackknife

Leave-one-market-out anti-overfit check for reward-memory FV controllers.

- Reward freeze timestamp UTC: `2026-05-06T01:46:48.111889+00:00`
- Selected/settled/markets: `172/172/172`

## Robustness

| overlay | pass | failures | full brier d | worst brier d | best brier d | full logloss d | worst logloss d |
|---|---|---:|---:|---:|---:|---:|---:|
| reward_memory_logit125 | False | 172 | 0.001503 | 0.001616 | 0.001164 | 0.001625 | 0.001902 |
| logit125_probability | False | 172 | 0.002276 | 0.002428 | 0.001809 | 0.002762 | 0.003140 |
| reward_memory_plus05 | False | 172 | 0.004831 | 0.005097 | 0.004491 | 0.008144 | 0.008668 |
| plus05_probability | False | 172 | 0.006406 | 0.006721 | 0.005961 | 0.011122 | 0.011744 |

## Worst Removals

| overlay | removed market | removed W/L | removed net c | brier d | logloss d |
|---|---|---:|---:|---:|---:|
| reward_memory_logit125 | KXBTC15M-26MAY061800-00 | 1/0 | 60.000000 | 0.001616 | 0.001889 |
| reward_memory_logit125 | KXBTC15M-26MAY061430-30 | 1/0 | 62.000000 | 0.001615 | 0.001877 |
| reward_memory_logit125 | KXBTC15M-26MAY060415-15 | 1/0 | 62.000000 | 0.001615 | 0.001876 |
| logit125_probability | KXBTC15M-26MAY061430-30 | 1/0 | 62.000000 | 0.002428 | 0.003107 |
| logit125_probability | KXBTC15M-26MAY060415-15 | 1/0 | 62.000000 | 0.002427 | 0.003106 |
| logit125_probability | KXBTC15M-26MAY061800-00 | 1/0 | 60.000000 | 0.002427 | 0.003123 |
| reward_memory_plus05 | KXBTC15M-26MAY061900-00 | 1/0 | 128.000000 | 0.005097 | 0.008668 |
| reward_memory_plus05 | KXBTC15M-26MAY070815-15 | 1/0 | 108.000000 | 0.005084 | 0.008641 |
| reward_memory_plus05 | KXBTC15M-26MAY051915-15 | 1/0 | 116.000000 | 0.005082 | 0.008641 |
| plus05_probability | KXBTC15M-26MAY070815-15 | 1/0 | 108.000000 | 0.006721 | 0.011744 |
| plus05_probability | KXBTC15M-26MAY061900-00 | 1/0 | 128.000000 | 0.006720 | 0.011743 |
| plus05_probability | KXBTC15M-26MAY060715-15 | 1/0 | 98.000000 | 0.006720 | 0.011743 |
