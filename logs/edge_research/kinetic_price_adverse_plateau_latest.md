# Kinetic Price/Adverse Plateau Diagnostic

Generated UTC: `20260503_100352Z`

## Scope

- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.
- Scans nearby ask and adverse-motion caps around the kinetic price/adverse guard.
- Any threshold change must receive a separate future lock before it counts as fresh evidence.

## Data

- Policy: `choose=kinetic_touch_score_15; kinetic_touch_score_15>=0.55; 50<=ask<=95; sec>=120; gate=touch_loss15<=0.90`
- Kinetic lock close time: `2026-05-03T02:15:00+00:00`
- Guards scanned: 84
- Both-dataset 80%-coverage guards: 70
- Both-dataset 80%-coverage all-split-positive guards: 70
- Local 3x3 neighbors around `adverse15<=100 AND ask<=70`: 9
- Neighbors with positive current and v21 delta versus unguarded kinetic: 3/9

## Top Plateau Rows

| rank | guard | family | current net/delta | current acc/cov | v21 net/delta | v21 acc/cov | min OOS ROI |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | `adverse15<=100 AND ask<=70` | `adverse_ask_plateau` | 1006.0c/247.0c | 69.35%/93.43% | 1200.0c/340.0c | 70.05%/89.14% | 8.36% |
| 2 | `kinetic>=0.57 AND adverse15<=100 AND ask<=70` | `kinetic57_adverse_ask_plateau` | 1172.0c/413.0c | 70.92%/92.02% | 987.0c/127.0c | 70.00%/85.97% | 12.11% |
| 3 | `kinetic>=0.57 AND adverse15<=125 AND ask<=70` | `kinetic57_adverse_ask_plateau` | 1076.0c/317.0c | 70.41%/92.02% | 987.0c/127.0c | 70.00%/85.97% | 12.11% |
| 4 | `kinetic>=0.57 AND adverse15<=100 AND ask<=75` | `kinetic57_adverse_ask_plateau` | 1098.0c/339.0c | 71.50%/97.18% | 962.0c/102.0c | 70.87%/93.21% | 9.59% |
| 5 | `adverse15<=125 AND ask<=70` | `adverse_ask_plateau` | 908.0c/149.0c | 68.84%/93.43% | 1108.0c/248.0c | 69.54%/89.14% | 8.36% |
| 6 | `ask<=70` | `adverse_ask_plateau` | 804.0c/45.0c | 68.34%/93.43% | 1176.0c/316.0c | 69.85%/90.05% | 8.36% |
| 7 | `kinetic>=0.57 AND adverse15<=125 AND ask<=75` | `kinetic57_adverse_ask_plateau` | 1002.0c/243.0c | 71.01%/97.18% | 961.0c/101.0c | 70.87%/93.21% | 9.59% |
| 8 | `kinetic>=0.57 AND adverse15<=50 AND ask<=75` | `kinetic57_adverse_ask_plateau` | 876.0c/117.0c | 70.35%/93.43% | 1082.0c/222.0c | 71.57%/89.14% | 8.48% |
| 9 | `adverse15<=150 AND ask<=70` | `adverse_ask_plateau` | 802.0c/43.0c | 68.34%/93.43% | 1142.0c/282.0c | 69.70%/89.59% | 8.36% |
| 10 | `kinetic>=0.57 AND ask<=70` | `kinetic57_adverse_ask_plateau` | 966.0c/207.0c | 69.90%/92.02% | 952.0c/92.0c | 69.79%/86.88% | 8.53% |
| 11 | `adverse15<=100 AND ask<=75` | `adverse_ask_plateau` | 994.0c/235.0c | 70.05%/97.18% | 924.0c/64.0c | 69.71%/94.12% | 6.64% |
| 12 | `kinetic>=0.57 AND adverse15<=150 AND ask<=70` | `kinetic57_adverse_ask_plateau` | 964.0c/205.0c | 69.90%/92.02% | 922.0c/62.0c | 69.63%/86.43% | 8.53% |
| 13 | `adverse15<=75 AND ask<=70` | `adverse_ask_plateau` | 722.0c/-37.0c | 67.86%/92.02% | 1151.0c/291.0c | 69.79%/86.88% | 4.69% |
| 14 | `adverse15<=100` | `adverse_ask_plateau` | 935.0c/176.0c | 70.62%/99.06% | 921.0c/61.0c | 70.78%/99.10% | 6.23% |
| 15 | `adverse15<=100 AND ask<=90` | `adverse_ask_plateau` | 935.0c/176.0c | 70.62%/99.06% | 914.0c/54.0c | 70.64%/98.64% | 6.23% |

## Local Neighbor Read

| guard | current delta | v21 delta | current cov | v21 cov | all-split-positive |
|---|---:|---:|---:|---:|---|
| `adverse15<=75 AND ask<=65` | -260.0c | -7.0c | 80.75% | 75.11% | False |
| `adverse15<=75 AND ask<=70` | -37.0c | 291.0c | 92.02% | 86.88% | True |
| `adverse15<=75 AND ask<=75` | -68.0c | 38.0c | 95.77% | 92.31% | True |
| `adverse15<=100 AND ask<=65` | 86.0c | 64.0c | 82.63% | 76.02% | True |
| `adverse15<=100 AND ask<=70` | 247.0c | 340.0c | 93.43% | 89.14% | True |
| `adverse15<=100 AND ask<=75` | 235.0c | 64.0c | 97.18% | 94.12% | True |
| `adverse15<=125 AND ask<=65` | 7.0c | -33.0c | 83.10% | 76.02% | True |
| `adverse15<=125 AND ask<=70` | 149.0c | 248.0c | 93.43% | 89.14% | True |
| `adverse15<=125 AND ask<=75` | 137.0c | -29.0c | 97.18% | 94.12% | True |

## Read

- The local price/adverse neighborhood is mixed; treat the exact guard as fragile until fresh evidence grows.
- Post-outcome plateau diagnostics are useful for physics, but they are not promotion evidence.
