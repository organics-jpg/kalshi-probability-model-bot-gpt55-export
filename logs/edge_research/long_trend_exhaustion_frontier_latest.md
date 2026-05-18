# Long-Trend Exhaustion Frontier

Generated UTC: `20260504_155958Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests whether large favorable 30-minute move on the selected side is terminal confirmation or exhaustion.
- Strict pass requires current+v21 80% split coverage, positive validation/holdout, positive all splits, and block stability.

## Diagnostics

- Current markets: 327
- V21 markets: 221
- Candidate specs: 85
- Strict pass rows: 0

## Top Rows

| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | triggers current/v21 | fades current/v21 | min block+ | worst block |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=250; ask>=0; fade_ask<=40` | False | 2058.0c | 1030.0c | 97.78% | 1341.0c/717.0c | 69.23%/69.86% | 28/17 | 28/17 | 0.562 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=250; ask>=0; fade_ask<=45` | False | 2058.0c | 1030.0c | 97.78% | 1341.0c/717.0c | 69.23%/69.86% | 28/17 | 28/17 | 0.562 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=250; ask>=0; fade_ask<=50` | False | 2058.0c | 1030.0c | 97.78% | 1341.0c/717.0c | 69.23%/69.86% | 28/17 | 28/17 | 0.562 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=250; ask>=60; fade_ask<=40` | False | 2058.0c | 1030.0c | 97.78% | 1341.0c/717.0c | 69.23%/69.86% | 28/17 | 28/17 | 0.562 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=250; ask>=60; fade_ask<=45` | False | 2058.0c | 1030.0c | 97.78% | 1341.0c/717.0c | 69.23%/69.86% | 28/17 | 28/17 | 0.562 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=250; ask>=60; fade_ask<=50` | False | 2058.0c | 1030.0c | 97.78% | 1341.0c/717.0c | 69.23%/69.86% | 28/17 | 28/17 | 0.562 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=300; ask>=0; fade_ask<=40` | False | 2283.0c | 971.0c | 97.78% | 1437.0c/846.0c | 70.15%/71.23% | 21/12 | 21/12 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=300; ask>=0; fade_ask<=45` | False | 2283.0c | 971.0c | 97.78% | 1437.0c/846.0c | 70.15%/71.23% | 21/12 | 21/12 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=300; ask>=0; fade_ask<=50` | False | 2283.0c | 971.0c | 97.78% | 1437.0c/846.0c | 70.15%/71.23% | 21/12 | 21/12 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=300; ask>=60; fade_ask<=40` | False | 2283.0c | 971.0c | 97.78% | 1437.0c/846.0c | 70.15%/71.23% | 21/12 | 21/12 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=300; ask>=60; fade_ask<=45` | False | 2283.0c | 971.0c | 97.78% | 1437.0c/846.0c | 70.15%/71.23% | 21/12 | 21/12 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=300; ask>=60; fade_ask<=50` | False | 2283.0c | 971.0c | 97.78% | 1437.0c/846.0c | 70.15%/71.23% | 21/12 | 21/12 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=350; ask>=0; fade_ask<=40` | False | 2062.0c | 848.0c | 97.78% | 1314.0c/748.0c | 69.85%/71.69% | 20/7 | 20/7 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=350; ask>=0; fade_ask<=45` | False | 2062.0c | 848.0c | 97.78% | 1314.0c/748.0c | 69.85%/71.69% | 20/7 | 20/7 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=350; ask>=0; fade_ask<=50` | False | 2062.0c | 848.0c | 97.78% | 1314.0c/748.0c | 69.85%/71.69% | 20/7 | 20/7 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=350; ask>=60; fade_ask<=40` | False | 2062.0c | 848.0c | 97.78% | 1314.0c/748.0c | 69.85%/71.69% | 20/7 | 20/7 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=350; ask>=60; fade_ask<=45` | False | 2062.0c | 848.0c | 97.78% | 1314.0c/748.0c | 69.85%/71.69% | 20/7 | 20/7 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=350; ask>=60; fade_ask<=50` | False | 2062.0c | 848.0c | 97.78% | 1314.0c/748.0c | 69.85%/71.69% | 20/7 | 20/7 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=500; ask>=0; fade_ask<=40` | False | 1649.0c | 809.0c | 97.78% | 1162.0c/487.0c | 70.15%/71.23% | 11/2 | 11/2 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=500; ask>=0; fade_ask<=45` | False | 1649.0c | 809.0c | 97.78% | 1162.0c/487.0c | 70.15%/71.23% | 11/2 | 11/2 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=500; ask>=0; fade_ask<=50` | False | 1649.0c | 809.0c | 97.78% | 1162.0c/487.0c | 70.15%/71.23% | 11/2 | 11/2 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=500; ask>=60; fade_ask<=40` | False | 1649.0c | 809.0c | 97.78% | 1162.0c/487.0c | 70.15%/71.23% | 11/2 | 11/2 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=500; ask>=60; fade_ask<=45` | False | 1649.0c | 809.0c | 97.78% | 1162.0c/487.0c | 70.15%/71.23% | 11/2 | 11/2 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=500; ask>=60; fade_ask<=50` | False | 1649.0c | 809.0c | 97.78% | 1162.0c/487.0c | 70.15%/71.23% | 11/2 | 11/2 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=400; ask>=0; fade_ask<=40` | False | 1962.0c | 797.0c | 97.78% | 1214.0c/748.0c | 69.85%/72.15% | 16/4 | 16/4 | 0.562 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=400; ask>=0; fade_ask<=45` | False | 1962.0c | 797.0c | 97.78% | 1214.0c/748.0c | 69.85%/72.15% | 16/4 | 16/4 | 0.562 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=400; ask>=0; fade_ask<=50` | False | 1962.0c | 797.0c | 97.78% | 1214.0c/748.0c | 69.85%/72.15% | 16/4 | 16/4 | 0.562 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=400; ask>=60; fade_ask<=40` | False | 1962.0c | 797.0c | 97.78% | 1214.0c/748.0c | 69.85%/72.15% | 16/4 | 16/4 | 0.562 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=400; ask>=60; fade_ask<=45` | False | 1962.0c | 797.0c | 97.78% | 1214.0c/748.0c | 69.85%/72.15% | 16/4 | 16/4 | 0.562 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=400; ask>=60; fade_ask<=50` | False | 1962.0c | 797.0c | 97.78% | 1214.0c/748.0c | 69.85%/72.15% | 16/4 | 16/4 | 0.562 | -332.0c |
| `veto; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=400; ask>=0; fade_ask<=45` | False | 1688.0c | 728.0c | 81.82% | 1091.0c/597.0c | 71.20%/72.09% | 16/4 | 0/0 | 0.625 | -332.0c |
| `veto; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=400; ask>=60; fade_ask<=45` | False | 1688.0c | 728.0c | 81.82% | 1091.0c/597.0c | 71.20%/72.09% | 16/4 | 0/0 | 0.625 | -332.0c |
| `veto; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=500; ask>=0; fade_ask<=45` | False | 1513.0c | 726.0c | 86.36% | 1052.0c/461.0c | 71.02%/71.43% | 11/2 | 0/0 | 0.625 | -332.0c |
| `veto; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=500; ask>=60; fade_ask<=45` | False | 1513.0c | 726.0c | 86.36% | 1052.0c/461.0c | 71.02%/71.43% | 11/2 | 0/0 | 0.625 | -332.0c |
| `fade_else_keep; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; signed_move_30m>=350; ask>=70; fade_ask<=40` | False | 1469.0c | 654.0c | 97.78% | 825.0c/644.0c | 69.54%/71.69% | 5/3 | 5/3 | 0.625 | -332.0c |

## Read

- No long-trend exhaustion row clears the full strict gate. Do not promote a row from this scan.
