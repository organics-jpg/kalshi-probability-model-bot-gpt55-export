# Kinetic-Guard Physics Sanity Audit

Generated UTC: `20260503_100351Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Tests whether the guarded kinetic family looks physically stable rather than merely explaining a recent loss.
- Does not update any lock and does not count post-outcome diagnostics as fresh evidence.

## Baseline Versus Guard

- Policy: `choose=kinetic_touch_score_15; kinetic_touch_score_15>=0.55; 50<=ask<=95; sec>=120; gate=touch_loss15<=0.90`
- Kinetic lock close time: `2026-05-03T02:15:00+00:00`
- Current intervals: 213; v21 intervals: 221; guard specs scanned: 83

| dataset | model | markets | wins/losses | acc | break-even | coverage | net P&L | ROI | delta vs unguarded |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| current | unguarded kinetic | 211/213 | 147/64 | 69.67% | 66.07% | 99.06% | 759.0c | 5.44% | 0.0c |
| current | `kinetic>=0.57 AND adverse15<=50` | 209/213 | 150/59 | 71.77% | 67.64% | 98.12% | 864.0c | 6.11% | 105.0c |
| v21 | unguarded kinetic | 219/221 | 154/65 | 70.32% | 66.39% | 99.10% | 860.0c | 5.91% | 0.0c |
| v21 | `kinetic>=0.57 AND adverse15<=50` | 217/221 | 156/61 | 71.89% | 68.28% | 98.19% | 783.0c | 5.28% | -77.0c |

## Guard Family Summary

| family | rows | 80%-coverage rows | positive coverage rows | best delta | median delta | best min OOS ROI |
|---|---:|---:|---:|---:|---:|---:|
| `kinetic_adverse` | 25 | 25 | 20 | 237.0c | -82.0c | 8.89% |
| `adverse_ask` | 20 | 18 | 18 | 587.0c | 76.5c | 8.36% |
| `kinetic_adverse_ask` | 18 | 18 | 18 | 339.0c | -22.5c | 8.53% |
| `kinetic_touchloss` | 9 | 9 | 8 | -43.0c | -307.0c | 8.44% |
| `kinetic_margin` | 6 | 6 | 3 | -43.0c | -264.0c | 8.44% |
| `base` | 1 | 1 | 1 | 0.0c | 0.0c | 6.31% |
| `kinetic_book` | 4 | 4 | 0 | -56.0c | -184.0c | 3.81% |

## Top Coverage-Preserving Guards

| rank | guard | family | current net/delta | current acc/cov | v21 net/delta | v21 acc/cov | min OOS ROI |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | `adverse15<=100 AND ask<=70` | `adverse_ask` | 1006.0c/247.0c | 69.35%/93.43% | 1200.0c/340.0c | 70.05%/89.14% | 8.36% |
| 2 | `kinetic>=0.57 AND adverse15<=50 AND ask<=75` | `kinetic_adverse_ask` | 876.0c/117.0c | 70.35%/93.43% | 1082.0c/222.0c | 71.57%/89.14% | 8.48% |
| 3 | `kinetic>=0.58 AND adverse15<=50 AND ask<=75` | `kinetic_adverse_ask` | 857.0c/98.0c | 70.71%/92.96% | 1074.0c/214.0c | 72.02%/87.33% | 6.43% |
| 4 | `adverse15<=100 AND ask<=75` | `adverse_ask` | 994.0c/235.0c | 70.05%/97.18% | 924.0c/64.0c | 69.71%/94.12% | 6.64% |
| 5 | `kinetic>=0.56 AND adverse15<=50 AND ask<=75` | `kinetic_adverse_ask` | 740.0c/-19.0c | 69.00%/93.90% | 1143.0c/283.0c | 71.21%/89.59% | 5.43% |
| 6 | `adverse15<=75 AND ask<=70` | `adverse_ask` | 722.0c/-37.0c | 67.86%/92.02% | 1151.0c/291.0c | 69.79%/86.88% | 4.69% |
| 7 | `kinetic>=0.55 AND adverse15<=100` | `kinetic_adverse` | 935.0c/176.0c | 70.62%/99.06% | 921.0c/61.0c | 70.78%/99.10% | 6.23% |
| 8 | `adverse15<=100 AND ask<=90` | `adverse_ask` | 935.0c/176.0c | 70.62%/99.06% | 914.0c/54.0c | 70.64%/98.64% | 6.23% |
| 9 | `adverse15<=100 AND ask<=85` | `adverse_ask` | 935.0c/176.0c | 70.62%/99.06% | 904.0c/44.0c | 70.51%/98.19% | 6.23% |
| 10 | `kinetic>=0.57 AND adverse15<=100` | `kinetic_adverse` | 1034.0c/275.0c | 72.04%/99.06% | 795.0c/-65.0c | 71.23%/99.10% | 8.89% |
| 11 | `adverse15<=100 AND ask<=80` | `adverse_ask` | 913.0c/154.0c | 70.33%/98.12% | 902.0c/42.0c | 70.23%/97.29% | 5.74% |
| 12 | `kinetic>=0.57 AND adverse15<=75 AND ask<=75` | `kinetic_adverse_ask` | 798.0c/39.0c | 70.10%/95.77% | 1003.0c/143.0c | 71.14%/90.95% | 8.53% |
| 13 | `adverse15<=50 AND ask<=75` | `adverse_ask` | 779.0c/20.0c | 69.00%/93.90% | 1009.0c/149.0c | 70.35%/90.05% | 3.21% |
| 14 | `kinetic>=0.55 AND adverse15<=50` | `kinetic_adverse` | 762.0c/3.0c | 70.33%/98.12% | 973.0c/113.0c | 71.89%/98.19% | 2.87% |
| 15 | `adverse15<=50 AND ask<=90` | `adverse_ask` | 760.0c/1.0c | 70.19%/97.65% | 963.0c/103.0c | 71.63%/97.29% | 2.87% |

## Read

- Both-dataset 80%-coverage guards: 81; all-split-positive coverage guards: 68.
- The locked guard improves current by 105.0c but changes v21 by -77.0c; combined delta is 28.0c.
- Market-set delta for the locked guard: current removed 2 base markets (68.0c) and added 0 alternate markets (0.0c); current common-market entry/timing delta is 173.0c. V21 removed 2 (49.0c) and added 0 (0.0c); v21 common-market entry/timing delta is -28.0c.
- This is a caution flag: the guard repairs the current weak slice but does not dominate the unguarded kinetic rule on v21.
- Treat the guard as a live forward hypothesis only. The next pending outcome is high leverage because one loss would wipe out the current +21c fresh guard net.
