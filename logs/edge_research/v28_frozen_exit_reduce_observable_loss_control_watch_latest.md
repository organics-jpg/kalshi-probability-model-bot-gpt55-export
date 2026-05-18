# v28 Frozen Exit Reduce Observable Loss-Control Watch

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:44:54.196719+00:00`
- Freeze UTC: `2026-05-07T00:08:36.297681+00:00`

## Interpretation

- This is a forward-only observable loss-control watch; pre-birth rows are diagnostic and cannot promote any rule.
- diagnostic_from_reduce_freeze: best diagnostic_from_reduce_freeze_reduce_suppress_p75_exit_cents_lte_72 settled 132, delta 359.0c, suppressed 9, suppressed W/L 8/1, loss cost -120.0c, blockers ['suppressed_decisions_lt_30', 'suppressed_losers_present', 'suppressed_loss_control_cost_negative'].
- post_observable_birth: best post_observable_birth_reduce_suppress_p75_exit_cents_lte_72 settled 54, delta -58.0c, suppressed 2, suppressed W/L 1/1, loss cost -120.0c, blockers ['suppressed_decisions_lt_30', 'delta_not_positive', 'suppressed_losers_present', 'suppressed_loss_control_cost_negative', 'full_loss_cushion_lt_3'].

## diagnostic_from_reduce_freeze

| rank | candidate | settled | cand W/L | delta c | suppressed | suppressed W/L | winner recovery | loss cost | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `diagnostic_from_reduce_freeze_reduce_suppress_p75_exit_cents_lte_72` | 132 | 82/50 | 359.000000 | 9 | 8/1 | 479.000000 | -120.000000 | 3 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 2 | `diagnostic_from_reduce_freeze_reduce_suppress_p75_entry_book_age_gte_672` | 132 | 83/49 | 304.000000 | 9 | 8/1 | 450.000000 | -146.000000 | 3 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 3 | `diagnostic_from_reduce_freeze_reduce_suppress_p75_entry_stc_lte_596` | 132 | 88/44 | 389.000000 | 15 | 13/2 | 693.000000 | -304.000000 | 3 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 4 | `diagnostic_from_reduce_freeze_reduce_suppress_p75_duration_lte_52` | 132 | 87/45 | 351.000000 | 14 | 12/2 | 655.000000 | -304.000000 | 3 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 5 | `diagnostic_from_reduce_freeze_reduce_suppress_p75_depth_lte384_or_duration_lte52` | 132 | 92/40 | 523.000000 | 21 | 18/3 | 947.000000 | -424.000000 | 5 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative |
| 6 | `diagnostic_from_reduce_freeze_reduce_suppress_p75_depth_lte384_and_duration_lte75` | 132 | 86/46 | 289.000000 | 13 | 11/2 | 593.000000 | -304.000000 | 2 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 7 | `diagnostic_from_reduce_freeze_reduce_suppress_p75_exit_sigma_gte_110` | 132 | 82/50 | 203.000000 | 11 | 9/2 | 507.000000 | -304.000000 | 2 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 8 | `diagnostic_from_reduce_freeze_reduce_suppress_p75_entry_volshock_gte_0468` | 132 | 81/51 | 91.000000 | 9 | 7/2 | 395.000000 | -304.000000 | 0 | suppressed_decisions_lt_30, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |

### Best Variant Suppressed Rows

| market | side | result | reason | entry | exit | p_hold | depth | stc | dur | book age | sigma | volshock | current c | hold c | delta | won |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062130-30 | no | yes | mushroom_v28_probability_reduce | 76 | 60 | 0.768407 | 24.000000 | 628.084000 | 245.683692 | 297.000000 | 76.542004 | 0.060341 | -32.000000 | -152.000000 | -120.000000 | False |
| KXBTC15M-26MAY060645-45 | yes | yes | mushroom_v28_probability_reduce | 78 | 72 | 0.779789 | 99.490000 | 596.372000 | 124.166970 | 828.000000 | 85.127577 | 0.468181 | -12.000000 | 44.000000 | 56.000000 | True |
| KXBTC15M-26MAY060930-30 | no | no | mushroom_v28_probability_reduce | 73 | 72 | 0.799180 | 179.000000 | 470.196000 | 43.811640 | 172.000000 | 110.113616 | 0.779291 | -3.000000 | 54.000000 | 57.000000 | True |
| KXBTC15M-26MAY060915-15 | no | no | mushroom_v28_probability_reduce | 70 | 70 | 0.793762 | 4953.550000 | 836.982000 | 79.387528 | 672.000000 | 125.230299 | 0.375678 | 0.000000 | 60.000000 | 60.000000 | True |
| KXBTC15M-26MAY061015-15 | no | no | mushroom_v28_probability_reduce | 70 | 70 | 0.799979 | 2075.040000 | 778.747000 | 84.739807 | 266.000000 | 137.842477 | 0.673097 | 0.000000 | 60.000000 | 60.000000 | True |
| KXBTC15M-26MAY061030-30 | yes | yes | mushroom_v28_probability_reduce | 78 | 70 | 0.752739 | 221.300000 | 518.045000 | 31.089772 | 906.000000 | 125.184173 | 0.791039 | -16.000000 | 44.000000 | 60.000000 | True |
| KXBTC15M-26MAY060300-00 | yes | yes | mushroom_v28_probability_reduce | 80 | 69 | 0.753164 | 40.000000 | 271.516000 | 31.087884 | 875.000000 | 47.661178 | -0.498899 | -22.000000 | 40.000000 | 62.000000 | True |
| KXBTC15M-26MAY060930-30 | no | no | mushroom_v28_probability_reduce | 76 | 69 | 0.787606 | 655.000000 | 519.475000 | 34.125873 | 891.000000 | 117.143469 | 0.765794 | -14.000000 | 48.000000 | 62.000000 | True |
| KXBTC15M-26MAY071045-45 | no | no | mushroom_v28_probability_reduce | 74 | 69 | 0.760529 | 225.990000 | 822.403000 | 35.479669 | 437.000000 | 137.454980 | 0.288890 | -10.000000 | 52.000000 | 62.000000 | True |

## post_observable_birth

| rank | candidate | settled | cand W/L | delta c | suppressed | suppressed W/L | winner recovery | loss cost | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `post_observable_birth_reduce_suppress_p75_exit_cents_lte_72` | 54 | 36/18 | -58.000000 | 2 | 1/1 | 62.000000 | -120.000000 | 0 | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 2 | `post_observable_birth_reduce_suppress_p75_entry_book_age_gte_672` | 54 | 35/19 | -146.000000 | 1 | 0/1 | 0 | -146.000000 | 0 | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 3 | `post_observable_birth_reduce_suppress_p75_entry_stc_lte_596` | 54 | 38/16 | -110.000000 | 6 | 4/2 | 194.000000 | -304.000000 | 0 | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 4 | `post_observable_birth_reduce_suppress_p75_duration_lte_52` | 54 | 37/17 | -142.000000 | 5 | 3/2 | 162.000000 | -304.000000 | 0 | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 5 | `post_observable_birth_reduce_suppress_p75_depth_lte384_and_duration_lte75` | 54 | 37/17 | -142.000000 | 5 | 3/2 | 162.000000 | -304.000000 | 0 | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 6 | `post_observable_birth_reduce_suppress_p75_exit_sigma_gte_110` | 54 | 35/19 | -242.000000 | 3 | 1/2 | 62.000000 | -304.000000 | 0 | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 7 | `post_observable_birth_reduce_suppress_p75_entry_volshock_gte_0468` | 54 | 34/20 | -304.000000 | 2 | 0/2 | 0 | -304.000000 | 0 | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |
| 8 | `post_observable_birth_reduce_suppress_p75_depth_lte384_or_duration_lte52` | 54 | 39/15 | -126.000000 | 9 | 6/3 | 298.000000 | -424.000000 | 0 | suppressed_decisions_lt_30, delta_not_positive, suppressed_losers_present, suppressed_loss_control_cost_negative, full_loss_cushion_lt_3 |

### Best Variant Suppressed Rows

| market | side | result | reason | entry | exit | p_hold | depth | stc | dur | book age | sigma | volshock | current c | hold c | delta | won |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062130-30 | no | yes | mushroom_v28_probability_reduce | 76 | 60 | 0.768407 | 24.000000 | 628.084000 | 245.683692 | 297.000000 | 76.542004 | 0.060341 | -32.000000 | -152.000000 | -120.000000 | False |
| KXBTC15M-26MAY071045-45 | no | no | mushroom_v28_probability_reduce | 74 | 69 | 0.760529 | 225.990000 | 822.403000 | 35.479669 | 437.000000 | 137.454980 | 0.288890 | -10.000000 | 52.000000 | 62.000000 | True |
