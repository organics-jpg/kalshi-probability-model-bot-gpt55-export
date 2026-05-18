# v52 Weak Re-cross Hazard FV Strategy

Generated UTC: `2026-05-05T07:31:34.631759+00:00`

## Scope

- Research-only FV probability transform on top of v45.
- Sweeps weaker near-strike re-cross caps than v47.
- Live bot untouched.

## Physics Notes

- Base model: `v45_latent_disagree_book_else_blend90`
- Hypothesis: v47 re-cross hazard threshold is too strict; moderate favorable velocity near strike is also fragile.
- `v52_weakrecross_sigma1_v3p10_cap68` hazard rows: 2475
- `v52_weakrecross_sigma1_v3p15_cap68` hazard rows: 1813
- `v52_weakrecross_sigma1_v3p20_cap68` hazard rows: 1303
- `v52_weakrecross_sigma1_v3p25_cap68` hazard rows: 968
- `v52_weakrecross_sigma1_v3p15_cap72` hazard rows: 1813
- `v52_weakrecross_sigma1_v3p15_cap75` hazard rows: 1813
- `v52_weakrecross_sigma08_v3p15_cap68` hazard rows: 1640
- `v52_weakrecross_sigma12_v3p15_cap68` hazard rows: 1989

## Holdout Probability

| candidate | Brier | logloss | side acc | mean p_yes |
|---|---:|---:|---:|---:|
| `v52_weakrecross_sigma1_v3p15_cap75` | 0.14219 | 0.42770 | 78.99% | 49.70% |
| `v52_weakrecross_sigma1_v3p15_cap72` | 0.14221 | 0.42774 | 78.99% | 49.70% |
| `v45_latent_disagree_book_else_blend90` | 0.14228 | 0.42788 | 78.99% | 49.70% |
| `v52_weakrecross_sigma1_v3p25_cap68` | 0.14228 | 0.42779 | 78.99% | 49.75% |
| `v52_weakrecross_sigma1_v3p10_cap68` | 0.14232 | 0.42803 | 78.99% | 49.70% |
| `v52_weakrecross_sigma1_v3p15_cap68` | 0.14237 | 0.42812 | 78.99% | 49.71% |
| `v52_weakrecross_sigma1_v3p20_cap68` | 0.14237 | 0.42809 | 78.99% | 49.72% |
| `v52_weakrecross_sigma08_v3p15_cap68` | 0.14274 | 0.42921 | 78.99% | 49.69% |
| `v52_weakrecross_sigma12_v3p15_cap68` | 0.14279 | 0.42952 | 78.99% | 49.69% |

## Strategy Search

- Candidate probability surfaces: 9
- Rows evaluated after 80% coverage prefilter: 1665
- Fee+1c positive train/validation/holdout rows: 126
- Fee+1c positive all-day rows: 43
- All-day rows with at least 7/10 positive chronological blocks: 38

## Selected Strategy Rows

| model | entry | exit | min cov | min 1c | all 1c | days | block10 | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `v52_weakrecross_sigma08_v3p15_cap68` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.96 | $11.98 | 5/5 | 8/10 | 333 |
| `v52_weakrecross_sigma08_v3p15_cap68` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.87 | $11.27 | 5/5 | 8/10 | 322 |
| `v52_weakrecross_sigma08_v3p15_cap68` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.74 | $9.47 | 5/5 | 7/10 | 335 |
| `v52_weakrecross_sigma1_v3p15_cap68` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $0.73 | $11.41 | 5/5 | 8/10 | 332 |
| `v52_weakrecross_sigma1_v3p20_cap68` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $0.73 | $10.67 | 5/5 | 8/10 | 332 |
| `v52_weakrecross_sigma08_v3p15_cap68` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.66 | $8.75 | 5/5 | 6/10 | 319 |
| `v52_weakrecross_sigma08_v3p15_cap68` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.65 | $11.75 | 5/5 | 8/10 | 333 |
| `v52_weakrecross_sigma08_v3p15_cap68` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 81.33% | $0.65 | $9.17 | 5/5 | 5/10 | 325 |
| `v52_weakrecross_sigma1_v3p25_cap68` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $0.62 | $11.04 | 5/5 | 8/10 | 333 |
| `v52_weakrecross_sigma08_v3p15_cap68` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.56 | $11.04 | 5/5 | 7/10 | 322 |
| `v52_weakrecross_sigma1_v3p15_cap68` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 81.33% | $0.51 | $8.90 | 5/5 | 7/10 | 334 |
| `v52_weakrecross_sigma08_v3p15_cap68` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 82.67% | $0.51 | $8.87 | 5/5 | 7/10 | 335 |
| `v52_weakrecross_sigma1_v3p20_cap68` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 81.33% | $0.51 | $7.95 | 5/5 | 7/10 | 334 |
| `v45_latent_disagree_book_else_blend90` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.45 | $10.55 | 5/5 | 8/10 | 334 |
| `v52_weakrecross_sigma1_v3p15_cap72` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $0.44 | $11.06 | 5/5 | 8/10 | 332 |
| `v52_weakrecross_sigma08_v3p15_cap68` | `edge0_ask100_p0.64_stc120-570` | `prob54` | 80.00% | $0.43 | $8.15 | 5/5 | 7/10 | 319 |
| `v52_weakrecross_sigma1_v3p15_cap68` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 80.00% | $0.42 | $11.46 | 5/5 | 8/10 | 332 |
| `v52_weakrecross_sigma1_v3p20_cap68` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 80.00% | $0.42 | $10.16 | 5/5 | 8/10 | 332 |
| `v52_weakrecross_sigma1_v3p15_cap68` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 80.00% | $0.42 | $8.60 | 5/5 | 7/10 | 324 |
| `v52_weakrecross_sigma08_v3p15_cap68` | `edge0_ask100_p0.64_stc60-570` | `prob54` | 81.33% | $0.42 | $8.57 | 5/5 | 6/10 | 325 |
| `v52_weakrecross_sigma1_v3p20_cap68` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 80.00% | $0.42 | $7.65 | 5/5 | 7/10 | 324 |
| `v52_weakrecross_sigma1_v3p25_cap68` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 81.33% | $0.40 | $8.32 | 5/5 | 7/10 | 335 |
| `v52_weakrecross_sigma1_v3p15_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $0.38 | $10.47 | 5/5 | 8/10 | 332 |
| `v45_latent_disagree_book_else_blend90` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.36 | $9.67 | 5/5 | 7/10 | 323 |
| `v52_weakrecross_sigma08_v3p15_cap68` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.32 | $11.32 | 5/5 | 8/10 | 333 |
| `v52_weakrecross_sigma1_v3p25_cap68` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 80.00% | $0.31 | $10.30 | 5/5 | 8/10 | 333 |
| `v52_weakrecross_sigma1_v3p25_cap68` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 80.00% | $0.31 | $7.85 | 5/5 | 7/10 | 325 |
| `v52_weakrecross_sigma1_v3p15_cap68` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 81.33% | $0.28 | $8.58 | 5/5 | 8/10 | 334 |
| `v52_weakrecross_sigma1_v3p20_cap68` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 81.33% | $0.28 | $7.28 | 5/5 | 8/10 | 334 |
| `v52_weakrecross_sigma08_v3p15_cap68` | `edge0_ask100_p0.65_stc60-600` | `prob52` | 80.00% | $0.23 | $10.61 | 5/5 | 7/10 | 322 |

## Read

- Best robust row is `v52_weakrecross_sigma08_v3p15_cap68` / `edge0_ask100_p0.65_stc0-600` / `prob54` with min split fee+1c $0.96 and all-market fee+1c $11.98.
- Treat this as a hypothesis screen; strict-forward validation is still required.
