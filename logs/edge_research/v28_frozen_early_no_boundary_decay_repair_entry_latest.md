# v28 Frozen Early NO Boundary Decay Repair Entry

Research-only frozen forward validator; this does not place orders.

- Freeze timestamp UTC: `2026-05-06T09:10:09.146392+00:00`
- Candidate: `skip_early_no_boundary_decay_repair_calm_geometry`
- Base policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Future denominator: `113`
- Live ready: `True`
- Blockers: `none`

## Current Read

- Future candidate has 85 entries and 85 settled rows.
- Candidate net is 27.0c versus target -57.0c.
- Early/path-decay danger rows removed: 30; repair rows added: 32.

## Summaries

| surface | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| target | 83 | 83 | 48/35 | 73.451327 | -57.000000 | -0.686747 |
| danger_removed | 30 | 30 | 14/16 | 26.548673 | -314.000000 | -10.466667 |
| repair_added | 32 | 32 | 22/10 | 28.318584 | -230.000000 | -7.187500 |
| candidate | 85 | 85 | 56/29 | 75.221239 | 27.000000 | 0.317647 |

## Danger Rows

| market | side | p | ask | stc | abs d | recross | won | net c | reasons |
|---|---|---:|---:|---:|---:|---:|---|---:|---|
| KXBTC15M-26MAY060530-30 | yes | 0.588889 | 0.540000 | 829.016000 | 0.202598 | 0.884715 | False | -112.000000 | cheap_boundary_turbulence |
| KXBTC15M-26MAY060545-45 | no | 0.626642 | 0.440000 | 807.560000 | 0.323422 | 0.689053 | False | -92.000000 | early_no_boundary_decay |
| KXBTC15M-26MAY060630-30 | no | 0.675344 | 0.660000 | 868.927000 | 0.393798 | 0.762043 | False | -136.000000 | early_no_boundary_decay |
| KXBTC15M-26MAY060800-00 | yes | 0.523411 | 0.470000 | 884.129000 | 0.027808 | 1.358871 | True | 102.000000 | cheap_boundary_turbulence |
| KXBTC15M-26MAY060830-30 | no | 0.600730 | 0.590000 | 884.233000 | 0.286154 | 0.943700 | False | -122.000000 | early_no_boundary_decay |
| KXBTC15M-26MAY060915-15 | no | 0.672099 | 0.600000 | 869.636000 | 0.431641 | 0.831637 | True | 76.000000 | early_no_boundary_decay |
| KXBTC15M-26MAY061015-15 | no | 0.595554 | 0.520000 | 883.995000 | 0.274143 | 1.130150 | True | 92.000000 | early_no_boundary_decay |
| KXBTC15M-26MAY061045-45 | no | 0.601767 | 0.570000 | 868.842000 | 0.212683 | 1.191443 | False | -118.000000 | early_no_boundary_decay |
| KXBTC15M-26MAY061700-00 | no | 0.547299 | 0.490000 | 759.628000 | 0.145303 | 0.799916 | False | -102.000000 | early_no_boundary_decay, cheap_boundary_turbulence |
| KXBTC15M-26MAY061900-00 | yes | 0.501794 | 0.340000 | 766.143000 | 0.001392 | 0.794136 | True | 128.000000 | cheap_boundary_turbulence |
| KXBTC15M-26MAY061930-30 | yes | 0.551364 | 0.470000 | 810.397000 | 0.100563 | 0.905378 | True | 102.000000 | cheap_boundary_turbulence |
| KXBTC15M-26MAY061945-45 | yes | 0.542407 | 0.420000 | 809.092000 | 0.132650 | 0.801256 | False | -88.000000 | cheap_boundary_turbulence |
| KXBTC15M-26MAY062045-45 | no | 0.617920 | 0.510000 | 834.661000 | 0.321769 | 0.590304 | True | 94.000000 | early_no_boundary_decay |
| KXBTC15M-26MAY062130-30 | yes | 0.586142 | 0.410000 | 753.109000 | 0.212967 | 0.800157 | True | 114.000000 | cheap_boundary_turbulence |
| KXBTC15M-26MAY062215-15 | no | 0.661831 | 0.590000 | 850.282000 | 0.404187 | 0.669869 | True | 78.000000 | early_no_boundary_decay |
| KXBTC15M-26MAY062245-45 | no | 0.605951 | 0.540000 | 841.408000 | 0.278629 | 0.786584 | False | -112.000000 | early_no_boundary_decay |
| KXBTC15M-26MAY062345-45 | no | 0.608623 | 0.460000 | 723.265000 | 0.276153 | 0.675325 | False | -96.000000 | early_no_boundary_decay |
| KXBTC15M-26MAY070030-30 | no | 0.523605 | 0.330000 | 770.113000 | 0.059362 | 0.901651 | False | -70.000000 | early_no_boundary_decay, cheap_boundary_turbulence |
| KXBTC15M-26MAY070045-45 | no | 0.582164 | 0.480000 | 810.351000 | 0.187292 | 0.830545 | True | 100.000000 | early_no_boundary_decay, cheap_boundary_turbulence |
| KXBTC15M-26MAY070530-30 | no | 0.540822 | 0.480000 | 879.618000 | 0.132673 | 0.894668 | True | 100.000000 | early_no_boundary_decay, cheap_boundary_turbulence |
| KXBTC15M-26MAY070630-30 | yes | 0.606974 | 0.470000 | 875.963000 | 0.230767 | 0.826469 | False | -98.000000 | cheap_boundary_turbulence |
| KXBTC15M-26MAY070715-15 | yes | 0.560435 | 0.510000 | 812.253000 | 0.157545 | 0.877232 | True | 94.000000 | cheap_boundary_turbulence |
| KXBTC15M-26MAY070730-30 | yes | 0.530778 | 0.460000 | 819.643000 | 0.091964 | 0.936121 | False | -96.000000 | cheap_boundary_turbulence |
| KXBTC15M-26MAY070800-00 | yes | 0.536385 | 0.450000 | 771.226000 | 0.080069 | 0.865475 | False | -94.000000 | cheap_boundary_turbulence |
| KXBTC15M-26MAY070815-15 | yes | 0.501147 | 0.440000 | 882.524000 | 0.024626 | 1.067161 | True | 108.000000 | cheap_boundary_turbulence |
| KXBTC15M-26MAY070830-30 | yes | 0.514492 | 0.410000 | 811.825000 | 0.078942 | 0.952791 | False | -86.000000 | cheap_boundary_turbulence |
| KXBTC15M-26MAY070945-45 | no | 0.532085 | 0.480000 | 860.716000 | 0.067417 | 1.088863 | True | 100.000000 | early_no_boundary_decay, cheap_boundary_turbulence |
| KXBTC15M-26MAY071015-15 | no | 0.609894 | 0.600000 | 864.225000 | 0.287274 | 1.102864 | False | -124.000000 | early_no_boundary_decay |
| KXBTC15M-26MAY071030-30 | no | 0.646380 | 0.620000 | 852.539000 | 0.326478 | 1.053270 | True | 72.000000 | early_no_boundary_decay |
| KXBTC15M-26MAY071115-15 | no | 0.635838 | 0.620000 | 843.330000 | 0.346131 | 0.982771 | False | -128.000000 | early_no_boundary_decay |

## Repair Rows

| market | side | p | ask | abs d | recross | won | net c |
|---|---|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY070015-15 | no | 0.963659 | 0.700000 | 1.543579 | 0.073753 | False | -72.000000 |
| KXBTC15M-26MAY062115-15 | yes | 0.942571 | 0.730000 | 1.308547 | 0.239053 | True | 25.000000 |
| KXBTC15M-26MAY060715-15 | yes | 0.872115 | 0.810000 | 0.965012 | 0.333271 | True | 17.000000 |
| KXBTC15M-26MAY071045-45 | no | 0.865260 | 0.750000 | 0.953688 | 0.469918 | True | 22.000000 |
| KXBTC15M-26MAY071000-00 | no | 0.861629 | 0.730000 | 0.928896 | 0.483183 | True | 25.000000 |
| KXBTC15M-26MAY071330-30 | no | 0.864780 | 0.820000 | 0.927901 | 0.391694 | True | 16.000000 |
| KXBTC15M-26MAY060700-00 | yes | 0.865871 | 0.820000 | 0.923263 | 0.087353 | True | 15.000000 |
| KXBTC15M-26MAY071315-15 | yes | 0.865868 | 0.810000 | 0.919202 | 0.145450 | True | 17.000000 |
| KXBTC15M-26MAY061300-00 | yes | 0.860906 | 0.800000 | 0.913273 | 0.301730 | False | -82.000000 |
| KXBTC15M-26MAY071100-00 | yes | 0.853486 | 0.810000 | 0.906587 | 0.339564 | False | -84.000000 |
| KXBTC15M-26MAY071215-15 | no | 0.855912 | 0.800000 | 0.904673 | 0.237930 | True | 18.000000 |
| KXBTC15M-26MAY061000-00 | no | 0.854748 | 0.650000 | 0.901711 | 0.586664 | True | 31.000000 |
| KXBTC15M-26MAY060815-15 | no | 0.860153 | 0.790000 | 0.900687 | 0.395024 | True | 18.000000 |
| KXBTC15M-26MAY060745-45 | yes | 0.851843 | 0.690000 | 0.889718 | 0.303224 | False | -71.000000 |
| KXBTC15M-26MAY060615-15 | yes | 0.852040 | 0.750000 | 0.888798 | 0.328333 | True | 23.000000 |
| KXBTC15M-26MAY070930-30 | yes | 0.855936 | 0.800000 | 0.878792 | 0.375669 | True | 17.000000 |
| KXBTC15M-26MAY060900-00 | yes | 0.856054 | 0.780000 | 0.872054 | 0.423474 | False | -80.000000 |
| KXBTC15M-26MAY061245-45 | no | 0.740496 | 0.690000 | 0.583513 | 0.671557 | False | -72.000000 |
| KXBTC15M-26MAY061145-45 | no | 0.726968 | 0.700000 | 0.540451 | 0.437401 | True | 27.000000 |
| KXBTC15M-26MAY061530-30 | yes | 0.735905 | 0.700000 | 0.527347 | 0.218517 | True | 27.000000 |
| KXBTC15M-26MAY061115-15 | yes | 0.727568 | 0.690000 | 0.509565 | 0.603892 | False | -72.000000 |
| KXBTC15M-26MAY061415-15 | no | 0.661034 | 0.620000 | 0.381932 | 0.655098 | True | 34.000000 |
| KXBTC15M-26MAY071245-45 | yes | 0.636765 | 0.490000 | 0.350996 | 0.806353 | False | -53.000000 |
| KXBTC15M-26MAY061215-15 | no | 0.614405 | 0.580000 | 0.273193 | 0.815053 | False | -62.000000 |
| KXBTC15M-26MAY060845-45 | no | 0.605958 | 0.590000 | 0.234273 | 0.940026 | True | 37.000000 |
| KXBTC15M-26MAY062045-45 | no | 0.925277 | 0.800000 | 1.216600 | 0.180083 | True | 18.000000 |
| KXBTC15M-26MAY070030-30 | yes | 0.924288 | 0.820000 | 1.178593 | 0.175127 | True | 15.000000 |
| KXBTC15M-26MAY062215-15 | no | 0.889241 | 0.650000 | 1.024084 | 0.319525 | True | 33.000000 |
| KXBTC15M-26MAY070830-30 | no | 0.890215 | 0.770000 | 1.007446 | 0.126622 | True | 21.000000 |
| KXBTC15M-26MAY062130-30 | no | 0.887777 | 0.760000 | 0.999156 | 0.303870 | False | -78.000000 |
| KXBTC15M-26MAY060530-30 | no | 0.878245 | 0.780000 | 0.974192 | 0.253292 | True | 19.000000 |
| KXBTC15M-26MAY060830-30 | yes | 0.873796 | 0.760000 | 0.951357 | 0.307137 | True | 21.000000 |
