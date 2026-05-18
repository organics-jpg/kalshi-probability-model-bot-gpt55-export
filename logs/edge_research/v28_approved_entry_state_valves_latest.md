# v28 Approved-Entry State Valves

Actual-approved-entry diagnostic for same-market reentry and raw/book disagreement valves.

- Surface: `actual_v28_approved_entries_only`
- Rows/markets: `173/107`
- Best policy: `same_side_reentry_gap_lte_15pp`

## Current Read

- Best actual-only state valve is same_side_reentry_gap_lte_15pp with delta 250.0c vs current approved entries.
- Control approved entries are 173 rows with gross 823.0c.
- This is diagnostic only because it is evaluated on already-approved live/shadow entries, not a frozen future promotion slice.

## Ranking

| rank | policy | entries | W/L | market coverage | gross c | delta c | skipped | skipped gross c | skipped markets |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `same_side_reentry_gap_lte_15pp` | 165 | 141/24 | 100.000000 | 1073.000000 | 250.000000 | 8 | -250.000000 | 0 |
| 2 | `same_side_reentry_gap_lte15_and_book_not_down10` | 165 | 141/24 | 100.000000 | 1073.000000 | 250.000000 | 8 | -250.000000 | 0 |
| 3 | `same_side_reentry_book_not_down_10pp` | 168 | 144/24 | 100.000000 | 1045.000000 | 222.000000 | 5 | -222.000000 | 0 |
| 4 | `raw_book_gap_lte_15pp` | 146 | 127/19 | 92.523364 | 1035.000000 | 212.000000 | 27 | -212.000000 | 8 |
| 5 | `raw_book_gap_lte_20pp` | 156 | 134/22 | 94.392523 | 1001.000000 | 178.000000 | 17 | -178.000000 | 6 |
| 6 | `current_v28_approved_all` | 173 | 146/27 | 100.000000 | 823.000000 | 0.000000 | 0 | 0 | 0 |
| 7 | `no_same_side_reentry` | 116 | 97/19 | 100.000000 | 532.000000 | -291.000000 | 57 | 291.000000 | 0 |
| 8 | `first_entry_per_market` | 107 | 91/16 | 100.000000 | 494.000000 | -329.000000 | 66 | 329.000000 | 0 |

## Skipped Examples

### first_entry_per_market
- `KXBTC15M-26MAY051615-15` `yes` won `True`, gross `32`, raw/book gap `0.362190`, same-side idx `0`, book delta `None`
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross `-48`, raw/book gap `0.190552`, same-side idx `1`, book delta `-0.130000`
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross `-22`, raw/book gap `0.468759`, same-side idx `2`, book delta `-0.290000`
- `KXBTC15M-26MAY051745-45` `no` won `True`, gross `-2`, raw/book gap `0.061770`, same-side idx `1`, book delta `0.030000`
- `KXBTC15M-26MAY051800-00` `yes` won `True`, gross `40`, raw/book gap `0.058155`, same-side idx `1`, book delta `0.020000`

### no_same_side_reentry
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross `-48`, raw/book gap `0.190552`, same-side idx `1`, book delta `-0.130000`
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross `-22`, raw/book gap `0.468759`, same-side idx `2`, book delta `-0.290000`
- `KXBTC15M-26MAY051745-45` `no` won `True`, gross `-2`, raw/book gap `0.061770`, same-side idx `1`, book delta `0.030000`
- `KXBTC15M-26MAY051800-00` `yes` won `True`, gross `40`, raw/book gap `0.058155`, same-side idx `1`, book delta `0.020000`
- `KXBTC15M-26MAY052045-45` `yes` won `False`, gross `14`, raw/book gap `0.074488`, same-side idx `1`, book delta `0.040000`

### raw_book_gap_lte_20pp
- `KXBTC15M-26MAY051615-15` `yes` won `True`, gross `32`, raw/book gap `0.362190`, same-side idx `0`, book delta `None`
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross `-22`, raw/book gap `0.468759`, same-side idx `2`, book delta `-0.290000`
- `KXBTC15M-26MAY052100-00` `yes` won `True`, gross `34`, raw/book gap `0.296314`, same-side idx `0`, book delta `None`
- `KXBTC15M-26MAY052245-45` `no` won `False`, gross `-26`, raw/book gap `0.516618`, same-side idx `0`, book delta `None`
- `KXBTC15M-26MAY060330-30` `no` won `False`, gross `-18`, raw/book gap `0.909788`, same-side idx `0`, book delta `None`

### raw_book_gap_lte_15pp
- `KXBTC15M-26MAY051615-15` `yes` won `True`, gross `32`, raw/book gap `0.362190`, same-side idx `0`, book delta `None`
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross `-48`, raw/book gap `0.190552`, same-side idx `1`, book delta `-0.130000`
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross `-22`, raw/book gap `0.468759`, same-side idx `2`, book delta `-0.290000`
- `KXBTC15M-26MAY052100-00` `yes` won `True`, gross `34`, raw/book gap `0.296314`, same-side idx `0`, book delta `None`
- `KXBTC15M-26MAY052115-15` `yes` won `True`, gross `44`, raw/book gap `0.161543`, same-side idx `0`, book delta `None`

### same_side_reentry_gap_lte_15pp
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross `-48`, raw/book gap `0.190552`, same-side idx `1`, book delta `-0.130000`
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross `-22`, raw/book gap `0.468759`, same-side idx `2`, book delta `-0.290000`
- `KXBTC15M-26MAY060800-00` `yes` won `True`, gross `-32`, raw/book gap `0.214265`, same-side idx `1`, book delta `-0.130000`
- `KXBTC15M-26MAY060945-45` `no` won `True`, gross `-16`, raw/book gap `0.150231`, same-side idx `1`, book delta `0.110000`
- `KXBTC15M-26MAY060945-45` `no` won `True`, gross `-12`, raw/book gap `0.151162`, same-side idx `2`, book delta `0.010000`

### same_side_reentry_book_not_down_10pp
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross `-48`, raw/book gap `0.190552`, same-side idx `1`, book delta `-0.130000`
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross `-22`, raw/book gap `0.468759`, same-side idx `2`, book delta `-0.290000`
- `KXBTC15M-26MAY060800-00` `yes` won `True`, gross `-32`, raw/book gap `0.214265`, same-side idx `1`, book delta `-0.130000`
- `KXBTC15M-26MAY062015-15` `yes` won `False`, gross `-134`, raw/book gap `0.215657`, same-side idx `1`, book delta `-0.190000`
- `KXBTC15M-26MAY062100-00` `yes` won `True`, gross `14`, raw/book gap `0.242359`, same-side idx `2`, book delta `-0.230000`

### same_side_reentry_gap_lte15_and_book_not_down10
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross `-48`, raw/book gap `0.190552`, same-side idx `1`, book delta `-0.130000`
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross `-22`, raw/book gap `0.468759`, same-side idx `2`, book delta `-0.290000`
- `KXBTC15M-26MAY060800-00` `yes` won `True`, gross `-32`, raw/book gap `0.214265`, same-side idx `1`, book delta `-0.130000`
- `KXBTC15M-26MAY060945-45` `no` won `True`, gross `-16`, raw/book gap `0.150231`, same-side idx `1`, book delta `0.110000`
- `KXBTC15M-26MAY060945-45` `no` won `True`, gross `-12`, raw/book gap `0.151162`, same-side idx `2`, book delta `0.010000`

