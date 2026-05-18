# Book V2 Regime Switch Scan

Generated UTC: `20260504_052234Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests high-coverage switches between book-margin anchors and Brownian/score references on current and v21 ledgers.
- Pair-dependent rules are diagnostic only. Forward candidates must be physically interpretable and causal.
- Anchor-only and reference-only switch rows use executable within-market semantics; reference-conditioned false fallbacks cannot claim earlier anchor prices.
- Best causal rows must improve both datasets individually; combined positive delta is not enough.

## Summary

- Rules scanned: 1122
- Both-dataset 80% coverage rules: 706
- Both-dataset OOS-positive coverage rules: 583
- Causal-class positive coverage rules: 10

## Top Rows

| rank | rule | class | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |
|---:|---|---|---:|---:|---:|---:|
| 1 | `book_margin_switch_to_score_min60_gap020_if_side_disagree` | pair_diagnostic | 1274.0c/381.0c | 2300.0c/76.14%/99.30% | 806.0c/73.52%/99.10% | 7.74% |
| 2 | `book_margin_switch_to_score_min60_gap020_if_anchor_earlier_side_disagree` | pair_diagnostic | 1274.0c/381.0c | 2300.0c/76.14%/99.30% | 806.0c/73.52%/99.10% | 7.74% |
| 3 | `book_margin_switch_to_score_min60_if_side_disagree` | pair_diagnostic | 1156.0c/381.0c | 2182.0c/75.79%/99.30% | 806.0c/73.52%/99.10% | 7.74% |
| 4 | `book_margin_switch_to_score_min60_if_anchor_earlier_side_disagree` | pair_diagnostic | 1156.0c/381.0c | 2182.0c/75.79%/99.30% | 806.0c/73.52%/99.10% | 7.74% |
| 5 | `book_margin_early_switch_to_score_min60_gap020_if_side_disagree` | pair_diagnostic | 1182.0c/128.0c | 2238.0c/76.14%/99.30% | 847.0c/73.85%/98.64% | 7.74% |
| 6 | `book_margin_early_switch_to_score_min60_gap020_if_anchor_earlier_side_disagree` | pair_diagnostic | 1182.0c/128.0c | 2238.0c/76.14%/99.30% | 847.0c/73.85%/98.64% | 7.74% |
| 7 | `book_margin_early_switch_to_score_min60_if_side_disagree` | pair_diagnostic | 1064.0c/128.0c | 2120.0c/75.79%/99.30% | 847.0c/73.85%/98.64% | 7.74% |
| 8 | `book_margin_early_switch_to_score_min60_if_anchor_earlier_side_disagree` | pair_diagnostic | 1064.0c/128.0c | 2120.0c/75.79%/99.30% | 847.0c/73.85%/98.64% | 7.74% |
| 9 | `book_margin_switch_to_frontier_v2_if_anchor_adverse_move_15m<=10` | anchor_only | -366.0c/1358.0c | 660.0c/66.32%/99.30% | 1783.0c/72.15%/99.10% | 2.93% |
| 10 | `book_margin_switch_to_frontier_v2_if_anchor_ask_cents>=70` | anchor_only | -132.0c/1110.0c | 894.0c/69.47%/99.30% | 1535.0c/73.06%/99.10% | 2.88% |
| 11 | `book_margin_early_switch_to_frontier_v2_if_anchor_ask_cents>=70` | anchor_only | -198.0c/1082.0c | 858.0c/69.12%/99.30% | 1801.0c/73.97%/99.10% | 1.44% |
| 12 | `book_margin_switch_to_frontier_v2_if_anchor_entry_hour_utc==04` | anchor_only | 569.0c/284.0c | 1595.0c/72.98%/99.30% | 709.0c/72.15%/99.10% | 7.82% |
| 13 | `book_margin_switch_to_frontier_v2_if_anchor_book_p_side>=0.7` | anchor_only | -150.0c/928.0c | 876.0c/69.47%/99.30% | 1353.0c/72.60%/99.10% | 2.93% |
| 14 | `book_margin_early_switch_to_frontier_v2_if_anchor_book_p_side>=0.7` | anchor_only | -216.0c/900.0c | 840.0c/69.12%/99.30% | 1619.0c/73.52%/99.10% | 0.98% |
| 15 | `book_margin_switch_to_frontier_v2_if_reference_ask_cents>=60` | reference_only | 193.0c/489.0c | 1219.0c/72.36%/95.82% | 914.0c/73.15%/97.74% | 3.54% |
| 16 | `book_margin_early_switch_to_frontier_v2_if_reference_ask_cents>=60` | reference_only | 193.0c/489.0c | 1249.0c/72.66%/93.03% | 1208.0c/74.63%/92.76% | 3.54% |
| 17 | `book_margin_early_switch_to_frontier_v2_if_anchor_entry_hour_utc==04` | anchor_only | 398.0c/241.0c | 1454.0c/72.28%/99.30% | 960.0c/72.60%/99.10% | 5.93% |
| 18 | `book_margin_early_switch_to_frontier_v2_if_anchor_adverse_move_15m<=10` | anchor_only | -492.0c/1085.0c | 564.0c/65.96%/99.30% | 1804.0c/72.15%/99.10% | 2.93% |
| 19 | `book_margin_early_switch_to_score_min60_gap020_if_reference_adverse_move_15m<=50` | reference_only | 565.0c/1.0c | 1621.0c/77.87%/85.02% | 720.0c/74.87%/90.05% | 2.07% |
| 20 | `book_margin_switch_to_score_min60_gap020_if_reference_adverse_move_15m<=50` | reference_only | 503.0c/42.0c | 1529.0c/77.38%/87.80% | 467.0c/73.68%/94.57% | 2.07% |
| 21 | `book_margin_switch_to_frontier_v2_if_anchor_abs_book_rv15_gap<=0.05` | anchor_only | -42.0c/585.0c | 984.0c/69.12%/99.30% | 1010.0c/68.95%/99.10% | 1.27% |
| 22 | `book_margin_switch_to_frontier_v2_if_anchor_entry_hour_utc==08` | anchor_only | 263.0c/270.0c | 1289.0c/71.93%/99.30% | 695.0c/72.15%/99.10% | 5.15% |
| 23 | `book_margin_early_switch_to_score_min60_gap020_if_reference_adverse_move_15m<=75` | reference_only | 535.0c/-10.0c | 1591.0c/77.56%/88.50% | 709.0c/74.75%/91.40% | 2.07% |
| 24 | `book_margin_switch_to_score_min60_gap020_if_reference_adverse_move_15m<=75` | reference_only | 473.0c/31.0c | 1499.0c/77.10%/91.29% | 456.0c/73.58%/95.93% | 2.07% |
| 25 | `book_margin_early_switch_to_score_min60_gap020_if_reference_adverse_move_15m<=100` | reference_only | 503.0c/-11.0c | 1559.0c/77.31%/90.59% | 708.0c/74.63%/92.76% | 3.20% |

## Best Causal-Class Rows

| rank | rule | class | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |
|---:|---|---|---:|---:|---:|---:|
| 1 | `book_margin_switch_to_frontier_v2_if_anchor_entry_hour_utc==04` | anchor_only | 569.0c/284.0c | 1595.0c/72.98%/99.30% | 709.0c/72.15%/99.10% | 7.82% |
| 2 | `book_margin_switch_to_frontier_v2_if_reference_ask_cents>=60` | reference_only | 193.0c/489.0c | 1219.0c/72.36%/95.82% | 914.0c/73.15%/97.74% | 3.54% |
| 3 | `book_margin_early_switch_to_frontier_v2_if_reference_ask_cents>=60` | reference_only | 193.0c/489.0c | 1249.0c/72.66%/93.03% | 1208.0c/74.63%/92.76% | 3.54% |
| 4 | `book_margin_early_switch_to_frontier_v2_if_anchor_entry_hour_utc==04` | anchor_only | 398.0c/241.0c | 1454.0c/72.28%/99.30% | 960.0c/72.60%/99.10% | 5.93% |
| 5 | `book_margin_early_switch_to_score_min60_gap020_if_reference_adverse_move_15m<=50` | reference_only | 565.0c/1.0c | 1621.0c/77.87%/85.02% | 720.0c/74.87%/90.05% | 2.07% |
| 6 | `book_margin_switch_to_score_min60_gap020_if_reference_adverse_move_15m<=50` | reference_only | 503.0c/42.0c | 1529.0c/77.38%/87.80% | 467.0c/73.68%/94.57% | 2.07% |
| 7 | `book_margin_switch_to_frontier_v2_if_anchor_entry_hour_utc==08` | anchor_only | 263.0c/270.0c | 1289.0c/71.93%/99.30% | 695.0c/72.15%/99.10% | 5.15% |
| 8 | `book_margin_switch_to_score_min60_gap020_if_reference_adverse_move_15m<=75` | reference_only | 473.0c/31.0c | 1499.0c/77.10%/91.29% | 456.0c/73.58%/95.93% | 2.07% |
| 9 | `book_margin_early_switch_to_score_min60_gap020_if_reference_abs_book_rv15_gap<=0.15` | reference_only | 421.0c/68.0c | 1477.0c/76.67%/94.08% | 787.0c/75.00%/94.12% | 0.32% |
| 10 | `book_margin_switch_to_score_min60_gap020_if_anchor_abs_book_rv15_gap<=0.1` | anchor_only | 383.0c/91.0c | 1409.0c/75.79%/99.30% | 516.0c/73.52%/99.10% | 4.76% |

## Read

- Best coverage-valid rule: `book_margin_switch_to_score_min60_gap020_if_side_disagree` with current/v21 delta 1274.0c/381.0c.
- The top rule is pair-dependent, so it explains the failure mode but is not directly forward-lockable.
- Best causal-class candidate is `book_margin_switch_to_frontier_v2_if_anchor_entry_hour_utc==04`, but it still needs strict forward registration before use.
- Goal remains strict live sample size plus >=75-80% recurring-market coverage, not retrospective scan rank.
