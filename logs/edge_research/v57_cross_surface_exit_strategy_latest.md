# v57 Cross-Surface Exit Strategy

Generated UTC: `2026-05-05T08:21:18.636913+00:00`

## Scope

- Research-only entry/exit decoupling test.
- Entry surfaces are high-PnL v50/v53/v55; exit surfaces include calibrated v56 variants.
- Live bot untouched.

## Search

- Rows evaluated: 252
- Robust rows: 102

## Selected Rows

| entry model | exit model | entry | exit | min cov | min 1c | all 1c | days | block10 | trades |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob52` | 81.33% | $0.93 | $13.60 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v56_bedge1_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob52` | 81.33% | $0.09 | $13.58 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v56_bedge0_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob52` | 81.33% | $0.09 | $13.58 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.93 | $13.36 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob54` | 81.33% | $0.99 | $13.35 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob54` | 81.33% | $0.99 | $13.35 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v56_bedge1_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.09 | $13.34 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v56_bedge0_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.09 | $13.34 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v56_bedge1_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob54` | 81.33% | $0.53 | $13.18 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v56_bedge0_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob54` | 81.33% | $0.53 | $13.18 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob54` | 81.33% | $0.35 | $13.12 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.99 | $13.11 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.99 | $13.11 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v56_bedge1_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.53 | $12.94 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v56_bedge0_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.53 | $12.94 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `v56_bedge1_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob52` | 81.33% | $0.09 | $12.91 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `v56_bedge0_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob52` | 81.33% | $0.09 | $12.91 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.35 | $12.88 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob54` | 81.33% | $0.99 | $12.78 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob54` | 81.33% | $0.99 | $12.78 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc60-600` | `hold15_prob52` | 80.00% | $0.84 | $12.72 | 5/5 | 8/10 | 322 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob52` | 81.33% | $0.35 | $12.69 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob52` | 81.33% | $0.35 | $12.69 | 5/5 | 8/10 | 333 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `v56_bedge1_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob52` | 81.33% | $0.19 | $12.68 | 5/5 | 8/10 | 332 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `v56_bedge0_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob52` | 81.33% | $0.19 | $12.68 | 5/5 | 8/10 | 332 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `v56_bedge1_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.09 | $12.67 | 5/5 | 8/10 | 333 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `v56_bedge0_m11_v15_g05_book_else_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.09 | $12.67 | 5/5 | 8/10 | 333 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob54` | 81.33% | $1.09 | $12.55 | 5/5 | 8/10 | 332 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `hold15_prob54` | 81.33% | $1.09 | $12.55 | 5/5 | 8/10 | 332 |
| `v50_thinedge_ask90_edge1_stc450_cap75` | `v50_thinedge_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.99 | $12.54 | 5/5 | 8/10 | 333 |

## Read

- Best row uses `v55_bookanchor_m10_v20_g05_book_plus2` for entry and `v55_bookanchor_m10_v20_g05_book_plus2` for exit with `hold15_prob52`: all-market fee+1c $13.60, min split fee+1c $0.93.
- Strict-forward validation is required before promotion.
