# v69 v55 Entry / v66 Exit Strategy

Generated UTC: `2026-05-05T12:18:37.394144+00:00`

## Scope

- Research-only cross-surface entry/exit test.
- Entry uses v55; exit probability can use v55 or v66 balanced.
- Live bot untouched.

## Selected Rows

| entry surface | exit surface | floor | min cov | min 1c | all 1c | days | block10 | exits | trades |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `v55` | `v66_bal` | 0.52 | 81.33% | $2.17 | $12.81 | 5/5 | 7/10 | 81 | 333 |
| `v55` | `v66_bal` | 0.54 | 81.33% | $1.67 | $12.79 | 5/5 | 8/10 | 83 | 333 |
| `v66_bal` | `v66_bal` | 0.54 | 81.33% | $1.51 | $11.65 | 5/5 | 8/10 | 80 | 333 |
| `v55` | `v55` | 0.52 | 81.33% | $0.93 | $13.60 | 5/5 | 8/10 | 78 | 333 |
| `v66_bal` | `v55` | 0.52 | 81.33% | $0.77 | $12.34 | 5/5 | 8/10 | 75 | 333 |
| `v66_bal` | `v55` | 0.50 | 81.33% | $0.49 | $10.58 | 5/5 | 7/10 | 72 | 333 |
| `v55` | `v55` | 0.54 | 81.33% | $0.35 | $13.12 | 5/5 | 8/10 | 80 | 333 |
| `v66_bal` | `v55` | 0.54 | 81.33% | $0.19 | $11.86 | 5/5 | 8/10 | 77 | 333 |

## Read

- v69 target row has min split fee+1c $2.17 and all-market fee+1c $12.81.
- This is the best worst-split cushion seen so far while keeping the v55 entry universe.
- Best all-market row in this cross-surface test remains `v55` entry / `v55` exit at 0.52, with all fee+1c $13.60.
- v69 is a robustness candidate, not the max-PnL leader; strict-forward validation is required.
