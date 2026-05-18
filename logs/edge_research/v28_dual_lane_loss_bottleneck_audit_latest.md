# v28 Dual-Lane Loss Bottleneck Audit

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:46:05.113250+00:00`
- Promotion use: `diagnostic_only_before_30_settled_rows`
- Freeze UTC: `2026-05-07T13:00:17.363339+00:00`
- Windows since freeze / remaining: `59` / `0`
- Live baseline: `2215c ($22.15)`
- Policy audited: `post_dual_union_birth_entry_cheap_penalty025_rank_only`

## Read

- Current forced replay is still immature diagnostic evidence, not a promotion sample.
- The immediate live-readiness bottleneck is damage control: two parent-fill losses are larger than six wins combined.
- The current losses do not yet show a clean enough shared shape for a new gate.

## Baseline Forced-Precheck Rows

- Entries/W/L: `16` / `13/3`
- Coverage: `88.89%`
- Net: `59c ($0.59)`
- Full-loss cushion: `0`
- Loss tags: `none`
- Primary failure modes: `Entry timing error, Execution/friction error, Fragility error`

## Failure-Mode Classification

| mode | status | evidence |
|---|---|---|
| FV error | `possible` | Both losses had positive modeled raw edge but resolved against the selected side; too few rows to separate calibration error from timing noise. |
| Entry timing error | `active` | Losses are expensive/thin-edge entries: avg ask=0.563 vs wins=0.792, avg raw_edge=0.068 vs wins=0.087. |
| Exit-policy error | `possible` | The child/exit rescue did not improve either current loss; needs more rows before calling the exit policy wrong. |
| Execution/friction error | `active` | Both losses are strict parent midprice hold-fill rows where high ask cost leaves little margin for path noise. |
| Market-regime error | `unknown` | The sample is too small to know whether the losses cluster in a volatility/path regime. |
| Source-quality error | `not_current_driver` | Loss source counts are {'approved_entry': 2, 'rejected_actionable': 1}; current strict precheck loss rows are approved-source, not reconstructed proxy rows. |
| Fragility error | `active` | Forced-precheck net is 59c with full-loss cushion 0; two losses erase the win stack. |

## Variant Stress

| variant | entries | W/L | coverage | net | delta | cushion |
|---|---:|---:|---:|---:|---:|---:|
| `baseline` | 16 | 13/3 | 88.89% | 59c ($0.59) | 0c ($0.00) | 0 |
| `shrink_high_cost_low_edge_25pct` | 16 | 13/3 | 88.89% | 90c ($0.91) | 32c ($0.32) | 0 |
| `shrink_high_cost_50pct` | 16 | 13/3 | 88.89% | 122c ($1.22) | 63c ($0.63) | 1 |
| `suppress_high_cost` | 7 | 6/1 | 38.89% | 185c ($1.85) | 126c ($1.26) | 1 |
| `shrink_high_cost_low_edge_50pct` | 16 | 13/3 | 88.89% | 122c ($1.22) | 63c ($0.63) | 1 |
| `shrink_high_cost_low_edge_75pct` | 16 | 13/3 | 88.89% | 154c ($1.53) | 94c ($0.94) | 1 |
| `suppress_high_cost_low_edge` | 7 | 6/1 | 38.89% | 185c ($1.85) | 126c ($1.26) | 1 |
| `shrink_high_cost_low_edge_near_boundary_50pct` | 16 | 13/3 | 88.89% | 174c ($1.74) | 115c ($1.15) | 1 |

## Current Loss Rows

| market | side | component | net | ask | raw edge | abs d | recross | rescue |
|---|---|---|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY071100-00` | yes | strict_delayed_recheck_rescue:drop15_bid60 | -166c ($-1.66) | 0.83 | 0.054041000000000006 | 1.010241 | 0.30500573389101787 | False |
| `KXBTC15M-26MAY071015-15` | no | strict_delayed_recheck_rescue:drop15_bid60 | -162c ($-1.62) | 0.78 | 0.08109199999999994 | 0.936079 | 0.41762272221317515 | False |
| `KXBTC15M-26MAY071300-00` | yes | continuous_penalty:cheap_penalty025_rank_only | -10c ($-0.10) | 0.08 | None | 0.932497 | 0.0838612713123607 | None |

Next research action: Test a parent-fill confidence shrink for expensive low-edge rows inside the dual-lane research scorer, then re-run strict precheck and wait for the 30-row own-freeze gate.
