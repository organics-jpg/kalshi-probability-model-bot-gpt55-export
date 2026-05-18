# v68 Regularized Physics-Logit FV Strategy

Generated UTC: `2026-05-05T12:12:58.792143+00:00`

## Scope

- Research-only train-split logistic calibration on top of v55/book/physics features.
- Tests probability accuracy and executable 80%+ coverage P&L separately.
- Live bot untouched.

## Holdout Probability

| candidate | Brier | logloss | side acc |
|---|---:|---:|---:|
| `v68_l2_C1p0` | 0.13377 | 0.40353 | 79.92% |
| `v68_l2_C0p5` | 0.13378 | 0.40348 | 79.92% |
| `v68_l2_C0p2` | 0.13378 | 0.40330 | 79.87% |
| `v68_l2_C0p1` | 0.13380 | 0.40312 | 79.75% |
| `v68_l2_C0p05` | 0.13384 | 0.40290 | 79.89% |
| `v68_l2_C0p02` | 0.13426 | 0.40365 | 79.94% |
| `v55_bookanchor_m10_v20_g05_book_plus2` | 0.14176 | 0.42589 | 79.31% |

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
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc0-600` | `prob52` | 82.67% | $0.31 | $10.05 | 5/5 | 7/10 | 335 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc0-570` | `prob52` | 81.33% | $0.64 | $9.29 | 5/5 | 8/10 | 334 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc120-600` | `prob52` | 80.00% | $0.23 | $9.16 | 5/5 | 7/10 | 319 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.05 | $8.96 | 5/5 | 7/10 | 319 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc60-570` | `prob52` | 80.00% | $0.55 | $8.82 | 5/5 | 7/10 | 324 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 81.33% | $0.06 | $8.63 | 5/5 | 8/10 | 334 |

## Read

- Best holdout calibration is `v68_l2_C1p0` with Brier 0.13377 and logloss 0.40353.
- Best robust row is `v55_bookanchor_m10_v20_g05_book_plus2` with all fee+1c $13.36.
- Treat v68 as calibration evidence, not a promotion candidate.
