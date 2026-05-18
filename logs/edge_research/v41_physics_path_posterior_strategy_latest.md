# v41 Physics/Path Posterior Strategy

Generated UTC: `2026-05-05T05:48:34.045000+00:00`

## Scope

- Train-only posterior probability models from v38/v39 plus path physics.
- Strategy projection requires at least 80% coverage in every chronological split.
- Entry simulation has an executable ask floor of 1c.
- Research-only; live bot untouched.

## Probability Holdout

| candidate | rows | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---:|---:|---:|---:|---:|---:|
| `v41_v38_physics_book_residual_l230` | 4307 | 0.13583 | 0.40859 | 79.43% | 49.30% | 54.03% |
| `v41_v39_physics_book_residual_l230` | 4307 | 0.13586 | 0.40864 | 79.43% | 49.30% | 54.03% |
| `v41_v39_physics_rich_l230` | 4307 | 0.13627 | 0.41503 | 79.17% | 49.19% | 54.03% |
| `v41_v38_physics_book_residual_l210` | 4307 | 0.13627 | 0.40962 | 79.45% | 49.11% | 54.03% |
| `v41_v38_physics_rich_l230` | 4307 | 0.13628 | 0.41512 | 79.15% | 49.19% | 54.03% |
| `v41_v39_physics_book_residual_l210` | 4307 | 0.13630 | 0.40962 | 79.43% | 49.12% | 54.03% |
| `v41_v39_physics_rich_l210` | 4307 | 0.13747 | 0.41950 | 79.13% | 49.01% | 54.03% |
| `v41_v38_physics_rich_l210` | 4307 | 0.13747 | 0.41957 | 79.08% | 49.01% | 54.03% |
| `v41_v39_physics_core_l210` | 4307 | 0.14246 | 0.42787 | 77.55% | 49.48% | 54.03% |
| `v41_v38_physics_core_l210` | 4307 | 0.14248 | 0.42798 | 77.52% | 49.48% | 54.03% |
| `v41_v39_physics_core_l230` | 4307 | 0.14284 | 0.42867 | 77.59% | 49.70% | 54.03% |
| `v41_v38_physics_core_l230` | 4307 | 0.14287 | 0.42881 | 77.59% | 49.70% | 54.03% |
| `v38_raw` | 4307 | 0.14318 | 0.43031 | 78.80% | 49.73% | 54.03% |
| `v39_raw` | 4307 | 0.14325 | 0.43027 | 78.89% | 49.75% | 54.03% |
| `v41_v39_physics_path_l230` | 4307 | 0.14406 | 0.43292 | 77.50% | 49.34% | 54.03% |

## Strategy Search

- Candidate probability surfaces: 18
- Rows evaluated after 80% coverage prefilter: 5418
- Fee+1c positive train/validation/holdout rows: 20
- Fee+1c positive across all UTC days rows: 1

## Best By Family

| family | model | veto | entry | exit | min cov | min 1c | all 1c | days | b10 | trades |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|
| `physics_path` | `v41_v38_physics_path_l210` | `block_first_edge_10_20` | `edge-3_ask95_p0.65_stc0-780` | `prob52` | 81.08% | $0.84 | $11.19 | 3/5 | 8/10 | 312 |
| `raw` | `v38_raw` | `none` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 82.67% | $0.66 | $5.53 | 4/5 | 6/10 | 343 |
| `physics_rich` | `v41_v38_physics_rich_l230` | `block_first_edge_8_20` | `edge-3_ask100_p0.60_stc0-780` | `hold` | 81.33% | $0.57 | $5.45 | 2/5 | 5/10 | 307 |
| `physics_core` | `v41_v39_physics_core_l210` | `block_first_edge_8_20` | `edge-3_ask95_p0.60_stc0-780` | `prob50` | 81.08% | $0.50 | $6.63 | 3/5 | 7/10 | 314 |

## Selected Strategy Rows

| model | veto | entry | exit | min cov | min 1c | all 1c | all fee | gross | days | b10 | trades |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `v41_v38_physics_path_l210` | `block_first_edge_10_20` | `edge-3_ask95_p0.65_stc0-780` | `prob52` | 81.08% | $0.84 | $11.19 | $17.43 | $32.46 | 3/5 | 8/10 | 312 |
| `v41_v38_physics_path_l210` | `block_first_edge_10_20` | `edge-3_ask100_p0.65_stc0-780` | `prob52` | 82.43% | $0.75 | $11.14 | $17.50 | $32.58 | 3/5 | 8/10 | 318 |
| `v38_raw` | `none` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 82.67% | $0.66 | $5.53 | $12.39 | $24.80 | 4/5 | 6/10 | 343 |
| `v41_v38_physics_rich_l230` | `block_first_edge_8_20` | `edge-3_ask100_p0.60_stc0-780` | `hold` | 81.33% | $0.57 | $5.45 | $11.59 | $22.22 | 2/5 | 5/10 | 307 |
| `v41_v38_physics_rich_l230` | `block_first_edge_8_20` | `edge-3_ask95_p0.60_stc0-780` | `hold` | 80.00% | $0.57 | $5.44 | $11.56 | $22.18 | 2/5 | 5/10 | 306 |
| `v41_v38_physics_path_l210` | `block_first_edge_10_20` | `edge0_ask100_p0.65_stc0-780` | `prob52` | 81.08% | $0.50 | $10.93 | $17.19 | $32.00 | 3/5 | 8/10 | 313 |
| `v41_v39_physics_core_l210` | `block_first_edge_8_20` | `edge-3_ask95_p0.60_stc0-780` | `prob50` | 81.08% | $0.50 | $6.63 | $12.91 | $28.32 | 3/5 | 7/10 | 314 |
| `v41_v39_physics_core_l210` | `block_first_edge_8_20` | `edge-3_ask100_p0.60_stc0-780` | `prob50` | 81.08% | $0.48 | $6.50 | $12.88 | $28.34 | 3/5 | 7/10 | 319 |
| `v41_v38_physics_path_l210` | `block_first_edge_10_20` | `edge1_ask100_p0.65_stc0-780` | `prob52` | 81.08% | $0.37 | $10.73 | $16.87 | $31.46 | 3/5 | 7/10 | 307 |
| `v41_v39_physics_path_l210` | `block_first_edge_10_20` | `edge0_ask100_p0.65_stc0-780` | `prob52` | 81.08% | $0.36 | $11.46 | $17.66 | $32.30 | 2/5 | 7/10 | 310 |
| `v41_v38_physics_path_l230` | `block_first_edge_8_20` | `edge-3_ask100_p0.60_stc0-780` | `prob52` | 80.00% | $0.29 | $9.65 | $15.77 | $31.42 | 5/5 | 6/10 | 306 |
| `v41_v38_physics_rich_l230` | `block_first_edge_10_20` | `edge1_ask100_p0.60_stc0-780` | `hold` | 82.43% | $0.13 | $6.51 | $13.09 | $24.42 | 2/5 | 5/10 | 329 |
| `v41_v38_physics_rich_l230` | `block_first_edge_10_20` | `edge1_ask95_p0.60_stc0-780` | `hold` | 82.43% | $0.13 | $6.51 | $13.09 | $24.42 | 2/5 | 5/10 | 329 |
| `v41_v38_physics_path_l230` | `block_first_edge_8_20` | `edge0_ask100_p0.60_stc0-780` | `prob52` | 80.00% | $0.12 | $10.39 | $16.41 | $31.68 | 4/5 | 6/10 | 301 |
| `v41_v38_physics_rich_l230` | `block_first_edge_8_20` | `edge-3_ask100_p0.60_stc0-780` | `prob56` | 81.33% | $0.12 | $3.69 | $9.83 | $27.20 | 3/5 | 6/10 | 307 |
| `v41_v38_physics_rich_l230` | `block_first_edge_8_20` | `edge-3_ask95_p0.60_stc0-780` | `prob56` | 80.00% | $0.12 | $3.68 | $9.80 | $27.16 | 3/5 | 6/10 | 306 |
| `v41_v39_physics_core_l210` | `block_first_edge_8_20` | `edge-3_ask95_p0.60_stc0-780` | `prob54` | 81.08% | $0.06 | $7.36 | $13.64 | $29.48 | 3/5 | 7/10 | 314 |
| `v41_v38_physics_rich_l230` | `block_first_edge_10_20` | `edge-3_ask100_p0.60_stc0-780` | `hold` | 83.78% | $0.05 | $6.98 | $13.66 | $25.32 | 2/5 | 5/10 | 334 |
| `v41_v38_physics_rich_l230` | `block_first_edge_10_20` | `edge-3_ask95_p0.60_stc0-780` | `hold` | 83.78% | $0.05 | $6.97 | $13.63 | $25.28 | 2/5 | 5/10 | 333 |
| `v38_raw` | `none` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 82.67% | $0.02 | $3.80 | $10.66 | $23.00 | 3/5 | 6/10 | 343 |
| `v41_v39_physics_core_l210` | `block_first_edge_8_20` | `edge-3_ask100_p0.60_stc0-780` | `prob54` | 81.08% | $-0.01 | $7.23 | $13.61 | $29.50 | 3/5 | 6/10 | 319 |
| `v41_v38_physics_path_l210` | `block_first_edge_10_20` | `edge-3_ask95_p0.65_stc0-780` | `prob54` | 81.08% | $-0.02 | $12.37 | $18.61 | $33.88 | 4/5 | 8/10 | 312 |
| `v41_v39_physics_path_l210` | `block_first_edge_10_20` | `edge-3_ask95_p0.65_stc0-780` | `prob54` | 81.08% | $-0.02 | $12.82 | $19.00 | $34.08 | 3/5 | 7/10 | 309 |
| `v41_v39_physics_rich_l230` | `block_first_edge_10_20` | `edge-3_ask100_p0.60_stc0-780` | `hold` | 83.78% | $-0.03 | $4.25 | $10.91 | $22.54 | 2/5 | 5/10 | 333 |
| `v41_v39_physics_rich_l230` | `block_first_edge_10_20` | `edge-3_ask95_p0.60_stc0-780` | `hold` | 83.78% | $-0.03 | $4.24 | $10.88 | $22.50 | 2/5 | 5/10 | 332 |
| `v41_v38_physics_path_l210` | `block_first_edge_10_20` | `edge-3_ask95_p0.65_stc0-780` | `prob50` | 81.08% | $-0.09 | $9.04 | $15.28 | $30.00 | 3/5 | 5/10 | 312 |
| `v41_v38_physics_path_l210` | `block_first_edge_10_20` | `edge-3_ask100_p0.65_stc0-780` | `prob54` | 82.43% | $-0.11 | $12.32 | $18.68 | $34.00 | 4/5 | 8/10 | 318 |
| `v41_v39_physics_path_l210` | `block_first_edge_10_20` | `edge-3_ask100_p0.65_stc0-780` | `prob54` | 82.43% | $-0.11 | $12.75 | $19.05 | $34.18 | 3/5 | 7/10 | 315 |
| `v41_v39_physics_rich_l230` | `block_first_edge_8_20` | `edge-3_ask100_p0.60_stc0-780` | `prob56` | 81.33% | $-0.14 | $3.44 | $9.60 | $27.06 | 4/5 | 6/10 | 308 |
| `v41_v39_physics_rich_l230` | `block_first_edge_8_20` | `edge-3_ask95_p0.60_stc0-780` | `prob56` | 80.00% | $-0.14 | $3.43 | $9.57 | $27.02 | 4/5 | 6/10 | 307 |

## Read

- Best fee+1c split-positive row is `v41_v38_physics_path_l210` / `block_first_edge_10_20` / `edge-3_ask95_p0.65_stc0-780` / `prob52` with min split fee+1c $0.84 and all-market fee+1c $11.19.
- Best all-day-positive row is `v41_v38_physics_path_l230` with min split fee+1c $0.29.
- Book-residual rows are labeled separately because they are observation-aided, not purely physical.
