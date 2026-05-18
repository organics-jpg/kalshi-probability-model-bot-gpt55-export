# v28 Calibrated FV Forward Monitor

Monitor for clean forward markets after the calibrated-FV freeze. Not a promotion rule.

- Freeze timestamp UTC: `2026-05-05T23:30:17.615882+00:00`
- Clean forward markets: `152`
- Selected/settled/pending/missed: `150/150/0/2`
- Coverage: `98.684211`
- Settled W/L and net: `83/67` / `-1009.000000c`
- Calibration deltas, +5 minus raw Brier/logloss: `1.455557` / `2.734740`
- Excluded partial markets: `[]`
- Latest observation time: `2026-05-07T17:22:28.173032+00:00`

## Clean Forward Markets

| market | selected | close state | sec to/since close | side | source | p raw | p +5 | ask | edge | won | net c | brier d | logloss d | first reason |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| KXBTC15M-26MAY051945-45 | True | settled | -149848.173032 | yes | rejected_actionable | 0.613944 | 0.663944 | 0.510000 | 0.103944 | True | 94.000000 | -0.036106 | -0.078294 | p_below_floor |
| KXBTC15M-26MAY052000-00 | True | settled | -148948.173032 | no | rejected_actionable | 0.665463 | 0.715463 | 0.630000 | 0.035463 | True | 70.000000 | -0.030954 | -0.072447 | p_below_floor |
| KXBTC15M-26MAY052015-15 | True | settled | -148048.173032 | no | rejected_actionable | 0.567861 | 0.617861 | 0.490000 | 0.077861 | False | -102.000000 | 0.059286 | 0.122963 | p_below_floor |
| KXBTC15M-26MAY052030-30 | True | settled | -147148.173032 | yes | rejected_actionable | 0.540780 | 0.590780 | 0.470000 | 0.070780 | False | -98.000000 | 0.056578 | 0.115276 | p_below_floor |
| KXBTC15M-26MAY052045-45 | True | settled | -146248.173032 | yes | rejected_actionable | 0.590266 | 0.640266 | 0.560000 | 0.030266 | False | -116.000000 | 0.061527 | 0.130143 | p_below_floor |
| KXBTC15M-26MAY052100-00 | True | settled | -145348.173032 | yes | rejected_actionable | 0.565554 | 0.615554 | 0.460000 | 0.105554 | True | 104.000000 | -0.040945 | -0.084717 | p_below_floor |
| KXBTC15M-26MAY052115-15 | True | settled | -144448.173032 | yes | rejected_actionable | 0.571476 | 0.621476 | 0.530000 | 0.041476 | True | 90.000000 | -0.040352 | -0.083875 | p_below_floor |
| KXBTC15M-26MAY052130-30 | True | settled | -143548.173032 | yes | rejected_actionable | 0.822836 | 0.872836 | 0.800000 | 0.022836 | True | 37.000000 | -0.015216 | -0.058991 | p_below_floor |
| KXBTC15M-26MAY052145-45 | True | settled | -142648.173032 | yes | rejected_actionable | 0.865417 | 0.915417 | 0.830000 | 0.035417 | True | 32.000000 | -0.010958 | -0.056168 | p_below_floor |
| KXBTC15M-26MAY052200-00 | True | settled | -141748.173032 | no | rejected_actionable | 0.551743 | 0.601743 | 0.520000 | 0.031743 | False | -108.000000 | 0.057674 | 0.118269 | p_below_floor |
| KXBTC15M-26MAY052215-15 | True | settled | -140848.173032 | no | rejected_actionable | 0.809232 | 0.859232 | 0.770000 | 0.039232 | True | 43.000000 | -0.016577 | -0.059953 | p_below_floor |
| KXBTC15M-26MAY052230-30 | True | settled | -139948.173032 | no | rejected_actionable | 0.730624 | 0.780624 | 0.650000 | 0.080624 | True | 66.000000 | -0.024438 | -0.066195 | p_below_floor |
| KXBTC15M-26MAY052245-45 | True | settled | -139048.173032 | no | rejected_actionable | 0.643789 | 0.693789 | 0.570000 | 0.073789 | False | -118.000000 | 0.066879 | 0.151249 | p_below_floor |
| KXBTC15M-26MAY052300-00 | True | settled | -138148.173032 | yes | approved_entry | 0.918967 | 0.968967 | 0.850000 | 0.068967 | True | 26.000000 | -0.005603 | -0.052980 | p_below_floor |
| KXBTC15M-26MAY052315-15 | True | settled | -137248.173032 | yes | approved_entry | 0.884999 | 0.934999 | 0.810000 | 0.074999 | True | -41.000000 | -0.009000 | -0.054959 | p_below_floor |
| KXBTC15M-26MAY052330-30 | True | settled | -136348.173032 | no | rejected_actionable | 0.659176 | 0.709176 | 0.630000 | 0.029176 | False | -130.000000 | 0.068418 | 0.158648 | p_below_floor |
| KXBTC15M-26MAY052345-45 | True | settled | -135448.173032 | no | rejected_actionable | 0.636767 | 0.686767 | 0.630000 | 0.006767 | True | 70.000000 | -0.033823 | -0.075591 | p_below_floor |
| KXBTC15M-26MAY060000-00 | True | settled | -134548.173032 | no | rejected_actionable | 0.576655 | 0.626655 | 0.560000 | 0.016655 | False | -116.000000 | 0.060166 | 0.125685 | p_below_floor |
| KXBTC15M-26MAY060015-15 | True | settled | -133648.173032 | yes | rejected_actionable | 0.532782 | 0.582782 | 0.520000 | 0.012782 | False | -108.000000 | 0.055778 | 0.113187 | p_below_floor |
| KXBTC15M-26MAY060030-30 | True | settled | -132748.173032 | yes | rejected_actionable | 0.617077 | 0.667077 | 0.510000 | 0.107077 | False | -106.000000 | 0.064208 | 0.139923 | p_below_floor |
| KXBTC15M-26MAY060045-45 | True | settled | -131848.173032 | no | rejected_actionable | 0.826505 | 0.876505 | 0.790000 | 0.036505 | True | 39.000000 | -0.014850 | -0.058736 | p_below_floor |
| KXBTC15M-26MAY060100-00 | True | settled | -130948.173032 | yes | rejected_actionable | 0.799928 | 0.849928 | 0.790000 | 0.009928 | False | -161.000000 | 0.082493 | 0.287562 | p_below_floor |
| KXBTC15M-26MAY060115-15 | True | settled | -130048.173032 | no | rejected_actionable | 0.513971 | 0.563971 | 0.510000 | 0.003971 | True | 94.000000 | -0.046103 | -0.092836 | p_below_floor |
| KXBTC15M-26MAY060130-30 | True | settled | -129148.173032 | no | rejected_actionable | 0.616779 | 0.666779 | 0.590000 | 0.026779 | True | 78.000000 | -0.035822 | -0.077948 | p_below_floor |
| KXBTC15M-26MAY060145-45 | True | settled | -128248.173032 | no | rejected_actionable | 0.557282 | 0.607282 | 0.550000 | 0.007282 | True | 86.000000 | -0.041772 | -0.085922 | p_below_floor |
| KXBTC15M-26MAY060200-00 | True | settled | -127348.173032 | yes | rejected_actionable | 0.618277 | 0.668277 | 0.600000 | 0.018277 | True | 76.000000 | -0.035672 | -0.077766 | p_below_floor |
| KXBTC15M-26MAY060215-15 | True | settled | -126448.173032 | yes | rejected_actionable | 0.583024 | 0.633024 | 0.530000 | 0.053024 | False | -110.000000 | 0.060802 | 0.127732 | p_below_floor |
| KXBTC15M-26MAY060230-30 | True | settled | -125548.173032 | no | rejected_actionable | 0.574094 | 0.624094 | 0.540000 | 0.034094 | False | -112.000000 | 0.059909 | 0.124880 | p_below_floor |
| KXBTC15M-26MAY060245-45 | True | settled | -124648.173032 | no | rejected_actionable | 0.660829 | 0.710829 | 0.650000 | 0.010829 | False | -134.000000 | 0.068583 | 0.159486 | p_below_floor |
| KXBTC15M-26MAY060300-00 | True | settled | -123748.173032 | yes | rejected_actionable | 0.661141 | 0.711141 | 0.640000 | 0.021141 | True | 68.000000 | -0.031386 | -0.072904 | p_below_floor |
| KXBTC15M-26MAY060315-15 | True | settled | -122848.173032 | yes | rejected_actionable | 0.512365 | 0.562365 | 0.500000 | 0.012365 | True | 96.000000 | -0.046264 | -0.093114 | p_below_floor |
| KXBTC15M-26MAY060330-30 | True | settled | -121948.173032 | no | rejected_actionable | 0.630880 | 0.680880 | 0.570000 | 0.060880 | False | -118.000000 | 0.065588 | 0.145555 | p_below_floor |
| KXBTC15M-26MAY060345-45 | True | settled | -121048.173032 | yes | rejected_actionable | 0.515105 | 0.565105 | 0.380000 | 0.135105 | False | -80.000000 | 0.054011 | 0.108828 | p_below_floor |
| KXBTC15M-26MAY060400-00 | True | settled | -120148.173032 | yes | rejected_actionable | 0.539723 | 0.589723 | 0.500000 | 0.039723 | False | -104.000000 | 0.056472 | 0.114996 | p_below_floor |
| KXBTC15M-26MAY060415-15 | True | settled | -119248.173032 | yes | rejected_actionable | 0.676831 | 0.726831 | 0.670000 | 0.006831 | True | 62.000000 | -0.029817 | -0.071272 | p_below_floor |
| KXBTC15M-26MAY060430-30 | False | None | None | None | None | None | None | None | None | None | None | None | None | p_below_floor |
| KXBTC15M-26MAY060445-45 | True | settled | -117448.173032 | no | rejected_actionable | 0.636374 | 0.686374 | 0.450000 | 0.186374 | False | -94.000000 | 0.066137 | 0.147925 | p_below_floor |
| KXBTC15M-26MAY060500-00 | True | settled | -116548.173032 | no | rejected_actionable | 0.674136 | 0.724136 | 0.610000 | 0.064136 | False | -126.000000 | 0.069914 | 0.166572 | p_below_floor |
| KXBTC15M-26MAY060515-15 | True | settled | -115648.173032 | yes | rejected_actionable | 0.532512 | 0.582512 | 0.410000 | 0.122512 | False | -86.000000 | 0.055751 | 0.113118 | p_below_floor |
| KXBTC15M-26MAY060530-30 | True | settled | -114748.173032 | yes | rejected_actionable | 0.588889 | 0.638889 | 0.540000 | 0.048889 | False | -112.000000 | 0.061389 | 0.129678 | p_below_floor |
| KXBTC15M-26MAY060545-45 | True | settled | -113848.173032 | no | rejected_actionable | 0.626642 | 0.676642 | 0.440000 | 0.186642 | False | -92.000000 | 0.065164 | 0.143778 | p_below_floor |
| KXBTC15M-26MAY060600-00 | True | settled | -112948.173032 | no | rejected_actionable | 0.792357 | 0.842357 | 0.750000 | 0.042357 | True | 47.000000 | -0.018264 | -0.061192 | p_below_floor |
| KXBTC15M-26MAY060615-15 | True | settled | -112048.173032 | yes | rejected_actionable | 0.598388 | 0.648388 | 0.570000 | 0.028388 | True | 41.000000 | -0.037661 | -0.080250 | p_below_floor |
| KXBTC15M-26MAY060630-30 | True | settled | -111148.173032 | no | rejected_actionable | 0.675344 | 0.725344 | 0.660000 | 0.015344 | False | -136.000000 | 0.070034 | 0.167247 | p_below_floor |
| KXBTC15M-26MAY060645-45 | True | settled | -110248.173032 | yes | rejected_actionable | 0.598639 | 0.648639 | 0.590000 | 0.008639 | True | 78.000000 | -0.037636 | -0.080218 | p_below_floor |
| KXBTC15M-26MAY060700-00 | True | settled | -109348.173032 | yes | rejected_actionable | 0.527819 | 0.577819 | 0.520000 | 0.007819 | True | 92.000000 | -0.044718 | -0.090507 | p_below_floor |
| KXBTC15M-26MAY060715-15 | True | settled | -108448.173032 | yes | rejected_actionable | 0.501801 | 0.551801 | 0.490000 | 0.011801 | True | 98.000000 | -0.047320 | -0.094984 | p_below_floor |
| KXBTC15M-26MAY060730-30 | True | settled | -107548.173032 | yes | rejected_actionable | 0.594884 | 0.644884 | 0.560000 | 0.034884 | True | 84.000000 | -0.038012 | -0.080704 | p_below_floor |
| KXBTC15M-26MAY060745-45 | True | settled | -106648.173032 | no | rejected_actionable | 0.553279 | 0.603279 | 0.540000 | 0.013279 | True | 88.000000 | -0.042172 | -0.086517 | p_below_floor |
| KXBTC15M-26MAY060800-00 | True | settled | -105748.173032 | yes | rejected_actionable | 0.523411 | 0.573411 | 0.470000 | 0.053411 | True | 102.000000 | -0.045159 | -0.091236 | p_below_floor |
| KXBTC15M-26MAY060815-15 | True | settled | -104848.173032 | no | rejected_actionable | 0.505085 | 0.555085 | 0.490000 | 0.015085 | True | 98.000000 | -0.046992 | -0.094395 | p_below_floor |
| KXBTC15M-26MAY060830-30 | True | settled | -103948.173032 | no | rejected_actionable | 0.600730 | 0.650730 | 0.590000 | 0.010730 | False | -122.000000 | 0.062573 | 0.133793 | p_below_floor |
| KXBTC15M-26MAY060845-45 | True | settled | -103048.173032 | yes | rejected_actionable | 0.506183 | 0.556183 | 0.500000 | 0.006183 | False | -104.000000 | 0.053118 | 0.106753 | p_below_floor |
| KXBTC15M-26MAY060900-00 | True | settled | -102148.173032 | no | rejected_actionable | 0.586412 | 0.636412 | 0.580000 | 0.006412 | True | 80.000000 | -0.038859 | -0.081824 | p_below_floor |
| KXBTC15M-26MAY060915-15 | True | settled | -101248.173032 | no | rejected_actionable | 0.672099 | 0.722099 | 0.600000 | 0.072099 | True | 76.000000 | -0.030290 | -0.071757 | p_below_floor |
| KXBTC15M-26MAY060930-30 | True | settled | -100348.173032 | yes | rejected_actionable | 0.604377 | 0.654377 | 0.600000 | 0.004377 | False | -124.000000 | 0.062938 | 0.135113 | p_below_floor |
| KXBTC15M-26MAY060945-45 | True | settled | -99448.173032 | no | rejected_actionable | 0.761891 | 0.811891 | 0.500000 | 0.261891 | True | 96.000000 | -0.021311 | -0.063563 | p_below_floor |
| KXBTC15M-26MAY061000-00 | True | settled | -98548.173032 | no | rejected_actionable | 0.513222 | 0.563222 | 0.500000 | 0.013222 | True | 96.000000 | -0.046178 | -0.092965 | p_below_floor |
| KXBTC15M-26MAY061015-15 | True | settled | -97648.173032 | no | rejected_actionable | 0.595554 | 0.645554 | 0.520000 | 0.075554 | True | 92.000000 | -0.037945 | -0.080617 | p_below_floor |
| KXBTC15M-26MAY061030-30 | True | settled | -96748.173032 | yes | rejected_actionable | 0.618153 | 0.668153 | 0.610000 | 0.008153 | True | 74.000000 | -0.035685 | -0.077781 | p_below_floor |
| KXBTC15M-26MAY061045-45 | True | settled | -95848.173032 | no | rejected_actionable | 0.601767 | 0.651767 | 0.570000 | 0.031767 | False | -118.000000 | 0.062677 | 0.134165 | p_below_floor |
| KXBTC15M-26MAY061100-00 | True | settled | -94948.173032 | yes | rejected_actionable | 0.740374 | 0.790374 | 0.740000 | 0.000374 | False | -151.000000 | 0.076537 | 0.213917 | p_below_floor |
| KXBTC15M-26MAY061115-15 | True | settled | -94048.173032 | yes | rejected_actionable | 0.533622 | 0.583622 | 0.520000 | 0.013622 | False | -108.000000 | 0.055862 | 0.113403 | p_below_floor |
| KXBTC15M-26MAY061130-30 | True | settled | -93148.173032 | yes | rejected_actionable | 0.653101 | 0.703101 | 0.650000 | 0.003101 | True | 66.000000 | -0.032190 | -0.073769 | p_below_floor |
| KXBTC15M-26MAY061145-45 | True | settled | -92248.173032 | no | rejected_actionable | 0.502076 | 0.552076 | 0.490000 | 0.012076 | True | 98.000000 | -0.047292 | -0.094934 | p_below_floor |
| KXBTC15M-26MAY061200-00 | True | settled | -91348.173032 | yes | rejected_actionable | 0.848576 | 0.898576 | 0.810000 | 0.038576 | True | 35.000000 | -0.012642 | -0.057252 | p_below_floor |
| KXBTC15M-26MAY061215-15 | True | settled | -90448.173032 | no | rejected_actionable | 0.536898 | 0.586898 | 0.530000 | 0.006898 | False | -110.000000 | 0.056190 | 0.114253 | p_below_floor |
| KXBTC15M-26MAY061230-30 | True | settled | -89548.173032 | yes | rejected_actionable | 0.681329 | 0.731329 | 0.680000 | 0.001329 | False | -140.000000 | 0.070633 | 0.170672 | p_below_floor |
| KXBTC15M-26MAY061245-45 | True | settled | -88648.173032 | no | rejected_actionable | 0.555732 | 0.605732 | 0.520000 | 0.035732 | False | -108.000000 | 0.058073 | 0.119397 | p_below_floor |
| KXBTC15M-26MAY061300-00 | True | settled | -87748.173032 | no | rejected_actionable | 0.544132 | 0.594132 | 0.540000 | 0.004132 | True | 88.000000 | -0.043087 | -0.087910 | p_below_floor |
| KXBTC15M-26MAY061400-00 | True | settled | -84148.173032 | no | approved_entry | 0.973640 | 0.999999 | 0.890000 | 0.083640 | True | -11.000000 | -0.000695 | -0.026713 | approved_entry |
| KXBTC15M-26MAY061415-15 | True | settled | -83248.173032 | no | rejected_actionable | 0.519091 | 0.569091 | 0.480000 | 0.039091 | True | 100.000000 | -0.045591 | -0.091961 | p_below_floor |
| KXBTC15M-26MAY061430-30 | True | settled | -82348.173032 | yes | rejected_actionable | 0.678512 | 0.728512 | 0.670000 | 0.008512 | True | 62.000000 | -0.029649 | -0.071102 | p_below_floor |
| KXBTC15M-26MAY061445-45 | True | settled | -81448.173032 | no | rejected_actionable | 0.724164 | 0.774164 | 0.710000 | 0.014164 | True | 55.000000 | -0.025084 | -0.066766 | p_below_floor |
| KXBTC15M-26MAY061500-00 | True | settled | -80548.173032 | yes | rejected_actionable | 0.550910 | 0.600910 | 0.550000 | 0.000910 | False | -114.000000 | 0.057591 | 0.118036 | p_below_floor |
| KXBTC15M-26MAY061515-15 | True | settled | -79648.173032 | no | rejected_actionable | 0.518915 | 0.568915 | 0.500000 | 0.018915 | True | 96.000000 | -0.045609 | -0.091991 | p_below_floor |
| KXBTC15M-26MAY061530-30 | True | settled | -78748.173032 | no | rejected_actionable | 0.548704 | 0.598704 | 0.530000 | 0.018704 | False | -110.000000 | 0.057370 | 0.117424 | p_below_floor |
| KXBTC15M-26MAY061545-45 | True | settled | -77848.173032 | no | rejected_actionable | 0.513617 | 0.563617 | 0.490000 | 0.023617 | False | -102.000000 | 0.053862 | 0.108476 | p_below_floor |
| KXBTC15M-26MAY061600-00 | True | settled | -76948.173032 | no | rejected_actionable | 0.610883 | 0.660883 | 0.600000 | 0.010883 | False | -124.000000 | 0.063588 | 0.137535 | p_below_floor |
| KXBTC15M-26MAY061615-15 | True | settled | -76048.173032 | yes | rejected_actionable | 0.770727 | 0.820727 | 0.740000 | 0.030727 | True | 49.000000 | -0.020427 | -0.062856 | p_below_floor |
| KXBTC15M-26MAY061630-30 | True | settled | -75148.173032 | no | rejected_actionable | 0.631665 | 0.681665 | 0.630000 | 0.001665 | True | 70.000000 | -0.034334 | -0.076179 | p_below_floor |
| KXBTC15M-26MAY061645-45 | True | settled | -74248.173032 | no | rejected_actionable | 0.736529 | 0.786529 | 0.710000 | 0.026529 | True | 55.000000 | -0.023847 | -0.065681 | p_below_floor |
| KXBTC15M-26MAY061700-00 | True | settled | -73348.173032 | no | rejected_actionable | 0.547299 | 0.597299 | 0.490000 | 0.057299 | False | -102.000000 | 0.057230 | 0.117038 | p_below_floor |
| KXBTC15M-26MAY061715-15 | True | settled | -72448.173032 | yes | rejected_actionable | 0.633073 | 0.683073 | 0.500000 | 0.133073 | False | -104.000000 | 0.065807 | 0.146491 | p_below_floor |
| KXBTC15M-26MAY061730-30 | True | settled | -71548.173032 | yes | rejected_actionable | 0.670106 | 0.720106 | 0.630000 | 0.040106 | True | 70.000000 | -0.030489 | -0.071963 | p_below_floor |
| KXBTC15M-26MAY061745-45 | True | settled | -70648.173032 | no | rejected_actionable | 0.510383 | 0.560383 | 0.140000 | 0.370383 | False | -30.000000 | 0.053538 | 0.107720 | p_below_floor |
| KXBTC15M-26MAY061800-00 | True | settled | -69748.173032 | no | rejected_actionable | 0.700391 | 0.750391 | 0.680000 | 0.020391 | True | 60.000000 | -0.027461 | -0.068956 | p_below_floor |
| KXBTC15M-26MAY061815-15 | True | settled | -68848.173032 | no | rejected_actionable | 0.794472 | 0.844472 | 0.720000 | 0.074472 | True | 53.000000 | -0.018053 | -0.061034 | p_below_floor |
| KXBTC15M-26MAY061830-30 | True | settled | -67948.173032 | yes | rejected_actionable | 0.553162 | 0.603162 | 0.230000 | 0.323162 | False | -49.000000 | 0.057816 | 0.118668 | p_below_floor |
| KXBTC15M-26MAY061845-45 | False | None | None | None | None | None | None | None | None | None | None | None | None | p_below_floor |
| KXBTC15M-26MAY061900-00 | True | settled | -66148.173032 | yes | rejected_actionable | 0.501794 | 0.551794 | 0.340000 | 0.161794 | True | 128.000000 | -0.047321 | -0.094985 | p_below_floor |
| KXBTC15M-26MAY061915-15 | True | settled | -65248.173032 | no | approved_entry | 0.923342 | 0.973342 | 0.870000 | 0.053342 | True | 22.000000 | -0.005166 | -0.052736 | p_below_floor |
| KXBTC15M-26MAY061930-30 | True | settled | -64348.173032 | yes | rejected_actionable | 0.551364 | 0.601364 | 0.470000 | 0.081364 | True | 102.000000 | -0.042364 | -0.086805 | p_below_floor |
| KXBTC15M-26MAY061945-45 | True | settled | -63448.173032 | yes | rejected_actionable | 0.542407 | 0.592407 | 0.420000 | 0.122407 | False | -88.000000 | 0.056741 | 0.115711 | p_below_floor |
| KXBTC15M-26MAY062000-00 | True | settled | -62548.173032 | yes | rejected_actionable | 0.582435 | 0.632435 | 0.500000 | 0.082435 | True | 96.000000 | -0.039257 | -0.082360 | p_below_floor |
| KXBTC15M-26MAY062015-15 | True | settled | -61648.173032 | yes | rejected_actionable | 0.526847 | 0.576847 | 0.510000 | 0.016847 | False | -106.000000 | 0.055185 | 0.111685 | p_below_floor |
| KXBTC15M-26MAY062030-30 | True | settled | -60748.173032 | yes | rejected_actionable | 0.544418 | 0.594418 | 0.320000 | 0.224418 | False | -68.000000 | 0.056942 | 0.116253 | p_below_floor |
| KXBTC15M-26MAY062045-45 | True | settled | -59848.173032 | no | rejected_actionable | 0.617920 | 0.667920 | 0.510000 | 0.107920 | True | 94.000000 | -0.035708 | -0.077809 | p_below_floor |
| KXBTC15M-26MAY062100-00 | True | settled | -58948.173032 | no | rejected_actionable | 0.615588 | 0.665588 | 0.220000 | 0.395588 | False | -47.000000 | 0.064059 | 0.139341 | p_below_floor |
| KXBTC15M-26MAY062115-15 | True | settled | -58048.173032 | yes | rejected_actionable | 0.543753 | 0.593753 | 0.530000 | 0.013753 | True | 90.000000 | -0.043125 | -0.087968 | p_below_floor |
| KXBTC15M-26MAY062130-30 | True | settled | -57148.173032 | yes | rejected_actionable | 0.586142 | 0.636142 | 0.410000 | 0.176142 | True | 114.000000 | -0.038886 | -0.081860 | p_below_floor |
| KXBTC15M-26MAY062145-45 | True | settled | -56248.173032 | yes | rejected_actionable | 0.600378 | 0.650378 | 0.570000 | 0.030378 | True | 82.000000 | -0.037462 | -0.079994 | p_below_floor |
| KXBTC15M-26MAY062200-00 | True | settled | -55348.173032 | no | rejected_actionable | 0.617816 | 0.667816 | 0.460000 | 0.157816 | True | 104.000000 | -0.035718 | -0.077822 | p_below_floor |
| KXBTC15M-26MAY062215-15 | True | settled | -54448.173032 | no | rejected_actionable | 0.661831 | 0.711831 | 0.590000 | 0.071831 | True | 78.000000 | -0.031317 | -0.072830 | p_below_floor |
| KXBTC15M-26MAY062230-30 | True | settled | -53548.173032 | yes | rejected_actionable | 0.718015 | 0.768015 | 0.380000 | 0.338015 | False | -80.000000 | 0.074302 | 0.195181 | p_below_floor |
| KXBTC15M-26MAY062245-45 | True | settled | -52648.173032 | no | rejected_actionable | 0.605951 | 0.655951 | 0.540000 | 0.065951 | False | -112.000000 | 0.063095 | 0.135691 | p_below_floor |
| KXBTC15M-26MAY062300-00 | True | settled | -51748.173032 | yes | rejected_actionable | 0.758354 | 0.808354 | 0.730000 | 0.028354 | True | 51.000000 | -0.021665 | -0.063850 | p_below_floor |
| KXBTC15M-26MAY062315-15 | True | settled | -50848.173032 | no | rejected_actionable | 0.744580 | 0.794580 | 0.680000 | 0.064580 | True | 60.000000 | -0.023042 | -0.064993 | p_below_floor |
| KXBTC15M-26MAY062330-30 | True | settled | -49948.173032 | yes | rejected_actionable | 0.546903 | 0.596903 | 0.520000 | 0.026903 | False | -108.000000 | 0.057190 | 0.116929 | p_below_floor |
| KXBTC15M-26MAY062345-45 | True | settled | -49048.173032 | no | rejected_actionable | 0.608623 | 0.658623 | 0.460000 | 0.148623 | False | -96.000000 | 0.063362 | 0.136684 | p_below_floor |
| KXBTC15M-26MAY070000-00 | True | settled | -48148.173032 | no | approved_entry | 0.863962 | 0.913962 | 0.780000 | 0.083962 | True | 0.000000 | -0.011104 | -0.056260 | p_below_floor |
| KXBTC15M-26MAY070015-15 | True | settled | -47248.173032 | yes | rejected_actionable | 0.560075 | 0.610075 | 0.560000 | 0.000075 | True | 84.000000 | -0.041493 | -0.085511 | p_below_floor |
| KXBTC15M-26MAY070030-30 | True | settled | -46348.173032 | no | rejected_actionable | 0.523605 | 0.573605 | 0.330000 | 0.193605 | False | -70.000000 | 0.054861 | 0.110881 | p_below_floor |
| KXBTC15M-26MAY070045-45 | True | settled | -45448.173032 | no | rejected_actionable | 0.582164 | 0.632164 | 0.480000 | 0.102164 | True | 100.000000 | -0.039284 | -0.082397 | p_below_floor |
| KXBTC15M-26MAY070100-00 | True | settled | -44548.173032 | no | rejected_actionable | 0.505013 | 0.555013 | 0.220000 | 0.285013 | False | -47.000000 | 0.053001 | 0.106486 | p_below_floor |
| KXBTC15M-26MAY070115-15 | True | settled | -43648.173032 | yes | rejected_actionable | 0.773654 | 0.823654 | 0.720000 | 0.053654 | True | 53.000000 | -0.020135 | -0.062626 | p_below_floor |
| KXBTC15M-26MAY070130-30 | True | settled | -42748.173032 | no | rejected_actionable | 0.604140 | 0.654140 | 0.590000 | 0.014140 | True | 78.000000 | -0.037086 | -0.079515 | p_below_floor |
| KXBTC15M-26MAY070145-45 | True | settled | -41848.173032 | no | rejected_actionable | 0.838040 | 0.888040 | 0.810000 | 0.028040 | True | 35.000000 | -0.013696 | -0.057951 | p_below_floor |
| KXBTC15M-26MAY070200-00 | True | settled | -40948.173032 | yes | rejected_actionable | 0.505710 | 0.555710 | 0.300000 | 0.205710 | False | -63.000000 | 0.053071 | 0.106645 | p_below_floor |
| KXBTC15M-26MAY070530-30 | True | settled | -28348.173032 | no | rejected_actionable | 0.540822 | 0.590822 | 0.480000 | 0.060822 | True | 100.000000 | -0.043418 | -0.088425 | p_below_floor |
| KXBTC15M-26MAY070545-45 | True | settled | -27448.173032 | yes | rejected_actionable | 0.707647 | 0.757647 | 0.600000 | 0.107647 | False | -124.000000 | 0.073265 | 0.187567 | p_below_floor |
| KXBTC15M-26MAY070600-00 | True | settled | -26548.173032 | yes | rejected_actionable | 0.723960 | 0.773960 | 0.670000 | 0.053960 | True | 62.000000 | -0.025104 | -0.066784 | p_below_floor |
| KXBTC15M-26MAY070615-15 | True | settled | -25648.173032 | no | rejected_actionable | 0.610872 | 0.660872 | 0.280000 | 0.330872 | True | 141.000000 | -0.036413 | -0.078673 | p_below_floor |
| KXBTC15M-26MAY070630-30 | True | settled | -24748.173032 | yes | rejected_actionable | 0.606974 | 0.656974 | 0.470000 | 0.136974 | False | -98.000000 | 0.063197 | 0.136070 | p_below_floor |
| KXBTC15M-26MAY070645-45 | True | settled | -23848.173032 | yes | approved_entry | 0.895399 | 0.945399 | 0.810000 | 0.085399 | True | 35.000000 | -0.007960 | -0.054338 | p_below_floor |
| KXBTC15M-26MAY070700-00 | True | settled | -22948.173032 | yes | rejected_actionable | 0.654812 | 0.704812 | 0.560000 | 0.094812 | False | -116.000000 | 0.067981 | 0.156477 | p_below_floor |
| KXBTC15M-26MAY070715-15 | True | settled | -22048.173032 | yes | rejected_actionable | 0.560435 | 0.610435 | 0.510000 | 0.050435 | True | 94.000000 | -0.041457 | -0.085459 | p_below_floor |
| KXBTC15M-26MAY070730-30 | True | settled | -21148.173032 | yes | rejected_actionable | 0.530778 | 0.580778 | 0.460000 | 0.070778 | False | -96.000000 | 0.055578 | 0.112675 | p_below_floor |
| KXBTC15M-26MAY070745-45 | True | settled | -20248.173032 | yes | approved_entry | 0.903807 | 0.953807 | 0.680000 | 0.223807 | True | 32.000000 | -0.007119 | -0.053846 | p_below_floor |
| KXBTC15M-26MAY070800-00 | True | settled | -19348.173032 | yes | rejected_actionable | 0.536385 | 0.586385 | 0.450000 | 0.086385 | False | -94.000000 | 0.056139 | 0.114119 | p_below_floor |
| KXBTC15M-26MAY070815-15 | True | settled | -18448.173032 | yes | rejected_actionable | 0.501147 | 0.551147 | 0.440000 | 0.061147 | True | 108.000000 | -0.047385 | -0.095102 | p_below_floor |
| KXBTC15M-26MAY070830-30 | True | settled | -17548.173032 | yes | rejected_actionable | 0.514492 | 0.564492 | 0.410000 | 0.104492 | False | -86.000000 | 0.053949 | 0.108683 | p_below_floor |
| KXBTC15M-26MAY070845-45 | True | settled | -16648.173032 | yes | rejected_actionable | 0.596088 | 0.646088 | 0.450000 | 0.146088 | True | 106.000000 | -0.037891 | -0.080547 | p_below_floor |
| KXBTC15M-26MAY070900-00 | True | settled | -15748.173032 | yes | rejected_actionable | 0.597604 | 0.647604 | 0.550000 | 0.047604 | True | 86.000000 | -0.037740 | -0.080351 | p_below_floor |
| KXBTC15M-26MAY070915-15 | True | settled | -14848.173032 | no | rejected_actionable | 0.788001 | 0.838001 | 0.750000 | 0.038001 | True | 47.000000 | -0.018700 | -0.061520 | p_below_floor |
| KXBTC15M-26MAY070930-30 | True | settled | -13948.173032 | no | rejected_actionable | 0.511849 | 0.561849 | 0.480000 | 0.031849 | False | -100.000000 | 0.053685 | 0.108061 | p_below_floor |
| KXBTC15M-26MAY070945-45 | True | settled | -13048.173032 | no | rejected_actionable | 0.532085 | 0.582085 | 0.480000 | 0.052085 | True | 100.000000 | -0.044292 | -0.089813 | p_below_floor |
| KXBTC15M-26MAY071000-00 | True | settled | -12148.173032 | yes | rejected_actionable | 0.543510 | 0.593510 | 0.540000 | 0.003510 | False | -112.000000 | 0.056851 | 0.116007 | p_below_floor |
| KXBTC15M-26MAY071015-15 | True | settled | -11248.173032 | no | rejected_actionable | 0.609894 | 0.659894 | 0.600000 | 0.009894 | False | -124.000000 | 0.063489 | 0.137161 | p_below_floor |
| KXBTC15M-26MAY071030-30 | True | settled | -10348.173032 | no | rejected_actionable | 0.646380 | 0.696380 | 0.620000 | 0.026380 | True | 72.000000 | -0.032862 | -0.074508 | p_below_floor |
| KXBTC15M-26MAY071045-45 | True | settled | -9448.173032 | yes | rejected_actionable | 0.557862 | 0.607862 | 0.550000 | 0.007862 | False | -114.000000 | 0.058286 | 0.120008 | p_below_floor |
| KXBTC15M-26MAY071100-00 | True | settled | -8548.173032 | no | rejected_actionable | 0.578800 | 0.628800 | 0.560000 | 0.018800 | True | 84.000000 | -0.039620 | -0.082856 | p_below_floor |
| KXBTC15M-26MAY071115-15 | True | settled | -7648.173032 | no | rejected_actionable | 0.635838 | 0.685838 | 0.620000 | 0.015838 | False | -128.000000 | 0.066084 | 0.147690 | p_below_floor |
| KXBTC15M-26MAY071130-30 | True | settled | -6748.173032 | no | rejected_actionable | 0.582087 | 0.632087 | 0.580000 | 0.002087 | True | 80.000000 | -0.039291 | -0.082407 | p_below_floor |
| KXBTC15M-26MAY071145-45 | True | settled | -5848.173032 | yes | rejected_actionable | 0.645637 | 0.695637 | 0.610000 | 0.035637 | True | 74.000000 | -0.032936 | -0.074591 | p_below_floor |
| KXBTC15M-26MAY071200-00 | True | settled | -4948.173032 | yes | rejected_actionable | 0.606055 | 0.656055 | 0.600000 | 0.006055 | False | -124.000000 | 0.063106 | 0.135730 | p_below_floor |
| KXBTC15M-26MAY071215-15 | True | settled | -4048.173032 | yes | rejected_actionable | 0.509397 | 0.559397 | 0.470000 | 0.039397 | False | -98.000000 | 0.053440 | 0.107491 | p_below_floor |
| KXBTC15M-26MAY071230-30 | True | settled | -3148.173032 | no | rejected_actionable | 0.729882 | 0.779882 | 0.700000 | 0.029882 | False | -143.000000 | 0.075488 | 0.204695 | p_below_floor |
| KXBTC15M-26MAY071245-45 | True | settled | -2248.173032 | yes | rejected_actionable | 0.559979 | 0.609979 | 0.550000 | 0.009979 | False | -114.000000 | 0.058498 | 0.120622 | p_below_floor |
| KXBTC15M-26MAY071300-00 | True | settled | -1348.173032 | yes | rejected_actionable | 0.636040 | 0.686040 | 0.590000 | 0.046040 | False | -122.000000 | 0.066104 | 0.147778 | p_below_floor |
| KXBTC15M-26MAY071315-15 | True | settled | -448.173032 | yes | rejected_actionable | 0.533442 | 0.583442 | 0.510000 | 0.023442 | True | 94.000000 | -0.044156 | -0.089595 | p_below_floor |
| KXBTC15M-26MAY071330-30 | True | settled | 451.826968 | yes | rejected_actionable | 0.544206 | 0.594206 | 0.520000 | 0.024206 | False | -108.000000 | 0.056921 | 0.116195 | p_below_floor |
