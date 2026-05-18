# v38 FV 80% Coverage Projection

Generated UTC: `2026-05-04T23:11:01.721859+00:00`

## Scope

- Pure FV probability projection, not live-bot scoring.
- Uses first qualifying minute-bucket entry per market and holds to settlement.
- Candidate ranking requires at least 80% train-market coverage.
- No live bot code/process or orders are touched.

## Live Reference

- Entries: 221
- Open positions: 2
- Net P&L: $16.42 on $399.75 (4.11%)
- Resolved/unresolved markets: 316 / 45

## Selected Thresholds

| model | threshold | train cov | train P&L | train ROI | validation cov | validation P&L | validation ROI | holdout cov | holdout P&L | holdout ROI | all cov | all P&L | all ROI | stable 80+ positive? |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `v28_live_surface` | -0.75c | 100.00% | $-5.82 | -3.20% | 100.00% | $7.28 | 11.99% | 100.00% | $-11.82 | -20.44% | 100.00% | $-10.36 | -3.45% | False |
| `v37_piecewise_dynamic_temp_antipersist3` | -0.75c | 100.00% | $1.12 | 0.62% | 100.00% | $15.78 | 26.20% | 100.00% | $-6.04 | -10.41% | 100.00% | $10.86 | 3.63% | False |
| `v38_long60_antipersist` | -0.75c | 100.00% | $-0.98 | -0.54% | 100.00% | $15.78 | 26.20% | 100.00% | $-2.06 | -3.55% | 100.00% | $12.74 | 4.26% | False |

## Read

- Best selected v38 row trades 100.00% of replay markets with $12.74 projected P&L on $299.26 (4.26%).
- This projection is useful for broad-coverage pressure testing, but it is not a substitute for strict forward validation or an exit-aware strategy replay.
