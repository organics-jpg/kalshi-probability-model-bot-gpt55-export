# v28 Frozen Approved-Entry Conditional Book FV

- Freeze timestamp UTC: `2026-05-06T12:51:13.278724+00:00`
- Candidate: `conditional_book_no_late_discount`
- Rule: `Use book_probability if side=no OR seconds_to_close<240 OR raw_probability-book_probability>=0.10; otherwise use raw_probability.`
- Physics: Book anchoring should act as humility under late/NO/market-discounted overconfidence while preserving raw conviction on expensive high-confidence YES rows.

## Interpretation

- Frozen candidate `conditional_book_no_late_discount` has future entries/settled 93/93.
- Future Brier/logloss deltas versus raw are 0.013951868950215066/0.030691846082473884.
- Pre-freeze context deltas were -0.025583191549724993/-0.1425133634906126 over 80 settled rows.
- Promotion blockers: brier_not_better_than_raw, logloss_not_better_than_raw.
- Pre-freeze context is only motivation; future rows are the validation evidence.

## Future Validation

| rank | overlay | settled | W/L | avg p | brier | d brier | logloss | d logloss | gross c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `raw_probability` | 93 | 83/10 | 0.884965 | 0.097457 | 0.000000 | 0.350604 | 0.000000 | 623.000000 | none |
| 2 | `conditional_book_no_late_discount` | 93 | 83/10 | 0.796708 | 0.111409 | 0.013952 | 0.381296 | 0.030692 | 623.000000 | brier_not_better_than_raw, logloss_not_better_than_raw |
| 3 | `book_probability` | 93 | 83/10 | 0.778602 | 0.112717 | 0.015260 | 0.387910 | 0.037306 | 623.000000 | none |

## Pre-Freeze Context

| rank | overlay | settled | W/L | avg p | brier | d brier | logloss | d logloss | gross c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `book_probability` | 80 | 63/17 | 0.775875 | 0.147534 | -0.028156 | 0.467256 | -0.148583 | 200.000000 | none |
| 2 | `conditional_book_no_late_discount` | 80 | 63/17 | 0.806597 | 0.150106 | -0.025583 | 0.473326 | -0.142513 | 200.000000 | none |
| 3 | `raw_probability` | 80 | 63/17 | 0.882635 | 0.175690 | 0.000000 | 0.615839 | 0.000000 | 200.000000 | none |
