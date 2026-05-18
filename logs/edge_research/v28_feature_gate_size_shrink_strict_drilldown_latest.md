# v28 Feature-Gate Size-Shrink Strict Drilldown

Research-only strict-forward drilldown. No live bot changes or orders.

- Generated UTC: `2026-05-11T00:05:18.987192+00:00`
- Freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Policy: `repair_low_absd_quarter_else_half`
- Entries/denominator: `66/82`
- Settled W/L: `54/12`
- Coverage: `80.488%`
- Weighted net: `408.750c`
- Live baseline delta: `-1806.250c`
- Source counts: `{'approved_entry': 40, 'rejected_actionable': 26}`
- Reconstructed share: `0.394`
- Exposure reconstructed share: `0.261`
- Clean rows needed for source: `9`
- Clean full wins needed for live: `19`
- Blockers: `['row_reconstructed_share_gt_35pct', 'does_not_beat_refreshed_live_baseline']`

## Interpretation

- Research-only strict-forward drilldown; no live bot changes or orders.
- The closest strict broad-ish lane clears settled count, net-positive, and three-full-loss cushion, but the latest denominator drift leaves it below the 75% coverage floor; it also still fails row-count source quality and refreshed live-baseline comparison.
- The current omitted positive pool is reconstructed-only, so source repair probably requires genuinely new clean approved future rows rather than an observable reshuffle of current rows.

## Loss Classes

- Loss tag counts: `{'coverage_repair_loss': 8, 'source_quality_error': 9, 'weak_boundary_distance': 8, 'cheap_or_midcheap_touch': 2, 'anchor_loss': 4, 'moderate_recross_risk': 7, 'fv_or_market_regime_error': 1, 'thin_raw_edge': 2}`
- Class weighted net: `{'anchor': 445.0, 'coverage_repair': 29.5, 'coverage_repair+lower_abs_d+source_fragile': -26.25, 'coverage_repair+lower_abs_d+recross_risk+source_fragile': -63.5, 'coverage_repair+lower_abs_d+mid_cheap+source_fragile': -22.25, 'coverage_repair+lower_abs_d+recross_risk+mid_cheap+source_fragile': 24.75, 'coverage_repair+source_fragile': 13.5, 'coverage_repair+recross_risk+source_fragile': 8.0}`

| market | side | source | net | weight | weighted | class | tags | raw edge | abs d | recross | ask |
|---|---|---|---:|---:|---:|---|---|---:|---:|---:|---:|
| KXBTC15M-26MAY071100-00 | yes | approved_entry | -84.000 | 1.000 | -84.000 | anchor | ['anchor_loss', 'moderate_recross_risk', 'thin_raw_edge'] | 0.054 | 1.010 | 0.305 | 0.830 |
| KXBTC15M-26MAY071015-15 | no | approved_entry | -80.000 | 1.000 | -80.000 | anchor | ['anchor_loss', 'moderate_recross_risk'] | 0.081 | 0.936 | 0.418 | 0.780 |
| KXBTC15M-26MAY070015-15 | no | approved_entry | -72.000 | 1.000 | -72.000 | anchor | ['anchor_loss', 'fv_or_market_regime_error'] | 0.264 | 1.544 | 0.074 | 0.700 |
| KXBTC15M-26MAY062130-30 | no | rejected_actionable | -65.000 | 1.000 | -65.000 | anchor | ['anchor_loss', 'source_quality_error', 'weak_boundary_distance', 'moderate_recross_risk'] | 0.158 | 0.624 | 0.267 | 0.610 |
| KXBTC15M-26MAY071215-15 | yes | rejected_actionable | -75.000 | 0.500 | -37.500 | coverage_repair+lower_abs_d+recross_risk+source_fragile | ['coverage_repair_loss', 'source_quality_error', 'moderate_recross_risk'] | 0.108 | 0.791 | 0.488 | 0.720 |
| KXBTC15M-26MAY070900-00 | no | rejected_actionable | -73.000 | 0.250 | -18.250 | coverage_repair+lower_abs_d+recross_risk+source_fragile | ['coverage_repair_loss', 'source_quality_error', 'weak_boundary_distance', 'moderate_recross_risk', 'thin_raw_edge'] | 0.056 | 0.592 | 0.457 | 0.700 |
| KXBTC15M-26MAY061715-15 | yes | rejected_actionable | -68.000 | 0.250 | -17.000 | coverage_repair+lower_abs_d+source_fragile | ['coverage_repair_loss', 'source_quality_error', 'weak_boundary_distance'] | 0.125 | 0.603 | 0.115 | 0.640 |
| KXBTC15M-26MAY062345-45 | no | rejected_actionable | -60.000 | 0.250 | -15.000 | coverage_repair+lower_abs_d+source_fragile | ['coverage_repair_loss', 'source_quality_error', 'weak_boundary_distance', 'moderate_recross_risk'] | 0.246 | 0.727 | 0.265 | 0.560 |
| KXBTC15M-26MAY070630-30 | yes | rejected_actionable | -59.000 | 0.250 | -14.750 | coverage_repair+lower_abs_d+recross_risk+source_fragile | ['coverage_repair_loss', 'source_quality_error', 'weak_boundary_distance', 'moderate_recross_risk'] | 0.238 | 0.658 | 0.372 | 0.550 |
| KXBTC15M-26MAY062230-30 | yes | rejected_actionable | -58.000 | 0.250 | -14.500 | coverage_repair+lower_abs_d+source_fragile | ['coverage_repair_loss', 'source_quality_error', 'weak_boundary_distance'] | 0.199 | 0.533 | 0.244 | 0.540 |
| KXBTC15M-26MAY070615-15 | yes | rejected_actionable | -47.000 | 0.250 | -11.750 | coverage_repair+lower_abs_d+mid_cheap+source_fragile | ['coverage_repair_loss', 'source_quality_error', 'weak_boundary_distance', 'cheap_or_midcheap_touch'] | 0.345 | 0.631 | 0.143 | 0.430 |
| KXBTC15M-26MAY061700-00 | no | rejected_actionable | -42.000 | 0.250 | -10.500 | coverage_repair+lower_abs_d+mid_cheap+source_fragile | ['coverage_repair_loss', 'source_quality_error', 'weak_boundary_distance', 'cheap_or_midcheap_touch'] | 0.408 | 0.665 | 0.196 | 0.380 |

## Omitted Positive Pool

- Omitted positive approved rows: `0` / `0c`
- Omitted positive reconstructed rows: `173` / `4891.000c`

| market | side | source | net | raw edge | abs d | recross | ask |
|---|---|---|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY061500-00 | no | rejected_actionable | 76.000 | 0.130 | 0.372 | 0.148 | 0.210 |
| KXBTC15M-26MAY070730-30 | no | rejected_actionable | 76.000 | 0.227 | 0.144 | 0.325 | 0.210 |
| KXBTC15M-26MAY061515-15 | no | rejected_actionable | 75.000 | -0.001 | 0.653 | 0.465 | 0.220 |
| KXBTC15M-26MAY070045-45 | no | rejected_actionable | 74.000 | -0.038 | 0.721 | 0.423 | 0.230 |
| KXBTC15M-26MAY061500-00 | no | rejected_actionable | 73.000 | 0.147 | 0.263 | 0.210 | 0.240 |
| KXBTC15M-26MAY061500-00 | no | rejected_actionable | 72.000 | 0.125 | 0.291 | 0.139 | 0.250 |
| KXBTC15M-26MAY061515-15 | no | rejected_actionable | 72.000 | 0.018 | 0.542 | 0.554 | 0.250 |
| KXBTC15M-26MAY061515-15 | no | rejected_actionable | 70.000 | -0.001 | 0.529 | 0.506 | 0.270 |
| KXBTC15M-26MAY061500-00 | no | rejected_actionable | 69.000 | 0.067 | 0.357 | 0.171 | 0.280 |
| KXBTC15M-26MAY061515-15 | no | rejected_actionable | 67.000 | 0.017 | 0.429 | 0.602 | 0.300 |
| KXBTC15M-26MAY061515-15 | no | rejected_actionable | 60.000 | 0.074 | 0.149 | 1.030 | 0.360 |
| KXBTC15M-26MAY070845-45 | yes | rejected_actionable | 60.000 | 0.094 | 0.106 | 0.151 | 0.360 |
| KXBTC15M-26MAY061500-00 | no | rejected_actionable | 59.000 | 0.046 | 0.206 | 0.426 | 0.370 |
| KXBTC15M-26MAY061515-15 | no | rejected_actionable | 58.000 | 0.001 | 0.279 | 0.532 | 0.380 |
| KXBTC15M-26MAY061500-00 | no | rejected_actionable | 57.000 | 0.022 | 0.196 | 0.968 | 0.390 |
| KXBTC15M-26MAY061500-00 | no | rejected_actionable | 56.000 | 0.027 | 0.200 | 0.295 | 0.400 |
| KXBTC15M-26MAY061500-00 | no | rejected_actionable | 55.000 | -0.008 | 0.225 | 0.918 | 0.410 |
| KXBTC15M-26MAY061515-15 | no | rejected_actionable | 55.000 | 0.036 | 0.135 | 0.856 | 0.410 |
| KXBTC15M-26MAY061500-00 | no | rejected_actionable | 54.000 | 0.029 | 0.135 | 0.376 | 0.420 |
| KXBTC15M-26MAY061500-00 | no | rejected_actionable | 54.000 | 0.041 | 0.103 | 0.272 | 0.420 |
