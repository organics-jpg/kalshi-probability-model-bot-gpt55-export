# Long-Memory Momentum Regime Frontier

Generated UTC: `20260504_113123Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Keeps `book_margin` as the high-coverage base and tests 15m/30m adverse path-memory overlays.
- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.

## Diagnostics

- Current markets: 313
- V21 markets: 221
- Candidate specs: 217
- Strict pass rows: 0

## Top Rows

| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | fades current/v21 | min block+ | worst block |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_min_15_30m<=-100; book_score<=0.65; sec>=600; fade_ask<=45` | False | 2273.0c | 1503.0c | 97.78% | 1872.0c/401.0c | 71.06%/69.41% | 36/16 | 0.545 | -277.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_min_15_30m<=-100; book_score<=0.65; sec>=600; fade_ask<=50` | False | 2273.0c | 1503.0c | 97.78% | 1872.0c/401.0c | 71.06%/69.41% | 36/16 | 0.545 | -277.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_min_15_30m<=-100; book_score<=0.65; sec>=300; fade_ask<=45` | False | 2198.0c | 1503.0c | 97.78% | 1872.0c/326.0c | 71.06%/68.95% | 36/17 | 0.545 | -277.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_min_15_30m<=-100; book_score<=0.65; sec>=300; fade_ask<=50` | False | 2198.0c | 1503.0c | 97.78% | 1872.0c/326.0c | 71.06%/68.95% | 36/17 | 0.545 | -277.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_30m<=-100; book_score<=0.65; sec>=600; fade_ask<=45` | False | 1792.0c | 1485.0c | 97.78% | 1893.0c/-101.0c | 71.70%/67.58% | 28/12 | 0.545 | -354.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_30m<=-100; book_score<=0.65; sec>=600; fade_ask<=50` | False | 1792.0c | 1485.0c | 97.78% | 1893.0c/-101.0c | 71.70%/67.58% | 28/12 | 0.545 | -354.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_30m<=-100; book_score<=0.65; sec>=300; fade_ask<=45` | False | 1717.0c | 1485.0c | 97.78% | 1893.0c/-176.0c | 71.70%/67.12% | 28/13 | 0.545 | -354.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_30m<=-100; book_score<=0.65; sec>=300; fade_ask<=50` | False | 1717.0c | 1485.0c | 97.78% | 1893.0c/-176.0c | 71.70%/67.12% | 28/13 | 0.545 | -354.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_min_15_30m<=-100; book_score<=0.7; sec>=600; fade_ask<=45` | False | 2290.0c | 1442.0c | 97.78% | 1955.0c/335.0c | 70.10%/68.04% | 47/23 | 0.455 | -277.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_min_15_30m<=-100; book_score<=0.7; sec>=600; fade_ask<=50` | False | 2290.0c | 1442.0c | 97.78% | 1955.0c/335.0c | 70.10%/68.04% | 47/23 | 0.455 | -277.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_min_15_30m<=-100; book_score<=0.7; sec>=300; fade_ask<=45` | False | 2215.0c | 1442.0c | 97.78% | 1955.0c/260.0c | 70.10%/67.58% | 47/24 | 0.364 | -277.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_min_15_30m<=-100; book_score<=0.7; sec>=300; fade_ask<=50` | False | 2215.0c | 1442.0c | 97.78% | 1955.0c/260.0c | 70.10%/67.58% | 47/24 | 0.364 | -277.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=veto; signed_move_min_15_30m<=-100; book_score<=0.65; sec>=600; fade_ask<=100` | False | 1710.0c | 1304.0c | 97.78% | 1192.0c/518.0c | 72.26%/72.15% | 0/0 | 0.545 | -287.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=veto; signed_move_min_15_30m<=-100; book_score<=0.65; sec>=300; fade_ask<=100` | False | 1694.0c | 1304.0c | 97.78% | 1192.0c/502.0c | 72.26%/72.15% | 0/0 | 0.545 | -287.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_30m<=-100; book_score<=0.7; sec>=600; fade_ask<=45` | False | 1482.0c | 1230.0c | 97.78% | 1780.0c/-298.0c | 70.42%/65.75% | 36/18 | 0.455 | -354.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_30m<=-100; book_score<=0.7; sec>=600; fade_ask<=50` | False | 1482.0c | 1230.0c | 97.78% | 1780.0c/-298.0c | 70.42%/65.75% | 36/18 | 0.455 | -354.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_30m<=-100; book_score<=0.7; sec>=300; fade_ask<=45` | False | 1407.0c | 1230.0c | 97.78% | 1780.0c/-373.0c | 70.42%/65.30% | 36/19 | 0.364 | -354.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_30m<=-100; book_score<=0.7; sec>=300; fade_ask<=50` | False | 1407.0c | 1230.0c | 97.78% | 1780.0c/-373.0c | 70.42%/65.30% | 36/19 | 0.364 | -354.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=veto; signed_move_min_15_30m<=-100; book_score<=0.7; sec>=600; fade_ask<=100` | False | 1881.0c | 1222.0c | 97.78% | 1318.0c/563.0c | 72.90%/72.60% | 0/0 | 0.545 | -287.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=veto; signed_move_min_15_30m<=-100; book_score<=0.7; sec>=300; fade_ask<=100` | False | 1834.0c | 1211.0c | 97.78% | 1306.0c/528.0c | 72.90%/72.60% | 0/0 | 0.545 | -287.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=veto; signed_move_30m<=-100; book_score<=0.65; sec>=600; fade_ask<=100` | False | 1386.0c | 1149.0c | 97.78% | 1047.0c/339.0c | 71.61%/71.23% | 0/0 | 0.545 | -334.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=veto; signed_move_30m<=-100; book_score<=0.65; sec>=300; fade_ask<=100` | False | 1370.0c | 1149.0c | 97.78% | 1047.0c/323.0c | 71.61%/71.23% | 0/0 | 0.545 | -334.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=veto; signed_move_min_15_30m<=-50; book_score<=0.65; sec>=600; fade_ask<=100` | False | 1206.0c | 1144.0c | 97.78% | 874.0c/332.0c | 71.94%/72.15% | 0/0 | 0.545 | -333.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=veto; signed_move_30m<=-100; book_score<=0.7; sec>=600; fade_ask<=100` | False | 1379.0c | 1092.0c | 97.78% | 1086.0c/293.0c | 71.94%/71.23% | 0/0 | 0.545 | -334.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=veto; signed_move_30m<=-100; book_score<=0.7; sec>=300; fade_ask<=100` | False | 1337.0c | 1086.0c | 97.78% | 1079.0c/258.0c | 71.94%/71.23% | 0/0 | 0.545 | -334.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=veto; signed_move_min_15_30m<=-50; book_score<=0.65; sec>=300; fade_ask<=100` | False | 1091.0c | 1083.0c | 97.78% | 841.0c/250.0c | 71.94%/72.15% | 0/0 | 0.545 | -345.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_min_15_30m<=-100; book_score<=0.8; sec>=600; fade_ask<=45` | False | 1591.0c | 1057.0c | 97.78% | 1456.0c/135.0c | 66.88%/66.21% | 57/27 | 0.364 | -280.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_min_15_30m<=-100; book_score<=0.8; sec>=600; fade_ask<=50` | False | 1591.0c | 1057.0c | 97.78% | 1456.0c/135.0c | 66.88%/66.21% | 57/27 | 0.364 | -280.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_min_15_30m<=-100; book_score<=0.8; sec>=300; fade_ask<=45` | False | 1465.0c | 1057.0c | 97.78% | 1456.0c/9.0c | 66.88%/65.30% | 57/29 | 0.364 | -280.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; signed_move_min_15_30m<=-100; book_score<=0.8; sec>=300; fade_ask<=50` | False | 1465.0c | 1057.0c | 97.78% | 1456.0c/9.0c | 66.88%/65.30% | 57/29 | 0.364 | -280.0c |

## Read

- No long-memory momentum overlay clears the strict gate.
