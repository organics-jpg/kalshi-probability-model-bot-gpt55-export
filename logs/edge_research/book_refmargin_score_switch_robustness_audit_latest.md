# Book Reference-Margin Switch Robustness Audit

Generated UTC: `20260504_090453Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Replays the exact locked switch rule on current and v21 ledgers.
- Promotion still requires strict pre-resolution live evidence; this audit can only reject or justify continued collection.

## Locked Rule

- Lock file: `logs\edge_research\profit_book_refmargin_score_switch_lock.json`
- Label: `book_margin_switch_to_score_min60_gap020_if_reference_margin_per_rv_sigma_15m<=0.5`
- Condition source: `reference`
- Condition: `{'feature': 'margin_per_rv_sigma_15m', 'op': '<=', 'threshold': 0.5}`

## Split Metrics

| dataset | policy | all net/acc/cov | train net/acc/cov | validation net/acc/cov | holdout net/acc/cov | split pass |
|---|---|---:|---:|---:|---:|---|
| current | `book_refmargin_score_switch` | 1233.0c/75.68%/98.98% | 683.0c/74.86%/98.87% | 453.0c/79.31%/98.31% | 97.0c/74.58%/100.00% | True |
| current | `book_margin` | 988.0c/70.99%/99.32% | 692.0c/71.02%/99.44% | 44.0c/68.97%/98.31% | 252.0c/72.88%/100.00% | True |
| current | `score_min60_gap020` | 1394.0c/76.21%/98.31% | 844.0c/75.72%/97.74% | 453.0c/79.31%/98.31% | 97.0c/74.58%/100.00% | True |
| v21 | `book_refmargin_score_switch` | 534.0c/73.85%/98.64% | -19.0c/70.77%/98.48% | 398.0c/79.55%/100.00% | 155.0c/77.27%/97.78% | False |
| v21 | `book_margin` | 425.0c/71.23%/99.10% | -80.0c/68.70%/99.24% | 212.0c/72.73%/100.00% | 293.0c/77.27%/97.78% | False |
| v21 | `score_min60_gap020` | 534.0c/73.85%/98.64% | -19.0c/70.77%/98.48% | 398.0c/79.55%/100.00% | 155.0c/77.27%/97.78% | False |

## Chronological Blocks

| dataset | block | markets | wins/losses | acc | break-even | coverage | net P&L | vs book_margin | pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| current | 1 | 37/37 | 26/11 | 70.27% | 69.57% | 100.00% | 26.0c | 86.0c | True |
| current | 2 | 36/37 | 29/7 | 80.56% | 70.58% | 97.30% | 359.0c | 40.0c | True |
| current | 3 | 37/37 | 26/11 | 70.27% | 69.89% | 100.00% | 14.0c | 265.0c | True |
| current | 4 | 37/37 | 28/9 | 75.68% | 72.49% | 100.00% | 118.0c | -359.0c | True |
| current | 5 | 35/37 | 28/7 | 80.00% | 71.49% | 94.59% | 298.0c | 143.0c | True |
| current | 6 | 37/37 | 31/6 | 83.78% | 72.38% | 100.00% | 422.0c | 273.0c | True |
| current | 7 | 37/37 | 27/10 | 72.97% | 71.81% | 100.00% | 43.0c | -52.0c | True |
| current | 8 | 36/36 | 26/10 | 72.22% | 73.53% | 100.00% | -47.0c | -151.0c | False |
| v21 | 1 | 27/28 | 21/6 | 77.78% | 72.33% | 96.43% | 147.0c | 167.0c | True |
| v21 | 2 | 28/28 | 18/10 | 64.29% | 71.71% | 100.00% | -208.0c | -30.0c | False |
| v21 | 3 | 27/27 | 17/10 | 62.96% | 71.19% | 100.00% | -222.0c | -159.0c | False |
| v21 | 4 | 27/28 | 21/6 | 77.78% | 69.33% | 96.43% | 228.0c | 134.0c | True |
| v21 | 5 | 28/28 | 22/6 | 78.57% | 70.75% | 100.00% | 219.0c | -82.0c | True |
| v21 | 6 | 27/27 | 21/6 | 77.78% | 69.70% | 100.00% | 218.0c | 58.0c | True |
| v21 | 7 | 28/28 | 20/8 | 71.43% | 71.36% | 100.00% | 2.0c | 8.0c | True |
| v21 | 8 | 26/27 | 21/5 | 80.77% | 75.00% | 96.30% | 150.0c | 13.0c | True |

## Source Slices

| dataset | bucket | markets | wins/losses | acc | break-even | net P&L | ROI | median ask | pass |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| current | `refmargin_score_switch:book_margin` | 21 | 20/1 | 95.24% | 74.38% | 438.0c | 28.04% | 72.0c | True |
| current | `refmargin_score_switch:book_margin_after_reference` | 61 | 42/19 | 68.85% | 76.41% | -461.0c | -9.89% | 73.0c | False |
| current | `refmargin_score_switch:score_min60_gap020` | 210 | 159/51 | 75.71% | 69.73% | 1256.0c | 8.58% | 67.5c | True |
| v21 | `refmargin_score_switch:book_margin` | 51 | 39/12 | 76.47% | 75.73% | 38.0c | 0.98% | 73.0c | True |
| v21 | `refmargin_score_switch:book_margin_after_reference` | 26 | 23/3 | 88.46% | 79.23% | 240.0c | 11.65% | 78.5c | True |
| v21 | `refmargin_score_switch:score_min60_gap020` | 141 | 99/42 | 70.21% | 68.40% | 256.0c | 2.65% | 66.0c | True |

## Read

- Split gate pass: False.
- Chronological block gate pass: False.
- Source-slice gate pass: False.
- Offline robustness pass: False.
- The locked switch is not robust enough for promotion evidence; keep it as diagnostic/forward-test only.
