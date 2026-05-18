# v39 Fee-Aware 75% Coverage Frontier

Generated UTC: `2026-05-05T00:25:13.592709+00:00`

## Scope

- Research-only replay. Live bot logic, process, and order path untouched.
- Minimum coverage relaxed to 75% in train, validation, and holdout.
- Entry grid adds stronger model-edge and p_side requirements than the 80% gross sweep.
- Fee-adjusted columns use the local Kalshi taker-fee formula also used by the dashboard.

## Search Result

- Policy rows evaluated after 75% coverage prefilter: 7620
- Rows positive across train/validation/holdout gross P&L: 1103
- Rows positive across train/validation/holdout fee-adjusted P&L: 19

## Selected Rows

| model | entry | exit | min cov | train net | val net | hold net | min net | all net | all gross | all ROI gross | trades | exits/settles |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `v38_long60_antipersist` | `edge-2_ask100_p0.65_stc0-600` | `prob50` | 95.45% | $1.95 | $1.95 | $1.16 | $1.16 | $5.06 | $16.36 | 3.22% | 322 | 91/231 |
| `v38_long60_antipersist` | `edge0_ask100_p0.65_stc0-600` | `prob50` | 92.42% | $1.04 | $1.62 | $2.12 | $1.04 | $4.78 | $16.04 | 3.26% | 314 | 91/223 |
| `v38_long60_antipersist` | `edge0_ask100_p0.65_stc0-600` | `prob55` | 92.42% | $1.44 | $1.87 | $0.93 | $0.93 | $4.24 | $15.94 | 3.24% | 314 | 100/214 |
| `v38_long60_antipersist` | `edge0_ask100_p0.65_stc120-600` | `prob50` | 89.39% | $0.66 | $1.62 | $1.25 | $0.66 | $3.53 | $14.66 | 3.08% | 305 | 91/214 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.62_stc0-600` | `prob50` | 95.45% | $0.88 | $1.14 | $0.65 | $0.65 | $2.67 | $14.84 | 2.99% | 323 | 104/219 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.62_stc120-600` | `prob50` | 90.91% | $0.58 | $1.14 | $0.64 | $0.58 | $2.36 | $14.46 | 3.02% | 313 | 103/210 |
| `v39_midband_v28_fallback` | `edge-2_ask100_p0.62_stc0-600` | `prob50` | 95.45% | $0.55 | $1.53 | $2.24 | $0.55 | $4.32 | $16.14 | 3.23% | 323 | 100/223 |
| `v39_midband_v28_fallback` | `edge0_ask100_p0.62_stc0-600` | `prob50` | 92.42% | $0.44 | $1.18 | $2.46 | $0.44 | $4.08 | $15.84 | 3.30% | 313 | 100/213 |
| `v38_long60_antipersist` | `edge0_ask100_p0.65_stc0-600` | `prob45` | 92.42% | $2.80 | $3.43 | $0.42 | $0.42 | $6.65 | $17.60 | 3.57% | 314 | 86/228 |
| `v38_long60_antipersist` | `edge1_ask100_p0.65_stc0-600` | `prob45` | 86.36% | $0.36 | $2.17 | $1.47 | $0.36 | $4.00 | $14.58 | 3.24% | 291 | 86/205 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.65_stc120-600` | `prob50` | 89.39% | $1.62 | $1.95 | $0.29 | $0.29 | $3.86 | $15.06 | 3.11% | 309 | 91/218 |
| `v39_midband_v28_fallback` | `edge-2_ask100_p0.62_stc120-600` | `prob50` | 90.91% | $0.23 | $1.53 | $2.23 | $0.23 | $3.99 | $15.72 | 3.30% | 310 | 99/211 |
| `v39_midband_v28_fallback` | `edge0_ask100_p0.62_stc120-600` | `prob50` | 90.91% | $0.10 | $1.18 | $2.45 | $0.10 | $3.73 | $15.38 | 3.31% | 304 | 99/205 |
| `v38_long60_antipersist` | `edge1_ask100_p0.62_stc0-600` | `prob45` | 88.38% | $0.84 | $1.56 | $0.07 | $0.07 | $2.47 | $13.76 | 3.09% | 296 | 96/200 |
| `v38_long60_antipersist` | `edge1_ask100_p0.62_stc120-600` | `prob45` | 86.87% | $0.55 | $1.56 | $0.07 | $0.07 | $2.18 | $13.42 | 3.04% | 293 | 95/198 |
| `v38_long60_antipersist` | `edge0_ask100_p0.65_stc120-600` | `prob55` | 89.39% | $1.06 | $1.87 | $0.06 | $0.06 | $2.99 | $14.56 | 3.06% | 305 | 100/205 |
| `v39_midband_v28_fallback` | `edge1_ask100_p0.62_stc0-600` | `prob45` | 85.86% | $2.97 | $0.61 | $0.05 | $0.05 | $3.63 | $14.50 | 3.37% | 286 | 92/194 |
| `v38_long60_antipersist` | `edge1_ask100_p0.65_stc120-600` | `prob45` | 84.85% | $0.04 | $2.17 | $0.61 | $0.04 | $2.82 | $13.32 | 3.01% | 287 | 86/201 |
| `v28_live_surface` | `edge0_ask100_p0.62_stc0-900` | `hold` | 87.88% | $8.65 | $0.03 | $1.18 | $0.03 | $9.86 | $19.58 | 4.79% | 296 | 0/296 |
| `v28_live_surface` | `edge-2_ask100_p0.62_stc0-900` | `hold` | 87.88% | $9.13 | $0.00 | $0.99 | $0.00 | $10.12 | $19.88 | 4.85% | 297 | 0/297 |
| `v39_midband_v28_fallback` | `edge0_ask100_p0.62_stc0-660` | `prob50` | 93.94% | $-1.06 | $1.41 | $1.60 | $-1.06 | $1.95 | $14.64 | 3.06% | 316 | 109/207 |
| `v39_midband_v28_fallback` | `edge0_ask100_p0.65_stc0-600` | `prob45` | 90.91% | $-2.51 | $2.44 | $1.82 | $-2.51 | $1.75 | $12.36 | 2.53% | 309 | 85/224 |
| `v39_midband_v28_fallback` | `edge0_ask100_p0.62_stc0-660` | `prob55` | 93.94% | $-0.68 | $1.13 | $0.85 | $-0.68 | $1.30 | $14.52 | 3.03% | 316 | 120/196 |
| `v28_live_surface` | `edge-2_ask100_p0.62_stc0-900` | `prob50` | 87.88% | $-4.73 | $0.84 | $0.51 | $-4.73 | $-3.38 | $11.30 | 2.76% | 297 | 135/162 |
| `v38_long60_antipersist` | `edge2_ask100_p0.65_stc0-600` | `prob45` | 76.77% | $-1.82 | $2.47 | $1.35 | $-1.82 | $2.00 | $12.28 | 3.09% | 264 | 86/178 |
| `v39_midband_v28_fallback` | `edge-2_ask100_p0.65_stc0-600` | `prob55` | 93.94% | $-3.14 | $2.36 | $1.62 | $-3.14 | $0.84 | $12.26 | 2.40% | 320 | 98/222 |
| `v39_midband_v28_fallback` | `edge0_ask100_p0.62_stc0-540` | `prob50` | 89.39% | $-2.99 | $5.86 | $2.41 | $-2.99 | $5.28 | $16.06 | 3.29% | 310 | 88/222 |
| `v38_long60_antipersist` | `edge0_ask100_p0.62_stc0-600` | `prob50` | 92.42% | $-0.35 | $1.25 | $1.32 | $-0.35 | $2.22 | $14.34 | 2.97% | 316 | 104/212 |
| `v38_long60_antipersist` | `edge0_ask100_p0.62_stc120-600` | `prob50` | 90.91% | $-0.66 | $1.25 | $1.31 | $-0.66 | $1.90 | $13.94 | 2.95% | 310 | 103/207 |
| `v39_midband_v28_fallback` | `edge0_ask100_p0.65_stc0-600` | `prob55` | 90.91% | $-3.18 | $1.59 | $2.39 | $-3.18 | $0.80 | $12.16 | 2.49% | 309 | 98/211 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.62_stc0-540` | `prob50` | 93.94% | $-3.36 | $5.65 | $1.21 | $-3.36 | $3.50 | $14.44 | 2.84% | 321 | 90/231 |
| `v38_long60_antipersist` | `edge0_ask100_p0.62_stc0-660` | `prob50` | 93.94% | $-2.60 | $1.13 | $0.71 | $-2.60 | $-0.76 | $12.14 | 2.53% | 317 | 112/205 |
| `v28_live_surface` | `edge3_ask100_p0.62_stc0-900` | `hold` | 77.27% | $6.64 | $-0.37 | $-0.47 | $-0.47 | $5.80 | $14.76 | 4.28% | 263 | 0/263 |
| `v28_live_surface` | `edge-2_ask85_p0.62_stc0-900` | `hold` | 80.30% | $8.86 | $-0.48 | $0.44 | $-0.48 | $8.82 | $18.22 | 5.18% | 267 | 0/267 |
| `v28_live_surface` | `edge0_ask85_p0.62_stc0-900` | `hold` | 79.80% | $8.31 | $-0.60 | $0.63 | $-0.60 | $8.34 | $17.68 | 5.08% | 265 | 0/265 |

## Read

- Best fee-adjusted robust row is `v38_long60_antipersist` / `edge-2_ask100_p0.65_stc0-600` / `prob50` with min fee-adjusted split P&L $1.16 and all fee-adjusted P&L $5.06.
