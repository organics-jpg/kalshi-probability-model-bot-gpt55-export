# v47 Re-cross Hazard FV Strategy

Generated UTC: `2026-05-05T06:17:16.181425+00:00`

## Scope

- Research-only FV probability transform on top of the v45 lead.
- Tests whether fresh favorable bursts near the strike should cap selected-side probability.
- Entry/exit replay keeps the same 80% split-coverage, fee, and 1c haircut checks.
- Live bot untouched.

## Physics Notes

- Base model: `v45_latent_disagree_book_else_blend90`
- Main hazard: selected side within 1.0 RV sigma and 3m selected-side velocity >= 0.50 dps
- Main hazard rows: 256
- Tighter margin hazard rows: 197
- One-minute burst hazard rows: 131

## Holdout Probability

| candidate | Brier | logloss | side acc | mean p_yes |
|---|---:|---:|---:|---:|
| `v47_recross_sigma1_v3cap72` | 0.14215 | 0.42737 | 78.99% | 49.68% |
| `v47_recross_sigma1_v3cap68` | 0.14223 | 0.42755 | 78.99% | 49.68% |
| `v45_latent_disagree_book_else_blend90` | 0.14228 | 0.42788 | 78.99% | 49.70% |
| `v47_recross_v1_2_shrink80` | 0.14232 | 0.42825 | 78.99% | 49.71% |
| `v47_recross_sigma075_v3cap75` | 0.14241 | 0.42831 | 78.99% | 49.68% |

## Strategy Search

- Candidate probability surfaces: 5
- Rows evaluated after 80% coverage prefilter: 1125
- Fee+1c positive train/validation/holdout rows: 70
- Fee+1c positive all-day rows: 34
- All-day rows with at least 7/10 positive chronological blocks: 23

## Selected Strategy Rows

| model | entry | exit | min cov | min 1c | all 1c | all fee | gross | days | block10 | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.86 | $12.10 | $18.78 | $29.94 | 5/5 | 8/10 | 334 |
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.77 | $11.22 | $17.68 | $28.70 | 5/5 | 8/10 | 323 |
| `v47_recross_sigma1_v3cap72` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.77 | $10.92 | $17.60 | $28.78 | 5/5 | 8/10 | 334 |
| `v47_recross_v1_2_shrink80` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.71 | $10.91 | $17.59 | $28.80 | 5/5 | 8/10 | 334 |
| `v47_recross_sigma1_v3cap72` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.68 | $10.04 | $16.50 | $27.54 | 5/5 | 7/10 | 323 |
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.64 | $9.40 | $16.12 | $27.74 | 5/5 | 7/10 | 336 |
| `v47_recross_v1_2_shrink80` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.62 | $10.03 | $16.49 | $27.56 | 5/5 | 7/10 | 323 |
| `v47_recross_sigma075_v3cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.61 | $11.22 | $17.90 | $29.10 | 5/5 | 8/10 | 334 |
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.56 | $8.51 | $14.91 | $26.34 | 5/5 | 6/10 | 320 |
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 81.33% | $0.55 | $8.93 | $15.45 | $26.96 | 5/5 | 6/10 | 326 |
| `v47_recross_sigma1_v3cap72` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.55 | $7.83 | $14.55 | $26.18 | 5/5 | 7/10 | 336 |
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.53 | $10.81 | $17.49 | $28.52 | 5/5 | 8/10 | 334 |
| `v47_recross_sigma075_v3cap75` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.52 | $10.34 | $16.80 | $27.86 | 5/5 | 7/10 | 323 |
| `v47_recross_v1_2_shrink80` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.49 | $8.00 | $14.72 | $26.38 | 5/5 | 6/10 | 336 |
| `v47_recross_sigma1_v3cap72` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.47 | $6.94 | $13.34 | $24.78 | 5/5 | 6/10 | 320 |
| `v47_recross_sigma1_v3cap72` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 81.33% | $0.46 | $7.36 | $13.88 | $25.40 | 5/5 | 6/10 | 326 |
| `v45_latent_disagree_book_else_blend90` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.45 | $10.55 | $17.23 | $28.42 | 5/5 | 8/10 | 334 |
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.44 | $9.93 | $16.39 | $27.28 | 5/5 | 7/10 | 323 |
| `v47_recross_sigma1_v3cap72` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.44 | $9.63 | $16.31 | $27.36 | 5/5 | 8/10 | 334 |
| `v47_recross_v1_2_shrink80` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 81.33% | $0.40 | $7.53 | $14.05 | $25.60 | 5/5 | 6/10 | 326 |
| `v47_recross_sigma075_v3cap75` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.39 | $8.13 | $14.85 | $26.50 | 5/5 | 6/10 | 336 |
| `v45_latent_disagree_book_else_blend90` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.36 | $9.67 | $16.13 | $27.18 | 5/5 | 7/10 | 323 |
| `v47_recross_sigma1_v3cap72` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.35 | $8.75 | $15.21 | $26.12 | 5/5 | 7/10 | 323 |
| `v47_recross_sigma075_v3cap75` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.31 | $7.24 | $13.64 | $25.10 | 5/5 | 6/10 | 320 |
| `v47_recross_sigma075_v3cap75` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 81.33% | $0.30 | $7.66 | $14.18 | $25.72 | 5/5 | 6/10 | 326 |
| `v47_recross_sigma075_v3cap75` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.28 | $10.01 | $16.69 | $27.78 | 5/5 | 8/10 | 334 |
| `v45_latent_disagree_book_else_blend90` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.23 | $7.64 | $14.36 | $26.00 | 5/5 | 6/10 | 336 |
| `v47_recross_sigma1_v3cap68` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.22 | $11.44 | $18.12 | $29.24 | 5/5 | 8/10 | 334 |
| `v47_recross_sigma075_v3cap75` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.19 | $9.13 | $15.59 | $26.54 | 5/5 | 7/10 | 323 |
| `v45_latent_disagree_book_else_blend90` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 81.33% | $0.14 | $7.17 | $13.69 | $25.22 | 5/5 | 6/10 | 326 |

## Read

- Best robust v47 row is `v47_recross_sigma1_v3cap68` / `edge0_ask100_p0.65_stc0-600` / `prob54` with min split fee+1c $0.86 and all-market fee+1c $12.10.
- Treat this as a candidate requiring strict-forward validation, not a live-bot patch.
