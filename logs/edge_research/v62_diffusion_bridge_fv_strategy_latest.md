# v62 Diffusion-Bridge FV Strategy

Generated UTC: `2026-05-05T11:09:00.927040+00:00`

## Scope

- Research-only FV probability transform on top of v55.
- Blends near-strike probability with a distance/time diffusion prior.
- Live bot untouched.

## Search

- Candidate probability surfaces: 13
- Rows evaluated after 80% coverage prefilter: 3175
- Robust rows: 15

## Holdout Probability

| candidate | Brier | logloss | side acc | mean p_yes |
|---|---:|---:|---:|---:|
| `v62_diff_m100_t125_w25` | 0.14096 | 0.42418 | 79.31% | 49.76% |
| `v62_diff_m100_t150_w50` | 0.14105 | 0.42463 | 79.34% | 49.84% |
| `v62_diff_m075_t125_w25` | 0.14117 | 0.42476 | 79.31% | 49.72% |
| `v62_diff_m100_t150_w25` | 0.14118 | 0.42475 | 79.31% | 49.74% |
| `v62_diff_m075_t150_w50` | 0.14124 | 0.42516 | 79.34% | 49.79% |
| `v62_diff_m075_t150_w25` | 0.14136 | 0.42523 | 79.31% | 49.72% |
| `v62_diff_m050_t125_w25` | 0.14144 | 0.42527 | 79.29% | 49.70% |
| `v62_diff_m100_t200_w25` | 0.14155 | 0.42569 | 79.31% | 49.73% |
| `v62_diff_m050_t150_w25` | 0.14159 | 0.42560 | 79.29% | 49.71% |
| `v62_diff_m075_t200_w25` | 0.14165 | 0.42593 | 79.31% | 49.72% |
| `v62_diff_m100_t200_w50` | 0.14167 | 0.42630 | 79.31% | 49.81% |
| `v55_bookanchor_m10_v20_g05_book_plus2` | 0.14176 | 0.42589 | 79.31% | 49.65% |
| `v62_diff_m050_t200_w25` | 0.14178 | 0.42605 | 79.29% | 49.72% |

## Selected Strategy Rows

| model | entry | exit | min cov | min 1c | all 1c | days | block10 | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.93 | $13.36 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.35 | $12.88 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc60-600` | `prob52` | 80.00% | $0.84 | $12.48 | 5/5 | 8/10 | 322 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.26 | $12.00 | 5/5 | 7/10 | 322 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-570` | `prob52` | 81.33% | $0.64 | $11.58 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.06 | $11.10 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc60-570` | `prob52` | 80.00% | $0.55 | $10.70 | 5/5 | 7/10 | 322 |
| `v62_diff_m075_t200_w25` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 81.33% | $0.60 | $10.17 | 5/5 | 7/10 | 332 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc0-600` | `prob52` | 82.67% | $0.31 | $10.05 | 5/5 | 7/10 | 335 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc0-570` | `prob52` | 81.33% | $0.64 | $9.29 | 5/5 | 8/10 | 334 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc120-600` | `prob52` | 80.00% | $0.23 | $9.16 | 5/5 | 7/10 | 319 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.05 | $8.96 | 5/5 | 7/10 | 319 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc60-570` | `prob52` | 80.00% | $0.55 | $8.82 | 5/5 | 7/10 | 324 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 81.33% | $0.06 | $8.63 | 5/5 | 8/10 | 334 |
| `v62_diff_m075_t200_w25` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 81.33% | $0.29 | $8.58 | 5/5 | 7/10 | 331 |

## Read

- Best v62 row is `v55_bookanchor_m10_v20_g05_book_plus2` / `edge0_ask100_p0.65_stc0-600` / `prob52` with min split fee+1c $0.93 and all-market fee+1c $13.36.
- Treat this as a probability-surface candidate requiring strict-forward validation before promotion.
