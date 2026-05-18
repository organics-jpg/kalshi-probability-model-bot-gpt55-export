# v48 v47 Exit Refinement

Generated UTC: `2026-05-05T06:27:06.192308+00:00`

## Scope

- Research-only exit sweep around `v47_recross_sigma1_v3cap68`.
- Entry is fixed at `edge0_ask100_p0.65_stc0-600`; only exit behavior changes.
- Live bot untouched.

## Search Result

- Exit policies evaluated: 130
- 80%+ coverage policies: 130
- Split-positive and all-day-positive policies: 12

## Selected Rows

| exit | min cov | min 1c | all 1c | train | validation | holdout | days | block10 | settled | exits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `hold15_prob54` | 81.33% | $0.86 | $12.34 | $7.40 | $4.08 | $0.86 | 5/5 | 8/10 | 251 | 83 |
| `prob54` | 81.33% | $0.86 | $12.10 | $7.16 | $4.08 | $0.86 | 5/5 | 8/10 | 251 | 83 |
| `stop30_or_prob54` | 81.33% | $0.81 | $10.95 | $6.33 | $3.81 | $0.81 | 5/5 | 8/10 | 249 | 85 |
| `hold30_prob54` | 81.33% | $0.66 | $11.87 | $7.13 | $4.08 | $0.66 | 5/5 | 8/10 | 251 | 83 |
| `stop45_or_prob54` | 81.33% | $0.64 | $10.19 | $5.40 | $4.15 | $0.64 | 5/5 | 8/10 | 246 | 88 |
| `stop25_or_prob54` | 81.33% | $0.41 | $10.60 | $6.15 | $4.04 | $0.41 | 5/5 | 8/10 | 249 | 85 |
| `stop50_or_prob56` | 81.33% | $0.37 | $6.62 | $5.30 | $0.95 | $0.37 | 5/5 | 8/10 | 238 | 96 |
| `stop50_or_prob54` | 81.33% | $0.30 | $10.41 | $6.56 | $3.55 | $0.30 | 5/5 | 8/10 | 245 | 89 |
| `hold15_prob52` | 81.33% | $0.22 | $11.68 | $7.38 | $4.08 | $0.22 | 5/5 | 8/10 | 252 | 82 |
| `prob52` | 81.33% | $0.22 | $11.44 | $7.14 | $4.08 | $0.22 | 5/5 | 8/10 | 252 | 82 |
| `hold30_prob52` | 81.33% | $0.22 | $11.41 | $7.11 | $4.08 | $0.22 | 5/5 | 8/10 | 252 | 82 |
| `stop30_or_prob52` | 81.33% | $0.17 | $10.29 | $6.31 | $3.81 | $0.17 | 5/5 | 8/10 | 250 | 84 |

## Read

- Best robust exit is `hold15_prob54` with min split fee+1c $0.86 and all-market fee+1c $12.34.
- The exit improvement is small; the main gain remains the v47 probability transform.
