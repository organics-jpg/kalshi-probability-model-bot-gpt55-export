# v44 Fast Physics Latent-Hole FV Strategy

Generated UTC: `2026-05-05T05:52:17.567276+00:00`

## Scope

- Research-only targeted test using cached v41 physics/book probability predictions.
- Tests whether the v43 latent-hole book blend improves those FV surfaces without hard entry vetoes.
- Uses the v42 entry/exit replay with at least 80% chronological split coverage.
- Live bot untouched.

## Model Notes

- Latent-hole markets: 45
- Latent-hole opportunity rows: 1356
- Candidate probability surfaces: 31

## Holdout Probability

| candidate | rows | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---:|---:|---:|---:|---:|---:|
| `v44_source_v41_v38_bookres_l230` | 4307 | 0.13583 | 0.40859 | 79.43% | 49.30% | 54.03% |
| `v44_v41_v38_bookres_l230_holeblend80` | 4307 | 0.13583 | 0.40851 | 79.45% | 49.33% | 54.03% |
| `v44_v41_v38_bookres_l230_holeblend90` | 4307 | 0.13584 | 0.40851 | 79.45% | 49.34% | 54.03% |
| `v44_v41_v38_bookres_l230_holeblend100` | 4307 | 0.13584 | 0.40852 | 79.45% | 49.34% | 54.03% |
| `v44_v41_v39_bookres_l230_holeblend80` | 4307 | 0.13585 | 0.40853 | 79.45% | 49.34% | 54.03% |
| `v44_v41_v39_bookres_l230_holeblend90` | 4307 | 0.13585 | 0.40853 | 79.45% | 49.34% | 54.03% |
| `v44_source_v41_v39_bookres_l230` | 4307 | 0.13586 | 0.40864 | 79.43% | 49.30% | 54.03% |
| `v44_v41_v39_bookres_l230_holeblend100` | 4307 | 0.13586 | 0.40853 | 79.45% | 49.34% | 54.03% |
| `v44_v41_v38_bookres_l230_outside_source_inside_v43hole90` | 4307 | 0.13590 | 0.40866 | 79.43% | 49.34% | 54.03% |
| `v44_v41_v39_bookres_l230_outside_source_inside_v43hole90` | 4307 | 0.13592 | 0.40868 | 79.43% | 49.35% | 54.03% |
| `v44_source_v41_v38_bookres_l210` | 4307 | 0.13627 | 0.40962 | 79.45% | 49.11% | 54.03% |
| `v44_source_v41_v39_bookres_l210` | 4307 | 0.13630 | 0.40962 | 79.43% | 49.12% | 54.03% |
| `v44_v41_v38_bookres_l210_holeblend80` | 4307 | 0.13639 | 0.40999 | 79.45% | 49.15% | 54.03% |
| `v44_v41_v39_bookres_l210_holeblend80` | 4307 | 0.13641 | 0.40997 | 79.43% | 49.16% | 54.03% |
| `v44_v41_v38_bookres_l210_holeblend90` | 4307 | 0.13641 | 0.41005 | 79.45% | 49.16% | 54.03% |
| `v44_v41_v39_bookres_l210_holeblend90` | 4307 | 0.13643 | 0.41002 | 79.43% | 49.16% | 54.03% |
| `v44_v41_v38_bookres_l210_holeblend100` | 4307 | 0.13643 | 0.41010 | 79.45% | 49.17% | 54.03% |
| `v44_v41_v39_bookres_l210_holeblend100` | 4307 | 0.13644 | 0.41008 | 79.43% | 49.17% | 54.03% |

## Strategy Search

- Rows evaluated after 80% coverage prefilter: 10310
- Fee+1c positive train/validation/holdout rows: 11
- Fee+1c positive all-day rows: 5
- All-day rows with at least 7/10 positive chronological blocks: 3

## Selected Strategy Rows

| model | entry | exit | min cov | min 1c | all 1c | all fee | gross | days | block10 | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.45 | $9.85 | $16.63 | $28.38 | 5/5 | 7/10 | 339 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.36 | $8.79 | $15.35 | $26.94 | 5/5 | 7/10 | 328 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.23 | $6.94 | $13.76 | $25.96 | 5/5 | 8/10 | 341 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.15 | $6.20 | $12.76 | $24.80 | 5/5 | 6/10 | 328 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 81.33% | $0.14 | $6.29 | $12.91 | $24.98 | 5/5 | 6/10 | 331 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.28 | $8.48 | $15.26 | $26.90 | 4/5 | 7/10 | 339 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.19 | $7.42 | $13.98 | $25.46 | 4/5 | 6/10 | 328 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 82.67% | $0.14 | $5.77 | $12.59 | $24.66 | 4/5 | 7/10 | 341 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.64_stc120-570` | `prob54` | 80.00% | $0.06 | $5.03 | $11.59 | $23.50 | 4/5 | 6/10 | 328 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.64_stc60-570` | `prob54` | 81.33% | $0.05 | $5.12 | $11.74 | $23.68 | 4/5 | 6/10 | 331 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc0-600` | `prob56` | 81.33% | $0.03 | $7.14 | $13.92 | $25.98 | 3/5 | 7/10 | 339 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc0-780` | `prob56` | 84.00% | $-0.13 | $0.42 | $7.26 | $21.54 | 2/5 | 6/10 | 342 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $-0.19 | $8.39 | $15.17 | $26.86 | 4/5 | 7/10 | 339 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc60-600` | `prob52` | 80.00% | $-0.28 | $7.33 | $13.89 | $25.42 | 4/5 | 7/10 | 328 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc60-600` | `prob56` | 80.00% | $-0.30 | $6.08 | $12.64 | $24.54 | 3/5 | 7/10 | 328 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc0-570` | `prob52` | 81.33% | $-0.36 | $7.02 | $13.80 | $25.38 | 4/5 | 7/10 | 339 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc0-570` | `prob56` | 81.33% | $-0.42 | $5.77 | $12.55 | $24.50 | 3/5 | 7/10 | 339 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc60-570` | `prob52` | 80.00% | $-0.45 | $5.96 | $12.52 | $23.94 | 4/5 | 6/10 | 328 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.66_stc0-780` | `prob56` | 81.33% | $-0.53 | $1.14 | $7.90 | $21.60 | 2/5 | 5/10 | 338 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.64_stc0-600` | `prob56` | 82.67% | $-0.57 | $4.46 | $11.28 | $23.80 | 3/5 | 6/10 | 341 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc60-780` | `prob56` | 82.67% | $-0.67 | $-0.62 | $6.04 | $20.18 | 1/5 | 5/10 | 333 |
| `v44_v38_holeblend90_reference` | `edge-2_ask100_p0.64_stc0-780` | `prob56` | 89.33% | $-0.73 | $-1.56 | $5.54 | $20.60 | 1/5 | 5/10 | 355 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc60-570` | `prob56` | 80.00% | $-0.75 | $4.71 | $11.27 | $23.06 | 3/5 | 7/10 | 328 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.65_stc120-780` | `prob56` | 81.33% | $-0.77 | $-0.71 | $5.89 | $20.00 | 1/5 | 5/10 | 330 |
| `v44_v38_holeblend90_reference` | `edge-2_ask100_p0.64_stc60-780` | `prob56` | 86.67% | $-0.80 | $-1.75 | $5.13 | $20.14 | 1/5 | 5/10 | 344 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.64_stc0-600` | `prob52` | 82.67% | $-0.81 | $5.18 | $12.00 | $24.14 | 4/5 | 8/10 | 341 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.66_stc60-780` | `prob56` | 80.00% | $-0.86 | $0.08 | $6.62 | $20.16 | 2/5 | 5/10 | 327 |
| `v44_v38_holeblend90_reference` | `edge0_ask100_p0.64_stc120-600` | `prob52` | 80.00% | $-0.89 | $4.44 | $11.00 | $22.98 | 4/5 | 6/10 | 328 |
| `v44_v41_v39_core_l210_holeblend100` | `edge0_ask100_p0.64_stc0-780` | `prob50` | 97.30% | $-0.89 | $10.96 | $18.22 | $34.90 | 3/5 | 5/10 | 363 |
| `v44_v41_v39_core_l210_holeblend100` | `edge0_ask100_p0.64_stc60-780` | `prob50` | 95.96% | $-0.89 | $10.58 | $17.76 | $34.38 | 3/5 | 5/10 | 359 |

## Read

- Best robust v44 fast row is `v44_v38_holeblend90_reference` / `edge0_ask100_p0.65_stc0-600` / `prob54` with min split fee+1c $0.45.
- Best split-positive v44 fast row is `v44_v38_holeblend90_reference` / `edge0_ask100_p0.65_stc0-600` / `prob54` with min split fee+1c $0.45.
