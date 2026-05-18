# Phi Reward Memory Live Trade Failure Audit - 2026-05-10

Source files: trades.csv, market_results.csv, execution_events.ndjson.

## Summary

- Trades scored: 57
- Actual net after fees: $-3.025
- Gross before fees: $-0.442
- Fees: $2.583
- Hypothetical entry-to-settlement hold net: $+7.633
- Actual minus hold: $-10.658

| Bucket | Trades | Actual net | Hold net | Actual - hold | Fees |
|---|---:|---:|---:|---:|---:|
| Correct side, lost on exit | 16 | $-3.371 | $+15.908 | $-19.279 | $0.893 |
| Wrong side, lost | 23 | $-2.851 | $-11.431 | $+8.580 | $0.805 |
| Correct side, profitable | 8 | $+1.110 | $+9.350 | $-8.240 | $0.410 |
| Wrong side, salvaged profit | 10 | $+2.087 | $-6.194 | $+8.281 | $0.475 |

## Individual Trades

| # | Market | Side | Entry -> Exit | Result | Net | Hold Net | Delta vs Hold | Entry Source | Exit Reason | Diagnosis |
|---:|---|---|---:|---|---:|---:|---:|---|---|---|
| 1 | KXBTC15M-26MAY092330-30 | YES | 9.8 -> 4.3 | NO | $-0.188 | $-0.308 | $+0.120 | explore raw=False | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 2 | KXBTC15M-26MAY092345-45 | YES | 73.0 -> 79.0 | YES | $+0.060 | $+0.510 | $-0.450 | keep raw=True | mushroom_v28_exit_value_over_hold | Correct side, profitable, but usually left settlement upside. |
| 3 | KXBTC15M-26MAY092345-45 | NO | 5.4 -> 2.4 | YES | $-0.114 | $-0.174 | $+0.060 | keep raw=True | mushroom_v28_exit_value_over_hold | Wrong settlement side; exit reduced what holding would have lost. |
| 4 | KXBTC15M-26MAY100015-15 | NO | 78.0 -> 74.0 | NO | $-0.130 | $+0.410 | $-0.540 | keep raw=True | mushroom_v28_probability_reduce | Correct settlement side, bad early exit. |
| 5 | KXBTC15M-26MAY100015-15 | NO | 79.0 -> 73.0 | NO | $-0.240 | $+0.600 | $-0.840 | keep raw=True | mushroom_v28_probability_reduce | Correct settlement side, bad early exit. |
| 6 | KXBTC15M-26MAY100015-15 | NO | 78.0 -> 81.0 | NO | $+0.020 | $+0.630 | $-0.610 | keep raw=True | mushroom_v28_exit_value_over_hold | Correct side, profitable, but usually left settlement upside. |
| 7 | KXBTC15M-26MAY100015-15 | YES | 8.0 -> 5.1 | NO | $-0.120 | $-0.260 | $+0.140 | keep raw=True | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 8 | KXBTC15M-26MAY100015-15 | YES | 7.0 -> 6.1 | NO | $-0.040 | $-0.150 | $+0.110 | keep raw=True | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 9 | KXBTC15M-26MAY100015-15 | YES | 5.9 -> 2.2 | NO | $-0.090 | $-0.130 | $+0.040 | explore raw=False | mushroom_v28_exit_value_over_hold | Wrong settlement side and still lost. |
| 10 | KXBTC15M-26MAY100015-15 | YES | 2.7 -> 1.4 | NO | $-0.057 | $-0.087 | $+0.030 | keep raw=True | mushroom_v28_exit_value_over_hold | Wrong settlement side and still lost. |
| 11 | KXBTC15M-26MAY100030-30 | YES | 78.0 -> 79.0 | YES | $-0.040 | $+0.630 | $-0.670 | keep raw=True | mushroom_v28_exit_value_over_hold | Correct settlement side, bad early exit. |
| 12 | KXBTC15M-26MAY100030-30 | YES | 66.0 -> 73.0 | YES | $+0.070 | $+0.640 | $-0.570 | keep raw=True | mushroom_v28_exit_value_over_hold | Correct side, profitable, but usually left settlement upside. |
| 13 | KXBTC15M-26MAY100030-30 | NO | 4.8 -> 6.4 | YES | $+0.012 | $-0.158 | $+0.170 | explore raw=False | mushroom_v28_probability_collapse_full | Wrong settlement side, but exit/price swing salvaged profit. |
| 14 | KXBTC15M-26MAY100030-30 | NO | 6.6 -> 6.4 | YES | $-0.046 | $-0.216 | $+0.170 | unknown raw=None | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 15 | KXBTC15M-26MAY100045-45 | YES | 79.0 -> 85.0 | NO | $+0.070 | $-1.610 | $+1.680 | keep raw=True | mushroom_v28_exit_value_over_hold | Wrong settlement side, but exit/price swing salvaged profit. |
| 16 | KXBTC15M-26MAY100045-45 | YES | 78.0 -> 74.0 | NO | $-0.200 | $-2.370 | $+2.170 | keep raw=True | mushroom_v28_exit_value_over_hold | Wrong settlement side; exit reduced what holding would have lost. |
| 17 | KXBTC15M-26MAY100045-45 | YES | 77.0 -> 75.0 | NO | $-0.100 | $-1.570 | $+1.470 | explore raw=False | mushroom_v28_exit_value_over_hold | Wrong settlement side; exit reduced what holding would have lost. |
| 18 | KXBTC15M-26MAY100045-45 | NO | 4.3 -> 12.0 | NO | $+0.187 | $+2.857 | $-2.670 | keep raw=True | mushroom_v28_probability_collapse_full | Correct side, profitable, but usually left settlement upside. |
| 19 | KXBTC15M-26MAY100045-45 | NO | 10.0 -> 8.1 | NO | $-0.100 | $+2.680 | $-2.780 | explore raw=False | mushroom_v28_probability_collapse_full | Correct settlement side, bad early exit. |
| 20 | KXBTC15M-26MAY100045-45 | NO | 6.7 -> 2.1 | NO | $-0.167 | $+2.783 | $-2.950 | explore raw=False | mushroom_v28_probability_collapse_full | Correct settlement side, bad early exit. |
| 21 | KXBTC15M-26MAY100045-45 | NO | 6.5 -> 3.4 | NO | $-0.115 | $+2.795 | $-2.910 | keep raw=True | mushroom_v28_probability_collapse_full | Correct settlement side, bad early exit. |
| 22 | KXBTC15M-26MAY100045-45 | NO | 3.7 -> 15.0 | NO | $+0.313 | $+2.883 | $-2.570 | keep raw=True | settlement/no_exit_ts | Correct side, profitable, but usually left settlement upside. |
| 23 | KXBTC15M-26MAY100100-00 | NO | 75.0 -> 69.0 | NO | $-0.240 | $+0.720 | $-0.960 | keep raw=True | mushroom_v28_probability_reduce | Correct settlement side, bad early exit. |
| 24 | KXBTC15M-26MAY100100-00 | NO | 75.0 -> 76.0 | NO | $-0.030 | $+0.720 | $-0.750 | keep raw=True | mushroom_v28_probability_reduce | Correct settlement side, bad early exit. |
| 25 | KXBTC15M-26MAY100115-15 | NO | 78.0 -> 76.0 | NO | $-0.130 | $+0.630 | $-0.760 | keep raw=True | mushroom_v28_exit_value_over_hold | Correct settlement side, bad early exit. |
| 26 | KXBTC15M-26MAY100115-15 | NO | 77.0 -> 67.0 | NO | $-0.380 | $+0.660 | $-1.040 | keep raw=True | mushroom_v28_probability_collapse_full | Correct settlement side, bad early exit. |
| 27 | KXBTC15M-26MAY100130-30 | NO | 8.6 -> 5.3 | YES | $-0.136 | $-0.276 | $+0.140 | keep raw=True | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 28 | KXBTC15M-26MAY100145-45 | YES | 12.0 -> 20.0 | NO | $+0.180 | $-0.380 | $+0.560 | keep raw=True | mushroom_v28_probability_collapse_full | Wrong settlement side, but exit/price swing salvaged profit. |
| 29 | KXBTC15M-26MAY100145-45 | YES | 8.8 -> 6.4 | NO | $-0.108 | $-0.278 | $+0.170 | keep raw=True | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 30 | KXBTC15M-26MAY100145-45 | YES | 3.8 -> 1.3 | NO | $-0.098 | $-0.128 | $+0.030 | keep raw=True | mushroom_v28_probability_collapse_full | Wrong settlement side and still lost. |
| 31 | KXBTC15M-26MAY100200-00 | YES | 13.0 -> 24.0 | NO | $+0.270 | $-0.410 | $+0.680 | keep raw=True | mushroom_v28_exit_value_over_hold | Wrong settlement side, but exit/price swing salvaged profit. |
| 32 | KXBTC15M-26MAY100200-00 | YES | 9.9 -> 6.1 | NO | $-0.149 | $-0.319 | $+0.170 | explore raw=False | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 33 | KXBTC15M-26MAY100200-00 | YES | 7.0 -> 8.4 | NO | $+0.010 | $-0.220 | $+0.230 | explore raw=False | mushroom_v28_probability_collapse_full | Wrong settlement side, but exit/price swing salvaged profit. |
| 34 | KXBTC15M-26MAY100200-00 | YES | 6.6 -> 2.1 | NO | $-0.166 | $-0.216 | $+0.050 | explore raw=False | mushroom_v28_probability_collapse_full | Wrong settlement side and still lost. |
| 35 | KXBTC15M-26MAY100215-15 | NO | 15.0 -> 12.0 | YES | $-0.140 | $-0.470 | $+0.330 | explore raw=False | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 36 | KXBTC15M-26MAY100215-15 | NO | 14.0 -> 22.0 | YES | $+0.180 | $-0.440 | $+0.620 | unknown raw=None | mushroom_v28_probability_collapse_full | Wrong settlement side, but exit/price swing salvaged profit. |
| 37 | KXBTC15M-26MAY100215-15 | YES | 81.0 -> 61.0 | YES | $-0.680 | $+0.540 | $-1.220 | keep raw=True | mushroom_v28_probability_collapse_full | Correct settlement side, bad early exit. |
| 38 | KXBTC15M-26MAY100230-30 | YES | 11.0 -> 5.1 | NO | $-0.210 | $-0.350 | $+0.140 | keep raw=True | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 39 | KXBTC15M-26MAY100245-45 | YES | 83.0 -> 81.0 | YES | $-0.120 | $+0.490 | $-0.610 | keep raw=True | mushroom_v28_exit_value_over_hold | Correct settlement side, bad early exit. |
| 40 | KXBTC15M-26MAY100245-45 | YES | 83.0 -> 87.0 | YES | $+0.080 | $+0.500 | $-0.420 | keep raw=True | mushroom_v28_exit_value_over_hold | Correct side, profitable, but usually left settlement upside. |
| 41 | KXBTC15M-26MAY100245-45 | NO | 13.0 -> 17.0 | YES | $+0.070 | $-0.410 | $+0.480 | explore raw=False | mushroom_v28_probability_collapse_full | Wrong settlement side, but exit/price swing salvaged profit. |
| 42 | KXBTC15M-26MAY100245-45 | NO | 9.7 -> 2.1 | YES | $-0.257 | $-0.307 | $+0.050 | keep raw=True | mushroom_v28_probability_collapse_full | Wrong settlement side and still lost. |
| 43 | KXBTC15M-26MAY100300-00 | YES | 81.0 -> 79.0 | YES | $-0.100 | $+0.550 | $-0.650 | keep raw=True | mushroom_v28_exit_value_over_hold | Correct settlement side, bad early exit. |
| 44 | KXBTC15M-26MAY100300-00 | NO | 7.7 -> 7.4 | YES | $-0.047 | $-0.247 | $+0.200 | keep raw=True | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 45 | KXBTC15M-26MAY100300-00 | NO | 7.6 -> 25.0 | YES | $+0.464 | $-0.246 | $+0.710 | keep raw=True | mushroom_v28_probability_collapse_full | Wrong settlement side, but exit/price swing salvaged profit. |
| 46 | KXBTC15M-26MAY100300-00 | YES | 75.0 -> 83.0 | YES | $+0.190 | $+0.720 | $-0.530 | keep raw=True | mushroom_v28_exit_value_over_hold | Correct side, profitable, but usually left settlement upside. |
| 47 | KXBTC15M-26MAY100300-00 | NO | 8.7 -> 5.2 | YES | $-0.137 | $-0.277 | $+0.140 | keep raw=True | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 48 | KXBTC15M-26MAY100300-00 | NO | 5.8 -> 5.2 | YES | $-0.048 | $-0.188 | $+0.140 | unknown raw=None | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 49 | KXBTC15M-26MAY100315-15 | YES | 71.0 -> 69.0 | YES | $-0.100 | $+0.550 | $-0.650 | keep raw=True | mushroom_v28_exit_value_over_hold | Correct settlement side, bad early exit. |
| 50 | KXBTC15M-26MAY100915-15 | NO | 74.0 -> 76.0 | YES | $+0.010 | $-2.250 | $+2.260 | explore raw=False | mushroom_v28_probability_reduce | Wrong settlement side, but exit/price swing salvaged profit. |
| 51 | KXBTC15M-26MAY100915-15 | NO | 77.0 -> 76.0 | YES | $-0.080 | $-2.340 | $+2.260 | unknown raw=None | mushroom_v28_probability_reduce | Wrong settlement side; exit reduced what holding would have lost. |
| 52 | KXBTC15M-26MAY100930-30 | YES | 85.0 -> 70.0 | YES | $-0.479 | $+0.430 | $-0.909 | keep raw=True | mushroom_v28_probability_collapse_full | Correct settlement side, bad early exit. |
| 53 | KXBTC15M-26MAY100930-30 | YES | 79.0 -> 87.0 | YES | $+0.190 | $+0.610 | $-0.420 | keep raw=True | mushroom_v28_exit_value_over_hold | Correct side, profitable, but usually left settlement upside. |
| 54 | KXBTC15M-26MAY100930-30 | NO | 14.0 -> 13.0 | YES | $-0.070 | $-0.430 | $+0.360 | explore raw=False | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 55 | KXBTC15M-26MAY100930-30 | NO | 11.0 -> 3.5 | YES | $-0.250 | $-0.340 | $+0.090 | keep raw=True | mushroom_v28_probability_collapse_full | Wrong settlement side; exit reduced what holding would have lost. |
| 56 | KXBTC15M-26MAY100930-30 | NO | 2.0 -> 30.0 | YES | $+0.821 | $-0.070 | $+0.891 | explore raw=False | settlement/no_exit_ts | Wrong settlement side, but exit/price swing salvaged profit. |
| 57 | KXBTC15M-26MAY100945-45 | NO | 75.0 -> 67.0 | NO | $-0.320 | $+0.720 | $-1.040 | explore raw=False | mushroom_v28_probability_collapse_full | Correct settlement side, bad early exit. |

## Main Diagnosis

- The dominant leak is exits, not just entries: 24 trades were on the final correct side, but 16 of those still lost money because the bot exited early.
- Exit logic saved many wrong-side trades, but it damaged correct-side trades more. Net exit effect versus holding is about -$10.658 on this sample.
- Fees are decisive. Gross PnL is only -$0.442, but fees are $2.583, turning a near-flat gross tape into -$3.025 net.
- After live exit-memory authority was disabled, gross was positive but fees still overwhelmed it: after the cap change, actual net was -$0.393 on 20 trades with +$0.470 gross and $0.863 fees.
- Raw kept entries are worse than phi exploration on this sample: keep/raw entries net -$2.464; explore entries net -$0.567. Exploration is not cleanly profitable, but it is not the main damage source.
