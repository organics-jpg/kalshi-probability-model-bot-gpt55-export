# v40 Observed-FV Strategy Projection

Generated UTC: `2026-05-05T02:52:28.791157+00:00`

## Scope

- Train-only book/FV probability posterior test.
- Strategy projection still requires at least 80% coverage in every split.
- Research-only; live bot untouched.

## Probability Holdout

| candidate | rows | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---:|---:|---:|---:|---:|---:|
| `book_v38_platt` | 3805 | 0.13590 | 0.40918 | 79.74% | 45.65% | 43.23% |
| `book_v39_platt` | 3805 | 0.13591 | 0.40917 | 79.74% | 45.65% | 43.23% |
| `book_platt` | 3805 | 0.13596 | 0.40910 | 79.58% | 45.71% | 43.23% |
| `book_mid` | 3805 | 0.13682 | 0.40972 | 79.42% | 46.75% | 43.23% |
| `book85_v3915_logit_blend` | 3805 | 0.13716 | 0.41040 | 79.40% | 46.82% | 43.23% |
| `book85_v3815_logit_blend` | 3805 | 0.13719 | 0.41047 | 79.40% | 46.81% | 43.23% |
| `book70_v3930_logit_blend` | 3805 | 0.13785 | 0.41219 | 79.29% | 46.90% | 43.23% |
| `book70_v3830_logit_blend` | 3805 | 0.13790 | 0.41235 | 79.26% | 46.89% | 43.23% |
| `v39_midband_v28_fallback_raw` | 3805 | 0.14673 | 0.43702 | 77.16% | 47.44% | 43.23% |
| `v38_long60_antipersist_raw` | 3805 | 0.14681 | 0.43752 | 76.95% | 47.41% | 43.23% |

## Strategy Search

- Candidate probability surfaces: 10
- Rows evaluated after 80% coverage prefilter: 4155
- Fee+1c positive train/validation/holdout rows: 0

## Selected Strategy Rows

| model | entry | exit | min cov | min 1c | all 1c | all fee | gross | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `book85_v3815_logit_blend` | `edge-3_ask95_p0.60_stc0-600` | `prob50` | 83.33% | $-0.07 | $3.81 | $9.49 | $20.86 | 284 |
| `book85_v3815_logit_blend` | `edge-2_ask95_p0.60_stc0-600` | `prob50` | 83.33% | $-0.07 | $3.81 | $9.49 | $20.86 | 284 |
| `book_platt` | `edge1_ask100_p0.65_stc0-780` | `prob52` | 98.48% | $-0.12 | $4.32 | $10.84 | $24.88 | 326 |
| `book_platt` | `edge1_ask95_p0.65_stc0-780` | `prob52` | 98.48% | $-0.12 | $4.32 | $10.84 | $24.88 | 326 |
| `book85_v3815_logit_blend` | `edge-3_ask100_p0.60_stc0-600` | `prob50` | 95.45% | $-0.21 | $3.54 | $9.98 | $21.62 | 322 |
| `book85_v3815_logit_blend` | `edge-2_ask100_p0.60_stc0-600` | `prob50` | 95.45% | $-0.21 | $3.54 | $9.98 | $21.62 | 322 |
| `book70_v3830_logit_blend` | `edge-3_ask95_p0.60_stc0-600` | `prob52` | 83.33% | $-0.43 | $2.98 | $8.70 | $20.40 | 286 |
| `book70_v3830_logit_blend` | `edge-2_ask95_p0.60_stc0-600` | `prob52` | 83.33% | $-0.43 | $2.98 | $8.70 | $20.40 | 286 |
| `book_platt` | `edge1_ask100_p0.60_stc0-900` | `hold` | 98.99% | $-0.47 | $2.89 | $9.45 | $20.36 | 328 |
| `book_platt` | `edge1_ask95_p0.60_stc0-900` | `hold` | 98.99% | $-0.47 | $2.89 | $9.45 | $20.36 | 328 |
| `book_platt` | `edge1_ask90_p0.65_stc0-780` | `prob52` | 89.39% | $-0.52 | $2.22 | $8.26 | $21.96 | 302 |
| `v38_long60_antipersist_raw` | `edge-3_ask95_p0.65_stc0-600` | `prob54` | 83.33% | $-0.59 | $2.95 | $8.67 | $19.94 | 286 |
| `v38_long60_antipersist_raw` | `edge-2_ask95_p0.65_stc0-600` | `prob54` | 83.33% | $-0.59 | $2.95 | $8.67 | $19.94 | 286 |
| `book70_v3830_logit_blend` | `edge-3_ask100_p0.60_stc0-600` | `prob52` | 95.45% | $-0.61 | $2.67 | $9.11 | $21.06 | 322 |
| `book70_v3830_logit_blend` | `edge-2_ask100_p0.60_stc0-600` | `prob52` | 95.45% | $-0.61 | $2.67 | $9.11 | $21.06 | 322 |
| `book85_v3815_logit_blend` | `edge-3_ask95_p0.65_stc0-780` | `prob50` | 83.33% | $-0.62 | $-0.70 | $4.94 | $16.42 | 282 |
| `book85_v3815_logit_blend` | `edge-2_ask95_p0.65_stc0-780` | `prob50` | 83.33% | $-0.62 | $-0.70 | $4.94 | $16.42 | 282 |
| `v38_long60_antipersist_raw` | `edge-3_ask100_p0.65_stc0-600` | `prob54` | 95.45% | $-0.79 | $2.62 | $9.06 | $20.58 | 322 |
| `v38_long60_antipersist_raw` | `edge-2_ask100_p0.65_stc0-600` | `prob54` | 95.45% | $-0.79 | $2.62 | $9.06 | $20.58 | 322 |
| `book70_v3930_logit_blend` | `edge0_ask100_p0.60_stc0-600` | `prob54` | 87.88% | $-0.95 | $0.04 | $6.10 | $17.10 | 303 |
| `book85_v3815_logit_blend` | `edge-3_ask100_p0.65_stc0-780` | `prob50` | 92.42% | $-0.99 | $-1.20 | $5.14 | $16.86 | 317 |
| `book85_v3815_logit_blend` | `edge-2_ask100_p0.65_stc0-780` | `prob50` | 92.42% | $-0.99 | $-1.20 | $5.14 | $16.86 | 317 |
| `v38_long60_antipersist_raw` | `edge-3_ask95_p0.65_stc0-600` | `prob52` | 83.33% | $-1.05 | $1.40 | $7.12 | $18.32 | 286 |
| `v38_long60_antipersist_raw` | `edge-2_ask95_p0.65_stc0-600` | `prob52` | 83.33% | $-1.05 | $1.40 | $7.12 | $18.32 | 286 |
| `book85_v3815_logit_blend` | `edge-3_ask95_p0.60_stc0-600` | `prob52` | 83.33% | $-1.20 | $1.96 | $7.64 | $19.18 | 284 |

## Read

- Observed/book posterior improves raw probability calibration, but did not produce an 80%-coverage fee+1c-positive strategy row.
