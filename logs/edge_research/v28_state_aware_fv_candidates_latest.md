# v28 State-Aware FV Candidates

Shadow-only probability candidates that explicitly forget stale same-market evidence.

- Observation rows: `6798`
- Scored rows: `61182`

## Ranked Overall

| rank | candidate | count | avg p | win rate | avg brier | vs raw | gross c |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | rmt_aggressive_forget | 6798 | 0.551155 | 0.549868 | 0.163366 | -0.005520 | -3233.0 |
| 2 | book_ask_prior | 6798 | 0.551125 | 0.549868 | 0.163490 | -0.005396 | -3233.0 |
| 3 | rmt_repetition_forget | 6798 | 0.550971 | 0.549868 | 0.163538 | -0.005348 | -3233.0 |
| 4 | first_market_raw_later_book | 6798 | 0.550856 | 0.549868 | 0.163687 | -0.005199 | -3233.0 |
| 5 | rmt_memory_gate | 6798 | 0.551021 | 0.549868 | 0.163693 | -0.005193 | -3233.0 |
| 6 | first_side_raw_later_book | 6798 | 0.550828 | 0.549868 | 0.163898 | -0.004988 | -3233.0 |
| 7 | repeated_market_book_anchor | 6798 | 0.550388 | 0.549868 | 0.164035 | -0.004851 | -3233.0 |
| 8 | repeated_side_book_anchor | 6798 | 0.550366 | 0.549868 | 0.164191 | -0.004695 | -3233.0 |
| 9 | v28_raw | 6798 | 0.549160 | 0.549868 | 0.168886 | 0.000000 | -3233.0 |

## Robustness Views

| view | best candidate | count | best brier | best vs raw |
|---|---|---:|---:|---:|
| all_observations | rmt_aggressive_forget | 6798 | 0.163366 | -0.005520 |
| approved_entries | repeated_side_book_anchor | 173 | 0.125567 | -0.008067 |
| rejected_actionable | rmt_aggressive_forget | 6625 | 0.164278 | -0.005528 |
| first_per_market_side_source | rmt_aggressive_forget | 464 | 0.202693 | -0.007788 |
| last_per_market_side_source | first_market_raw_later_book | 464 | 0.059716 | -0.011112 |
