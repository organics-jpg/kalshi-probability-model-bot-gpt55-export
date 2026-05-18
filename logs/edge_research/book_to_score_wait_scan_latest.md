# Book To Score Wait Scan

Generated UTC: `20260504_023644Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests causal rules that decide from the first book-style row whether to wait for a later score-style row.
- Passing rows are diagnostic only; promotion still requires strict pre-registered live evidence.

## Summary

- Rules scanned: 390
- Both-dataset 80% coverage rules: 250
- Both-dataset OOS-positive rules: 246

## Top Rows

| rank | rule | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |
|---:|---|---:|---:|---:|---:|
| 1 | `book_margin_wait_for_score_min60_gap020_enter_ref_if_seconds_to_close>=480` | 442.0c/68.0c | 1654.0c/77.21%/98.19% | 493.0c/73.52%/99.10% | 5.13% |
| 2 | `book_margin_early_wait_for_score_min60_gap020_enter_ref_if_seconds_to_close>=360` | 442.0c/68.0c | 1684.0c/77.65%/95.31% | 787.0c/75.00%/94.12% | 4.44% |
| 3 | `book_margin_early_wait_for_score_min60_gap020_enter_ref_if_seconds_to_close>=480` | 442.0c/68.0c | 1684.0c/77.65%/95.31% | 787.0c/75.00%/94.12% | 4.44% |
| 4 | `book_margin_early_wait_for_score_min60_gap020_enter_ref_if_brownian_p_rv_15m<=0.65` | 442.0c/68.0c | 1684.0c/77.65%/95.31% | 787.0c/75.00%/94.12% | 4.44% |
| 5 | `book_margin_early_wait_for_score_min60_gap020_enter_ref_if_brownian_p_rv_15m<=0.7` | 442.0c/68.0c | 1684.0c/77.65%/95.31% | 787.0c/75.00%/94.12% | 4.44% |
| 6 | `book_margin_early_wait_for_score_min60_gap020_enter_ref_if_score_min_book_rv15<=0.65` | 442.0c/68.0c | 1684.0c/77.65%/95.31% | 787.0c/75.00%/94.12% | 4.44% |
| 7 | `book_margin_early_wait_for_score_min60_gap020_enter_ref_if_score_min_book_rv15<=0.7` | 442.0c/68.0c | 1684.0c/77.65%/95.31% | 787.0c/75.00%/94.12% | 4.44% |
| 8 | `book_margin_wait_for_score_min60_gap020_enter_ref_if_brownian_p_rv_15m<=0.65` | 380.0c/109.0c | 1592.0c/77.21%/98.19% | 534.0c/73.85%/98.64% | 4.78% |
| 9 | `book_margin_wait_for_score_min60_gap020_enter_ref_if_brownian_p_rv_15m<=0.7` | 380.0c/109.0c | 1592.0c/77.21%/98.19% | 534.0c/73.85%/98.64% | 4.78% |
| 10 | `book_margin_wait_for_score_min60_gap020_enter_ref_if_score_min_book_rv15<=0.65` | 380.0c/109.0c | 1592.0c/77.21%/98.19% | 534.0c/73.85%/98.64% | 4.78% |
| 11 | `book_margin_wait_for_score_min60_gap020_enter_ref_if_score_min_book_rv15<=0.7` | 380.0c/109.0c | 1592.0c/77.21%/98.19% | 534.0c/73.85%/98.64% | 4.78% |
| 12 | `book_margin_wait_for_score_min60_gap020_enter_ref_if_book_p_side<=0.65` | 387.0c/68.0c | 1599.0c/76.92%/98.56% | 493.0c/73.39%/98.64% | 5.56% |
| 13 | `book_margin_gap015_wait_for_score_min60_gap020_enter_ref_if_book_p_side<=0.65` | 387.0c/68.0c | 1878.0c/78.28%/88.09% | 374.0c/72.77%/96.38% | 1.33% |
| 14 | `book_margin_early_wait_for_score_min60_gap020_enter_ref_if_book_p_side<=0.65` | 425.0c/27.0c | 1667.0c/77.36%/95.67% | 746.0c/74.52%/94.12% | 5.26% |
| 15 | `book_margin_wait_for_score_min60_gap020_enter_ref_if_seconds_to_close>=360` | 400.0c/44.0c | 1612.0c/77.21%/98.19% | 469.0c/73.52%/99.10% | 4.78% |
| 16 | `book_margin_early_wait_for_score_min60_gap020_enter_ref_if_book_p_side<=0.7` | 361.0c/69.0c | 1603.0c/77.36%/95.67% | 788.0c/75.00%/94.12% | 4.54% |
| 17 | `book_margin_early_wait_for_score_min60_gap020_enter_ref_if_brownian_p_rv_15m<=0.6` | 358.0c/68.0c | 1600.0c/77.36%/95.67% | 787.0c/75.00%/94.12% | 4.44% |
| 18 | `book_margin_early_wait_for_score_min60_gap020_enter_ref_if_score_min_book_rv15<=0.6` | 358.0c/68.0c | 1600.0c/77.36%/95.67% | 787.0c/75.00%/94.12% | 4.44% |
| 19 | `book_margin_wait_for_score_min60_gap020_enter_ref_if_book_p_side<=0.7` | 299.0c/110.0c | 1511.0c/76.92%/98.56% | 535.0c/73.85%/98.64% | 4.87% |
| 20 | `book_margin_wait_for_score_min60_switch_only_if_adverse_move_15m>=100` | 148.0c/261.0c | 1360.0c/72.97%/93.50% | 686.0c/72.86%/95.02% | 1.72% |
| 21 | `book_margin_wait_for_score_min60_gap020_switch_only_if_adverse_move_15m>=100` | 148.0c/261.0c | 1360.0c/72.97%/93.50% | 686.0c/72.86%/95.02% | 1.72% |
| 22 | `book_margin_wait_for_score_min60_gap020_enter_ref_if_brownian_p_rv_15m<=0.6` | 296.0c/109.0c | 1508.0c/76.92%/98.56% | 534.0c/73.85%/98.64% | 4.78% |
| 23 | `book_margin_wait_for_score_min60_gap020_enter_ref_if_score_min_book_rv15<=0.6` | 296.0c/109.0c | 1508.0c/76.92%/98.56% | 534.0c/73.85%/98.64% | 4.78% |
| 24 | `book_margin_wait_for_score_min60_enter_ref_if_adverse_move_15m>=100` | 157.0c/233.0c | 1369.0c/73.09%/99.28% | 658.0c/72.60%/99.10% | 2.98% |
| 25 | `book_margin_wait_for_score_min60_gap020_enter_ref_if_adverse_move_15m>=100` | 157.0c/233.0c | 1369.0c/73.09%/99.28% | 658.0c/72.60%/99.10% | 2.98% |

## Read

- Best coverage-valid row: `book_margin_wait_for_score_min60_gap020_enter_ref_if_seconds_to_close>=480` with current/v21 delta 442.0c/68.0c.
- Worth forward-lock consideration only if the trigger is physically interpretable and not just a timing artifact.
