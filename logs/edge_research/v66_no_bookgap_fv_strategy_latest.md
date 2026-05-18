# v66 NO-Side Book-Gap FV Strategy

Generated UTC: `2026-05-05T11:52:27.714003+00:00`

## Scope

- Research-only FV transform on top of v55.
- Shrinks large selected NO-side model/book gaps toward the book.
- Live bot untouched.

## Entry Diagnostic

| slice | trades | fee+1c | avg c | wins | losses | exits | avg ask | avg edge | avg p | avg gap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `all_v57_style` | 333 | $13.60 | 4.1 | 277 | 56 | 78 | 80.9 | 3.13 | 0.840 | 0.036 |
| `YES_gap_ge_05` | 26 | $3.94 | 15.2 | 18 | 8 | 11 | 64.8 | 12.83 | 0.776 | 0.134 |
| `NO_gap_ge_05` | 28 | $-1.94 | -6.9 | 18 | 10 | 14 | 69.1 | 10.59 | 0.797 | 0.112 |
| `NO_gap_ge_08` | 10 | $-1.58 | -15.8 | 6 | 4 | 8 | 55.1 | 19.74 | 0.748 | 0.205 |
| `NO_gap_ge_05_ask_lt_90` | 25 | $-2.34 | -9.4 | 15 | 10 | 14 | 66.5 | 11.23 | 0.777 | 0.119 |
| `NO_gap_ge_05_ask_ge_90` | 3 | $0.40 | 13.3 | 3 | 0 | 0 | 91.3 | 5.32 | 0.967 | 0.057 |

## Holdout Probability

| candidate | Brier | logloss | side acc |
|---|---:|---:|---:|
| `v66_no_bookgap_g05_bookplus00` | 0.13583 | 0.40894 | 80.10% |
| `v66_no_bookgap_g05_bookplus04` | 0.13677 | 0.41198 | 79.96% |
| `v66_no_bookgap_g08_bookplus04` | 0.13692 | 0.41292 | 79.94% |
| `v66_no_bookgap_g08_blend75` | 0.13705 | 0.41336 | 79.89% |
| `v66_no_bookgap_g05_blend50` | 0.13806 | 0.41549 | 79.94% |
| `v66_no_bookgap_g08_blend50` | 0.13827 | 0.41673 | 79.89% |
| `v55_bookanchor_m10_v20_g05_book_plus2` | 0.14176 | 0.42589 | 79.31% |

## Selected Strategy Rows

| model | entry | exit | min cov | min 1c | all 1c | days | block10 | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `v66_no_bookgap_g05_bookplus00` | `edge0_ask100_p0.66_stc0-570` | `prob56` | 84.00% | $1.57 | $8.93 | 5/5 | 7/10 | 338 |
| `v66_no_bookgap_g08_blend75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $1.51 | $11.45 | 5/5 | 8/10 | 333 |
| `v66_no_bookgap_g08_blend50` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $1.45 | $11.18 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.93 | $13.36 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc60-600` | `prob52` | 80.00% | $0.84 | $12.48 | 5/5 | 8/10 | 322 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-570` | `prob52` | 81.33% | $0.64 | $11.58 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc0-570` | `prob52` | 81.33% | $0.64 | $9.29 | 5/5 | 8/10 | 334 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc60-570` | `prob52` | 80.00% | $0.55 | $10.70 | 5/5 | 7/10 | 322 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc60-570` | `prob52` | 80.00% | $0.55 | $8.82 | 5/5 | 7/10 | 324 |
| `v66_no_bookgap_g05_bookplus00` | `edge0_ask100_p0.66_stc0-600` | `prob54` | 85.33% | $0.45 | $10.06 | 5/5 | 7/10 | 339 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.35 | $12.88 | 5/5 | 8/10 | 333 |
| `v66_no_bookgap_g08_bookplus04` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.35 | $10.45 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc0-600` | `prob52` | 82.67% | $0.31 | $10.05 | 5/5 | 7/10 | 335 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.26 | $12.00 | 5/5 | 7/10 | 322 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc120-600` | `prob52` | 80.00% | $0.23 | $9.16 | 5/5 | 7/10 | 319 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.06 | $11.10 | 5/5 | 8/10 | 333 |
| `v66_no_bookgap_g08_bookplus04` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.06 | $8.79 | 5/5 | 8/10 | 333 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 81.33% | $0.06 | $8.63 | 5/5 | 8/10 | 334 |
| `v55_bookanchor_m10_v20_g05_book_plus2` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.05 | $8.96 | 5/5 | 7/10 | 319 |

## Read

- Best all-market v66 row is `v55_bookanchor_m10_v20_g05_book_plus2` with all fee+1c $13.36 and min split $0.93.
- Best min-split v66 row is `v66_no_bookgap_g05_bookplus00` with min split fee+1c $1.57 and all fee+1c $8.93.
- Current read: useful robustness lens, not a PnL upgrade over v57/v60.
- Strict-forward validation would be required before any promotion.
