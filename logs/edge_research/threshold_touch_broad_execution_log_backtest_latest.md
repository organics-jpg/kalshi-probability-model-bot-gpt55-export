# Broad Execution-Log Threshold Touch Backtest

Research-only. This is log-derived historical replay, not live trading and not continuous exchange replay.

- Labels loaded: 2730
- Labels with close time: 2730
- Execution log files seen: 26
- Execution log files used: 25
- Execution events scanned: 120017
- Side observations joined to labels: 116044
- Markets seen before label join: 752
- Markets with joined log observations: 729

## Key Include-Left-Censored Rows
| threshold | gate | entries | wins if held | losses if held | exits | exited winners | exited losers | net c | avg c | LCB c |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 80 | hold | 687 | 556 | 131 | 0 | 0 | 0 | -734.0 | -1.07 | -4.01 |
| 80 | v28_fair_lt_70 | 687 | 556 | 131 | 333 | 226 | 107 | -762.0 | -1.11 | -3.05 |
| 80 | v28_fair_lt_75 | 687 | 556 | 131 | 408 | 297 | 111 | -1229.0 | -1.79 | -3.57 |
| 80 | v28_fair_lt_80 | 687 | 556 | 131 | 462 | 345 | 117 | -1095.0 | -1.59 | -3.14 |
| 90 | hold | 579 | 534 | 45 | 0 | 0 | 0 | 711.0 | 1.23 | -0.95 |
| 90 | v28_fair_lt_70 | 579 | 534 | 45 | 98 | 70 | 28 | 501.0 | 0.87 | -0.95 |
| 90 | v28_fair_lt_75 | 579 | 534 | 45 | 126 | 97 | 29 | 395.0 | 0.68 | -1.06 |
| 90 | v28_fair_lt_80 | 579 | 534 | 45 | 162 | 130 | 32 | 504.0 | 0.87 | -0.69 |

## Top Configurations
| threshold | mode | gate | entries | wins if held | losses if held | exits | left censored | net c | avg c | LCB c |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 90 | include_left_censored | hold | 579 | 534 | 45 | 0 | 6 | 711.0 | 1.23 | -0.95 |
| 90 | strict_cross | hold | 575 | 530 | 45 | 0 | 0 | 675.0 | 1.17 | -1.02 |
| 90 | include_left_censored | v28_fair_lt_60 | 579 | 534 | 45 | 63 | 6 | 561.0 | 0.97 | -0.96 |
| 90 | strict_cross | v28_fair_lt_60 | 575 | 530 | 45 | 63 | 0 | 525.0 | 0.91 | -1.03 |
| 90 | include_left_censored | v28_fair_lt_80 | 579 | 534 | 45 | 162 | 6 | 504.0 | 0.87 | -0.69 |
| 90 | include_left_censored | v28_fair_lt_70 | 579 | 534 | 45 | 98 | 6 | 501.0 | 0.87 | -0.95 |
| 90 | strict_cross | v28_fair_lt_80 | 575 | 530 | 45 | 162 | 0 | 468.0 | 0.81 | -0.75 |
| 90 | strict_cross | v28_fair_lt_70 | 575 | 530 | 45 | 98 | 0 | 465.0 | 0.81 | -1.02 |
| 90 | include_left_censored | v28_fair_lt_75 | 579 | 534 | 45 | 126 | 6 | 395.0 | 0.68 | -1.06 |
| 90 | include_left_censored | v28_fair_lt_85 | 579 | 534 | 45 | 205 | 6 | 373.0 | 0.64 | -0.83 |
| 90 | strict_cross | v28_fair_lt_75 | 575 | 530 | 45 | 126 | 0 | 359.0 | 0.62 | -1.13 |
| 90 | strict_cross | v28_fair_lt_85 | 575 | 530 | 45 | 205 | 0 | 337.0 | 0.59 | -0.89 |
| 80 | include_left_censored | v28_fair_lt_60 | 687 | 556 | 131 | 217 | 87 | -554.0 | -0.81 | -3.10 |
| 80 | include_left_censored | hold | 687 | 556 | 131 | 0 | 87 | -734.0 | -1.07 | -4.01 |
| 80 | include_left_censored | v28_fair_lt_70 | 687 | 556 | 131 | 333 | 87 | -762.0 | -1.11 | -3.05 |
| 80 | strict_cross | v28_fair_lt_70 | 630 | 506 | 124 | 296 | 0 | -767.0 | -1.22 | -3.28 |
| 80 | strict_cross | v28_fair_lt_60 | 630 | 506 | 124 | 200 | 0 | -830.0 | -1.32 | -3.74 |
| 80 | strict_cross | v28_fair_lt_75 | 630 | 506 | 124 | 364 | 0 | -912.0 | -1.45 | -3.30 |
| 80 | strict_cross | v28_fair_lt_80 | 630 | 506 | 124 | 413 | 0 | -948.0 | -1.50 | -3.15 |
| 80 | strict_cross | v28_fair_lt_85 | 630 | 506 | 124 | 449 | 0 | -968.0 | -1.54 | -3.04 |

## Correctness Notes
- This tier uses historical bot execution observations, so it is much broader than native raw ticker replay but lower confidence for fillability.
- Entries are still first threshold touches by market, not FV-filtered approvals.
- Exit PnL is only scored when a later log row has both a v28 fair trigger and an inferable same-side bid.
- Treat this as a hypothesis generator; the native replay and future frozen live-forward rows remain the cleaner evidence tiers.
