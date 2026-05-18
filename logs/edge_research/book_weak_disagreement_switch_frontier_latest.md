# Weak-Book Disagreement Switch Frontier

Generated UTC: `20260504_125112Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Preserves `book_margin` coverage and only switches when an opposite physics side is cheaper and strong enough.
- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.

## Diagnostics

- Current markets: 314
- V21 markets: 221
- Candidate specs: 541
- Strict pass rows: 0

## Top Rows

| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | switches current/v21 | min block+ | worst block |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.55; alt_ask<=60; alt_cheaper_by>=0c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.55; alt_ask<=60; alt_cheaper_by>=5c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.55; alt_ask<=60; alt_cheaper_by>=10c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.55; alt_ask<=70; alt_cheaper_by>=0c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.55; alt_ask<=70; alt_cheaper_by>=5c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.55; alt_ask<=70; alt_cheaper_by>=10c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.55; alt_ask<=80; alt_cheaper_by>=0c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.55; alt_ask<=80; alt_cheaper_by>=5c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.55; alt_ask<=80; alt_cheaper_by>=10c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.55; alt_ask<=90; alt_cheaper_by>=0c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.55; alt_ask<=90; alt_cheaper_by>=5c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.55; alt_ask<=90; alt_cheaper_by>=10c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.6; alt_ask<=60; alt_cheaper_by>=0c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.6; alt_ask<=60; alt_cheaper_by>=5c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.6; alt_ask<=60; alt_cheaper_by>=10c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.6; alt_ask<=70; alt_cheaper_by>=0c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.6; alt_ask<=70; alt_cheaper_by>=5c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.6; alt_ask<=70; alt_cheaper_by>=10c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.6; alt_ask<=80; alt_cheaper_by>=0c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.6; alt_ask<=80; alt_cheaper_by>=5c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.6; alt_ask<=80; alt_cheaper_by>=10c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.6; alt_ask<=90; alt_cheaper_by>=0c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.6; alt_ask<=90; alt_cheaper_by>=5c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.6; alt_ask<=90; alt_cheaper_by>=10c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.65; alt_ask<=60; alt_cheaper_by>=0c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.65; alt_ask<=60; alt_cheaper_by>=5c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.65; alt_ask<=60; alt_cheaper_by>=10c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.65; alt_ask<=70; alt_cheaper_by>=0c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; switch_if_book<=0.62; alt=brownian_p_rv_15m>=0.65; alt_ask<=70; alt_cheaper_by>=5c` | False | 1410.0c | 749.0c | 97.78% | 985.0c/425.0c | 70.83%/71.23% | 0/0 | 0.6250 | -332.0c |

## Read

- No weak-book disagreement switch clears the strict gate.
