# v53 Weak Re-cross + Thin-Edge Combo FV Strategy

Generated UTC: `2026-05-05T07:35:10.686747+00:00`

## Scope

- Research-only FV probability transform.
- Combines v52 weak re-cross caution with v50 expensive tiny-edge certainty cap.
- Live bot untouched.

## Search

- Candidate probability surfaces: 12
- Rows evaluated after 80% coverage prefilter: 2315
- Robust rows: 64

## Holdout Probability

| candidate | Brier | logloss | side acc |
|---|---:|---:|---:|
| `v53_v52_weakrecross_sigma1_v3p15_cap75_thin_ask90_edge1_stc450_cap75` | 0.14216 | 0.42733 | 78.99% |
| `v53_v52_weakrecross_sigma1_v3p15_cap75_thin_ask92_edge1_stc450_cap75` | 0.14216 | 0.42733 | 78.99% |
| `v53_v52_weakrecross_sigma1_v3p15_cap72_thin_ask90_edge1_stc450_cap75` | 0.14218 | 0.42737 | 78.99% |
| `v53_v52_weakrecross_sigma1_v3p15_cap72_thin_ask92_edge1_stc450_cap75` | 0.14218 | 0.42737 | 78.99% |
| `v53_v52_weakrecross_sigma1_v3p15_cap75_thin_ask90_edge1_stc450_cap72` | 0.14221 | 0.42745 | 78.99% |
| `v53_v52_weakrecross_sigma1_v3p15_cap72_thin_ask90_edge1_stc450_cap72` | 0.14222 | 0.42748 | 78.99% |
| `v53_v52_weakrecross_sigma1_v3p15_cap75_thin_ask90_edge2_stc450_cap75` | 0.14242 | 0.42841 | 78.99% |
| `v53_v52_weakrecross_sigma1_v3p15_cap72_thin_ask90_edge2_stc450_cap75` | 0.14243 | 0.42844 | 78.99% |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | 0.14271 | 0.42884 | 78.99% |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask92_edge1_stc450_cap75` | 0.14271 | 0.42884 | 78.99% |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap72` | 0.14275 | 0.42896 | 78.99% |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge2_stc450_cap75` | 0.14298 | 0.42998 | 78.99% |

## Selected Strategy Rows

| model | entry | exit | min cov | min 1c | all 1c | days | block10 | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $1.09 | $12.31 | 5/5 | 8/10 | 332 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap72` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $1.09 | $12.31 | 5/5 | 8/10 | 332 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $1.09 | $12.20 | 5/5 | 8/10 | 332 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge2_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $1.03 | $12.35 | 5/5 | 8/10 | 331 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $1.00 | $11.60 | 5/5 | 8/10 | 321 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap72` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $1.00 | $11.60 | 5/5 | 8/10 | 321 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $1.00 | $11.49 | 5/5 | 8/10 | 321 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.87 | $9.80 | 5/5 | 7/10 | 334 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap72` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.87 | $9.80 | 5/5 | 7/10 | 334 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.87 | $9.69 | 5/5 | 7/10 | 334 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.82 | $11.86 | 5/5 | 8/10 | 332 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap72` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.82 | $11.86 | 5/5 | 8/10 | 332 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.82 | $11.83 | 5/5 | 8/10 | 332 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge2_stc450_cap75` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 81.33% | $0.81 | $9.84 | 5/5 | 7/10 | 333 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.73 | $11.15 | 5/5 | 7/10 | 321 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap72` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.73 | $11.15 | 5/5 | 7/10 | 321 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.73 | $11.12 | 5/5 | 7/10 | 321 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge2_stc450_cap75` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 80.00% | $0.72 | $9.54 | 5/5 | 7/10 | 323 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge2_stc450_cap75` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 80.00% | $0.70 | $8.89 | 5/5 | 8/10 | 331 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 82.67% | $0.68 | $8.98 | 5/5 | 7/10 | 334 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap72` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 82.67% | $0.68 | $8.98 | 5/5 | 7/10 | 334 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 82.67% | $0.68 | $8.95 | 5/5 | 7/10 | 334 |
| `v53_v52_weakrecross_sigma1_v3p15_cap72_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $0.57 | $11.41 | 5/5 | 8/10 | 330 |
| `v53_v52_weakrecross_sigma1_v3p15_cap72_thin_ask90_edge1_stc450_cap72` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $0.57 | $11.41 | 5/5 | 8/10 | 330 |
| `v53_v52_weakrecross_sigma1_v3p15_cap72_thin_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $0.57 | $11.25 | 5/5 | 8/10 | 330 |
| `v53_v52_weakrecross_sigma1_v3p15_cap75_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $0.51 | $10.82 | 5/5 | 8/10 | 330 |
| `v53_v52_weakrecross_sigma1_v3p15_cap75_thin_ask90_edge1_stc450_cap72` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $0.51 | $10.82 | 5/5 | 8/10 | 330 |
| `v53_v52_weakrecross_sigma1_v3p15_cap75_thin_ask92_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $0.51 | $10.66 | 5/5 | 8/10 | 330 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.45 | $11.65 | 5/5 | 8/10 | 332 |
| `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap72` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.45 | $11.65 | 5/5 | 8/10 | 332 |

## Read

- Best v53 row is `v53_v52_weakrecross_sigma08_v3p15_cap68_thin_ask90_edge1_stc450_cap75` / `edge0_ask100_p0.65_stc0-600` / `prob54` with min split fee+1c $1.09 and all-market fee+1c $12.31.
- This improves worst-split PnL versus v50 but gives back some all-market PnL.
- Strict-forward validation is required before promotion.
