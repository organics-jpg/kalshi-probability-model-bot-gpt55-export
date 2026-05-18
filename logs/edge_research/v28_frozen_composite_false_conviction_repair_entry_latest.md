# v28 Frozen Composite False-Conviction Repair Entry

Research-only frozen forward validator; this does not place orders.

- Freeze timestamp UTC: `2026-05-06T09:49:36.645793+00:00`
- Candidate: `skip_composite_false_conviction_repair_highest_raw_p`
- Base policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Future denominator: `110`
- Needed repairs: `36`
- Missed repairs available: `25`
- Candidate live ready: `False`
- Blockers: `net_not_positive`

## Summaries

| slice | entries | settled | W/L | coverage | net c | avg net c |
|---|---:|---:|---:|---:|---:|---:|
| target | 80 | 80 | 47/33 | 72.727273 | 100.000000 | 1.250000 |
| danger_removed | 33 | 33 | 16/17 | 30.000000 | -159.000000 | -4.818182 |
| repair_rows | 36 | 36 | 24/12 | 32.727273 | -343.000000 | -9.527778 |
| candidate | 83 | 83 | 55/28 | 75.454545 | -84.000000 | -1.012048 |

## Interpretation

- Future candidate has 83 entries and 83 settled rows.
- Candidate net is -84.0c versus target 100.0c.
- Composite false-conviction rows removed: 33; repair rows added: 36.
- Promotion blockers: net_not_positive.

## Repair Rows

| market | source | side | won | net c | p | ask | edge | recross | abs d |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.700000 | 0.263659 | 0.073753 | 1.543579 |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 0.942571 | 0.730000 | 0.212571 | 0.239053 | 1.308547 |
| KXBTC15M-26MAY060715-15 | approved_entry | yes | True | 17.000000 | 0.872115 | 0.810000 | 0.062115 | 0.333271 | 0.965012 |
| KXBTC15M-26MAY060700-00 | rejected_actionable | yes | True | 15.000000 | 0.865871 | 0.820000 | 0.045871 | 0.087353 | 0.923263 |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 17.000000 | 0.865868 | 0.810000 | 0.055868 | 0.145450 | 0.919202 |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 22.000000 | 0.865260 | 0.750000 | 0.115260 | 0.469918 | 0.953688 |
| KXBTC15M-26MAY071330-30 | rejected_actionable | no | True | 16.000000 | 0.864780 | 0.820000 | 0.044780 | 0.391694 | 0.927901 |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 25.000000 | 0.861629 | 0.730000 | 0.131629 | 0.483183 | 0.928896 |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.860906 | 0.800000 | 0.060906 | 0.301730 | 0.913273 |
| KXBTC15M-26MAY060815-15 | approved_entry | no | True | 18.000000 | 0.860153 | 0.790000 | 0.070153 | 0.395024 | 0.900687 |
| KXBTC15M-26MAY060900-00 | rejected_actionable | yes | False | -85.000000 | 0.856369 | 0.820000 | 0.036369 | 0.194746 | 0.849928 |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 17.000000 | 0.855936 | 0.800000 | 0.055936 | 0.375669 | 0.878792 |
| KXBTC15M-26MAY071215-15 | approved_entry | no | True | 18.000000 | 0.855912 | 0.800000 | 0.055912 | 0.237930 | 0.904673 |
| KXBTC15M-26MAY061000-00 | approved_entry | no | True | 31.000000 | 0.854748 | 0.650000 | 0.204748 | 0.586664 | 0.901711 |
| KXBTC15M-26MAY071100-00 | rejected_actionable | yes | False | -84.000000 | 0.853486 | 0.810000 | 0.043486 | 0.339564 | 0.906587 |
| KXBTC15M-26MAY060615-15 | approved_entry | yes | True | 23.000000 | 0.852040 | 0.750000 | 0.102040 | 0.328333 | 0.888798 |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -71.000000 | 0.851843 | 0.690000 | 0.161843 | 0.303224 | 0.889718 |
| KXBTC15M-26MAY061245-45 | rejected_actionable | no | False | -72.000000 | 0.740496 | 0.690000 | 0.050496 | 0.671557 | 0.583513 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | yes | True | 27.000000 | 0.735905 | 0.700000 | 0.035905 | 0.218517 | 0.527347 |
| KXBTC15M-26MAY061145-45 | rejected_actionable | yes | False | -74.000000 | 0.732848 | 0.710000 | 0.022848 | 0.613876 | 0.535356 |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -72.000000 | 0.727568 | 0.690000 | 0.037568 | 0.603892 | 0.509565 |
| KXBTC15M-26MAY061415-15 | rejected_actionable | no | True | 34.000000 | 0.661034 | 0.620000 | 0.041034 | 0.655098 | 0.381932 |
| KXBTC15M-26MAY071245-45 | rejected_actionable | yes | False | -53.000000 | 0.636765 | 0.490000 | 0.146765 | 0.806353 | 0.350996 |
| KXBTC15M-26MAY061215-15 | rejected_actionable | no | False | -62.000000 | 0.614405 | 0.580000 | 0.034405 | 0.815053 | 0.273193 |
| KXBTC15M-26MAY060845-45 | rejected_actionable | no | True | 37.000000 | 0.605958 | 0.590000 | 0.015958 | 0.940026 | 0.234273 |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | 18.000000 | 0.925277 | 0.800000 | 0.125277 | 0.180083 | 1.216600 |
| KXBTC15M-26MAY070030-30 | approved_entry | yes | True | 15.000000 | 0.924288 | 0.820000 | 0.104288 | 0.175127 | 1.178593 |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | 21.000000 | 0.890215 | 0.770000 | 0.120215 | 0.126622 | 1.007446 |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | 33.000000 | 0.889241 | 0.650000 | 0.239241 | 0.319525 | 1.024084 |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.887777 | 0.760000 | 0.127777 | 0.303870 | 0.999156 |
| KXBTC15M-26MAY060800-00 | approved_entry | yes | True | 32.000000 | 0.874265 | 0.660000 | 0.214265 | 0.130377 | 0.931829 |
| KXBTC15M-26MAY060830-30 | approved_entry | yes | True | 21.000000 | 0.873796 | 0.760000 | 0.113796 | 0.307137 | 0.951357 |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -83.000000 | 0.866013 | 0.810000 | 0.056013 | 0.380974 | 0.948846 |
| KXBTC15M-26MAY061045-45 | approved_entry | yes | True | 18.000000 | 0.861569 | 0.800000 | 0.061569 | 0.408876 | 0.917282 |
| KXBTC15M-26MAY061015-15 | approved_entry | no | True | 30.000000 | 0.859312 | 0.680000 | 0.179312 | 0.581489 | 0.912125 |
| KXBTC15M-26MAY060630-30 | rejected_actionable | yes | True | 15.000000 | 0.858957 | 0.820000 | 0.038957 | 0.182821 | 0.898392 |
