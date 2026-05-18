# v50 Thin-Edge Certainty FV Strategy

Generated UTC: `2026-05-05T06:44:10.914235+00:00`

## Scope

- Research-only FV probability transform on top of v47.
- Caps expensive tiny-edge certainty before close instead of treating it as reliable edge.
- Live bot untouched.

## Physics Notes

- Base model: `v47_recross_sigma1_v3cap68`
- Hypothesis: expensive selected ask plus <= small fair edge with 450-600s left is fragile certainty
- `v50_thinedge_ask90_edge1_stc450_cap75` hazard rows: 124
- `v50_thinedge_ask90_edge2_stc450_cap75` hazard rows: 226
- `v50_thinedge_ask92_edge1_stc450_cap75` hazard rows: 103
- `v50_thinedge_ask90_edge3_stc500_cap75` hazard rows: 161

## Holdout Probability

| candidate | Brier | logloss | side acc | mean p_yes |
|---|---:|---:|---:|---:|
| `v50_thinedge_ask90_edge1_stc450_cap75` | 0.14220 | 0.42718 | 78.99% | 49.62% |
| `v50_thinedge_ask92_edge1_stc450_cap75` | 0.14220 | 0.42718 | 78.99% | 49.62% |
| `v47_recross_sigma1_v3cap68` | 0.14223 | 0.42755 | 78.99% | 49.68% |
| `v50_thinedge_ask90_edge2_stc450_cap75` | 0.14246 | 0.42832 | 78.99% | 49.59% |
| `v50_thinedge_ask90_edge3_stc500_cap75` | 0.14247 | 0.42855 | 78.99% | 49.64% |

## Strategy Search

- Candidate probability surfaces: 5
- Rows evaluated after 80% coverage prefilter: 1090
- Fee+1c positive train/validation/holdout rows: 105
- Fee+1c positive all-day rows: 42
- All-day rows with at least 7/10 positive chronological blocks: 37

## Selected Strategy Rows

| model | entry | exit | min cov | min 1c | all 1c | all fee | gross | days | block10 | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.99 | $12.54 | $19.20 | $30.38 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.99 | $12.38 | $19.04 | $30.22 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge2_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $0.93 | $12.58 | $19.22 | $30.42 | 5/5 | 8/10 | 332 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.90 | $11.66 | $18.10 | $29.14 | 5/5 | 8/10 | 322 |
| `v50_thinedge_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.90 | $11.50 | $17.94 | $28.98 | 5/5 | 8/10 | 322 |
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.86 | $12.10 | $18.78 | $29.94 | 5/5 | 8/10 | 334 |
| `v50_thinedge_ask90_edge3_stc500_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.86 | $12.42 | $19.08 | $30.26 | 5/5 | 8/10 | 333 |
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.77 | $11.22 | $17.68 | $28.70 | 5/5 | 8/10 | 323 |
| `v50_thinedge_ask90_edge3_stc500_cap75` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.77 | $11.54 | $17.98 | $29.02 | 5/5 | 8/10 | 322 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.77 | $9.84 | $16.54 | $28.18 | 5/5 | 7/10 | 335 |
| `v50_thinedge_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.77 | $9.68 | $16.38 | $28.02 | 5/5 | 7/10 | 335 |
| `v50_thinedge_ask90_edge2_stc450_cap75` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 81.33% | $0.71 | $9.88 | $16.56 | $28.22 | 5/5 | 7/10 | 334 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.70 | $10.98 | $17.64 | $28.66 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.70 | $10.95 | $17.61 | $28.64 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.69 | $8.95 | $15.33 | $26.78 | 5/5 | 7/10 | 319 |
| `v50_thinedge_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.69 | $8.79 | $15.17 | $26.62 | 5/5 | 7/10 | 319 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 81.33% | $0.68 | $9.37 | $15.87 | $27.40 | 5/5 | 6/10 | 325 |
| `v50_thinedge_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 81.33% | $0.68 | $9.21 | $15.71 | $27.24 | 5/5 | 6/10 | 325 |
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.64 | $9.40 | $16.12 | $27.74 | 5/5 | 7/10 | 336 |
| `v50_thinedge_ask90_edge3_stc500_cap75` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.64 | $9.72 | $16.42 | $28.06 | 5/5 | 7/10 | 335 |
| `v50_thinedge_ask90_edge2_stc450_cap75` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 80.00% | $0.62 | $9.41 | $15.89 | $27.44 | 5/5 | 7/10 | 324 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.61 | $10.10 | $16.54 | $27.42 | 5/5 | 7/10 | 322 |
| `v50_thinedge_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.61 | $10.07 | $16.51 | $27.40 | 5/5 | 7/10 | 322 |
| `v50_thinedge_ask90_edge3_stc500_cap75` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.56 | $8.83 | $15.21 | $26.66 | 5/5 | 7/10 | 319 |
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.56 | $8.51 | $14.91 | $26.34 | 5/5 | 6/10 | 320 |
| `v50_thinedge_ask90_edge3_stc500_cap75` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 81.33% | $0.55 | $9.25 | $15.75 | $27.28 | 5/5 | 6/10 | 325 |
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 81.33% | $0.55 | $8.93 | $15.45 | $26.96 | 5/5 | 6/10 | 326 |
| `v50_thinedge_ask90_edge3_stc500_cap75` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.54 | $10.72 | $17.36 | $28.36 | 5/5 | 8/10 | 332 |
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.53 | $10.81 | $17.49 | $28.52 | 5/5 | 8/10 | 334 |
| `v50_thinedge_ask90_edge3_stc500_cap75` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.45 | $9.84 | $16.26 | $27.12 | 5/5 | 7/10 | 321 |

## Read

- Best robust v50 row is `v50_thinedge_ask90_edge1_stc450_cap75` / `edge0_ask100_p0.65_stc0-600` / `prob54` with min split fee+1c $0.99 and all-market fee+1c $12.54.
- Treat this as research evidence requiring strict-forward validation, not a live-bot patch.
