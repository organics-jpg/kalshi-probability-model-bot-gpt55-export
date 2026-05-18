# Cross-Dataset Fee-Aware Profit Frontier

Generated UTC: `20260504_131357Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Objective is fee-aware held-to-settlement profit while keeping at least 80% recurring-market coverage on both datasets.
- The same policy grid is evaluated on current heartbeat data and independent v21 passive websocket data.
- P&L uses one contract, logged ask as entry cost, and the local entry-only Kalshi taker fee estimate; no exit trade is assumed.

## Data

- Current intervals: 316; rows: 36410
- V21 intervals: 221; rows: 6554
- Policies scanned: 2880
- Both-dataset 80%-coverage policies: 2068
- Both-dataset 80%-coverage policies profitable on validation and holdout splits: 352
- Both-dataset 80%-coverage policies profitable on all splits: 4
- Nondegenerate both-dataset 80%-coverage policies: 654
- Fee model: `entry-only local Kalshi taker estimate: ceil(7*contracts*p*(100-p)/10000), min 1c`

## Top Both-Dataset 80%-Coverage Profit Policies

| rank | policy | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS ROI | median ask | ask=100 | oos profitable |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `choose=book_p_side; book_p_side>=0.8; ask<=95; sec_to_close>=120` | 167.0c/0.65% | 86.05%/95.25% | 299.0c/1.79% | 88.54%/86.88% | 0.95% | 85.0c | 0 | True |
| 2 | `choose=book_p_side; book_p_side>=0.8; ask<=95; sec_to_close>=120; spread<=4` | 167.0c/0.65% | 86.05%/95.25% | 299.0c/1.79% | 88.54%/86.88% | 0.95% | 85.0c | 0 | True |
| 3 | `choose=book_p_side; book_p_side>=0.8; ask<=90; sec_to_close>=0` | 240.0c/0.94% | 86.05%/95.25% | 348.0c/2.21% | 87.98%/82.81% | 0.41% | 84.0c | 0 | True |
| 4 | `choose=book_p_side; book_p_side>=0.8; ask<=90; sec_to_close>=0; spread<=4` | 240.0c/0.94% | 86.05%/95.25% | 348.0c/2.21% | 87.98%/82.81% | 0.41% | 84.0c | 0 | True |
| 5 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120` | 1292.0c/5.77% | 75.72%/99.05% | 534.0c/3.43% | 73.85%/98.64% | 2.59% | 69.0c | 0 | True |
| 6 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120; spread<=4` | 1292.0c/5.77% | 75.72%/99.05% | 534.0c/3.43% | 73.85%/98.64% | 2.59% | 69.0c | 0 | True |
| 7 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0` | 1292.0c/5.77% | 75.72%/99.05% | 534.0c/3.43% | 73.85%/98.64% | 2.59% | 69.0c | 0 | True |
| 8 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120; brownian15>=0.55_and_brownian30>=0.55` | 1276.0c/5.69% | 75.72%/99.05% | 534.0c/3.43% | 73.85%/98.64% | 2.59% | 69.0c | 0 | True |
| 9 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=60` | 1292.0c/5.77% | 75.72%/99.05% | 443.0c/2.83% | 73.52%/99.10% | 2.59% | 69.0c | 0 | True |
| 10 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=60; spread<=4` | 1292.0c/5.77% | 75.72%/99.05% | 443.0c/2.83% | 73.52%/99.10% | 2.59% | 69.0c | 0 | True |
| 11 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=60; margin_rv15>=0` | 1292.0c/5.77% | 75.72%/99.05% | 443.0c/2.83% | 73.52%/99.10% | 2.59% | 69.0c | 0 | True |
| 12 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=60; brownian15>=0.55_and_brownian30>=0.55` | 1276.0c/5.69% | 75.72%/99.05% | 443.0c/2.83% | 73.52%/99.10% | 2.59% | 69.0c | 0 | True |
| 13 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=90; sec_to_close>=120` | 1284.0c/5.78% | 75.56%/98.42% | 514.0c/3.36% | 73.49%/97.29% | 2.58% | 69.0c | 0 | True |
| 14 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=90; sec_to_close>=120; spread<=4` | 1284.0c/5.78% | 75.56%/98.42% | 514.0c/3.36% | 73.49%/97.29% | 2.58% | 69.0c | 0 | True |
| 15 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=90; sec_to_close>=120; margin_rv15>=0` | 1284.0c/5.78% | 75.56%/98.42% | 514.0c/3.36% | 73.49%/97.29% | 2.58% | 69.0c | 0 | True |

## Top Nondegenerate 80%-Coverage Profit Policies

| rank | policy | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS ROI | median ask | ask=100 | oos profitable |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `choose=book_p_side; book_p_side>=0.8; ask<=95; sec_to_close>=120` | 167.0c/0.65% | 86.05%/95.25% | 299.0c/1.79% | 88.54%/86.88% | 0.95% | 85.0c | 0 | True |
| 2 | `choose=book_p_side; book_p_side>=0.8; ask<=95; sec_to_close>=120; spread<=4` | 167.0c/0.65% | 86.05%/95.25% | 299.0c/1.79% | 88.54%/86.88% | 0.95% | 85.0c | 0 | True |
| 3 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120` | 1292.0c/5.77% | 75.72%/99.05% | 534.0c/3.43% | 73.85%/98.64% | 2.59% | 69.0c | 0 | True |
| 4 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120; spread<=4` | 1292.0c/5.77% | 75.72%/99.05% | 534.0c/3.43% | 73.85%/98.64% | 2.59% | 69.0c | 0 | True |
| 5 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0` | 1292.0c/5.77% | 75.72%/99.05% | 534.0c/3.43% | 73.85%/98.64% | 2.59% | 69.0c | 0 | True |
| 6 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120; brownian15>=0.55_and_brownian30>=0.55` | 1276.0c/5.69% | 75.72%/99.05% | 534.0c/3.43% | 73.85%/98.64% | 2.59% | 69.0c | 0 | True |
| 7 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=60` | 1292.0c/5.77% | 75.72%/99.05% | 443.0c/2.83% | 73.52%/99.10% | 2.59% | 69.0c | 0 | True |
| 8 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=60; spread<=4` | 1292.0c/5.77% | 75.72%/99.05% | 443.0c/2.83% | 73.52%/99.10% | 2.59% | 69.0c | 0 | True |
| 9 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=60; margin_rv15>=0` | 1292.0c/5.77% | 75.72%/99.05% | 443.0c/2.83% | 73.52%/99.10% | 2.59% | 69.0c | 0 | True |
| 10 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=60; brownian15>=0.55_and_brownian30>=0.55` | 1276.0c/5.69% | 75.72%/99.05% | 443.0c/2.83% | 73.52%/99.10% | 2.59% | 69.0c | 0 | True |
| 11 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=90; sec_to_close>=120` | 1284.0c/5.78% | 75.56%/98.42% | 514.0c/3.36% | 73.49%/97.29% | 2.58% | 69.0c | 0 | True |
| 12 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=90; sec_to_close>=120; spread<=4` | 1284.0c/5.78% | 75.56%/98.42% | 514.0c/3.36% | 73.49%/97.29% | 2.58% | 69.0c | 0 | True |
| 13 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=90; sec_to_close>=120; margin_rv15>=0` | 1284.0c/5.78% | 75.56%/98.42% | 514.0c/3.36% | 73.49%/97.29% | 2.58% | 69.0c | 0 | True |
| 14 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=90; sec_to_close>=120; brownian15>=0.55_and_brownian30>=0.55` | 1268.0c/5.70% | 75.56%/98.42% | 514.0c/3.36% | 73.49%/97.29% | 2.58% | 69.0c | 0 | True |
| 15 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=90; sec_to_close>=60` | 1284.0c/5.78% | 75.56%/98.42% | 423.0c/2.75% | 73.15%/97.74% | 2.58% | 69.0c | 0 | True |

## Top 80%-Coverage Policies Profitable On Validation And Holdout

| rank | policy | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS ROI | median ask | ask=100 | oos profitable |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `choose=book_p_side; book_p_side>=0.8; ask<=95; sec_to_close>=120` | 167.0c/0.65% | 86.05%/95.25% | 299.0c/1.79% | 88.54%/86.88% | 0.95% | 85.0c | 0 | True |
| 2 | `choose=book_p_side; book_p_side>=0.8; ask<=95; sec_to_close>=120; spread<=4` | 167.0c/0.65% | 86.05%/95.25% | 299.0c/1.79% | 88.54%/86.88% | 0.95% | 85.0c | 0 | True |
| 3 | `choose=book_p_side; book_p_side>=0.8; ask<=90; sec_to_close>=0` | 240.0c/0.94% | 86.05%/95.25% | 348.0c/2.21% | 87.98%/82.81% | 0.41% | 84.0c | 0 | True |
| 4 | `choose=book_p_side; book_p_side>=0.8; ask<=90; sec_to_close>=0; spread<=4` | 240.0c/0.94% | 86.05%/95.25% | 348.0c/2.21% | 87.98%/82.81% | 0.41% | 84.0c | 0 | True |
| 5 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120` | 1292.0c/5.77% | 75.72%/99.05% | 534.0c/3.43% | 73.85%/98.64% | 2.59% | 69.0c | 0 | True |
| 6 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120; spread<=4` | 1292.0c/5.77% | 75.72%/99.05% | 534.0c/3.43% | 73.85%/98.64% | 2.59% | 69.0c | 0 | True |
| 7 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0` | 1292.0c/5.77% | 75.72%/99.05% | 534.0c/3.43% | 73.85%/98.64% | 2.59% | 69.0c | 0 | True |
| 8 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=120; brownian15>=0.55_and_brownian30>=0.55` | 1276.0c/5.69% | 75.72%/99.05% | 534.0c/3.43% | 73.85%/98.64% | 2.59% | 69.0c | 0 | True |
| 9 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=60` | 1292.0c/5.77% | 75.72%/99.05% | 443.0c/2.83% | 73.52%/99.10% | 2.59% | 69.0c | 0 | True |
| 10 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=60; spread<=4` | 1292.0c/5.77% | 75.72%/99.05% | 443.0c/2.83% | 73.52%/99.10% | 2.59% | 69.0c | 0 | True |
| 11 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=60; margin_rv15>=0` | 1292.0c/5.77% | 75.72%/99.05% | 443.0c/2.83% | 73.52%/99.10% | 2.59% | 69.0c | 0 | True |
| 12 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec_to_close>=60; brownian15>=0.55_and_brownian30>=0.55` | 1276.0c/5.69% | 75.72%/99.05% | 443.0c/2.83% | 73.52%/99.10% | 2.59% | 69.0c | 0 | True |
| 13 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=90; sec_to_close>=120` | 1284.0c/5.78% | 75.56%/98.42% | 514.0c/3.36% | 73.49%/97.29% | 2.58% | 69.0c | 0 | True |
| 14 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=90; sec_to_close>=120; spread<=4` | 1284.0c/5.78% | 75.56%/98.42% | 514.0c/3.36% | 73.49%/97.29% | 2.58% | 69.0c | 0 | True |
| 15 | `choose=score_min_book_rv15; score_min_book_rv15>=0.6; ask<=90; sec_to_close>=120; margin_rv15>=0` | 1284.0c/5.78% | 75.56%/98.42% | 514.0c/3.36% | 73.49%/97.29% | 2.58% | 69.0c | 0 | True |

## Read

- Best coverage-valid profit row: `choose=book_p_side; book_p_side>=0.8; ask<=95; sec_to_close>=120`.
- Current all split: 167.0c net, 0.65% ROI, 86.05% accuracy at 95.25% coverage.
- V21 all split: 299.0c net, 1.79% ROI, 88.54% accuracy at 86.88% coverage.
- Minimum validation/holdout ROI across both datasets is 0.95%; max median ask is 85.0c.
- This is a profit-frontier falsification scan, not a live-trading promotion lock; fresh post-lock sample size remains required.
