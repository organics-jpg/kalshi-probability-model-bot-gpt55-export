# v28 Frozen Target-Coverage p70 Empirical-Bayes Runway

- Freeze timestamp UTC: `2026-05-06T04:22:07.414318+00:00`
- Future denominator: `132`
- Selected entries: `96`
- Base-seen markets: `130`
- Coverage: `72.727273`
- Base opportunity summary: `{'base_rows': 130, 'selected_rows': 96, 'raw_lt_60': 66, 'raw_60_70_boundary': 39, 'raw_ge_70_eb_adjustable': 25, 'missing_raw': 0, 'near_edge_miss_lt_2pp': 45, 'high_recross_miss_ge_75': 82, 'eb_adjustable_unselected': 0}`

## Current Read

- Frozen empirical-Bayes p70 has 96 selected markets, 34 markets with base rows that failed the target policy, and 2 markets with no target base row.
- Base rows by raw-probability bucket: <60=66, 60-70 boundary=39, >=70 EB-adjustable=25.
- Unselected EB-adjustable rows: 0; if this stays 0, the blocker is opportunity, not EB probability scoring.

## Markets

| market | status | base rows | selected rows | settled selected |
|---|---|---:|---:|---:|
| KXBTC15M-26MAY060045-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.826505/0.790000/0.036505/0.461756 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.826505/0.790000/0.036505/0.461756 |  |  |  |
| KXBTC15M-26MAY060100-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.799928/0.790000/0.009928/0.407561 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.799928/0.790000/0.009928/0.407561 |  |  |  |
| KXBTC15M-26MAY060115-15 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.513971/0.510000/0.003971/1.023107 |  |  |  |
| KXBTC15M-26MAY060130-30 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.616779/0.590000/0.026779/0.777744 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.616779/0.590000/0.026779/0.777744 |  |  |  |
| KXBTC15M-26MAY060145-45 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.557282/0.550000/0.007282/0.849189 |  |  |  |
| KXBTC15M-26MAY060200-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.618277/0.600000/0.018277/0.767680 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.618277/0.600000/0.018277/0.767680 |  |  |  |
| KXBTC15M-26MAY060215-15 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.583024/0.530000/0.053024/0.792609 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.583024/0.530000/0.053024/0.792609 |  |  |  |
| KXBTC15M-26MAY060230-30 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.574094/0.540000/0.034094/0.789327 |  |  |  |
| KXBTC15M-26MAY060245-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.660829/0.650000/0.010829/0.663720 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.660829/0.650000/0.010829/0.663720 |  |  |  |
| KXBTC15M-26MAY060300-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.661141/0.640000/0.021141/0.620295 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.661141/0.640000/0.021141/0.620295 |  |  |  |
| KXBTC15M-26MAY060315-15 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.512365/0.500000/0.012365/0.857943 |  |  |  |
| KXBTC15M-26MAY060330-30 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.630880/0.570000/0.060880/0.689280 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.630880/0.570000/0.060880/0.689280 |  |  |  |
| KXBTC15M-26MAY060345-45 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.515105/0.380000/0.135105/0.911219 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.515105/0.380000/0.135105/0.911219 |  |  |  |
| KXBTC15M-26MAY060400-00 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.539723/0.500000/0.039723/0.811777 |  |  |  |
| KXBTC15M-26MAY060415-15 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.676831/0.670000/0.006831/0.625830 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.676831/0.670000/0.006831/0.625830 |  |  |  |
| KXBTC15M-26MAY060430-30 | no_target_base_row | 0 | 0 | 0 |
| KXBTC15M-26MAY060445-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.636374/0.450000/0.186374/0.666569 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.636374/0.450000/0.186374/0.666569 |  |  |  |
| KXBTC15M-26MAY060500-00 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.674136/0.610000/0.064136/0.620318 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.674136/0.610000/0.064136/0.620318 |  |  |  |
| KXBTC15M-26MAY060515-15 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.532512/0.410000/0.122512/0.958625 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.532512/0.410000/0.122512/0.958625 |  |  |  |
| KXBTC15M-26MAY060530-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.588889/0.540000/0.048889/0.884715 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.588889/0.540000/0.048889/0.884715 |  |  |  |
| KXBTC15M-26MAY060545-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.626642/0.440000/0.186642/0.689053 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.626642/0.440000/0.186642/0.689053 |  |  |  |
| KXBTC15M-26MAY060600-00 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.792357/0.750000/0.042357/0.552274 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.792357/0.750000/0.042357/0.552274 |  |  |  |
| KXBTC15M-26MAY060615-15 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.598388/0.570000/0.028388/0.915169 |  |  |  |
| KXBTC15M-26MAY060630-30 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.675344/0.660000/0.015344/0.762043 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.675344/0.660000/0.015344/0.762043 |  |  |  |
| KXBTC15M-26MAY060645-45 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.598639/0.590000/0.008639/0.856108 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.598639/0.590000/0.008639/0.856108 |  |  |  |
| KXBTC15M-26MAY060700-00 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.527819/0.520000/0.007819/0.876433 |  |  |  |
| KXBTC15M-26MAY060715-15 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.501801/0.490000/0.011801/1.135459 |  |  |  |
| KXBTC15M-26MAY060730-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.594884/0.560000/0.034884/0.863859 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.594884/0.560000/0.034884/0.863859 |  |  |  |
| KXBTC15M-26MAY060745-45 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.553279/0.540000/0.013279/1.217111 |  |  |  |
| KXBTC15M-26MAY060800-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.523411/0.470000/0.053411/1.358871 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.523411/0.470000/0.053411/1.358871 |  |  |  |
| KXBTC15M-26MAY060815-15 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.505085/0.490000/0.015085/1.192913 |  |  |  |
| KXBTC15M-26MAY060830-30 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.600730/0.590000/0.010730/0.943700 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.600730/0.590000/0.010730/0.943700 |  |  |  |
| KXBTC15M-26MAY060845-45 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.506183/0.500000/0.006183/1.244034 |  |  |  |
| KXBTC15M-26MAY060900-00 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.586412/0.580000/0.006412/0.886305 |  |  |  |
| KXBTC15M-26MAY060915-15 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.672099/0.600000/0.072099/0.831637 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.672099/0.600000/0.072099/0.831637 |  |  |  |
| KXBTC15M-26MAY060930-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.604377/0.600000/0.004377/1.150583 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.604377/0.600000/0.004377/1.150583 |  |  |  |
| KXBTC15M-26MAY060945-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.761891/0.500000/0.261891/0.777721 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.761891/0.500000/0.261891/0.777721 |  |  |  |
| KXBTC15M-26MAY061000-00 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.513222/0.500000/0.013222/1.411643 |  |  |  |
| KXBTC15M-26MAY061015-15 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.595554/0.520000/0.075554/1.130150 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.595554/0.520000/0.075554/1.130150 |  |  |  |
| KXBTC15M-26MAY061030-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.618153/0.610000/0.008153/1.168280 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.618153/0.610000/0.008153/1.168280 |  |  |  |
| KXBTC15M-26MAY061045-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.601767/0.570000/0.031767/1.191443 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.601767/0.570000/0.031767/1.191443 |  |  |  |
| KXBTC15M-26MAY061100-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.740374/0.740000/0.000374/0.809587 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.740374/0.740000/0.000374/0.809587 |  |  |  |
| KXBTC15M-26MAY061115-15 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.533622/0.520000/0.013622/1.452888 |  |  |  |
| KXBTC15M-26MAY061130-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.653101/0.650000/0.003101/1.056221 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.653101/0.650000/0.003101/1.056221 |  |  |  |
| KXBTC15M-26MAY061145-45 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.502076/0.490000/0.012076/1.417050 |  |  |  |
| KXBTC15M-26MAY061200-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.848576/0.810000/0.038576/0.613707 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.848576/0.810000/0.038576/0.613707 |  |  |  |
| KXBTC15M-26MAY061215-15 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.536898/0.530000/0.006898/1.278404 |  |  |  |
| KXBTC15M-26MAY061230-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.681329/0.680000/0.001329/0.862457 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.681329/0.680000/0.001329/0.862457 |  |  |  |
| KXBTC15M-26MAY061245-45 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.555732/0.520000/0.035732/1.211363 |  |  |  |
| KXBTC15M-26MAY061300-00 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.544132/0.540000/0.004132/1.327168 |  |  |  |
| KXBTC15M-26MAY061400-00 | selected | 1 | 1 | 1 |
| -> no approved_entry | base raw/ask/edge/recross 0.973640/0.890000/0.083640/0.051736 |  |  |  |
| -> no approved_entry | selected raw/ask/edge/recross 0.973640/0.890000/0.083640/0.051736 |  |  |  |
| KXBTC15M-26MAY061415-15 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.519091/0.480000/0.039091/1.049181 |  |  |  |
| KXBTC15M-26MAY061430-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.678512/0.670000/0.008512/0.893555 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.678512/0.670000/0.008512/0.893555 |  |  |  |
| KXBTC15M-26MAY061445-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.724164/0.710000/0.014164/0.800263 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.724164/0.710000/0.014164/0.800263 |  |  |  |
| KXBTC15M-26MAY061500-00 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.550910/0.550000/0.000910/1.002871 |  |  |  |
| KXBTC15M-26MAY061515-15 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.518915/0.500000/0.018915/1.055565 |  |  |  |
| KXBTC15M-26MAY061530-30 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.548704/0.530000/0.018704/0.995442 |  |  |  |
| KXBTC15M-26MAY061545-45 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.513617/0.490000/0.023617/0.971969 |  |  |  |
| KXBTC15M-26MAY061600-00 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.610883/0.600000/0.010883/0.723320 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.610883/0.600000/0.010883/0.723320 |  |  |  |
| KXBTC15M-26MAY061615-15 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.770727/0.740000/0.030727/0.500664 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.770727/0.740000/0.030727/0.500664 |  |  |  |
| KXBTC15M-26MAY061630-30 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.631665/0.630000/0.001665/0.450319 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.631665/0.630000/0.001665/0.450319 |  |  |  |
| KXBTC15M-26MAY061645-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.736529/0.710000/0.026529/0.588375 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.736529/0.710000/0.026529/0.588375 |  |  |  |
| KXBTC15M-26MAY061700-00 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.547299/0.490000/0.057299/0.799916 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.547299/0.490000/0.057299/0.799916 |  |  |  |
| KXBTC15M-26MAY061715-15 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.633073/0.500000/0.133073/0.683095 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.633073/0.500000/0.133073/0.683095 |  |  |  |
| KXBTC15M-26MAY061730-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.670106/0.630000/0.040106/0.501796 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.670106/0.630000/0.040106/0.501796 |  |  |  |
| KXBTC15M-26MAY061745-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.510383/0.140000/0.370383/0.689790 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.510383/0.140000/0.370383/0.689790 |  |  |  |
| KXBTC15M-26MAY061800-00 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.700391/0.680000/0.020391/0.545766 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.700391/0.680000/0.020391/0.545766 |  |  |  |
| KXBTC15M-26MAY061815-15 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.794472/0.720000/0.074472/0.363637 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.794472/0.720000/0.074472/0.363637 |  |  |  |
| KXBTC15M-26MAY061830-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.553162/0.230000/0.323162/0.631576 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.553162/0.230000/0.323162/0.631576 |  |  |  |
| KXBTC15M-26MAY061845-45 | no_target_base_row | 0 | 0 | 0 |
| KXBTC15M-26MAY061900-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.501794/0.340000/0.161794/0.794136 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.501794/0.340000/0.161794/0.794136 |  |  |  |
| KXBTC15M-26MAY061915-15 | selected | 1 | 1 | 1 |
| -> no approved_entry | base raw/ask/edge/recross 0.923342/0.870000/0.053342/0.229504 |  |  |  |
| -> no approved_entry | selected raw/ask/edge/recross 0.923342/0.870000/0.053342/0.229504 |  |  |  |
| KXBTC15M-26MAY061930-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.551364/0.470000/0.081364/0.905378 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.551364/0.470000/0.081364/0.905378 |  |  |  |
| KXBTC15M-26MAY061945-45 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.542407/0.420000/0.122407/0.801256 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.542407/0.420000/0.122407/0.801256 |  |  |  |
| KXBTC15M-26MAY062000-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.582435/0.500000/0.082435/0.673972 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.582435/0.500000/0.082435/0.673972 |  |  |  |
| KXBTC15M-26MAY062015-15 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.526847/0.510000/0.016847/0.736601 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.526847/0.510000/0.016847/0.736601 |  |  |  |
| KXBTC15M-26MAY062030-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.544418/0.320000/0.224418/0.680770 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.544418/0.320000/0.224418/0.680770 |  |  |  |
| KXBTC15M-26MAY062045-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.617920/0.510000/0.107920/0.590304 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.617920/0.510000/0.107920/0.590304 |  |  |  |
| KXBTC15M-26MAY062100-00 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.615588/0.220000/0.395588/0.515467 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.615588/0.220000/0.395588/0.515467 |  |  |  |
| KXBTC15M-26MAY062115-15 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.543753/0.530000/0.013753/0.866336 |  |  |  |
| KXBTC15M-26MAY062130-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.586142/0.410000/0.176142/0.800157 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.586142/0.410000/0.176142/0.800157 |  |  |  |
| KXBTC15M-26MAY062145-45 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.600378/0.570000/0.030378/0.820982 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.600378/0.570000/0.030378/0.820982 |  |  |  |
| KXBTC15M-26MAY062200-00 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.617816/0.460000/0.157816/0.567395 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.617816/0.460000/0.157816/0.567395 |  |  |  |
| KXBTC15M-26MAY062215-15 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.661831/0.590000/0.071831/0.669869 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.661831/0.590000/0.071831/0.669869 |  |  |  |
| KXBTC15M-26MAY062230-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.718015/0.380000/0.338015/0.349672 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.718015/0.380000/0.338015/0.349672 |  |  |  |
| KXBTC15M-26MAY062245-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.605951/0.540000/0.065951/0.786584 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.605951/0.540000/0.065951/0.786584 |  |  |  |
| KXBTC15M-26MAY062300-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.758354/0.730000/0.028354/0.572785 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.758354/0.730000/0.028354/0.572785 |  |  |  |
| KXBTC15M-26MAY062315-15 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.744580/0.680000/0.064580/0.455010 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.744580/0.680000/0.064580/0.455010 |  |  |  |
| KXBTC15M-26MAY062330-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.546903/0.520000/0.026903/0.717935 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.546903/0.520000/0.026903/0.717935 |  |  |  |
| KXBTC15M-26MAY062345-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.608623/0.460000/0.148623/0.675325 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.608623/0.460000/0.148623/0.675325 |  |  |  |
| KXBTC15M-26MAY070000-00 | selected | 1 | 1 | 1 |
| -> no approved_entry | base raw/ask/edge/recross 0.863962/0.780000/0.083962/0.193188 |  |  |  |
| -> no approved_entry | selected raw/ask/edge/recross 0.863962/0.780000/0.083962/0.193188 |  |  |  |
| KXBTC15M-26MAY070015-15 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.560075/0.560000/0.000075/0.785731 |  |  |  |
| KXBTC15M-26MAY070030-30 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.523605/0.330000/0.193605/0.901651 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.523605/0.330000/0.193605/0.901651 |  |  |  |
| KXBTC15M-26MAY070045-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.582164/0.480000/0.102164/0.830545 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.582164/0.480000/0.102164/0.830545 |  |  |  |
| KXBTC15M-26MAY070100-00 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.505013/0.220000/0.285013/0.647900 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.505013/0.220000/0.285013/0.647900 |  |  |  |
| KXBTC15M-26MAY070115-15 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.773654/0.720000/0.053654/0.488844 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.773654/0.720000/0.053654/0.488844 |  |  |  |
| KXBTC15M-26MAY070130-30 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.604140/0.590000/0.014140/0.544225 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.604140/0.590000/0.014140/0.544225 |  |  |  |
| KXBTC15M-26MAY070145-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.838040/0.810000/0.028040/0.206140 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.838040/0.810000/0.028040/0.206140 |  |  |  |
| KXBTC15M-26MAY070200-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.505710/0.300000/0.205710/0.602432 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.505710/0.300000/0.205710/0.602432 |  |  |  |
| KXBTC15M-26MAY070530-30 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.540822/0.480000/0.060822/0.894668 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.540822/0.480000/0.060822/0.894668 |  |  |  |
| KXBTC15M-26MAY070545-45 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.707647/0.600000/0.107647/0.622015 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.707647/0.600000/0.107647/0.622015 |  |  |  |
| KXBTC15M-26MAY070600-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.723960/0.670000/0.053960/0.394421 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.723960/0.670000/0.053960/0.394421 |  |  |  |
| KXBTC15M-26MAY070615-15 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.610872/0.280000/0.330872/0.645491 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.610872/0.280000/0.330872/0.645491 |  |  |  |
| KXBTC15M-26MAY070630-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.606974/0.470000/0.136974/0.826469 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.606974/0.470000/0.136974/0.826469 |  |  |  |
| KXBTC15M-26MAY070645-45 | selected | 1 | 1 | 1 |
| -> yes approved_entry | base raw/ask/edge/recross 0.895399/0.810000/0.085399/0.368798 |  |  |  |
| -> yes approved_entry | selected raw/ask/edge/recross 0.895399/0.810000/0.085399/0.368798 |  |  |  |
| KXBTC15M-26MAY070700-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.654812/0.560000/0.094812/0.760124 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.654812/0.560000/0.094812/0.760124 |  |  |  |
| KXBTC15M-26MAY070715-15 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.560435/0.510000/0.050435/0.877232 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.560435/0.510000/0.050435/0.877232 |  |  |  |
| KXBTC15M-26MAY070730-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.530778/0.460000/0.070778/0.936121 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.530778/0.460000/0.070778/0.936121 |  |  |  |
| KXBTC15M-26MAY070745-45 | selected | 1 | 1 | 1 |
| -> yes approved_entry | base raw/ask/edge/recross 0.903807/0.680000/0.223807/0.197594 |  |  |  |
| -> yes approved_entry | selected raw/ask/edge/recross 0.903807/0.680000/0.223807/0.197594 |  |  |  |
| KXBTC15M-26MAY070800-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.536385/0.450000/0.086385/0.865475 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.536385/0.450000/0.086385/0.865475 |  |  |  |
| KXBTC15M-26MAY070815-15 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.501147/0.440000/0.061147/1.067161 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.501147/0.440000/0.061147/1.067161 |  |  |  |
| KXBTC15M-26MAY070830-30 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.514492/0.410000/0.104492/0.952791 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.514492/0.410000/0.104492/0.952791 |  |  |  |
| KXBTC15M-26MAY070845-45 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.596088/0.450000/0.146088/0.596576 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.596088/0.450000/0.146088/0.596576 |  |  |  |
| KXBTC15M-26MAY070900-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.597604/0.550000/0.047604/0.771689 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.597604/0.550000/0.047604/0.771689 |  |  |  |
| KXBTC15M-26MAY070915-15 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.788001/0.750000/0.038001/0.519751 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.788001/0.750000/0.038001/0.519751 |  |  |  |
| KXBTC15M-26MAY070930-30 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.511849/0.480000/0.031849/1.050154 |  |  |  |
| KXBTC15M-26MAY070945-45 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.532085/0.480000/0.052085/1.088863 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.532085/0.480000/0.052085/1.088863 |  |  |  |
| KXBTC15M-26MAY071000-00 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.543510/0.540000/0.003510/1.219674 |  |  |  |
| KXBTC15M-26MAY071015-15 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.609894/0.600000/0.009894/1.102864 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.609894/0.600000/0.009894/1.102864 |  |  |  |
| KXBTC15M-26MAY071030-30 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.646380/0.620000/0.026380/1.053270 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.646380/0.620000/0.026380/1.053270 |  |  |  |
| KXBTC15M-26MAY071045-45 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.557862/0.550000/0.007862/1.306314 |  |  |  |
| KXBTC15M-26MAY071100-00 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.578800/0.560000/0.018800/1.073938 |  |  |  |
| KXBTC15M-26MAY071115-15 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.635838/0.620000/0.015838/0.982771 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.635838/0.620000/0.015838/0.982771 |  |  |  |
| KXBTC15M-26MAY071130-30 | base_seen_not_selected | 1 | 0 | 0 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.582087/0.580000/0.002087/0.927686 |  |  |  |
| KXBTC15M-26MAY071145-45 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.645637/0.610000/0.035637/1.101255 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.645637/0.610000/0.035637/1.101255 |  |  |  |
| KXBTC15M-26MAY071200-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.606055/0.600000/0.006055/1.096302 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.606055/0.600000/0.006055/1.096302 |  |  |  |
| KXBTC15M-26MAY071215-15 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.509397/0.470000/0.039397/1.397041 |  |  |  |
| KXBTC15M-26MAY071230-30 | selected | 1 | 1 | 1 |
| -> no rejected_actionable | base raw/ask/edge/recross 0.729882/0.700000/0.029882/0.815016 |  |  |  |
| -> no rejected_actionable | selected raw/ask/edge/recross 0.729882/0.700000/0.029882/0.815016 |  |  |  |
| KXBTC15M-26MAY071245-45 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.559979/0.550000/0.009979/1.255835 |  |  |  |
| KXBTC15M-26MAY071300-00 | selected | 1 | 1 | 1 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.636040/0.590000/0.046040/1.011545 |  |  |  |
| -> yes rejected_actionable | selected raw/ask/edge/recross 0.636040/0.590000/0.046040/1.011545 |  |  |  |
| KXBTC15M-26MAY071315-15 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.533442/0.510000/0.023442/1.215232 |  |  |  |
| KXBTC15M-26MAY071330-30 | base_seen_not_selected | 1 | 0 | 0 |
| -> yes rejected_actionable | base raw/ask/edge/recross 0.544206/0.520000/0.024206/1.086679 |  |  |  |
