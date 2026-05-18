# v28 Early-NO Boundary Decay Repair Stress

Research-only; no live bot changes or orders.

- Candidate: `skip_early_no_boundary_decay_repair_calm_geometry`
- Freeze timestamp UTC: `2026-05-06T09:10:09.146392+00:00`
- Future denominator: `113`
- Delta versus target: `84.000000c`

## Current Read

- Full candidate: 85 settled, 56/29, net 27.0c, coverage 75.22123893805309%.
- Delta versus target: 84.0c.
- Danger source mix: Counter({'rejected_actionable': 30}).
- Repair source mix: Counter({'approved_entry': 21, 'rejected_actionable': 11}).
- All avoided danger rows are reconstructed rejected-actionable rows so far; this is useful physics evidence, but not enough live-approved proof.
- 11 repair rows are reconstructed; check approved-only repair performance before promotion.

## Scenario Stress

| scenario | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| target_control | 83 | 83 | 48/35 | 73.451327 | -57.000000 | -0.686747 |
| candidate_full | 85 | 85 | 56/29 | 75.221239 | 27.000000 | 0.317647 |
| skip_only_no_repairs | 53 | 53 | 34/19 | 46.902655 | 257.000000 | 4.849057 |
| approved_repairs_only | 74 | 74 | 50/24 | 65.486726 | 214.000000 | 2.891892 |
| rejected_repairs_only | 64 | 64 | 40/24 | 56.637168 | 70.000000 | 1.093750 |
| approved_source_candidate_rows_only | 26 | 26 | 21/5 | 23.008850 | 55.000000 | 2.115385 |
| rejected_source_candidate_rows_only | 59 | 59 | 35/24 | 52.212389 | -28.000000 | -0.474576 |

## Candidate Source Split

| source | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| approved_entry | 26 | 26 | 21/5 | 23.008850 | 55.000000 | 2.115385 |
| rejected_actionable | 59 | 59 | 35/24 | 52.212389 | -28.000000 | -0.474576 |

## Danger Source Split

| source | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| rejected_actionable | 30 | 30 | 14/16 | 26.548673 | -314.000000 | -10.466667 |

## Repair Source Split

| source | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| approved_entry | 21 | 21 | 16/5 | 18.584071 | -43.000000 | -2.047619 |
| rejected_actionable | 11 | 11 | 6/5 | 9.734513 | -187.000000 | -17.000000 |

## Danger Reason Split

| reason | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| cheap_boundary_turbulence | 17 | 17 | 9/8 | 15.044248 | 135.000000 | 7.941176 |
| early_no_boundary_decay | 18 | 18 | 8/10 | 15.929204 | -158.000000 | -8.777778 |

## Future Full-Loss Runway

| added full losses | stressed settled | stressed net c | still positive | sample gate met |
|---:|---:|---:|---:|---:|
| 1 | 86 | -73.000000 | False | True |
| 2 | 87 | -173.000000 | False | True |
| 3 | 88 | -273.000000 | False | True |
| 4 | 89 | -373.000000 | False | True |
| 5 | 90 | -473.000000 | False | True |

## Worst Leave-One Market

| market | removed rows | removed net c | net without market c | delta vs full c |
|---|---:|---:|---:|---:|
| KXBTC15M-26MAY070615-15 | 1 | 141.000000 | -114.000000 | -141.000000 |
| KXBTC15M-26MAY070845-45 | 1 | 106.000000 | -79.000000 | -106.000000 |
| KXBTC15M-26MAY062200-00 | 1 | 104.000000 | -77.000000 | -104.000000 |
| KXBTC15M-26MAY060945-45 | 1 | 96.000000 | -69.000000 | -96.000000 |
| KXBTC15M-26MAY062000-00 | 1 | 96.000000 | -69.000000 | -96.000000 |
| KXBTC15M-26MAY070900-00 | 1 | 86.000000 | -59.000000 | -86.000000 |
| KXBTC15M-26MAY060730-30 | 1 | 84.000000 | -57.000000 | -84.000000 |
| KXBTC15M-26MAY062145-45 | 1 | 82.000000 | -55.000000 | -82.000000 |
| KXBTC15M-26MAY060645-45 | 1 | 78.000000 | -51.000000 | -78.000000 |
| KXBTC15M-26MAY070130-30 | 1 | 78.000000 | -51.000000 | -78.000000 |

## Warnings

- All avoided danger rows are reconstructed rejected-actionable rows so far; this is useful physics evidence, but not enough live-approved proof.
- 11 repair rows are reconstructed; check approved-only repair performance before promotion.
