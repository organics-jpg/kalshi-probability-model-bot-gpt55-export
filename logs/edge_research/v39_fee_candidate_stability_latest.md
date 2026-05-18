# v39 Fee Candidate Stability

Generated UTC: `2026-05-05T00:27:19.604040+00:00`

## Scope

- Focused audit of top fee-aware 75% coverage candidates.
- Uses observed ask/bid replay, quantity 2, local taker-fee estimate.
- Reports chronological block stability over candidate trades.

## Candidates

| candidate | model | entry | exit | min fee net | all fee net | 1c entry min | all gross | coverage | block10 + | worst block10 | block20 + | worst block20 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `best_min_fee_v38_p65_prob50` | `v38_long60_antipersist` | `edge-2_ask100_p0.65_stc0-600` | `prob50` | $1.16 | $5.06 | $-1.91 | $16.36 | 97.58% | 5/10 | $-4.98 | 11/20 | $-4.37 |
| `v38_p65_edge0_prob50` | `v38_long60_antipersist` | `edge0_ask100_p0.65_stc0-600` | `prob50` | $1.04 | $4.78 | $-2.72 | $16.04 | 95.15% | 6/10 | $-5.49 | 11/20 | $-4.37 |
| `v38_p65_edge0_prob45` | `v38_long60_antipersist` | `edge0_ask100_p0.65_stc0-600` | `prob45` | $0.42 | $6.65 | $-0.96 | $17.60 | 95.15% | 6/10 | $-4.90 | 11/20 | $-3.34 |
| `best_v39_fee_v39_p62_prob50` | `v39_midband_v28_fallback` | `edge-2_ask100_p0.62_stc0-600` | `prob50` | $0.55 | $4.32 | $-3.33 | $16.14 | 97.88% | 5/10 | $-3.15 | 10/20 | $-4.39 |
| `best_allnet_v28_p62_hold` | `v28_live_surface` | `edge0_ask100_p0.62_stc0-900` | `hold` | $0.03 | $9.86 | $-1.23 | $19.58 | 89.70% | 6/10 | $-4.99 | 11/20 | $-5.96 |

## Read

- Best split-balanced fee candidate is `best_min_fee_v38_p65_prob50` with min split fee net $1.16 and all fee net $5.06.
- Its 1c-entry-haircut min split value is $-1.91, so the edge is fee-positive but execution-fragile.
- Treat this as a forward-shadow candidate, not a live-bot patch.
