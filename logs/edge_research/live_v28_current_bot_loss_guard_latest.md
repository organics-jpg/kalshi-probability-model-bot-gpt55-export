# Live v28 Current Bot Loss Guard

Generated UTC: `20260505_122256Z`

## Scope

- Research-only audit of the current `live_mushroom_v28_size2` fill tape.
- No orders are submitted and no live bot files or processes are touched.
- Candidate guards are pre-entry only and must keep at least 80% of current v28 filled trades and filled markets.
- This does not solve the separate requirement to trade 80% of all recurring BTC 15m markets; it only improves the current live bot's own filled-entry stream.

## Baseline

- Matched filled trades: 252
- Current v28 filled markets: 169
- Observed resolved recurring markets in scorer: 406
- Current v28 recurring-market coverage: 41.63%
- Net P&L: $18.60
- Negative trades: 120
- Settled losses: 3

## Top Guards

| guard | strict | trades | trade ret | market ret | recurring cov | net | delta | neg trades | train/val/holdout net | val/hold ret |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ask_cents>=60 AND eligible_depth<=1300` | True | 215 | 85.32% | 89.35% | 37.19% | $22.18 | $3.58 | 103 (-17) | $14.04/$4.44/$3.70 | 80.95%/84.13% |
| `eligible_depth<=1300` | True | 224 | 88.89% | 90.53% | 37.68% | $21.90 | $3.30 | 109 (-11) | $15.28/$3.68/$2.94 | 85.71%/85.71% |
| `p_side>=0.85 AND eligible_depth<=1300` | True | 224 | 88.89% | 90.53% | 37.68% | $21.90 | $3.30 | 109 (-11) | $15.28/$3.68/$2.94 | 85.71%/85.71% |
| `ask_cents>=60 AND btc_age_ms<=600` | True | 228 | 90.48% | 93.49% | 38.92% | $21.80 | $3.20 | 107 (-13) | $13.00/$4.88/$3.92 | 90.48%/92.06% |
| `btc_age_ms<=600 AND eligible_depth<=2000` | True | 227 | 90.08% | 91.72% | 38.18% | $21.76 | $3.16 | 110 (-10) | $14.90/$4.10/$2.76 | 90.48%/90.48% |
| `abs_d_sigma<=1.35 AND eligible_depth<=1300` | True | 212 | 84.13% | 86.39% | 35.96% | $21.76 | $3.16 | 105 (-15) | $15.28/$3.86/$2.62 | 82.54%/80.95% |
| `abs_d_sigma<=1.35 AND btc_age_ms<=600` | True | 225 | 89.29% | 90.53% | 37.68% | $21.32 | $2.72 | 109 (-11) | $14.18/$4.30/$2.84 | 92.06%/88.89% |
| `btc_age_ms<=600` | True | 238 | 94.44% | 95.27% | 39.66% | $21.28 | $2.68 | 114 (-6) | $14.00/$4.12/$3.16 | 95.24%/93.65% |
| `p_side>=0.85 AND btc_age_ms<=600` | True | 238 | 94.44% | 95.27% | 39.66% | $21.28 | $2.68 | 114 (-6) | $14.00/$4.12/$3.16 | 95.24%/93.65% |
| `p_side<=0.945 AND btc_age_ms<=600` | True | 224 | 88.89% | 90.53% | 37.68% | $21.22 | $2.62 | 109 (-11) | $14.18/$4.06/$2.98 | 93.65%/85.71% |
| `sigma_t_dollars<=175 AND btc_age_ms<=600` | True | 228 | 90.48% | 91.72% | 38.18% | $21.16 | $2.56 | 108 (-12) | $14.00/$4.24/$2.92 | 90.48%/82.54% |
| `edge_cents>=2.1 AND btc_age_ms<=600` | True | 229 | 90.87% | 93.49% | 38.92% | $21.12 | $2.52 | 109 (-11) | $14.04/$3.76/$3.32 | 88.89%/92.06% |
| `abs_d_sigma>=0.8 AND eligible_depth<=1300` | True | 210 | 83.33% | 87.57% | 36.45% | $21.08 | $2.48 | 101 (-19) | $14.14/$3.80/$3.14 | 82.54%/84.13% |
| `abs_d_sigma<=1.2 AND btc_age_ms<=600` | True | 214 | 84.92% | 88.17% | 36.70% | $20.72 | $2.12 | 103 (-17) | $13.66/$4.36/$2.70 | 87.30%/80.95% |
| `ask_cents<=87 AND eligible_depth<=1300` | True | 212 | 84.13% | 86.39% | 35.96% | $20.50 | $1.90 | 106 (-14) | $14.72/$3.68/$2.10 | 85.71%/80.95% |
| `abs_d_sigma>=0.8 AND btc_age_ms<=600` | True | 224 | 88.89% | 92.31% | 38.42% | $20.46 | $1.86 | 106 (-14) | $12.86/$4.24/$3.36 | 92.06%/92.06% |
| `ask_cents<=87 AND btc_age_ms<=600` | True | 228 | 90.48% | 92.90% | 38.67% | $20.38 | $1.78 | 111 (-9) | $13.86/$3.98/$2.54 | 93.65%/90.48% |
| `ask_cents>=60 AND btc_age_ms<=350` | True | 216 | 85.71% | 89.94% | 37.44% | $20.34 | $1.74 | 103 (-17) | $12.00/$4.28/$4.06 | 82.54%/88.89% |
| `btc_age_ms<=350 AND eligible_depth<=2000` | True | 215 | 85.32% | 88.17% | 36.70% | $20.30 | $1.70 | 106 (-14) | $13.90/$3.50/$2.90 | 82.54%/87.30% |
| `p_side<=0.945 AND btc_age_ms<=350` | True | 213 | 84.52% | 86.98% | 36.21% | $20.16 | $1.56 | 105 (-15) | $13.18/$3.46/$3.52 | 85.71%/84.13% |

## Read

- Strict-pass guards: 46
- Best guard by this audit: `ask_cents>=60 AND eligible_depth<=1300` with $3.58 delta at 85.32% trade retention.
