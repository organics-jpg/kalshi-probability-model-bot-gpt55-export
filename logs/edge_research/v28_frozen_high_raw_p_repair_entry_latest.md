# v28 Frozen High-Raw-P Repair Entry

- Freeze timestamp UTC: `2026-05-06T07:59:24.730118+00:00`
- Candidate: `skip_paid_or_weak_boundary_repair_highest_raw_p`
- Future denominator: `118`
- Needed/missed repairs: `29/25`
- Delta vs target: `27.000000c`
- Blockers: `net_not_positive`

## Interpretation

- Future candidate has 89 entries and 89 settled rows.
- Candidate net is -274.0c versus target -301.0c.
- Danger rows removed: 27; repair rows added: 29.
- Promotion blockers: net_not_positive.

## Summaries

| slice | entries | settled | W/L | coverage | net c | avg net c |
|---|---:|---:|---:|---:|---:|---:|
| target | 87 | 87 | 49/38 | 73.728814 | -301.000000 | -3.459770 |
| danger_removed | 27 | 27 | 14/13 | 22.881356 | -332.000000 | -12.296296 |
| kept | 60 | 60 | 35/25 | 50.847458 | 31.000000 | 0.516667 |
| repairs | 29 | 29 | 19/10 | 24.576271 | -305.000000 | -10.517241 |
| candidate | 89 | 89 | 54/35 | 75.423729 | -274.000000 | -3.078652 |

## Repair Rows

| market | source | side | won | net c | p | ask | edge | recross | abs d | score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.700000 | 0.263659 | 0.073753 | 1.543579 | 0.963659 |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 0.942571 | 0.730000 | 0.212571 | 0.239053 | 1.308547 | 0.942571 |
| KXBTC15M-26MAY060715-15 | approved_entry | yes | True | 17.000000 | 0.872115 | 0.810000 | 0.062115 | 0.333271 | 0.965012 | 0.872115 |
| KXBTC15M-26MAY060700-00 | rejected_actionable | yes | True | 15.000000 | 0.865871 | 0.820000 | 0.045871 | 0.087353 | 0.923263 | 0.865871 |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 17.000000 | 0.865868 | 0.810000 | 0.055868 | 0.145450 | 0.919202 | 0.865868 |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 22.000000 | 0.865260 | 0.750000 | 0.115260 | 0.469918 | 0.953688 | 0.865260 |
| KXBTC15M-26MAY071330-30 | rejected_actionable | no | True | 16.000000 | 0.864780 | 0.820000 | 0.044780 | 0.391694 | 0.927901 | 0.864780 |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 25.000000 | 0.861629 | 0.730000 | 0.131629 | 0.483183 | 0.928896 | 0.861629 |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.860906 | 0.800000 | 0.060906 | 0.301730 | 0.913273 | 0.860906 |
| KXBTC15M-26MAY060815-15 | approved_entry | no | True | 18.000000 | 0.860153 | 0.790000 | 0.070153 | 0.395024 | 0.900687 | 0.860153 |
| KXBTC15M-26MAY060900-00 | rejected_actionable | yes | False | -85.000000 | 0.856369 | 0.820000 | 0.036369 | 0.194746 | 0.849928 | 0.856369 |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 17.000000 | 0.855936 | 0.800000 | 0.055936 | 0.375669 | 0.878792 | 0.855936 |
| KXBTC15M-26MAY071215-15 | approved_entry | no | True | 18.000000 | 0.855912 | 0.800000 | 0.055912 | 0.237930 | 0.904673 | 0.855912 |
| KXBTC15M-26MAY061000-00 | approved_entry | no | True | 31.000000 | 0.854748 | 0.650000 | 0.204748 | 0.586664 | 0.901711 | 0.854748 |
| KXBTC15M-26MAY071100-00 | rejected_actionable | yes | False | -84.000000 | 0.853486 | 0.810000 | 0.043486 | 0.339564 | 0.906587 | 0.853486 |
| KXBTC15M-26MAY060615-15 | approved_entry | yes | True | 23.000000 | 0.852040 | 0.750000 | 0.102040 | 0.328333 | 0.888798 | 0.852040 |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -71.000000 | 0.851843 | 0.690000 | 0.161843 | 0.303224 | 0.889718 | 0.851843 |
| KXBTC15M-26MAY061245-45 | rejected_actionable | no | False | -72.000000 | 0.740496 | 0.690000 | 0.050496 | 0.671557 | 0.583513 | 0.740496 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | yes | True | 27.000000 | 0.735905 | 0.700000 | 0.035905 | 0.218517 | 0.527347 | 0.735905 |
| KXBTC15M-26MAY061145-45 | rejected_actionable | yes | False | -74.000000 | 0.732848 | 0.710000 | 0.022848 | 0.613876 | 0.535356 | 0.732848 |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -72.000000 | 0.727568 | 0.690000 | 0.037568 | 0.603892 | 0.509565 | 0.727568 |
| KXBTC15M-26MAY061415-15 | rejected_actionable | no | True | 34.000000 | 0.661034 | 0.620000 | 0.041034 | 0.655098 | 0.381932 | 0.661034 |
| KXBTC15M-26MAY071245-45 | rejected_actionable | yes | False | -53.000000 | 0.636765 | 0.490000 | 0.146765 | 0.806353 | 0.350996 | 0.636765 |
| KXBTC15M-26MAY061215-15 | rejected_actionable | no | False | -62.000000 | 0.614405 | 0.580000 | 0.034405 | 0.815053 | 0.273193 | 0.614405 |
| KXBTC15M-26MAY060845-45 | rejected_actionable | no | True | 37.000000 | 0.605958 | 0.590000 | 0.015958 | 0.940026 | 0.234273 | 0.605958 |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | 21.000000 | 0.890215 | 0.770000 | 0.120215 | 0.126622 | 1.007446 | 0.890215 |
| KXBTC15M-26MAY060515-15 | approved_entry | no | True | 23.000000 | 0.884180 | 0.740000 | 0.144180 | 0.123272 | 0.969762 | 0.884180 |
| KXBTC15M-26MAY060530-30 | approved_entry | no | True | 19.000000 | 0.878245 | 0.780000 | 0.098245 | 0.253292 | 0.974192 | 0.878245 |
| KXBTC15M-26MAY061130-30 | approved_entry | yes | True | 17.000000 | 0.877418 | 0.800000 | 0.077418 | 0.536330 | 0.989346 | 0.877418 |
