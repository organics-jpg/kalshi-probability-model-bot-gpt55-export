# v65 Exit-Floor Path-Instability Audit

Generated UTC: `2026-05-05T11:42:53.378485+00:00`

## Scope

- Research-only audit for the v55 FV / v57 hold15 probability-collapse exit.
- Tests exit floors without changing entry coverage, then slices adverse path motion.
- Live bot untouched.

## Exit-Floor Scan

| floor | all fee+1c entry | all fee+1c roundtrip | min split fee+1c entry | min split fee+1c roundtrip | exits | trades | min cov |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.40 | $8.05 | $6.75 | $-3.33 | $-3.63 | 65 | 333 | 81.33% |
| 0.45 | $10.52 | $9.12 | $-3.64 | $-3.96 | 70 | 333 | 81.33% |
| 0.50 | $11.41 | $9.91 | $-0.86 | $-1.18 | 75 | 333 | 81.33% |
| 0.52 | $13.60 | $12.04 | $0.93 | $0.61 | 78 | 333 | 81.33% |
| 0.54 | $13.12 | $11.52 | $0.35 | $0.01 | 80 | 333 | 81.33% |
| 0.56 | $10.59 | $8.85 | $1.13 | $0.77 | 87 | 333 | 81.33% |
| 0.58 | $5.91 | $3.99 | $-1.51 | $-1.93 | 96 | 333 | 81.33% |
| 0.60 | $3.06 | $0.96 | $-2.54 | $-2.98 | 105 | 333 | 81.33% |
| 0.62 | $-1.19 | $-3.43 | $-3.81 | $-4.29 | 112 | 333 | 81.33% |
| 0.65 | $-4.35 | $-6.79 | $-5.98 | $-6.54 | 122 | 333 | 81.33% |
| 0.70 | $-7.42 | $-10.46 | $-3.64 | $-4.30 | 152 | 333 | 81.33% |
| 0.75 | $-10.14 | $-14.02 | $-3.99 | $-6.15 | 194 | 333 | 81.33% |
| 0.80 | $-9.38 | $-13.52 | $-3.84 | $-6.20 | 207 | 333 | 81.33% |

## Path Slices

| slice | trades | fee+1c entry | hold-to-settle fee+1c | exit over hold | exits | wins | losses | avg full bid dd | avg full p dd | avg 120s bid dd | avg 120s p dd |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `all_v57_style` | 333 | $13.60 | $0.43 | $13.17 | 78 | 277 | 56 | 18.2 | 0.199 | 6.5 | 0.081 |
| `YES_entries` | 171 | $9.13 | $-2.61 | $11.74 | 36 | 142 | 29 | 17.1 | 0.195 | 5.2 | 0.081 |
| `NO_entries` | 162 | $4.47 | $3.04 | $1.43 | 42 | 135 | 27 | 19.4 | 0.204 | 7.9 | 0.082 |
| `exited_by_prob52` | 78 | $-53.10 | $-66.27 | $13.17 | 78 | 23 | 55 | 59.7 | 0.627 | 16.9 | 0.177 |
| `settlement_would_lose` | 56 | $-40.89 | $-82.38 | $41.49 | 55 | 0 | 56 | 69.1 | 0.709 | 16.9 | 0.175 |
| `w120_pdrop_ge_20pp` | 39 | $-11.55 | $-16.02 | $4.47 | 25 | 21 | 18 | 37.4 | 0.486 | 20.0 | 0.326 |
| `w120_pdrop_ge_35pp` | 12 | $-5.05 | $-7.65 | $2.60 | 12 | 3 | 9 | 49.0 | 0.668 | 31.9 | 0.504 |
| `w120_bid_drop_ge_20c` | 35 | $-17.04 | $-19.77 | $2.73 | 28 | 16 | 19 | 54.0 | 0.533 | 30.8 | 0.251 |
| `w120_bid_drop_ge_40c` | 6 | $-5.22 | $-5.39 | $0.17 | 6 | 2 | 4 | 67.0 | 0.576 | 49.7 | 0.420 |
| `full_pdrop_ge_35pp` | 67 | $-48.54 | $-72.49 | $23.95 | 66 | 13 | 54 | 65.2 | 0.692 | 17.1 | 0.179 |
| `full_bid_drop_ge_40c` | 69 | $-50.30 | $-74.26 | $23.96 | 64 | 16 | 53 | 67.4 | 0.644 | 16.9 | 0.143 |
| `NO_tail_highask_tinyedge` | 18 | $0.46 | $0.46 | $0.00 | 0 | 18 | 0 | 1.2 | 0.010 | 1.1 | 0.010 |
| `NO_tail_highask_tinyedge_w120_pdrop20` | 0 | $0.00 | $0.00 | $0.00 | 0 | 0 | 0 |  |  |  |  |

## Read

- Best all-market exit floor is `0.52` with $13.60 all fee+1c entry P&L.
- Best min-split exit floor is `0.56` with $1.13 min-split fee+1c entry P&L.
- Baseline v57 floor `0.52` remains $13.60 all-market and $0.93 min-split fee+1c entry P&L.
- The scan does not justify changing the simple v57 probability floor on retrospective data.
- Path-instability slices are diagnostic only: they explain where losses happen, but any rule based on them must keep 75-80% coverage and pass strict-forward validation.
