# V2 Consensus Override Scan

Generated UTC: `20260504_022312Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Keeps Brownian v2 as default and flips only at the same heartbeat when a consensus chooser disagrees.
- This avoids late-switch optionality and preserves the recurring-market coverage unit.

## Baseline

- Current v2 baseline: 395.0c
- V21 v2 baseline: 1283.0c

## Summary

- Hybrid policies scanned: 64
- Both-dataset 80% coverage policies: 64
- Both-dataset OOS-positive policies: 4

## Top Rows

| rank | policy | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |
|---:|---|---:|---:|---:|---:|
| 1 | `v2_default_then_book_p_side; book_p_side>=0.55; ask<=90; sec>=120; disagree_only; fallback` | 104.0c/-114.0c | 499.0c/64.00%/99.28% | 1169.0c/68.04%/99.10% | 2.10% |
| 2 | `v2_default_then_book_p_side; book_p_side>=0.55; ask<=95; sec>=120; disagree_only; fallback` | 104.0c/-114.0c | 499.0c/64.00%/99.28% | 1169.0c/68.04%/99.10% | 2.10% |
| 3 | `v2_default_then_book_p_side; book_p_side>=0.55; ask<=90; sec>=120; disagree_only` | 3.0c/-120.0c | 398.0c/64.73%/99.28% | 1163.0c/68.49%/99.10% | 0.68% |
| 4 | `v2_default_then_book_p_side; book_p_side>=0.55; ask<=95; sec>=120; disagree_only` | 3.0c/-120.0c | 398.0c/64.73%/99.28% | 1163.0c/68.49%/99.10% | 0.68% |
| 5 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.55; ask<=90; sec>=120; disagree_only` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 6 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.55; ask<=90; sec>=120; disagree_only; fallback` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 7 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.55; ask<=95; sec>=120; disagree_only` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 8 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.55; ask<=95; sec>=120; disagree_only; fallback` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 9 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.6; ask<=90; sec>=120; disagree_only` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 10 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.6; ask<=90; sec>=120; disagree_only; fallback` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 11 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec>=120; disagree_only` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 12 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.6; ask<=95; sec>=120; disagree_only; fallback` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 13 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.65; ask<=90; sec>=120; disagree_only` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 14 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.65; ask<=90; sec>=120; disagree_only; fallback` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 15 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.65; ask<=95; sec>=120; disagree_only` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 16 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.65; ask<=95; sec>=120; disagree_only; fallback` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 17 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.7; ask<=90; sec>=120; disagree_only` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 18 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.7; ask<=90; sec>=120; disagree_only; fallback` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 19 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.7; ask<=95; sec>=120; disagree_only` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |
| 20 | `v2_default_then_score_min_book_rv15; score_min_book_rv15>=0.7; ask<=95; sec>=120; disagree_only; fallback` | 0.0c/0.0c | 395.0c/64.00%/99.28% | 1283.0c/68.04%/99.10% | -3.85% |

## Read

- Best hybrid row: `v2_default_then_book_p_side; book_p_side>=0.55; ask<=90; sec>=120; disagree_only; fallback` with current/v21 delta 104.0c/-114.0c.
- No hybrid beats v2 robustly enough to lock.
