# Touch-Hazard Blocker Overlay Scan

Generated UTC: `20260503_001124Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- The frozen touch-hazard lock is not changed; overlays are diagnostics/challengers only.
- Ranking requires 80% recurring-market coverage on current and v21 before rewarding fresh and OOS profit.

## Data

- Policy: `choose=book_touch_blend_15; book_touch_blend_15>=0.35; 0<=ask<=80; sec>=120; gate=none`
- Lock close time: `2026-05-02T22:00:00+00:00`
- Current intervals: 180
- V21 intervals: 221
- Fresh post-lock base markets: 8
- Overlays scanned: 34
- Both-dataset 80%-coverage overlays: 34
- Both-dataset 80%-coverage overlays positive on all splits: 11

## Top Coverage-Preserving Overlays

| rank | overlay | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | fresh | min OOS ROI | median ask |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `ask>=50 AND touch_loss15>=0.80` | 672.0c/6.57% | 63.01%/96.11% | 715.0c/5.82% | 62.20%/94.57% | 6/2, 110.0c, 100.00% | 8.32% | 56.0c |
| 2 | `ask>=50 AND brownian15<=0.58` | 892.0c/9.00% | 64.29%/93.33% | 902.0c/7.58% | 63.05%/91.86% | 6/2, 110.0c, 100.00% | 7.03% | 56.0c |
| 3 | `score>=0.43 AND touch_loss15>=0.80` | 257.0c/2.46% | 62.21%/95.56% | 761.0c/6.32% | 64.00%/90.50% | 6/2, 110.0c, 100.00% | 0.48% | 58.0c |
| 4 | `ask>=50` | 733.0c/6.87% | 63.69%/99.44% | 688.0c/5.29% | 62.84%/98.64% | 6/2, 110.0c, 100.00% | 0.31% | 56.0c |
| 5 | `ask>=50 AND ask<=70` | 793.0c/7.62% | 63.64%/97.78% | 575.0c/4.55% | 61.68%/96.83% | 6/2, 110.0c, 100.00% | 0.31% | 56.0c |
| 6 | `ask<=70` | 633.0c/6.11% | 62.15%/98.33% | 616.0c/4.93% | 60.93%/97.29% | 5/3, 23.0c, 100.00% | 2.36% | 56.0c |
| 7 | `none` | 547.0c/5.18% | 62.01%/99.44% | 711.0c/5.56% | 61.93%/98.64% | 5/3, 23.0c, 100.00% | 1.69% | 56.0c |
| 8 | `ask>=45` | 542.0c/5.13% | 62.01%/99.44% | 954.0c/7.43% | 63.30%/98.64% | 5/3, 23.0c, 100.00% | 1.45% | 56.0c |
| 9 | `margin15>=-0.10` | 526.0c/4.97% | 62.01%/99.44% | 709.0c/5.54% | 61.93%/98.64% | 5/3, 13.0c, 100.00% | 1.20% | 56.0c |
| 10 | `adverse15<=150` | 606.0c/5.72% | 62.57%/99.44% | 657.0c/5.12% | 61.93%/98.64% | 5/3, 8.0c, 100.00% | 0.96% | 56.0c |
| 11 | `touch_loss15<=0.95` | 468.0c/4.32% | 63.13%/99.44% | 941.0c/7.15% | 64.68%/98.64% | 5/3, -1.0c, 100.00% | 0.19% | 58.0c |
| 12 | `book>=0.60` | 625.0c/5.26% | 69.83%/99.44% | 367.0c/2.49% | 70.23%/97.29% | 7/1, 191.0c, 100.00% | 6.95% | 65.0c |
| 13 | `ask>=50 AND ask<=60` | 897.0c/9.44% | 62.65%/92.22% | 393.0c/3.51% | 58.88%/89.14% | 6/1, 188.0c, 87.50% | 4.57% | 55.0c |
| 14 | `ask<=60` | 734.0c/7.75% | 61.08%/92.78% | 427.0c/3.82% | 58.29%/90.05% | 5/2, 101.0c, 87.50% | 4.91% | 55.0c |
| 15 | `ask>=50 AND drift5<=0.95` | -279.0c/-2.71% | 58.14%/95.56% | 400.0c/3.10% | 61.86%/97.29% | 7/1, 208.0c, 100.00% | -9.87% | 57.0c |

## Read

- Best coverage-preserving overlay: `ask>=50 AND touch_loss15>=0.80`.
- Fresh post-lock result for that overlay: 6/2, 110.0c, 100.00% coverage.
- Current/V21 all-ledger net: 672.0c / 715.0c.
- 11 coverage-preserving overlays were positive on all splits across both datasets.
- This is not a promotion lock; it is an attribution scan for the next frozen challenger.
