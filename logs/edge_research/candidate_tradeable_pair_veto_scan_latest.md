# Candidate Tradeable Pair-Veto Scan

Generated UTC: `20260504_035121Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests one- and two-clause physical/book vetoes on current leading high-coverage locks.
- Vetoes are applied to each lock's first selected row per market; skipped markets are not re-entered later.
- Any apparent winner still needs strict pre-resolution forward registration and sample size.

## Summary

- Rules scanned: 822
- Both-dataset 80% coverage rules: 257
- Both-dataset OOS-positive rules: 257
- Diagnostic pass rules: 0

## Top Rows

| rank | rule | diagnostic | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor | block pass | worst block |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `book_margin: seconds_to_close>=480 AND adverse_move_15m<=100` | False | 145.0c/486.0c | 1282.0c/72.80%/88.97% | 911.0c/73.98%/88.69% | 2.85% | 63.64% | -283.0c |
| 2 | `book_margin: seconds_to_close>=480 AND abs_book_rv15_gap<=0.15` | False | 338.0c/175.0c | 1475.0c/72.84%/86.48% | 600.0c/71.92%/91.86% | 3.55% | 54.55% | -338.0c |
| 3 | `book_margin: seconds_to_close>=360 AND adverse_move_15m<=100` | False | 153.0c/310.0c | 1290.0c/72.66%/91.10% | 735.0c/72.91%/91.86% | 4.70% | 54.55% | -251.0c |
| 4 | `book_margin_early: abs_book_rv15_gap<=0.2 AND adverse_move_15m<=100` | False | 290.0c/135.0c | 1457.0c/73.25%/86.48% | 854.0c/73.58%/87.33% | 2.22% | 63.64% | -306.0c |
| 5 | `book_margin: seconds_to_close>=480 AND abs_book_rv15_gap<=0.2` | False | 185.0c/237.0c | 1322.0c/72.24%/93.59% | 662.0c/72.20%/92.76% | 4.46% | 63.64% | -338.0c |
| 6 | `book_margin: seconds_to_close>=480` | False | 30.0c/294.0c | 1167.0c/71.96%/96.44% | 719.0c/72.60%/94.12% | 5.00% | 63.64% | -315.0c |
| 7 | `book_margin: ask_cents<=95 AND seconds_to_close>=480` | False | 30.0c/294.0c | 1167.0c/71.96%/96.44% | 719.0c/72.60%/94.12% | 5.00% | 63.64% | -315.0c |
| 8 | `book_margin: seconds_to_close>=480 AND seconds_to_close<=900` | False | 30.0c/294.0c | 1167.0c/71.96%/96.44% | 719.0c/72.60%/94.12% | 5.00% | 63.64% | -315.0c |
| 9 | `book_margin: seconds_to_close>=480 AND book_p_side>=0.6` | False | 30.0c/294.0c | 1167.0c/71.96%/96.44% | 719.0c/72.60%/94.12% | 5.00% | 63.64% | -315.0c |
| 10 | `book_margin: seconds_to_close>=480 AND brownian_p_rv_15m>=0.5` | False | 30.0c/294.0c | 1167.0c/71.96%/96.44% | 719.0c/72.60%/94.12% | 5.00% | 63.64% | -315.0c |
| 11 | `book_margin: seconds_to_close>=480 AND margin_per_rv_sigma_15m>=0` | False | 30.0c/294.0c | 1167.0c/71.96%/96.44% | 719.0c/72.60%/94.12% | 5.00% | 63.64% | -315.0c |
| 12 | `book_margin: seconds_to_close>=480 AND spread_cents<=4` | False | 30.0c/294.0c | 1167.0c/71.96%/96.44% | 719.0c/72.60%/94.12% | 5.00% | 63.64% | -315.0c |
| 13 | `book_margin: ask_cents<=90 AND seconds_to_close>=480` | False | 30.0c/287.0c | 1167.0c/71.96%/96.44% | 712.0c/72.46%/93.67% | 5.00% | 63.64% | -315.0c |
| 14 | `book_margin: seconds_to_close>=480 AND spread_cents<=2` | False | 58.0c/259.0c | 1195.0c/72.12%/95.73% | 684.0c/72.46%/93.67% | 5.00% | 63.64% | -315.0c |
| 15 | `book_margin_early: adverse_move_15m<=100` | False | 115.0c/192.0c | 1282.0c/72.80%/88.97% | 911.0c/73.98%/88.69% | 2.85% | 63.64% | -283.0c |
| 16 | `book_margin_early: ask_cents<=95 AND adverse_move_15m<=100` | False | 115.0c/192.0c | 1282.0c/72.80%/88.97% | 911.0c/73.98%/88.69% | 2.85% | 63.64% | -283.0c |
| 17 | `book_margin_early: seconds_to_close>=360 AND adverse_move_15m<=100` | False | 115.0c/192.0c | 1282.0c/72.80%/88.97% | 911.0c/73.98%/88.69% | 2.85% | 63.64% | -283.0c |
| 18 | `book_margin_early: seconds_to_close>=480 AND adverse_move_15m<=100` | False | 115.0c/192.0c | 1282.0c/72.80%/88.97% | 911.0c/73.98%/88.69% | 2.85% | 63.64% | -283.0c |
| 19 | `book_margin_early: seconds_to_close<=900 AND adverse_move_15m<=100` | False | 115.0c/192.0c | 1282.0c/72.80%/88.97% | 911.0c/73.98%/88.69% | 2.85% | 63.64% | -283.0c |
| 20 | `book_margin_early: book_p_side>=0.6 AND adverse_move_15m<=100` | False | 115.0c/192.0c | 1282.0c/72.80%/88.97% | 911.0c/73.98%/88.69% | 2.85% | 63.64% | -283.0c |
| 21 | `book_margin_early: brownian_p_rv_15m>=0.5 AND adverse_move_15m<=100` | False | 115.0c/192.0c | 1282.0c/72.80%/88.97% | 911.0c/73.98%/88.69% | 2.85% | 63.64% | -283.0c |
| 22 | `book_margin_early: adverse_move_15m<=100 AND margin_per_rv_sigma_15m>=0` | False | 115.0c/192.0c | 1282.0c/72.80%/88.97% | 911.0c/73.98%/88.69% | 2.85% | 63.64% | -283.0c |
| 23 | `book_margin_early: adverse_move_15m<=100 AND spread_cents<=4` | False | 115.0c/192.0c | 1282.0c/72.80%/88.97% | 911.0c/73.98%/88.69% | 2.85% | 63.64% | -283.0c |
| 24 | `book_margin_early: ask_cents<=90 AND adverse_move_15m<=100` | False | 115.0c/185.0c | 1282.0c/72.80%/88.97% | 904.0c/73.85%/88.24% | 2.85% | 63.64% | -283.0c |
| 25 | `book_margin_early: adverse_move_15m<=100 AND spread_cents<=2` | False | 143.0c/157.0c | 1310.0c/72.98%/88.26% | 876.0c/73.85%/88.24% | 2.85% | 63.64% | -283.0c |
| 26 | `book_margin: ask_cents<=85 AND seconds_to_close>=480` | False | 20.0c/277.0c | 1157.0c/71.85%/96.09% | 702.0c/72.33%/93.21% | 5.00% | 63.64% | -315.0c |
| 27 | `book_margin: seconds_to_close>=480 AND abs_book_rv15_gap<=0.3` | False | 15.0c/279.0c | 1152.0c/71.85%/96.09% | 704.0c/72.46%/93.67% | 5.00% | 63.64% | -315.0c |
| 28 | `book_margin_early: ask_cents<=85 AND adverse_move_15m<=100` | False | 105.0c/175.0c | 1272.0c/72.69%/88.61% | 894.0c/73.71%/87.78% | 2.85% | 63.64% | -283.0c |
| 29 | `book_margin_early: abs_book_rv15_gap<=0.3 AND adverse_move_15m<=100` | False | 100.0c/177.0c | 1267.0c/72.69%/88.61% | 896.0c/73.85%/88.24% | 2.85% | 63.64% | -283.0c |
| 30 | `book_margin: seconds_to_close>=360 AND abs_book_rv15_gap<=0.2` | False | 193.0c/61.0c | 1330.0c/72.12%/95.73% | 486.0c/71.23%/95.93% | 6.18% | 63.64% | -332.0c |

## Read

- No pair-veto rule clears the diagnostic robustness screen.
- Strict registered-signal readiness remains the promotion gate.
