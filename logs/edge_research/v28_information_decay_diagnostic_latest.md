# v28 Information Decay Diagnostic

Shadow-only test of whether older same-market evidence should be retained or forgotten.

Interpretation: positive `retained-current` Brier means stale retained evidence was worse than the current signal, so faster forgetting helped on this sample.

- Rows: `6798`
- Settled rows: `6798`
- Current p Brier: `0.16888504598027948`
- Current book Brier: `0.16348959988231831`
- Hypothetical gross on resolved rows: `$-32.33`

## Half-Life Comparison

| half-life sec | comparable | current p brier | retained p brier | retained-current p | current book brier | retained book brier | retained-current book | avg abs p surprise | stale worse |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 15 | 6448 | 0.165422 | 0.177436 | 0.012014 | 0.160164 | 0.172189 | 0.012024 | 0.073045 | 4056 |
| 45 | 6448 | 0.165422 | 0.182708 | 0.017286 | 0.160164 | 0.177608 | 0.017444 | 0.095084 | 4364 |
| 120 | 6448 | 0.165422 | 0.192560 | 0.027138 | 0.160164 | 0.188318 | 0.028153 | 0.129561 | 4567 |
| 300 | 6448 | 0.165422 | 0.207555 | 0.042133 | 0.160164 | 0.204751 | 0.044586 | 0.167970 | 4702 |

## State FV Variants

| rank | variant | count | avg p | win rate | avg brier | vs current | gross c |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | book_prior | 6798 | 0.551125 | 0.549868 | 0.163490 | -0.005395 | -3233.000000 |
| 2 | book_anchor_on_large_surprise | 6798 | 0.549003 | 0.549868 | 0.167981 | -0.000904 | -3233.000000 |
| 3 | shock_forget_else_light_15s_blend | 6798 | 0.548996 | 0.549868 | 0.168860 | -0.000025 | -3233.000000 |
| 4 | current_v28 | 6798 | 0.549160 | 0.549868 | 0.168885 | 0.000000 | -3233.000000 |
| 5 | opening_context_then_current | 6798 | 0.548440 | 0.549868 | 0.169587 | 0.000702 | -3233.000000 |
| 6 | retain_15s_prior | 6798 | 0.544021 | 0.549868 | 0.180281 | 0.011395 | -3233.000000 |

## De-Duplicated Views

| view | rows | settled | current p brier | retained-current p 15s | retained-current p 45s | retained-current p 120s | retained-current p 300s | gross c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all_observations | 6798 | 6798 | 0.168885 | 0.012014 | 0.017286 | 0.027138 | 0.042133 | -3233.000000 |
| first_per_market_side_source | 464 | 464 | 0.210460 | 0.021378 | 0.034919 | 0.056378 | 0.072802 | 10.000000 |
| last_per_market_side_source | 464 | 464 | 0.070809 | 0.022894 | 0.034394 | 0.056939 | 0.087932 | 116.000000 |

## By Source

- `approved_entry`: rows=173, settled=173, current_p_brier=0.133578826358, gross=$8.23
- `rejected_actionable`: rows=6625, settled=6625, current_p_brier=0.16980700462098203, gross=$-40.56
