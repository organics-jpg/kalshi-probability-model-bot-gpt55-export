# Book-Margin Time-Window Stability Scan

Generated UTC: `20260504_092109Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests causal time windows for the locked book-margin policy.
- Motivation: early entries have more first-passage time for BTC to cross the strike.
- Any passing row is only a forward-test candidate because this scan sees validation/holdout.

## Combined Read

| candidate | combined net | coverage | all splits | OOS | min positive+coverage blocks | robust |
|---|---:|---|---|---|---:|---|
| `book_margin_wait480_locked` | 1737.0c | True | False | False | 63.64% | False |
| `book_margin_locked` | 1413.0c | True | False | True | 60.00% | False |
| `book_margin_window540_780` | 273.0c | True | False | False | 46.67% | False |
| `book_margin_window480_780` | 195.0c | True | False | False | 46.67% | False |
| `book_margin_window360_780` | -45.0c | True | False | False | 46.67% | False |
| `book_margin_max780` | -201.0c | True | False | False | 46.67% | False |
| `book_margin_window540_720` | 70.0c | True | False | False | 40.00% | False |
| `book_margin_window600_780` | 30.0c | False | False | False | 36.36% | False |
| `book_margin_window480_660` | -760.0c | True | False | False | 36.36% | False |
| `book_margin_window480_720` | -134.0c | True | False | False | 33.33% | False |
| `book_margin_window600_720` | -169.0c | False | False | False | 18.18% | False |
| `book_margin_window540_660` | -567.0c | False | False | False | 18.18% | False |

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | median sec | coverage pass | all splits positive |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| current | `book_margin_locked` | 988.0c/4.99% | 70.99%/99.32% | 692.0c | 44.0c | 252.0c | 819.5c | True | True |
| v21 | `book_margin_locked` | 425.0c/2.80% | 71.23%/99.10% | -80.0c | 212.0c | 293.0c | 779.8c | True | False |
| current | `book_margin_max780` | 148.0c/0.72% | 70.65%/99.32% | 38.0c | 325.0c | -215.0c | 766.0c | True | False |
| v21 | `book_margin_max780` | -349.0c/-2.22% | 70.32%/99.10% | -463.0c | 111.0c | 3.0c | 779.1c | True | False |
| current | `book_margin_wait480_locked` | 1018.0c/5.28% | 71.23%/96.61% | 791.0c | -25.0c | 252.0c | 822.8c | True | False |
| v21 | `book_margin_wait480_locked` | 719.0c/5.00% | 72.60%/94.12% | 226.0c | 243.0c | 250.0c | 779.9c | True | True |
| current | `book_margin_window360_780` | 186.0c/0.91% | 70.79%/98.64% | 76.0c | 325.0c | -215.0c | 766.0c | True | False |
| v21 | `book_margin_window360_780` | -231.0c/-1.50% | 70.70%/97.29% | -338.0c | 111.0c | -4.0c | 779.1c | True | False |
| current | `book_margin_window480_660` | -600.0c/-2.90% | 73.36%/92.88% | -366.0c | -266.0c | 32.0c | 649.3c | True | False |
| v21 | `book_margin_window480_660` | -160.0c/-1.11% | 75.66%/85.52% | -326.0c | 138.0c | 28.0c | 659.3c | True | False |
| current | `book_margin_window480_720` | -429.0c/-2.12% | 70.71%/94.92% | -168.0c | -19.0c | -242.0c | 708.5c | True | False |
| v21 | `book_margin_window480_720` | 295.0c/2.05% | 74.62%/89.14% | 137.0c | 133.0c | 25.0c | 719.2c | True | True |
| current | `book_margin_window480_780` | 131.0c/0.66% | 70.67%/95.93% | 101.0c | 256.0c | -226.0c | 766.2c | True | False |
| v21 | `book_margin_window480_780` | 64.0c/0.44% | 72.14%/90.95% | -132.0c | 113.0c | 83.0c | 779.1c | True | False |
| current | `book_margin_window540_660` | -475.0c/-2.39% | 74.05%/88.81% | -218.0c | -289.0c | 32.0c | 649.9c | True | False |
| v21 | `book_margin_window540_660` | -92.0c/-0.68% | 76.14%/79.64% | -124.0c | 94.0c | -62.0c | 659.3c | False | False |
| current | `book_margin_window540_720` | -286.0c/-1.45% | 71.32%/92.20% | -2.0c | -42.0c | -242.0c | 708.8c | True | False |
| v21 | `book_margin_window540_720` | 356.0c/2.55% | 74.87%/86.43% | 254.0c | 133.0c | -31.0c | 719.3c | True | False |
| current | `book_margin_window540_780` | 148.0c/0.76% | 70.76%/93.90% | 141.0c | 233.0c | -226.0c | 766.5c | True | False |
| v21 | `book_margin_window540_780` | 125.0c/0.89% | 72.31%/88.24% | -15.0c | 113.0c | 27.0c | 779.2c | True | False |
| current | `book_margin_window600_720` | -356.0c/-1.91% | 71.21%/87.12% | -83.0c | -57.0c | -216.0c | 709.4c | True | False |
| v21 | `book_margin_window600_720` | 187.0c/1.54% | 74.55%/74.66% | 45.0c | 106.0c | 36.0c | 719.4c | False | True |
| current | `book_margin_window600_780` | -91.0c/-0.49% | 69.92%/90.17% | -46.0c | 218.0c | -263.0c | 767.0c | True | False |
| v21 | `book_margin_window600_780` | 121.0c/0.97% | 72.41%/78.73% | -118.0c | 122.0c | 117.0c | 779.3c | False | False |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask | median sec |
|---|---|---|---:|---:|---:|---:|---:|---:|
| current | `book_margin_window480_720` | score=`p<=0.65` | 102 | 58/44 | -803.0c | -7.9c | 63.0c | 701.1c |
| current | `book_margin_window600_720` | score=`p<=0.65` | 92 | 52/40 | -762.0c | -8.3c | 63.0c | 705.7c |
| current | `book_margin_window540_720` | score=`p<=0.65` | 98 | 56/42 | -746.0c | -7.6c | 63.0c | 703.2c |
| current | `book_margin_window480_720` | ask=`ask<=70` | 167 | 104/63 | -716.0c | -4.3c | 64.0c | 705.0c |
| current | `book_margin_window600_720` | ask=`ask<=70` | 148 | 92/56 | -658.0c | -4.4c | 64.0c | 707.5c |
| v21 | `book_margin_locked` | ask=`ask<=80` | 44 | 27/17 | -632.0c | -14.4c | 72.5c | 779.4c |
| current | `book_margin_window540_720` | ask=`ask<=70` | 161 | 101/60 | -626.0c | -3.9c | 64.0c | 706.4c |
| current | `book_margin_window480_660` | time=`sec<=720` | 240 | 178/62 | -576.0c | -2.4c | 73.0c | 650.6c |
| current | `book_margin_window540_660` | time=`sec<=720` | 240 | 178/62 | -576.0c | -2.4c | 73.0c | 650.6c |
| v21 | `book_margin_max780` | ask=`ask<=80` | 58 | 39/19 | -516.0c | -8.9c | 73.5c | 779.1c |
| v21 | `book_margin_locked` | score=`p<=0.80` | 41 | 26/15 | -513.0c | -12.5c | 73.0c | 779.4c |
| v21 | `book_margin_wait480_locked` | ask=`ask<=80` | 42 | 27/15 | -479.0c | -11.4c | 72.0c | 779.5c |
| v21 | `book_margin_max780` | time=`sec<=600` | 45 | 28/17 | -470.0c | -10.4c | 69.0c | 539.4c |
| v21 | `book_margin_max780` | split=`train` | 131 | 90/41 | -463.0c | -3.5c | 68.0c | 779.1c |
| v21 | `book_margin_window360_780` | ask=`ask<=80` | 57 | 39/18 | -441.0c | -7.7c | 74.0c | 779.1c |
| v21 | `book_margin_max780` | score=`p<=0.80` | 54 | 37/17 | -424.0c | -7.9c | 74.0c | 779.1c |
| current | `book_margin_window540_660` | ask=`ask<=95` | 80 | 66/14 | -414.0c | -5.2c | 86.0c | 652.0c |
| current | `book_margin_window480_660` | ask=`ask<=95` | 80 | 66/14 | -414.0c | -5.2c | 86.0c | 652.0c |

## Read

- No book-margin time-window row clears the combined coverage, split, OOS, and block-stability gate.
