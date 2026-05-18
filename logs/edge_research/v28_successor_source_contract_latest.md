# v28 Successor Source Contract

Research-only source-quality gate. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-18T20:51:48Z`
- Overall verdict: `promotion_grade`
- Promotion contract ready: `True`
- Required forward datasets: `['forward_registry', 'forward_labeled_predictions']`
- Required forward dataset status: `{'forward_registry': 'promotion_grade', 'forward_labeled_predictions': 'promotion_grade'}`
- Missing required forward datasets: `[]`
- Non-promotion-ready required forward datasets: `[]`
- Required forward hard blockers: `[]`
- Auxiliary hard blockers: `['boundary_geometry_complete', 'broad_market_coverage_floor', 'forward_labels_joined_after_resolution', 'forward_promotion_rows_present', 'forward_rows_not_after_the_fact', 'forward_rows_pre_resolution_registered', 'strike_fields_complete', 'target_label_present']`
- Datasets checked: `9`
- Promotion-grade datasets: `['forward_registry', 'forward_labeled_predictions']`
- Blocked datasets: `['seed_causal_rows', 'logged_event_causal_rows', 'seed_feature_table', 'logged_event_feature_table', 'passive_forward_snapshots', 'shadow_forward_labeled_rows', 'sidecar_batch_labeled_predictions']`
- Hard blockers: `['boundary_geometry_complete', 'broad_market_coverage_floor', 'forward_labels_joined_after_resolution', 'forward_promotion_rows_present', 'forward_rows_not_after_the_fact', 'forward_rows_pre_resolution_registered', 'strike_fields_complete', 'target_label_present']`

## Dataset Verdicts

| dataset | artifact type | rows | markets | status | hard failed gates |
|---|---|---:|---:|---|---|
| `seed_causal_rows` | `causal_rows` | 795 | 176 | `blocked` | `strike_fields_complete`, `boundary_geometry_complete`, `forward_promotion_rows_present`, `forward_rows_pre_resolution_registered`, `forward_rows_not_after_the_fact` |
| `logged_event_causal_rows` | `causal_rows` | 1745 | 118 | `blocked` | `forward_promotion_rows_present`, `forward_rows_pre_resolution_registered`, `forward_rows_not_after_the_fact` |
| `seed_feature_table` | `feature_table` | 795 | 176 | `blocked` | `strike_fields_complete`, `boundary_geometry_complete`, `forward_promotion_rows_present`, `forward_rows_pre_resolution_registered`, `forward_rows_not_after_the_fact` |
| `logged_event_feature_table` | `feature_table` | 1745 | 118 | `blocked` | `forward_promotion_rows_present`, `forward_rows_pre_resolution_registered`, `forward_rows_not_after_the_fact` |
| `passive_forward_snapshots` | `passive_forward_snapshots` | 1750 | 2 | `blocked` | `forward_promotion_rows_present`, `forward_rows_pre_resolution_registered`, `forward_rows_not_after_the_fact`, `broad_market_coverage_floor` |
| `shadow_forward_labeled_rows` | `shadow_forward_labeled_rows` | 1506 | 2 | `blocked` | `forward_promotion_rows_present`, `forward_rows_pre_resolution_registered`, `forward_rows_not_after_the_fact`, `broad_market_coverage_floor` |
| `forward_registry` | `forward_registry` | 16896 | 196 | `promotion_grade` |  |
| `forward_labeled_predictions` | `forward_labeled_predictions` | 16860 | 195 | `promotion_grade` |  |
| `sidecar_batch_labeled_predictions` | `forward_labeled_predictions` | 16896 | 196 | `blocked` | `target_label_present`, `forward_labels_joined_after_resolution` |

## Gate Detail

### seed_causal_rows

| gate | pass | evidence |
|---|---:|---|
| `artifact_exists` | True | path=research_particle/v28_successor/causal_rows_seed_latest.csv |
| `artifact_has_header` | True | columns=46 |
| `artifact_not_empty` | True | rows=795 |
| `identifier_fields_complete` | True | missing={'row_id': 0, 'market_ticker': 0, 'decision_ts_utc': 0, 'market_close_ts_utc': 0} |
| `pre_resolution_clock_valid` | True | checked=795 missing_or_unparseable=0 decision_after_close=0 |
| `target_label_present` | True | fields=['y_yes_win'] coverage=795/795 |
| `probability_fields_complete_and_bounded` | True | fields=['v28_p_yes', 'v28_p_no'] coverage=795/795 violations=0 |
| `fair_yes_no_cents_complete_and_sum_to_100` | True | fields=['v28_fair_yes_cents', 'v28_fair_no_cents'] coverage=795/795 sum_checked=795 sum_violations=0 |
| `strike_fields_complete` | False | fields=['strike'] coverage=0/795 |
| `boundary_geometry_complete` | False | fields=['d_sigma', 'abs_d_sigma', 'strike_distance_dollars_abs', 'distance_per_sigma_from_prices'] coverage=0/795 |
| `book_price_or_implied_price_available` | True | fields=['ask_cents', 'book_implied_yes_from_side_ask'] coverage=795/795 |
| `recross_or_path_risk_signal_available` | True | fields=['recross_hazard_score', 'h6_recross_hazard_high'] coverage=795/795 |
| `forward_promotion_rows_present` | False | forward_rows=0 total_rows=795 |
| `forward_rows_pre_resolution_registered` | False | not_registered_forward_rows=0 forward_rows=0 |
| `forward_rows_not_after_the_fact` | False | recomputed=0 backfilled=0 simulated=0 sidecar=0 diagnostic=0 posthoc=0 diagnostic_source=0 |
| `broad_market_coverage_floor` | True | rows=795 markets=176 required_rows=200 required_markets=40 |

### logged_event_causal_rows

| gate | pass | evidence |
|---|---:|---|
| `artifact_exists` | True | path=research_particle/v28_successor/causal_rows_logged_events_latest.csv |
| `artifact_has_header` | True | columns=61 |
| `artifact_not_empty` | True | rows=1745 |
| `identifier_fields_complete` | True | missing={'row_id': 0, 'market_ticker': 0, 'decision_ts_utc': 0, 'market_close_ts_utc': 0} |
| `pre_resolution_clock_valid` | True | checked=1745 missing_or_unparseable=0 decision_after_close=0 |
| `target_label_present` | True | fields=['y_yes_win'] coverage=1745/1745 |
| `probability_fields_complete_and_bounded` | True | fields=['v28_p_yes', 'v28_p_no'] coverage=1745/1745 violations=0 |
| `fair_yes_no_cents_complete_and_sum_to_100` | True | fields=['v28_fair_yes_cents', 'v28_fair_no_cents'] coverage=1745/1745 sum_checked=1745 sum_violations=0 |
| `strike_fields_complete` | True | fields=['strike'] coverage=1745/1745 |
| `boundary_geometry_complete` | True | fields=['d_sigma', 'abs_d_sigma', 'strike_distance_dollars_abs', 'distance_per_sigma_from_prices'] coverage=1745/1745 |
| `book_price_or_implied_price_available` | True | fields=['ask_cents', 'book_implied_yes_from_side_ask'] coverage=1745/1745 |
| `recross_or_path_risk_signal_available` | True | fields=['recross_hazard_score', 'h6_recross_hazard_high', 'prior_recross_seen'] coverage=1745/1745 |
| `forward_promotion_rows_present` | False | forward_rows=0 total_rows=1745 |
| `forward_rows_pre_resolution_registered` | False | not_registered_forward_rows=0 forward_rows=0 |
| `forward_rows_not_after_the_fact` | False | recomputed=0 backfilled=0 simulated=0 sidecar=0 diagnostic=0 posthoc=0 diagnostic_source=0 |
| `broad_market_coverage_floor` | True | rows=1745 markets=118 required_rows=200 required_markets=40 |

### seed_feature_table

| gate | pass | evidence |
|---|---:|---|
| `artifact_exists` | True | path=research_particle/v28_successor/features_latest.csv |
| `artifact_has_header` | True | columns=47 |
| `artifact_not_empty` | True | rows=795 |
| `identifier_fields_complete` | True | missing={'row_id': 0, 'market_ticker': 0, 'decision_ts_utc': 0, 'market_close_ts_utc': 0} |
| `pre_resolution_clock_valid` | True | checked=795 missing_or_unparseable=0 decision_after_close=0 |
| `target_label_present` | True | fields=['target_y_yes_win'] coverage=795/795 |
| `probability_fields_complete_and_bounded` | True | fields=['target_v28_p_yes'] coverage=795/795 violations=0 |
| `strike_fields_complete` | False | fields=['strike'] coverage=0/795 |
| `boundary_geometry_complete` | False | fields=['d_sigma', 'abs_d_sigma', 'strike_distance_dollars_abs', 'distance_per_sigma_from_prices'] coverage=0/795 |
| `book_price_or_implied_price_available` | True | fields=['ask_cents', 'book_implied_yes_from_side_ask'] coverage=795/795 |
| `recross_or_path_risk_signal_available` | True | fields=['recross_hazard_score', 'recross_hazard_high'] coverage=795/795 |
| `forward_promotion_rows_present` | False | forward_rows=0 total_rows=795 |
| `forward_rows_pre_resolution_registered` | False | not_registered_forward_rows=0 forward_rows=0 |
| `forward_rows_not_after_the_fact` | False | recomputed=0 backfilled=0 simulated=0 sidecar=0 diagnostic=0 posthoc=0 diagnostic_source=0 |
| `feature_manifest_exists` | True | path=research_particle/v28_successor/feature_manifest_latest.json |
| `feature_manifest_not_empty` | True | feature_count=29 |
| `feature_manifest_no_leaky_names` | True | leaky_feature_names=[] |
| `feature_manifest_no_leaky_source_columns` | True | leaky_source_columns=[] |
| `broad_market_coverage_floor` | True | rows=795 markets=176 required_rows=200 required_markets=40 |

### logged_event_feature_table

| gate | pass | evidence |
|---|---:|---|
| `artifact_exists` | True | path=research_particle/v28_successor/features_logged_events_latest.csv |
| `artifact_has_header` | True | columns=100 |
| `artifact_not_empty` | True | rows=1745 |
| `identifier_fields_complete` | True | missing={'row_id': 0, 'market_ticker': 0, 'decision_ts_utc': 0, 'market_close_ts_utc': 0} |
| `pre_resolution_clock_valid` | True | checked=1745 missing_or_unparseable=0 decision_after_close=0 |
| `target_label_present` | True | fields=['target_y_yes_win'] coverage=1745/1745 |
| `probability_fields_complete_and_bounded` | True | fields=['target_v28_p_yes'] coverage=1745/1745 violations=0 |
| `strike_fields_complete` | True | fields=['strike'] coverage=1745/1745 |
| `boundary_geometry_complete` | True | fields=['d_sigma', 'abs_d_sigma', 'strike_distance_dollars_abs', 'distance_per_sigma_from_prices'] coverage=1745/1745 |
| `book_price_or_implied_price_available` | True | fields=['ask_cents', 'book_implied_yes_from_side_ask'] coverage=1745/1745 |
| `recross_or_path_risk_signal_available` | True | fields=['recross_hazard_score', 'recross_hazard_high', 'prior_recross_seen'] coverage=1745/1745 |
| `forward_promotion_rows_present` | False | forward_rows=0 total_rows=1745 |
| `forward_rows_pre_resolution_registered` | False | not_registered_forward_rows=0 forward_rows=0 |
| `forward_rows_not_after_the_fact` | False | recomputed=0 backfilled=0 simulated=0 sidecar=0 diagnostic=0 posthoc=0 diagnostic_source=0 |
| `feature_manifest_exists` | True | path=research_particle/v28_successor/feature_manifest_logged_events_latest.json |
| `feature_manifest_not_empty` | True | feature_count=78 |
| `feature_manifest_no_leaky_names` | True | leaky_feature_names=[] |
| `feature_manifest_no_leaky_source_columns` | True | leaky_source_columns=[] |
| `broad_market_coverage_floor` | True | rows=1745 markets=118 required_rows=200 required_markets=40 |

### passive_forward_snapshots

| gate | pass | evidence |
|---|---:|---|
| `artifact_exists` | True | path=research_particle/v28_successor/passive_forward_snapshots_latest.csv |
| `artifact_has_header` | True | columns=52 |
| `artifact_not_empty` | True | rows=1750 |
| `identifier_fields_complete` | True | missing={'row_id': 0, 'market_ticker': 0, 'decision_ts_utc': 0, 'market_close_ts_utc': 0} |
| `pre_resolution_clock_valid` | True | checked=1750 missing_or_unparseable=0 decision_after_close=0 |
| `target_label_present` | True | fields=[] coverage=1750/1750 |
| `probability_fields_complete_and_bounded` | True | fields=[] coverage=1750/1750 violations=0 |
| `strike_fields_complete` | True | fields=['strike'] coverage=1750/1750 |
| `book_price_or_implied_price_available` | True | fields=['ask_cents', 'book_implied_yes_from_side_ask'] coverage=1686/1750 |
| `forward_promotion_rows_present` | False | forward_rows=0 total_rows=1750 |
| `forward_rows_pre_resolution_registered` | False | not_registered_forward_rows=0 forward_rows=0 |
| `forward_rows_not_after_the_fact` | False | recomputed=0 backfilled=0 simulated=0 sidecar=0 diagnostic=0 posthoc=0 diagnostic_source=0 |
| `broad_market_coverage_floor` | False | rows=1750 markets=2 required_rows=200 required_markets=40 |

### shadow_forward_labeled_rows

| gate | pass | evidence |
|---|---:|---|
| `artifact_exists` | True | path=research_particle/v28_successor/shadow_forward_labeled_rows_latest.csv |
| `artifact_has_header` | True | columns=111 |
| `artifact_not_empty` | True | rows=1506 |
| `identifier_fields_complete` | True | missing={'row_id': 0, 'market_ticker': 0, 'decision_ts_utc': 0, 'market_close_ts_utc': 0} |
| `pre_resolution_clock_valid` | True | checked=1506 missing_or_unparseable=0 decision_after_close=0 |
| `target_label_present` | True | fields=['y_yes_win'] coverage=1506/1506 |
| `probability_fields_complete_and_bounded` | True | fields=['v28_p_yes', 'candidate_p_yes'] coverage=1506/1506 violations=0 |
| `fair_yes_no_cents_complete_and_sum_to_100` | True | fields=['candidate_fair_yes_cents', 'candidate_fair_no_cents'] coverage=1506/1506 sum_checked=1506 sum_violations=0 |
| `strike_fields_complete` | True | fields=['strike'] coverage=1506/1506 |
| `boundary_geometry_complete` | True | fields=['v28_d_sigma', 'abs_v28_d_sigma', 'strike_distance_dollars_abs'] coverage=1506/1506 |
| `book_price_or_implied_price_available` | True | fields=['ask_cents', 'book_implied_yes_from_side_ask'] coverage=1506/1506 |
| `recross_or_path_risk_signal_available` | True | fields=['recross_hazard_score', 'max_adverse_move_3m'] coverage=1506/1506 |
| `forward_promotion_rows_present` | False | forward_rows=0 total_rows=1506 |
| `forward_rows_pre_resolution_registered` | False | not_registered_forward_rows=0 forward_rows=0 |
| `forward_rows_not_after_the_fact` | False | recomputed=0 backfilled=0 simulated=0 sidecar=0 diagnostic=0 posthoc=0 diagnostic_source=0 |
| `broad_market_coverage_floor` | False | rows=1506 markets=2 required_rows=200 required_markets=40 |

### forward_registry

| gate | pass | evidence |
|---|---:|---|
| `artifact_exists` | True | path=research_particle/v28_successor/forward_registry_latest.csv |
| `artifact_has_header` | True | columns=27 |
| `identifier_fields_complete` | True | missing={'row_id': 0, 'market_ticker': 0, 'decision_ts_utc': 0} |
| `probability_fields_complete_and_bounded` | True | fields=['candidate_p_yes', 'v28_p_yes'] coverage=16896/16896 violations=0 |
| `fair_yes_no_cents_complete_and_sum_to_100` | True | fields=['candidate_fair_yes_cents', 'candidate_fair_no_cents'] coverage=16896/16896 sum_checked=16896 sum_violations=0 |
| `book_price_or_implied_price_available` | True | fields=['ask_cents'] coverage=16896/16896 |
| `forward_registry_not_empty` | True | rows=16896 registry_status=active |
| `forward_registry_min_rows` | True | rows=16896 required_rows=200 |
| `forward_registry_min_markets` | True | markets=196 required_markets=40 |
| `forward_registry_promotion_ready` | True | promotion_ready=True registry_status=active |
| `forward_registry_from_frozen_predictions` | True | non_frozen_source_rows=0 rows=16896 |
| `forward_registry_frozen_before_close` | True | missing_or_unparseable_freeze_clock=0 freeze_after_close=0 rows=16896 |
| `forward_registry_unique_frozen_predictions` | True | registry_ids=16896/16896 duplicates=0 frozen_prediction_ids=16896/16896 duplicates=0 |
| `broad_market_coverage_floor` | True | rows=16896 markets=196 required_rows=200 required_markets=40 |

### forward_labeled_predictions

| gate | pass | evidence |
|---|---:|---|
| `artifact_exists` | True | path=research_particle/v28_successor/forward_labeled_predictions_latest.csv |
| `artifact_has_header` | True | columns=55 |
| `artifact_not_empty` | True | rows=16860 |
| `identifier_fields_complete` | True | missing={'row_id': 0, 'market_ticker': 0, 'decision_ts_utc': 0, 'market_close_ts_utc': 0} |
| `pre_resolution_clock_valid` | True | checked=16860 missing_or_unparseable=0 decision_after_close=0 |
| `target_label_present` | True | fields=['y_yes_win'] coverage=16860/16860 |
| `probability_fields_complete_and_bounded` | True | fields=['candidate_p_yes', 'v28_p_yes'] coverage=16860/16860 violations=0 |
| `fair_yes_no_cents_complete_and_sum_to_100` | True | fields=['candidate_fair_yes_cents', 'candidate_fair_no_cents'] coverage=16860/16860 sum_checked=16860 sum_violations=0 |
| `strike_fields_complete` | True | fields=['strike'] coverage=16860/16860 |
| `boundary_geometry_complete` | True | fields=['v28_d_sigma'] coverage=16860/16860 |
| `book_price_or_implied_price_available` | True | fields=['ask_cents', 'book_implied_yes_from_side_ask'] coverage=16860/16860 |
| `recross_or_path_risk_signal_available` | True | fields=['v28_sigma_t_dollars'] coverage=16860/16860 |
| `forward_labeled_rows_present` | True | joined_rows=16860 total_rows=16860 |
| `forward_labeled_min_rows` | True | joined_rows=16860 required_rows=200 |
| `forward_labeled_min_markets` | True | joined_markets=195 required_markets=40 |
| `forward_labels_joined_after_resolution` | True | blocked_join_rows=0 joined_rows=16860 |
| `forward_labels_from_frozen_predictions` | True | non_frozen_source_rows=0 joined_rows=16860 |
| `forward_labels_frozen_before_close` | True | missing_or_unparseable_freeze_clock=0 freeze_after_close=0 joined_rows=16860 |
| `broad_market_coverage_floor` | True | rows=16860 markets=195 required_rows=200 required_markets=40 |

### sidecar_batch_labeled_predictions

| gate | pass | evidence |
|---|---:|---|
| `artifact_exists` | True | path=research_particle/v28_successor/sidecar_bundle_batch_labeled_latest.csv |
| `artifact_has_header` | True | columns=55 |
| `artifact_not_empty` | True | rows=16896 |
| `identifier_fields_complete` | True | missing={'row_id': 0, 'market_ticker': 0, 'decision_ts_utc': 0, 'market_close_ts_utc': 0} |
| `pre_resolution_clock_valid` | True | checked=16896 missing_or_unparseable=0 decision_after_close=0 |
| `target_label_present` | False | fields=['y_yes_win'] coverage=16860/16896 |
| `probability_fields_complete_and_bounded` | True | fields=['candidate_p_yes', 'v28_p_yes'] coverage=16896/16896 violations=0 |
| `fair_yes_no_cents_complete_and_sum_to_100` | True | fields=['candidate_fair_yes_cents', 'candidate_fair_no_cents'] coverage=16896/16896 sum_checked=16896 sum_violations=0 |
| `strike_fields_complete` | True | fields=['strike'] coverage=16896/16896 |
| `boundary_geometry_complete` | True | fields=['v28_d_sigma'] coverage=16896/16896 |
| `book_price_or_implied_price_available` | True | fields=['ask_cents', 'book_implied_yes_from_side_ask'] coverage=16896/16896 |
| `recross_or_path_risk_signal_available` | True | fields=['v28_sigma_t_dollars'] coverage=16896/16896 |
| `forward_labeled_rows_present` | True | joined_rows=16860 total_rows=16896 |
| `forward_labeled_min_rows` | True | joined_rows=16860 required_rows=200 |
| `forward_labeled_min_markets` | True | joined_markets=195 required_markets=40 |
| `forward_labels_joined_after_resolution` | False | blocked_join_rows=36 joined_rows=16860 |
| `forward_labels_from_frozen_predictions` | True | non_frozen_source_rows=0 joined_rows=16860 |
| `forward_labels_frozen_before_close` | True | missing_or_unparseable_freeze_clock=0 freeze_after_close=0 joined_rows=16860 |
| `broad_market_coverage_floor` | True | rows=16896 markets=196 required_rows=200 required_markets=40 |

## Read

- A dataset is promotion grade only when every hard gate passes at once.
- Current seed/logged-event artifacts can support diagnostics, but they remain blocked for promotion because no rows are frozen forward evidence.
- Feature manifests are checked separately so target/outcome columns cannot enter the modeled feature surface.
