# v71 v55 Entry / v68 Exit Strategy

Generated UTC: `2026-05-05T12:53:47.395872+00:00`

## Scope

- Research-only cross-surface exit test.
- Entry universe is fixed to v55 `edge0_ask100_p0.65_stc0-600`.
- Exit tests v68 calibrated-logit probabilities with the v60/v70 margin-gated policy family.
- Live bot untouched.

## Holdout Probability

| candidate | Brier | logloss | side acc |
|---|---:|---:|---:|
| `v68_l2_C1p0` | 0.13377 | 0.40353 | 79.92% |
| `v68_l2_C0p5` | 0.13378 | 0.40348 | 79.92% |
| `v68_l2_C0p2` | 0.13378 | 0.40330 | 79.87% |
| `v68_l2_C0p1` | 0.13380 | 0.40312 | 79.75% |
| `v68_l2_C0p05` | 0.13384 | 0.40290 | 79.89% |
| `v68_l2_C0p02` | 0.13426 | 0.40365 | 79.94% |
| `v55_bookanchor_m10_v20_g05_book_plus2` | 0.14176 | 0.42589 | 79.31% |

## Selected Rows

| exit surface | exit policy | min cov | min 1c | all 1c | all fee | days | block10 | exits | trades |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `v55` | `hold15_prob56_noside_marginlte0p25` | 81.33% | $0.99 | $16.37 | $23.03 | 5/5 | 8/10 | 79 | 333 |
| `v55` | `hold15_prob52` | 81.33% | $0.93 | $13.60 | $20.26 | 5/5 | 8/10 | 78 | 333 |
| `v55` | `hold15_prob52_noside_marginlte0p25` | 81.33% | $0.87 | $21.26 | $27.92 | 5/5 | 8/10 | 68 | 333 |
| `v55` | `hold15_prob52_noside_marginlte0p5` | 81.33% | $0.87 | $17.67 | $24.33 | 5/5 | 8/10 | 71 | 333 |
| `v55` | `hold15_prob56_marginlte0p25` | 81.33% | $0.69 | $15.58 | $22.24 | 5/5 | 8/10 | 79 | 333 |
| `v55` | `hold15_prob52_yesside_marginlte0p5` | 81.33% | $0.63 | $13.26 | $19.92 | 5/5 | 8/10 | 78 | 333 |
| `v55` | `hold15_prob52_yesside_marginlte0p25` | 81.33% | $0.63 | $12.79 | $19.45 | 5/5 | 8/10 | 78 | 333 |
| `v55` | `hold15_prob52_marginlte0p25` | 81.33% | $0.57 | $20.45 | $27.11 | 5/5 | 8/10 | 68 | 333 |
| `v55` | `hold15_prob52_marginlte0p5` | 81.33% | $0.57 | $17.33 | $23.99 | 5/5 | 8/10 | 71 | 333 |
| `v55` | `hold15_prob54` | 81.33% | $0.35 | $13.12 | $19.78 | 5/5 | 8/10 | 80 | 333 |
| `v55` | `hold15_prob54_noside_marginlte0p25` | 81.33% | $0.29 | $19.88 | $26.54 | 5/5 | 9/10 | 71 | 333 |
| `v55` | `hold15_prob54_noside_marginlte0p5` | 81.33% | $0.29 | $16.29 | $22.95 | 5/5 | 9/10 | 74 | 333 |
| `v68_C0p05` | `hold15_prob56_marginlte0p25` | 81.33% | $0.08 | $12.59 | $19.25 | 5/5 | 7/10 | 85 | 333 |
| `v68_C0p1` | `hold15_prob56_marginlte0p25` | 81.33% | $0.08 | $9.65 | $16.31 | 5/5 | 7/10 | 88 | 333 |
| `v68_C0p05` | `hold15_prob56_yesside_marginlte0p25` | 81.33% | $0.08 | $9.58 | $16.24 | 5/5 | 7/10 | 88 | 333 |
| `v68_C1p0` | `hold15_prob56_marginlte0p25` | 81.33% | $0.06 | $9.75 | $16.41 | 5/5 | 7/10 | 88 | 333 |
| `v68_C0p5` | `hold15_prob56_marginlte0p25` | 81.33% | $0.06 | $9.63 | $16.29 | 5/5 | 7/10 | 88 | 333 |
| `v68_C0p2` | `hold15_prob56_marginlte0p25` | 81.33% | $0.06 | $9.63 | $16.29 | 5/5 | 7/10 | 88 | 333 |
| `v55` | `hold15_prob54_yesside_marginlte0p5` | 81.33% | $0.05 | $12.78 | $19.44 | 5/5 | 8/10 | 80 | 333 |
| `v55` | `hold15_prob54_yesside_marginlte0p25` | 81.33% | $0.05 | $12.31 | $18.97 | 5/5 | 8/10 | 80 | 333 |

## Read

- Best all-market robust v71 row is `v55` / `hold15_prob52_noside_marginlte0p25` with all fee+1c $21.26.
- Best min-split robust v71 row is `v55` / `hold15_prob56_noside_marginlte0p25` with min split fee+1c $0.99.
- Compare to v60 all fee+1c $21.26 and v70 balanced all/min fee+1c $14.40/$2.17.
