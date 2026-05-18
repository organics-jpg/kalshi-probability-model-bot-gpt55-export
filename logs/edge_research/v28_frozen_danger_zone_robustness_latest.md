# v28 Frozen Danger-Zone Robustness

- Surface: `actual_v28_approved_entries_only`
- FV freeze timestamp UTC: `2026-05-06T03:14:35.467881+00:00`
- Future rows/markets: `142/84`
- Promotion ready: `False`
- Blockers: `fv_leave_one_failure`

## Current Read

- Frozen entry valve delta is 258.0c with 8 skipped future entries.
- Frozen danger-to-book FV Brier/logloss deltas are -0.004051658561887328/-0.05274815488405854 over 142 rows and 8 adjusted rows.
- Leave-one failures entry/FV: 0/1.
- Promotion blockers: fv_leave_one_failure.

## Full Future Sample

- Entry selected/skipped/control/candidate/delta: `134/8/715.000000c/973.000000c/258.000000c`
- FV rows/danger/adjusted: `142/8/8`
- FV Brier/logloss delta: `-0.004052/-0.052748`

## Worst Leave-One-Market Rows

| removed market | removed rows | danger | skips | removed gross c | entry delta c | fv adjusted | fv d brier | fv d logloss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY062015-15` | 3 | 2 | 2 | -186.000000 | 64.000000 | 6 | -0.004027 | -0.051514 |
| `KXBTC15M-26MAY060800-00` | 2 | 1 | 1 | -50.000000 | 226.000000 | 7 | -0.004822 | -0.055510 |
| `KXBTC15M-26MAY060945-45` | 4 | 2 | 2 | 4.000000 | 230.000000 | 6 | -0.005128 | -0.057085 |
| `KXBTC15M-26MAY060330-30` | 2 | 1 | 1 | -70.000000 | 240.000000 | 7 | 0.002972 | 0.006246 |
| `KXBTC15M-26MAY061015-15` | 3 | 1 | 1 | 48.000000 | 258.000000 | 7 | -0.004637 | -0.055333 |
| `KXBTC15M-26MAY060300-00` | 4 | 0 | 0 | -38.000000 | 258.000000 | 8 | -0.004169 | -0.054277 |
| `KXBTC15M-26MAY060930-30` | 4 | 0 | 0 | 9.000000 | 258.000000 | 8 | -0.004169 | -0.054277 |
| `KXBTC15M-26MAY060700-00` | 4 | 0 | 0 | -48.000000 | 258.000000 | 8 | -0.004169 | -0.054277 |
| `KXBTC15M-26MAY060900-00` | 4 | 0 | 0 | -68.000000 | 258.000000 | 8 | -0.004169 | -0.054277 |
| `KXBTC15M-26MAY062115-15` | 3 | 0 | 0 | -24.000000 | 258.000000 | 8 | -0.004139 | -0.053887 |
| `KXBTC15M-26MAY071015-15` | 3 | 0 | 0 | 6.000000 | 258.000000 | 8 | -0.004139 | -0.053887 |
| `KXBTC15M-26MAY060215-15` | 3 | 0 | 0 | -8.000000 | 258.000000 | 8 | -0.004139 | -0.053887 |
