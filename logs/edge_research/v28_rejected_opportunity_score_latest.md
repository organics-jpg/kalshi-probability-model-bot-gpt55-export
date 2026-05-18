# v28 Rejected Opportunity Score

- Purpose: score rejected v28 opportunities after settlement without changing strategy logic.
- Unit: first rejected observation per market/side/reason, so repeated throttle events do not dominate.

## Overall

- Opportunities: `1972`
- Resolved: `1951`
- Actionable resolved: `622`
- Would win: `1111`
- Would lose: `840`
- Hypothetical hold gross: `$-13.69`
- Actionable hold gross: `$-3.51`
- Actionable missed-profit/protected-loss: `422` / `200`
- Avg Brier: `0.16670087539383438`

## By Reject Reason

| reason | count | resolved | actionable resolved | missed | protected | hold gross | actionable gross | avg brier |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ask_too_high | 169 | 169 | 168 | 158 | 10 | $2.57 | $2.57 | 0.06849973035339645 |
| book_stale | 341 | 341 | 0 | 0 | 0 | $-4.68 | $0.00 | 0.20905134656048094 |
| btc_stale | 341 | 341 | 0 | 0 | 0 | $-3.03 | $0.00 | 0.24477588942650144 |
| edge_below_floor | 112 | 112 | 111 | 94 | 17 | $-0.91 | $-1.06 | 0.12611240365852677 |
| missing_horizon | 344 | 325 | 0 | 0 | 0 | $-1.26 | $0.00 | 0.0 |
| missing_strike | 2 | 0 | 0 | 0 | 0 | $0.00 | $0.00 | None |
| p_below_floor | 345 | 345 | 343 | 170 | 173 | $-5.13 | $-5.02 | 0.23621904797705506 |
| risk_or_depth | 3 | 3 | 0 | 0 | 0 | $-0.40 | $0.00 | 0.2843695811283334 |
| time_window | 313 | 313 | 0 | 0 | 0 | $-0.85 | $0.00 | 0.025295240361271565 |
| warming | 2 | 2 | 0 | 0 | 0 | $0.00 | $0.00 | 0.0 |

## Latest Rows

| market | side | reason | action | status | result | ask | side won | hold gross | verdict | p_side | edge |
|---|---|---|---|---|---|---:|---|---:|---|---:|---:|
| KXBTC15M-26MAY071315-15 | yes | p_below_floor | True | finalized | yes | 51 | True | 98 | missed_profit | 0.533442 | -1.655794 |
| KXBTC15M-26MAY071315-15 | no | p_below_floor | True | finalized | yes | 50 | False | -100 | protected_loss | 0.466558 | -7.344206 |
| KXBTC15M-26MAY071315-15 | yes | btc_stale | False | finalized | yes | 51 | True | 98 | missed_profit | 0.533465 | -1.653518 |
| KXBTC15M-26MAY071315-15 | no | btc_stale | False | finalized | yes | 50 | False | -100 | protected_loss | 0.466535 | -7.346482 |
| KXBTC15M-26MAY071315-15 | yes | book_stale | False | finalized | yes | 55 | True | 90 | missed_profit | 0.586781 | -0.321858 |
| KXBTC15M-26MAY071315-15 | no | book_stale | False | finalized | yes | 46 | False | -92 | protected_loss | 0.413219 | -8.678142 |
| KXBTC15M-26MAY071315-15 | yes | edge_below_floor | True | finalized | yes | 80 | True | 40 | missed_profit | 0.850666 | 1.56663 |
| KXBTC15M-26MAY071315-15 | yes | ask_too_high | True | finalized | yes | 93 | True | 14 | missed_profit | 0.955633 | 0.063253 |
| KXBTC15M-26MAY071315-15 | yes | time_window | False | finalized | yes | 100 | True | 0 | neutral | 0.982952 | -4.204752 |
| KXBTC15M-26MAY071315-15 | no | time_window | False | finalized | yes | 0 | False | 0 | neutral | 0.017048 | -0.795248 |
| KXBTC15M-26MAY071315-15 | yes | missing_horizon | False | finalized | yes | 100 | True | 0 | neutral | None | None |
| KXBTC15M-26MAY071315-15 | no | missing_horizon | False | finalized | yes | 0 | False | 0 | neutral | None | None |
| KXBTC15M-26MAY071330-30 | yes | p_below_floor | True | finalized | no | 41 | False | -82 | protected_loss | 0.423237 | -2.676282 |
| KXBTC15M-26MAY071330-30 | no | p_below_floor | True | finalized | no | 60 | True | 80 | missed_profit | 0.576763 | -6.323718 |
| KXBTC15M-26MAY071330-30 | yes | btc_stale | False | finalized | no | 38 | False | -76 | protected_loss | 0.392367 | -2.763296 |
| KXBTC15M-26MAY071330-30 | no | btc_stale | False | finalized | no | 63 | True | 74 | missed_profit | 0.607633 | -6.236704 |
| KXBTC15M-26MAY071330-30 | no | edge_below_floor | True | finalized | no | 82 | True | 18 | missed_profit | 0.86478 | 0.977966 |
| KXBTC15M-26MAY071330-30 | yes | book_stale | False | finalized | no | 14 | False | -28 | protected_loss | 0.094582 | -7.541807 |
| KXBTC15M-26MAY071330-30 | no | book_stale | False | finalized | no | 87 | True | 13 | missed_profit | 0.905418 | 0.541807 |
| KXBTC15M-26MAY071330-30 | no | ask_too_high | True | finalized | no | 92 | True | 16 | missed_profit | 0.921226 | -2.877394 |
