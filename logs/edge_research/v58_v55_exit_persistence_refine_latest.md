# v58 v55 Exit Persistence Refinement

Generated UTC: `2026-05-05T10:40:55.176079+00:00`

## Scope

- Research-only exit persistence sweep around `v55_bookanchor_m10_v20_g05_book_plus2`.
- Entry is fixed at `edge0_ask100_p0.65_stc0-600`; FV probability surface is unchanged.
- Tests whether probability-collapse exits need confirmation/dwell before acting.
- `marginlte*` rows are asymmetric YES-axis margin gates; `heldmarginlte*` rows are symmetric held-side margin gates.
- Live bot untouched.

## Search

- Exit policies evaluated: 586
- 80%+ coverage policies: 586
- Robust policies: 60

## Baselines

| exit | min cov | min 1c | all 1c | all fee | days | block10 | trades | exits | settled |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `hold15_prob52` | 81.33% | $0.93 | $13.60 | $20.26 | 5/5 | 8/10 | 333 | 78 | 255 |
| `prob52` | 81.33% | $0.93 | $13.36 | $20.02 | 5/5 | 8/10 | 333 | 78 | 255 |
| `prob54` | 81.33% | $0.35 | $12.88 | $19.54 | 5/5 | 8/10 | 333 | 80 | 253 |
| `hold60_prob52` | 81.33% | $0.17 | $12.67 | $19.33 | 4/5 | 8/10 | 333 | 78 | 255 |
| `prob52_confirm2` | 81.33% | $-2.07 | $11.33 | $17.99 | 4/5 | 7/10 | 333 | 76 | 257 |
| `prob52_dwell30` | 81.33% | $-3.71 | $8.84 | $15.50 | 4/5 | 5/10 | 333 | 74 | 259 |

## Selected Rows

| exit | min cov | min 1c | all 1c | all fee | days | block10 | trades | exits | settled |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `hold15_prob52_noside_marginlte0p25` | 81.33% | $0.87 | $21.26 | $27.92 | 5/5 | 8/10 | 333 | 68 | 265 |
| `prob52_noside_marginlte0p25` | 81.33% | $0.87 | $21.02 | $27.68 | 5/5 | 8/10 | 333 | 68 | 265 |
| `hold15_prob52_marginlte0p25` | 81.33% | $0.57 | $20.45 | $27.11 | 5/5 | 8/10 | 333 | 68 | 265 |
| `prob52_marginlte0p25` | 81.33% | $0.57 | $20.21 | $26.87 | 5/5 | 8/10 | 333 | 68 | 265 |
| `hold15_prob54_noside_marginlte0p25` | 81.33% | $0.29 | $19.88 | $26.54 | 5/5 | 9/10 | 333 | 71 | 262 |
| `prob54_noside_marginlte0p25` | 81.33% | $0.29 | $19.64 | $26.30 | 5/5 | 9/10 | 333 | 71 | 262 |
| `hold15_prob52_noside_marginlte0p5` | 81.33% | $0.87 | $17.67 | $24.33 | 5/5 | 8/10 | 333 | 71 | 262 |
| `prob52_noside_marginlte0p5` | 81.33% | $0.87 | $17.43 | $24.09 | 5/5 | 8/10 | 333 | 71 | 262 |
| `hold15_prob52_marginlte0p5` | 81.33% | $0.57 | $17.33 | $23.99 | 5/5 | 8/10 | 333 | 71 | 262 |
| `prob52_marginlte0p5` | 81.33% | $0.57 | $17.09 | $23.75 | 5/5 | 8/10 | 333 | 71 | 262 |
| `hold15_prob56_noside_marginlte0p25` | 81.33% | $0.99 | $16.37 | $23.03 | 5/5 | 8/10 | 333 | 79 | 254 |
| `hold15_prob54_noside_marginlte0p5` | 81.33% | $0.29 | $16.29 | $22.95 | 5/5 | 9/10 | 333 | 74 | 259 |
| `prob56_noside_marginlte0p25` | 81.33% | $0.99 | $16.13 | $22.79 | 5/5 | 8/10 | 333 | 79 | 254 |
| `prob54_noside_marginlte0p5` | 81.33% | $0.29 | $16.05 | $22.71 | 5/5 | 9/10 | 333 | 74 | 259 |
| `hold15_prob56_marginlte0p25` | 81.33% | $0.69 | $15.58 | $22.24 | 5/5 | 8/10 | 333 | 79 | 254 |
| `prob56_marginlte0p25` | 81.33% | $0.69 | $15.34 | $22.00 | 5/5 | 8/10 | 333 | 79 | 254 |
| `hold15_prob52` | 81.33% | $0.93 | $13.60 | $20.26 | 5/5 | 8/10 | 333 | 78 | 255 |
| `hold30_prob52` | 81.33% | $0.93 | $13.60 | $20.26 | 5/5 | 8/10 | 333 | 78 | 255 |
| `prob52` | 81.33% | $0.93 | $13.36 | $20.02 | 5/5 | 8/10 | 333 | 78 | 255 |
| `hold15_prob52_yesside_marginlte0p5` | 81.33% | $0.63 | $13.26 | $19.92 | 5/5 | 8/10 | 333 | 78 | 255 |
| `hold15_prob54_heldmarginlte0p5` | 81.33% | $1.07 | $13.14 | $19.80 | 5/5 | 8/10 | 333 | 79 | 254 |
| `hold15_prob54` | 81.33% | $0.35 | $13.12 | $19.78 | 5/5 | 8/10 | 333 | 80 | 253 |
| `hold30_prob54` | 81.33% | $0.35 | $13.12 | $19.78 | 5/5 | 8/10 | 333 | 80 | 253 |
| `prob52_yesside_marginlte0p5` | 81.33% | $0.63 | $13.02 | $19.68 | 5/5 | 8/10 | 333 | 78 | 255 |
| `prob54_heldmarginlte0p5` | 81.33% | $1.07 | $12.90 | $19.56 | 5/5 | 8/10 | 333 | 79 | 254 |
| `prob54` | 81.33% | $0.35 | $12.88 | $19.54 | 5/5 | 8/10 | 333 | 80 | 253 |
| `hold15_prob52_yesside_marginlte0p25` | 81.33% | $0.63 | $12.79 | $19.45 | 5/5 | 8/10 | 333 | 78 | 255 |
| `hold15_prob54_yesside_marginlte0p5` | 81.33% | $0.05 | $12.78 | $19.44 | 5/5 | 8/10 | 333 | 80 | 253 |
| `hold15_prob52_heldmarginlte0p5` | 81.33% | $0.63 | $12.60 | $19.26 | 5/5 | 8/10 | 333 | 78 | 255 |
| `hold15_prob56_marginlte0p1` | 81.33% | $0.06 | $12.58 | $19.24 | 5/5 | 7/10 | 333 | 69 | 264 |

## Read

- Best v58 row is `hold15_prob52_noside_marginlte0p25` with all-market fee+1c $21.26 and min-split fee+1c $0.87.
- This best row is an asymmetric YES-axis market-structure gate, not a symmetric held-side physics law.
- Delta vs v55 `prob54`: all fee+1c $8.38; delta vs v57-style `hold15_prob52`: $7.66.
- Strict-forward shadow validation is still required before promotion.
