# v28 Target Hybrid-Veto Repair

Research-only: use hybrid FV as a warning light, then repair coverage from cleaner missed-market rows.

- Generated UTC: `2026-05-07T09:41:30.425918+00:00`
- Repair freeze UTC: `2026-05-06T15:26:49.986562+00:00`
- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Coverage floor: `75.0`

## Interpretation

- This probe is research-only and does not change live entries.
- The diagnostic window is for idea triage; the post-repair-freeze window is the promotion evidence stream.
- diagnostic_existing_target_window: target net -308.0c, hybrid-veto cluster 22 settled for -309.0c, best candidate skip_hybrid_veto_high_recross_hybrid_edge_repair coverage 75.20661157024793% net -101.0c delta 207.0c blockers ['net_not_positive'].
- post_repair_freeze_window: target net 381.0c, hybrid-veto cluster 8 settled for 143.0c, best candidate skip_hybrid_veto_edge_lte_minus2pp_hybrid_edge_repair coverage 75.43859649122807% net 332.0c delta -49.0c blockers [].

## diagnostic_existing_target_window

- Freeze UTC: `2026-05-05T23:30:17.615882+00:00`
- Forward denominator: `121`

| rank | candidate | repairs | coverage | net c | delta c | W/L | veto net c | repair net c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | skip_hybrid_veto_high_recross_hybrid_edge_repair | 15 | 75.206612 | -101.000000 | 207.000000 | 55/35 | -228.000000 | -21.000000 | net_not_positive |
| 2 | skip_hybrid_veto_high_recross_raw_clean_repair | 15 | 75.206612 | -101.000000 | 207.000000 | 55/35 | -228.000000 | -21.000000 | net_not_positive |
| 3 | skip_hybrid_veto_phi_half_reason_hybrid_edge_repair | 15 | 75.206612 | -101.000000 | 207.000000 | 55/35 | -228.000000 | -21.000000 | net_not_positive |
| 4 | skip_hybrid_veto_phi_half_reason_raw_clean_repair | 15 | 75.206612 | -101.000000 | 207.000000 | 55/35 | -228.000000 | -21.000000 | net_not_positive |
| 5 | skip_hybrid_veto_edge_lte_minus2pp_hybrid_edge_repair | 13 | 75.206612 | -168.000000 | 140.000000 | 54/36 | -204.000000 | -64.000000 | net_not_positive |
| 6 | skip_hybrid_veto_edge_lte_minus2pp_raw_clean_repair | 13 | 75.206612 | -168.000000 | 140.000000 | 54/36 | -204.000000 | -64.000000 | net_not_positive |
| 7 | skip_all_hybrid_vetoes_hybrid_edge_repair | 23 | 75.206612 | -187.000000 | 121.000000 | 54/36 | -309.000000 | -188.000000 | net_not_positive |
| 8 | skip_all_hybrid_vetoes_raw_clean_repair | 23 | 75.206612 | -187.000000 | 121.000000 | 54/36 | -309.000000 | -188.000000 | net_not_positive |
| 9 | skip_hybrid_veto_high_recross_near_hybrid_edge_repair | 12 | 75.206612 | -396.000000 | -88.000000 | 53/37 | 8.000000 | -80.000000 | net_not_positive |
| 10 | skip_hybrid_veto_high_recross_near_raw_clean_repair | 12 | 75.206612 | -396.000000 | -88.000000 | 53/37 | 8.000000 | -80.000000 | net_not_positive |

### Best Candidate Repairs

| market | source | side | won | net c | raw p | hybrid p | ask | raw edge | hybrid edge | recross | abs d | score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.952539 | 0.700000 | 0.263659 | 0.252539 | 0.073753 | 1.543579 | 1.531676 |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 0.942571 | 0.936858 | 0.730000 | 0.212571 | 0.206858 | 0.239053 | 1.308547 | 1.398305 |
| KXBTC15M-26MAY061000-00 | approved_entry | no | True | 31.000000 | 0.854748 | 0.836415 | 0.650000 | 0.204748 | 0.186415 | 0.586664 | 0.901711 | 1.211980 |
| KXBTC15M-26MAY060745-45 | approved_entry | yes | False | -71.000000 | 0.851843 | 0.846082 | 0.690000 | 0.161843 | 0.156082 | 0.303224 | 0.889718 | 1.179914 |
| KXBTC15M-26MAY060900-00 | approved_entry | no | True | 25.000000 | 0.855256 | 0.852463 | 0.730000 | 0.125256 | 0.122463 | 0.145613 | 0.858522 | 1.129363 |
| KXBTC15M-26MAY052045-45 | rejected_actionable | yes | False | -73.000000 | 0.819741 | 0.811603 | 0.700000 | 0.119741 | 0.111603 | 0.100982 | 0.766279 | 1.067078 |
| KXBTC15M-26MAY060615-15 | approved_entry | yes | True | 23.000000 | 0.852040 | 0.845798 | 0.750000 | 0.102040 | 0.095798 | 0.328333 | 0.888798 | 1.057129 |
| KXBTC15M-26MAY060700-00 | approved_entry | yes | True | 23.000000 | 0.852084 | 0.841391 | 0.750000 | 0.102084 | 0.091391 | 0.192044 | 0.872216 | 1.055094 |
| KXBTC15M-26MAY061530-30 | rejected_actionable | yes | True | 56.000000 | 0.608780 | 0.602430 | 0.400000 | 0.208780 | 0.202430 | 0.228156 | 0.226282 | 1.001938 |
| KXBTC15M-26MAY060715-15 | approved_entry | yes | True | 17.000000 | 0.872115 | 0.865418 | 0.810000 | 0.062115 | 0.055418 | 0.333271 | 0.965012 | 0.999518 |
| KXBTC15M-26MAY060815-15 | approved_entry | no | True | 18.000000 | 0.860153 | 0.852470 | 0.790000 | 0.070153 | 0.062470 | 0.395024 | 0.900687 | 0.992764 |
| KXBTC15M-26MAY061300-00 | approved_entry | yes | False | -82.000000 | 0.860906 | 0.855026 | 0.800000 | 0.060906 | 0.055026 | 0.301730 | 0.913273 | 0.988072 |
| KXBTC15M-26MAY060315-15 | rejected_actionable | yes | True | 16.000000 | 0.854395 | 0.851273 | 0.810000 | 0.044395 | 0.041273 | 0.163136 | 0.837534 | 0.963425 |
| KXBTC15M-26MAY052200-00 | approved_entry | yes | True | 19.000000 | 0.850777 | 0.843118 | 0.790000 | 0.060777 | 0.053118 | 0.404344 | 0.880811 | 0.962962 |
| KXBTC15M-26MAY060115-15 | rejected_actionable | no | True | 24.000000 | 0.819858 | 0.796866 | 0.730000 | 0.089858 | 0.066866 | 0.405225 | 0.766642 | 0.942260 |

## post_repair_freeze_window

- Freeze UTC: `2026-05-06T15:26:49.986562+00:00`
- Forward denominator: `57`

| rank | candidate | repairs | coverage | net c | delta c | W/L | veto net c | repair net c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | skip_hybrid_veto_edge_lte_minus2pp_hybrid_edge_repair | 1 | 75.438596 | 332.000000 | -49.000000 | 25/17 | -23.000000 | -72.000000 |  |
| 2 | skip_hybrid_veto_edge_lte_minus2pp_raw_clean_repair | 1 | 75.438596 | 332.000000 | -49.000000 | 25/17 | -23.000000 | -72.000000 |  |
| 3 | skip_hybrid_veto_high_recross_hybrid_edge_repair | 2 | 75.438596 | 275.000000 | -106.000000 | 25/17 | 59.000000 | -47.000000 |  |
| 4 | skip_hybrid_veto_high_recross_raw_clean_repair | 2 | 75.438596 | 275.000000 | -106.000000 | 25/17 | 59.000000 | -47.000000 |  |
| 5 | skip_hybrid_veto_phi_half_reason_hybrid_edge_repair | 2 | 75.438596 | 275.000000 | -106.000000 | 25/17 | 59.000000 | -47.000000 |  |
| 6 | skip_hybrid_veto_phi_half_reason_raw_clean_repair | 2 | 75.438596 | 275.000000 | -106.000000 | 25/17 | 59.000000 | -47.000000 |  |
| 7 | skip_hybrid_veto_high_recross_near_hybrid_edge_repair | 0 | 75.438596 | 237.000000 | -144.000000 | 25/17 | 144.000000 | 0 |  |
| 8 | skip_hybrid_veto_high_recross_near_raw_clean_repair | 0 | 75.438596 | 237.000000 | -144.000000 | 25/17 | 144.000000 | 0 |  |
| 9 | skip_all_hybrid_vetoes_hybrid_edge_repair | 6 | 75.438596 | 19.000000 | -362.000000 | 23/19 | 143.000000 | -219.000000 |  |
| 10 | skip_all_hybrid_vetoes_raw_clean_repair | 6 | 75.438596 | 19.000000 | -362.000000 | 23/19 | 143.000000 | -219.000000 |  |

### Best Candidate Repairs

| market | source | side | won | net c | raw p | hybrid p | ask | raw edge | hybrid edge | recross | abs d | score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.963659 | 0.952539 | 0.700000 | 0.263659 | 0.252539 | 0.073753 | 1.543579 | 1.531676 |
