# v28 Composite False-Conviction Repair Stress

Research-only; no live bot changes or orders.

- Candidate: `skip_composite_false_conviction_repair_highest_raw_p`
- Freeze timestamp UTC: `2026-05-06T09:49:36.645793+00:00`
- Future denominator: `110`
- Delta versus target: `-184.000000c`

## Current Read

- Full candidate: 83 settled, 55/28, net -84.0c, coverage 75.45454545454545%.
- Delta versus target: -184.0c.
- Danger source mix: Counter({'rejected_actionable': 33}).
- Repair source mix: Counter({'approved_entry': 23, 'rejected_actionable': 13}).
- All avoided danger rows are reconstructed rejected-actionable rows so far; this is not enough live-approved proof.
- 13 repair rows are reconstructed; approved-only repair behavior must stay acceptable.
- Three ordinary full losses would erase current positive net.

## Scenario Stress

| scenario | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| target_control | 80 | 80 | 47/33 | 72.727273 | 100.000000 | 1.250000 |
| candidate_full | 83 | 83 | 55/28 | 75.454545 | -84.000000 | -1.012048 |
| skip_only_no_repairs | 47 | 47 | 31/16 | 42.727273 | 259.000000 | 5.510638 |
| approved_repairs_only | 70 | 70 | 49/21 | 63.636364 | 274.000000 | 3.914286 |
| rejected_repairs_only | 60 | 60 | 37/23 | 54.545455 | -99.000000 | -1.650000 |
| approved_source_candidate_rows_only | 28 | 28 | 23/5 | 25.454545 | 113.000000 | 4.035714 |
| rejected_source_candidate_rows_only | 55 | 55 | 32/23 | 50.000000 | -197.000000 | -3.581818 |

## Candidate Source Split

| source | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| approved_entry | 28 | 28 | 23/5 | 25.454545 | 113.000000 | 4.035714 |
| rejected_actionable | 55 | 55 | 32/23 | 50.000000 | -197.000000 | -3.581818 |

## Danger Source Split

| source | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| rejected_actionable | 33 | 33 | 16/17 | 30.000000 | -159.000000 | -4.818182 |

## Repair Source Split

| source | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| approved_entry | 23 | 23 | 18/5 | 20.909091 | 15.000000 | 0.652174 |
| rejected_actionable | 13 | 13 | 6/7 | 11.818182 | -358.000000 | -27.538462 |

## Candidate Side Split

| side | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| no | 34 | 34 | 26/8 | 30.909091 | 443.000000 | 13.029412 |
| yes | 49 | 49 | 29/20 | 44.545455 | -527.000000 | -10.755102 |

## Future Full-Loss Runway

| added full losses | stressed settled | stressed net c | still positive | sample gate met |
|---:|---:|---:|---:|---:|
| 1 | 84 | -184.000000 | False | True |
| 2 | 85 | -284.000000 | False | True |
| 3 | 86 | -384.000000 | False | True |
| 4 | 87 | -484.000000 | False | True |
| 5 | 88 | -584.000000 | False | True |

## Worst Leave-One Market

| market | removed rows | removed net c | net without market c | delta vs full c |
|---|---:|---:|---:|---:|
| KXBTC15M-26MAY070845-45 | 1 | 106.000000 | -190.000000 | -106.000000 |
| KXBTC15M-26MAY062200-00 | 1 | 104.000000 | -188.000000 | -104.000000 |
| KXBTC15M-26MAY060945-45 | 1 | 96.000000 | -180.000000 | -96.000000 |
| KXBTC15M-26MAY062000-00 | 1 | 96.000000 | -180.000000 | -96.000000 |
| KXBTC15M-26MAY060730-30 | 1 | 84.000000 | -168.000000 | -84.000000 |
| KXBTC15M-26MAY062145-45 | 1 | 82.000000 | -166.000000 | -82.000000 |
| KXBTC15M-26MAY060645-45 | 1 | 78.000000 | -162.000000 | -78.000000 |
| KXBTC15M-26MAY070130-30 | 1 | 78.000000 | -162.000000 | -78.000000 |
| KXBTC15M-26MAY061030-30 | 1 | 74.000000 | -158.000000 | -74.000000 |
| KXBTC15M-26MAY071145-45 | 1 | 74.000000 | -158.000000 | -74.000000 |

## Warnings

- All avoided danger rows are reconstructed rejected-actionable rows so far; this is not enough live-approved proof.
- 13 repair rows are reconstructed; approved-only repair behavior must stay acceptable.
- Three ordinary full losses would erase current positive net.
