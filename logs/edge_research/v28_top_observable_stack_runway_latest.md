# v28 Top Observable Stack Runway

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:53:25.273132+00:00`
- Freeze UTC: `2026-05-07T10:29:46.104521+00:00`
- Policy: `diagnostic_observable_mid_confidence_parent_fill_quarter`
- Gate decision: `no_live_test`
- Open live positions: `0`
- Live baseline: `2215.000c`
- Broad/sidecar eligible: `0/0`

## Diagnostic

- Settled: `76`
- W/L: `67/9`
- Coverage: `75.248%`
- Net: `2233.000c`
- Reconstructed share: `0.342`
- Full-loss cushion: `22`
- Blockers: `diagnostic_prefreeze, source_gate_zero_row_margin`

## Strict Forward

- Settled: `21`
- W/L: `19/2`
- Coverage: `75.000%`
- Net: `194.000c`
- Rows needed for 30: `9`
- Net needed to beat live: `2022.000c`
- Net needed for cushion 3: `106.000c`
- Full-loss cushion: `1`
- Blockers: `settled_lt_30, full_loss_cushion_lt_3, controlled_live_test_gate_not_passed`

## Runway

- Future denominator: `28`
- Future observation rows: `1157`
- Broad pass rows: `89`
- Selected parent rows: `24`
- Selected pending rows: `0`
- Settled exit-clock joins: `10`

## Pending Rows

| market | side | source | raw edge | recross | abs d | ask | weight |
|---|---|---|---:|---:|---:|---:|---:|

## Settled Strict Rows

| market | side | source | component | pnl | won | raw edge | recross | abs d | ask |
|---|---|---|---|---:|---|---:|---:|---:|---:|
| KXBTC15M-26MAY071100-00 | yes | approved_entry | strict_delayed_recheck_rescue:drop15_bid60 | -166.000 | False | 0.054 | 0.305 | 1.010 | 0.830 |
| KXBTC15M-26MAY071015-15 | no | approved_entry | strict_delayed_recheck_rescue:drop15_bid60 | -162.000 | False | 0.081 | 0.418 | 0.936 | 0.780 |
| KXBTC15M-26MAY071030-30 | no | rejected_actionable | strict_parent_midprice_hold_fill | 7.000 | True | 0.057 | 0.180 | 1.626 | 0.910 |
| KXBTC15M-26MAY070715-15 | yes | rejected_actionable | strict_parent_midprice_hold_fill | 8.000 | True | 0.081 | 0.051 | 2.281 | 0.910 |
| KXBTC15M-26MAY071300-00 | no | rejected_actionable | strict_parent_midprice_hold_fill | 8.000 | True | 0.038 | 0.062 | 1.290 | 0.900 |
| KXBTC15M-26MAY071245-45 | no | rejected_actionable | strict_parent_midprice_hold_fill | 8.000 | True | 0.034 | 0.231 | 1.286 | 0.900 |
| KXBTC15M-26MAY071130-30 | no | approved_entry | strict_parent_midprice_hold_fill | 13.000 | True | 0.067 | 0.332 | 1.183 | 0.850 |
| KXBTC15M-26MAY070645-45 | yes | approved_entry | strict_parent_midprice_hold_fill | 16.000 | True | 0.085 | 0.369 | 1.014 | 0.810 |
| KXBTC15M-26MAY070815-15 | yes | approved_entry | strict_delayed_recheck_rescue:drop15_bid60 | 20.000 | True | 0.051 | 0.186 | 1.397 | 0.900 |
| KXBTC15M-26MAY070915-15 | no | approved_entry | strict_parent_midprice_hold_fill | 20.000 | True | 0.107 | 0.284 | 0.951 | 0.770 |
| KXBTC15M-26MAY070830-30 | no | approved_entry | strict_parent_midprice_hold_fill | 21.000 | True | 0.120 | 0.127 | 1.007 | 0.770 |
| KXBTC15M-26MAY071230-30 | yes | approved_entry | strict_parent_midprice_hold_fill | 21.000 | True | 0.082 | 0.296 | 0.882 | 0.770 |
| KXBTC15M-26MAY071045-45 | no | approved_entry | strict_parent_midprice_hold_fill | 22.000 | True | 0.115 | 0.470 | 0.954 | 0.750 |
| KXBTC15M-26MAY070945-45 | no | approved_entry | strict_parent_midprice_hold_fill | 28.000 | True | 0.164 | 0.436 | 0.883 | 0.690 |

## Interpretation

- Research-only runway watch; no live bot changes or orders.
- Diagnostic top row is 2233.0c with W/L 67/9.
- Strict proof has 21 settled rows and needs 9 more to reach the minimum sample gate.
- A zero strict score is not failure yet; it means the child has not accumulated settled post-freeze rows.
