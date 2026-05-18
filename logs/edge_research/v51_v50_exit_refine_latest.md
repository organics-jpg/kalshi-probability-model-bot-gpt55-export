# v51 v50 Exit Refinement

Generated UTC: `2026-05-05T06:49:29.595465+00:00`

## Scope

- Research-only exit sweep around `v50_thinedge_ask90_edge1_stc450_cap75`.
- Entry is fixed at `edge0_ask100_p0.65_stc0-600`; only exit behavior changes.
- Live bot untouched.

## Search Result

- Exit policies evaluated: 130
- 80%+ coverage policies: 130
- Split-positive and all-day-positive policies: 15

## Selected Rows

| exit | min cov | min 1c | all 1c | train | validation | holdout | days | block10 | settled | exits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `hold15_prob54` | 81.33% | $0.99 | $12.78 | $7.54 | $4.25 | $0.99 | 5/5 | 8/10 | 250 | 83 |
| `prob54` | 81.33% | $0.99 | $12.54 | $7.30 | $4.25 | $0.99 | 5/5 | 8/10 | 250 | 83 |
| `stop30_or_prob54` | 81.33% | $0.94 | $11.39 | $6.47 | $3.98 | $0.94 | 5/5 | 8/10 | 248 | 85 |
| `hold30_prob54` | 81.33% | $0.79 | $12.31 | $7.27 | $4.25 | $0.79 | 5/5 | 8/10 | 250 | 83 |
| `stop45_or_prob54` | 81.33% | $0.77 | $10.63 | $5.54 | $4.32 | $0.77 | 5/5 | 8/10 | 245 | 88 |
| `stop25_or_prob54` | 81.33% | $0.54 | $11.04 | $6.29 | $4.21 | $0.54 | 5/5 | 8/10 | 248 | 85 |
| `stop40_or_prob56` | 81.33% | $0.53 | $8.08 | $6.15 | $1.40 | $0.53 | 5/5 | 8/10 | 239 | 94 |
| `stop50_or_prob56` | 81.33% | $0.50 | $7.06 | $5.44 | $1.12 | $0.50 | 5/5 | 8/10 | 237 | 96 |
| `stop50_or_prob54` | 81.33% | $0.43 | $10.85 | $6.70 | $3.72 | $0.43 | 5/5 | 8/10 | 244 | 89 |
| `hold15_prob52` | 81.33% | $0.35 | $12.12 | $7.52 | $4.25 | $0.35 | 5/5 | 8/10 | 251 | 82 |
| `prob52` | 81.33% | $0.35 | $11.88 | $7.28 | $4.25 | $0.35 | 5/5 | 8/10 | 251 | 82 |
| `hold30_prob52` | 81.33% | $0.35 | $11.85 | $7.25 | $4.25 | $0.35 | 5/5 | 8/10 | 251 | 82 |
| `stop30_or_prob52` | 81.33% | $0.30 | $10.73 | $6.45 | $3.98 | $0.30 | 5/5 | 8/10 | 249 | 84 |
| `stop45_or_prob52` | 81.33% | $0.13 | $9.01 | $4.56 | $4.32 | $0.13 | 5/5 | 7/10 | 245 | 88 |
| `stop40_or_prob54` | 81.33% | $0.10 | $11.13 | $7.45 | $3.58 | $0.10 | 5/5 | 8/10 | 246 | 87 |

## Read

- Best robust exit is `hold15_prob54` with min split fee+1c $0.99 and all-market fee+1c $12.78.
- The exit improvement remains smaller than the v50 FV improvement.
