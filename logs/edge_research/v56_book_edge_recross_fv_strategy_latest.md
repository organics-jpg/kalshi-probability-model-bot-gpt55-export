# v56 Book-Edge Re-cross FV Strategy

Generated UTC: `2026-05-05T08:18:04.763435+00:00`

## Scope

- Research-only FV probability transform on top of v50.
- Tests whether unsupported near-strike model/book edge should be anchored fully to book.
- Live bot untouched.

## Search

- Candidate probability surfaces: 10
- Rows evaluated after 80% coverage prefilter: 2415
- Robust rows: 9

## Holdout Probability

| candidate | Brier | logloss | side acc |
|---|---:|---:|---:|
| `v56_bedge1_m11_v15_g05_book_else_plus2` | 0.14129 | 0.42455 | 79.17% |
| `v56_bedge0_m11_v15_g05_book_else_plus2` | 0.14129 | 0.42456 | 79.17% |
| `v56_bedge1_m10_v15_g04_book_else_plus2` | 0.14154 | 0.42528 | 79.15% |
| `v56_bedge0_m10_v15_g04_book_else_plus2` | 0.14154 | 0.42531 | 79.15% |
| `v56_bedge1_m10_v15_g05_book_else_plus2` | 0.14161 | 0.42546 | 79.15% |
| `v56_bedge2_m10_v15_g05_book_else_plus2` | 0.14161 | 0.42546 | 79.15% |
| `v56_bedge0_m10_v15_g05_book_else_plus2` | 0.14161 | 0.42548 | 79.15% |
| `v56_bedge1_m10_v20_g05_book_else_plus2` | 0.14182 | 0.42597 | 79.22% |
| `v56_bedge0_m10_v20_g05_book_else_plus2` | 0.14182 | 0.42599 | 79.22% |
| `v50_thinedge_ask90_edge1_stc450_cap75` | 0.14220 | 0.42718 | 78.99% |

## Selected Strategy Rows

| model | entry | exit | min cov | min 1c | all 1c | days | block10 | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.99 | $12.54 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.35 | $11.88 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.90 | $11.66 | 5/5 | 8/10 | 322 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-600` | `prob52` | 80.00% | $0.26 | $11.00 | 5/5 | 7/10 | 322 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.70 | $10.98 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-570` | `prob52` | 81.33% | $0.06 | $10.32 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.61 | $10.10 | 5/5 | 7/10 | 322 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.77 | $9.84 | 5/5 | 7/10 | 335 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.69 | $8.95 | 5/5 | 7/10 | 319 |

## Read

- Best v56 row is `v50_thinedge_ask90_edge1_stc450_cap75` / `edge0_ask100_p0.65_stc0-600` / `prob54` with min split fee+1c $0.99 and all-market fee+1c $12.54.
- Strict-forward validation is required before promotion.
