# Book-Brownian Arbitration Audit

Generated UTC: `20260504_103836Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Tests fixed book-vs-Brownian side arbitration rules on current and v21 datasets.
- Strict pass requires current+v21 80% split coverage, positive validation/holdout, positive all splits, and block stability.

## Combined Read

| candidate | combined net | current/v21 net | current/v21 acc | current/v21 cov | coverage | all splits | OOS | min positive+coverage blocks | worst block | robust |
|---|---:|---:|---:|---:|---|---|---|---:|---:|---|
| `score_min60_lock_equiv` | 1708.0c | 1174.0c/534.0c | 75.33%/73.85% | 99.02%/98.64% | True | False | True | 63.64% | -228.0c | False |
| `book_margin_locked` | 1376.0c | 951.0c/425.0c | 70.82%/71.23% | 99.35%/99.10% | True | False | True | 60.00% | -332.0c | False |
| `book_margin_skip_brownian_conflict` | 1376.0c | 951.0c/425.0c | 70.82%/71.23% | 99.35%/99.10% | True | False | True | 60.00% | -332.0c | False |
| `brownian70_sec120` | 1044.0c | 912.0c/132.0c | 82.25%/79.81% | 95.44%/96.38% | True | False | True | 54.55% | -368.0c | False |
| `brownian70_override_book60_on_conflict` | 936.0c | 889.0c/47.0c | 82.25%/79.72% | 95.44%/95.93% | True | False | True | 54.55% | -368.0c | False |
| `brownian70_override_book65_on_conflict` | 936.0c | 889.0c/47.0c | 82.25%/79.72% | 95.44%/95.93% | True | False | True | 54.55% | -368.0c | False |
| `brownian70_skip_book_conflict` | 936.0c | 889.0c/47.0c | 82.25%/79.72% | 95.44%/95.93% | True | False | True | 54.55% | -368.0c | False |
| `brownian70_override_book60_no_margin_on_conflict` | 601.0c | 642.0c/-41.0c | 75.25%/78.50% | 98.70%/96.83% | True | False | True | 54.55% | -348.0c | False |
| `brownian70_override_book55_no_margin_on_conflict` | 276.0c | 583.0c/-307.0c | 70.07%/74.42% | 99.02%/97.29% | True | False | False | 45.45% | -416.0c | False |
| `book_conflict_only_no_margin` | 189.0c | 385.0c/-196.0c | 69.83%/56.25% | 58.31%/7.24% | False | False | False | 0.00% | -153.0c | False |
| `book_margin_conflict_only` | 0.0c | 0.0c/0.0c | NA/NA | 0.00%/0.00% | False | False | False | 0.00% | 0.0c | False |
| `brownian70_conflict_only` | -350.0c | -358.0c/8.0c | 28.00%/50.00% | 8.14%/0.90% | False | False | False | 0.00% | -160.0c | False |

## Split Summary

| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | conflict share | coverage | all splits | OOS |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|
| current | `book_conflict_only_no_margin` | 385.0c/3.18% | 69.83%/58.31% | 409.0c | -11.0c | -13.0c | 100.00% | False | False | False |
| v21 | `book_conflict_only_no_margin` | -196.0c/-17.88% | 56.25%/7.24% | -19.0c | -63.0c | -114.0c | 100.00% | False | False | False |
| current | `book_margin_conflict_only` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | 0.00% | False | False | False |
| v21 | `book_margin_conflict_only` | 0.0c/NA | NA/0.00% | 0.0c | 0.0c | 0.0c | 0.00% | False | False | False |
| current | `book_margin_locked` | 951.0c/4.61% | 70.82%/99.35% | 603.0c | 117.0c | 231.0c | 0.00% | True | True | True |
| v21 | `book_margin_locked` | 425.0c/2.80% | 71.23%/99.10% | -80.0c | 212.0c | 293.0c | 0.00% | True | False | True |
| current | `book_margin_skip_brownian_conflict` | 951.0c/4.61% | 70.82%/99.35% | 603.0c | 117.0c | 231.0c | 0.00% | True | True | True |
| v21 | `book_margin_skip_brownian_conflict` | 425.0c/2.80% | 71.23%/99.10% | -80.0c | 212.0c | 293.0c | 0.00% | True | False | True |
| current | `brownian70_conflict_only` | -358.0c/-33.84% | 28.00%/8.14% | -283.0c | -149.0c | 74.0c | 100.00% | False | False | False |
| v21 | `brownian70_conflict_only` | 8.0c/8.70% | 50.00%/0.90% | 8.0c | 0.0c | 0.0c | 100.00% | False | False | False |
| current | `brownian70_override_book55_no_margin_on_conflict` | 583.0c/2.81% | 70.07%/99.02% | 556.0c | 372.0c | -345.0c | 61.18% | True | False | False |
| v21 | `brownian70_override_book55_no_margin_on_conflict` | -307.0c/-1.88% | 74.42%/97.29% | -752.0c | 348.0c | 97.0c | 20.47% | True | False | True |
| current | `brownian70_override_book60_no_margin_on_conflict` | 642.0c/2.90% | 75.25%/98.70% | 482.0c | 53.0c | 107.0c | 45.21% | True | True | True |
| v21 | `brownian70_override_book60_no_margin_on_conflict` | -41.0c/-0.24% | 78.50%/96.83% | -378.0c | 265.0c | 72.0c | 6.54% | True | False | True |
| current | `brownian70_override_book60_on_conflict` | 889.0c/3.83% | 82.25%/95.44% | 298.0c | 262.0c | 329.0c | 0.00% | True | True | True |
| v21 | `brownian70_override_book60_on_conflict` | 47.0c/0.28% | 79.72%/95.93% | -422.0c | 341.0c | 128.0c | 0.00% | True | False | True |
| current | `brownian70_override_book65_on_conflict` | 889.0c/3.83% | 82.25%/95.44% | 298.0c | 262.0c | 329.0c | 0.00% | True | True | True |
| v21 | `brownian70_override_book65_on_conflict` | 47.0c/0.28% | 79.72%/95.93% | -422.0c | 341.0c | 128.0c | 0.00% | True | False | True |
| current | `brownian70_sec120` | 912.0c/3.93% | 82.25%/95.44% | 298.0c | 262.0c | 352.0c | 0.00% | True | True | True |
| v21 | `brownian70_sec120` | 132.0c/0.78% | 79.81%/96.38% | -337.0c | 341.0c | 128.0c | 0.00% | True | False | True |
| current | `brownian70_skip_book_conflict` | 889.0c/3.83% | 82.25%/95.44% | 298.0c | 262.0c | 329.0c | 0.00% | True | True | True |
| v21 | `brownian70_skip_book_conflict` | 47.0c/0.28% | 79.72%/95.93% | -422.0c | 341.0c | 128.0c | 0.00% | True | False | True |
| current | `score_min60_lock_equiv` | 1174.0c/5.40% | 75.33%/99.02% | 784.0c | 287.0c | 103.0c | 0.00% | True | True | True |
| v21 | `score_min60_lock_equiv` | 534.0c/3.43% | 73.85%/98.64% | -19.0c | 398.0c | 155.0c | 0.00% | True | False | True |

## Block Summary

| dataset | candidate | blocks | positive blocks | positive+coverage blocks | worst block |
|---|---|---:|---:|---:|---:|
| current | `book_conflict_only_no_margin` | 15 | 73.33% | 0.00% | -153.0c |
| v21 | `book_conflict_only_no_margin` | 11 | 18.18% | 0.00% | -74.0c |
| current | `book_margin_conflict_only` | 15 | 0.00% | 0.00% | 0.0c |
| v21 | `book_margin_conflict_only` | 11 | 0.00% | 0.00% | 0.0c |
| current | `book_margin_locked` | 15 | 60.00% | 60.00% | -260.0c |
| v21 | `book_margin_locked` | 11 | 63.64% | 63.64% | -332.0c |
| current | `book_margin_skip_brownian_conflict` | 15 | 60.00% | 60.00% | -260.0c |
| v21 | `book_margin_skip_brownian_conflict` | 11 | 63.64% | 63.64% | -332.0c |
| current | `brownian70_conflict_only` | 15 | 26.67% | 0.00% | -160.0c |
| v21 | `brownian70_conflict_only` | 11 | 9.09% | 0.00% | -45.0c |
| current | `brownian70_override_book55_no_margin_on_conflict` | 15 | 53.33% | 53.33% | -188.0c |
| v21 | `brownian70_override_book55_no_margin_on_conflict` | 11 | 45.45% | 45.45% | -416.0c |
| current | `brownian70_override_book60_no_margin_on_conflict` | 15 | 60.00% | 60.00% | -179.0c |
| v21 | `brownian70_override_book60_no_margin_on_conflict` | 11 | 54.55% | 54.55% | -348.0c |
| current | `brownian70_override_book60_on_conflict` | 15 | 73.33% | 73.33% | -290.0c |
| v21 | `brownian70_override_book60_on_conflict` | 11 | 54.55% | 54.55% | -368.0c |
| current | `brownian70_override_book65_on_conflict` | 15 | 73.33% | 73.33% | -290.0c |
| v21 | `brownian70_override_book65_on_conflict` | 11 | 54.55% | 54.55% | -368.0c |
| current | `brownian70_sec120` | 15 | 73.33% | 73.33% | -290.0c |
| v21 | `brownian70_sec120` | 11 | 54.55% | 54.55% | -368.0c |
| current | `brownian70_skip_book_conflict` | 15 | 73.33% | 73.33% | -290.0c |
| v21 | `brownian70_skip_book_conflict` | 11 | 54.55% | 54.55% | -368.0c |
| current | `score_min60_lock_equiv` | 15 | 66.67% | 66.67% | -220.0c |
| v21 | `score_min60_lock_equiv` | 11 | 63.64% | 63.64% | -228.0c |

## Worst Supported Slices

Only slices with at least `12` selected markets are shown.

| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |
|---|---|---|---:|---:|---:|---:|---:|
| v21 | `brownian70_sec120` | time=`sec<=600` | 77 | 54/23 | -779.0c | -10.1c | 78.0c |
| v21 | `brownian70_override_book65_on_conflict` | time=`sec<=600` | 77 | 54/23 | -779.0c | -10.1c | 78.0c |
| v21 | `brownian70_override_book60_on_conflict` | time=`sec<=600` | 77 | 54/23 | -779.0c | -10.1c | 78.0c |
| v21 | `brownian70_skip_book_conflict` | time=`sec<=600` | 77 | 54/23 | -779.0c | -10.1c | 78.0c |
| v21 | `brownian70_override_book55_no_margin_on_conflict` | split=`train` | 128 | 88/40 | -752.0c | -5.9c | 74.0c |
| v21 | `brownian70_override_book55_no_margin_on_conflict` | time=`sec<=600` | 67 | 46/21 | -744.0c | -11.1c | 78.0c |
| v21 | `brownian70_override_book60_no_margin_on_conflict` | time=`sec<=600` | 74 | 52/22 | -731.0c | -9.9c | 78.0c |
| v21 | `book_margin_locked` | ask=`ask<=80` | 44 | 27/17 | -632.0c | -14.4c | 72.5c |
| v21 | `book_margin_skip_brownian_conflict` | ask=`ask<=80` | 44 | 27/17 | -632.0c | -14.4c | 72.5c |
| v21 | `score_min60_lock_equiv` | ask=`ask<=80` | 59 | 40/19 | -486.0c | -8.2c | 73.0c |
| v21 | `brownian70_override_book60_on_conflict` | split=`train` | 126 | 95/31 | -422.0c | -3.3c | 76.0c |
| v21 | `brownian70_override_book65_on_conflict` | split=`train` | 126 | 95/31 | -422.0c | -3.3c | 76.0c |
| v21 | `brownian70_skip_book_conflict` | split=`train` | 126 | 95/31 | -422.0c | -3.3c | 76.0c |
| current | `brownian70_override_book55_no_margin_on_conflict` | hour=`3` | 16 | 7/9 | -388.0c | -24.2c | 61.5c |
| v21 | `brownian70_override_book55_no_margin_on_conflict` | side=`yes` | 118 | 85/33 | -380.0c | -3.2c | 75.0c |
| v21 | `brownian70_override_book60_no_margin_on_conflict` | split=`train` | 127 | 95/32 | -378.0c | -3.0c | 75.0c |
| current | `brownian70_conflict_only` | conflict=`True` | 25 | 7/18 | -358.0c | -14.3c | 41.0c |
| current | `brownian70_conflict_only` | source=`brownian_conflict` | 25 | 7/18 | -358.0c | -14.3c | 41.0c |

## Read

- No book-vs-Brownian arbitration row clears the full robustness gate.
- Side-conflict behavior remains useful failure attribution, not promotion evidence.
