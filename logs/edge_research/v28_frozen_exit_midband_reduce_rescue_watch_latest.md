# v28 Frozen Exit Midband Reduce Rescue Watch

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:07:59.468085+00:00`
- Watch freeze UTC: `2026-05-07T02:01:12.356709+00:00`
- Diagnostic source rows: `132`
- Post-birth rows: `42`

## Interpretation

- Research-only frozen watch; no live exits are changed.
- Diagnostic rows explain the mechanism only. Promotion evidence must come from post-birth rows after this watch freeze.
- The variants test lower-p_hold probability-reduce clips while avoiding rich-entry/high-p_hold states that caused current suppression harm.

## Diagnostic

| candidate | rows | suppressed | current c | candidate c | delta c | W/L -> candidate | loss delta | helpful/harmful | cushion | blockers |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---|
| midband_p60_75_exit50_75_asklt80 | 132 | 8 | 721.000000 | 1239.000000 | 518.000000 | 73/56 -> 81/48 | 8 | 8/0 | 5 | suppressed_decisions_lt_30 |
| midband_p65_75_exit50_75_asklt80 | 132 | 8 | 721.000000 | 1239.000000 | 518.000000 | 73/56 -> 81/48 | 8 | 8/0 | 5 | suppressed_decisions_lt_30 |
| midband_p60_75_exit50_70_asklt80 | 132 | 6 | 721.000000 | 1131.000000 | 410.000000 | 73/56 -> 79/50 | 6 | 6/0 | 4 | suppressed_decisions_lt_30 |
| midband_p60_75_exit50_75_asklt80_fairddgte0 | 132 | 6 | 721.000000 | 1099.000000 | 378.000000 | 73/56 -> 79/50 | 6 | 6/0 | 3 | suppressed_decisions_lt_30 |

## Post Birth

| candidate | rows | suppressed | current c | candidate c | delta c | W/L -> candidate | loss delta | helpful/harmful | cushion | blockers |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---|
| midband_p60_75_exit50_75_asklt80 | 42 | 1 | 534.000000 | 590.000000 | 56.000000 | 29/12 -> 30/11 | 1 | 1/0 | 0 | suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| midband_p60_75_exit50_75_asklt80_fairddgte0 | 42 | 1 | 534.000000 | 590.000000 | 56.000000 | 29/12 -> 30/11 | 1 | 1/0 | 0 | suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| midband_p65_75_exit50_75_asklt80 | 42 | 1 | 534.000000 | 590.000000 | 56.000000 | 29/12 -> 30/11 | 1 | 1/0 | 0 | suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| midband_p60_75_exit50_70_asklt80 | 42 | 0 | 534.000000 | 534.000000 | 0.000000 | 29/12 -> 29/12 | 0 | 0/0 | 0 | suppressed_decisions_lt_30, delta_not_positive, full_loss_cushion_lt_3 |

## Top Diagnostic Helpful Suppressions

| market | side | current c | hold c | delta c | p_hold | entry | exit |
|---|---|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY060700-00 | yes | -22.000000 | 50.000000 | 72.000000 | 0.748579 | 75 | 64 |
| KXBTC15M-26MAY060900-00 | no | -16.000000 | 54.000000 | 70.000000 | 0.721102 | 73 | 65 |
| KXBTC15M-26MAY060945-45 | no | -12.000000 | 58.000000 | 70.000000 | 0.735773 | 71 | 65 |
| KXBTC15M-26MAY061015-15 | no | -6.000000 | 64.000000 | 70.000000 | 0.733426 | 68 | 65 |
| KXBTC15M-26MAY060930-30 | no | -20.000000 | 48.000000 | 68.000000 | 0.725946 | 76 | 66 |
| KXBTC15M-26MAY060800-00 | yes | -18.000000 | 42.000000 | 60.000000 | 0.738185 | 79 | 70 |
| KXBTC15M-26MAY071230-30 | yes | -10.000000 | 46.000000 | 56.000000 | 0.749378 | 77 | 72 |
| KXBTC15M-26MAY060245-45 | yes | -6.000000 | 46.000000 | 52.000000 | 0.749392 | 77 | 74 |
