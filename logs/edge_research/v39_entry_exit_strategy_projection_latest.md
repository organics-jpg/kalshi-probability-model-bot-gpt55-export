# v39 Entry/Exit Strategy Projection

Generated UTC: `2026-05-05T03:18:28.480205+00:00`

## Scope

- Research-only entry/exit replay using observed heartbeat bid/ask paths.
- One entry per market; no live bot code/process/order path is touched.
- Entry candidates must keep at least 80% coverage in train, validation, and holdout before exit policies are ranked.
- Gross P&L assumes fills at observed ask for entry and observed bid for exit, quantity 2.
- Fee-adjusted columns use the local Kalshi taker-fee formula also used by the dashboard.

## Live Reference

- Entries: 238
- Completed round trips: 177
- Open positions: 0
- Net P&L: $20.30 on $432.21 (4.70%)

## Search Result

- Policy rows evaluated after coverage prefilter: 5280
- 80%+ rows with positive train/validation/holdout gross P&L: 233
- 80%+ rows with positive train/validation/holdout fee-adjusted P&L: 0

## Selected Rows

| model | entry | exit | min cov | train gross | val gross | hold gross | all gross | all fee net | min fee net | all ROI | exits/settles | avg entry stc |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `v39_midband_v28_fallback` | `edge1_ask100_p0.60_stc0-780` | `prob50` | 90.91% | $5.92 | $3.16 | $2.52 | $11.60 | $-2.91 | $-2.74 | 2.73% | 136/167 | 601.2s |
| `v38_long60_antipersist` | `edge2_ask100_p0.60_stc0-780` | `prob50` | 86.87% | $5.42 | $2.56 | $2.46 | $10.44 | $-3.95 | $-3.06 | 2.60% | 137/155 | 600.5s |
| `v39_midband_v28_fallback` | `edge2_ask100_p0.60_stc0-780` | `prob50` | 84.85% | $3.62 | $2.68 | $2.46 | $8.76 | $-5.42 | $-4.76 | 2.23% | 136/150 | 600.4s |
| `v28_live_surface` | `edge3_ask100_p0.60_stc0-900` | `prob50` | 81.31% | $2.36 | $2.98 | $2.92 | $8.26 | $-6.74 | $-6.46 | 2.36% | 150/123 | 671.7s |
| `v39_midband_v28_fallback` | `edge0_ask100_p0.60_stc0-600` | `prob50` | 92.42% | $2.58 | $4.30 | $2.24 | $9.12 | $-3.35 | $-4.96 | 1.92% | 112/202 | 475.3s |
| `v39_midband_v28_fallback` | `edge0_ask100_p0.60_stc120-600` | `prob50` | 90.91% | $2.34 | $4.30 | $2.22 | $8.86 | $-3.52 | $-5.12 | 1.90% | 111/197 | 482.8s |
| `v28_live_surface` | `edge2_ask100_p0.60_stc0-780` | `prob50` | 81.31% | $5.12 | $2.92 | $2.18 | $10.22 | $-3.56 | $-2.96 | 2.73% | 132/142 | 603.9s |
| `v38_long60_antipersist` | `edge1_ask100_p0.60_stc0-660` | `prob50` | 90.91% | $3.46 | $3.98 | $2.14 | $9.58 | $-3.80 | $-4.53 | 2.14% | 122/184 | 535.2s |
| `v39_midband_v28_fallback` | `edge-2_ask100_p0.60_stc0-600` | `prob50` | 95.45% | $2.08 | $4.70 | $2.40 | $9.18 | $-3.36 | $-5.48 | 1.86% | 112/211 | 472.4s |
| `v28_live_surface` | `edge1_ask100_p0.60_stc0-900` | `prob50` | 87.37% | $3.98 | $2.24 | $2.04 | $8.26 | $-7.45 | $-5.33 | 2.13% | 153/139 | 683.0s |
| `v39_midband_v28_fallback` | `edge2_ask100_p0.55_stc120-600` | `take10_or_fair0` | 80.30% | $4.42 | $3.56 | $1.96 | $9.94 | $-6.05 | $-5.21 | 2.57% | 273/1 | 496.7s |
| `v39_midband_v28_fallback` | `edge2_ask100_p0.55_stc0-600` | `take10_or_fair0` | 80.30% | $4.28 | $3.56 | $1.96 | $9.80 | $-6.24 | $-5.40 | 2.54% | 274/1 | 495.2s |
| `v39_midband_v28_fallback` | `edge2_ask100_p0.55_stc120-600` | `fair_bid_ge_fair` | 80.30% | $3.80 | $3.84 | $1.94 | $9.58 | $-6.34 | $-5.77 | 2.48% | 273/1 | 496.7s |
| `v39_midband_v28_fallback` | `edge2_ask100_p0.55_stc0-600` | `fair_bid_ge_fair` | 80.30% | $3.66 | $3.84 | $1.94 | $9.44 | $-6.53 | $-5.96 | 2.44% | 274/1 | 495.2s |
| `v38_long60_antipersist` | `edge2_ask100_p0.60_stc0-660` | `prob45` | 84.85% | $3.30 | $4.08 | $1.94 | $9.32 | $-3.21 | $-4.11 | 2.26% | 113/174 | 529.6s |
| `v38_long60_antipersist` | `edge-2_ask100_p0.60_stc0-900` | `hold` | 96.97% | $16.54 | $2.40 | $-0.44 | $18.50 | $7.88 | $-2.55 | 4.17% | 0/325 | 657.1s |
| `v38_long60_antipersist` | `edge0_ask100_p0.60_stc0-900` | `hold` | 93.94% | $15.44 | $2.50 | $0.24 | $18.18 | $7.60 | $-1.89 | 4.17% | 0/321 | 659.2s |
| `v39_midband_v28_fallback` | `edge-2_ask100_p0.60_stc0-900` | `hold` | 96.97% | $15.82 | $2.42 | $-0.06 | $18.18 | $7.57 | $-2.19 | 4.10% | 0/325 | 652.8s |
| `v39_midband_v28_fallback` | `edge0_ask100_p0.60_stc0-900` | `hold` | 93.94% | $15.12 | $2.60 | $0.20 | $17.92 | $7.37 | $-1.93 | 4.11% | 0/321 | 655.1s |
| `v38_long60_antipersist` | `edge-2_ask80_p0.60_stc0-900` | `hold` | 83.33% | $13.78 | $1.36 | $0.48 | $15.62 | $5.48 | $-1.61 | 4.51% | 0/275 | 690.9s |
| `v39_midband_v28_fallback` | `edge-2_ask80_p0.60_stc0-900` | `hold` | 82.32% | $13.00 | $1.38 | $0.48 | $14.86 | $4.77 | $-1.61 | 4.33% | 0/273 | 690.6s |
| `v38_long60_antipersist` | `edge1_ask100_p0.60_stc0-900` | `hold` | 92.42% | $15.12 | $1.58 | $-1.84 | $14.86 | $4.50 | $-3.92 | 3.60% | 0/309 | 663.9s |
| `v38_long60_antipersist` | `edge0_ask80_p0.60_stc0-900` | `hold` | 81.82% | $12.90 | $0.98 | $0.74 | $14.62 | $4.57 | $-1.35 | 4.26% | 0/273 | 687.5s |
| `v28_live_surface` | `edge-2_ask70_p0.50_stc0-900` | `prob45` | 93.94% | $12.70 | $1.44 | $0.46 | $14.60 | $-5.96 | $-3.69 | 4.54% | 224/91 | 836.9s |
| `v39_midband_v28_fallback` | `edge0_ask80_p0.60_stc0-900` | `hold` | 80.30% | $12.92 | $0.84 | $0.74 | $14.50 | $4.50 | $-1.35 | 4.27% | 0/271 | 686.7s |
| `v38_long60_antipersist` | `edge-2_ask100_p0.60_stc0-780` | `prob45` | 96.97% | $10.16 | $5.18 | $-0.94 | $14.40 | $0.01 | $-3.99 | 3.10% | 128/197 | 600.3s |
| `v39_midband_v28_fallback` | `edge-2_ask100_p0.60_stc0-780` | `prob45` | 96.97% | $8.26 | $4.68 | $1.38 | $14.32 | $0.05 | $-1.61 | 3.07% | 126/199 | 594.6s |
| `v38_long60_antipersist` | `edge0_ask100_p0.60_stc0-780` | `prob45` | 93.94% | $9.04 | $5.28 | $-0.32 | $14.00 | $-0.35 | $-3.38 | 3.06% | 128/193 | 601.8s |
| `v28_live_surface` | `edge-2_ask80_p0.50_stc0-900` | `prob45` | 95.45% | $12.90 | $1.36 | $-0.30 | $13.96 | $-6.63 | $-4.41 | 4.23% | 224/95 | 840.4s |
| `v28_live_surface` | `edge-2_ask100_p0.50_stc0-900` | `prob45` | 96.97% | $13.44 | $1.36 | $-0.98 | $13.82 | $-6.82 | $-5.09 | 4.06% | 224/100 | 839.8s |

## Read

- Best robust row is `v39_midband_v28_fallback` / `edge1_ask100_p0.60_stc0-780` / `prob50` with min split P&L $2.52 and all P&L $11.60.
- After the repo's local Kalshi taker-fee estimate, no 80%+ row remains positive across train, validation, and holdout.
- This is a projection from observed quotes, not a live patch; forward shadowing is still required before promotion.
