# v28 Forward Physics Registry

Descriptive forward registry only. These tags are predeclared diagnostics, not tuned rules.

- Entries: `173`
- Settled entries: `173`
- Settled wins: `146`
- Exited/settled P&L: `$8.23`
- Hold-to-settlement P&L on comparable rows: `$23.04`
- Avg Brier on settled rows: `0.13363403471027746`

## Physics Tags

- `h1_feed_fresh`: count=169, settled=169, wins=143, gross=$8.03, avg_brier=0.13226788198471007
- `h2_thin_touch_depth`: count=22, settled=22, wins=19, gross=$1.56, avg_brier=0.11805903684272727
- `h2_crowded_depth`: count=17, settled=17, wins=14, gross=$-0.22, avg_brier=0.15364643729441174
- `h4_large_model_disagreement`: count=0, settled=0, wins=0, gross=$0.00, avg_brier=None
- `h4_old_model_opposes_side`: count=0, settled=0, wins=0, gross=$0.00, avg_brier=None
- `h5_late_high_sigma`: count=5, settled=5, wins=5, gross=$1.38, avg_brier=0.0132579419478
- `h6_recross_hazard_high`: count=86, settled=86, wins=71, gross=$4.59, avg_brier=0.14530119255818605

## Entries

| market | side | p_side | ask | edge | depth | recross | v28-v22 p | old best | flags | result | gross c |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---:|
| KXBTC15M-26MAY051300-00 | yes | 0.867375 | 81 | 2.23752 | 65.0 | 0.36657919808610573 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 36 |
| KXBTC15M-26MAY051330-30 | yes | 0.879391 | 82 | 2.439055 | 7.02 | 0.30242891547156237 | None |  | h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high | yes | 0 |
| KXBTC15M-26MAY051545-45 | yes | 0.851935 | 75 | 6.693536 | 318.78 | 0.38190335478068066 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 16 |
| KXBTC15M-26MAY051615-15 | no | 0.855253 | 76 | 6.02531 | 7.0 | 0.2723002958536802 | None |  | h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high | yes | -24 |
| KXBTC15M-26MAY051615-15 | yes | 0.92219 | 56 | 32.218966 | 718.38 | 0.1613755631733708 | None |  | h1_feed_fresh | yes | 32 |
| KXBTC15M-26MAY051715-15 | yes | 0.877551 | 82 | 2.255072 | 27.0 | 0.3259898292285944 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -28 |
| KXBTC15M-26MAY051715-15 | yes | 0.880552 | 69 | 15.555165 | 333.0 | 0.07487322238906284 | None |  | h1_feed_fresh | no | -48 |
| KXBTC15M-26MAY051715-15 | yes | 0.868759 | 40 | 42.87586 | 670.95 | 0.05680344649000784 | None |  | h1_feed_fresh | no | -22 |
| KXBTC15M-26MAY051745-45 | no | 0.861462 | 77 | 5.646183 | 167.26 | 0.3993723747635055 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -10 |
| KXBTC15M-26MAY051745-45 | no | 0.86177 | 80 | 2.676999 | 1763.3 | 0.3597654028345304 | None |  | h1_feed_fresh,h2_crowded_depth,h6_recross_hazard_high | no | -2 |
| KXBTC15M-26MAY051800-00 | yes | 0.85382 | 78 | 3.882043 | 326.6 | 0.3496464060083165 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | -24 |
| KXBTC15M-26MAY051800-00 | yes | 0.858155 | 80 | 2.315549 | 611.66 | 0.28302462076710433 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 40 |
| KXBTC15M-26MAY051815-15 | yes | 0.865481 | 81 | 2.048056 | 93.0 | 0.3479522342160163 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 24 |
| KXBTC15M-26MAY051830-30 | no | 0.865344 | 80 | 3.034397 | 82.79 | 0.18481237302914516 | None |  | h1_feed_fresh | yes | -92 |
| KXBTC15M-26MAY051845-45 | no | 0.864024 | 79 | 3.902414 | 97.0 | 0.4162522477382457 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 42 |
| KXBTC15M-26MAY051900-00 | yes | 0.876273 | 80 | 4.127337 | 254.05 | 0.3021213220864653 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 40 |
| KXBTC15M-26MAY051915-15 | yes | 0.880213 | 82 | 2.521344 | 119.82 | 0.15500111387451665 | None |  | h1_feed_fresh | yes | 34 |
| KXBTC15M-26MAY051945-45 | yes | 0.870179 | 74 | 9.517919 | 516.02 | 0.060671416989530894 | None |  | h1_feed_fresh | yes | 26 |
| KXBTC15M-26MAY052015-15 | yes | 0.91064 | 85 | 3.064008 | 27.53 | 0.28190119029157684 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 30 |
| KXBTC15M-26MAY052045-45 | yes | 0.851889 | 79 | 2.688928 | 40.0 | 0.2917497589224879 | None |  | h6_recross_hazard_high | no | -18 |
| KXBTC15M-26MAY052045-45 | yes | 0.904488 | 83 | 4.448812 | 1104.3 | 0.06396205708883733 | None |  | h1_feed_fresh | no | 14 |
| KXBTC15M-26MAY052100-00 | no | 0.852877 | 79 | 2.787743 | 110.0 | 0.3666540312599931 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | -30 |
| KXBTC15M-26MAY052100-00 | yes | 0.856314 | 56 | 25.631386 | 10.0 | 0.2414159418683516 | None |  | h1_feed_fresh,h2_thin_touch_depth | yes | 34 |
| KXBTC15M-26MAY052100-00 | yes | 0.951629 | 90 | 2.162887 | 51.18 | 0.0981953245588825 | None |  | h1_feed_fresh | yes | 12 |
| KXBTC15M-26MAY052115-15 | yes | 0.941543 | 78 | 12.654292 | 46.0 | 0.21507757842206168 | None |  | h1_feed_fresh | yes | 44 |
| KXBTC15M-26MAY052145-45 | yes | 0.93473 | 85 | 5.473022 | 2150.71 | 0.20704926938576498 | None |  | h1_feed_fresh,h2_crowded_depth | yes | 20 |
| KXBTC15M-26MAY052200-00 | yes | 0.850777 | 79 | 2.577696 | 58.0 | 0.40434357182519426 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 12 |
| KXBTC15M-26MAY052215-15 | no | 0.881293 | 83 | 2.129313 | 40.0 | 0.42803907980422096 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -14 |
| KXBTC15M-26MAY052245-45 | no | 0.916618 | 40 | 47.661822 | 40.0 | 0.14133142354912012 | None |  | h1_feed_fresh | yes | -26 |
| KXBTC15M-26MAY052300-00 | yes | 0.918967 | 85 | 3.896671 | 90.0 | 0.17919533255862446 | None |  | h1_feed_fresh | yes | 28 |
| KXBTC15M-26MAY052315-15 | yes | 0.884999 | 81 | 3.999851 | 41.68 | 0.21482441758698537 | None |  | h1_feed_fresh | yes | -38 |
| KXBTC15M-26MAY060045-45 | no | 0.85093 | 79 | 2.593011 | 131.0 | 0.28470197519819407 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -10 |
| KXBTC15M-26MAY060045-45 | no | 0.91131 | 85 | 3.130953 | 9.0 | 0.12048968703951406 | None |  | h1_feed_fresh,h2_thin_touch_depth | no | 20 |
| KXBTC15M-26MAY060100-00 | no | 0.867914 | 78 | 5.29135 | 95.03 | 0.23029818959354578 | None |  | h1_feed_fresh | no | -4 |
| KXBTC15M-26MAY060145-45 | no | 0.935752 | 88 | 2.575198 | 1100.0 | 0.17814503082894895 | None |  | h1_feed_fresh | no | 22 |
| KXBTC15M-26MAY060200-00 | yes | 0.858683 | 80 | 2.368332 | 50.0 | 0.3497083999828257 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | -12 |
| KXBTC15M-26MAY060200-00 | yes | 0.874865 | 81 | 2.986534 | 132.92 | 0.29306662969753194 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 6 |
| KXBTC15M-26MAY060215-15 | yes | 0.869074 | 77 | 6.407435 | 8.0 | 0.3639664202953999 | None |  | h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high | no | -16 |
| KXBTC15M-26MAY060215-15 | yes | 0.881378 | 83 | 2.137791 | 1110.0 | 0.23953217885049563 | None |  | h1_feed_fresh | no | -26 |
| KXBTC15M-26MAY060215-15 | no | 0.862656 | 80 | 2.765568 | 15.0 | 0.13314483275771213 | None |  | h1_feed_fresh,h2_thin_touch_depth | no | 34 |
| KXBTC15M-26MAY060230-30 | yes | 0.890973 | 84 | 2.097279 | 50.0 | 0.1236428180917944 | None |  | h1_feed_fresh | yes | -20 |
| KXBTC15M-26MAY060245-45 | yes | 0.857529 | 80 | 2.252876 | 40.0 | 0.2050981102340683 | None |  | h1_feed_fresh | yes | -8 |
| KXBTC15M-26MAY060245-45 | yes | 0.862971 | 77 | 5.797133 | 39.0 | 0.07879689391159121 | None |  | h1_feed_fresh | yes | -6 |
| KXBTC15M-26MAY060245-45 | yes | 0.877828 | 76 | 8.282842 | 151.68 | 0.05867289889682264 | None |  | h1_feed_fresh | yes | 38 |
| KXBTC15M-26MAY060300-00 | yes | 0.866164 | 81 | 2.116434 | 40.0 | 0.28943265545756386 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | -14 |
| KXBTC15M-26MAY060300-00 | yes | 0.86587 | 81 | 2.08696 | 10.49 | 0.15716255412753313 | None |  | h1_feed_fresh,h2_thin_touch_depth | yes | -30 |
| KXBTC15M-26MAY060300-00 | yes | 0.906682 | 80 | 7.168219 | 40.0 | 0.09600737655651764 | None |  | h1_feed_fresh | yes | -22 |
| KXBTC15M-26MAY060300-00 | yes | 0.855141 | 80 | 2.014147 | 60.0 | 0.09007340966375871 | None |  | h1_feed_fresh | yes | 28 |
| KXBTC15M-26MAY060315-15 | yes | 0.910009 | 86 | 2.000939 | 4.0 | 0.12454022861601939 | None |  | h1_feed_fresh,h2_thin_touch_depth | yes | 26 |
| KXBTC15M-26MAY060330-30 | yes | 0.908265 | 79 | 8.32655 | 2212.09 | 0.14812412666257624 | None |  | h1_feed_fresh,h2_crowded_depth | yes | -52 |
| KXBTC15M-26MAY060330-30 | no | 0.999788 | 9 | 87.978808 | 689.46 | 0.002807203427908955 | None |  | h1_feed_fresh | yes | -18 |
| KXBTC15M-26MAY060345-45 | no | 0.893931 | 78 | 7.893144 | 62.32 | 0.2784612767640184 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 34 |
| KXBTC15M-26MAY060445-45 | yes | 0.951245 | 90 | 2.124484 | 684.42 | 0.18476769845807034 | None |  | h1_feed_fresh | yes | 18 |
| KXBTC15M-26MAY060500-00 | yes | 0.904525 | 79 | 7.952498 | 360.0 | 0.22428736467274224 | None |  | h1_feed_fresh | yes | 42 |
| KXBTC15M-26MAY060515-15 | no | 0.882737 | 79 | 5.773652 | 83.0 | 0.3950550396110429 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -26 |
| KXBTC15M-26MAY060515-15 | no | 0.88418 | 74 | 10.918048 | 60.0 | 0.12327156428832237 | None |  | h1_feed_fresh | no | 42 |
| KXBTC15M-26MAY060530-30 | no | 0.878245 | 78 | 6.324454 | 405.73 | 0.2532924795100611 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 34 |
| KXBTC15M-26MAY060545-45 | yes | 0.960233 | 90 | 3.023343 | 65.0 | 0.2004492371382108 | None |  | h1_feed_fresh | yes | 20 |
| KXBTC15M-26MAY060600-00 | no | 0.870169 | 75 | 8.516936 | 2050.0 | 0.41552602726017807 | None |  | h1_feed_fresh,h2_crowded_depth,h6_recross_hazard_high | no | 12 |
| KXBTC15M-26MAY060615-15 | yes | 0.85204 | 75 | 6.704033 | 1003.0 | 0.3283327949656283 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | -30 |
| KXBTC15M-26MAY060615-15 | yes | 0.930577 | 88 | 2.057694 | 52.46 | 0.1028785918435462 | None |  | h1_feed_fresh | yes | 24 |
| KXBTC15M-26MAY060630-30 | yes | 0.852499 | 79 | 2.749855 | 9.0 | 0.2720718279701733 | None |  | h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high | yes | -12 |
| KXBTC15M-26MAY060630-30 | yes | 0.902826 | 85 | 2.282605 | 92.23 | 0.14341887790493552 | None |  | h1_feed_fresh | yes | 28 |
| KXBTC15M-26MAY060645-45 | yes | 0.875253 | 82 | 2.025331 | 384.0 | 0.30529976479941184 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | -16 |
| KXBTC15M-26MAY060645-45 | yes | 0.868675 | 78 | 5.367466 | 99.49 | 0.3016711464084146 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | -12 |
| KXBTC15M-26MAY060645-45 | yes | 0.859632 | 80 | 2.463183 | 64.0 | 0.24236576973562732 | None |  | h1_feed_fresh | yes | 34 |
| KXBTC15M-26MAY060700-00 | no | 0.890574 | 84 | 2.05744 | 2717.89 | 0.2857440916011646 | None |  | h1_feed_fresh,h2_crowded_depth,h6_recross_hazard_high | yes | -8 |
| KXBTC15M-26MAY060700-00 | yes | 0.852084 | 75 | 6.708443 | 145.34 | 0.19204408883172794 | None |  | h1_feed_fresh | yes | -22 |
| KXBTC15M-26MAY060700-00 | yes | 0.854571 | 77 | 4.957055 | 60.0 | 0.15091520720134025 | None |  | h1_feed_fresh | yes | -30 |
| KXBTC15M-26MAY060700-00 | yes | 0.880608 | 83 | 2.060833 | 104.88 | 0.08149612540552126 | None |  | h1_feed_fresh,h5_late_high_sigma | yes | 12 |
| KXBTC15M-26MAY060715-15 | yes | 0.872115 | 81 | 2.711512 | 154.34 | 0.33327148213923247 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 24 |
| KXBTC15M-26MAY060715-15 | yes | 0.947668 | 89 | 2.766793 | 165.0 | 0.18857738603460397 | None |  | h1_feed_fresh | yes | 20 |
| KXBTC15M-26MAY060730-30 | yes | 0.899565 | 84 | 2.95653 | 50.0 | 0.3347696641718883 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 32 |
| KXBTC15M-26MAY060745-45 | yes | 0.851843 | 69 | 12.684309 | 578.57 | 0.3032242515016857 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -24 |
| KXBTC15M-26MAY060745-45 | yes | 0.850438 | 78 | 3.543807 | 52.0 | 0.17312459053557222 | None |  | h1_feed_fresh | no | -70 |
| KXBTC15M-26MAY060800-00 | yes | 0.85 | 79 | 2.500023 | 99.39 | 0.1698860167511377 | None |  | h1_feed_fresh | yes | -18 |
| KXBTC15M-26MAY060800-00 | yes | 0.874265 | 66 | 17.426542 | 386.27 | 0.13037654446491642 | None |  | h1_feed_fresh | yes | -32 |
| KXBTC15M-26MAY060815-15 | no | 0.860153 | 79 | 3.515349 | 204.67 | 0.39502393499448535 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 42 |
| KXBTC15M-26MAY060830-30 | yes | 0.873796 | 76 | 7.879562 | 967.0 | 0.3071369986810028 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 48 |
| KXBTC15M-26MAY060900-00 | yes | 0.856054 | 78 | 4.105411 | 500.0 | 0.42347442313737094 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -10 |
| KXBTC15M-26MAY060900-00 | yes | 0.851503 | 78 | 3.650336 | 32.77 | 0.26705469444086044 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -76 |
| KXBTC15M-26MAY060900-00 | no | 0.855256 | 73 | 9.025574 | 1100.9 | 0.1456127710368916 | None |  | h1_feed_fresh | no | -16 |
| KXBTC15M-26MAY060900-00 | no | 0.853869 | 79 | 2.886882 | 55.0 | 0.11042228288847712 | None |  | h1_feed_fresh,h5_late_high_sigma | no | 34 |
| KXBTC15M-26MAY060915-15 | no | 0.850409 | 70 | 11.540902 | 4953.55 | 0.5084126970275672 | None |  | h1_feed_fresh,h2_crowded_depth,h6_recross_hazard_high | no | 0 |
| KXBTC15M-26MAY060915-15 | no | 0.850534 | 75 | 6.553378 | 85.0 | 0.39483162919703507 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 50 |
| KXBTC15M-26MAY060930-30 | no | 0.866835 | 76 | 7.183483 | 227.0 | 0.41510300263167554 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -20 |
| KXBTC15M-26MAY060930-30 | no | 0.857875 | 76 | 6.287483 | 655.0 | 0.38059617369193155 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -14 |
| KXBTC15M-26MAY060930-30 | no | 0.851733 | 73 | 8.673278 | 179.0 | 0.35378003234582406 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -3 |
| KXBTC15M-26MAY060930-30 | no | 0.852543 | 77 | 4.754265 | 160.0 | 0.3078986934577516 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 46 |
| KXBTC15M-26MAY060945-45 | no | 0.854149 | 59 | 22.414906 | 8757.49 | 0.5882306018534502 | None |  | h1_feed_fresh,h2_crowded_depth,h6_recross_hazard_high | no | -16 |
| KXBTC15M-26MAY060945-45 | no | 0.850231 | 70 | 11.523092 | 9543.6 | 0.33255592758743224 | None |  | h1_feed_fresh,h2_crowded_depth,h6_recross_hazard_high | no | -16 |
| KXBTC15M-26MAY060945-45 | no | 0.861162 | 71 | 11.616192 | 2.0 | 0.22595024441507225 | None |  | h1_feed_fresh,h2_thin_touch_depth | no | -12 |
| KXBTC15M-26MAY060945-45 | no | 0.852929 | 72 | 9.792897 | 121.03 | 0.1882466731492732 | None |  | h1_feed_fresh | no | 48 |
| KXBTC15M-26MAY061000-00 | no | 0.854748 | 65 | 16.474759 | 107.0 | 0.5866639910305327 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 70 |
| KXBTC15M-26MAY061015-15 | no | 0.859312 | 68 | 13.931175 | 269.86 | 0.5814886127535356 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -6 |
| KXBTC15M-26MAY061015-15 | no | 0.85586 | 70 | 12.085958 | 2075.04 | 0.5588405505167043 | None |  | h1_feed_fresh,h2_crowded_depth,h6_recross_hazard_high | no | 0 |
| KXBTC15M-26MAY061015-15 | no | 0.853364 | 73 | 8.83635 | 10.0 | 0.5053900102338842 | None |  | h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high | no | 54 |
| KXBTC15M-26MAY061030-30 | yes | 0.851204 | 78 | 3.620359 | 221.3 | 0.4119781212705184 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | -16 |
| KXBTC15M-26MAY061030-30 | yes | 0.850668 | 78 | 3.566818 | 295.0 | 0.3767253384297188 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | -10 |
| KXBTC15M-26MAY061030-30 | yes | 0.861605 | 74 | 8.660544 | 183.14 | 0.32474472240620245 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 52 |
| KXBTC15M-26MAY061045-45 | yes | 0.861569 | 80 | 2.656943 | 185.0 | 0.4088757000780344 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | -6 |
| KXBTC15M-26MAY061045-45 | yes | 0.896088 | 84 | 2.608755 | 20.81 | 0.0904738204447633 | None |  | h1_feed_fresh,h2_thin_touch_depth,h5_late_high_sigma | yes | 28 |
| KXBTC15M-26MAY061100-00 | no | 0.880408 | 83 | 2.040808 | 527.42 | 0.4421322714023326 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -40 |
| KXBTC15M-26MAY061100-00 | no | 0.868814 | 81 | 2.381373 | 55.0 | 0.331062545685405 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 38 |
| KXBTC15M-26MAY061130-30 | yes | 0.877418 | 80 | 4.241773 | 133.26 | 0.5363298971132572 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 40 |
| KXBTC15M-26MAY061200-00 | yes | 0.876246 | 82 | 2.124613 | 126.0 | 0.5526871033269218 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 16 |
| KXBTC15M-26MAY061300-00 | yes | 0.860906 | 80 | 2.590566 | 1412.0 | 0.30173010638435865 | None |  | h1_feed_fresh,h2_crowded_depth,h6_recross_hazard_high | no | -30 |
| KXBTC15M-26MAY061400-00 | no | 0.97364 | 89 | 5.364022 | 1564.77 | 0.05173622929495089 | None |  | h1_feed_fresh,h2_crowded_depth | no | -10 |
| KXBTC15M-26MAY061415-15 | no | 0.936538 | 88 | 2.653786 | 100.0 | 0.036021852060430126 | None |  | h1_feed_fresh | no | 24 |
| KXBTC15M-26MAY061445-45 | no | 0.931168 | 88 | 2.116797 | 55.0 | 0.30626002441386213 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -22 |
| KXBTC15M-26MAY061445-45 | no | 0.95423 | 90 | 2.42301 | 990.42 | 0.21306142679499787 | None |  | h1_feed_fresh | no | 18 |
| KXBTC15M-26MAY061545-45 | yes | 0.894983 | 84 | 2.498288 | 16.0 | 0.15655407010504802 | None |  | h1_feed_fresh,h2_thin_touch_depth | yes | 22 |
| KXBTC15M-26MAY061615-15 | yes | 0.957239 | 90 | 2.723898 | 435.42 | 0.16233734364968389 | None |  | h1_feed_fresh | yes | 8 |
| KXBTC15M-26MAY061645-45 | no | 0.855564 | 76 | 6.056402 | 27.93 | 0.41532436376612036 | None |  | h6_recross_hazard_high | no | 48 |
| KXBTC15M-26MAY061800-00 | no | 0.897587 | 67 | 18.758707 | 132.0 | 0.2551010740832833 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -86 |
| KXBTC15M-26MAY061815-15 | no | 0.948944 | 84 | 7.894387 | 60.0 | 0.14726933295332775 | None |  | h1_feed_fresh | no | 24 |
| KXBTC15M-26MAY061830-30 | no | 0.94737 | 89 | 2.737019 | 55.0 | 0.09386761131456846 | None |  | h1_feed_fresh | no | 20 |
| KXBTC15M-26MAY061900-00 | yes | 0.955382 | 90 | 2.5382 | 132.0 | 0.06948748597263207 | None |  | h1_feed_fresh | yes | 20 |
| KXBTC15M-26MAY061915-15 | no | 0.923342 | 87 | 2.334214 | 185.54 | 0.2295042151020138 | None |  | h1_feed_fresh | no | 24 |
| KXBTC15M-26MAY062015-15 | no | 0.871622 | 42 | 41.162189 | 108.0 | 0.09439569910943164 | None |  | h1_feed_fresh | no | -60 |
| KXBTC15M-26MAY062015-15 | yes | 0.934569 | 86 | 4.456922 | 1557.14 | 0.051560846761120625 | None |  | h1_feed_fresh,h2_crowded_depth | no | 8 |
| KXBTC15M-26MAY062015-15 | yes | 0.885657 | 67 | 17.565723 | 100.0 | 0.03209081623854011 | None |  | h1_feed_fresh | no | -134 |
| KXBTC15M-26MAY062030-30 | no | 0.874426 | 67 | 16.442646 | 192.08 | 0.223976175011057 | None |  | h1_feed_fresh | no | 32 |
| KXBTC15M-26MAY062045-45 | no | 0.925277 | 80 | 9.027718 | 182.48 | 0.18008324702870745 | None |  | h1_feed_fresh | no | 24 |
| KXBTC15M-26MAY062100-00 | yes | 0.909296 | 83 | 4.929645 | 1091.93 | 0.23636880575375532 | None |  | h1_feed_fresh | yes | -4 |
| KXBTC15M-26MAY062100-00 | yes | 0.908226 | 84 | 3.822597 | 65.0 | 0.2152024091712024 | None |  |  | yes | -20 |
| KXBTC15M-26MAY062100-00 | yes | 0.852359 | 61 | 20.235911 | 633.0 | 0.1975068124858315 | None |  | h1_feed_fresh | yes | 14 |
| KXBTC15M-26MAY062115-15 | yes | 0.942571 | 73 | 17.757121 | 1252.35 | 0.23905318791075164 | None |  | h1_feed_fresh | yes | -12 |
| KXBTC15M-26MAY062115-15 | no | 0.860865 | 69 | 13.586452 | 111.0 | 0.24724590482473205 | None |  | h1_feed_fresh | yes | -34 |
| KXBTC15M-26MAY062115-15 | yes | 0.993517 | 88 | 8.351657 | 50.0 | 0.01871038914515192 | None |  | h1_feed_fresh,h5_late_high_sigma | yes | 22 |
| KXBTC15M-26MAY062130-30 | no | 0.887777 | 76 | 9.277671 | 24.0 | 0.3038697963028121 | None |  | h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high | yes | -32 |
| KXBTC15M-26MAY062215-15 | no | 0.889241 | 65 | 19.92409 | 548.68 | 0.3195253376053145 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 14 |
| KXBTC15M-26MAY062215-15 | no | 0.897937 | 84 | 2.793675 | 625.0 | 0.22318437858918544 | None |  |  | no | 10 |
| KXBTC15M-26MAY062245-45 | yes | 0.949793 | 86 | 5.979256 | 2329.71 | 0.2143515250453267 | None |  | h1_feed_fresh,h2_crowded_depth | yes | 8 |
| KXBTC15M-26MAY062300-00 | yes | 0.923042 | 87 | 2.304222 | 1125.39 | 0.2978333379290589 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 16 |
| KXBTC15M-26MAY062315-15 | no | 0.91617 | 84 | 4.616959 | 54.0 | 0.19128692789448937 | None |  | h1_feed_fresh | no | 6 |
| KXBTC15M-26MAY070000-00 | no | 0.863962 | 78 | 4.896244 | 60.35 | 0.1931875391606329 | None |  | h1_feed_fresh | no | 2 |
| KXBTC15M-26MAY070015-15 | no | 0.963659 | 70 | 22.865923 | 522.86 | 0.07375286170271013 | None |  | h1_feed_fresh | yes | -2 |
| KXBTC15M-26MAY070030-30 | yes | 0.924288 | 82 | 6.928791 | 236.0 | 0.1751266718605662 | None |  | h1_feed_fresh | yes | 30 |
| KXBTC15M-26MAY070115-15 | yes | 0.879857 | 82 | 2.485652 | 55.0 | 0.3214091633389714 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 0 |
| KXBTC15M-26MAY070545-45 | no | 0.925171 | 82 | 7.017143 | 510.0 | 0.12492601757355813 | None |  | h1_feed_fresh | no | 18 |
| KXBTC15M-26MAY070645-45 | yes | 0.895399 | 81 | 5.039895 | 1405.25 | 0.36879792565874936 | None |  | h1_feed_fresh,h2_crowded_depth,h6_recross_hazard_high | yes | 38 |
| KXBTC15M-26MAY070745-45 | yes | 0.903807 | 68 | 18.380737 | 1155.7 | 0.1975936328082862 | None |  | h1_feed_fresh | yes | 34 |
| KXBTC15M-26MAY070815-15 | yes | 0.950799 | 90 | 2.079863 | 665.0 | 0.1855824939071499 | None |  | h1_feed_fresh | yes | 2 |
| KXBTC15M-26MAY070830-30 | no | 0.875926 | 82 | 2.09255 | 1230.2 | 0.2815228625858157 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 18 |
| KXBTC15M-26MAY070830-30 | no | 0.890215 | 77 | 8.52148 | 2840.98 | 0.12662156928196733 | None |  | h1_feed_fresh,h2_crowded_depth | no | -14 |
| KXBTC15M-26MAY070830-30 | no | 0.852625 | 77 | 4.762529 | 10.0 | 0.08780896924696753 | None |  | h1_feed_fresh,h2_thin_touch_depth | no | 46 |
| KXBTC15M-26MAY070915-15 | no | 0.876673 | 77 | 7.167327 | 10.0 | 0.28381172517459047 | None |  | h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high | no | 46 |
| KXBTC15M-26MAY070930-30 | yes | 0.855936 | 80 | 2.09357 | 146.03 | 0.37566863848192883 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 34 |
| KXBTC15M-26MAY070945-45 | no | 0.853699 | 69 | 12.869922 | 52.0 | 0.43642658262493145 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 62 |
| KXBTC15M-26MAY071000-00 | no | 0.861629 | 73 | 9.66294 | 8.79 | 0.48318335835479914 | None |  | h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high | no | -36 |
| KXBTC15M-26MAY071000-00 | no | 0.851825 | 71 | 10.682459 | 21.0 | 0.48411120022028664 | None |  | h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high | no | 16 |
| KXBTC15M-26MAY071015-15 | no | 0.861092 | 78 | 4.609185 | 29.38 | 0.41762272221317515 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 2 |
| KXBTC15M-26MAY071015-15 | no | 0.866013 | 81 | 2.101334 | 55.0 | 0.3809737029180094 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | -16 |
| KXBTC15M-26MAY071015-15 | yes | 0.909403 | 84 | 3.940302 | 106.46 | 0.13171334830670237 | None |  | h1_feed_fresh | yes | 20 |
| KXBTC15M-26MAY071030-30 | no | 0.852355 | 77 | 4.735533 | 300.0 | 0.5927426169341831 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -24 |
| KXBTC15M-26MAY071030-30 | no | 0.852278 | 76 | 5.727803 | 9662.42 | 0.572086869997676 | None |  | h1_feed_fresh,h2_crowded_depth,h6_recross_hazard_high | no | 48 |
| KXBTC15M-26MAY071045-45 | no | 0.856439 | 74 | 8.143857 | 225.99 | 0.5367354413690074 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | -10 |
| KXBTC15M-26MAY071045-45 | no | 0.86526 | 75 | 8.026019 | 50.0 | 0.4699176077596592 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 50 |
| KXBTC15M-26MAY071100-00 | yes | 0.884041 | 83 | 2.404098 | 110.0 | 0.30500573389101787 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 4 |
| KXBTC15M-26MAY071115-15 | yes | 0.891894 | 84 | 2.189408 | 1139.25 | 0.21995572150628764 | None |  | h1_feed_fresh | yes | 14 |
| KXBTC15M-26MAY071130-30 | no | 0.916601 | 85 | 3.660104 | 741.0 | 0.33188369997953837 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 30 |
| KXBTC15M-26MAY071145-45 | yes | 0.855371 | 77 | 5.037053 | 46.45 | 0.5850484031165768 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | 44 |
| KXBTC15M-26MAY071200-00 | no | 0.859141 | 77 | 5.414132 | 513.0 | 0.08952903130635531 | None |  | h1_feed_fresh,h5_late_high_sigma | no | 42 |
| KXBTC15M-26MAY071215-15 | no | 0.900118 | 84 | 3.011812 | 8.0 | 0.25314482933670285 | None |  | h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high | no | -16 |
| KXBTC15M-26MAY071215-15 | no | 0.850947 | 78 | 3.594658 | 476.47 | 0.2624012891254945 | None |  | h1_feed_fresh,h6_recross_hazard_high | no | 2 |
| KXBTC15M-26MAY071215-15 | no | 0.855912 | 80 | 2.091248 | 1329.71 | 0.23793016778534123 | None |  | h1_feed_fresh,h2_crowded_depth | no | -8 |
| KXBTC15M-26MAY071230-30 | yes | 0.852419 | 77 | 4.741888 | 20.0 | 0.2960374313658712 | None |  | h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high | yes | -10 |
| KXBTC15M-26MAY071230-30 | yes | 0.897482 | 84 | 2.748165 | 142.0 | 0.21651944452366917 | None |  | h1_feed_fresh | yes | -38 |
| KXBTC15M-26MAY071230-30 | yes | 0.857001 | 80 | 2.200119 | 150.0 | 0.2169488405391984 | None |  | h1_feed_fresh | yes | 40 |
| KXBTC15M-26MAY071315-15 | yes | 0.860278 | 80 | 2.527813 | 73.58 | 0.29994875175637187 | None |  | h1_feed_fresh,h6_recross_hazard_high | yes | -6 |
| KXBTC15M-26MAY071315-15 | yes | 0.865868 | 81 | 2.086807 | 20.0 | 0.14544955952771735 | None |  | h1_feed_fresh,h2_thin_touch_depth | yes | -14 |
| KXBTC15M-26MAY071315-15 | yes | 0.850827 | 78 | 3.582713 | 18.0 | 0.13242642354050885 | None |  | h1_feed_fresh,h2_thin_touch_depth | yes | 32 |
