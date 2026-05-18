# Rolling Online Probability Audit

Generated UTC: `20260504_100603Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Each block is scored by a model fit only on earlier closed markets from the same dataset.
- EV floor is selected from earlier markets only, with a high-coverage preference.
- This is diagnostic anti-overfit evidence, not strict pre-registered live promotion evidence.

## Protocol

- Block size: `20` recurring BTC 15m markets.
- Minimum prior blocks before scoring: `4`.
- Tradeability filters: `ask<=95`, `seconds_to_close>=120`.
- Prior edge floors scanned: `-20c, -15c, -10c, -5c, 0c, 2c, 5c, 10c, 15c, 20c`.
- Diagnostic robust gate also requires net per selected market >= `2c` and positive+coverage block rate >= `75.00%`.

## Combined Model Ranking

| rank | model | robust both datasets | combined net | combined acc/cov | min block pass rate | worst block |
|---:|---|---|---:|---:|---:|---:|
| 1 | `prob_gap_margin_C0.05` | False | 729.0c | 62.79%/95.56% | 63.64% | -428.0c |
| 2 | `prob_gap_margin_C0.1` | False | 85.0c | 62.28%/95.00% | 57.14% | -329.0c |
| 3 | `prob3_C0.1` | False | 68.0c | 62.94%/94.44% | 54.55% | -329.0c |
| 4 | `prob_gap_margin_C0.25` | False | -100.0c | 63.05%/94.72% | 42.86% | -329.0c |
| 5 | `prob3_C0.05` | False | -353.0c | 59.71%/97.22% | 54.55% | -608.0c |
| 6 | `prob_path_compact_C0.25` | False | -540.0c | 59.65%/96.39% | 36.36% | -508.0c |
| 7 | `prob_micro_full_C0.05` | False | -623.0c | 57.01%/93.06% | 28.57% | -455.0c |
| 8 | `prob_path_compact_C0.1` | False | -764.0c | 57.60%/95.00% | 36.36% | -342.0c |
| 9 | `prob3_C0.25` | False | -841.0c | 60.47%/95.56% | 36.36% | -409.0c |
| 10 | `prob_path_compact_C0.05` | False | -866.0c | 56.51%/93.89% | 27.27% | -455.0c |
| 11 | `prob_micro_full_C0.1` | False | -938.0c | 57.18%/94.72% | 28.57% | -369.0c |
| 12 | `prob_micro_full_C0.25` | False | -1060.0c | 56.40%/95.56% | 27.27% | -390.0c |

## Dataset Summary

| dataset | model | blocks | selected/base | acc | coverage | net | net/sel | positive+coverage blocks | worst block | robust |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| current | `prob_gap_margin_C0.05` | 11 | 206/220 | 64.56% | 93.64% | 247.0c | 1.2c | 7/63.64% | -428.0c | False |
| current | `prob_gap_margin_C0.1` | 11 | 203/220 | 65.52% | 92.27% | -35.0c | -0.2c | 7/63.64% | -329.0c | False |
| current | `prob_gap_margin_C0.25` | 11 | 203/220 | 67.00% | 92.27% | -154.0c | -0.8c | 5/45.45% | -329.0c | False |
| current | `prob3_C0.1` | 11 | 202/220 | 65.35% | 91.82% | -175.0c | -0.9c | 6/54.55% | -329.0c | False |
| current | `prob3_C0.05` | 11 | 212/220 | 59.91% | 96.36% | -564.0c | -2.7c | 6/54.55% | -608.0c | False |
| current | `prob3_C0.25` | 11 | 206/220 | 63.59% | 93.64% | -621.0c | -3.0c | 4/36.36% | -409.0c | False |
| current | `prob_path_compact_C0.25` | 11 | 208/220 | 59.62% | 94.55% | -961.0c | -4.6c | 4/36.36% | -508.0c | False |
| current | `prob_path_compact_C0.1` | 11 | 207/220 | 56.52% | 94.09% | -1006.0c | -4.9c | 4/36.36% | -342.0c | False |
| current | `prob_path_compact_C0.05` | 11 | 202/220 | 54.46% | 91.82% | -1202.0c | -6.0c | 3/27.27% | -455.0c | False |
| current | `prob_micro_full_C0.05` | 11 | 202/220 | 54.46% | 91.82% | -1212.0c | -6.0c | 4/36.36% | -455.0c | False |
| current | `prob_micro_full_C0.1` | 11 | 208/220 | 55.29% | 94.55% | -1263.0c | -6.1c | 4/36.36% | -369.0c | False |
| current | `prob_micro_full_C0.25` | 11 | 211/220 | 54.50% | 95.91% | -1380.0c | -6.5c | 3/27.27% | -390.0c | False |
| v21 | `prob_micro_full_C0.05` | 7 | 133/140 | 60.90% | 95.00% | 589.0c | 4.4c | 2/28.57% | -221.0c | False |
| v21 | `prob_gap_margin_C0.05` | 7 | 138/140 | 60.14% | 98.57% | 482.0c | 3.5c | 5/71.43% | -136.0c | False |
| v21 | `prob_path_compact_C0.25` | 7 | 139/140 | 59.71% | 99.29% | 421.0c | 3.0c | 3/42.86% | -224.0c | False |
| v21 | `prob_path_compact_C0.05` | 7 | 136/140 | 59.56% | 97.14% | 336.0c | 2.5c | 4/57.14% | -227.0c | False |
| v21 | `prob_micro_full_C0.1` | 7 | 133/140 | 60.15% | 95.00% | 325.0c | 2.4c | 2/28.57% | -282.0c | False |
| v21 | `prob_micro_full_C0.25` | 7 | 133/140 | 59.40% | 95.00% | 320.0c | 2.4c | 2/28.57% | -275.0c | False |
| v21 | `prob3_C0.1` | 7 | 138/140 | 59.42% | 98.57% | 243.0c | 1.8c | 4/57.14% | -151.0c | False |
| v21 | `prob_path_compact_C0.1` | 7 | 135/140 | 59.26% | 96.43% | 242.0c | 1.8c | 4/57.14% | -320.0c | False |
| v21 | `prob3_C0.05` | 7 | 138/140 | 59.42% | 98.57% | 211.0c | 1.5c | 4/57.14% | -160.0c | False |
| v21 | `prob_gap_margin_C0.1` | 7 | 139/140 | 57.55% | 99.29% | 120.0c | 0.9c | 4/57.14% | -133.0c | False |
| v21 | `prob_gap_margin_C0.25` | 7 | 138/140 | 57.25% | 98.57% | 54.0c | 0.4c | 3/42.86% | -133.0c | False |
| v21 | `prob3_C0.25` | 7 | 138/140 | 55.80% | 98.57% | -220.0c | -1.6c | 3/42.86% | -233.0c | False |

## Worst Blocks

| dataset | model | block | selected/base | acc | coverage | edge | net |
|---|---|---:|---:|---:|---:|---:|---:|
| current | `prob3_C0.05` | 14 | 20/20 | 30.00% | 100.00% | -5.0c | -608.0c |
| current | `prob_path_compact_C0.25` | 14 | 20/20 | 35.00% | 100.00% | -10.0c | -508.0c |
| current | `prob_path_compact_C0.05` | 10 | 20/20 | 35.00% | 100.00% | -15.0c | -455.0c |
| current | `prob_micro_full_C0.05` | 10 | 20/20 | 35.00% | 100.00% | -15.0c | -455.0c |
| current | `prob_gap_margin_C0.05` | 9 | 19/20 | 36.84% | 95.00% | -10.0c | -428.0c |
| current | `prob3_C0.05` | 9 | 19/20 | 36.84% | 95.00% | -10.0c | -428.0c |
| current | `prob3_C0.25` | 14 | 20/20 | 40.00% | 100.00% | -10.0c | -409.0c |
| current | `prob_micro_full_C0.25` | 11 | 20/20 | 40.00% | 100.00% | -10.0c | -390.0c |
| current | `prob_micro_full_C0.1` | 10 | 20/20 | 40.00% | 100.00% | -5.0c | -369.0c |
| current | `prob_micro_full_C0.25` | 14 | 19/20 | 47.37% | 95.00% | 0.0c | -351.0c |
| current | `prob_path_compact_C0.25` | 4 | 20/20 | 40.00% | 100.00% | -5.0c | -344.0c |
| current | `prob_micro_full_C0.25` | 4 | 20/20 | 40.00% | 100.00% | -5.0c | -344.0c |
| current | `prob_path_compact_C0.1` | 4 | 20/20 | 40.00% | 100.00% | -5.0c | -342.0c |
| current | `prob_gap_margin_C0.25` | 9 | 19/20 | 42.11% | 95.00% | -5.0c | -329.0c |
| current | `prob3_C0.25` | 9 | 19/20 | 42.11% | 95.00% | -5.0c | -329.0c |

## Read

- No rolling online probability model clears the robust diagnostic gate on both datasets.
- The live strict registered-signal gate remains the only promotion gate.
