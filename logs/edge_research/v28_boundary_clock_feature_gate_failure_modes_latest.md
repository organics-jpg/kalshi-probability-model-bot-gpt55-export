# v28 Boundary-Clock Feature-Gate Failure Modes

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T01:55:02.062085+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- Classifier scope is selected rows only; omitted denominator rows are covered by coverage/sample blockers, not row-level tags.
- Post-freeze selected rows have structural blockers ['coverage_error'] and selected-row counts {'clean_or_unclassified': 27, 'entry_timing_error': 2, 'execution_friction_error': 9, 'fragility_error': 9, 'fv_error': 6, 'market_regime_error': 7, 'source_quality_error': 8}.
- Best diagnostic entry lane has blockers [] but row-level failure counts {'clean_or_unclassified': 61, 'entry_timing_error': 4, 'execution_friction_error': 29, 'fragility_error': 28, 'fv_error': 12, 'market_regime_error': 17, 'source_quality_error': 32}.
- Promotion still requires the live readiness gate; this report only explains failure modes.

## diagnostic_bridge

| candidate | settled/den | W/L | coverage | net c | recon | cushion | structural modes | row mode counts | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| diagnostic_bridge_raw03_recross70_abs075 | 98/119 | 71/27 | 82.352941 | 717.000000 | 0.326531 | 7 | none | clean_or_unclassified:60, entry_timing_error:4, execution_friction_error:28, fragility_error:27, fv_error:11, market_regime_error:17, source_quality_error:32 | none |
| diagnostic_bridge_raw05_recross60_abs085 | 84/119 | 66/18 | 70.588235 | 851.000000 | 0.202381 | 8 | coverage_error | clean_or_unclassified:61, entry_timing_error:4, execution_friction_error:18, fragility_error:18, fv_error:7, market_regime_error:12, source_quality_error:17 | coverage_too_low |
| diagnostic_bridge_raw07_recross60_abs085 | 58/119 | 48/10 | 48.739496 | 828.000000 | 0.155172 | 8 | coverage_error | clean_or_unclassified:45, entry_timing_error:2, execution_friction_error:10, fragility_error:10, fv_error:7, market_regime_error:8, source_quality_error:9 | coverage_too_low |
| diagnostic_bridge_raw05_recross60_abs085_ask65 | 76/119 | 69/7 | 63.865546 | 738.000000 | 0.052632 | 7 | coverage_error | clean_or_unclassified:65, entry_timing_error:4, execution_friction_error:7, fragility_error:7, fv_error:5, market_regime_error:5, source_quality_error:4 | coverage_too_low |

### Selected Loss Rows

| candidate | market | source | side | net c | edge | recross | abs d | ask | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY060745-45 | approved_entry | yes | -71.000000 | 0.161843 | 0.303224 | 0.889718 | 0.690000 | execution_friction_error, fragility_error, fv_error, market_regime_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY060845-45 | rejected_actionable | yes | -15.000000 | 0.034631 | 0.085692 | 0.785314 | 0.130000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061115-15 | rejected_actionable | yes | -3.000000 | 0.033834 | 0.045738 | 1.393553 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061245-45 | rejected_actionable | no | -10.000000 | 0.044470 | 0.199275 | 0.943912 | 0.080000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061300-00 | approved_entry | yes | -82.000000 | 0.060906 | 0.301730 | 0.913273 | 0.800000 | entry_timing_error, execution_friction_error, fragility_error, market_regime_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061415-15 | rejected_actionable | yes | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061430-30 | rejected_actionable | no | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7.000000 | 0.104874 | 0.041740 | 0.791108 | 0.060000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -6.000000 | 0.059156 | 0.160756 | 0.997837 | 0.050000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061930-30 | rejected_actionable | no | -2.000000 | 0.031608 | 0.083294 | 1.513246 | 0.010000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY062130-30 | approved_entry | no | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY062245-45 | rejected_actionable | no | -5.000000 | 0.104085 | 0.082631 | 0.877475 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY062300-00 | rejected_actionable | no | -2.000000 | 0.053100 | 0.076598 | 1.282765 | 0.010000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY062345-45 | rejected_actionable | no | -15.000000 | 0.041601 | 0.132257 | 0.784861 | 0.130000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY070015-15 | approved_entry | no | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | execution_friction_error, fragility_error, fv_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY070130-30 | rejected_actionable | yes | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY070145-45 | rejected_actionable | yes | -3.000000 | 0.043906 | 0.028894 | 1.241798 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY070200-00 | rejected_actionable | yes | -11.000000 | 0.086934 | 0.122242 | 0.758696 | 0.090000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY070615-15 | rejected_actionable | yes | -68.000000 | 0.200931 | 0.253348 | 0.819952 | 0.640000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY070900-00 | rejected_actionable | no | -6.000000 | 0.047205 | 0.073267 | 1.083550 | 0.050000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY071015-15 | approved_entry | no | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY071100-00 | approved_entry | yes | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | entry_timing_error, execution_friction_error, fragility_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY071115-15 | rejected_actionable | no | -7.000000 | 0.052022 | 0.062104 | 1.014490 | 0.060000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY071215-15 | rejected_actionable | yes | -75.000000 | 0.108282 | 0.487740 | 0.790551 | 0.720000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY071300-00 | rejected_actionable | yes | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY060745-45 | approved_entry | yes | -71.000000 | 0.161843 | 0.303224 | 0.889718 | 0.690000 | execution_friction_error, fragility_error, fv_error, market_regime_error |
| diagnostic_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY061300-00 | approved_entry | yes | -82.000000 | 0.060906 | 0.301730 | 0.913273 | 0.800000 | entry_timing_error, execution_friction_error, fragility_error, market_regime_error |
| diagnostic_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY061415-15 | rejected_actionable | yes | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY061430-30 | rejected_actionable | no | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -6.000000 | 0.059156 | 0.160756 | 0.997837 | 0.050000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY062130-30 | approved_entry | no | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| diagnostic_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY062245-45 | rejected_actionable | no | -5.000000 | 0.104085 | 0.082631 | 0.877475 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY062300-00 | rejected_actionable | no | -2.000000 | 0.053100 | 0.076598 | 1.282765 | 0.010000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY070015-15 | approved_entry | no | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | execution_friction_error, fragility_error, fv_error |
| diagnostic_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY070130-30 | rejected_actionable | yes | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |

## diagnostic_entry

| candidate | settled/den | W/L | coverage | net c | recon | cushion | structural modes | row mode counts | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| diagnostic_entry_raw03_recross70_abs075 | 100/121 | 72/28 | 82.644628 | 725.000000 | 0.320000 | 7 | none | clean_or_unclassified:61, entry_timing_error:4, execution_friction_error:29, fragility_error:28, fv_error:12, market_regime_error:17, source_quality_error:32 | none |
| diagnostic_entry_raw05_recross60_abs085 | 86/121 | 67/19 | 71.074380 | 859.000000 | 0.197674 | 8 | coverage_error | clean_or_unclassified:62, entry_timing_error:4, execution_friction_error:19, fragility_error:19, fv_error:8, market_regime_error:12, source_quality_error:17 | coverage_too_low |
| diagnostic_entry_raw07_recross60_abs085 | 60/121 | 49/11 | 49.586777 | 836.000000 | 0.150000 | 8 | coverage_error | clean_or_unclassified:46, entry_timing_error:2, execution_friction_error:11, fragility_error:11, fv_error:8, market_regime_error:8, source_quality_error:9 | coverage_too_low |
| diagnostic_entry_raw05_recross60_abs085_ask65 | 78/121 | 71/7 | 64.462810 | 775.000000 | 0.051282 | 7 | coverage_error | clean_or_unclassified:67, entry_timing_error:4, execution_friction_error:7, fragility_error:7, fv_error:5, market_regime_error:5, source_quality_error:4 | coverage_too_low |

### Selected Loss Rows

| candidate | market | source | side | net c | edge | recross | abs d | ask | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY060330-30 | approved_entry | no | -11.000000 | 0.909788 | 0.002807 | 3.991247 | 0.090000 | execution_friction_error, fragility_error, fv_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY060745-45 | approved_entry | yes | -71.000000 | 0.161843 | 0.303224 | 0.889718 | 0.690000 | execution_friction_error, fragility_error, fv_error, market_regime_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY060845-45 | rejected_actionable | yes | -15.000000 | 0.034631 | 0.085692 | 0.785314 | 0.130000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061115-15 | rejected_actionable | yes | -3.000000 | 0.033834 | 0.045738 | 1.393553 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061245-45 | rejected_actionable | no | -10.000000 | 0.044470 | 0.199275 | 0.943912 | 0.080000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061300-00 | approved_entry | yes | -82.000000 | 0.060906 | 0.301730 | 0.913273 | 0.800000 | entry_timing_error, execution_friction_error, fragility_error, market_regime_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061415-15 | rejected_actionable | yes | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061430-30 | rejected_actionable | no | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7.000000 | 0.104874 | 0.041740 | 0.791108 | 0.060000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -6.000000 | 0.059156 | 0.160756 | 0.997837 | 0.050000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061930-30 | rejected_actionable | no | -2.000000 | 0.031608 | 0.083294 | 1.513246 | 0.010000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY062130-30 | approved_entry | no | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY062245-45 | rejected_actionable | no | -5.000000 | 0.104085 | 0.082631 | 0.877475 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY062300-00 | rejected_actionable | no | -2.000000 | 0.053100 | 0.076598 | 1.282765 | 0.010000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY062345-45 | rejected_actionable | no | -15.000000 | 0.041601 | 0.132257 | 0.784861 | 0.130000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY070015-15 | approved_entry | no | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | execution_friction_error, fragility_error, fv_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY070130-30 | rejected_actionable | yes | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY070145-45 | rejected_actionable | yes | -3.000000 | 0.043906 | 0.028894 | 1.241798 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY070200-00 | rejected_actionable | yes | -11.000000 | 0.086934 | 0.122242 | 0.758696 | 0.090000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY070615-15 | rejected_actionable | yes | -68.000000 | 0.200931 | 0.253348 | 0.819952 | 0.640000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY070900-00 | rejected_actionable | no | -6.000000 | 0.047205 | 0.073267 | 1.083550 | 0.050000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY071015-15 | approved_entry | no | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY071100-00 | approved_entry | yes | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | entry_timing_error, execution_friction_error, fragility_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY071115-15 | rejected_actionable | no | -7.000000 | 0.052022 | 0.062104 | 1.014490 | 0.060000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY071215-15 | rejected_actionable | yes | -75.000000 | 0.108282 | 0.487740 | 0.790551 | 0.720000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw03_recross70_abs075 | KXBTC15M-26MAY071300-00 | rejected_actionable | yes | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw05_recross60_abs085 | KXBTC15M-26MAY060330-30 | approved_entry | no | -11.000000 | 0.909788 | 0.002807 | 3.991247 | 0.090000 | execution_friction_error, fragility_error, fv_error |
| diagnostic_entry_raw05_recross60_abs085 | KXBTC15M-26MAY060745-45 | approved_entry | yes | -71.000000 | 0.161843 | 0.303224 | 0.889718 | 0.690000 | execution_friction_error, fragility_error, fv_error, market_regime_error |
| diagnostic_entry_raw05_recross60_abs085 | KXBTC15M-26MAY061300-00 | approved_entry | yes | -82.000000 | 0.060906 | 0.301730 | 0.913273 | 0.800000 | entry_timing_error, execution_friction_error, fragility_error, market_regime_error |
| diagnostic_entry_raw05_recross60_abs085 | KXBTC15M-26MAY061415-15 | rejected_actionable | yes | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw05_recross60_abs085 | KXBTC15M-26MAY061430-30 | rejected_actionable | no | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_entry_raw05_recross60_abs085 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| diagnostic_entry_raw05_recross60_abs085 | KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw05_recross60_abs085 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw05_recross60_abs085 | KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -6.000000 | 0.059156 | 0.160756 | 0.997837 | 0.050000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw05_recross60_abs085 | KXBTC15M-26MAY062130-30 | approved_entry | no | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| diagnostic_entry_raw05_recross60_abs085 | KXBTC15M-26MAY062245-45 | rejected_actionable | no | -5.000000 | 0.104085 | 0.082631 | 0.877475 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| diagnostic_entry_raw05_recross60_abs085 | KXBTC15M-26MAY062300-00 | rejected_actionable | no | -2.000000 | 0.053100 | 0.076598 | 1.282765 | 0.010000 | execution_friction_error, fragility_error, source_quality_error |

## post_feature_freeze_bridge

| candidate | settled/den | W/L | coverage | net c | recon | cushion | structural modes | row mode counts | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| post_feature_freeze_bridge_raw07_recross60_abs085 | 38/82 | 29/9 | 46.341463 | 454.000000 | 0.210526 | 4 | coverage_error | clean_or_unclassified:27, entry_timing_error:2, execution_friction_error:9, fragility_error:9, fv_error:6, market_regime_error:7, source_quality_error:8 | coverage_too_low |
| post_feature_freeze_bridge_raw05_recross60_abs085 | 55/82 | 39/16 | 67.073171 | 445.000000 | 0.272727 | 4 | coverage_error | clean_or_unclassified:36, entry_timing_error:3, execution_friction_error:16, fragility_error:16, fv_error:6, market_regime_error:10, source_quality_error:15 | coverage_too_low |
| post_feature_freeze_bridge_raw05_recross60_abs085_ask65 | 47/82 | 42/5 | 57.317073 | 344.000000 | 0.042553 | 3 | coverage_error | clean_or_unclassified:40, entry_timing_error:3, execution_friction_error:5, fragility_error:5, fv_error:4, market_regime_error:3, source_quality_error:2 | coverage_too_low |
| post_feature_freeze_bridge_raw03_recross70_abs075 | 64/82 | 42/22 | 78.048780 | 307.000000 | 0.390625 | 3 | source_quality_error | clean_or_unclassified:35, entry_timing_error:3, execution_friction_error:23, fragility_error:22, fv_error:10, market_regime_error:13, source_quality_error:25 | reconstructed_share_gt_35pct |

### Selected Loss Rows

| candidate | market | source | side | net c | edge | recross | abs d | ask | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| post_feature_freeze_bridge_raw07_recross60_abs085 | KXBTC15M-26MAY061415-15 | rejected_actionable | yes | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw07_recross60_abs085 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_bridge_raw07_recross60_abs085 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw07_recross60_abs085 | KXBTC15M-26MAY062130-30 | approved_entry | no | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_bridge_raw07_recross60_abs085 | KXBTC15M-26MAY062245-45 | rejected_actionable | no | -5.000000 | 0.104085 | 0.082631 | 0.877475 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw07_recross60_abs085 | KXBTC15M-26MAY070015-15 | approved_entry | no | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | execution_friction_error, fragility_error, fv_error |
| post_feature_freeze_bridge_raw07_recross60_abs085 | KXBTC15M-26MAY070130-30 | rejected_actionable | yes | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw07_recross60_abs085 | KXBTC15M-26MAY070200-00 | rejected_actionable | yes | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw07_recross60_abs085 | KXBTC15M-26MAY071015-15 | approved_entry | no | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY061415-15 | rejected_actionable | yes | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY061430-30 | rejected_actionable | no | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -6.000000 | 0.059156 | 0.160756 | 0.997837 | 0.050000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY062130-30 | approved_entry | no | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY062245-45 | rejected_actionable | no | -5.000000 | 0.104085 | 0.082631 | 0.877475 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY062300-00 | rejected_actionable | no | -2.000000 | 0.053100 | 0.076598 | 1.282765 | 0.010000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY070015-15 | approved_entry | no | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | execution_friction_error, fragility_error, fv_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY070130-30 | rejected_actionable | yes | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY070200-00 | rejected_actionable | yes | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY071015-15 | approved_entry | no | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY071100-00 | approved_entry | yes | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | entry_timing_error, execution_friction_error, fragility_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY071115-15 | rejected_actionable | no | -7.000000 | 0.052022 | 0.062104 | 1.014490 | 0.060000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_bridge_raw05_recross60_abs085 | KXBTC15M-26MAY071300-00 | rejected_actionable | yes | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw05_recross60_abs085_ask65 | KXBTC15M-26MAY062015-15 | approved_entry | yes | -71.000000 | 0.215657 | 0.032091 | 0.973796 | 0.670000 | execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_bridge_raw05_recross60_abs085_ask65 | KXBTC15M-26MAY062130-30 | approved_entry | no | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_bridge_raw05_recross60_abs085_ask65 | KXBTC15M-26MAY070015-15 | approved_entry | no | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | execution_friction_error, fragility_error, fv_error |
| post_feature_freeze_bridge_raw05_recross60_abs085_ask65 | KXBTC15M-26MAY071015-15 | approved_entry | no | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_bridge_raw05_recross60_abs085_ask65 | KXBTC15M-26MAY071100-00 | approved_entry | yes | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | entry_timing_error, execution_friction_error, fragility_error |
| post_feature_freeze_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061415-15 | rejected_actionable | yes | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061430-30 | rejected_actionable | no | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7.000000 | 0.104874 | 0.041740 | 0.791108 | 0.060000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -6.000000 | 0.059156 | 0.160756 | 0.997837 | 0.050000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY061930-30 | rejected_actionable | no | -2.000000 | 0.031608 | 0.083294 | 1.513246 | 0.010000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY062130-30 | approved_entry | no | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY062245-45 | rejected_actionable | no | -5.000000 | 0.104085 | 0.082631 | 0.877475 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_bridge_raw03_recross70_abs075 | KXBTC15M-26MAY062300-00 | rejected_actionable | no | -2.000000 | 0.053100 | 0.076598 | 1.282765 | 0.010000 | execution_friction_error, fragility_error, source_quality_error |

## post_feature_freeze_entry

| candidate | settled/den | W/L | coverage | net c | recon | cushion | structural modes | row mode counts | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| post_feature_freeze_entry_raw07_recross60_abs085 | 38/82 | 29/9 | 46.341463 | 454.000000 | 0.210526 | 4 | coverage_error | clean_or_unclassified:27, entry_timing_error:2, execution_friction_error:9, fragility_error:9, fv_error:6, market_regime_error:7, source_quality_error:8 | coverage_too_low |
| post_feature_freeze_entry_raw05_recross60_abs085 | 55/82 | 39/16 | 67.073171 | 445.000000 | 0.272727 | 4 | coverage_error | clean_or_unclassified:36, entry_timing_error:3, execution_friction_error:16, fragility_error:16, fv_error:6, market_regime_error:10, source_quality_error:15 | coverage_too_low |
| post_feature_freeze_entry_raw05_recross60_abs085_ask65 | 47/82 | 42/5 | 57.317073 | 344.000000 | 0.042553 | 3 | coverage_error | clean_or_unclassified:40, entry_timing_error:3, execution_friction_error:5, fragility_error:5, fv_error:4, market_regime_error:3, source_quality_error:2 | coverage_too_low |
| post_feature_freeze_entry_raw03_recross70_abs075 | 64/82 | 42/22 | 78.048780 | 307.000000 | 0.390625 | 3 | source_quality_error | clean_or_unclassified:35, entry_timing_error:3, execution_friction_error:23, fragility_error:22, fv_error:10, market_regime_error:13, source_quality_error:25 | reconstructed_share_gt_35pct |

### Selected Loss Rows

| candidate | market | source | side | net c | edge | recross | abs d | ask | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| post_feature_freeze_entry_raw07_recross60_abs085 | KXBTC15M-26MAY061415-15 | rejected_actionable | yes | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw07_recross60_abs085 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_entry_raw07_recross60_abs085 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw07_recross60_abs085 | KXBTC15M-26MAY062130-30 | approved_entry | no | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_entry_raw07_recross60_abs085 | KXBTC15M-26MAY062245-45 | rejected_actionable | no | -5.000000 | 0.104085 | 0.082631 | 0.877475 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw07_recross60_abs085 | KXBTC15M-26MAY070015-15 | approved_entry | no | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | execution_friction_error, fragility_error, fv_error |
| post_feature_freeze_entry_raw07_recross60_abs085 | KXBTC15M-26MAY070130-30 | rejected_actionable | yes | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw07_recross60_abs085 | KXBTC15M-26MAY070200-00 | rejected_actionable | yes | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw07_recross60_abs085 | KXBTC15M-26MAY071015-15 | approved_entry | no | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY061415-15 | rejected_actionable | yes | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY061430-30 | rejected_actionable | no | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -6.000000 | 0.059156 | 0.160756 | 0.997837 | 0.050000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY062130-30 | approved_entry | no | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY062245-45 | rejected_actionable | no | -5.000000 | 0.104085 | 0.082631 | 0.877475 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY062300-00 | rejected_actionable | no | -2.000000 | 0.053100 | 0.076598 | 1.282765 | 0.010000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY070015-15 | approved_entry | no | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | execution_friction_error, fragility_error, fv_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY070130-30 | rejected_actionable | yes | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY070200-00 | rejected_actionable | yes | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY071015-15 | approved_entry | no | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY071100-00 | approved_entry | yes | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | entry_timing_error, execution_friction_error, fragility_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY071115-15 | rejected_actionable | no | -7.000000 | 0.052022 | 0.062104 | 1.014490 | 0.060000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_entry_raw05_recross60_abs085 | KXBTC15M-26MAY071300-00 | rejected_actionable | yes | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw05_recross60_abs085_ask65 | KXBTC15M-26MAY062015-15 | approved_entry | yes | -71.000000 | 0.215657 | 0.032091 | 0.973796 | 0.670000 | execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_entry_raw05_recross60_abs085_ask65 | KXBTC15M-26MAY062130-30 | approved_entry | no | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_entry_raw05_recross60_abs085_ask65 | KXBTC15M-26MAY070015-15 | approved_entry | no | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | execution_friction_error, fragility_error, fv_error |
| post_feature_freeze_entry_raw05_recross60_abs085_ask65 | KXBTC15M-26MAY071015-15 | approved_entry | no | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_entry_raw05_recross60_abs085_ask65 | KXBTC15M-26MAY071100-00 | approved_entry | yes | -84.000000 | 0.054041 | 0.305006 | 1.010241 | 0.830000 | entry_timing_error, execution_friction_error, fragility_error |
| post_feature_freeze_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061415-15 | rejected_actionable | yes | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061430-30 | rejected_actionable | no | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061530-30 | rejected_actionable | no | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7.000000 | 0.104874 | 0.041740 | 0.791108 | 0.060000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061730-30 | rejected_actionable | no | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -6.000000 | 0.059156 | 0.160756 | 0.997837 | 0.050000 | execution_friction_error, fragility_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw03_recross70_abs075 | KXBTC15M-26MAY061930-30 | rejected_actionable | no | -2.000000 | 0.031608 | 0.083294 | 1.513246 | 0.010000 | execution_friction_error, fragility_error, source_quality_error |
| post_feature_freeze_entry_raw03_recross70_abs075 | KXBTC15M-26MAY062130-30 | approved_entry | no | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | entry_timing_error, execution_friction_error, fragility_error, fv_error, market_regime_error |
| post_feature_freeze_entry_raw03_recross70_abs075 | KXBTC15M-26MAY062245-45 | rejected_actionable | no | -5.000000 | 0.104085 | 0.082631 | 0.877475 | 0.040000 | execution_friction_error, fragility_error, fv_error, market_regime_error, source_quality_error |
| post_feature_freeze_entry_raw03_recross70_abs075 | KXBTC15M-26MAY062300-00 | rejected_actionable | no | -2.000000 | 0.053100 | 0.076598 | 1.282765 | 0.010000 | execution_friction_error, fragility_error, source_quality_error |
