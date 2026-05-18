# v28 Danger-Zone Entry Valve

- Surface: `actual_v28_approved_entries_only`
- Rows/markets: `173/107`
- Best policy: `skip_reentry_gap15_or_gap30`

## Current Read

- Best danger-zone policy is skip_reentry_gap15_or_gap30 with delta 322.0c and coverage 99.06542056074767%.
- Control gross is 823.0c over 173 entries.
- Discovery-only: this must be frozen and validated forward before promotion.

## Ranking

| rank | policy | entries | W/L | coverage | gross c | hold c | delta c | skipped | skipped gross c |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `skip_reentry_gap15_or_gap30` | 161 | 139/22 | 99.065421 | 1145.000000 | 2226.000000 | 322.000000 | 12 | -322.000000 |
| 2 | `skip_raw_book_gap_gt30` | 168 | 144/24 | 99.065421 | 917.000000 | 2278.000000 | 94.000000 | 5 | -94.000000 |
| 3 | `current_v28_approved_all` | 173 | 146/27 | 100.000000 | 823.000000 | 2304.000000 | 0.000000 | 0 | 0 |
| 4 | `skip_reentry_or_gap30` | 112 | 95/17 | 99.065421 | 604.000000 | 1250.000000 | -219.000000 | 61 | 219.000000 |
| 5 | `skip_same_side_reentry` | 116 | 97/19 | 100.000000 | 532.000000 | 1356.000000 | -291.000000 | 57 | 291.000000 |

## Skipped Examples

### skip_reentry_gap15_or_gap30
- `KXBTC15M-26MAY051615-15` `yes` won `True`, gross/hold `32/88`, gap `0.362190`, same-side idx `0`
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross/hold `-48/-138`, gap `0.190552`, same-side idx `1`
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross/hold `-22/-80`, gap `0.468759`, same-side idx `2`
- `KXBTC15M-26MAY052245-45` `no` won `False`, gross/hold `-26/-80`, gap `0.516618`, same-side idx `0`
- `KXBTC15M-26MAY060330-30` `no` won `False`, gross/hold `-18/-18`, gap `0.909788`, same-side idx `0`

### skip_raw_book_gap_gt30
- `KXBTC15M-26MAY051615-15` `yes` won `True`, gross/hold `32/88`, gap `0.362190`, same-side idx `0`
- `KXBTC15M-26MAY051715-15` `yes` won `False`, gross/hold `-22/-80`, gap `0.468759`, same-side idx `2`
- `KXBTC15M-26MAY052245-45` `no` won `False`, gross/hold `-26/-80`, gap `0.516618`, same-side idx `0`
- `KXBTC15M-26MAY060330-30` `no` won `False`, gross/hold `-18/-18`, gap `0.909788`, same-side idx `0`
- `KXBTC15M-26MAY062015-15` `no` won `True`, gross/hold `-60/116`, gap `0.451622`, same-side idx `0`

