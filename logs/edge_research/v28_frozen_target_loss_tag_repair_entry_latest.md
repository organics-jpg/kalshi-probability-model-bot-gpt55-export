# v28 Frozen Target-Loss Tag Repair Entry

- Freeze timestamp UTC: `2026-05-06T08:59:17.610337+00:00`
- Candidate: `skip_target_loss_tags_repair_lowest_recross`
- Future denominator: `114`
- Needed/missed repairs: `30/25`
- Delta vs target: `-588.000000c`
- Blockers: `net_not_positive`

## Interpretation

- Future candidate has 86 entries and 86 settled rows.
- Candidate net is -731.0c versus target -143.0c.
- Target-loss rows removed: 28; repair rows added: 30.
- Promotion blockers: net_not_positive.

## Summaries

| slice | entries | settled | W/L | coverage | net c | avg net c |
|---|---:|---:|---:|---:|---:|---:|
| target | 84 | 84 | 48/36 | 73.684211 | -143.000000 | -1.702381 |
| danger_removed | 28 | 28 | 18/10 | 24.561404 | 380.000000 | 13.571429 |
| kept | 56 | 56 | 30/26 | 49.122807 | -523.000000 | -9.339286 |
| repairs | 30 | 30 | 20/10 | 26.315789 | -208.000000 | -6.933333 |
| candidate | 86 | 86 | 50/36 | 75.438596 | -731.000000 | -8.500000 |

## Removed Rows

| market | source | side | won | net c | p | ask | edge | abs d | recross | reasons |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY060515-15 | rejected_actionable | yes | False | -86.000000 | 0.532512 | 0.410000 | 0.122512 | 0.141500 | 0.958625 | weak_boundary_turbulence |
| KXBTC15M-26MAY060530-30 | rejected_actionable | yes | False | -112.000000 | 0.588889 | 0.540000 | 0.048889 | 0.202598 | 0.884715 | weak_boundary_turbulence |
| KXBTC15M-26MAY060600-00 | rejected_actionable | no | True | 47.000000 | 0.792357 | 0.750000 | 0.042357 | 0.672314 | 0.552274 | paid_high_price_thin_edge |
| KXBTC15M-26MAY060800-00 | rejected_actionable | yes | True | 102.000000 | 0.523411 | 0.470000 | 0.053411 | 0.027808 | 1.358871 | weak_boundary_turbulence |
| KXBTC15M-26MAY061100-00 | rejected_actionable | yes | False | -151.000000 | 0.740374 | 0.740000 | 0.000374 | 0.597049 | 0.809587 | paid_high_price_thin_edge |
| KXBTC15M-26MAY061200-00 | rejected_actionable | yes | True | 35.000000 | 0.848576 | 0.810000 | 0.038576 | 0.876136 | 0.613707 | paid_high_price_thin_edge |
| KXBTC15M-26MAY061445-45 | rejected_actionable | no | True | 55.000000 | 0.724164 | 0.710000 | 0.014164 | 0.536135 | 0.800263 | paid_high_price_thin_edge |
| KXBTC15M-26MAY061615-15 | rejected_actionable | yes | True | 49.000000 | 0.770727 | 0.740000 | 0.030727 | 0.652892 | 0.500664 | paid_high_price_thin_edge |
| KXBTC15M-26MAY061645-45 | rejected_actionable | no | True | 55.000000 | 0.736529 | 0.710000 | 0.026529 | 0.561593 | 0.588375 | paid_high_price_thin_edge |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | False | -102.000000 | 0.547299 | 0.490000 | 0.057299 | 0.145303 | 0.799916 | weak_boundary_turbulence |
| KXBTC15M-26MAY061900-00 | rejected_actionable | yes | True | 128.000000 | 0.501794 | 0.340000 | 0.161794 | 0.001392 | 0.794136 | weak_boundary_turbulence |
| KXBTC15M-26MAY061930-30 | rejected_actionable | yes | True | 102.000000 | 0.551364 | 0.470000 | 0.081364 | 0.100563 | 0.905378 | weak_boundary_turbulence |
| KXBTC15M-26MAY061945-45 | rejected_actionable | yes | False | -88.000000 | 0.542407 | 0.420000 | 0.122407 | 0.132650 | 0.801256 | weak_boundary_turbulence |
| KXBTC15M-26MAY062130-30 | rejected_actionable | yes | True | 114.000000 | 0.586142 | 0.410000 | 0.176142 | 0.212967 | 0.800157 | weak_boundary_turbulence |
| KXBTC15M-26MAY062300-00 | rejected_actionable | yes | True | 51.000000 | 0.758354 | 0.730000 | 0.028354 | 0.609402 | 0.572785 | paid_high_price_thin_edge |
| KXBTC15M-26MAY070030-30 | rejected_actionable | no | False | -70.000000 | 0.523605 | 0.330000 | 0.193605 | 0.059362 | 0.901651 | weak_boundary_turbulence |
| KXBTC15M-26MAY070045-45 | rejected_actionable | no | True | 100.000000 | 0.582164 | 0.480000 | 0.102164 | 0.187292 | 0.830545 | weak_boundary_turbulence |
| KXBTC15M-26MAY070145-45 | rejected_actionable | no | True | 35.000000 | 0.838040 | 0.810000 | 0.028040 | 0.811917 | 0.206140 | paid_high_price_thin_edge |
| KXBTC15M-26MAY070530-30 | rejected_actionable | no | True | 100.000000 | 0.540822 | 0.480000 | 0.060822 | 0.132673 | 0.894668 | weak_boundary_turbulence |
| KXBTC15M-26MAY070715-15 | rejected_actionable | yes | True | 94.000000 | 0.560435 | 0.510000 | 0.050435 | 0.157545 | 0.877232 | weak_boundary_turbulence |
| KXBTC15M-26MAY070730-30 | rejected_actionable | yes | False | -96.000000 | 0.530778 | 0.460000 | 0.070778 | 0.091964 | 0.936121 | weak_boundary_turbulence |
| KXBTC15M-26MAY070800-00 | rejected_actionable | yes | False | -94.000000 | 0.536385 | 0.450000 | 0.086385 | 0.080069 | 0.865475 | weak_boundary_turbulence |
| KXBTC15M-26MAY070815-15 | rejected_actionable | yes | True | 108.000000 | 0.501147 | 0.440000 | 0.061147 | 0.024626 | 1.067161 | weak_boundary_turbulence |
| KXBTC15M-26MAY070830-30 | rejected_actionable | yes | False | -86.000000 | 0.514492 | 0.410000 | 0.104492 | 0.078942 | 0.952791 | weak_boundary_turbulence |
| KXBTC15M-26MAY070900-00 | rejected_actionable | yes | True | 86.000000 | 0.597604 | 0.550000 | 0.047604 | 0.238237 | 0.771689 | weak_boundary_turbulence |
| KXBTC15M-26MAY070915-15 | rejected_actionable | no | True | 47.000000 | 0.788001 | 0.750000 | 0.038001 | 0.676857 | 0.519751 | paid_high_price_thin_edge |
| KXBTC15M-26MAY070945-45 | rejected_actionable | no | True | 100.000000 | 0.532085 | 0.480000 | 0.052085 | 0.067417 | 1.088863 | weak_boundary_turbulence |
| KXBTC15M-26MAY071230-30 | rejected_actionable | no | False | -143.000000 | 0.729882 | 0.700000 | 0.029882 | 0.573733 | 0.815016 | paid_high_price_thin_edge |

## Repair Rows

| market | source | side | won | net c | p | ask | edge | abs d | recross |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.700000 | 0.263659 | 1.543579 | 0.073753 |
| KXBTC15M-26MAY070930-30 | rejected_actionable | no | False | -65.000000 | 0.656126 | 0.610000 | 0.046126 | 0.394183 | 0.081541 |
| KXBTC15M-26MAY060700-00 | rejected_actionable | yes | True | 15.000000 | 0.865871 | 0.820000 | 0.045871 | 0.923263 | 0.087353 |
| KXBTC15M-26MAY060900-00 | approved_entry | no | True | 18.000000 | 0.853869 | 0.790000 | 0.063869 | 0.854076 | 0.110422 |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 0.850827 | 0.780000 | 0.070827 | 0.850077 | 0.132426 |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -80.000000 | 0.850438 | 0.780000 | 0.070438 | 0.862815 | 0.173125 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | yes | True | 27.000000 | 0.735905 | 0.700000 | 0.035905 | 0.527347 | 0.218517 |
| KXBTC15M-26MAY071215-15 | approved_entry | no | True | 18.000000 | 0.855912 | 0.800000 | 0.055912 | 0.904673 | 0.237930 |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 0.942571 | 0.730000 | 0.212571 | 1.308547 | 0.239053 |
| KXBTC15M-26MAY060615-15 | rejected_actionable | yes | True | 27.000000 | 0.728033 | 0.700000 | 0.028033 | 0.540997 | 0.296225 |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.860906 | 0.800000 | 0.060906 | 0.913273 | 0.301730 |
| KXBTC15M-26MAY060715-15 | approved_entry | yes | True | 17.000000 | 0.872115 | 0.810000 | 0.062115 | 0.965012 | 0.333271 |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -63.000000 | 0.647368 | 0.590000 | 0.057368 | 0.324579 | 0.338898 |
| KXBTC15M-26MAY071100-00 | rejected_actionable | yes | False | -84.000000 | 0.853486 | 0.810000 | 0.043486 | 0.906587 | 0.339564 |
| KXBTC15M-26MAY071330-30 | rejected_actionable | no | True | 16.000000 | 0.864780 | 0.820000 | 0.044780 | 0.927901 | 0.391694 |
| KXBTC15M-26MAY060815-15 | approved_entry | no | True | 18.000000 | 0.860153 | 0.790000 | 0.070153 | 0.900687 | 0.395024 |
| KXBTC15M-26MAY061145-45 | rejected_actionable | no | True | 27.000000 | 0.726968 | 0.700000 | 0.026968 | 0.540451 | 0.437401 |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 22.000000 | 0.865260 | 0.750000 | 0.115260 | 0.953688 | 0.469918 |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 25.000000 | 0.861629 | 0.730000 | 0.131629 | 0.928896 | 0.483183 |
| KXBTC15M-26MAY061000-00 | approved_entry | no | True | 31.000000 | 0.854748 | 0.650000 | 0.204748 | 0.901711 | 0.586664 |
| KXBTC15M-26MAY061415-15 | rejected_actionable | no | True | 34.000000 | 0.661034 | 0.620000 | 0.041034 | 0.381932 | 0.655098 |
| KXBTC15M-26MAY061245-45 | rejected_actionable | no | False | -72.000000 | 0.740496 | 0.690000 | 0.050496 | 0.583513 | 0.671557 |
| KXBTC15M-26MAY071245-45 | rejected_actionable | yes | False | -53.000000 | 0.636765 | 0.490000 | 0.146765 | 0.350996 | 0.806353 |
| KXBTC15M-26MAY061215-15 | rejected_actionable | no | False | -62.000000 | 0.614405 | 0.580000 | 0.034405 | 0.273193 | 0.815053 |
| KXBTC15M-26MAY060845-45 | rejected_actionable | no | True | 37.000000 | 0.605958 | 0.590000 | 0.015958 | 0.234273 | 0.940026 |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | 20.000000 | 0.852625 | 0.770000 | 0.082625 | 0.865277 | 0.087809 |
| KXBTC15M-26MAY060515-15 | approved_entry | no | True | 23.000000 | 0.884180 | 0.740000 | 0.144180 | 0.969762 | 0.123272 |
| KXBTC15M-26MAY060800-00 | approved_entry | yes | True | 32.000000 | 0.874265 | 0.660000 | 0.214265 | 0.931829 | 0.130377 |
| KXBTC15M-26MAY070030-30 | approved_entry | yes | True | 15.000000 | 0.924288 | 0.820000 | 0.104288 | 1.178593 | 0.175127 |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | False | -42.000000 | 0.788347 | 0.380000 | 0.408347 | 0.665443 | 0.196391 |
