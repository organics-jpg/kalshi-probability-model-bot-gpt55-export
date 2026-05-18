# v42 Edge-Hole Latent FV Strategy

Generated UTC: `2026-05-05T05:53:21.652579+00:00`

## Scope

- Research-only probability transformation probe on top of v38.
- Tests edge-hole as a latent fair-value state, not only an explicit entry veto.
- Strategy projection requires at least 80% coverage in every chronological split.
- Live bot untouched.

## Data Notes

- Latent first-hole markets under all-day rule: 45
- Opportunity rows in local 8-20 edge band: 544

## Probability Holdout

| candidate | rows | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---:|---:|---:|---:|---:|---:|
| `v42_latent_hole_book` | 4307 | 0.14222 | 0.42772 | 79.01% | 49.69% | 54.03% |
| `v42_latent_hole_bookblend80` | 4307 | 0.14234 | 0.42804 | 78.99% | 49.69% | 54.03% |
| `v42_band_cap_edge-2` | 4307 | 0.14252 | 0.42831 | 78.85% | 49.77% | 54.03% |
| `v42_band_cap_edge0` | 4307 | 0.14256 | 0.42840 | 78.85% | 49.76% | 54.03% |
| `v42_band_bookblend80` | 4307 | 0.14263 | 0.42859 | 78.80% | 49.76% | 54.03% |
| `v42_band_bookblend50` | 4307 | 0.14281 | 0.42910 | 78.80% | 49.75% | 54.03% |
| `v38_raw` | 4307 | 0.14318 | 0.43031 | 78.80% | 49.73% | 54.03% |
| `v42_latent_hole_flat` | 4307 | 0.14932 | 0.44606 | 76.48% | 50.34% | 54.03% |

## Strategy Search

- Candidate probability surfaces: 8
- Rows evaluated after 80% coverage prefilter: 1710
- Fee+1c positive train/validation/holdout rows: 41
- Fee+1c positive across all UTC days rows: 6

## Selected Strategy Rows

| model | entry | exit | min cov | min 1c | all 1c | all fee | gross | days | block10 | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `v42_latent_hole_bookblend80` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.45 | $8.53 | $15.33 | $27.14 | 5/5 | 8/10 | 340 |
| `v42_latent_hole_book` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 84.00% | $0.39 | $7.64 | $14.38 | $25.70 | 5/5 | 6/10 | 337 |
| `v42_latent_hole_bookblend80` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.36 | $7.47 | $14.05 | $25.70 | 5/5 | 7/10 | 329 |
| `v42_latent_hole_book` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 82.67% | $0.30 | $7.18 | $13.74 | $24.96 | 5/5 | 5/10 | 328 |
| `v42_latent_hole_book` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 84.00% | $0.30 | $7.37 | $14.11 | $25.32 | 5/5 | 5/10 | 337 |
| `v42_latent_hole_bookblend80` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.23 | $5.61 | $12.45 | $24.72 | 5/5 | 7/10 | 342 |
| `v42_latent_hole_book` | `edge0_ask100_p0.65_stc0-570` | `prob56` | 82.67% | $0.77 | $6.33 | $13.01 | $24.06 | 4/5 | 6/10 | 334 |
| `v42_latent_hole_book` | `edge0_ask100_p0.65_stc60-570` | `prob56` | 81.33% | $0.70 | $5.80 | $12.28 | $23.22 | 4/5 | 6/10 | 324 |
| `v38_raw` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 82.67% | $0.66 | $5.53 | $12.39 | $24.80 | 4/5 | 6/10 | 343 |
| `v38_raw` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 82.67% | $0.66 | $5.28 | $12.02 | $24.36 | 4/5 | 6/10 | 337 |
| `v42_latent_hole_book` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 82.67% | $0.61 | $9.74 | $16.42 | $27.24 | 4/5 | 6/10 | 334 |
| `v42_latent_hole_book` | `edge0_ask100_p0.65_stc0-600` | `prob56` | 82.67% | $0.60 | $6.65 | $13.33 | $24.46 | 4/5 | 6/10 | 334 |
| `v42_latent_hole_book` | `edge0_ask100_p0.65_stc120-600` | `prob54` | 80.00% | $0.53 | $9.65 | $15.91 | $26.42 | 4/5 | 6/10 | 313 |
| `v42_latent_hole_book` | `edge0_ask100_p0.65_stc60-600` | `prob56` | 81.33% | $0.53 | $6.12 | $12.60 | $23.62 | 4/5 | 6/10 | 324 |
| `v42_latent_hole_book` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 81.33% | $0.52 | $9.21 | $15.69 | $26.40 | 4/5 | 6/10 | 324 |
| `v38_raw` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 82.67% | $0.49 | $4.30 | $11.16 | $23.48 | 4/5 | 6/10 | 343 |
| `v38_raw` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 82.67% | $0.49 | $4.05 | $10.79 | $23.04 | 3/5 | 6/10 | 337 |
| `v42_latent_hole_book` | `edge0_ask100_p0.65_stc120-570` | `prob56` | 80.00% | $0.46 | $6.24 | $12.50 | $23.24 | 4/5 | 6/10 | 313 |
| `v42_latent_hole_book` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 82.67% | $0.44 | $9.42 | $16.10 | $26.84 | 4/5 | 6/10 | 334 |
| `v42_latent_hole_book` | `edge0_ask100_p0.65_stc120-570` | `prob54` | 80.00% | $0.36 | $9.33 | $15.59 | $26.02 | 4/5 | 6/10 | 313 |
| `v42_latent_hole_book` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 81.33% | $0.35 | $8.89 | $15.37 | $26.00 | 4/5 | 5/10 | 324 |
| `v42_latent_hole_book` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 81.33% | $0.31 | $7.63 | $13.99 | $25.02 | 4/5 | 5/10 | 318 |
| `v42_latent_hole_book` | `edge0_ask100_p0.65_stc120-600` | `prob56` | 80.00% | $0.29 | $6.56 | $12.82 | $23.64 | 4/5 | 6/10 | 313 |
| `v42_latent_hole_bookblend80` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 81.33% | $0.28 | $7.56 | $14.36 | $26.08 | 4/5 | 7/10 | 340 |
| `v42_latent_hole_book` | `edge0_ask100_p0.64_stc120-570` | `prob54` | 81.33% | $0.22 | $7.36 | $13.72 | $24.64 | 4/5 | 5/10 | 318 |
| `v42_latent_hole_book` | `edge0_ask100_p0.64_stc60-570` | `prob54` | 82.67% | $0.21 | $6.91 | $13.47 | $24.58 | 4/5 | 5/10 | 328 |
| `v42_latent_hole_bookblend80` | `edge0_ask100_p0.65_stc60-570` | `prob54` | 80.00% | $0.19 | $6.50 | $13.08 | $24.64 | 4/5 | 6/10 | 329 |
| `v42_latent_hole_bookblend80` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $0.15 | $4.87 | $11.45 | $23.56 | 4/5 | 7/10 | 329 |
| `v42_band_bookblend50` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.15 | $3.19 | $10.03 | $22.08 | 3/5 | 7/10 | 342 |
| `v42_latent_hole_bookblend80` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 81.33% | $0.14 | $4.96 | $11.60 | $23.74 | 4/5 | 6/10 | 332 |

## Read

- Best split-positive v42 row is `v42_latent_hole_book` / `edge0_ask100_p0.65_stc0-570` / `prob56` with min split fee+1c $0.77.
- Best all-day-positive v42 row is `v42_latent_hole_bookblend80` / `edge0_ask100_p0.65_stc0-600` / `prob54` with min split fee+1c $0.45.
- Compare this with the explicit-veto all-day v38 row before treating it as a candidate replacement.
