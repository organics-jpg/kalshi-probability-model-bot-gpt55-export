# Book/FV Calibrated Probability

Generated UTC: `2026-05-04T20:57:14.004709+00:00`

## Scope

- Chronological train-only calibration of book/FV probability layers.
- Probability quality only; not a trade scorer and not ask-crossing edge proof.
- No live bot code/process or orders are touched.

## Coefficients

- `book_bias_only`: `[0.037204]`
- `book_platt`: `[-0.065579, 1.108623]`
- `book_v31_platt`: `[-0.068883, 1.197192, -0.097481]`
- `book_v32_platt`: `[-0.068959, 1.198229, -0.096029]`
- `book_v33_platt`: `[-0.068914, 1.197913, -0.095377]`
- `book_v34_platt`: `[-0.069125, 1.199762, -0.097285]`
- `book_v35_platt`: `[-0.068619, 1.192592, -0.089025]`
- `book_v31_time_platt`: `[-0.004612, 1.194904, -0.095689, 0.109918]`
- `book_v31_drift3_platt`: `{'beta': [0.271574, 5.69752, -0.369663, -0.01526], 'means': [0.306026, 0.262382, 14.957027], 'scales': [4.794658, 4.301973, 187.652108], 'l2': 0.3}`
- `book_v32_drift3_platt`: `{'beta': [0.27179, 5.704331, -0.371881, -0.015727], 'means': [0.306026, 0.266422, 14.957027], 'scales': [4.794658, 4.374104, 187.652108], 'l2': 0.3}`
- `book_v33_drift3_platt`: `{'beta': [0.271627, 5.708965, -0.373294, -0.019133], 'means': [0.306026, 0.271208, 14.957027], 'scales': [4.794658, 4.424231, 187.652108], 'l2': 0.3}`
- `book_v34_drift3_platt`: `{'beta': [0.27184, 5.721925, -0.379965, -0.021376], 'means': [0.306026, 0.267976, 14.957027], 'scales': [4.794658, 4.403424, 187.652108], 'l2': 0.3}`
- `book_v35_drift3_platt`: `{'beta': [0.272143, 5.696197, -0.351763, -0.02408], 'means': [0.306026, 0.271418, 14.957027], 'scales': [4.794658, 4.458585, 187.652108], 'l2': 0.3}`
- `book_time_v32drift85`: `{'book_v31_time_platt_logit_weight': 0.15, 'book_v32_drift3_platt_logit_weight': 0.85}`
- `book_time_v33drift85`: `{'book_v31_time_platt_logit_weight': 0.15, 'book_v33_drift3_platt_logit_weight': 0.85}`
- `book_time_v34drift85`: `{'book_v31_time_platt_logit_weight': 0.15, 'book_v34_drift3_platt_logit_weight': 0.85}`
- `book_time_v35drift85`: `{'book_v31_time_platt_logit_weight': 0.15, 'book_v35_drift3_platt_logit_weight': 0.85}`
- `book_v31_micro_platt`: `[0.09129, 1.19718, -0.072231, 0.007382, -0.025931, -0.203772]`

## Holdout

| model | n | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---:|---:|---:|---:|---:|---:|
| `book_v34_drift3_platt` | 3805 | 0.13577 | 0.40868 | 79.50% | 45.64% | 43.23% |
| `book_v31_drift3_platt` | 3805 | 0.13578 | 0.40866 | 79.58% | 45.64% | 43.23% |
| `book_v33_drift3_platt` | 3805 | 0.13578 | 0.40867 | 79.47% | 45.64% | 43.23% |
| `book_v35_drift3_platt` | 3805 | 0.13578 | 0.40868 | 79.47% | 45.65% | 43.23% |
| `book_v32_drift3_platt` | 3805 | 0.13578 | 0.40871 | 79.58% | 45.64% | 43.23% |
| `book_time_v34drift85` | 3805 | 0.13580 | 0.40872 | 79.53% | 45.64% | 43.23% |
| `book_time_v33drift85` | 3805 | 0.13580 | 0.40872 | 79.53% | 45.65% | 43.23% |
| `book_time_v35drift85` | 3805 | 0.13581 | 0.40872 | 79.53% | 45.65% | 43.23% |
| `book_time_v32drift85` | 3805 | 0.13581 | 0.40875 | 79.55% | 45.65% | 43.23% |
| `book_v31_platt` | 3805 | 0.13586 | 0.40900 | 79.68% | 45.64% | 43.23% |
| `book_v32_platt` | 3805 | 0.13587 | 0.40907 | 79.68% | 45.64% | 43.23% |
| `book_v33_platt` | 3805 | 0.13588 | 0.40909 | 79.68% | 45.65% | 43.23% |
| `book_v34_platt` | 3805 | 0.13589 | 0.40915 | 79.74% | 45.65% | 43.23% |
| `book_v35_platt` | 3805 | 0.13592 | 0.40920 | 79.74% | 45.66% | 43.23% |
| `book_platt` | 3805 | 0.13596 | 0.40910 | 79.58% | 45.71% | 43.23% |
| `book_v31_time_platt` | 3805 | 0.13605 | 0.40923 | 79.45% | 45.66% | 43.23% |
| `book_mid_probability` | 3805 | 0.13682 | 0.40972 | 79.42% | 46.75% | 43.23% |
| `book_v31_micro_platt` | 3805 | 0.13711 | 0.41482 | 79.11% | 45.69% | 43.23% |
| `v35_probability` | 3805 | 0.14694 | 0.43800 | 76.95% | 47.43% | 43.23% |
| `v34_probability` | 3805 | 0.14701 | 0.43800 | 76.98% | 47.44% | 43.23% |
| `v33_probability` | 3805 | 0.14703 | 0.43836 | 76.66% | 47.47% | 43.23% |
| `v32_probability` | 3805 | 0.14714 | 0.43848 | 77.32% | 47.51% | 43.23% |
| `v31_probability` | 3805 | 0.14728 | 0.43872 | 77.35% | 47.55% | 43.23% |
| `v28_live_surface` | 3805 | 0.14872 | 0.44383 | 77.42% | 47.80% | 43.23% |
| `book_bias_only` | 3805 | 0.25135 | 0.69584 | 43.23% | 50.93% | 43.23% |

## Validation

| model | n | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---:|---:|---:|---:|---:|---:|
| `book_time_v32drift85` | 3818 | 0.12122 | 0.36256 | 80.83% | 50.83% | 51.89% |
| `book_v31_time_platt` | 3818 | 0.12122 | 0.36232 | 80.59% | 50.90% | 51.89% |
| `book_v31_drift3_platt` | 3818 | 0.12123 | 0.36262 | 80.75% | 50.82% | 51.89% |
| `book_v32_drift3_platt` | 3818 | 0.12123 | 0.36264 | 80.72% | 50.82% | 51.89% |
| `book_time_v33drift85` | 3818 | 0.12126 | 0.36266 | 80.83% | 50.83% | 51.89% |
| `book_v33_drift3_platt` | 3818 | 0.12127 | 0.36275 | 80.67% | 50.82% | 51.89% |
| `book_v31_platt` | 3818 | 0.12128 | 0.36273 | 80.67% | 50.81% | 51.89% |
| `book_v32_platt` | 3818 | 0.12128 | 0.36276 | 80.67% | 50.81% | 51.89% |
| `book_time_v34drift85` | 3818 | 0.12132 | 0.36281 | 80.83% | 50.83% | 51.89% |
| `book_time_v35drift85` | 3818 | 0.12133 | 0.36283 | 80.88% | 50.83% | 51.89% |
| `book_mid_probability` | 3818 | 0.12134 | 0.36487 | 80.38% | 51.73% | 51.89% |
| `book_v34_drift3_platt` | 3818 | 0.12134 | 0.36292 | 80.70% | 50.82% | 51.89% |
| `book_v33_platt` | 3818 | 0.12135 | 0.36295 | 80.67% | 50.81% | 51.89% |
| `book_v35_drift3_platt` | 3818 | 0.12135 | 0.36295 | 80.75% | 50.82% | 51.89% |
| `book_v34_platt` | 3818 | 0.12145 | 0.36319 | 80.62% | 50.81% | 51.89% |
| `book_v35_platt` | 3818 | 0.12148 | 0.36326 | 80.62% | 50.82% | 51.89% |
| `book_v31_micro_platt` | 3818 | 0.12149 | 0.36309 | 80.46% | 50.62% | 51.89% |
| `book_platt` | 3818 | 0.12170 | 0.36378 | 80.78% | 50.91% | 51.89% |
| `v35_probability` | 3818 | 0.13420 | 0.40151 | 79.10% | 51.96% | 51.89% |
| `v34_probability` | 3818 | 0.13435 | 0.40196 | 79.10% | 51.96% | 51.89% |
| `v33_probability` | 3818 | 0.13538 | 0.40493 | 78.71% | 51.99% | 51.89% |
| `v31_probability` | 3818 | 0.13600 | 0.40686 | 78.58% | 52.03% | 51.89% |
| `v32_probability` | 3818 | 0.13602 | 0.40697 | 78.58% | 52.01% | 51.89% |
| `v28_live_surface` | 3818 | 0.13667 | 0.41049 | 78.58% | 52.11% | 51.89% |
| `book_bias_only` | 3818 | 0.24974 | 0.69262 | 51.89% | 50.93% | 51.89% |

## Read

- Best holdout model: `book_v34_drift3_platt` at Brier/logloss 0.13577/0.40868.
- If calibrated book beats raw book on validation but not holdout, treat it as unstable and do not promote.
- If the physics coefficient is small or negative in a book/FV posterior, current physics adds little beyond book once book is observed.
