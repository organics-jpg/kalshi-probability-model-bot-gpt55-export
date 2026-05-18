# v28 Policy Failure Modes

- Scope: causal policy selections from the latest entry bakeoff.
- Purpose: expose physical regimes that create losses or fragile wins without threshold hunting.

## Loss Rows

| policy | market | side | p | ask | edge c | abs d sigma | recross | stc | gross c | tags |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY060445-45 | no | 0.636374 | 45.0 | 14.637394 | 0.322198 | 0.6665690270808117 | 864.716 | -90 | early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY060500-00 | no | 0.674136 | 61.0 | 2.413631 | 0.377919 | 0.6203177051235377 | 783.254 | -122 | early_market_long_horizon,high_confidence_side |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY060515-15 | yes | 0.532512 | 41.0 | 8.251221 | 0.1415 | 0.9586252411430818 | 825.119 | -82 | near_coinflip_model,high_recross_hazard,near_strike_low_sigma_distance,early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY060530-30 | yes | 0.590382 | 43.0 | 12.03821 | 0.222165 | 0.7235308647918584 | 693.336 | -86 | near_strike_low_sigma_distance |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY060545-45 | no | 0.626642 | 44.0 | 14.664224 | 0.323422 | 0.6890532658346525 | 807.56 | -88 | early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY060700-00 | no | 0.860281 | 81.0 | 1.528096 | 0.898159 | 0.3342858192462624 | 633.193 | -162 | high_confidence_side |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY060745-45 | yes | 0.62726 | 53.0 | 5.725985 | 0.322555 | 0.6887963067510932 | 626.004 | -106 | untagged |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY060830-30 | no | 0.702743 | 65.0 | 1.274326 | 0.519063 | 0.7304579111697096 | 864.233 | -130 | early_market_long_horizon,high_confidence_side |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY060900-00 | yes | 0.856054 | 78.0 | 4.105411 | 0.872054 | 0.42347442313737094 | 743.816 | -10 | early_market_long_horizon,high_confidence_side |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY061100-00 | yes | 0.767873 | 70.0 | 3.287312 | 0.662662 | 0.749369537618552 | 845.343 | -140 | early_market_long_horizon,high_confidence_side |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY061115-15 | yes | 0.565523 | 49.0 | 3.552327 | 0.134127 | 0.536458603321024 | 355.876 | -98 | near_coinflip_model,near_strike_low_sigma_distance |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY061245-45 | no | 0.740496 | 69.0 | 1.549568 | 0.583513 | 0.6715565348717097 | 738.97 | -138 | early_market_long_horizon,high_confidence_side |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY061700-00 | no | 0.547299 | 49.0 | 1.729939 | 0.145303 | 0.7999159734871153 | 759.628 | -98 | near_coinflip_model,high_recross_hazard,near_strike_low_sigma_distance,early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY061715-15 | yes | 0.633073 | 50.0 | 9.307271 | 0.324075 | 0.6830949302308119 | 804.817 | -100 | early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY061745-45 | no | 0.510383 | 14.0 | 34.038275 | 0.021042 | 0.6897895866379721 | 668.465 | -28 | near_coinflip_model,near_strike_low_sigma_distance |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY061830-30 | yes | 0.553162 | 23.0 | 28.816194 | 0.098877 | 0.6315757792925781 | 653.539 | -46 | near_coinflip_model,near_strike_low_sigma_distance |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY061945-45 | yes | 0.542407 | 42.0 | 8.240693 | 0.13265 | 0.8012564138437247 | 809.092 | -84 | near_coinflip_model,high_recross_hazard,near_strike_low_sigma_distance,early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY062015-15 | yes | 0.614301 | 54.0 | 3.430147 | 0.29011 | 0.5841335298890138 | 844.672 | -108 | early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY062030-30 | yes | 0.544418 | 32.0 | 18.44184 | 0.107412 | 0.6807697699219372 | 804.712 | -64 | near_coinflip_model,near_strike_low_sigma_distance,early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY062100-00 | no | 0.615588 | 22.0 | 36.05876 | 0.321159 | 0.5154674438225817 | 683.547 | -44 | untagged |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY062230-30 | yes | 0.718015 | 38.0 | 29.801453 | 0.481781 | 0.34967152719409217 | 460.951 | -76 | high_confidence_side |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY062245-45 | no | 0.605951 | 54.0 | 2.595082 | 0.278629 | 0.7865843246178028 | 841.408 | -108 | high_recross_hazard,early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY062330-30 | yes | 0.554636 | 4.0 | 48.963649 | 0.121467 | 0.30748388986008607 | 281.559 | -8 | near_coinflip_model,near_strike_low_sigma_distance |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY062345-45 | no | 0.608623 | 46.0 | 10.862287 | 0.276153 | 0.6753249635352406 | 723.265 | -92 | early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070030-30 | no | 0.523605 | 33.0 | 15.360541 | 0.059362 | 0.9016513046480161 | 770.113 | -66 | near_coinflip_model,high_recross_hazard,near_strike_low_sigma_distance,early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070100-00 | no | 0.505013 | 22.0 | 25.001343 | 0.032616 | 0.647900380591622 | 543.305 | -44 | near_coinflip_model,near_strike_low_sigma_distance |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070200-00 | yes | 0.50571 | 30.0 | 17.071017 | 0.019784 | 0.6024318401067633 | 532.791 | -60 | near_coinflip_model,near_strike_low_sigma_distance |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070545-45 | yes | 0.707647 | 60.0 | 6.764695 | 0.46275 | 0.6220148866755595 | 855.69 | -120 | early_market_long_horizon,high_confidence_side |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070630-30 | yes | 0.606974 | 47.0 | 9.697411 | 0.230767 | 0.8264694476309769 | 875.963 | -94 | high_recross_hazard,near_strike_low_sigma_distance,early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070700-00 | yes | 0.654812 | 56.0 | 5.481241 | 0.375634 | 0.7601242607081649 | 869.636 | -112 | high_recross_hazard,early_market_long_horizon,high_confidence_side |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070730-30 | yes | 0.530778 | 46.0 | 3.077802 | 0.091964 | 0.9361206885177036 | 819.643 | -92 | near_coinflip_model,high_recross_hazard,near_strike_low_sigma_distance,early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070800-00 | yes | 0.536385 | 45.0 | 4.638461 | 0.080069 | 0.8654745987079465 | 771.226 | -90 | near_coinflip_model,high_recross_hazard,near_strike_low_sigma_distance,early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070830-30 | yes | 0.514492 | 41.0 | 6.449161 | 0.078942 | 0.9527908104356088 | 811.825 | -82 | near_coinflip_model,high_recross_hazard,near_strike_low_sigma_distance,early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070900-00 | no | 0.606083 | 52.0 | 4.608252 | 0.253011 | 0.7010000307286993 | 713.192 | -104 | untagged |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071015-15 | no | 0.861092 | 78.0 | 4.609185 | 0.936079 | 0.41762272221317515 | 583.765 | 2 | high_confidence_side |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071100-00 | yes | 0.884041 | 83.0 | 2.404098 | 1.010241 | 0.30500573389101787 | 498.551 | 4 | high_confidence_side |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071200-00 | yes | 0.588818 | 53.0 | 1.881758 | 0.195956 | 0.2279178112729362 | 165.619 | -106 | near_strike_low_sigma_distance,late_market_short_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071215-15 | yes | 0.530384 | 47.0 | 2.038384 | 0.026648 | 1.2451451719991744 | 782.308 | -94 | near_coinflip_model,high_recross_hazard,near_strike_low_sigma_distance,early_market_long_horizon |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071245-45 | yes | 0.6248 | 56.0 | 2.479997 | 0.321099 | 0.8824764177724596 | 718.733 | -112 | high_recross_hazard |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071300-00 | yes | 0.502685 | 43.0 | 3.268521 | 0.012349 | 0.5360356020400235 | 366.622 | -86 | near_coinflip_model,near_strike_low_sigma_distance |

## Tag Summaries

### baseline_v28_approved

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| high_confidence_side | 107 | 107 | 91 | 16 | 494.0 | 4.616822429906542 |
| early_market_long_horizon | 27 | 27 | 24 | 3 | 310.0 | 11.481481481481481 |
| thin_touch_depth | 7 | 7 | 5 | 2 | -78.0 | -11.142857142857142 |
| late_market_short_horizon | 3 | 3 | 3 | 0 | 92.0 | 30.666666666666668 |

### book_plus_02_avoid_coinflip

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| early_market_long_horizon | 115 | 115 | 66 | 49 | 685.0 | 5.956521739130435 |
| cheap_low_p_side | 50 | 50 | 13 | 37 | -260.0 | -5.2 |
| negative_net_edge | 62 | 62 | 35 | 27 | 173.0 | 2.7903225806451615 |
| high_confidence_side | 72 | 72 | 47 | 25 | -700.0 | -9.722222222222221 |
| high_recross_hazard | 59 | 59 | 34 | 25 | 873.0 | 14.796610169491526 |
| cheap_yes_boundary_pull | 28 | 28 | 8 | 20 | -56.0 | -2.0 |
| near_strike_low_sigma_distance | 37 | 37 | 19 | 18 | 385.0 | 10.405405405405405 |
| thin_touch_depth | 8 | 8 | 5 | 3 | -115.0 | -14.375 |
| late_market_short_horizon | 1 | 1 | 0 | 1 | -4.0 | -4.0 |
| untagged | 4 | 4 | 3 | 1 | 234.0 | 58.5 |

### book_plus_02_avoid_coinflip_liquid

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| early_market_long_horizon | 115 | 115 | 66 | 49 | 696.0 | 6.052173913043478 |
| cheap_low_p_side | 50 | 50 | 13 | 37 | -260.0 | -5.2 |
| negative_net_edge | 60 | 60 | 33 | 27 | 112.0 | 1.8666666666666667 |
| high_confidence_side | 73 | 73 | 48 | 25 | -686.0 | -9.397260273972602 |
| high_recross_hazard | 58 | 58 | 33 | 25 | 830.0 | 14.310344827586206 |
| cheap_yes_boundary_pull | 28 | 28 | 8 | 20 | -56.0 | -2.0 |
| near_strike_low_sigma_distance | 36 | 36 | 18 | 18 | 342.0 | 9.5 |
| thin_touch_depth | 6 | 6 | 3 | 3 | -176.0 | -29.333333333333332 |
| late_market_short_horizon | 1 | 1 | 0 | 1 | -4.0 | -4.0 |
| untagged | 4 | 4 | 3 | 1 | 234.0 | 58.5 |

### book_plus_03

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| early_market_long_horizon | 134 | 134 | 66 | 68 | -174.0 | -1.2985074626865671 |
| near_strike_low_sigma_distance | 93 | 93 | 38 | 55 | -272.0 | -2.924731182795699 |
| high_recross_hazard | 98 | 98 | 45 | 53 | -10.0 | -0.10204081632653061 |
| near_coinflip_model | 72 | 72 | 28 | 44 | -362.0 | -5.027777777777778 |
| cheap_low_p_side | 28 | 28 | 6 | 22 | -423.0 | -15.107142857142858 |
| negative_net_edge | 38 | 38 | 18 | 20 | -406.0 | -10.68421052631579 |
| cheap_yes_boundary_pull | 12 | 12 | 3 | 9 | -194.0 | -16.166666666666668 |
| high_confidence_side | 45 | 45 | 37 | 8 | 586.0 | 13.022222222222222 |
| thin_touch_depth | 5 | 5 | 3 | 2 | -35.0 | -7.0 |
| untagged | 2 | 2 | 2 | 0 | 232.0 | 116.0 |

### book_plus_03_avoid_coinflip

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| early_market_long_horizon | 98 | 98 | 55 | 43 | 32.0 | 0.32653061224489793 |
| cheap_low_p_side | 48 | 48 | 9 | 39 | -601.0 | -12.520833333333334 |
| high_confidence_side | 79 | 79 | 55 | 24 | -494.0 | -6.253164556962025 |
| high_recross_hazard | 45 | 45 | 25 | 20 | 492.0 | 10.933333333333334 |
| cheap_yes_boundary_pull | 23 | 23 | 5 | 18 | -310.0 | -13.478260869565217 |
| negative_net_edge | 32 | 32 | 18 | 14 | -196.0 | -6.125 |
| near_strike_low_sigma_distance | 30 | 30 | 16 | 14 | 510.0 | 17.0 |
| thin_touch_depth | 7 | 7 | 4 | 3 | -47.0 | -6.714285714285714 |
| late_market_short_horizon | 1 | 1 | 0 | 1 | -4.0 | -4.0 |
| untagged | 4 | 4 | 3 | 1 | 234.0 | 58.5 |

### book_plus_03_cheap_convex

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| cheap_low_p_side | 92 | 92 | 32 | 60 | 916.0 | 9.956521739130435 |
| cheap_yes_boundary_pull | 45 | 45 | 15 | 30 | 249.0 | 5.533333333333333 |
| near_strike_low_sigma_distance | 41 | 41 | 16 | 25 | 574.0 | 14.0 |
| early_market_long_horizon | 31 | 31 | 13 | 18 | 489.0 | 15.774193548387096 |
| near_coinflip_model | 27 | 27 | 13 | 14 | 850.0 | 31.48148148148148 |
| negative_net_edge | 16 | 16 | 6 | 10 | 51.0 | 3.1875 |
| high_recross_hazard | 20 | 20 | 10 | 10 | 606.0 | 30.3 |
| late_market_short_horizon | 4 | 4 | 1 | 3 | -12.0 | -3.0 |
| thin_touch_depth | 10 | 10 | 7 | 3 | 724.0 | 72.4 |

### book_plus_05

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| early_market_long_horizon | 98 | 98 | 50 | 48 | 372.0 | 3.795918367346939 |
| near_strike_low_sigma_distance | 72 | 72 | 30 | 42 | 368.0 | 5.111111111111111 |
| near_coinflip_model | 55 | 55 | 21 | 34 | -42.0 | -0.7636363636363637 |
| high_recross_hazard | 66 | 66 | 34 | 32 | 1034.0 | 15.666666666666666 |
| cheap_low_p_side | 23 | 23 | 4 | 19 | -430.0 | -18.695652173913043 |
| high_confidence_side | 64 | 64 | 50 | 14 | 536.0 | 8.375 |
| cheap_yes_boundary_pull | 8 | 8 | 0 | 8 | -408.0 | -51.0 |
| untagged | 6 | 6 | 3 | 3 | 66.0 | 11.0 |
| thin_touch_depth | 4 | 4 | 3 | 1 | 206.0 | 51.5 |

### book_plus_05_no_cheap_yes_boundary

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| early_market_long_horizon | 96 | 96 | 51 | 45 | 530.0 | 5.520833333333333 |
| near_strike_low_sigma_distance | 69 | 69 | 30 | 39 | 550.0 | 7.971014492753623 |
| near_coinflip_model | 55 | 55 | 21 | 34 | -42.0 | -0.7636363636363637 |
| high_recross_hazard | 65 | 65 | 34 | 31 | 1086.0 | 16.70769230769231 |
| high_confidence_side | 67 | 67 | 53 | 14 | 642.0 | 9.582089552238806 |
| cheap_low_p_side | 15 | 15 | 4 | 11 | -22.0 | -1.4666666666666666 |
| untagged | 6 | 6 | 3 | 3 | 66.0 | 11.0 |
| thin_touch_depth | 5 | 5 | 4 | 1 | 262.0 | 52.4 |

### p50_book_plus_05_edge_nonnegative

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| early_market_long_horizon | 77 | 77 | 46 | 31 | 446.0 | 5.792207792207792 |
| near_strike_low_sigma_distance | 49 | 49 | 24 | 25 | 652.0 | 13.306122448979592 |
| near_coinflip_model | 35 | 35 | 14 | 21 | -38.0 | -1.0857142857142856 |
| high_recross_hazard | 45 | 45 | 27 | 18 | 1064.0 | 23.644444444444446 |
| high_confidence_side | 80 | 80 | 63 | 17 | 626.0 | 7.825 |
| untagged | 7 | 7 | 4 | 3 | 174.0 | 24.857142857142858 |
| thin_touch_depth | 6 | 6 | 4 | 2 | 66.0 | 11.0 |
| late_market_short_horizon | 2 | 2 | 1 | 1 | -82.0 | -41.0 |

### p55_edge_nonnegative

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| high_confidence_side | 103 | 103 | 75 | 28 | -53.0 | -0.5145631067961165 |
| early_market_long_horizon | 78 | 78 | 51 | 27 | 442.0 | 5.666666666666667 |
| high_recross_hazard | 31 | 31 | 20 | 11 | 742.0 | 23.93548387096774 |
| near_strike_low_sigma_distance | 25 | 25 | 16 | 9 | 882.0 | 35.28 |
| near_coinflip_model | 11 | 11 | 6 | 5 | 250.0 | 22.727272727272727 |
| thin_touch_depth | 9 | 9 | 6 | 3 | -13.0 | -1.4444444444444444 |
| untagged | 6 | 6 | 4 | 2 | 272.0 | 45.333333333333336 |

### p65_book_plus_02

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| high_confidence_side | 152 | 152 | 101 | 51 | -1542.0 | -10.144736842105264 |
| early_market_long_horizon | 69 | 69 | 48 | 21 | -56.0 | -0.8115942028985508 |
| negative_net_edge | 44 | 44 | 28 | 16 | -840.0 | -19.09090909090909 |
| high_recross_hazard | 15 | 15 | 8 | 7 | -300.0 | -20.0 |
| thin_touch_depth | 8 | 8 | 7 | 1 | 162.0 | 20.25 |
| late_market_short_horizon | 1 | 1 | 1 | 0 | 42.0 | 42.0 |

### p65_book_plus_03

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| high_confidence_side | 145 | 145 | 97 | 48 | -1486.0 | -10.248275862068965 |
| early_market_long_horizon | 59 | 59 | 42 | 17 | 74.0 | 1.2542372881355932 |
| negative_net_edge | 20 | 20 | 13 | 7 | -314.0 | -15.7 |
| high_recross_hazard | 9 | 9 | 7 | 2 | 294.0 | 32.666666666666664 |
| thin_touch_depth | 8 | 8 | 7 | 1 | 286.0 | 35.75 |
| late_market_short_horizon | 1 | 1 | 1 | 0 | 42.0 | 42.0 |

### p65_large_disagreement_anchor_plus_02

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| high_confidence_side | 145 | 145 | 101 | 44 | -1198.0 | -8.26206896551724 |
| early_market_long_horizon | 66 | 66 | 47 | 19 | 20.0 | 0.30303030303030304 |
| negative_net_edge | 44 | 44 | 28 | 16 | -840.0 | -19.09090909090909 |
| high_recross_hazard | 14 | 14 | 8 | 6 | -226.0 | -16.142857142857142 |
| thin_touch_depth | 7 | 7 | 6 | 1 | 70.0 | 10.0 |
| late_market_short_horizon | 1 | 1 | 1 | 0 | 42.0 | 42.0 |

### p65_v28_premium_anchor_plus_02

| tag | entries | resolved | wins | losses | gross c | avg gross c |
|---|---:|---:|---:|---:|---:|---:|
| high_confidence_side | 144 | 144 | 100 | 44 | -1376.0 | -9.555555555555555 |
| early_market_long_horizon | 65 | 65 | 46 | 19 | -158.0 | -2.4307692307692306 |
| negative_net_edge | 44 | 44 | 28 | 16 | -840.0 | -19.09090909090909 |
| high_recross_hazard | 13 | 13 | 7 | 6 | -308.0 | -23.692307692307693 |
| thin_touch_depth | 7 | 7 | 6 | 1 | 70.0 | 10.0 |
| late_market_short_horizon | 1 | 1 | 1 | 0 | 42.0 | 42.0 |

