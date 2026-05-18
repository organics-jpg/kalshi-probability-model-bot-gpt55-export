# v55 Book-Anchored Re-cross FV Strategy

Generated UTC: `2026-05-05T07:59:26.432365+00:00`

## Scope

- Research-only FV probability transform on top of v50.
- Anchors moderate near-strike extrapolation back toward the book.
- Live bot untouched.

## Search

- Candidate probability surfaces: 7
- Rows evaluated after 80% coverage prefilter: 1555
- Robust rows: 31

## Holdout Probability

| candidate | Brier | logloss | side acc |
|---|---:|---:|---:|
| `v55_bookanchor_m10_v15_g05_book_plus2` | 0.14153 | 0.42537 | 79.27% |
| `v55_bookanchor_m10_v15_g05_book` | 0.14161 | 0.42546 | 79.15% |
| `v55_bookanchor_m10_v20_g05_book_plus2` | 0.14176 | 0.42589 | 79.31% |
| `v55_bookanchor_m10_v20_g05_book` | 0.14182 | 0.42597 | 79.22% |
| `v55_bookanchor_m10_v20_g06_book` | 0.14184 | 0.42605 | 79.24% |
| `v55_bookanchor_m10_v15_g05_cap75` | 0.14217 | 0.42714 | 78.99% |
| `v50_thinedge_ask90_edge1_stc450_cap75` | 0.14220 | 0.42718 | 78.99% |

## Selected Strategy Rows

| model | entry | exit | min cov | min 1c | all 1c | days | block10 | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.93 | $13.36 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.35 | $12.88 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.99 | $12.54 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc60-600` | `prob52` | 80.00% | $0.84 | $12.48 | 5/5 | 8/10 | 322 |
| `v55_bookanchor_m10_v15_g05_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.99 | $12.00 | 5/5 | 8/10 | 332 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.26 | $12.00 | 5/5 | 7/10 | 322 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.35 | $11.88 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.90 | $11.66 | 5/5 | 8/10 | 322 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-570` | `prob52` | 81.33% | $0.64 | $11.58 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v15_g05_cap75` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.90 | $11.36 | 5/5 | 8/10 | 322 |
| `v55_bookanchor_m10_v15_g05_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.35 | $11.34 | 5/5 | 8/10 | 332 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.06 | $11.10 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-600` | `prob52` | 80.00% | $0.26 | $11.00 | 5/5 | 7/10 | 322 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.70 | $10.98 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc60-570` | `prob52` | 80.00% | $0.55 | $10.70 | 5/5 | 7/10 | 322 |
| `v55_bookanchor_m10_v15_g05_cap75` | `edge0_ask100_p0.65_stc60-600` | `prob52` | 80.00% | $0.26 | $10.70 | 5/5 | 7/10 | 322 |
| `v55_bookanchor_m10_v15_g05_cap75` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.70 | $10.52 | 5/5 | 8/10 | 332 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-570` | `prob52` | 81.33% | $0.06 | $10.32 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.61 | $10.10 | 5/5 | 7/10 | 322 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc0-600` | `prob52` | 82.67% | $0.31 | $10.05 | 5/5 | 7/10 | 335 |
| `v55_bookanchor_m10_v15_g05_cap75` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.61 | $9.88 | 5/5 | 7/10 | 322 |
| `v55_bookanchor_m10_v15_g05_cap75` | `edge0_ask100_p0.65_stc0-570` | `prob52` | 81.33% | $0.06 | $9.86 | 5/5 | 8/10 | 332 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.77 | $9.84 | 5/5 | 7/10 | 335 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc0-570` | `prob52` | 81.33% | $0.64 | $9.29 | 5/5 | 8/10 | 334 |
| `v55_bookanchor_m10_v15_g05_cap75` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.77 | $9.18 | 5/5 | 7/10 | 334 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc120-600` | `prob52` | 80.00% | $0.23 | $9.16 | 5/5 | 7/10 | 319 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.05 | $8.96 | 5/5 | 7/10 | 319 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.69 | $8.95 | 5/5 | 7/10 | 319 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc60-570` | `prob52` | 80.00% | $0.55 | $8.82 | 5/5 | 7/10 | 324 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 81.33% | $0.06 | $8.63 | 5/5 | 8/10 | 334 |

## Read

- Best v55 row is `v55_bookanchor_m10_v20_g05_book_plus2` / `edge0_ask100_p0.65_stc0-600` / `prob52` with min split fee+1c $0.93 and all-market fee+1c $13.36.
- Strict-forward validation is required before promotion.
