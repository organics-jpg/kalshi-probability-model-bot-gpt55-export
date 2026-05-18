# v28 Feature-Gate Live Outcome Alignment

Research-only attribution audit. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:26.255402+00:00`
- Feature source: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_boundary_clock_feature_gate_candidate_latest.json`
- Trades source: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\stats\live_mushroom_v28_size2\trades.csv`

## Interpretation

- This is an attribution audit only; it does not change official candidate scoring or live behavior.
- post_feature_freeze_bridge_raw03_recross70_abs075: theory 307.0c vs live total 66.99999999999999c and live per-contract market-sum 68.49166666666666c on 48/64 selected markets; tags {'live_exited_before_settlement': 37, 'same_sign_positive': 21, 'no_live_trade_on_market': 16, 'live_traded_opposite_side': 13, 'theory_win_live_market_loss': 13, 'theory_win_selected_side_live_loss': 12, 'same_sign_negative': 10, 'live_did_not_trade_selected_side': 8, 'theory_loss_live_market_win': 4}.
- post_feature_freeze_bridge_raw05_recross60_abs085: theory 445.0c vs live total 73.0c and live per-contract market-sum 64.74166666666666c on 43/55 selected markets; tags {'live_exited_before_settlement': 33, 'same_sign_positive': 19, 'theory_win_live_market_loss': 14, 'theory_win_selected_side_live_loss': 13, 'no_live_trade_on_market': 12, 'live_traded_opposite_side': 11, 'same_sign_negative': 6, 'live_did_not_trade_selected_side': 6, 'theory_loss_live_market_win': 4}.
- post_feature_freeze_bridge_raw05_recross60_abs085_ask65: theory 344.0c vs live total 48.0c and live per-contract market-sum 52.24166666666667c on 42/47 selected markets; tags {'live_exited_before_settlement': 32, 'same_sign_positive': 21, 'theory_win_live_market_loss': 16, 'theory_win_selected_side_live_loss': 15, 'live_traded_opposite_side': 5, 'no_live_trade_on_market': 5, 'same_sign_negative': 4, 'theory_loss_live_market_win': 1}.
- post_feature_freeze_entry_raw03_recross70_abs075: theory 307.0c vs live total 66.99999999999999c and live per-contract market-sum 68.49166666666666c on 48/64 selected markets; tags {'live_exited_before_settlement': 37, 'same_sign_positive': 21, 'no_live_trade_on_market': 16, 'live_traded_opposite_side': 13, 'theory_win_live_market_loss': 13, 'theory_win_selected_side_live_loss': 12, 'same_sign_negative': 10, 'live_did_not_trade_selected_side': 8, 'theory_loss_live_market_win': 4}.
- post_feature_freeze_entry_raw05_recross60_abs085: theory 445.0c vs live total 73.0c and live per-contract market-sum 64.74166666666666c on 43/55 selected markets; tags {'live_exited_before_settlement': 33, 'same_sign_positive': 19, 'theory_win_live_market_loss': 14, 'theory_win_selected_side_live_loss': 13, 'no_live_trade_on_market': 12, 'live_traded_opposite_side': 11, 'same_sign_negative': 6, 'live_did_not_trade_selected_side': 6, 'theory_loss_live_market_win': 4}.
- post_feature_freeze_entry_raw05_recross60_abs085_ask65: theory 344.0c vs live total 48.0c and live per-contract market-sum 52.24166666666667c on 42/47 selected markets; tags {'live_exited_before_settlement': 32, 'same_sign_positive': 21, 'theory_win_live_market_loss': 16, 'theory_win_selected_side_live_loss': 15, 'live_traded_opposite_side': 5, 'no_live_trade_on_market': 5, 'same_sign_negative': 4, 'theory_loss_live_market_win': 1}.

## post_feature_freeze_bridge_raw03_recross70_abs075

- Lane: `post_feature_freeze_bridge`
- Official summary: `{'avg_net_cents': 4.796875, 'coverage_pct': 78.04878048780488, 'entries': 64, 'losses': 22, 'net_cents': 307.0, 'settled': 64, 'wins': 42}`
- Official blockers: `['reconstructed_share_gt_35pct']`
- Alignment summary: `{'rows': 64, 'live_traded_markets': 48, 'no_live_trade_markets': 16, 'theory_net_cents': 307.0, 'live_net_cents_total': 66.99999999999999, 'selected_side_live_net_cents': 311.0, 'live_net_cents_per_contract_market_sum': 68.49166666666666, 'selected_side_live_net_cents_per_contract_market_sum': 88.74166666666666, 'theory_minus_live_total_cents': 240.0, 'theory_minus_selected_side_live_cents': -4.0, 'theory_minus_live_per_contract_market_sum_cents': 238.50833333333333, 'theory_minus_selected_side_per_contract_market_sum_cents': 218.25833333333333, 'tag_counts': {'live_exited_before_settlement': 37, 'same_sign_positive': 21, 'no_live_trade_on_market': 16, 'live_traded_opposite_side': 13, 'theory_win_live_market_loss': 13, 'theory_win_selected_side_live_loss': 12, 'same_sign_negative': 10, 'live_did_not_trade_selected_side': 8, 'theory_loss_live_market_win': 4}, 'source_tag_counts': {'approved_entry::live_exited_before_settlement': 27, 'approved_entry::same_sign_positive': 18, 'approved_entry::theory_win_live_market_loss': 13, 'approved_entry::theory_win_selected_side_live_loss': 12, 'rejected_actionable::no_live_trade_on_market': 12, 'rejected_actionable::live_exited_before_settlement': 10, 'rejected_actionable::live_did_not_trade_selected_side': 8, 'rejected_actionable::live_traded_opposite_side': 8, 'rejected_actionable::same_sign_negative': 7, 'approved_entry::live_traded_opposite_side': 5, 'approved_entry::no_live_trade_on_market': 4, 'approved_entry::same_sign_negative': 3, 'rejected_actionable::theory_loss_live_market_win': 3, 'rejected_actionable::same_sign_positive': 3, 'approved_entry::theory_loss_live_market_win': 1}}`

| market | source | side | won | theory c | live trades | live sides | live c | live c/ct | selected-side c/ct | tags |
|---|---|---|---|---:|---:|---|---:|---:|---:|---|
| KXBTC15M-26MAY062015-15 | approved_entry | no | True | 56.000000 | 3 | {'no': 1, 'yes': 2} | -164.000000 | -27.333333 | -23.500000 | live_traded_opposite_side, theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070030-30 | approved_entry | yes | True | 15.000000 | 2 | {'yes': 2} | -100.000000 | -16.666667 | -16.666667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062315-15 | approved_entry | no | True | 15.000000 | 2 | {'no': 2} | -72.000000 | -12.000000 | -12.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 27.000000 | 3 | {'no': 3} | -72.000000 | -6.000000 | -6.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | 21.000000 | 2 | {'no': 2} | -53.000000 | -8.833333 | -8.833333 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 17.000000 | 1 | {'yes': 1} | -40.000000 | -10.000000 | -10.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071230-30 | approved_entry | yes | True | 21.000000 | 3 | {'yes': 3} | -22.000000 | -3.666667 | -3.666667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070745-45 | approved_entry | yes | True | 30.000000 | 2 | {'yes': 2} | -19.000000 | -3.166667 | -3.166667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY061400-00 | approved_entry | no | True | 10.000000 | 1 | {'no': 1} | -14.000000 | -7.000000 | -7.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070545-45 | approved_entry | no | True | 16.000000 | 3 | {'yes': 2, 'no': 1} | -10.000000 | -1.250000 | 13.250000 | live_traded_opposite_side, theory_win_live_market_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062100-00 | approved_entry | yes | True | 37.000000 | 3 | {'yes': 3} | -9.000000 | -1.500000 | -1.500000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 3 | {'yes': 3} | -8.000000 | -1.000000 | -1.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | 18.000000 | 3 | {'no': 3} | -2.000000 | -0.333333 | -0.333333 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 3 | {'no': 3} | -99.000000 | -19.800000 | -19.800000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 1 | {'no': 1} | -92.000000 | -23.000000 | -23.000000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY071215-15 | rejected_actionable | yes | False | -75.000000 | 2 | {'no': 2} | -45.000000 | -11.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -15.000000 | 2 | {'no': 2} | -44.000000 | -11.000000 | -11.000000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | False | -5.000000 | 2 | {'yes': 2} | -41.000000 | -10.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY070145-45 | rejected_actionable | yes | False | -3.000000 | 2 | {'no': 2} | -41.000000 | -10.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062300-00 | rejected_actionable | no | False | -2.000000 | 2 | {'yes': 2} | -17.000000 | -4.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | False | -7.000000 | 2 | {'yes': 2} | -13.000000 | -2.166667 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | False | -68.000000 | 1 | {'yes': 1} | -9.000000 | -4.500000 | -4.500000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 4 | {'no': 3, 'yes': 1} | -6.000000 | -0.750000 | -5.333333 | live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061545-45 | approved_entry | yes | True | 15.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061900-00 | approved_entry | yes | True | 8.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061930-30 | rejected_actionable | no | False | -2.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY062145-45 | rejected_actionable | yes | True | 6.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY070000-00 | approved_entry | no | True | 20.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY070900-00 | rejected_actionable | no | False | -6.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071200-00 | approved_entry | no | True | 20.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071245-45 | rejected_actionable | no | True | 8.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071330-30 | rejected_actionable | no | True | 16.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 4 | {'yes': 3, 'no': 1} | 1.000000 | 0.125000 | -3.833333 | live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 3 | {'yes': 2, 'no': 1} | 5.000000 | 0.625000 | 7.666667 | live_traded_opposite_side, live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061800-00 | approved_entry | no | True | 28.000000 | 2 | {'no': 2} | 6.000000 | 1.500000 | 1.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061615-15 | approved_entry | yes | True | 9.000000 | 1 | {'yes': 1} | 12.000000 | 6.000000 | 6.000000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061815-15 | approved_entry | no | True | 14.000000 | 2 | {'no': 2} | 18.000000 | 4.500000 | 4.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY070115-15 | approved_entry | yes | True | 16.000000 | 2 | {'yes': 2} | 20.000000 | 3.333333 | 3.333333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | 33.000000 | 3 | {'no': 3} | 23.000000 | 2.875000 | 2.875000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 24.000000 | 2 | {'no': 2} | 23.000000 | 3.833333 | 3.833333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061445-45 | approved_entry | no | True | 8.000000 | 1 | {'no': 1} | 24.000000 | 12.000000 | 12.000000 | same_sign_positive |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -11.000000 | 1 | {'no': 1} | 25.000000 | 12.500000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | False | -6.000000 | 1 | {'no': 1} | 29.000000 | 7.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY061415-15 | rejected_actionable | yes | False | -3.000000 | 1 | {'no': 1} | 30.000000 | 15.000000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, theory_loss_live_market_win |
| KXBTC15M-26MAY070530-30 | rejected_actionable | no | True | 7.000000 | 1 | {'no': 1} | 30.000000 | 15.000000 | 15.000000 | same_sign_positive |
| KXBTC15M-26MAY070715-15 | rejected_actionable | yes | True | 8.000000 | 1 | {'yes': 1} | 37.000000 | 18.500000 | 18.500000 | same_sign_positive |
| KXBTC15M-26MAY071030-30 | approved_entry | no | True | 21.000000 | 2 | {'no': 2} | 37.000000 | 6.166667 | 6.166667 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062030-30 | approved_entry | no | True | 31.000000 | 2 | {'no': 2} | 38.000000 | 9.500000 | 9.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY071130-30 | approved_entry | no | True | 13.000000 | 1 | {'no': 1} | 42.000000 | 10.500000 | 10.500000 | same_sign_positive |
| KXBTC15M-26MAY061645-45 | approved_entry | no | True | 21.000000 | 1 | {'no': 1} | 45.000000 | 22.500000 | 22.500000 | same_sign_positive |
| KXBTC15M-26MAY070915-15 | approved_entry | no | True | 20.000000 | 2 | {'no': 2} | 56.000000 | 9.333333 | 9.333333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062200-00 | rejected_actionable | no | True | 4.000000 | 1 | {'no': 1} | 58.000000 | 14.500000 | 14.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061915-15 | approved_entry | no | True | 11.000000 | 1 | {'no': 1} | 67.000000 | 16.750000 | 16.750000 | same_sign_positive |
| KXBTC15M-26MAY070815-15 | approved_entry | yes | True | 9.000000 | 1 | {'yes': 1} | 87.000000 | 14.500000 | 14.500000 | same_sign_positive |
| KXBTC15M-26MAY070645-45 | approved_entry | yes | True | 16.000000 | 1 | {'yes': 1} | 101.000000 | 16.833333 | 16.833333 | same_sign_positive |
| KXBTC15M-26MAY071145-45 | approved_entry | yes | True | 20.000000 | 1 | {'yes': 1} | 106.000000 | 17.666667 | 17.666667 | same_sign_positive |
| KXBTC15M-26MAY070945-45 | approved_entry | no | True | 28.000000 | 1 | {'no': 1} | 139.000000 | 23.166667 | 23.166667 | same_sign_positive |

## post_feature_freeze_bridge_raw05_recross60_abs085

- Lane: `post_feature_freeze_bridge`
- Official summary: `{'avg_net_cents': 8.090909090909092, 'coverage_pct': 67.07317073170732, 'entries': 55, 'losses': 16, 'net_cents': 445.0, 'settled': 55, 'wins': 39}`
- Official blockers: `['coverage_too_low']`
- Alignment summary: `{'rows': 55, 'live_traded_markets': 43, 'no_live_trade_markets': 12, 'theory_net_cents': 445.0, 'live_net_cents_total': 73.0, 'selected_side_live_net_cents': 231.0, 'live_net_cents_per_contract_market_sum': 64.74166666666666, 'selected_side_live_net_cents_per_contract_market_sum': 63.49166666666667, 'theory_minus_live_total_cents': 372.0, 'theory_minus_selected_side_live_cents': 214.0, 'theory_minus_live_per_contract_market_sum_cents': 380.2583333333333, 'theory_minus_selected_side_per_contract_market_sum_cents': 381.5083333333333, 'tag_counts': {'live_exited_before_settlement': 33, 'same_sign_positive': 19, 'theory_win_live_market_loss': 14, 'theory_win_selected_side_live_loss': 13, 'no_live_trade_on_market': 12, 'live_traded_opposite_side': 11, 'same_sign_negative': 6, 'live_did_not_trade_selected_side': 6, 'theory_loss_live_market_win': 4}, 'source_tag_counts': {'approved_entry::live_exited_before_settlement': 28, 'approved_entry::same_sign_positive': 18, 'approved_entry::theory_win_live_market_loss': 14, 'approved_entry::theory_win_selected_side_live_loss': 13, 'rejected_actionable::no_live_trade_on_market': 8, 'rejected_actionable::live_did_not_trade_selected_side': 6, 'rejected_actionable::live_traded_opposite_side': 6, 'approved_entry::live_traded_opposite_side': 5, 'rejected_actionable::live_exited_before_settlement': 5, 'approved_entry::no_live_trade_on_market': 4, 'approved_entry::same_sign_negative': 3, 'rejected_actionable::same_sign_negative': 3, 'rejected_actionable::theory_loss_live_market_win': 3, 'approved_entry::theory_loss_live_market_win': 1, 'rejected_actionable::same_sign_positive': 1}}`

| market | source | side | won | theory c | live trades | live sides | live c | live c/ct | selected-side c/ct | tags |
|---|---|---|---|---:|---:|---|---:|---:|---:|---|
| KXBTC15M-26MAY062015-15 | approved_entry | no | True | 56.000000 | 3 | {'no': 1, 'yes': 2} | -164.000000 | -27.333333 | -23.500000 | live_traded_opposite_side, theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070030-30 | approved_entry | yes | True | 15.000000 | 2 | {'yes': 2} | -100.000000 | -16.666667 | -16.666667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062315-15 | approved_entry | no | True | 15.000000 | 2 | {'no': 2} | -72.000000 | -12.000000 | -12.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 27.000000 | 3 | {'no': 3} | -72.000000 | -6.000000 | -6.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | 21.000000 | 2 | {'no': 2} | -53.000000 | -8.833333 | -8.833333 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071215-15 | approved_entry | no | True | 20.000000 | 2 | {'no': 2} | -45.000000 | -11.250000 | -11.250000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 17.000000 | 1 | {'yes': 1} | -40.000000 | -10.000000 | -10.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071230-30 | approved_entry | yes | True | 21.000000 | 3 | {'yes': 3} | -22.000000 | -3.666667 | -3.666667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070745-45 | approved_entry | yes | True | 30.000000 | 2 | {'yes': 2} | -19.000000 | -3.166667 | -3.166667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY061400-00 | approved_entry | no | True | 10.000000 | 1 | {'no': 1} | -14.000000 | -7.000000 | -7.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070545-45 | approved_entry | no | True | 16.000000 | 3 | {'yes': 2, 'no': 1} | -10.000000 | -1.250000 | 13.250000 | live_traded_opposite_side, theory_win_live_market_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062100-00 | approved_entry | yes | True | 16.000000 | 3 | {'yes': 3} | -9.000000 | -1.500000 | -1.500000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 3 | {'yes': 3} | -8.000000 | -1.000000 | -1.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | 18.000000 | 3 | {'no': 3} | -2.000000 | -0.333333 | -0.333333 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 3 | {'no': 3} | -99.000000 | -19.800000 | -19.800000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 1 | {'no': 1} | -92.000000 | -23.000000 | -23.000000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | False | -5.000000 | 2 | {'yes': 2} | -41.000000 | -10.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062300-00 | rejected_actionable | no | False | -2.000000 | 2 | {'yes': 2} | -17.000000 | -4.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | False | -7.000000 | 2 | {'yes': 2} | -13.000000 | -2.166667 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 4 | {'no': 3, 'yes': 1} | -6.000000 | -0.750000 | -5.333333 | live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061545-45 | approved_entry | yes | True | 15.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061900-00 | approved_entry | yes | True | 8.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY062145-45 | rejected_actionable | yes | True | 6.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY070000-00 | approved_entry | no | True | 20.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071200-00 | approved_entry | no | True | 20.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 4 | {'yes': 3, 'no': 1} | 1.000000 | 0.125000 | -3.833333 | live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 3 | {'yes': 2, 'no': 1} | 5.000000 | 0.625000 | 7.666667 | live_traded_opposite_side, live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061800-00 | approved_entry | no | True | 28.000000 | 2 | {'no': 2} | 6.000000 | 1.500000 | 1.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061615-15 | approved_entry | yes | True | 9.000000 | 1 | {'yes': 1} | 12.000000 | 6.000000 | 6.000000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061815-15 | approved_entry | no | True | 14.000000 | 2 | {'no': 2} | 18.000000 | 4.500000 | 4.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY070115-15 | approved_entry | yes | True | 16.000000 | 2 | {'yes': 2} | 20.000000 | 3.333333 | 3.333333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | 33.000000 | 3 | {'no': 3} | 23.000000 | 2.875000 | 2.875000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 24.000000 | 2 | {'no': 2} | 23.000000 | 3.833333 | 3.833333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061445-45 | approved_entry | no | True | 8.000000 | 1 | {'no': 1} | 24.000000 | 12.000000 | 12.000000 | same_sign_positive |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 1 | {'no': 1} | 25.000000 | 12.500000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | False | -6.000000 | 1 | {'no': 1} | 29.000000 | 7.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY061415-15 | rejected_actionable | yes | False | -3.000000 | 1 | {'no': 1} | 30.000000 | 15.000000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, theory_loss_live_market_win |
| KXBTC15M-26MAY070715-15 | rejected_actionable | yes | True | 8.000000 | 1 | {'yes': 1} | 37.000000 | 18.500000 | 18.500000 | same_sign_positive |
| KXBTC15M-26MAY071030-30 | approved_entry | no | True | 21.000000 | 2 | {'no': 2} | 37.000000 | 6.166667 | 6.166667 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062030-30 | approved_entry | no | True | 31.000000 | 2 | {'no': 2} | 38.000000 | 9.500000 | 9.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY071130-30 | approved_entry | no | True | 13.000000 | 1 | {'no': 1} | 42.000000 | 10.500000 | 10.500000 | same_sign_positive |
| KXBTC15M-26MAY061645-45 | approved_entry | no | True | 21.000000 | 1 | {'no': 1} | 45.000000 | 22.500000 | 22.500000 | same_sign_positive |
| KXBTC15M-26MAY070915-15 | approved_entry | no | True | 20.000000 | 2 | {'no': 2} | 56.000000 | 9.333333 | 9.333333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061915-15 | approved_entry | no | True | 11.000000 | 1 | {'no': 1} | 67.000000 | 16.750000 | 16.750000 | same_sign_positive |
| KXBTC15M-26MAY070815-15 | approved_entry | yes | True | 9.000000 | 1 | {'yes': 1} | 87.000000 | 14.500000 | 14.500000 | same_sign_positive |
| KXBTC15M-26MAY070645-45 | approved_entry | yes | True | 16.000000 | 1 | {'yes': 1} | 101.000000 | 16.833333 | 16.833333 | same_sign_positive |
| KXBTC15M-26MAY071145-45 | approved_entry | yes | True | 20.000000 | 1 | {'yes': 1} | 106.000000 | 17.666667 | 17.666667 | same_sign_positive |
| KXBTC15M-26MAY070945-45 | approved_entry | no | True | 28.000000 | 1 | {'no': 1} | 139.000000 | 23.166667 | 23.166667 | same_sign_positive |

## post_feature_freeze_bridge_raw05_recross60_abs085_ask65

- Lane: `post_feature_freeze_bridge`
- Official summary: `{'avg_net_cents': 7.319148936170213, 'coverage_pct': 57.31707317073171, 'entries': 47, 'losses': 5, 'net_cents': 344.0, 'settled': 47, 'wins': 42}`
- Official blockers: `['coverage_too_low']`
- Alignment summary: `{'rows': 47, 'live_traded_markets': 42, 'no_live_trade_markets': 5, 'theory_net_cents': 344.0, 'live_net_cents_total': 48.0, 'selected_side_live_net_cents': 149.0, 'live_net_cents_per_contract_market_sum': 52.24166666666667, 'selected_side_live_net_cents_per_contract_market_sum': 63.325, 'theory_minus_live_total_cents': 296.0, 'theory_minus_selected_side_live_cents': 195.0, 'theory_minus_live_per_contract_market_sum_cents': 291.7583333333333, 'theory_minus_selected_side_per_contract_market_sum_cents': 280.675, 'tag_counts': {'live_exited_before_settlement': 32, 'same_sign_positive': 21, 'theory_win_live_market_loss': 16, 'theory_win_selected_side_live_loss': 15, 'live_traded_opposite_side': 5, 'no_live_trade_on_market': 5, 'same_sign_negative': 4, 'theory_loss_live_market_win': 1}, 'source_tag_counts': {'approved_entry::live_exited_before_settlement': 32, 'approved_entry::same_sign_positive': 20, 'approved_entry::theory_win_live_market_loss': 16, 'approved_entry::theory_win_selected_side_live_loss': 15, 'approved_entry::live_traded_opposite_side': 5, 'approved_entry::same_sign_negative': 4, 'approved_entry::no_live_trade_on_market': 4, 'rejected_actionable::no_live_trade_on_market': 1, 'approved_entry::theory_loss_live_market_win': 1, 'rejected_actionable::same_sign_positive': 1}}`

| market | source | side | won | theory c | live trades | live sides | live c | live c/ct | selected-side c/ct | tags |
|---|---|---|---|---:|---:|---|---:|---:|---:|---|
| KXBTC15M-26MAY070030-30 | approved_entry | yes | True | 15.000000 | 2 | {'yes': 2} | -100.000000 | -16.666667 | -16.666667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062315-15 | approved_entry | no | True | 15.000000 | 2 | {'no': 2} | -72.000000 | -12.000000 | -12.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 27.000000 | 3 | {'no': 3} | -72.000000 | -6.000000 | -6.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | 21.000000 | 2 | {'no': 2} | -53.000000 | -8.833333 | -8.833333 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071215-15 | approved_entry | no | True | 20.000000 | 2 | {'no': 2} | -45.000000 | -11.250000 | -11.250000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062245-45 | approved_entry | yes | True | 13.000000 | 2 | {'yes': 2} | -41.000000 | -10.250000 | -10.250000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 17.000000 | 1 | {'yes': 1} | -40.000000 | -10.000000 | -10.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071230-30 | approved_entry | yes | True | 21.000000 | 3 | {'yes': 3} | -22.000000 | -3.666667 | -3.666667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070745-45 | approved_entry | yes | True | 30.000000 | 2 | {'yes': 2} | -19.000000 | -3.166667 | -3.166667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062300-00 | approved_entry | yes | True | 12.000000 | 2 | {'yes': 2} | -17.000000 | -4.250000 | -4.250000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY061400-00 | approved_entry | no | True | 10.000000 | 1 | {'no': 1} | -14.000000 | -7.000000 | -7.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071115-15 | approved_entry | yes | True | 15.000000 | 2 | {'yes': 2} | -13.000000 | -2.166667 | -2.166667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070545-45 | approved_entry | no | True | 16.000000 | 3 | {'yes': 2, 'no': 1} | -10.000000 | -1.250000 | 13.250000 | live_traded_opposite_side, theory_win_live_market_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062100-00 | approved_entry | yes | True | 16.000000 | 3 | {'yes': 3} | -9.000000 | -1.500000 | -1.500000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 3 | {'yes': 3} | -8.000000 | -1.000000 | -1.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | 18.000000 | 3 | {'no': 3} | -2.000000 | -0.333333 | -0.333333 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062015-15 | approved_entry | yes | False | -71.000000 | 3 | {'no': 1, 'yes': 2} | -164.000000 | -27.333333 | -29.250000 | live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 3 | {'no': 3} | -99.000000 | -19.800000 | -19.800000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 1 | {'no': 1} | -92.000000 | -23.000000 | -23.000000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 4 | {'no': 3, 'yes': 1} | -6.000000 | -0.750000 | -5.333333 | live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY061545-45 | approved_entry | yes | True | 15.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061900-00 | approved_entry | yes | True | 8.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY062145-45 | rejected_actionable | yes | True | 6.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY070000-00 | approved_entry | no | True | 20.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071200-00 | approved_entry | no | True | 20.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 4 | {'yes': 3, 'no': 1} | 1.000000 | 0.125000 | -3.833333 | live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 3 | {'yes': 2, 'no': 1} | 5.000000 | 0.625000 | 7.666667 | live_traded_opposite_side, live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061800-00 | approved_entry | no | True | 28.000000 | 2 | {'no': 2} | 6.000000 | 1.500000 | 1.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061615-15 | approved_entry | yes | True | 9.000000 | 1 | {'yes': 1} | 12.000000 | 6.000000 | 6.000000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061815-15 | approved_entry | no | True | 14.000000 | 2 | {'no': 2} | 18.000000 | 4.500000 | 4.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY070115-15 | approved_entry | yes | True | 16.000000 | 2 | {'yes': 2} | 20.000000 | 3.333333 | 3.333333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | 33.000000 | 3 | {'no': 3} | 23.000000 | 2.875000 | 2.875000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 24.000000 | 2 | {'no': 2} | 23.000000 | 3.833333 | 3.833333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061445-45 | approved_entry | no | True | 8.000000 | 1 | {'no': 1} | 24.000000 | 12.000000 | 12.000000 | same_sign_positive |
| KXBTC15M-26MAY061830-30 | approved_entry | no | True | 9.000000 | 1 | {'no': 1} | 29.000000 | 7.250000 | 7.250000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061415-15 | approved_entry | no | True | 10.000000 | 1 | {'no': 1} | 30.000000 | 15.000000 | 15.000000 | same_sign_positive |
| KXBTC15M-26MAY070715-15 | rejected_actionable | yes | True | 8.000000 | 1 | {'yes': 1} | 37.000000 | 18.500000 | 18.500000 | same_sign_positive |
| KXBTC15M-26MAY071030-30 | approved_entry | no | True | 21.000000 | 2 | {'no': 2} | 37.000000 | 6.166667 | 6.166667 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062030-30 | approved_entry | no | True | 31.000000 | 2 | {'no': 2} | 38.000000 | 9.500000 | 9.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY071130-30 | approved_entry | no | True | 13.000000 | 1 | {'no': 1} | 42.000000 | 10.500000 | 10.500000 | same_sign_positive |
| KXBTC15M-26MAY061645-45 | approved_entry | no | True | 21.000000 | 1 | {'no': 1} | 45.000000 | 22.500000 | 22.500000 | same_sign_positive |
| KXBTC15M-26MAY070915-15 | approved_entry | no | True | 20.000000 | 2 | {'no': 2} | 56.000000 | 9.333333 | 9.333333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061915-15 | approved_entry | no | True | 11.000000 | 1 | {'no': 1} | 67.000000 | 16.750000 | 16.750000 | same_sign_positive |
| KXBTC15M-26MAY070815-15 | approved_entry | yes | True | 9.000000 | 1 | {'yes': 1} | 87.000000 | 14.500000 | 14.500000 | same_sign_positive |
| KXBTC15M-26MAY070645-45 | approved_entry | yes | True | 16.000000 | 1 | {'yes': 1} | 101.000000 | 16.833333 | 16.833333 | same_sign_positive |
| KXBTC15M-26MAY071145-45 | approved_entry | yes | True | 20.000000 | 1 | {'yes': 1} | 106.000000 | 17.666667 | 17.666667 | same_sign_positive |
| KXBTC15M-26MAY070945-45 | approved_entry | no | True | 28.000000 | 1 | {'no': 1} | 139.000000 | 23.166667 | 23.166667 | same_sign_positive |

## post_feature_freeze_entry_raw03_recross70_abs075

- Lane: `post_feature_freeze_entry`
- Official summary: `{'avg_net_cents': 4.796875, 'coverage_pct': 78.04878048780488, 'entries': 64, 'losses': 22, 'net_cents': 307.0, 'settled': 64, 'wins': 42}`
- Official blockers: `['reconstructed_share_gt_35pct']`
- Alignment summary: `{'rows': 64, 'live_traded_markets': 48, 'no_live_trade_markets': 16, 'theory_net_cents': 307.0, 'live_net_cents_total': 66.99999999999999, 'selected_side_live_net_cents': 311.0, 'live_net_cents_per_contract_market_sum': 68.49166666666666, 'selected_side_live_net_cents_per_contract_market_sum': 88.74166666666666, 'theory_minus_live_total_cents': 240.0, 'theory_minus_selected_side_live_cents': -4.0, 'theory_minus_live_per_contract_market_sum_cents': 238.50833333333333, 'theory_minus_selected_side_per_contract_market_sum_cents': 218.25833333333333, 'tag_counts': {'live_exited_before_settlement': 37, 'same_sign_positive': 21, 'no_live_trade_on_market': 16, 'live_traded_opposite_side': 13, 'theory_win_live_market_loss': 13, 'theory_win_selected_side_live_loss': 12, 'same_sign_negative': 10, 'live_did_not_trade_selected_side': 8, 'theory_loss_live_market_win': 4}, 'source_tag_counts': {'approved_entry::live_exited_before_settlement': 27, 'approved_entry::same_sign_positive': 18, 'approved_entry::theory_win_live_market_loss': 13, 'approved_entry::theory_win_selected_side_live_loss': 12, 'rejected_actionable::no_live_trade_on_market': 12, 'rejected_actionable::live_exited_before_settlement': 10, 'rejected_actionable::live_did_not_trade_selected_side': 8, 'rejected_actionable::live_traded_opposite_side': 8, 'rejected_actionable::same_sign_negative': 7, 'approved_entry::live_traded_opposite_side': 5, 'approved_entry::no_live_trade_on_market': 4, 'approved_entry::same_sign_negative': 3, 'rejected_actionable::theory_loss_live_market_win': 3, 'rejected_actionable::same_sign_positive': 3, 'approved_entry::theory_loss_live_market_win': 1}}`

| market | source | side | won | theory c | live trades | live sides | live c | live c/ct | selected-side c/ct | tags |
|---|---|---|---|---:|---:|---|---:|---:|---:|---|
| KXBTC15M-26MAY062015-15 | approved_entry | no | True | 56.000000 | 3 | {'no': 1, 'yes': 2} | -164.000000 | -27.333333 | -23.500000 | live_traded_opposite_side, theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070030-30 | approved_entry | yes | True | 15.000000 | 2 | {'yes': 2} | -100.000000 | -16.666667 | -16.666667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062315-15 | approved_entry | no | True | 15.000000 | 2 | {'no': 2} | -72.000000 | -12.000000 | -12.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 27.000000 | 3 | {'no': 3} | -72.000000 | -6.000000 | -6.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | 21.000000 | 2 | {'no': 2} | -53.000000 | -8.833333 | -8.833333 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 17.000000 | 1 | {'yes': 1} | -40.000000 | -10.000000 | -10.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071230-30 | approved_entry | yes | True | 21.000000 | 3 | {'yes': 3} | -22.000000 | -3.666667 | -3.666667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070745-45 | approved_entry | yes | True | 30.000000 | 2 | {'yes': 2} | -19.000000 | -3.166667 | -3.166667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY061400-00 | approved_entry | no | True | 10.000000 | 1 | {'no': 1} | -14.000000 | -7.000000 | -7.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070545-45 | approved_entry | no | True | 16.000000 | 3 | {'yes': 2, 'no': 1} | -10.000000 | -1.250000 | 13.250000 | live_traded_opposite_side, theory_win_live_market_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062100-00 | approved_entry | yes | True | 37.000000 | 3 | {'yes': 3} | -9.000000 | -1.500000 | -1.500000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 3 | {'yes': 3} | -8.000000 | -1.000000 | -1.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | 18.000000 | 3 | {'no': 3} | -2.000000 | -0.333333 | -0.333333 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 3 | {'no': 3} | -99.000000 | -19.800000 | -19.800000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 1 | {'no': 1} | -92.000000 | -23.000000 | -23.000000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY071215-15 | rejected_actionable | yes | False | -75.000000 | 2 | {'no': 2} | -45.000000 | -11.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -15.000000 | 2 | {'no': 2} | -44.000000 | -11.000000 | -11.000000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | False | -5.000000 | 2 | {'yes': 2} | -41.000000 | -10.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY070145-45 | rejected_actionable | yes | False | -3.000000 | 2 | {'no': 2} | -41.000000 | -10.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062300-00 | rejected_actionable | no | False | -2.000000 | 2 | {'yes': 2} | -17.000000 | -4.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | False | -7.000000 | 2 | {'yes': 2} | -13.000000 | -2.166667 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | False | -68.000000 | 1 | {'yes': 1} | -9.000000 | -4.500000 | -4.500000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 4 | {'no': 3, 'yes': 1} | -6.000000 | -0.750000 | -5.333333 | live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061545-45 | approved_entry | yes | True | 15.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061900-00 | approved_entry | yes | True | 8.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061930-30 | rejected_actionable | no | False | -2.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY062145-45 | rejected_actionable | yes | True | 6.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY070000-00 | approved_entry | no | True | 20.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY070900-00 | rejected_actionable | no | False | -6.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071200-00 | approved_entry | no | True | 20.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071245-45 | rejected_actionable | no | True | 8.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071330-30 | rejected_actionable | no | True | 16.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 4 | {'yes': 3, 'no': 1} | 1.000000 | 0.125000 | -3.833333 | live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 3 | {'yes': 2, 'no': 1} | 5.000000 | 0.625000 | 7.666667 | live_traded_opposite_side, live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061800-00 | approved_entry | no | True | 28.000000 | 2 | {'no': 2} | 6.000000 | 1.500000 | 1.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061615-15 | approved_entry | yes | True | 9.000000 | 1 | {'yes': 1} | 12.000000 | 6.000000 | 6.000000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061815-15 | approved_entry | no | True | 14.000000 | 2 | {'no': 2} | 18.000000 | 4.500000 | 4.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY070115-15 | approved_entry | yes | True | 16.000000 | 2 | {'yes': 2} | 20.000000 | 3.333333 | 3.333333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | 33.000000 | 3 | {'no': 3} | 23.000000 | 2.875000 | 2.875000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 24.000000 | 2 | {'no': 2} | 23.000000 | 3.833333 | 3.833333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061445-45 | approved_entry | no | True | 8.000000 | 1 | {'no': 1} | 24.000000 | 12.000000 | 12.000000 | same_sign_positive |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -11.000000 | 1 | {'no': 1} | 25.000000 | 12.500000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | False | -6.000000 | 1 | {'no': 1} | 29.000000 | 7.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY061415-15 | rejected_actionable | yes | False | -3.000000 | 1 | {'no': 1} | 30.000000 | 15.000000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, theory_loss_live_market_win |
| KXBTC15M-26MAY070530-30 | rejected_actionable | no | True | 7.000000 | 1 | {'no': 1} | 30.000000 | 15.000000 | 15.000000 | same_sign_positive |
| KXBTC15M-26MAY070715-15 | rejected_actionable | yes | True | 8.000000 | 1 | {'yes': 1} | 37.000000 | 18.500000 | 18.500000 | same_sign_positive |
| KXBTC15M-26MAY071030-30 | approved_entry | no | True | 21.000000 | 2 | {'no': 2} | 37.000000 | 6.166667 | 6.166667 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062030-30 | approved_entry | no | True | 31.000000 | 2 | {'no': 2} | 38.000000 | 9.500000 | 9.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY071130-30 | approved_entry | no | True | 13.000000 | 1 | {'no': 1} | 42.000000 | 10.500000 | 10.500000 | same_sign_positive |
| KXBTC15M-26MAY061645-45 | approved_entry | no | True | 21.000000 | 1 | {'no': 1} | 45.000000 | 22.500000 | 22.500000 | same_sign_positive |
| KXBTC15M-26MAY070915-15 | approved_entry | no | True | 20.000000 | 2 | {'no': 2} | 56.000000 | 9.333333 | 9.333333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062200-00 | rejected_actionable | no | True | 4.000000 | 1 | {'no': 1} | 58.000000 | 14.500000 | 14.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061915-15 | approved_entry | no | True | 11.000000 | 1 | {'no': 1} | 67.000000 | 16.750000 | 16.750000 | same_sign_positive |
| KXBTC15M-26MAY070815-15 | approved_entry | yes | True | 9.000000 | 1 | {'yes': 1} | 87.000000 | 14.500000 | 14.500000 | same_sign_positive |
| KXBTC15M-26MAY070645-45 | approved_entry | yes | True | 16.000000 | 1 | {'yes': 1} | 101.000000 | 16.833333 | 16.833333 | same_sign_positive |
| KXBTC15M-26MAY071145-45 | approved_entry | yes | True | 20.000000 | 1 | {'yes': 1} | 106.000000 | 17.666667 | 17.666667 | same_sign_positive |
| KXBTC15M-26MAY070945-45 | approved_entry | no | True | 28.000000 | 1 | {'no': 1} | 139.000000 | 23.166667 | 23.166667 | same_sign_positive |

## post_feature_freeze_entry_raw05_recross60_abs085

- Lane: `post_feature_freeze_entry`
- Official summary: `{'avg_net_cents': 8.090909090909092, 'coverage_pct': 67.07317073170732, 'entries': 55, 'losses': 16, 'net_cents': 445.0, 'settled': 55, 'wins': 39}`
- Official blockers: `['coverage_too_low']`
- Alignment summary: `{'rows': 55, 'live_traded_markets': 43, 'no_live_trade_markets': 12, 'theory_net_cents': 445.0, 'live_net_cents_total': 73.0, 'selected_side_live_net_cents': 231.0, 'live_net_cents_per_contract_market_sum': 64.74166666666666, 'selected_side_live_net_cents_per_contract_market_sum': 63.49166666666667, 'theory_minus_live_total_cents': 372.0, 'theory_minus_selected_side_live_cents': 214.0, 'theory_minus_live_per_contract_market_sum_cents': 380.2583333333333, 'theory_minus_selected_side_per_contract_market_sum_cents': 381.5083333333333, 'tag_counts': {'live_exited_before_settlement': 33, 'same_sign_positive': 19, 'theory_win_live_market_loss': 14, 'theory_win_selected_side_live_loss': 13, 'no_live_trade_on_market': 12, 'live_traded_opposite_side': 11, 'same_sign_negative': 6, 'live_did_not_trade_selected_side': 6, 'theory_loss_live_market_win': 4}, 'source_tag_counts': {'approved_entry::live_exited_before_settlement': 28, 'approved_entry::same_sign_positive': 18, 'approved_entry::theory_win_live_market_loss': 14, 'approved_entry::theory_win_selected_side_live_loss': 13, 'rejected_actionable::no_live_trade_on_market': 8, 'rejected_actionable::live_did_not_trade_selected_side': 6, 'rejected_actionable::live_traded_opposite_side': 6, 'approved_entry::live_traded_opposite_side': 5, 'rejected_actionable::live_exited_before_settlement': 5, 'approved_entry::no_live_trade_on_market': 4, 'approved_entry::same_sign_negative': 3, 'rejected_actionable::same_sign_negative': 3, 'rejected_actionable::theory_loss_live_market_win': 3, 'approved_entry::theory_loss_live_market_win': 1, 'rejected_actionable::same_sign_positive': 1}}`

| market | source | side | won | theory c | live trades | live sides | live c | live c/ct | selected-side c/ct | tags |
|---|---|---|---|---:|---:|---|---:|---:|---:|---|
| KXBTC15M-26MAY062015-15 | approved_entry | no | True | 56.000000 | 3 | {'no': 1, 'yes': 2} | -164.000000 | -27.333333 | -23.500000 | live_traded_opposite_side, theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070030-30 | approved_entry | yes | True | 15.000000 | 2 | {'yes': 2} | -100.000000 | -16.666667 | -16.666667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062315-15 | approved_entry | no | True | 15.000000 | 2 | {'no': 2} | -72.000000 | -12.000000 | -12.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 27.000000 | 3 | {'no': 3} | -72.000000 | -6.000000 | -6.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | 21.000000 | 2 | {'no': 2} | -53.000000 | -8.833333 | -8.833333 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071215-15 | approved_entry | no | True | 20.000000 | 2 | {'no': 2} | -45.000000 | -11.250000 | -11.250000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 17.000000 | 1 | {'yes': 1} | -40.000000 | -10.000000 | -10.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071230-30 | approved_entry | yes | True | 21.000000 | 3 | {'yes': 3} | -22.000000 | -3.666667 | -3.666667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070745-45 | approved_entry | yes | True | 30.000000 | 2 | {'yes': 2} | -19.000000 | -3.166667 | -3.166667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY061400-00 | approved_entry | no | True | 10.000000 | 1 | {'no': 1} | -14.000000 | -7.000000 | -7.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070545-45 | approved_entry | no | True | 16.000000 | 3 | {'yes': 2, 'no': 1} | -10.000000 | -1.250000 | 13.250000 | live_traded_opposite_side, theory_win_live_market_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062100-00 | approved_entry | yes | True | 16.000000 | 3 | {'yes': 3} | -9.000000 | -1.500000 | -1.500000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 3 | {'yes': 3} | -8.000000 | -1.000000 | -1.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | 18.000000 | 3 | {'no': 3} | -2.000000 | -0.333333 | -0.333333 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 3 | {'no': 3} | -99.000000 | -19.800000 | -19.800000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 1 | {'no': 1} | -92.000000 | -23.000000 | -23.000000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062245-45 | rejected_actionable | no | False | -5.000000 | 2 | {'yes': 2} | -41.000000 | -10.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062300-00 | rejected_actionable | no | False | -2.000000 | 2 | {'yes': 2} | -17.000000 | -4.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY071115-15 | rejected_actionable | no | False | -7.000000 | 2 | {'yes': 2} | -13.000000 | -2.166667 | None | live_did_not_trade_selected_side, live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 4 | {'no': 3, 'yes': 1} | -6.000000 | -0.750000 | -5.333333 | live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | False | -5.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061530-30 | rejected_actionable | no | False | -3.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061545-45 | approved_entry | yes | True | 15.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | False | -7.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | True | 96.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | False | -5.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061900-00 | approved_entry | yes | True | 8.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY062145-45 | rejected_actionable | yes | True | 6.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY070000-00 | approved_entry | no | True | 20.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | False | -4.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071200-00 | approved_entry | no | True | 20.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071300-00 | rejected_actionable | yes | False | -10.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 4 | {'yes': 3, 'no': 1} | 1.000000 | 0.125000 | -3.833333 | live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 3 | {'yes': 2, 'no': 1} | 5.000000 | 0.625000 | 7.666667 | live_traded_opposite_side, live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061800-00 | approved_entry | no | True | 28.000000 | 2 | {'no': 2} | 6.000000 | 1.500000 | 1.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061615-15 | approved_entry | yes | True | 9.000000 | 1 | {'yes': 1} | 12.000000 | 6.000000 | 6.000000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061815-15 | approved_entry | no | True | 14.000000 | 2 | {'no': 2} | 18.000000 | 4.500000 | 4.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY070115-15 | approved_entry | yes | True | 16.000000 | 2 | {'yes': 2} | 20.000000 | 3.333333 | 3.333333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | 33.000000 | 3 | {'no': 3} | 23.000000 | 2.875000 | 2.875000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 24.000000 | 2 | {'no': 2} | 23.000000 | 3.833333 | 3.833333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061445-45 | approved_entry | no | True | 8.000000 | 1 | {'no': 1} | 24.000000 | 12.000000 | 12.000000 | same_sign_positive |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | False | -6.000000 | 1 | {'no': 1} | 25.000000 | 12.500000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY061830-30 | rejected_actionable | yes | False | -6.000000 | 1 | {'no': 1} | 29.000000 | 7.250000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY061415-15 | rejected_actionable | yes | False | -3.000000 | 1 | {'no': 1} | 30.000000 | 15.000000 | None | live_did_not_trade_selected_side, live_traded_opposite_side, theory_loss_live_market_win |
| KXBTC15M-26MAY070715-15 | rejected_actionable | yes | True | 8.000000 | 1 | {'yes': 1} | 37.000000 | 18.500000 | 18.500000 | same_sign_positive |
| KXBTC15M-26MAY071030-30 | approved_entry | no | True | 21.000000 | 2 | {'no': 2} | 37.000000 | 6.166667 | 6.166667 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062030-30 | approved_entry | no | True | 31.000000 | 2 | {'no': 2} | 38.000000 | 9.500000 | 9.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY071130-30 | approved_entry | no | True | 13.000000 | 1 | {'no': 1} | 42.000000 | 10.500000 | 10.500000 | same_sign_positive |
| KXBTC15M-26MAY061645-45 | approved_entry | no | True | 21.000000 | 1 | {'no': 1} | 45.000000 | 22.500000 | 22.500000 | same_sign_positive |
| KXBTC15M-26MAY070915-15 | approved_entry | no | True | 20.000000 | 2 | {'no': 2} | 56.000000 | 9.333333 | 9.333333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061915-15 | approved_entry | no | True | 11.000000 | 1 | {'no': 1} | 67.000000 | 16.750000 | 16.750000 | same_sign_positive |
| KXBTC15M-26MAY070815-15 | approved_entry | yes | True | 9.000000 | 1 | {'yes': 1} | 87.000000 | 14.500000 | 14.500000 | same_sign_positive |
| KXBTC15M-26MAY070645-45 | approved_entry | yes | True | 16.000000 | 1 | {'yes': 1} | 101.000000 | 16.833333 | 16.833333 | same_sign_positive |
| KXBTC15M-26MAY071145-45 | approved_entry | yes | True | 20.000000 | 1 | {'yes': 1} | 106.000000 | 17.666667 | 17.666667 | same_sign_positive |
| KXBTC15M-26MAY070945-45 | approved_entry | no | True | 28.000000 | 1 | {'no': 1} | 139.000000 | 23.166667 | 23.166667 | same_sign_positive |

## post_feature_freeze_entry_raw05_recross60_abs085_ask65

- Lane: `post_feature_freeze_entry`
- Official summary: `{'avg_net_cents': 7.319148936170213, 'coverage_pct': 57.31707317073171, 'entries': 47, 'losses': 5, 'net_cents': 344.0, 'settled': 47, 'wins': 42}`
- Official blockers: `['coverage_too_low']`
- Alignment summary: `{'rows': 47, 'live_traded_markets': 42, 'no_live_trade_markets': 5, 'theory_net_cents': 344.0, 'live_net_cents_total': 48.0, 'selected_side_live_net_cents': 149.0, 'live_net_cents_per_contract_market_sum': 52.24166666666667, 'selected_side_live_net_cents_per_contract_market_sum': 63.325, 'theory_minus_live_total_cents': 296.0, 'theory_minus_selected_side_live_cents': 195.0, 'theory_minus_live_per_contract_market_sum_cents': 291.7583333333333, 'theory_minus_selected_side_per_contract_market_sum_cents': 280.675, 'tag_counts': {'live_exited_before_settlement': 32, 'same_sign_positive': 21, 'theory_win_live_market_loss': 16, 'theory_win_selected_side_live_loss': 15, 'live_traded_opposite_side': 5, 'no_live_trade_on_market': 5, 'same_sign_negative': 4, 'theory_loss_live_market_win': 1}, 'source_tag_counts': {'approved_entry::live_exited_before_settlement': 32, 'approved_entry::same_sign_positive': 20, 'approved_entry::theory_win_live_market_loss': 16, 'approved_entry::theory_win_selected_side_live_loss': 15, 'approved_entry::live_traded_opposite_side': 5, 'approved_entry::same_sign_negative': 4, 'approved_entry::no_live_trade_on_market': 4, 'rejected_actionable::no_live_trade_on_market': 1, 'approved_entry::theory_loss_live_market_win': 1, 'rejected_actionable::same_sign_positive': 1}}`

| market | source | side | won | theory c | live trades | live sides | live c | live c/ct | selected-side c/ct | tags |
|---|---|---|---|---:|---:|---|---:|---:|---:|---|
| KXBTC15M-26MAY070030-30 | approved_entry | yes | True | 15.000000 | 2 | {'yes': 2} | -100.000000 | -16.666667 | -16.666667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062315-15 | approved_entry | no | True | 15.000000 | 2 | {'no': 2} | -72.000000 | -12.000000 | -12.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | 27.000000 | 3 | {'no': 3} | -72.000000 | -6.000000 | -6.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | 21.000000 | 2 | {'no': 2} | -53.000000 | -8.833333 | -8.833333 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071215-15 | approved_entry | no | True | 20.000000 | 2 | {'no': 2} | -45.000000 | -11.250000 | -11.250000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062245-45 | approved_entry | yes | True | 13.000000 | 2 | {'yes': 2} | -41.000000 | -10.250000 | -10.250000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 17.000000 | 1 | {'yes': 1} | -40.000000 | -10.000000 | -10.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071230-30 | approved_entry | yes | True | 21.000000 | 3 | {'yes': 3} | -22.000000 | -3.666667 | -3.666667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070745-45 | approved_entry | yes | True | 30.000000 | 2 | {'yes': 2} | -19.000000 | -3.166667 | -3.166667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062300-00 | approved_entry | yes | True | 12.000000 | 2 | {'yes': 2} | -17.000000 | -4.250000 | -4.250000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY061400-00 | approved_entry | no | True | 10.000000 | 1 | {'no': 1} | -14.000000 | -7.000000 | -7.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071115-15 | approved_entry | yes | True | 15.000000 | 2 | {'yes': 2} | -13.000000 | -2.166667 | -2.166667 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY070545-45 | approved_entry | no | True | 16.000000 | 3 | {'yes': 2, 'no': 1} | -10.000000 | -1.250000 | 13.250000 | live_traded_opposite_side, theory_win_live_market_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062100-00 | approved_entry | yes | True | 16.000000 | 3 | {'yes': 3} | -9.000000 | -1.500000 | -1.500000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 3 | {'yes': 3} | -8.000000 | -1.000000 | -1.000000 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | 18.000000 | 3 | {'no': 3} | -2.000000 | -0.333333 | -0.333333 | theory_win_live_market_loss, theory_win_selected_side_live_loss, live_exited_before_settlement |
| KXBTC15M-26MAY062015-15 | approved_entry | yes | False | -71.000000 | 3 | {'no': 1, 'yes': 2} | -164.000000 | -27.333333 | -29.250000 | live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 3 | {'no': 3} | -99.000000 | -19.800000 | -19.800000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY062130-30 | approved_entry | no | False | -78.000000 | 1 | {'no': 1} | -92.000000 | -23.000000 | -23.000000 | live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 4 | {'no': 3, 'yes': 1} | -6.000000 | -0.750000 | -5.333333 | live_traded_opposite_side, live_exited_before_settlement, same_sign_negative |
| KXBTC15M-26MAY061545-45 | approved_entry | yes | True | 15.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY061900-00 | approved_entry | yes | True | 8.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY062145-45 | rejected_actionable | yes | True | 6.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY070000-00 | approved_entry | no | True | 20.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071200-00 | approved_entry | no | True | 20.000000 | 0 | {} | 0 | None | None | no_live_trade_on_market |
| KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 4 | {'yes': 3, 'no': 1} | 1.000000 | 0.125000 | -3.833333 | live_traded_opposite_side, theory_loss_live_market_win, live_exited_before_settlement |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 3 | {'yes': 2, 'no': 1} | 5.000000 | 0.625000 | 7.666667 | live_traded_opposite_side, live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061800-00 | approved_entry | no | True | 28.000000 | 2 | {'no': 2} | 6.000000 | 1.500000 | 1.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061615-15 | approved_entry | yes | True | 9.000000 | 1 | {'yes': 1} | 12.000000 | 6.000000 | 6.000000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061815-15 | approved_entry | no | True | 14.000000 | 2 | {'no': 2} | 18.000000 | 4.500000 | 4.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY070115-15 | approved_entry | yes | True | 16.000000 | 2 | {'yes': 2} | 20.000000 | 3.333333 | 3.333333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | 33.000000 | 3 | {'no': 3} | 23.000000 | 2.875000 | 2.875000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 24.000000 | 2 | {'no': 2} | 23.000000 | 3.833333 | 3.833333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061445-45 | approved_entry | no | True | 8.000000 | 1 | {'no': 1} | 24.000000 | 12.000000 | 12.000000 | same_sign_positive |
| KXBTC15M-26MAY061830-30 | approved_entry | no | True | 9.000000 | 1 | {'no': 1} | 29.000000 | 7.250000 | 7.250000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061415-15 | approved_entry | no | True | 10.000000 | 1 | {'no': 1} | 30.000000 | 15.000000 | 15.000000 | same_sign_positive |
| KXBTC15M-26MAY070715-15 | rejected_actionable | yes | True | 8.000000 | 1 | {'yes': 1} | 37.000000 | 18.500000 | 18.500000 | same_sign_positive |
| KXBTC15M-26MAY071030-30 | approved_entry | no | True | 21.000000 | 2 | {'no': 2} | 37.000000 | 6.166667 | 6.166667 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY062030-30 | approved_entry | no | True | 31.000000 | 2 | {'no': 2} | 38.000000 | 9.500000 | 9.500000 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY071130-30 | approved_entry | no | True | 13.000000 | 1 | {'no': 1} | 42.000000 | 10.500000 | 10.500000 | same_sign_positive |
| KXBTC15M-26MAY061645-45 | approved_entry | no | True | 21.000000 | 1 | {'no': 1} | 45.000000 | 22.500000 | 22.500000 | same_sign_positive |
| KXBTC15M-26MAY070915-15 | approved_entry | no | True | 20.000000 | 2 | {'no': 2} | 56.000000 | 9.333333 | 9.333333 | live_exited_before_settlement, same_sign_positive |
| KXBTC15M-26MAY061915-15 | approved_entry | no | True | 11.000000 | 1 | {'no': 1} | 67.000000 | 16.750000 | 16.750000 | same_sign_positive |
| KXBTC15M-26MAY070815-15 | approved_entry | yes | True | 9.000000 | 1 | {'yes': 1} | 87.000000 | 14.500000 | 14.500000 | same_sign_positive |
| KXBTC15M-26MAY070645-45 | approved_entry | yes | True | 16.000000 | 1 | {'yes': 1} | 101.000000 | 16.833333 | 16.833333 | same_sign_positive |
| KXBTC15M-26MAY071145-45 | approved_entry | yes | True | 20.000000 | 1 | {'yes': 1} | 106.000000 | 17.666667 | 17.666667 | same_sign_positive |
| KXBTC15M-26MAY070945-45 | approved_entry | no | True | 28.000000 | 1 | {'no': 1} | 139.000000 | 23.166667 | 23.166667 | same_sign_positive |
