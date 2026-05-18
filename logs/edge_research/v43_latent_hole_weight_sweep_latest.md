# v43 Latent-Hole Posterior Weight Sweep

Generated UTC: `2026-05-05T05:53:18.654758+00:00`

## Scope

- Research-only sweep over book/FV posterior weights after latent edge-hole trigger.
- Uses the same v42 80% split-coverage, fee, 1c haircut, day, and block checks.
- Live bot untouched.

## Search Result

- Candidate probability surfaces: 7
- Rows after 80% coverage prefilter: 1610
- Fee+1c positive split rows: 49
- Fee+1c positive all-day rows: 8

## Holdout Probability

| candidate | Brier | logloss | side acc | mean p_yes |
|---|---:|---:|---:|---:|
| `v43_latent_hole_bookblend100` | 0.14222 | 0.42772 | 79.01% | 49.69% |
| `v43_latent_hole_bookblend90` | 0.14228 | 0.42787 | 78.99% | 49.69% |
| `v43_latent_hole_bookblend80` | 0.14234 | 0.42804 | 78.99% | 49.69% |
| `v43_latent_hole_bookblend65` | 0.14245 | 0.42834 | 78.99% | 49.70% |
| `v43_latent_hole_bookblend50` | 0.14258 | 0.42869 | 78.99% | 49.70% |
| `v43_latent_hole_bookblend35` | 0.14273 | 0.42910 | 78.96% | 49.71% |
| `v38_raw` | 0.14318 | 0.43031 | 78.80% | 49.73% |

## Best Row Per Surface

| model | entry | exit | min cov | min 1c | all 1c | days | block10 | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `v43_latent_hole_bookblend80` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.45 | $8.53 | 5/5 | 8/10 | 340 |
| `v43_latent_hole_bookblend90` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.45 | $9.85 | 5/5 | 7/10 | 339 |
| `v38_raw` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 82.67% | $0.66 | $5.53 | 4/5 | 6/10 | 343 |
| `v43_latent_hole_bookblend100` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 82.67% | $0.59 | $9.12 | 4/5 | 7/10 | 330 |
| `v43_latent_hole_bookblend65` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.15 | $5.84 | 4/5 | 7/10 | 340 |
| `v43_latent_hole_bookblend50` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.15 | $4.93 | 4/5 | 7/10 | 341 |
| `v43_latent_hole_bookblend35` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.15 | $3.88 | 3/5 | 7/10 | 341 |

## Read

- Best all-day row is `v43_latent_hole_bookblend80` / `edge0_ask100_p0.65_stc0-600` / `prob54` with min split fee+1c $0.45.
