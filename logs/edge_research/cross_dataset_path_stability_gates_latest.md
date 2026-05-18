# Cross-Dataset Path-Stability Gates

Generated UTC: `20260502_210203Z`

## Scope

- Research-only probe; no orders are submitted and no bot files are modified.
- Starts from economical interval policies and requires causal pre-entry path stability.
- If a heartbeat fails the stability gate, the policy can wait for a later heartbeat in the same recurring market.
- Tests the same base policies and gates on current live heartbeat data and independent v21 passive websocket data.

## Data

- Current intervals: 166; rows: 19190
- V21 intervals: 221; rows: 6554
- Base policies: 4
- Stability gate combinations: 805
- Candidate rows evaluated: 3220
- Both-dataset 80%-coverage rows: 577
- Both-dataset target passes: 0
- Both-dataset Wilson passes: 0

## Top Shared Path-Stability Gates

| rank | base policy | stability gates | current acc/cov | v21 acc/cov | min split acc | min split cov | max median ask | target |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` | `adverse_move_5m<=0` | 88.00%/90.36% | 87.30%/85.52% | 85.00% | 82.22% | 87.0 | False |
| 2 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` | `book_drawdown_4<=0.05 AND adverse_move_5m<=0` | 88.00%/90.36% | 87.23%/85.07% | 85.00% | 82.22% | 87.0 | False |
| 3 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` | `book_drawdown_4<=0.08 AND adverse_move_5m<=0` | 88.00%/90.36% | 87.30%/85.52% | 85.00% | 82.22% | 87.0 | False |
| 4 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` | `book_drawdown_4<=0.1 AND adverse_move_5m<=0` | 88.00%/90.36% | 87.30%/85.52% | 85.00% | 82.22% | 87.0 | False |
| 5 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` | `book_drawdown_8<=0.05 AND adverse_move_5m<=0` | 88.59%/89.76% | 87.23%/85.07% | 85.00% | 82.22% | 87.0 | False |
| 6 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` | `book_drawdown_8<=0.08 AND adverse_move_5m<=0` | 88.00%/90.36% | 87.30%/85.52% | 85.00% | 82.22% | 87.0 | False |
| 7 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` | `book_drawdown_8<=0.12 AND adverse_move_5m<=0` | 88.00%/90.36% | 87.30%/85.52% | 85.00% | 82.22% | 87.0 | False |
| 8 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` | `book_drawdown_8<=0.16 AND adverse_move_5m<=0` | 88.00%/90.36% | 87.30%/85.52% | 85.00% | 82.22% | 87.0 | False |
| 9 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` | `book_delta_4>=-0.05 AND adverse_move_5m<=0` | 88.00%/90.36% | 87.10%/84.16% | 85.00% | 82.22% | 88.0 | False |
| 10 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` | `book_delta_4>=0 AND adverse_move_5m<=0` | 88.67%/90.36% | 87.10%/84.16% | 85.00% | 82.22% | 88.0 | False |
| 11 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` | `book_delta_4>=0.05 AND adverse_move_5m<=0` | 88.59%/89.76% | 87.10%/84.16% | 85.00% | 82.22% | 88.0 | False |
| 12 | `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60` | `book_drawdown_4<=0.03 AND adverse_move_5m<=0` | 88.00%/90.36% | 87.17%/84.62% | 84.62% | 82.22% | 87.0 | False |
| 13 | `choose=book_p_side; book_p_side>=0.8; ask<=95; sec_to_close>=60; adverse15<=10_or_margin_rv15>=0.5` | `rv_ratio_15_30<=1.25` | 86.71%/95.18% | 87.37%/89.59% | 84.04% | 86.67% | 85.0 | False |
| 14 | `choose=book_p_side; book_p_side>=0.8; ask<=95; sec_to_close>=60; adverse15<=10_or_margin_rv15>=0.5` | `book_drawdown_4<=0.03 AND rv_ratio_15_30<=1.25` | 86.71%/95.18% | 87.31%/89.14% | 84.04% | 86.67% | 85.0 | False |
| 15 | `choose=book_p_side; book_p_side>=0.8; ask<=95; sec_to_close>=60; adverse15<=10_or_margin_rv15>=0.5` | `book_drawdown_4<=0.05 AND rv_ratio_15_30<=1.25` | 86.71%/95.18% | 87.31%/89.14% | 84.04% | 86.67% | 85.0 | False |

## Read

- No shared path-stability gate cleared the 95% accuracy / 80% recurring-market target.
- Best shared 80%-coverage row had current 88.00%/90.36%, v21 87.30%/85.52%, and max median ask 87.0c.
- This rejects simple pre-entry path persistence as a standalone fix if target-pass rows remain zero.
