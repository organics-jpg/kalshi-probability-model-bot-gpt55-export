# v28 Boundary-Clock Feature-Gate Loss Analog Monitor

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T01:55:02.815952+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Prototype source: `diagnostic_entry_raw03_recross70_abs075`
- Prototype loss rows: `28`

## Interpretation

- Loss analog scores compare selected rows to frozen diagnostic selected losses; they are warning signals, not promotion gates or new thresholds.
- Post-freeze entry has 38 scored row(s), max analog score 1.0, components {'expensive_touch': 21, 'moderate_recross': 14, 'none': 3, 'reconstructed_source': 8, 'weak_boundary_distance': 22}.
- Diagnostic entry reference has 100 scored row(s), max analog score 1.0, components {'expensive_touch': 56, 'moderate_recross': 43, 'none': 4, 'reconstructed_source': 32, 'thin_raw_edge': 38, 'weak_boundary_distance': 59}.

## diagnostic_entry

- Candidate: `diagnostic_entry_raw03_recross70_abs075`
- Rows: `100`
- Max analog score: `1.000000`
- Avg analog score: `0.831260`
- Risk components: `{'expensive_touch': 56, 'moderate_recross': 43, 'none': 4, 'reconstructed_source': 32, 'thin_raw_edge': 38, 'weak_boundary_distance': 59}`

### Top Analog Rows

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest loss | components |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY060330-30 | approved_entry | no | False | -11.000000 | 0.909788 | 0.002807 | 3.991247 | 0.090000 | 1.000000 | KXBTC15M-26MAY060330-30 | none |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -71.000000 | 0.161843 | 0.303224 | 0.889718 | 0.690000 | 1.000000 | KXBTC15M-26MAY060745-45 | moderate_recross, weak_boundary_distance |
| KXBTC15M-26MAY060845-45 | rejected_actionable | yes | False | -15.000000 | 0.034631 | 0.085692 | 0.785314 | 0.130000 | 1.000000 | KXBTC15M-26MAY060845-45 | thin_raw_edge, weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -3.000000 | 0.033834 | 0.045738 | 1.393553 | 0.020000 | 1.000000 | KXBTC15M-26MAY061115-15 | thin_raw_edge, reconstructed_source |
| KXBTC15M-26MAY061245-45 | rejected_actionable | no | False | -10.000000 | 0.044470 | 0.199275 | 0.943912 | 0.080000 | 1.000000 | KXBTC15M-26MAY061245-45 | thin_raw_edge, weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.060906 | 0.301730 | 0.913273 | 0.800000 | 1.000000 | KXBTC15M-26MAY061300-00 | thin_raw_edge, moderate_recross, weak_boundary_distance, expensive_touch |
| KXBTC15M-26MAY061415-15 | rejected_actionable | yes | False | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | 1.000000 | KXBTC15M-26MAY061415-15 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | 1.000000 | KXBTC15M-26MAY061430-30 | thin_raw_edge, reconstructed_source |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | reconstructed_source |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.104874 | 0.041740 | 0.791108 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | False | -6.000000 | 0.059156 | 0.160756 | 0.997837 | 0.050000 | 1.000000 | KXBTC15M-26MAY061830-30 | thin_raw_edge, weak_boundary_distance, reconstructed_source |

## diagnostic_bridge

- Candidate: `diagnostic_bridge_raw03_recross70_abs075`
- Rows: `98`
- Max analog score: `1.000000`
- Avg analog score: `0.828812`
- Risk components: `{'expensive_touch': 55, 'moderate_recross': 42, 'none': 3, 'reconstructed_source': 32, 'thin_raw_edge': 38, 'weak_boundary_distance': 59}`

### Top Analog Rows

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest loss | components |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -71.000000 | 0.161843 | 0.303224 | 0.889718 | 0.690000 | 1.000000 | KXBTC15M-26MAY060745-45 | moderate_recross, weak_boundary_distance |
| KXBTC15M-26MAY060845-45 | rejected_actionable | yes | False | -15.000000 | 0.034631 | 0.085692 | 0.785314 | 0.130000 | 1.000000 | KXBTC15M-26MAY060845-45 | thin_raw_edge, weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061115-15 | rejected_actionable | yes | False | -3.000000 | 0.033834 | 0.045738 | 1.393553 | 0.020000 | 1.000000 | KXBTC15M-26MAY061115-15 | thin_raw_edge, reconstructed_source |
| KXBTC15M-26MAY061245-45 | rejected_actionable | no | False | -10.000000 | 0.044470 | 0.199275 | 0.943912 | 0.080000 | 1.000000 | KXBTC15M-26MAY061245-45 | thin_raw_edge, weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.060906 | 0.301730 | 0.913273 | 0.800000 | 1.000000 | KXBTC15M-26MAY061300-00 | thin_raw_edge, moderate_recross, weak_boundary_distance, expensive_touch |
| KXBTC15M-26MAY061415-15 | rejected_actionable | yes | False | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | 1.000000 | KXBTC15M-26MAY061415-15 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | 1.000000 | KXBTC15M-26MAY061430-30 | thin_raw_edge, reconstructed_source |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | reconstructed_source |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0.104874 | 0.041740 | 0.791108 | 0.060000 | 1.000000 | KXBTC15M-26MAY061600-00 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | False | -6.000000 | 0.059156 | 0.160756 | 0.997837 | 0.050000 | 1.000000 | KXBTC15M-26MAY061830-30 | thin_raw_edge, weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061930-30 | rejected_actionable | no | False | -2.000000 | 0.031608 | 0.083294 | 1.513246 | 0.010000 | 1.000000 | KXBTC15M-26MAY061930-30 | thin_raw_edge, reconstructed_source |

## post_feature_freeze_entry

- Candidate: `post_feature_freeze_entry_raw07_recross60_abs085`
- Rows: `38`
- Max analog score: `1.000000`
- Avg analog score: `0.816797`
- Risk components: `{'expensive_touch': 21, 'moderate_recross': 14, 'none': 3, 'reconstructed_source': 8, 'weak_boundary_distance': 22}`

### Top Analog Rows

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest loss | components |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY061415-15 | rejected_actionable | yes | False | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | 1.000000 | KXBTC15M-26MAY061415-15 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | reconstructed_source |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross, weak_boundary_distance, expensive_touch |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | False | -5.000000 | 0.104085 | 0.082631 | 0.877475 | 0.040000 | 1.000000 | KXBTC15M-26MAY062245-45 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | none |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | 1.000000 | KXBTC15M-26MAY070130-30 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross, weak_boundary_distance, expensive_touch |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 | 0.927720 | KXBTC15M-26MAY070130-30 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 0.906216 | KXBTC15M-26MAY061730-30 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061645-45 | approved_entry | no | True | 21.000000 | 0.095564 | 0.415324 | 0.899418 | 0.760000 | 0.906115 | KXBTC15M-26MAY071015-15 | moderate_recross, weak_boundary_distance, expensive_touch |
| KXBTC15M-26MAY071215-15 | approved_entry | no | True | 20.000000 | 0.070947 | 0.262401 | 0.887915 | 0.780000 | 0.900636 | KXBTC15M-26MAY061300-00 | moderate_recross, weak_boundary_distance, expensive_touch |

## post_feature_freeze_bridge

- Candidate: `post_feature_freeze_bridge_raw07_recross60_abs085`
- Rows: `38`
- Max analog score: `1.000000`
- Avg analog score: `0.816797`
- Risk components: `{'expensive_touch': 21, 'moderate_recross': 14, 'none': 3, 'reconstructed_source': 8, 'weak_boundary_distance': 22}`

### Top Analog Rows

| market | source | side | won | net c | edge | recross | abs d | ask | score | nearest loss | components |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY061415-15 | rejected_actionable | yes | False | -3.000000 | 0.106664 | 0.100908 | 0.937376 | 0.020000 | 1.000000 | KXBTC15M-26MAY061415-15 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | 1.000000 | KXBTC15M-26MAY061530-30 | reconstructed_source |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | 1.000000 | KXBTC15M-26MAY061730-30 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | 1.000000 | KXBTC15M-26MAY062130-30 | moderate_recross, weak_boundary_distance, expensive_touch |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | False | -5.000000 | 0.104085 | 0.082631 | 0.877475 | 0.040000 | 1.000000 | KXBTC15M-26MAY062245-45 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | 1.000000 | KXBTC15M-26MAY070015-15 | none |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | 1.000000 | KXBTC15M-26MAY070130-30 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.417623 | 0.936079 | 0.780000 | 1.000000 | KXBTC15M-26MAY071015-15 | moderate_recross, weak_boundary_distance, expensive_touch |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 | 0.927720 | KXBTC15M-26MAY070130-30 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | 0.906216 | KXBTC15M-26MAY061730-30 | weak_boundary_distance, reconstructed_source |
| KXBTC15M-26MAY061645-45 | approved_entry | no | True | 21.000000 | 0.095564 | 0.415324 | 0.899418 | 0.760000 | 0.906115 | KXBTC15M-26MAY071015-15 | moderate_recross, weak_boundary_distance, expensive_touch |
| KXBTC15M-26MAY071215-15 | approved_entry | no | True | 20.000000 | 0.070947 | 0.262401 | 0.887915 | 0.780000 | 0.900636 | KXBTC15M-26MAY061300-00 | moderate_recross, weak_boundary_distance, expensive_touch |
