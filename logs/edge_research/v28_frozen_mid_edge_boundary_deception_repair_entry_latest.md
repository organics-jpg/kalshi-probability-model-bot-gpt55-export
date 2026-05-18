# v28 Frozen Mid-Edge Boundary Deception Repair Entry

Research-only frozen forward validator; this does not place orders.

- Freeze timestamp UTC: `2026-05-06T09:23:03.299714+00:00`
- Candidate: `skip_mid_edge_boundary_deception_repair_stable_geometry`
- Base policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Future denominator: `112`
- Live ready: `False`
- Blockers: `net_not_positive`

## Current Read

- Future candidate has 84 entries and 84 settled rows.
- Candidate net is -431.0c versus target 55.0c.
- Mid-edge boundary-deception rows removed: 13; repair rows added: 15.
- Promotion blockers: net_not_positive.

## Summaries

| surface | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| target | 82 | 82 | 48/34 | 73.214286 | 55.000000 | 0.670732 |
| danger_removed | 13 | 13 | 9/4 | 11.607143 | 404.000000 | 31.076923 |
| repair_added | 15 | 15 | 11/4 | 13.392857 | -82.000000 | -5.466667 |
| candidate | 84 | 84 | 50/34 | 75.000000 | -431.000000 | -5.130952 |

## Danger Rows

| market | side | p | ask | edge | stc | abs d | recross | won | net c |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| KXBTC15M-26MAY060800-00 | yes | 0.523411 | 0.470000 | 0.053411 | 884.129000 | 0.027808 | 1.358871 | True | 102.000000 |
| KXBTC15M-26MAY060915-15 | no | 0.672099 | 0.600000 | 0.072099 | 869.636000 | 0.431641 | 0.831637 | True | 76.000000 |
| KXBTC15M-26MAY061015-15 | no | 0.595554 | 0.520000 | 0.075554 | 883.995000 | 0.274143 | 1.130150 | True | 92.000000 |
| KXBTC15M-26MAY061700-00 | no | 0.547299 | 0.490000 | 0.057299 | 759.628000 | 0.145303 | 0.799916 | False | -102.000000 |
| KXBTC15M-26MAY062215-15 | no | 0.661831 | 0.590000 | 0.071831 | 850.282000 | 0.404187 | 0.669869 | True | 78.000000 |
| KXBTC15M-26MAY062245-45 | no | 0.605951 | 0.540000 | 0.065951 | 841.408000 | 0.278629 | 0.786584 | False | -112.000000 |
| KXBTC15M-26MAY070530-30 | no | 0.540822 | 0.480000 | 0.060822 | 879.618000 | 0.132673 | 0.894668 | True | 100.000000 |
| KXBTC15M-26MAY070715-15 | yes | 0.560435 | 0.510000 | 0.050435 | 812.253000 | 0.157545 | 0.877232 | True | 94.000000 |
| KXBTC15M-26MAY070730-30 | yes | 0.530778 | 0.460000 | 0.070778 | 819.643000 | 0.091964 | 0.936121 | False | -96.000000 |
| KXBTC15M-26MAY070815-15 | yes | 0.501147 | 0.440000 | 0.061147 | 882.524000 | 0.024626 | 1.067161 | True | 108.000000 |
| KXBTC15M-26MAY070900-00 | yes | 0.597604 | 0.550000 | 0.047604 | 773.230000 | 0.238237 | 0.771689 | True | 86.000000 |
| KXBTC15M-26MAY070945-45 | no | 0.532085 | 0.480000 | 0.052085 | 860.716000 | 0.067417 | 1.088863 | True | 100.000000 |
| KXBTC15M-26MAY071300-00 | yes | 0.636040 | 0.590000 | 0.046040 | 842.515000 | 0.289227 | 1.011545 | False | -122.000000 |
