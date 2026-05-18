# Locked Profit Candidate Blocker Overlays

Generated UTC: `20260502_213940Z`

## Scope

- Research-only challenger scan; no orders are submitted and no bot files or live processes are touched.
- The locked candidate itself is not changed. Overlays are candidate refinements for falsification.
- Each overlay is causal and applied before first-per-market selection.
- Ranking requires 80% recurring-market coverage across current and v21 before rewarding profitability.

## Data

- Locked policy: `choose=brownian_p_rv_15m; brownian_p_rv_15m>=0.55; ask<=95; sec_to_close>=120; adverse15<=10_or_margin_rv15>=0.5`
- Lock close time: `2026-05-02T20:30:00+00:00`
- Current intervals: 169; rows: 19538
- V21 intervals: 221; rows: 6554
- Overlays scanned: 180
- Both-dataset 80%-coverage overlays: 157
- Both-dataset 80%-coverage overlays positive on all splits: 15

## Top Coverage-Preserving Overlays

| rank | overlay | current net/ROI | current train | current acc/cov | v21 net/ROI | v21 train | v21 acc/cov | fresh net/cov | min OOS ROI | median ask |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `ask>=50 AND ask<=80` | 661.0c/6.21% | 189.0c/2.95% | 68.90%/97.04% | 1151.0c/8.31% | 437.0c/5.35% | 70.75%/95.93% | 16.0c/100.00% | 10.28% | 62.0c |
| 2 | `ask>=50` | 671.0c/6.14% | 174.0c/2.67% | 69.46%/98.82% | 1186.0c/8.17% | 467.0c/5.35% | 71.69%/99.10% | 16.0c/100.00% | 10.85% | 62.0c |
| 3 | `ask>=50 AND ask<=90` | 671.0c/6.14% | 174.0c/2.67% | 69.46%/98.82% | 1173.0c/8.19% | 454.0c/5.31% | 71.43%/98.19% | 16.0c/100.00% | 10.85% | 62.0c |
| 4 | `ask>=55 AND brownian30>=0.55` | 451.0c/3.97% | 153.0c/2.27% | 70.66%/98.82% | 712.0c/4.72% | 437.0c/4.82% | 72.15%/99.10% | -108.0c/100.00% | 1.28% | 65.0c |
| 5 | `ask>=60` | 369.0c/3.17% | 123.0c/1.79% | 71.86%/98.82% | 727.0c/4.70% | 257.0c/2.75% | 74.31%/98.64% | -113.0c/100.00% | 2.08% | 67.0c |
| 6 | `ask>=60 AND book>=0.55` | 369.0c/3.17% | 123.0c/1.79% | 71.86%/98.82% | 727.0c/4.70% | 257.0c/2.75% | 74.31%/98.64% | -113.0c/100.00% | 2.08% | 67.0c |
| 7 | `ask>=60 AND mean_book_rv15>=0.55` | 369.0c/3.17% | 123.0c/1.79% | 71.86%/98.82% | 727.0c/4.70% | 257.0c/2.75% | 74.31%/98.64% | -113.0c/100.00% | 2.08% | 67.0c |
| 8 | `ask>=60 AND ask<=90` | 364.0c/3.16% | 123.0c/1.79% | 71.69%/98.22% | 707.0c/4.65% | 244.0c/2.66% | 73.95%/97.29% | -113.0c/100.00% | 1.95% | 67.0c |
| 9 | `ask>=60 AND ask<=80` | 331.0c/2.96% | 115.0c/1.72% | 70.99%/95.86% | 651.0c/4.54% | 200.0c/2.35% | 72.82%/93.21% | -113.0c/100.00% | 0.67% | 66.0c |
| 10 | `ask>=60 AND brownian30>=0.60` | 424.0c/3.54% | 280.0c/3.99% | 74.70%/98.22% | 718.0c/4.55% | 144.0c/1.52% | 76.04%/98.19% | -112.0c/100.00% | 2.29% | 70.0c |
| 11 | `ask>=50 AND brownian30>=0.55` | 496.0c/4.47% | 95.0c/1.44% | 69.46%/98.82% | 980.0c/6.66% | 298.0c/3.39% | 71.69%/99.10% | 14.0c/100.00% | 8.74% | 63.0c |
| 12 | `ask>=50 AND brownian15>=0.60` | 188.0c/1.63% | 75.0c/1.10% | 70.06%/98.82% | 667.0c/4.32% | 149.0c/1.61% | 73.52%/99.10% | -107.0c/100.00% | 1.14% | 67.0c |
| 13 | `ask>=60 AND brownian30>=0.55` | 274.0c/2.34% | 72.0c/1.04% | 71.86%/98.82% | 723.0c/4.67% | 253.0c/2.71% | 74.31%/98.64% | -113.0c/100.00% | 0.63% | 67.0c |
| 14 | `ask>=50 AND adverse15<=20` | 587.0c/5.38% | 29.0c/0.45% | 69.28%/98.22% | 1078.0c/7.47% | 488.0c/5.60% | 71.43%/98.19% | 16.0c/100.00% | 8.60% | 62.0c |
| 15 | `ask>=60 AND mean_book_rv15>=0.60` | 464.0c/3.92% | 117.0c/1.68% | 73.65%/98.82% | 419.0c/2.67% | 38.0c/0.40% | 73.85%/98.64% | -113.0c/100.00% | 3.95% | 68.0c |

## Read

- Baseline locked candidate: current 400.0c, v21 1194.0c, current train -95.0c.
- Best all-split-positive overlay: `ask>=50 AND ask<=80` with current 661.0c and v21 1151.0c.
- This is a challenger only; it should not replace the locked fresh validation candidate without its own forward lock.
