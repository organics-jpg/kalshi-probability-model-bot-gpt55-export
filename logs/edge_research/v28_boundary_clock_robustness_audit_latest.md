# v28 Boundary-Clock Robustness Audit

Diagnostic-only: no live bot changes and no orders.

- Rule: `clock_composite`
- Passes basic robustness: `True`
- Candidate entries/settled/coverage: `114/114/75.000000`
- Candidate net/delta: `213.000000/819.000000c`
- Pending adverse net/delta: `213.000000/819.000000c`

## Interpretation

- Base diagnostic candidate net is 213.0c with delta 819.0c over 114 settled rows.
- Worst leave-one-market delta is 685.0c after removing KXBTC15M-26MAY060800-00.
- If all pending rows lose at ask-sized loss, pending stress is 0c and stressed delta is 819.0c.
- This audit is still diagnostic; promotion still requires frozen future rows.

## Worst Leave-One Markets

| market | contribution c | candidate net without | delta without |
|---|---:|---:|---:|
| KXBTC15M-26MAY060800-00 | 134.000000 | 79.000000 | 685.000000 |
| KXBTC15M-26MAY061900-00 | 128.000000 | 85.000000 | 691.000000 |
| KXBTC15M-26MAY052100-00 | 119.000000 | 94.000000 | 700.000000 |
| KXBTC15M-26MAY062130-30 | 114.000000 | 99.000000 | 705.000000 |
| KXBTC15M-26MAY052115-15 | 109.000000 | 104.000000 | 710.000000 |
| KXBTC15M-26MAY070815-15 | 108.000000 | 105.000000 | 711.000000 |
| KXBTC15M-26MAY061930-30 | 102.000000 | 111.000000 | 717.000000 |
| KXBTC15M-26MAY070045-45 | 100.000000 | 113.000000 | 719.000000 |
| KXBTC15M-26MAY070530-30 | 100.000000 | 113.000000 | 719.000000 |
| KXBTC15M-26MAY070945-45 | 100.000000 | 113.000000 | 719.000000 |
| KXBTC15M-26MAY060645-45 | 95.000000 | 118.000000 | 724.000000 |
| KXBTC15M-26MAY070715-15 | 94.000000 | 119.000000 | 725.000000 |
