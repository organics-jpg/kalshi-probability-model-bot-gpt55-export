# v28 Dual-Lane Conflict-Arbiter Frontier

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:47:01.482982+00:00`
- Same-window compare UTC: `2026-05-11T03:47:01.196227+00:00`
- Promotion use: `diagnostic_conflict_arbiter_design_only`
- Candidate policy: `post_dual_union_birth_entry_cheap_penalty025_rank_only`
- Rows available / denominator: `16` / `18`
- Rules tested: `66`

## Read

- This is not promotion evidence; it is a same-window design audit.
- A deployable arbiter must use only observable pre-entry features and then get its own freeze.
- The desired physical mechanism is suppressing high-cost/path-unstable rows where live v28 may need side-flip state management.

## Best Diagnostic Arbiter

- Rule: `suppress_ask_ge0.78_recross_ge0.3`
- Allowed rows/coverage: `11` / `61.11%`
- Allowed candidate/live/delta: `288c ($2.88)` / `106c ($1.06)` / `182c ($1.82)`
- Allowed W/L/cushion: `10/1` / `2`
- Suppressed rows candidate/live/delta: `5` / `-229c ($-2.29)` / `134c ($1.34)` / `-363c ($-3.63)`
- Side-flips suppressed: `2` / `2`
- Blockers: `diagnostic_only_not_frozen_forward`
- Suppressed markets: `['KXBTC15M-26MAY071100-00', 'KXBTC15M-26MAY071015-15', 'KXBTC15M-26MAY071145-45', 'KXBTC15M-26MAY071130-30', 'KXBTC15M-26MAY070930-30']`

## Top Rules

| rank | rule | allowed rows | allowed cov | allowed net | live net | delta | suppressed rows | side-flips | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `suppress_ask_ge0.78_recross_ge0.3` | 11 | 61.11% | 288c ($2.88) | 106c ($1.06) | 182c ($1.82) | 5 | 2/2 | diagnostic_only_not_frozen_forward |
| 2 | `suppress_cost_recross_combo_ge0.04` | 6 | 33.33% | 141c ($1.41) | -19c ($-0.19) | 160c ($1.60) | 10 | 2/2 | diagnostic_only_not_frozen_forward |
| 3 | `suppress_ask_ge0.78_recross_ge0.25` | 10 | 55.56% | 268c ($2.68) | 151c ($1.51) | 117c ($1.17) | 6 | 2/2 | diagnostic_only_not_frozen_forward |
| 4 | `suppress_ask_ge0.78_raw_missing_or_le0.09` | 7 | 38.89% | 185c ($1.85) | 135c ($1.35) | 50c ($0.50) | 9 | 2/2 | diagnostic_only_not_frozen_forward |
| 5 | `suppress_ask_ge0.78_raw_missing_or_le0.12` | 7 | 38.89% | 185c ($1.85) | 135c ($1.35) | 50c ($0.50) | 9 | 2/2 | diagnostic_only_not_frozen_forward |
| 6 | `suppress_ask_ge0.78_raw_missing_or_le0.09_or_yes` | 7 | 38.89% | 185c ($1.85) | 135c ($1.35) | 50c ($0.50) | 9 | 2/2 | diagnostic_only_not_frozen_forward |
| 7 | `suppress_ask_ge0.78_raw_missing_or_le0.12_or_yes` | 7 | 38.89% | 185c ($1.85) | 135c ($1.35) | 50c ($0.50) | 9 | 2/2 | diagnostic_only_not_frozen_forward |
| 8 | `suppress_delayed_recheck_recross_ge0.25` | 11 | 61.11% | 243c ($2.43) | 220c ($2.20) | 23c ($0.23) | 5 | 2/2 | diagnostic_only_not_frozen_forward |
| 9 | `suppress_delayed_recheck_recross_ge0.3` | 11 | 61.11% | 243c ($2.43) | 220c ($2.20) | 23c ($0.23) | 5 | 2/2 | diagnostic_only_not_frozen_forward |
| 10 | `suppress_ask_ge0.82_recross_ge0.25` | 13 | 72.22% | 166c ($1.66) | 72c ($0.72) | 94c ($0.94) | 3 | 1/2 | diagnostic_only_not_frozen_forward, does_not_suppress_all_current_side_flips |
| 11 | `suppress_ask_ge0.82_recross_ge0.3` | 13 | 72.22% | 166c ($1.66) | 72c ($0.72) | 94c ($0.94) | 3 | 1/2 | diagnostic_only_not_frozen_forward, does_not_suppress_all_current_side_flips |
| 12 | `suppress_ask_ge0.82_raw_missing_or_le0.07` | 11 | 61.11% | 127c ($1.27) | 48c ($0.48) | 79c ($0.79) | 5 | 1/2 | diagnostic_only_not_frozen_forward, does_not_suppress_all_current_side_flips |
| 13 | `suppress_ask_ge0.82_raw_missing_or_le0.09` | 11 | 61.11% | 127c ($1.27) | 48c ($0.48) | 79c ($0.79) | 5 | 1/2 | diagnostic_only_not_frozen_forward, does_not_suppress_all_current_side_flips |
| 14 | `suppress_ask_ge0.82_raw_missing_or_le0.12` | 11 | 61.11% | 127c ($1.27) | 48c ($0.48) | 79c ($0.79) | 5 | 1/2 | diagnostic_only_not_frozen_forward, does_not_suppress_all_current_side_flips |
| 15 | `suppress_ask_ge0.82_raw_missing_or_le0.07_or_yes` | 11 | 61.11% | 127c ($1.27) | 48c ($0.48) | 79c ($0.79) | 5 | 1/2 | diagnostic_only_not_frozen_forward, does_not_suppress_all_current_side_flips |
| 16 | `suppress_ask_ge0.82_raw_missing_or_le0.09_or_yes` | 11 | 61.11% | 127c ($1.27) | 48c ($0.48) | 79c ($0.79) | 5 | 1/2 | diagnostic_only_not_frozen_forward, does_not_suppress_all_current_side_flips |
| 17 | `suppress_ask_ge0.82_raw_missing_or_le0.12_or_yes` | 11 | 61.11% | 127c ($1.27) | 48c ($0.48) | 79c ($0.79) | 5 | 1/2 | diagnostic_only_not_frozen_forward, does_not_suppress_all_current_side_flips |
| 18 | `suppress_ask_ge0.8_recross_ge0.25` | 12 | 66.67% | 126c ($1.26) | 100c ($1.00) | 26c ($0.26) | 4 | 1/2 | diagnostic_only_not_frozen_forward, does_not_suppress_all_current_side_flips |
| 19 | `suppress_ask_ge0.8_recross_ge0.3` | 12 | 66.67% | 126c ($1.26) | 100c ($1.00) | 26c ($0.26) | 4 | 1/2 | diagnostic_only_not_frozen_forward, does_not_suppress_all_current_side_flips |
| 20 | `suppress_yes_ask_ge0.82` | 13 | 72.22% | 147c ($1.47) | 127c ($1.27) | 20c ($0.20) | 3 | 1/2 | diagnostic_only_not_frozen_forward, does_not_suppress_all_current_side_flips |
