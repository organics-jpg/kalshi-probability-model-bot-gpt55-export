# v28 Approved-Entry Book-Edge Actionability

Research-only; no live bot changes or orders.

- Freeze timestamp UTC: `2026-05-06T06:20:06.824407+00:00`
- Future actual-approved entries: `133`

## Current Read

- Scored 133 future actual-approved v28 entries from book-FV freeze 2026-05-06T06:20:06.824407+00:00.
- Keep-all control net is 701.0c with 133 settled rows.
- Useful retained-coverage policies found: 2.
- Best clean policy skip_discount15_book_edge_lt_5pp keeps coverage 84.21052631578948%, improves net by 226.0c, and skipped rows were 16/5 for -226.0c.

## Policy Ranking

| policy | retained settled | retained W/L | retained coverage | retained net c | skipped W/L | skipped net c | delta c | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `skip_discount15_book_edge_lt_5pp` | 112 | 102/10 | 84.210526 | 927.000000 | 16/5 | -226.000000 | 226.000000 | none |
| `skip_late_discount10` | 128 | 115/13 | 96.240602 | 825.000000 | 3/2 | -124.000000 | 124.000000 | none |
| `keep_all` | 133 | 118/15 | 100.000000 | 701.000000 | 0/0 | 0 | 0.000000 | net_not_better_than_keep_all |
| `skip_book_edge_lt_0` | 133 | 118/15 | 100.000000 | 701.000000 | 0/0 | 0 | 0.000000 | net_not_better_than_keep_all |
| `skip_high_recross_book_edge_lt_5pp` | 133 | 118/15 | 100.000000 | 701.000000 | 0/0 | 0 | 0.000000 | net_not_better_than_keep_all |
| `skip_discount10_book_edge_lt_5pp` | 83 | 74/9 | 62.406015 | 534.000000 | 44/6 | 167.000000 | -167.000000 | retained_coverage_lt_75, net_not_better_than_keep_all |
| `skip_no_discount10` | 99 | 88/11 | 74.436090 | 486.000000 | 30/4 | 215.000000 | -215.000000 | retained_coverage_lt_75, net_not_better_than_keep_all |
| `skip_book_edge_lt_2pp` | 0 | 0/0 | 0.000000 | 0 | 118/15 | 701.000000 | -701.000000 | retained_settled_lt_30, retained_coverage_lt_75, net_not_better_than_keep_all |

## Useful Policy Skips

- `skip_discount15_book_edge_lt_5pp`: Skip if raw exceeds book by at least 15pp and book edge is below 5pp.
  - `KXBTC15M-26MAY060330-30` `no` won `False` gross `-18c`, raw/book/ask `0.999788/0.090000/0.090000`
  - `KXBTC15M-26MAY060745-45` `yes` won `False` gross `-24c`, raw/book/ask `0.851843/0.690000/0.690000`
  - `KXBTC15M-26MAY060800-00` `yes` won `True` gross `-32c`, raw/book/ask `0.874265/0.660000/0.660000`
  - `KXBTC15M-26MAY060915-15` `no` won `True` gross `0c`, raw/book/ask `0.850409/0.700000/0.700000`
  - `KXBTC15M-26MAY060945-45` `no` won `True` gross `-16c`, raw/book/ask `0.854149/0.590000/0.590000`
  - `KXBTC15M-26MAY060945-45` `no` won `True` gross `-16c`, raw/book/ask `0.850231/0.700000/0.700000`
  - `KXBTC15M-26MAY060945-45` `no` won `True` gross `-12c`, raw/book/ask `0.861162/0.710000/0.710000`
  - `KXBTC15M-26MAY061000-00` `no` won `True` gross `70c`, raw/book/ask `0.854748/0.650000/0.650000`
- `skip_late_discount10`: Skip late entries when raw exceeds book by at least 10pp.
  - `KXBTC15M-26MAY060245-45` `yes` won `True` gross `38c`, raw/book/ask `0.877828/0.760000/0.760000`
  - `KXBTC15M-26MAY060330-30` `no` won `False` gross `-18c`, raw/book/ask `0.999788/0.090000/0.090000`
  - `KXBTC15M-26MAY060800-00` `yes` won `True` gross `-32c`, raw/book/ask `0.874265/0.660000/0.660000`
  - `KXBTC15M-26MAY062015-15` `yes` won `False` gross `-134c`, raw/book/ask `0.885657/0.670000/0.670000`
  - `KXBTC15M-26MAY062115-15` `yes` won `True` gross `22c`, raw/book/ask `0.993517/0.880000/0.880000`
