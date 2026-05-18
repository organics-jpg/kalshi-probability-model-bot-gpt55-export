# v28 Approved-Entry Book FV Robustness

- Surface: `actual_v28_approved_entries_only`
- Candidate: `book_probability`
- Rows: `173`
- Full Brier/logloss deltas: `-0.004817/-0.048654`
- Bootstrap p95 Brier/logloss: `0.010699/0.028218`
- Blockers: `leave_one_market_failure, bootstrap_brier_p95_not_negative, bootstrap_logloss_p95_not_negative`

## Interpretation

- Book probability full-sample Brier/logloss deltas are -0.004816693669815029/-0.048654430823182764 versus raw.
- Bootstrap p95 Brier/logloss deltas are 0.010699206867728323/0.02821750921046068.
- Leave-one-market failures: 2.
- Promotion blockers: leave_one_market_failure, bootstrap_brier_p95_not_negative, bootstrap_logloss_p95_not_negative.

## Worst Leave-One-Market Slices

| left out | rows | W/L | brier d | logloss d | brier better | logloss better |
|---|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY051715-15 | 170 | 146/24 | 0.000932 | -0.032696 | False | True |
| KXBTC15M-26MAY060330-30 | 171 | 145/26 | 0.000716 | -0.001123 | False | True |
| KXBTC15M-26MAY052245-45 | 172 | 146/26 | -0.000890 | -0.037463 | True | True |
| KXBTC15M-26MAY070015-15 | 172 | 146/26 | -0.002294 | -0.036665 | True | True |
| KXBTC15M-26MAY060745-45 | 171 | 146/25 | -0.002742 | -0.042649 | True | True |
| KXBTC15M-26MAY052045-45 | 171 | 146/25 | -0.003523 | -0.043810 | True | True |
| KXBTC15M-26MAY060215-15 | 170 | 145/25 | -0.003554 | -0.044525 | True | True |
| KXBTC15M-26MAY062130-30 | 172 | 146/26 | -0.003621 | -0.044518 | True | True |
| KXBTC15M-26MAY071015-15 | 170 | 145/25 | -0.003669 | -0.045221 | True | True |
| KXBTC15M-26MAY062115-15 | 170 | 144/26 | -0.003837 | -0.047018 | True | True |
| KXBTC15M-26MAY060900-00 | 169 | 144/25 | -0.003946 | -0.046367 | True | True |
| KXBTC15M-26MAY062015-15 | 170 | 145/25 | -0.004023 | -0.043099 | True | True |
