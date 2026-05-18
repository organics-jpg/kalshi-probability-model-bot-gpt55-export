# v45 Latent Disagreement Switch Strategy

Generated UTC: `2026-05-05T05:53:00.575478+00:00`

## Scope

- Research-only FV probability probe on top of v38/v43 latent-hole logic.
- Inside latent-hole state, switch fully to book only when raw FV and book selected sides disagree.
- Entry/exit replay keeps the same 80% split-coverage, fee, and 1c haircut checks.
- Live bot untouched.

## Model Notes

- Latent-hole markets: 45
- Latent-hole rows: 1356
- Raw/book disagreement rows inside latent state: 631
- Raw/book disagreement markets inside latent state: 44

## Holdout Probability

| candidate | Brier | logloss | side acc | mean p_yes |
|---|---:|---:|---:|---:|
| `v45_latent_full_book_reference` | 0.14222 | 0.42772 | 79.01% | 49.69% |
| `v45_latent_disagree_book_else_blend90` | 0.14228 | 0.42788 | 78.99% | 49.70% |
| `v45_latent_blend90_reference` | 0.14228 | 0.42787 | 78.99% | 49.69% |
| `v45_latent_disagree_book_else_raw` | 0.14301 | 0.42999 | 78.83% | 49.79% |

## Strategy Search

- Candidate probability surfaces: 4
- Rows evaluated after 80% coverage prefilter: 935
- Fee+1c positive train/validation/holdout rows: 40
- Fee+1c positive all-day rows: 12
- All-day rows with at least 7/10 positive chronological blocks: 5

## Selected Strategy Rows

| model | entry | exit | min cov | min 1c | all 1c | all fee | gross | days | block10 | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `v45_latent_disagree_book_else_blend90` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.45 | $10.55 | $17.23 | $28.42 | 5/5 | 8/10 | 334 |
| `v45_latent_blend90_reference` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.45 | $9.85 | $16.63 | $28.38 | 5/5 | 7/10 | 339 |
| `v45_latent_full_book_reference` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 84.00% | $0.39 | $7.64 | $14.38 | $25.70 | 5/5 | 6/10 | 337 |
| `v45_latent_disagree_book_else_blend90` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.36 | $9.67 | $16.13 | $27.18 | 5/5 | 7/10 | 323 |
| `v45_latent_blend90_reference` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 80.00% | $0.36 | $8.79 | $15.35 | $26.94 | 5/5 | 7/10 | 328 |
| `v45_latent_full_book_reference` | `edge0_ask100_p0.64_stc0-570` | `prob54` | 84.00% | $0.30 | $7.37 | $14.11 | $25.32 | 5/5 | 5/10 | 337 |
| `v45_latent_full_book_reference` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 82.67% | $0.30 | $7.18 | $13.74 | $24.96 | 5/5 | 5/10 | 328 |
| `v45_latent_blend90_reference` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.23 | $6.94 | $13.76 | $25.96 | 5/5 | 8/10 | 341 |
| `v45_latent_disagree_book_else_blend90` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.23 | $7.64 | $14.36 | $26.00 | 5/5 | 6/10 | 336 |
| `v45_latent_disagree_book_else_raw` | `edge-2_ask100_p0.66_stc0-570` | `prob54` | 85.33% | $-1.39 | $2.49 | $9.53 | $21.46 | 4/5 | 5/10 | 352 |
| `v45_latent_disagree_book_else_raw` | `edge-2_ask100_p0.66_stc120-570` | `prob54` | 81.33% | $-1.45 | $2.71 | $9.39 | $21.16 | 4/5 | 6/10 | 334 |
| `v45_latent_disagree_book_else_raw` | `edge-2_ask100_p0.66_stc60-570` | `prob54` | 82.67% | $-1.46 | $2.67 | $9.45 | $21.26 | 4/5 | 6/10 | 339 |

## Read

- Best robust v45 row is `v45_latent_disagree_book_else_blend90` / `edge0_ask100_p0.65_stc0-600` / `prob54` with min split fee+1c $0.45.
