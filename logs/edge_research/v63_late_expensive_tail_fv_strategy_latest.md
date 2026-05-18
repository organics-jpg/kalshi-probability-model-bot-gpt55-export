# v63 Late Expensive-Tail FV Strategy

Generated UTC: `2026-05-05T11:31:24.291135+00:00`

## Scope

- Research-only FV probability transform on top of v55.
- Caps fragile high-ask tiny-edge selected-side probabilities.
- Live bot untouched.

## Search

- Candidate probability surfaces: 18
- Rows evaluated after 80% coverage prefilter: 985
- Robust rows: 13

## Holdout Probability

| candidate | Brier | logloss | side acc | mean p_yes |
|---|---:|---:|---:|---:|
| `v55_bookanchor_m10_v20_g05_book_plus2` | 0.14176 | 0.42589 | 79.31% | 49.65% |
| `v63_tail_a95_e250_s240_cap85` | 0.14220 | 0.42802 | 79.31% | 49.58% |
| `v63_tail_a95_e200_s240_cap85` | 0.14222 | 0.42821 | 79.31% | 49.60% |
| `v63_tail_a95_e250_s180_cap85` | 0.14243 | 0.42966 | 79.31% | 49.57% |
| `v63_tail_a95_e200_s180_cap85` | 0.14245 | 0.42983 | 79.31% | 49.59% |
| `v63_tail_a96_e150_s120_cap85` | 0.14248 | 0.43048 | 79.31% | 49.60% |
| `v63_tail_a95_e150_s120_cap85` | 0.14250 | 0.43062 | 79.31% | 49.60% |
| `v63_tail_a94_e150_s120_cap85` | 0.14251 | 0.43067 | 79.31% | 49.60% |
| `v63_tail_a96_e200_s120_cap85` | 0.14252 | 0.43032 | 79.31% | 49.60% |
| `v63_tail_a96_e250_s120_cap85` | 0.14254 | 0.43047 | 79.31% | 49.59% |
| `v63_tail_a95_e250_s120_cap85` | 0.14255 | 0.43045 | 79.31% | 49.59% |
| `v63_tail_a95_e200_s120_cap85` | 0.14256 | 0.43061 | 79.31% | 49.61% |
| `v63_tail_a94_e250_s120_cap85` | 0.14258 | 0.43061 | 79.31% | 49.60% |
| `v63_tail_a94_e200_s120_cap85` | 0.14259 | 0.43077 | 79.31% | 49.61% |
| `v63_tail_a96_e200_s120_cap80` | 0.14319 | 0.43267 | 79.31% | 49.59% |
| `v63_tail_a96_e250_s120_cap80` | 0.14323 | 0.43287 | 79.31% | 49.57% |
| `v63_tail_a95_e250_s120_cap80` | 0.14328 | 0.43297 | 79.31% | 49.58% |
| `v63_tail_a95_e200_s120_cap80` | 0.14328 | 0.43310 | 79.31% | 49.60% |

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

- Best v63 row is `v55_bookanchor_m10_v20_g05_book_plus2` / `edge0_ask100_p0.65_stc0-600` / `prob52` with min split fee+1c $0.93 and all-market fee+1c $13.36.
- Treat this as a probability-surface candidate requiring strict-forward validation before promotion.
