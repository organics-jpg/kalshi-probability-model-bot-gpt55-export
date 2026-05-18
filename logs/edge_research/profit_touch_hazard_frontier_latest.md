# Touch-Hazard Profit Frontier

Generated UTC: `20260504_053420Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Adds first-passage-style touch hazard to terminal Brownian/book scores.
- Objective is fee-aware held-to-settlement profit while keeping at least 80% recurring-market coverage on both datasets.

## Data

- Current intervals: 287; rows: 33106
- V21 intervals: 221; rows: 6554
- Policies scanned: 1440
- Both-dataset 80%-coverage policies: 1328
- Both-dataset 80%-coverage policies profitable on validation and holdout splits: 180
- Both-dataset 80%-coverage policies profitable on all splits: 16
- Nondegenerate both-dataset 80%-coverage policies: 848

## Top Both-Dataset 80%-Coverage Touch-Hazard Policies

| rank | policy | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS ROI | median ask | ask=100 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=touch_loss15<=0.80` | 887.0c/4.55% | 75.00%/94.77% | 804.0c/5.55% | 75.00%/92.31% | 0.10% | 69.0c | 0 |
| 2 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=120; gate=touch_loss15<=0.80` | 887.0c/4.55% | 75.00%/94.77% | 804.0c/5.55% | 75.00%/92.31% | 0.10% | 69.0c | 0 |
| 3 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=60; gate=touch_loss15<=0.80` | 887.0c/4.55% | 75.00%/94.77% | 804.0c/5.55% | 75.00%/92.31% | 0.10% | 69.0c | 0 |
| 4 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=120; gate=touch_loss15<=0.80` | 887.0c/4.55% | 75.00%/94.77% | 804.0c/5.55% | 75.00%/92.31% | 0.10% | 69.0c | 0 |
| 5 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=touch_loss15<=0.85_or_adverse15<=10` | 901.0c/4.60% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 6 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=120; gate=touch_loss15<=0.85_or_adverse15<=10` | 901.0c/4.60% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 7 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=60; gate=touch_loss15<=0.85_or_adverse15<=10` | 901.0c/4.60% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 8 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=120; gate=touch_loss15<=0.85_or_adverse15<=10` | 901.0c/4.60% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 9 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=none` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 10 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=touch_loss15<=0.90` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 11 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=120; gate=none` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 12 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=120; gate=touch_loss15<=0.90` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 13 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=60; gate=none` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 14 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=60; gate=touch_loss15<=0.90` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 15 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=120; gate=none` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |

## Top Nondegenerate 80%-Coverage Touch-Hazard Policies

| rank | policy | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS ROI | median ask | ask=100 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=touch_loss15<=0.80` | 887.0c/4.55% | 75.00%/94.77% | 804.0c/5.55% | 75.00%/92.31% | 0.10% | 69.0c | 0 |
| 2 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=120; gate=touch_loss15<=0.80` | 887.0c/4.55% | 75.00%/94.77% | 804.0c/5.55% | 75.00%/92.31% | 0.10% | 69.0c | 0 |
| 3 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=60; gate=touch_loss15<=0.80` | 887.0c/4.55% | 75.00%/94.77% | 804.0c/5.55% | 75.00%/92.31% | 0.10% | 69.0c | 0 |
| 4 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=120; gate=touch_loss15<=0.80` | 887.0c/4.55% | 75.00%/94.77% | 804.0c/5.55% | 75.00%/92.31% | 0.10% | 69.0c | 0 |
| 5 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=touch_loss15<=0.85_or_adverse15<=10` | 901.0c/4.60% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 6 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=120; gate=touch_loss15<=0.85_or_adverse15<=10` | 901.0c/4.60% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 7 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=60; gate=touch_loss15<=0.85_or_adverse15<=10` | 901.0c/4.60% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 8 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=120; gate=touch_loss15<=0.85_or_adverse15<=10` | 901.0c/4.60% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 9 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=none` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 10 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=touch_loss15<=0.90` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 11 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=120; gate=none` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 12 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=120; gate=touch_loss15<=0.90` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 13 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=60; gate=none` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 14 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=60; gate=touch_loss15<=0.90` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 15 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=120; gate=none` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |

## Top 80%-Coverage Policies Profitable On Validation And Holdout

| rank | policy | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS ROI | median ask | ask=100 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=touch_loss15<=0.80` | 887.0c/4.55% | 75.00%/94.77% | 804.0c/5.55% | 75.00%/92.31% | 0.10% | 69.0c | 0 |
| 2 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=120; gate=touch_loss15<=0.80` | 887.0c/4.55% | 75.00%/94.77% | 804.0c/5.55% | 75.00%/92.31% | 0.10% | 69.0c | 0 |
| 3 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=60; gate=touch_loss15<=0.80` | 887.0c/4.55% | 75.00%/94.77% | 804.0c/5.55% | 75.00%/92.31% | 0.10% | 69.0c | 0 |
| 4 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=120; gate=touch_loss15<=0.80` | 887.0c/4.55% | 75.00%/94.77% | 804.0c/5.55% | 75.00%/92.31% | 0.10% | 69.0c | 0 |
| 5 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=touch_loss15<=0.85_or_adverse15<=10` | 901.0c/4.60% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 6 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=120; gate=touch_loss15<=0.85_or_adverse15<=10` | 901.0c/4.60% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 7 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=60; gate=touch_loss15<=0.85_or_adverse15<=10` | 901.0c/4.60% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 8 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=120; gate=touch_loss15<=0.85_or_adverse15<=10` | 901.0c/4.60% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 9 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=none` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 10 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=touch_loss15<=0.90` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 11 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=120; gate=none` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 12 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=120; gate=touch_loss15<=0.90` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 13 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=60; gate=none` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 14 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=60; gate=touch_loss15<=0.90` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |
| 15 | `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 50<=ask<=80; sec>=120; gate=none` | 897.0c/4.58% | 75.09%/95.12% | 804.0c/5.55% | 75.00%/92.31% | 0.05% | 69.0c | 0 |

## Read

- Best coverage-valid touch-hazard row: `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=touch_loss15<=0.80`.
- Current all split: 887.0c net, 4.55% ROI, 75.00% accuracy at 94.77% coverage.
- V21 all split: 804.0c net, 5.55% ROI, 75.00% accuracy at 92.31% coverage.
- Minimum validation/holdout ROI across both datasets is 0.10%; max median ask is 69.0c.
- Best all-split-positive touch-hazard row: `choose=hazard_discounted_mean_15; hazard_discounted_mean_15>=0.45; 0<=ask<=80; sec>=60; gate=touch_loss15<=0.80`.
- Touch hazard is a physics falsification prior, not a live-trading promotion lock; fresh post-lock sample size remains required.
