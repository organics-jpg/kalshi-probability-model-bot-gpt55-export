# Preemptive Physics Switch Frontier

Generated UTC: `20260504_125437Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Preserves `book_margin` coverage but lets an earlier cheaper opposite physics row preempt a later weak book row.
- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.

## Diagnostics

- Current markets: 314
- V21 markets: 221
- Candidate specs: 811
- Strict pass rows: 0

## Top Rows

| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | preempts current/v21 | min block+ | worst block |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=score_mean_book_rv15>=0.55; alt_ask<=60; alt_cheaper_by>=10c; alt_age<=600s` | False | 1717.0c | 1108.0c | 97.78% | 1045.0c/672.0c | 70.51%/72.15% | 13/4 | 0.6875 | -283.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=score_mean_book_rv15>=0.55; alt_ask<=70; alt_cheaper_by>=10c; alt_age<=600s` | False | 1717.0c | 1108.0c | 97.78% | 1045.0c/672.0c | 70.51%/72.15% | 13/4 | 0.6875 | -283.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=score_mean_book_rv15>=0.55; alt_ask<=80; alt_cheaper_by>=10c; alt_age<=600s` | False | 1717.0c | 1108.0c | 97.78% | 1045.0c/672.0c | 70.51%/72.15% | 13/4 | 0.6875 | -283.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_30m>=0.6; alt_ask<=60; alt_cheaper_by>=10c; alt_age<=600s` | False | 1449.0c | 1041.0c | 97.78% | 845.0c/604.0c | 69.87%/71.69% | 11/5 | 0.5625 | -283.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_30m>=0.6; alt_ask<=70; alt_cheaper_by>=10c; alt_age<=600s` | False | 1449.0c | 1041.0c | 97.78% | 845.0c/604.0c | 69.87%/71.69% | 11/5 | 0.5625 | -283.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_30m>=0.6; alt_ask<=80; alt_cheaper_by>=10c; alt_age<=600s` | False | 1449.0c | 1041.0c | 97.78% | 845.0c/604.0c | 69.87%/71.69% | 11/5 | 0.5625 | -283.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_15m>=0.6; alt_ask<=60; alt_cheaper_by>=10c; alt_age<=600s` | False | 1338.0c | 1041.0c | 97.78% | 867.0c/471.0c | 69.87%/70.78% | 13/9 | 0.5625 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_15m>=0.6; alt_ask<=70; alt_cheaper_by>=10c; alt_age<=600s` | False | 1338.0c | 1041.0c | 97.78% | 867.0c/471.0c | 69.87%/70.78% | 13/9 | 0.5625 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_15m>=0.6; alt_ask<=80; alt_cheaper_by>=10c; alt_age<=600s` | False | 1338.0c | 1041.0c | 97.78% | 867.0c/471.0c | 69.87%/70.78% | 13/9 | 0.5625 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=score_mean_book_rv15>=0.55; alt_ask<=60; alt_cheaper_by>=10c; alt_age<=300s` | False | 1608.0c | 998.0c | 97.78% | 1046.0c/562.0c | 70.51%/71.69% | 13/3 | 0.6875 | -283.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=score_mean_book_rv15>=0.55; alt_ask<=70; alt_cheaper_by>=10c; alt_age<=300s` | False | 1608.0c | 998.0c | 97.78% | 1046.0c/562.0c | 70.51%/71.69% | 13/3 | 0.6875 | -283.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=score_mean_book_rv15>=0.55; alt_ask<=80; alt_cheaper_by>=10c; alt_age<=300s` | False | 1608.0c | 998.0c | 97.78% | 1046.0c/562.0c | 70.51%/71.69% | 13/3 | 0.6875 | -283.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_30m>=0.6; alt_ask<=60; alt_cheaper_by>=10c; alt_age<=300s` | False | 1429.0c | 931.0c | 97.78% | 935.0c/494.0c | 70.19%/71.23% | 10/4 | 0.5625 | -283.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_30m>=0.6; alt_ask<=70; alt_cheaper_by>=10c; alt_age<=300s` | False | 1429.0c | 931.0c | 97.78% | 935.0c/494.0c | 70.19%/71.23% | 10/4 | 0.5625 | -283.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_30m>=0.6; alt_ask<=80; alt_cheaper_by>=10c; alt_age<=300s` | False | 1429.0c | 931.0c | 97.78% | 935.0c/494.0c | 70.19%/71.23% | 10/4 | 0.5625 | -283.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_15m>=0.6; alt_ask<=60; alt_cheaper_by>=10c; alt_age<=300s` | False | 1318.0c | 931.0c | 97.78% | 957.0c/361.0c | 70.19%/70.32% | 12/8 | 0.5625 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_15m>=0.6; alt_ask<=70; alt_cheaper_by>=10c; alt_age<=300s` | False | 1318.0c | 931.0c | 97.78% | 957.0c/361.0c | 70.19%/70.32% | 12/8 | 0.5625 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_15m>=0.6; alt_ask<=80; alt_cheaper_by>=10c; alt_age<=300s` | False | 1318.0c | 931.0c | 97.78% | 957.0c/361.0c | 70.19%/70.32% | 12/8 | 0.5625 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.7; alt=score_mean_book_rv15>=0.55; alt_ask<=60; alt_cheaper_by>=10c; alt_age<=600s` | False | 1250.0c | 899.0c | 97.78% | 746.0c/504.0c | 69.23%/70.78% | 21/13 | 0.6364 | -350.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.7; alt=score_mean_book_rv15>=0.55; alt_ask<=70; alt_cheaper_by>=10c; alt_age<=600s` | False | 1250.0c | 899.0c | 97.78% | 746.0c/504.0c | 69.23%/70.78% | 21/13 | 0.6364 | -350.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.7; alt=score_mean_book_rv15>=0.55; alt_ask<=80; alt_cheaper_by>=10c; alt_age<=600s` | False | 1250.0c | 899.0c | 97.78% | 746.0c/504.0c | 69.23%/70.78% | 21/13 | 0.6364 | -350.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_15m>=0.58; alt_ask<=60; alt_cheaper_by>=10c; alt_age<=120s` | False | 1231.0c | 841.0c | 97.78% | 986.0c/245.0c | 70.19%/69.86% | 14/7 | 0.5625 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_15m>=0.58; alt_ask<=70; alt_cheaper_by>=10c; alt_age<=120s` | False | 1231.0c | 841.0c | 97.78% | 986.0c/245.0c | 70.19%/69.86% | 14/7 | 0.5625 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_15m>=0.58; alt_ask<=80; alt_cheaper_by>=10c; alt_age<=120s` | False | 1231.0c | 841.0c | 97.78% | 986.0c/245.0c | 70.19%/69.86% | 14/7 | 0.5625 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_30m>=0.6; alt_ask<=60; alt_cheaper_by>=5c; alt_age<=600s` | False | 952.0c | 839.0c | 97.78% | 626.0c/326.0c | 69.23%/70.32% | 15/8 | 0.5000 | -310.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_30m>=0.6; alt_ask<=70; alt_cheaper_by>=5c; alt_age<=600s` | False | 952.0c | 839.0c | 97.78% | 626.0c/326.0c | 69.23%/70.32% | 15/8 | 0.5000 | -310.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_30m>=0.6; alt_ask<=80; alt_cheaper_by>=5c; alt_age<=600s` | False | 952.0c | 839.0c | 97.78% | 626.0c/326.0c | 69.23%/70.32% | 15/8 | 0.5000 | -310.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_15m>=0.6; alt_ask<=60; alt_cheaper_by>=5c; alt_age<=600s` | False | 747.0c | 839.0c | 97.78% | 646.0c/101.0c | 69.23%/68.95% | 17/13 | 0.5000 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_15m>=0.6; alt_ask<=70; alt_cheaper_by>=5c; alt_age<=600s` | False | 747.0c | 839.0c | 97.78% | 646.0c/101.0c | 69.23%/68.95% | 17/13 | 0.5000 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; preempt_if_book<=0.65; alt=brownian_p_rv_15m>=0.6; alt_ask<=80; alt_cheaper_by>=5c; alt_age<=600s` | False | 747.0c | 839.0c | 97.78% | 646.0c/101.0c | 69.23%/68.95% | 17/13 | 0.5000 | -366.0c |

## Read

- No preemptive physics switch clears the strict gate.
