# v28 Exit Reduce Promotion Runway

Research-only; no live bot changes or orders.

- Freeze timestamp UTC: `2026-05-06T06:33:56.987999+00:00`
- Candidate: `suppress_reduce_p_hold_ge_075`
- Status: `collecting`
- Invalidators now: `suppressed_loss_control_cost_negative, robustness_shadow_interest_false`

## Runway

- Settled rows: `132`
- Rows needed for 30: `0`
- Current delta: `337.000000c`
- Suppressed exits: `25`
- Winner recovery: `1067.000000c`
- Loss-control cost: `-730.000000c`

## Interpretation

- Need 0 more settled future rows to reach the 30-row gate.
- Current frozen delta is 337.0c over 132 settled rows.
- Suppressed exits so far: 25; winner recovery 1067.0c; loss-control cost -730.0c.
- The fragile part is not PnL buffer; it is whether future suppressed reduce exits include losers.

## Future Tests

- Continue collecting until settled >= 30.
- Reject if cumulative delta versus current exits becomes <= 0.
- Reject if suppressed exits begin adding net loss-control cost; one suppressed loser is enough to require review.
- Keep collapse exits separate; this lane only concerns probability_reduce exits with p_hold >= 0.75.

## Suppressed Rows

| market | side | result | p_hold | current c | hold c | candidate c | delta c | worst hold mark |
|---|---|---|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY060245-45 | yes | yes | 0.793334 | -8.000000 | 40.000000 | 40.000000 | 48.000000 | 40 |
| KXBTC15M-26MAY060300-00 | yes | yes | 0.780402 | -14.000000 | 38.000000 | 38.000000 | 52.000000 | 28 |
| KXBTC15M-26MAY060300-00 | yes | yes | 0.753164 | -22.000000 | 40.000000 | 40.000000 | 62.000000 | 28 |
| KXBTC15M-26MAY060630-30 | yes | yes | 0.777774 | -12.000000 | 42.000000 | 42.000000 | 54.000000 | 26 |
| KXBTC15M-26MAY060645-45 | yes | yes | 0.799349 | -16.000000 | 36.000000 | 36.000000 | 52.000000 | 30 |
| KXBTC15M-26MAY060645-45 | yes | yes | 0.779789 | -12.000000 | 44.000000 | 44.000000 | 56.000000 | 30 |
| KXBTC15M-26MAY060700-00 | no | yes | 0.799603 | -8.000000 | -168.000000 | -168.000000 | -160.000000 | 10 |
| KXBTC15M-26MAY060900-00 | yes | no | 0.789990 | -10.000000 | -156.000000 | -156.000000 | -146.000000 | 34 |
| KXBTC15M-26MAY060915-15 | no | no | 0.793762 | 0.000000 | 60.000000 | 60.000000 | 60.000000 | 48 |
| KXBTC15M-26MAY060930-30 | no | no | 0.787606 | -14.000000 | 48.000000 | 48.000000 | 62.000000 | -10 |
| KXBTC15M-26MAY060930-30 | no | no | 0.799180 | -3.000000 | 54.000000 | 54.000000 | 57.000000 | -10 |
| KXBTC15M-26MAY061015-15 | no | no | 0.799979 | 0.000000 | 60.000000 | 60.000000 | 60.000000 | 4 |
| KXBTC15M-26MAY061030-30 | yes | yes | 0.752739 | -16.000000 | 44.000000 | 44.000000 | 60.000000 | -10 |
| KXBTC15M-26MAY061030-30 | yes | yes | 0.796458 | -10.000000 | 44.000000 | 44.000000 | 54.000000 | -10 |
| KXBTC15M-26MAY061045-45 | yes | yes | 0.796949 | -6.000000 | 40.000000 | 40.000000 | 46.000000 | 28 |
| KXBTC15M-26MAY061445-45 | no | no | 0.797830 | -22.000000 | 24.000000 | 24.000000 | 46.000000 | 14 |
| KXBTC15M-26MAY062130-30 | no | yes | 0.768407 | -32.000000 | -152.000000 | -152.000000 | -120.000000 | -152 |
| KXBTC15M-26MAY071000-00 | no | no | 0.781361 | 16.000000 | 58.000000 | 58.000000 | 42.000000 | 12 |
| KXBTC15M-26MAY071015-15 | no | yes | 0.789130 | 2.000000 | -156.000000 | -156.000000 | -158.000000 | 18 |
| KXBTC15M-26MAY071015-15 | no | yes | 0.763980 | -16.000000 | -162.000000 | -162.000000 | -146.000000 | 18 |
| KXBTC15M-26MAY071045-45 | no | no | 0.760529 | -10.000000 | 52.000000 | 52.000000 | 62.000000 | -14 |
| KXBTC15M-26MAY071215-15 | no | no | 0.797661 | -16.000000 | 32.000000 | 32.000000 | 48.000000 | -28 |
| KXBTC15M-26MAY071215-15 | no | no | 0.765822 | -8.000000 | 40.000000 | 40.000000 | 48.000000 | -28 |
| KXBTC15M-26MAY071315-15 | yes | yes | 0.798341 | -6.000000 | 40.000000 | 40.000000 | 46.000000 | 28 |
| KXBTC15M-26MAY071315-15 | yes | yes | 0.784166 | -14.000000 | 38.000000 | 38.000000 | 52.000000 | 28 |
