# v38 Fee Refined Exit Frontier

Generated UTC: `2026-05-05T00:40:24.095095+00:00`

## Scope

- Fine-grained refinement around v38/v39 fee-aware 75% candidates.
- Sweeps p_side, seconds-to-close windows, edge floors, and probability-exit thresholds.
- Requires at least 75% coverage in train, validation, and holdout.

## Search Result

- Policy rows evaluated after coverage prefilter: 360
- Fee-positive train/validation/holdout rows: 44
- Fee-positive plus 1c-entry-haircut rows: 0

## Selected Rows

| model | entry | exit | min cov | min fee net | all fee net | min 1c entry | all 1c entry | all gross | block10 + | worst block10 | block20 + | worst block20 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `v38_long60_antipersist` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 92.42% | $1.70 | $7.23 | $-2.06 | $0.95 | $18.64 | 6/10 | $-4.06 | 11/20 | $-3.51 |
| `v38_long60_antipersist` | `edge0_ask100_p0.64_stc0-600` | `prob52` | 92.42% | $1.60 | $6.03 | $-1.94 | $-0.25 | $17.62 | 6/10 | $-4.06 | 12/20 | $-4.02 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.65_stc0-600` | `prob52` | 95.45% | $1.57 | $7.51 | $-1.25 | $1.07 | $18.96 | 5/10 | $-3.75 | 13/20 | $-3.33 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.65_stc0-570` | `prob52` | 95.45% | $1.45 | $6.44 | $-2.09 | $0.00 | $17.80 | 5/10 | $-4.02 | 11/20 | $-3.17 |
| `v38_long60_antipersist` | `edge0_ask100_p0.65_stc120-600` | `prob52` | 89.39% | $1.32 | $5.98 | $-2.30 | $-0.12 | $17.26 | 6/10 | $-3.68 | 10/20 | $-2.73 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.65_stc0-600` | `prob50` | 95.45% | $1.16 | $5.06 | $-1.91 | $-1.38 | $16.36 | 5/10 | $-4.98 | 11/20 | $-4.37 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.65_stc0-600` | `prob51` | 95.45% | $1.13 | $4.69 | $-2.73 | $-1.75 | $16.10 | 5/10 | $-4.19 | 12/20 | $-4.37 |
| `v38_long60_antipersist` | `edge0_ask100_p0.64_stc0-570` | `prob52` | 92.42% | $1.11 | $4.67 | $-2.65 | $-1.61 | $16.14 | 6/10 | $-3.83 | 11/20 | $-3.65 |
| `v38_long60_antipersist` | `edge0_ask100_p0.65_stc0-600` | `prob50` | 92.42% | $1.04 | $4.78 | $-2.72 | $-1.50 | $16.04 | 6/10 | $-5.49 | 11/20 | $-4.37 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.65_stc0-570` | `prob50` | 95.45% | $1.04 | $3.99 | $-2.75 | $-2.45 | $15.20 | 5/10 | $-5.23 | 9/20 | $-4.20 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.65_stc0-600` | `prob49` | 95.45% | $0.83 | $4.23 | $-2.41 | $-2.21 | $15.52 | 5/10 | $-4.98 | 11/20 | $-4.37 |
| `v38_long60_antipersist` | `edge0_ask100_p0.64_stc120-600` | `prob52` | 89.39% | $0.73 | $4.78 | $-2.18 | $-1.32 | $16.24 | 5/10 | $-3.68 | 9/20 | $-3.23 |
| `v38_long60_antipersist` | `edge0_ask100_p0.65_stc0-570` | `prob52` | 92.42% | $0.71 | $5.90 | $-3.05 | $-0.38 | $17.22 | 6/10 | $-3.83 | 11/20 | $-3.65 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.65_stc120-600` | `prob52` | 89.39% | $0.70 | $6.31 | $-1.40 | $0.13 | $17.66 | 6/10 | $-4.62 | 10/20 | $-3.18 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.65_stc120-600` | `prob51` | 89.39% | $0.68 | $3.49 | $-2.88 | $-2.69 | $14.80 | 5/10 | $-4.64 | 10/20 | $-3.74 |
| `v38_long60_antipersist` | `edge0_ask100_p0.65_stc120-600` | `prob50` | 89.39% | $0.66 | $3.53 | $-2.96 | $-2.57 | $14.66 | 4/10 | $-4.14 | 10/20 | $-3.74 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.65_stc0-570` | `prob49` | 95.45% | $0.61 | $3.16 | $-3.25 | $-3.28 | $14.36 | 5/10 | $-5.23 | 9/20 | $-4.20 |
| `v38_long60_antipersist` | `edge-2_ask100_p0.65_stc120-570` | `prob52` | 89.39% | $0.58 | $5.24 | $-2.24 | $-0.94 | $16.50 | 5/10 | $-4.89 | 9/20 | $-3.18 |
| `v38_long60_antipersist` | `edge0_ask100_p0.65_stc0-600` | `prob44` | 92.42% | $0.55 | $3.64 | $-3.16 | $-2.64 | $14.42 | 6/10 | $-5.66 | 10/20 | $-3.77 |
| `v38_long60_antipersist` | `edge0_ask100_p0.65_stc0-600` | `prob49` | 92.42% | $0.54 | $3.95 | $-3.22 | $-2.33 | $15.20 | 6/10 | $-5.49 | 10/20 | $-4.37 |

## Read

- No refined row remains positive in all splits after a 1c adverse entry-fill haircut. Closest row is `v38_long60_antipersist` / `edge0_ask100_p0.65_stc0-600` / `prob45` with min 1c-entry split $-0.96.
