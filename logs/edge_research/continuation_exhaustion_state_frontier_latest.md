# Continuation/Exhaustion State Frontier

Generated UTC: `20260504_151947Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Uses broad book-margin as the coverage anchor, then tests same-side touch repricing and opposite-touch veto.
- Strict pass requires current+v21 80% split coverage, positive validation/holdout, positive all splits, and block stability.

## Diagnostics

- Current markets: 325
- V21 markets: 221
- Candidate specs: 577
- Strict pass rows: 0

## Top Rows

| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | repriced current/v21 | vetoed current/v21 | min block+ | worst block |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=65; touch_age<=180s; conflict_book<=1` | False | 4543.0c | 2073.0c | 97.78% | 2655.0c/1888.0c | 70.90%/71.23% | 236/131 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=65; touch_age<=300s; conflict_book<=1` | False | 4543.0c | 2073.0c | 97.78% | 2655.0c/1888.0c | 70.90%/71.23% | 236/131 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=65; touch_age<=600s; conflict_book<=1` | False | 4543.0c | 2073.0c | 97.78% | 2655.0c/1888.0c | 70.90%/71.23% | 236/131 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=65; touch_age<=900s; conflict_book<=1` | False | 4543.0c | 2073.0c | 97.78% | 2655.0c/1888.0c | 70.90%/71.23% | 236/131 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=65; touch_age<=180s; conflict_book<=1` | False | 4543.0c | 2073.0c | 97.78% | 2655.0c/1888.0c | 70.90%/71.23% | 236/131 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=65; touch_age<=300s; conflict_book<=1` | False | 4543.0c | 2073.0c | 97.78% | 2655.0c/1888.0c | 70.90%/71.23% | 236/131 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=65; touch_age<=600s; conflict_book<=1` | False | 4543.0c | 2073.0c | 97.78% | 2655.0c/1888.0c | 70.90%/71.23% | 236/131 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=65; touch_age<=900s; conflict_book<=1` | False | 4543.0c | 2073.0c | 97.78% | 2655.0c/1888.0c | 70.90%/71.23% | 236/131 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=60; touch_age<=180s; conflict_book<=1` | False | 4550.0c | 2072.0c | 97.78% | 2664.0c/1886.0c | 70.90%/71.23% | 217/126 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=60; touch_age<=300s; conflict_book<=1` | False | 4550.0c | 2072.0c | 97.78% | 2664.0c/1886.0c | 70.90%/71.23% | 217/126 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=60; touch_age<=600s; conflict_book<=1` | False | 4550.0c | 2072.0c | 97.78% | 2664.0c/1886.0c | 70.90%/71.23% | 217/126 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=60; touch_age<=900s; conflict_book<=1` | False | 4550.0c | 2072.0c | 97.78% | 2664.0c/1886.0c | 70.90%/71.23% | 217/126 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=60; touch_age<=180s; conflict_book<=1` | False | 4550.0c | 2072.0c | 97.78% | 2664.0c/1886.0c | 70.90%/71.23% | 217/126 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=60; touch_age<=300s; conflict_book<=1` | False | 4550.0c | 2072.0c | 97.78% | 2664.0c/1886.0c | 70.90%/71.23% | 217/126 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=60; touch_age<=600s; conflict_book<=1` | False | 4550.0c | 2072.0c | 97.78% | 2664.0c/1886.0c | 70.90%/71.23% | 217/126 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=60; touch_age<=900s; conflict_book<=1` | False | 4550.0c | 2072.0c | 97.78% | 2664.0c/1886.0c | 70.90%/71.23% | 217/126 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=70; touch_age<=180s; conflict_book<=1` | False | 4434.0c | 2003.0c | 97.78% | 2546.0c/1888.0c | 70.90%/71.23% | 245/133 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=70; touch_age<=300s; conflict_book<=1` | False | 4434.0c | 2003.0c | 97.78% | 2546.0c/1888.0c | 70.90%/71.23% | 245/133 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=70; touch_age<=600s; conflict_book<=1` | False | 4434.0c | 2003.0c | 97.78% | 2546.0c/1888.0c | 70.90%/71.23% | 245/133 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=70; touch_age<=900s; conflict_book<=1` | False | 4434.0c | 2003.0c | 97.78% | 2546.0c/1888.0c | 70.90%/71.23% | 245/133 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=70; touch_age<=180s; conflict_book<=1` | False | 4434.0c | 2003.0c | 97.78% | 2546.0c/1888.0c | 70.90%/71.23% | 245/133 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=70; touch_age<=300s; conflict_book<=1` | False | 4434.0c | 2003.0c | 97.78% | 2546.0c/1888.0c | 70.90%/71.23% | 245/133 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=70; touch_age<=600s; conflict_book<=1` | False | 4434.0c | 2003.0c | 97.78% | 2546.0c/1888.0c | 70.90%/71.23% | 245/133 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=70; touch_age<=900s; conflict_book<=1` | False | 4434.0c | 2003.0c | 97.78% | 2546.0c/1888.0c | 70.90%/71.23% | 245/133 | 0/0 | 0.688 | -288.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=55; touch_age<=300s; conflict_book<=1` | False | 4216.0c | 1931.0c | 97.78% | 2613.0c/1603.0c | 70.90%/71.23% | 136/79 | 0/0 | 0.625 | -303.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=55; touch_age<=600s; conflict_book<=1` | False | 4216.0c | 1931.0c | 97.78% | 2613.0c/1603.0c | 70.90%/71.23% | 136/79 | 0/0 | 0.625 | -303.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=55; touch_age<=900s; conflict_book<=1` | False | 4216.0c | 1931.0c | 97.78% | 2613.0c/1603.0c | 70.90%/71.23% | 136/79 | 0/0 | 0.625 | -303.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=55; touch_age<=300s; conflict_book<=1` | False | 4216.0c | 1931.0c | 97.78% | 2613.0c/1603.0c | 70.90%/71.23% | 136/79 | 0/0 | 0.625 | -303.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=55; touch_age<=600s; conflict_book<=1` | False | 4216.0c | 1931.0c | 97.78% | 2613.0c/1603.0c | 70.90%/71.23% | 136/79 | 0/0 | 0.625 | -303.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=55; touch_age<=900s; conflict_book<=1` | False | 4216.0c | 1931.0c | 97.78% | 2613.0c/1603.0c | 70.90%/71.23% | 136/79 | 0/0 | 0.625 | -303.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.35; touch_ask<=55; touch_age<=180s; conflict_book<=1` | False | 4135.0c | 1906.0c | 97.78% | 2604.0c/1531.0c | 70.90%/71.23% | 135/74 | 0/0 | 0.625 | -303.0c |
| `same-side touch reprice; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.4; touch_ask<=55; touch_age<=180s; conflict_book<=1` | False | 4135.0c | 1906.0c | 97.78% | 2604.0c/1531.0c | 70.90%/71.23% | 135/74 | 0/0 | 0.625 | -303.0c |
| `same-side touch reprice+opposite-touch veto; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.45; touch_ask<=70; touch_age<=180s; conflict_book<=0.8` | False | 3243.0c | 1631.0c | 81.82% | 1803.0c/1440.0c | 70.65%/72.02% | 187/91 | 30/26 | 0.688 | -220.0c |
| `same-side touch reprice+opposite-touch veto; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.45; touch_ask<=70; touch_age<=180s; conflict_book<=0.9` | False | 3218.0c | 1631.0c | 81.82% | 1803.0c/1415.0c | 70.65%/71.73% | 187/91 | 30/28 | 0.688 | -220.0c |
| `same-side touch reprice+opposite-touch veto; base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; touch>=0.45; touch_ask<=70; touch_age<=180s; conflict_book<=1` | False | 3218.0c | 1631.0c | 81.82% | 1803.0c/1415.0c | 70.65%/71.73% | 187/91 | 30/28 | 0.688 | -220.0c |

## Read

- No continuation/exhaustion overlay clears the full strict gate. Do not promote a row from this scan.
- Same-side touch repricing is a distinct hypothesis from opposite-touch preemption: it asks whether path/book agreement can improve entry price without changing side.
- Opposite-touch veto is a conservative exhaustion hypothesis; it skips conflict rather than buying the opposite side.
