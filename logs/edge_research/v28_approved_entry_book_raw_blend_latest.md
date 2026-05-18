# v28 Approved-Entry Book/Raw FV Blend

- Surface: `actual_v28_approved_entries_only`
- Hypothesis: `convex FV blend p = book + alpha * (raw - book)`
- Rows: `173`
- Best alpha raw weight: `0.350000`
- Best Brier/logloss deltas vs raw: `-0.007792/-0.057994`
- Best bootstrap p95 Brier/logloss vs raw: `0.003590/0.009405`
- Blockers: `bootstrap_brier_p95_not_negative, bootstrap_logloss_p95_not_negative`

## Interpretation

- Best blend uses raw weight alpha=0.35; alpha=0 is pure book and alpha=1 is raw v28.
- Best Brier/logloss deltas versus raw are -0.007791697570985245/-0.057993896385894306.
- Raw v28 appears useful only as a partial memory term after anchoring to the executable book.
- Promotion blockers: bootstrap_brier_p95_not_negative, bootstrap_logloss_p95_not_negative.

## Alpha Ranking

| rank | alpha raw weight | rows | W/L | avg p | win rate | cal err | brier | d brier | brier p95 | logloss | d logloss | logloss p95 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.350000 | 173 | 146/27 | 0.814632 | 0.843931 | 0.029298 | 0.125842 | -0.007792 | 0.003590 | 0.415262 | -0.057994 | 0.009405 |
| 2 | 0.500000 | 173 | 146/27 | 0.830614 | 0.843931 | 0.013316 | 0.126104 | -0.007530 | 0.001275 | 0.414482 | -0.058774 | 0.002746 |
| 3 | 0.200000 | 173 | 146/27 | 0.798650 | 0.843931 | 0.045280 | 0.126503 | -0.007131 | 0.006357 | 0.418116 | -0.055140 | 0.017709 |
| 4 | 0.100000 | 173 | 146/27 | 0.787996 | 0.843931 | 0.055935 | 0.127455 | -0.006179 | 0.008368 | 0.421001 | -0.052255 | 0.022712 |
| 5 | 0.750000 | 173 | 146/27 | 0.857251 | 0.843931 | -0.013320 | 0.128589 | -0.005046 | -0.000175 | 0.419780 | -0.053477 | -0.001681 |
| 6 | 0.000000 | 173 | 146/27 | 0.777341 | 0.843931 | 0.066590 | 0.128817 | -0.004817 | 0.010643 | 0.424602 | -0.048654 | 0.029276 |
| 7 | 1.000000 | 173 | 146/27 | 0.883888 | 0.843931 | -0.039957 | 0.133634 | 0.000000 | 0.000000 | 0.473256 | 0.000000 | 0.000000 |

## Raw/Book Disagreement Buckets

| bucket | rows | W/L | avg raw-book | best brier | book brier | raw brier | best logloss | book logloss | raw logloss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| raw_above_book_5_15 | 146 | 127/19 | 0.077256 | 0.114035 | 0.117751 | 0.111406 | 0.387061 | 0.399101 | 0.376080 |
| raw_above_book_gt15 | 27 | 19/8 | 0.264935 | 0.189688 | 0.188659 | 0.253827 | 0.567755 | 0.562494 | 0.998725 |

## Worst Leave-One-Market Slices For Best Alpha

| left out | rows | W/L | d brier vs raw | d logloss vs raw |
|---|---:|---:|---:|---:|
| KXBTC15M-26MAY060330-30 | 171 | 145/26 | -0.003130 | -0.012792 |
| KXBTC15M-26MAY051715-15 | 170 | 146/24 | -0.003790 | -0.046203 |
| KXBTC15M-26MAY052245-45 | 172 | 146/26 | -0.004914 | -0.048942 |
| KXBTC15M-26MAY070015-15 | 172 | 146/26 | -0.006087 | -0.048196 |
| KXBTC15M-26MAY060745-45 | 171 | 146/25 | -0.006456 | -0.053973 |
| KXBTC15M-26MAY052045-45 | 171 | 146/25 | -0.006993 | -0.054869 |
| KXBTC15M-26MAY062015-15 | 170 | 145/25 | -0.007015 | -0.053465 |
| KXBTC15M-26MAY062130-30 | 172 | 146/26 | -0.007020 | -0.055111 |
| KXBTC15M-26MAY060215-15 | 170 | 145/25 | -0.007031 | -0.055490 |
| KXBTC15M-26MAY071015-15 | 170 | 145/25 | -0.007108 | -0.056010 |
| KXBTC15M-26MAY062115-15 | 170 | 144/26 | -0.007120 | -0.056952 |
| KXBTC15M-26MAY060900-00 | 169 | 144/25 | -0.007295 | -0.056895 |
