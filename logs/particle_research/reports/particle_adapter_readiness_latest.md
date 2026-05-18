# Particle Adapter Readiness

- artifact_count: 1273
- adapter_ready_count: 0
- conclusion: No existing artifact has every required strict replay field. Best candidate is logs\edge_research\v28_continuous_scorecard_latest.json but it is missing: fee_cents, fill_prob, no_ask_cents, recv_ts_utc, settlement_price, yes_ask_cents, brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes.

## Top Artifacts

| score | ready | path | missing core | missing probability |
| ---: | --- | --- | --- | --- |
| 4 | False | `logs\edge_research\v28_continuous_scorecard_latest.json` | fee_cents, fill_prob, no_ask_cents, recv_ts_utc, settlement_price, yes_ask_cents | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 4 | False | `logs\edge_research\v28_forward_physics_registry_latest.json` | fee_cents, fill_prob, no_ask_cents, recv_ts_utc, settlement_price, yes_ask_cents | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 4 | False | `logs\edge_research\v28_forward_physics_registry_latest.csv` | fee_cents, fill_prob, no_ask_cents, recv_ts_utc, settlement_price, yes_ask_cents | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\edge_research\live_heartbeat_physics_prior_ledger_latest.csv` | decision_ts_utc, fee_cents, fill_prob, no_ask_cents, recv_ts_utc, settlement_price, yes_ask_cents | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\edge_research\v21_locked_interval_candidate_validation_ledger_latest.csv` | decision_ts_utc, fee_cents, fill_prob, no_ask_cents, recv_ts_utc, settlement_price, yes_ask_cents | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\edge_research\v21_native_passive_interval_validation_ledger_latest.csv` | decision_ts_utc, fee_cents, fill_prob, no_ask_cents, recv_ts_utc, settlement_price, yes_ask_cents | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\live_mushroom_v28_common_clock_exit_guard_sourcefix_featuregate_btcrest_size1\execution_events.ndjson` | decision_ts_utc, fee_cents, fill_prob, recv_ts_utc, settlement_price, spot, strike | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_nowindow\execution_events.ndjson` | decision_ts_utc, fee_cents, fill_prob, recv_ts_utc, settlement_price, spot, strike | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\live_mushroom_v28_feature_gate_ask65_size1\execution_events.ndjson` | decision_ts_utc, fee_cents, fill_prob, recv_ts_utc, settlement_price, spot, strike | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\live_mushroom_v28_common_clock_exit_guard_sourcefix_size1\execution_events.ndjson` | decision_ts_utc, fee_cents, fill_prob, recv_ts_utc, settlement_price, spot, strike | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_size1\execution_events.ndjson` | decision_ts_utc, fee_cents, fill_prob, recv_ts_utc, settlement_price, spot, strike | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi\execution_events.ndjson` | decision_ts_utc, fee_cents, fill_prob, recv_ts_utc, settlement_price, spot, strike | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio\execution_events.ndjson` | decision_ts_utc, fee_cents, fill_prob, recv_ts_utc, settlement_price, spot, strike | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size1\execution_events.ndjson` | decision_ts_utc, fee_cents, fill_prob, recv_ts_utc, settlement_price, spot, strike | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\live_mushroom_v28_common_clock_exit_guard_sourcefix_broad_btcrest_size1\execution_events.ndjson` | decision_ts_utc, fee_cents, fill_prob, recv_ts_utc, settlement_price, spot, strike | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\live_mushroom_v28_common_clock_exit_guard_size1\execution_events.ndjson` | decision_ts_utc, fee_cents, fill_prob, recv_ts_utc, settlement_price, spot, strike | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\live_mushroom_v28_feature_gate_size1\execution_events.ndjson` | decision_ts_utc, fee_cents, fill_prob, recv_ts_utc, settlement_price, spot, strike | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\edge_research\v21_locked_interval_candidate_validation_selected_latest.csv` | decision_ts_utc, fee_cents, fill_prob, no_ask_cents, recv_ts_utc, settlement_price, yes_ask_cents | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\edge_research\live_v28_websocket_opportunity_physics_trades_latest.csv` | decision_ts_utc, fee_cents, fill_prob, no_ask_cents, recv_ts_utc, settlement_price, yes_ask_cents | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |
| 3 | False | `logs\edge_research\v21_native_passive_interval_validation_selected_latest.csv` | decision_ts_utc, fee_cents, fill_prob, no_ask_cents, recv_ts_utc, settlement_price, yes_ask_cents | brownian_p_yes, current_calibrated_p_yes, market_p_yes, particle_p_yes |

## Field Coverage

- `decision_ts_utc`: 47
- `fee_cents`: 18
- `market_ticker`: 1273
- `no_ask_cents`: 18
- `spot`: 144
- `strike`: 136
- `yes_ask_cents`: 18
