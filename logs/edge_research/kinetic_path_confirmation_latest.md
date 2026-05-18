# Kinetic Path-Confirmation Scan

Generated UTC: `20260504_053420Z`

## Scope

- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.
- Tests delayed same-side confirmation after the frozen kinetic-touch row first becomes eligible.
- Any confirmation rule must receive a separate future lock before it counts as fresh validation.

## Data

- Policy: `choose=kinetic_touch_score_15; kinetic_touch_score_15>=0.55; 50<=ask<=95; sec>=120; gate=touch_loss15<=0.90`
- Kinetic lock close time: `2026-05-03T02:15:00+00:00`
- Rules scanned: 101
- Both-dataset 80%-coverage rules: 63
- Both-dataset all-split-positive coverage rules: 18
- Baseline current/v21 net: 334.0c / 860.0c

## Top Confirmation Rows

| rank | confirmation | current net/delta | current acc/cov | v21 net/delta | v21 acc/cov | fresh | min OOS ROI |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `same_side_for>=60s AND confirm_score>=0.6` | 1492.0c/1158.0c | 79.86%/98.61% | 794.0c/-66.0c | 79.53%/97.29% | 84/20 458.0c | 4.61% |
| 2 | `same_side_for>=60s AND confirm_score>=0.57` | 1635.0c/1301.0c | 78.87%/98.95% | 575.0c/-285.0c | 77.17%/99.10% | 83/21 535.0c | 4.93% |
| 3 | `same_side_for>=60s AND confirm_score>=0.55` | 1579.0c/1245.0c | 77.82%/98.95% | 611.0c/-249.0c | 76.71%/99.10% | 81/23 432.0c | 2.64% |
| 4 | `same_side_for>=30s AND confirm_score>=0.6` | 1486.0c/1152.0c | 76.41%/98.95% | 685.0c/-175.0c | 77.42%/98.19% | 80/24 430.0c | 4.90% |
| 5 | `same_side_for>=120s AND confirm_score>=0.6` | 1440.0c/1106.0c | 83.09%/96.86% | 633.0c/-227.0c | 81.34%/94.57% | 84/18 307.0c | 2.75% |
| 6 | `same_side_for>=30s AND confirm_score>=0.55` | 1469.0c/1135.0c | 73.94%/98.95% | 457.0c/-403.0c | 74.43%/99.10% | 78/26 456.0c | 5.00% |
| 7 | `same_side_for>=90s AND confirm_score>=0.6` | 1208.0c/874.0c | 80.43%/97.91% | 627.0c/-233.0c | 80.37%/96.83% | 83/20 270.0c | 3.00% |
| 8 | `same_side_for>=30s AND confirm_score>=0.57` | 1305.0c/971.0c | 74.30%/98.95% | 529.0c/-331.0c | 75.34%/99.10% | 79/25 495.0c | 4.99% |
| 9 | `same_side_for>=30s AND confirm_score>=0.55 AND confirm_book>=0.55` | 1320.0c/986.0c | 75.00%/98.95% | 278.0c/-582.0c | 73.97%/99.10% | 78/26 356.0c | 3.17% |
| 10 | `same_side_for>=90s AND confirm_score>=0.55` | 1155.0c/821.0c | 78.09%/98.61% | 382.0c/-478.0c | 77.52%/98.64% | 81/23 220.0c | 0.23% |
| 11 | `same_side_for>=60s AND ask_worse<=5c AND confirm_score>=0.57` | 1052.0c/718.0c | 77.06%/97.21% | 190.0c/-670.0c | 75.38%/90.05% | 81/22 388.0c | 0.84% |
| 12 | `same_side_for>=60s AND ask_worse<=5c AND confirm_score>=0.55` | 940.0c/606.0c | 75.71%/97.56% | 137.0c/-723.0c | 74.38%/91.86% | 79/24 307.0c | 0.85% |
| 13 | `same_side_for>=60s AND ask_worse<=10c AND confirm_score>=0.55` | 908.0c/574.0c | 75.70%/98.95% | 159.0c/-701.0c | 74.30%/96.83% | 80/24 309.0c | 0.26% |
| 14 | `same_side_for>=120s AND ask_worse<=10c AND confirm_score>=0.6` | 734.0c/400.0c | 80.00%/92.33% | 320.0c/-540.0c | 78.80%/83.26% | 79/19 239.0c | 2.64% |
| 15 | `same_side_for>=60s AND ask_worse<=10c AND confirm_score>=0.57` | 957.0c/623.0c | 76.68%/98.61% | 94.0c/-766.0c | 74.53%/95.93% | 82/22 419.0c | 0.55% |

## 03:45 Loss Market Behavior

| confirmation | selected side | entry | ask | outcome | win |
|---|---|---|---:|---|---|
| `same_side_for>=60s AND confirm_score>=0.6` | yes | `2026-05-03 03:33:03.553000+00:00` | 67.0c | yes | True |
| `same_side_for>=60s AND confirm_score>=0.57` | yes | `2026-05-03 03:33:03.553000+00:00` | 67.0c | yes | True |
| `same_side_for>=60s AND confirm_score>=0.55` | yes | `2026-05-03 03:33:03.553000+00:00` | 67.0c | yes | True |
| `same_side_for>=30s AND confirm_score>=0.6` | yes | `2026-05-03 03:32:33.516000+00:00` | 64.0c | yes | True |
| `same_side_for>=120s AND confirm_score>=0.6` | yes | `2026-05-03 03:34:03.629000+00:00` | 84.0c | yes | True |
| `same_side_for>=30s AND confirm_score>=0.55` | yes | `2026-05-03 03:32:33.516000+00:00` | 64.0c | yes | True |
| `same_side_for>=90s AND confirm_score>=0.6` | yes | `2026-05-03 03:33:33.586000+00:00` | 71.0c | yes | True |
| `same_side_for>=30s AND confirm_score>=0.57` | yes | `2026-05-03 03:32:33.516000+00:00` | 64.0c | yes | True |

## Read

- Best diagnostic confirmation row is `same_side_for>=60s AND confirm_score>=0.6` with current/v21 deltas 1158.0c/-66.0c.
- Same-side confirmation may be a real path-physics prior, but it is post-loss research and needs its own forward lock.
