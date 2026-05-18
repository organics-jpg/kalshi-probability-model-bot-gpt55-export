# v70 v55 Entry / v66 Margin Exit Strategy

Generated UTC: `2026-05-05T12:47:42.259573+00:00`

## Scope

- Research-only cross-surface exit test.
- Entry universe is fixed to v55 `edge0_ask100_p0.65_stc0-600`.
- Exit tests the v60 margin-gated policy family on v55 and v66 balanced probability paths.
- Live bot untouched.

## Selected Rows

| exit surface | exit policy | min cov | min 1c | all 1c | all fee | days | block10 | exits | trades |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `v66_bal` | `hold15_prob52_noside_marginlte0p25` | 81.33% | $2.17 | $14.40 | $21.06 | 5/5 | 7/10 | 80 | 333 |
| `v66_bal` | `hold15_prob52_noside_marginlte0p5` | 81.33% | $2.17 | $14.40 | $21.06 | 5/5 | 7/10 | 80 | 333 |
| `v66_bal` | `hold15_prob52` | 81.33% | $2.17 | $12.81 | $19.47 | 5/5 | 7/10 | 81 | 333 |
| `v66_bal` | `hold15_prob52_marginlte0p5` | 81.33% | $1.87 | $14.06 | $20.72 | 5/5 | 7/10 | 80 | 333 |
| `v66_bal` | `hold15_prob52_marginlte0p25` | 81.33% | $1.87 | $13.59 | $20.25 | 5/5 | 7/10 | 80 | 333 |
| `v66_bal` | `hold15_prob52_yesside_marginlte0p5` | 81.33% | $1.87 | $12.47 | $19.13 | 5/5 | 7/10 | 81 | 333 |
| `v66_bal` | `hold15_prob52_yesside_marginlte0p25` | 81.33% | $1.87 | $12.00 | $18.66 | 5/5 | 7/10 | 81 | 333 |
| `v66_bal` | `hold15_prob54_noside_marginlte0p25` | 81.33% | $1.67 | $13.48 | $20.14 | 5/5 | 8/10 | 83 | 333 |
| `v66_bal` | `hold15_prob54_noside_marginlte0p5` | 81.33% | $1.67 | $13.48 | $20.14 | 5/5 | 8/10 | 83 | 333 |
| `v66_bal` | `hold15_prob54` | 81.33% | $1.67 | $12.79 | $19.45 | 5/5 | 8/10 | 83 | 333 |
| `v66_bal` | `hold15_prob54_marginlte0p5` | 81.33% | $1.37 | $13.14 | $19.80 | 5/5 | 8/10 | 83 | 333 |
| `v66_bal` | `hold15_prob54_marginlte0p25` | 81.33% | $1.37 | $12.67 | $19.33 | 5/5 | 8/10 | 83 | 333 |
| `v66_bal` | `hold15_prob54_yesside_marginlte0p5` | 81.33% | $1.37 | $12.45 | $19.11 | 5/5 | 8/10 | 83 | 333 |
| `v66_bal` | `hold15_prob54_yesside_marginlte0p25` | 81.33% | $1.37 | $11.98 | $18.64 | 5/5 | 8/10 | 83 | 333 |
| `v66_bal` | `hold15_prob56_noside_marginlte0p25` | 81.33% | $1.11 | $9.38 | $16.04 | 5/5 | 7/10 | 91 | 333 |
| `v66_bal` | `hold15_prob56_noside_marginlte0p5` | 81.33% | $1.11 | $9.38 | $16.04 | 5/5 | 7/10 | 91 | 333 |
| `v55` | `hold15_prob56_noside_marginlte0p25` | 81.33% | $0.99 | $16.37 | $23.03 | 5/5 | 8/10 | 79 | 333 |
| `v55` | `hold15_prob52` | 81.33% | $0.93 | $13.60 | $20.26 | 5/5 | 8/10 | 78 | 333 |
| `v55` | `hold15_prob52_noside_marginlte0p25` | 81.33% | $0.87 | $21.26 | $27.92 | 5/5 | 8/10 | 68 | 333 |
| `v55` | `hold15_prob52_noside_marginlte0p5` | 81.33% | $0.87 | $17.67 | $24.33 | 5/5 | 8/10 | 71 | 333 |
| `v66_bal` | `hold15_prob56_marginlte0p5` | 81.33% | $0.81 | $9.06 | $15.72 | 5/5 | 7/10 | 91 | 333 |
| `v66_bal` | `hold15_prob56_marginlte0p25` | 81.33% | $0.81 | $8.59 | $15.25 | 5/5 | 7/10 | 91 | 333 |
| `v55` | `hold15_prob56_marginlte0p25` | 81.33% | $0.69 | $15.58 | $22.24 | 5/5 | 8/10 | 79 | 333 |
| `v55` | `hold15_prob52_yesside_marginlte0p5` | 81.33% | $0.63 | $13.26 | $19.92 | 5/5 | 8/10 | 78 | 333 |
| `v55` | `hold15_prob52_yesside_marginlte0p25` | 81.33% | $0.63 | $12.79 | $19.45 | 5/5 | 8/10 | 78 | 333 |
| `v55` | `hold15_prob52_marginlte0p25` | 81.33% | $0.57 | $20.45 | $27.11 | 5/5 | 8/10 | 68 | 333 |
| `v55` | `hold15_prob52_marginlte0p5` | 81.33% | $0.57 | $17.33 | $23.99 | 5/5 | 8/10 | 71 | 333 |
| `v55` | `hold15_prob54` | 81.33% | $0.35 | $13.12 | $19.78 | 5/5 | 8/10 | 80 | 333 |
| `v55` | `hold15_prob54_noside_marginlte0p25` | 81.33% | $0.29 | $19.88 | $26.54 | 5/5 | 9/10 | 71 | 333 |
| `v55` | `hold15_prob54_noside_marginlte0p5` | 81.33% | $0.29 | $16.29 | $22.95 | 5/5 | 9/10 | 74 | 333 |

## Read

- Best all-market robust v70 row is `v55` / `hold15_prob52_noside_marginlte0p25` with all fee+1c $21.26.
- Best min-split robust v70 row is `v66_bal` / `hold15_prob52_noside_marginlte0p25` with min split fee+1c $2.17.
- Compare to v60 all fee+1c $21.26 and v69 min split fee+1c $2.17 before promotion.
