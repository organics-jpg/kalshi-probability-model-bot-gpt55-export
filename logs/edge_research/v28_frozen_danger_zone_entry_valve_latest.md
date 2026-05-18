# v28 Frozen Danger-Zone Entry Valve

- Freeze timestamp UTC: `2026-05-06T03:09:58.042066+00:00`
- Policy: `skip_reentry_gap15_or_gap30`
- Future rows/markets: `142/84`
- Candidate entries/W-L/gross: `134/119-15/973.000000c`
- Control entries/W-L/gross: `142/125-17/715.000000c`
- Delta / coverage / skipped: `258.000000c/100.000000%/8`
- Blockers: `none`

## Current Read

- Frozen danger-zone policy skip_reentry_gap15_or_gap30 has 134 future settled approved rows and delta 258.0c vs current approved entries.
- This is actual-v28-approved-only forward validation; it does not score rejected simulated entries.

## Skipped Examples

- `KXBTC15M-26MAY060330-30` `no` won `False`, gross/hold `-18/-18`, gap `0.909788`, same-side idx `0`
- `KXBTC15M-26MAY060800-00` `yes` won `True`, gross/hold `-32/68`, gap `0.214265`, same-side idx `1`
- `KXBTC15M-26MAY060945-45` `no` won `True`, gross/hold `-16/60`, gap `0.150231`, same-side idx `1`
- `KXBTC15M-26MAY060945-45` `no` won `True`, gross/hold `-12/58`, gap `0.151162`, same-side idx `2`
- `KXBTC15M-26MAY061015-15` `no` won `True`, gross/hold `0/60`, gap `0.155860`, same-side idx `1`
- `KXBTC15M-26MAY062015-15` `no` won `True`, gross/hold `-60/116`, gap `0.451622`, same-side idx `0`
- `KXBTC15M-26MAY062015-15` `yes` won `False`, gross/hold `-134/-134`, gap `0.215657`, same-side idx `1`
- `KXBTC15M-26MAY062100-00` `yes` won `True`, gross/hold `14/78`, gap `0.242359`, same-side idx `2`
