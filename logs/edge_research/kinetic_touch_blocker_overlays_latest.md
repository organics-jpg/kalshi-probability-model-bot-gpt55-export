# Kinetic-Touch Blocker Overlay Scan

Generated UTC: `20260503_100352Z`

## Scope

- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.
- Scans simple causal overlays on top of the frozen kinetic-touch rule.
- Any useful overlay must receive a separate future lock before it counts as fresh validation.

## Data

- Policy: `choose=kinetic_touch_score_15; kinetic_touch_score_15>=0.55; 50<=ask<=95; sec>=120; gate=touch_loss15<=0.90`
- Lock close time: `2026-05-03T02:15:00+00:00`
- Current intervals: 213
- V21 intervals: 221
- Fresh base intervals after kinetic lock: 30
- Overlays scanned: 36
- Both-dataset 80%-coverage overlays: 36
- Both-dataset 80%-coverage all-split-positive overlays: 25

## Top Coverage-Preserving Overlays

| rank | overlay | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | fresh net | min OOS ROI |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `kinetic>=0.57 AND ask<=80` | 849.0c/6.04% | 70.95%/98.59% | 722.0c/4.99% | 70.37%/97.74% | 262.0c | 8.77% |
| 2 | `kinetic>=0.57` | 854.0c/6.04% | 71.09%/99.06% | 722.0c/4.89% | 70.78%/99.10% | 262.0c | 8.44% |
| 3 | `ask<=70` | 804.0c/6.28% | 68.34%/93.43% | 1176.0c/9.24% | 69.85%/90.05% | 233.0c | 8.36% |
| 4 | `kinetic>=0.57 AND adverse15<=50` | 864.0c/6.11% | 71.77%/98.12% | 783.0c/5.28% | 71.89%/98.19% | 242.0c | 7.64% |
| 5 | `touch_loss15>=0.50` | 846.0c/6.15% | 69.86%/98.12% | 846.0c/5.98% | 69.77%/97.29% | 191.0c | 6.85% |
| 6 | `ask<=75` | 796.0c/5.89% | 69.08%/97.18% | 900.0c/6.57% | 69.52%/95.02% | 212.0c | 6.64% |
| 7 | `none` | 759.0c/5.44% | 69.67%/99.06% | 860.0c/5.91% | 70.32%/99.10% | 213.0c | 6.31% |
| 8 | `margin15>=0.00` | 759.0c/5.44% | 69.67%/99.06% | 860.0c/5.91% | 70.32%/99.10% | 213.0c | 6.31% |
| 9 | `spread<=2` | 759.0c/5.44% | 69.67%/99.06% | 831.0c/5.70% | 70.32%/99.10% | 212.0c | 6.31% |
| 10 | `ask<=80` | 754.0c/5.45% | 69.52%/98.59% | 857.0c/6.02% | 69.91%/97.74% | 213.0c | 6.27% |
| 11 | `adverse15<=100` | 935.0c/6.70% | 70.62%/99.06% | 921.0c/6.32% | 70.78%/99.10% | 213.0c | 6.23% |
| 12 | `adverse15<=20` | 903.0c/6.41% | 71.77%/98.12% | 674.0c/4.55% | 71.43%/98.19% | 301.0c | 3.23% |
| 13 | `adverse15<=50 AND ask<=80` | 753.0c/5.64% | 69.46%/95.31% | 880.0c/6.46% | 70.39%/93.21% | 210.0c | 3.02% |
| 14 | `adverse15<=50` | 762.0c/5.47% | 70.33%/98.12% | 973.0c/6.65% | 71.89%/98.19% | 193.0c | 2.87% |
| 15 | `margin15>=0.00 AND adverse15<=50` | 762.0c/5.47% | 70.33%/98.12% | 973.0c/6.65% | 71.89%/98.19% | 193.0c | 2.87% |

## Read

- Best all-split-positive coverage-preserving overlay: `kinetic>=0.57 AND ask<=80`.
- It has current 849.0c / 6.04%, v21 722.0c / 4.99%, and fresh diagnostic net 262.0c.
- This scan is post-outcome diagnostics only; do not merge an overlay into existing fresh evidence.
