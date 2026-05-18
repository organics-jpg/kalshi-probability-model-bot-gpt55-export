# v28 Boundary-Clock Feature-Gate Ask-Floor Mechanism

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T18:12:51.155137+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- This is a mechanism audit of the already-frozen ask>=0.65 variant; it does not search or propose a new threshold.
- diagnostic_entry: ask floor changes net by -84.0c with entry delta -8; omitted rows net 56.0c and tags {'cheap_touch_or_contrarian_side': 8, 'source_quality_risk': 8, 'realized_loss': 7}; same-market switched base/ask rows net 72.0c/49.0c with tags {'cheap_touch_or_contrarian_side': 8, 'large_raw_edge_on_cheap_side': 5, 'realized_loss': 6, 'source_quality_risk': 5}; ask-floor selected coverage 64.46280991735537%.
- diagnostic_bridge: ask floor changes net by -113.0c with entry delta -8; omitted rows net 56.0c and tags {'cheap_touch_or_contrarian_side': 8, 'source_quality_risk': 8, 'realized_loss': 7}; same-market switched base/ask rows net 81.0c/28.0c with tags {'cheap_touch_or_contrarian_side': 7, 'large_raw_edge_on_cheap_side': 4, 'source_quality_risk': 5, 'realized_loss': 5}; ask-floor selected coverage 63.865546218487395%.
- post_feature_freeze_entry: ask floor changes net by -101.0c with entry delta -8; omitted rows net 56.0c and tags {'cheap_touch_or_contrarian_side': 8, 'source_quality_risk': 8, 'realized_loss': 7}; same-market switched base/ask rows net 40.0c/-1.0c with tags {'cheap_touch_or_contrarian_side': 6, 'large_raw_edge_on_cheap_side': 3, 'source_quality_risk': 5, 'realized_loss': 5}; ask-floor selected coverage 57.31707317073171%.
- post_feature_freeze_bridge: ask floor changes net by -101.0c with entry delta -8; omitted rows net 56.0c and tags {'cheap_touch_or_contrarian_side': 8, 'source_quality_risk': 8, 'realized_loss': 7}; same-market switched base/ask rows net 40.0c/-1.0c with tags {'cheap_touch_or_contrarian_side': 6, 'large_raw_edge_on_cheap_side': 3, 'source_quality_risk': 5, 'realized_loss': 5}; ask-floor selected coverage 57.31707317073171%.

## diagnostic_entry

| slice | entries | settled | W/L | coverage | net c | sources | sides | feature means |
|---|---:|---:|---:|---:|---:|---|---|---|
| base_raw05_recross60_abs085 | 86 | 86 | 67/19 | 71.074380 | 859.000000 | {'approved_entry': 69, 'rejected_actionable': 17} | {'no': 46, 'yes': 40} | {'raw_edge': 0.11600108139534883, 'recross_hazard_score': 0.2482752595330874, 'abs_d_sigma': 1.107562441860465, 'ask_prob': 0.6588372093023256} |
| ask_floor_raw05_recross60_abs085_ask65 | 78 | 78 | 71/7 | 64.462810 | 775.000000 | {'approved_entry': 74, 'rejected_actionable': 4} | {'yes': 40, 'no': 38} | {'raw_edge': 0.1050686923076923, 'recross_hazard_score': 0.2673723025585711, 'abs_d_sigma': 1.0992942307692308, 'ask_prob': 0.788974358974359} |
| omitted_by_ask_floor | 8 | 8 | 1/7 | 6.611570 | 56.000000 | {'rejected_actionable': 8} | {'no': 5, 'yes': 3} | {'raw_edge': 0.07173375, 'recross_hazard_score': 0.07454964397612504, 'abs_d_sigma': 0.98104775, 'ask_prob': 0.04375} |
| switched_out_base_rows | 8 | 8 | 2/6 | 6.611570 | 72.000000 | {'approved_entry': 3, 'rejected_actionable': 5} | {'no': 6, 'yes': 2} | {'raw_edge': 0.25007325, 'recross_hazard_score': 0.1460538504549793, 'abs_d_sigma': 1.365499875, 'ask_prob': 0.16} |
| switched_in_ask_floor_rows | 8 | 8 | 7/1 | 6.611570 | 49.000000 | {'approved_entry': 8} | {'yes': 5, 'no': 3} | {'raw_edge': 0.099215125, 'recross_hazard_score': 0.15852440439648255, 'abs_d_sigma': 1.158370125, 'ask_prob': 0.81375} |

### Omitted By Ask Floor

| market | source | side | outcome | net c | edge | recross | abs d | ask | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | loss | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | loss | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | loss | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | loss | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | loss | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | loss | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | loss | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | win | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 | cheap_touch_or_contrarian_side, source_quality_risk |

### Same-Market Switches

| market | base source | base side | base outcome | base net c | base edge | base ask | ask source | ask side | ask outcome | ask net c | ask edge | ask ask | delta c | tags |
|---|---|---|---|---:|---:|---:|---|---|---|---:|---:|---:|---:|---|
| KXBTC15M-26MAY060330-30 | approved_entry | no | loss | -11.000000 | 0.909788 | 0.090000 | approved_entry | yes | win | 18.000000 | 0.118265 | 0.790000 | 29.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side, realized_loss |
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | loss | -7.000000 | 0.052022 | 0.060000 | approved_entry | yes | win | 15.000000 | 0.051894 | 0.840000 | 22.000000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | loss | -5.000000 | 0.104085 | 0.040000 | approved_entry | yes | win | 13.000000 | 0.089793 | 0.860000 | 18.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | loss | -6.000000 | 0.059156 | 0.050000 | approved_entry | no | win | 9.000000 | 0.057370 | 0.890000 | 15.000000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY062300-00 | rejected_actionable | no | loss | -2.000000 | 0.053100 | 0.010000 | approved_entry | yes | win | 12.000000 | 0.053042 | 0.870000 | 14.000000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061415-15 | rejected_actionable | yes | loss | -3.000000 | 0.106664 | 0.020000 | approved_entry | no | win | 10.000000 | 0.056538 | 0.880000 | 13.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY060945-45 | approved_entry | no | win | 39.000000 | 0.264149 | 0.590000 | approved_entry | no | win | 27.000000 | 0.151162 | 0.710000 | -12.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side |
| KXBTC15M-26MAY062015-15 | approved_entry | no | win | 56.000000 | 0.451622 | 0.420000 | approved_entry | yes | loss | -71.000000 | 0.215657 | 0.670000 | -127.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side |

## diagnostic_bridge

| slice | entries | settled | W/L | coverage | net c | sources | sides | feature means |
|---|---:|---:|---:|---:|---:|---|---|---|
| base_raw05_recross60_abs085 | 84 | 84 | 66/18 | 70.588235 | 851.000000 | {'rejected_actionable': 17, 'approved_entry': 67} | {'yes': 40, 'no': 44} | {'raw_edge': 0.10657588095238094, 'recross_hazard_score': 0.250838140948257, 'abs_d_sigma': 1.0744593928571429, 'ask_prob': 0.6641666666666667} |
| ask_floor_raw05_recross60_abs085_ask65 | 76 | 76 | 69/7 | 63.865546 | 738.000000 | {'rejected_actionable': 4, 'approved_entry': 72} | {'yes': 39, 'no': 37} | {'raw_edge': 0.10477844736842104, 'recross_hazard_score': 0.26879544994923615, 'abs_d_sigma': 1.1008942105263158, 'ask_prob': 0.7890789473684211} |
| omitted_by_ask_floor | 8 | 8 | 1/7 | 6.722689 | 56.000000 | {'rejected_actionable': 8} | {'no': 5, 'yes': 3} | {'raw_edge': 0.07173375, 'recross_hazard_score': 0.07454964397612504, 'abs_d_sigma': 0.98104775, 'ask_prob': 0.04375} |
| switched_out_base_rows | 7 | 7 | 2/5 | 5.882353 | 81.000000 | {'approved_entry': 2, 'rejected_actionable': 5} | {'no': 5, 'yes': 2} | {'raw_edge': 0.15582828571428572, 'recross_hazard_score': 0.16651765717313222, 'abs_d_sigma': 0.9903931428571429, 'ask_prob': 0.16999999999999998} |
| switched_in_ask_floor_rows | 7 | 7 | 6/1 | 5.882353 | 28.000000 | {'approved_entry': 7} | {'no': 3, 'yes': 4} | {'raw_edge': 0.0964937142857143, 'recross_hazard_score': 0.16001015835846918, 'abs_d_sigma': 1.1706435714285714, 'ask_prob': 0.8171428571428572} |

### Omitted By Ask Floor

| market | source | side | outcome | net c | edge | recross | abs d | ask | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | loss | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | loss | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | loss | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | loss | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | loss | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | loss | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | loss | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | win | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 | cheap_touch_or_contrarian_side, source_quality_risk |

### Same-Market Switches

| market | base source | base side | base outcome | base net c | base edge | base ask | ask source | ask side | ask outcome | ask net c | ask edge | ask ask | delta c | tags |
|---|---|---|---|---:|---:|---:|---|---|---|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | loss | -7.000000 | 0.052022 | 0.060000 | approved_entry | yes | win | 15.000000 | 0.051894 | 0.840000 | 22.000000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | loss | -5.000000 | 0.104085 | 0.040000 | approved_entry | yes | win | 13.000000 | 0.089793 | 0.860000 | 18.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | loss | -6.000000 | 0.059156 | 0.050000 | approved_entry | no | win | 9.000000 | 0.057370 | 0.890000 | 15.000000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY062300-00 | rejected_actionable | no | loss | -2.000000 | 0.053100 | 0.010000 | approved_entry | yes | win | 12.000000 | 0.053042 | 0.870000 | 14.000000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061415-15 | rejected_actionable | yes | loss | -3.000000 | 0.106664 | 0.020000 | approved_entry | no | win | 10.000000 | 0.056538 | 0.880000 | 13.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY060945-45 | approved_entry | no | win | 39.000000 | 0.264149 | 0.590000 | approved_entry | no | win | 27.000000 | 0.151162 | 0.710000 | -12.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side |
| KXBTC15M-26MAY062015-15 | approved_entry | no | win | 56.000000 | 0.451622 | 0.420000 | approved_entry | yes | loss | -71.000000 | 0.215657 | 0.670000 | -127.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side |

## post_feature_freeze_entry

| slice | entries | settled | W/L | coverage | net c | sources | sides | feature means |
|---|---:|---:|---:|---:|---:|---|---|---|
| base_raw05_recross60_abs085 | 55 | 55 | 39/16 | 67.073171 | 445.000000 | {'approved_entry': 40, 'rejected_actionable': 15} | {'no': 33, 'yes': 22} | {'raw_edge': 0.1048464909090909, 'recross_hazard_score': 0.20964054676957206, 'abs_d_sigma': 1.1046047454545453, 'ask_prob': 0.6096363636363636} |
| ask_floor_raw05_recross60_abs085_ask65 | 47 | 47 | 42/5 | 57.317073 | 344.000000 | {'approved_entry': 45, 'rejected_actionable': 2} | {'no': 26, 'yes': 21} | {'raw_edge': 0.10404961702127659, 'recross_hazard_score': 0.23937363375006807, 'abs_d_sigma': 1.1530521914893617, 'ask_prob': 0.7997872340425531} |
| omitted_by_ask_floor | 8 | 8 | 1/7 | 9.756098 | 56.000000 | {'rejected_actionable': 8} | {'no': 5, 'yes': 3} | {'raw_edge': 0.07173375, 'recross_hazard_score': 0.07454964397612504, 'abs_d_sigma': 0.98104775, 'ask_prob': 0.04375} |
| switched_out_base_rows | 6 | 6 | 1/5 | 7.317073 | 40.000000 | {'rejected_actionable': 5, 'approved_entry': 1} | {'yes': 2, 'no': 4} | {'raw_edge': 0.13777483333333335, 'recross_hazard_score': 0.0962321663930792, 'abs_d_sigma': 1.0044005, 'ask_prob': 0.09999999999999999} |
| switched_in_ask_floor_rows | 6 | 6 | 5/1 | 7.317073 | -1.000000 | {'approved_entry': 6} | {'no': 2, 'yes': 4} | {'raw_edge': 0.08738233333333334, 'recross_hazard_score': 0.149020144015702, 'abs_d_sigma': 1.2191628333333333, 'ask_prob': 0.835} |

### Omitted By Ask Floor

| market | source | side | outcome | net c | edge | recross | abs d | ask | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | loss | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | loss | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | loss | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | loss | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | loss | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | loss | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | loss | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | win | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 | cheap_touch_or_contrarian_side, source_quality_risk |

### Same-Market Switches

| market | base source | base side | base outcome | base net c | base edge | base ask | ask source | ask side | ask outcome | ask net c | ask edge | ask ask | delta c | tags |
|---|---|---|---|---:|---:|---:|---|---|---|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | loss | -7.000000 | 0.052022 | 0.060000 | approved_entry | yes | win | 15.000000 | 0.051894 | 0.840000 | 22.000000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | loss | -5.000000 | 0.104085 | 0.040000 | approved_entry | yes | win | 13.000000 | 0.089793 | 0.860000 | 18.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | loss | -6.000000 | 0.059156 | 0.050000 | approved_entry | no | win | 9.000000 | 0.057370 | 0.890000 | 15.000000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY062300-00 | rejected_actionable | no | loss | -2.000000 | 0.053100 | 0.010000 | approved_entry | yes | win | 12.000000 | 0.053042 | 0.870000 | 14.000000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061415-15 | rejected_actionable | yes | loss | -3.000000 | 0.106664 | 0.020000 | approved_entry | no | win | 10.000000 | 0.056538 | 0.880000 | 13.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY062015-15 | approved_entry | no | win | 56.000000 | 0.451622 | 0.420000 | approved_entry | yes | loss | -71.000000 | 0.215657 | 0.670000 | -127.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side |

## post_feature_freeze_bridge

| slice | entries | settled | W/L | coverage | net c | sources | sides | feature means |
|---|---:|---:|---:|---:|---:|---|---|---|
| base_raw05_recross60_abs085 | 55 | 55 | 39/16 | 67.073171 | 445.000000 | {'approved_entry': 40, 'rejected_actionable': 15} | {'no': 33, 'yes': 22} | {'raw_edge': 0.1048464909090909, 'recross_hazard_score': 0.20964054676957206, 'abs_d_sigma': 1.1046047454545453, 'ask_prob': 0.6096363636363636} |
| ask_floor_raw05_recross60_abs085_ask65 | 47 | 47 | 42/5 | 57.317073 | 344.000000 | {'approved_entry': 45, 'rejected_actionable': 2} | {'no': 26, 'yes': 21} | {'raw_edge': 0.10404961702127659, 'recross_hazard_score': 0.23937363375006807, 'abs_d_sigma': 1.1530521914893617, 'ask_prob': 0.7997872340425531} |
| omitted_by_ask_floor | 8 | 8 | 1/7 | 9.756098 | 56.000000 | {'rejected_actionable': 8} | {'no': 5, 'yes': 3} | {'raw_edge': 0.07173375, 'recross_hazard_score': 0.07454964397612504, 'abs_d_sigma': 0.98104775, 'ask_prob': 0.04375} |
| switched_out_base_rows | 6 | 6 | 1/5 | 7.317073 | 40.000000 | {'rejected_actionable': 5, 'approved_entry': 1} | {'yes': 2, 'no': 4} | {'raw_edge': 0.13777483333333335, 'recross_hazard_score': 0.0962321663930792, 'abs_d_sigma': 1.0044005, 'ask_prob': 0.09999999999999999} |
| switched_in_ask_floor_rows | 6 | 6 | 5/1 | 7.317073 | -1.000000 | {'approved_entry': 6} | {'no': 2, 'yes': 4} | {'raw_edge': 0.08738233333333334, 'recross_hazard_score': 0.149020144015702, 'abs_d_sigma': 1.2191628333333333, 'ask_prob': 0.835} |

### Omitted By Ask Floor

| market | source | side | outcome | net c | edge | recross | abs d | ask | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | loss | -10.000000 | 0.053235 | 0.083861 | 0.932497 | 0.080000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | loss | -7.000000 | 0.057585 | 0.083577 | 0.967753 | 0.060000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | loss | -6.000000 | 0.077518 | 0.050841 | 0.913861 | 0.050000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | loss | -5.000000 | 0.062326 | 0.081020 | 1.050761 | 0.040000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | loss | -5.000000 | 0.080622 | 0.099074 | 0.943937 | 0.040000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | loss | -4.000000 | 0.077885 | 0.087550 | 0.997935 | 0.030000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | loss | -3.000000 | 0.075977 | 0.038855 | 1.069646 | 0.020000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | win | 96.000000 | 0.088722 | 0.071618 | 0.971992 | 0.030000 | cheap_touch_or_contrarian_side, source_quality_risk |

### Same-Market Switches

| market | base source | base side | base outcome | base net c | base edge | base ask | ask source | ask side | ask outcome | ask net c | ask edge | ask ask | delta c | tags |
|---|---|---|---|---:|---:|---:|---|---|---|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | loss | -7.000000 | 0.052022 | 0.060000 | approved_entry | yes | win | 15.000000 | 0.051894 | 0.840000 | 22.000000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | loss | -5.000000 | 0.104085 | 0.040000 | approved_entry | yes | win | 13.000000 | 0.089793 | 0.860000 | 18.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | loss | -6.000000 | 0.059156 | 0.050000 | approved_entry | no | win | 9.000000 | 0.057370 | 0.890000 | 15.000000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY062300-00 | rejected_actionable | no | loss | -2.000000 | 0.053100 | 0.010000 | approved_entry | yes | win | 12.000000 | 0.053042 | 0.870000 | 14.000000 | cheap_touch_or_contrarian_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY061415-15 | rejected_actionable | yes | loss | -3.000000 | 0.106664 | 0.020000 | approved_entry | no | win | 10.000000 | 0.056538 | 0.880000 | 13.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side, source_quality_risk, realized_loss |
| KXBTC15M-26MAY062015-15 | approved_entry | no | win | 56.000000 | 0.451622 | 0.420000 | approved_entry | yes | loss | -71.000000 | 0.215657 | 0.670000 | -127.000000 | cheap_touch_or_contrarian_side, large_raw_edge_on_cheap_side |
