# v28 Frozen Low-Recross Repair Entry

- Freeze timestamp UTC: `2026-05-06T06:55:26.848310+00:00`
- Candidate: `skip_paid_or_weak_boundary_repair_lowest_recross`
- Future denominator: `122`
- Needed/missed repairs: `31/26`
- Delta vs target: `282.000000c`
- Blockers: `net_not_positive`

## Interpretation

- Future candidate has 92 entries and 92 settled rows.
- Candidate net is -217.0c versus target -499.0c.
- Danger rows removed: 28; repair rows added: 31.
- Promotion blockers: net_not_positive.

## Summaries

| slice | entries | settled | W/L | coverage | net c | avg net c |
|---|---:|---:|---:|---:|---:|---:|
| target | 89 | 89 | 49/40 | 72.950820 | -499.000000 | -5.606742 |
| danger_removed | 28 | 28 | 14/14 | 22.950820 | -412.000000 | -14.714286 |
| kept | 61 | 61 | 35/26 | 50.000000 | -87.000000 | -1.426230 |
| repairs | 31 | 31 | 22/9 | 25.409836 | -130.000000 | -4.193548 |
| candidate | 92 | 92 | 57/35 | 75.409836 | -217.000000 | -2.358696 |

## Repair Rows

| market | source | side | won | net c | p | ask | edge | recross | abs d |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.700000 | 0.263659 | 0.073753 | 1.543579 |
| KXBTC15M-26MAY070930-30 | rejected_actionable | no | False | -65.000000 | 0.656126 | 0.610000 | 0.046126 | 0.081541 | 0.394183 |
| KXBTC15M-26MAY060700-00 | rejected_actionable | yes | True | 15.000000 | 0.865871 | 0.820000 | 0.045871 | 0.087353 | 0.923263 |
| KXBTC15M-26MAY060900-00 | approved_entry | no | True | 18.000000 | 0.853869 | 0.790000 | 0.063869 | 0.110422 | 0.854076 |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 0.850827 | 0.780000 | 0.070827 | 0.132426 | 0.850077 |
| KXBTC15M-26MAY060315-15 | rejected_actionable | yes | True | 16.000000 | 0.854395 | 0.810000 | 0.044395 | 0.163136 | 0.837534 |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -80.000000 | 0.850438 | 0.780000 | 0.070438 | 0.173125 | 0.862815 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | yes | True | 27.000000 | 0.735905 | 0.700000 | 0.035905 | 0.218517 | 0.527347 |
| KXBTC15M-26MAY071215-15 | approved_entry | no | True | 18.000000 | 0.855912 | 0.800000 | 0.055912 | 0.237930 | 0.904673 |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 0.942571 | 0.730000 | 0.212571 | 0.239053 | 1.308547 |
| KXBTC15M-26MAY060615-15 | rejected_actionable | yes | True | 27.000000 | 0.728033 | 0.700000 | 0.028033 | 0.296225 | 0.540997 |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.860906 | 0.800000 | 0.060906 | 0.301730 | 0.913273 |
| KXBTC15M-26MAY060715-15 | approved_entry | yes | True | 17.000000 | 0.872115 | 0.810000 | 0.062115 | 0.333271 | 0.965012 |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -63.000000 | 0.647368 | 0.590000 | 0.057368 | 0.338898 | 0.324579 |
| KXBTC15M-26MAY071100-00 | rejected_actionable | yes | False | -84.000000 | 0.853486 | 0.810000 | 0.043486 | 0.339564 | 0.906587 |
| KXBTC15M-26MAY071330-30 | rejected_actionable | no | True | 16.000000 | 0.864780 | 0.820000 | 0.044780 | 0.391694 | 0.927901 |
| KXBTC15M-26MAY060815-15 | approved_entry | no | True | 18.000000 | 0.860153 | 0.790000 | 0.070153 | 0.395024 | 0.900687 |
| KXBTC15M-26MAY061145-45 | rejected_actionable | no | True | 27.000000 | 0.726968 | 0.700000 | 0.026968 | 0.437401 | 0.540451 |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 22.000000 | 0.865260 | 0.750000 | 0.115260 | 0.469918 | 0.953688 |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 25.000000 | 0.861629 | 0.730000 | 0.131629 | 0.483183 | 0.928896 |
| KXBTC15M-26MAY061000-00 | approved_entry | no | True | 31.000000 | 0.854748 | 0.650000 | 0.204748 | 0.586664 | 0.901711 |
| KXBTC15M-26MAY061415-15 | rejected_actionable | no | True | 34.000000 | 0.661034 | 0.620000 | 0.041034 | 0.655098 | 0.381932 |
| KXBTC15M-26MAY061245-45 | rejected_actionable | no | False | -72.000000 | 0.740496 | 0.690000 | 0.050496 | 0.671557 | 0.583513 |
| KXBTC15M-26MAY071245-45 | rejected_actionable | yes | False | -53.000000 | 0.636765 | 0.490000 | 0.146765 | 0.806353 | 0.350996 |
| KXBTC15M-26MAY061215-15 | rejected_actionable | no | False | -62.000000 | 0.614405 | 0.580000 | 0.034405 | 0.815053 | 0.273193 |
| KXBTC15M-26MAY060845-45 | rejected_actionable | no | True | 37.000000 | 0.605958 | 0.590000 | 0.015958 | 0.940026 | 0.234273 |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | 20.000000 | 0.852625 | 0.770000 | 0.082625 | 0.087809 | 0.865277 |
| KXBTC15M-26MAY071200-00 | approved_entry | no | True | 20.000000 | 0.859141 | 0.770000 | 0.089141 | 0.089529 | 0.918677 |
| KXBTC15M-26MAY060515-15 | approved_entry | no | True | 23.000000 | 0.884180 | 0.740000 | 0.144180 | 0.123272 | 0.969762 |
| KXBTC15M-26MAY060800-00 | approved_entry | yes | True | 32.000000 | 0.874265 | 0.660000 | 0.214265 | 0.130377 | 0.931829 |
| KXBTC15M-26MAY060630-30 | rejected_actionable | yes | True | 15.000000 | 0.858957 | 0.820000 | 0.038957 | 0.182821 | 0.898392 |
