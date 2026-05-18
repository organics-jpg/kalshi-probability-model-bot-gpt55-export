# v31 Book Observation Blend

Generated UTC: `2026-05-04T17:50:34.538547+00:00`

## Scope

- Probability calibration only; not a trade scorer.
- Treats Kalshi book mid as a noisy observation and blends it with v31 log-odds.
- Better book calibration does not imply edge after crossing the ask/spread.

## Holdout

| model | n | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---:|---:|---:|---:|---:|---:|
| `book_mid_probability` | 3805 | 0.13682 | 0.40972 | 79.42% | 46.75% | 43.23% |
| `v31_book_logit_blend_w1.00` | 3805 | 0.13682 | 0.40972 | 79.42% | 46.75% | 43.23% |
| `v31_book_logit_blend_w0.80` | 3805 | 0.13747 | 0.41123 | 79.37% | 46.86% | 43.23% |
| `v31_book_logit_blend_w0.70` | 3805 | 0.13802 | 0.41270 | 79.37% | 46.93% | 43.23% |
| `v31_book_logit_blend_w0.60` | 3805 | 0.13873 | 0.41468 | 79.40% | 47.00% | 43.23% |
| `v31_book_logit_blend_w0.50` | 3805 | 0.13961 | 0.41716 | 79.11% | 47.07% | 43.23% |
| `v31_book_logit_blend_w0.40` | 3805 | 0.14068 | 0.42018 | 78.92% | 47.15% | 43.23% |
| `v31_book_logit_blend_w0.35` | 3805 | 0.14129 | 0.42189 | 78.87% | 47.20% | 43.23% |
| `v31_book_logit_blend_w0.30` | 3805 | 0.14195 | 0.42375 | 78.63% | 47.24% | 43.23% |
| `v31_book_logit_blend_w0.25` | 3805 | 0.14266 | 0.42577 | 78.34% | 47.29% | 43.23% |
| `v31_book_logit_blend_w0.20` | 3805 | 0.14343 | 0.42796 | 78.21% | 47.33% | 43.23% |
| `v31_book_logit_blend_w0.15` | 3805 | 0.14428 | 0.43033 | 78.00% | 47.39% | 43.23% |

## Validation

| model | n | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---:|---:|---:|---:|---:|---:|
| `book_mid_probability` | 3818 | 0.12134 | 0.36487 | 80.38% | 51.73% | 51.89% |
| `v31_book_logit_blend_w1.00` | 3818 | 0.12134 | 0.36487 | 80.38% | 51.73% | 51.89% |
| `v31_book_logit_blend_w0.80` | 3818 | 0.12284 | 0.36897 | 80.49% | 51.83% | 51.89% |
| `v31_book_logit_blend_w0.70` | 3818 | 0.12385 | 0.37185 | 80.59% | 51.87% | 51.89% |
| `v31_book_logit_blend_w0.60` | 3818 | 0.12502 | 0.37526 | 80.54% | 51.91% | 51.89% |
| `v31_book_logit_blend_w0.50` | 3818 | 0.12637 | 0.37919 | 80.41% | 51.93% | 51.89% |
| `v31_book_logit_blend_w0.40` | 3818 | 0.12791 | 0.38365 | 80.17% | 51.96% | 51.89% |
| `v31_book_logit_blend_w0.35` | 3818 | 0.12874 | 0.38608 | 79.88% | 51.97% | 51.89% |
| `v31_book_logit_blend_w0.30` | 3818 | 0.12963 | 0.38863 | 79.54% | 51.98% | 51.89% |
| `v31_book_logit_blend_w0.25` | 3818 | 0.13057 | 0.39133 | 79.47% | 51.99% | 51.89% |
| `v31_book_logit_blend_w0.20` | 3818 | 0.13155 | 0.39415 | 79.07% | 52.00% | 51.89% |
| `v31_book_logit_blend_w0.15` | 3818 | 0.13259 | 0.39712 | 78.78% | 52.00% | 51.89% |

## Read

- Best holdout probability model: `book_mid_probability` at Brier/logloss 0.13682/0.40972.
- The book mid dominates pure physics probability calibration in this sample.
- The next FV question is how much book observation to trust without erasing tradable edge.
