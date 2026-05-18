# v28 Successor Logged Event Feature Audit

Research-only logged-event feature artifact. It does not touch live bot state, orders, thresholds, or processes.

## Summary

- Created UTC: `2026-05-12T07:29:18Z`
- Input rows: `research_particle/v28_successor/causal_rows_logged_events_latest.csv`
- Input hash: `59ca630ce2eb4be8fe8db8143403382026411079a58250ebbd21914ae4d6193f`
- Rows: `1745`
- Markets: `118`
- Features: `78`
- Feature manifest hash: `03d1ec494e707394a3d8c39e`
- Forward-promotion rows: `0`
- v28 API replay rows joined: `1745`

## Track Coverage

| track | feature count |
|---|---:|
| book_aware | 63 |
| pure_physics | 49 |
| reliability | 74 |

## Source Rows

| source | rows |
|---|---:|
| execution_deferred | 197 |
| fill_full | 251 |
| fill_partial | 2 |
| mushroom_v28_approved | 450 |
| plan_built | 395 |
| signal_seen | 450 |

## Leakage Audit

- Status: `pass`
- Logged v28 outputs are used as features only when they were emitted before event resolution.
- Labels are included as target columns for scoring joins but not in the feature manifest.
- Rows remain diagnostic-only because labels are sourced from posthoc seed market outcomes.

## Feature Manifest

| feature | family | tracks | source columns | leakage risk | transform |
|---|---|---|---|---|---|
| `v28_logit_yes` | v28_derived | pure_physics, book_aware, reliability | v28_p_yes | low | logit(clamp(v28_p_yes)) |
| `v28_p_yes_centered` | v28_derived | pure_physics, book_aware, reliability | v28_p_yes | low | v28_p_yes - 0.5 |
| `v28_abs_logit_yes` | v28_derived | pure_physics, book_aware, reliability | v28_p_yes | low | abs(logit(clamp(v28_p_yes))) |
| `v28_side_probability` | v28_derived | book_aware, reliability | v28_p_side | medium | clamp(v28_p_side) |
| `seconds_to_close` | time_geometry | pure_physics, book_aware, reliability | seconds_to_close | low | float(seconds_to_close) |
| `minutes_to_close` | time_geometry | pure_physics, book_aware, reliability | seconds_to_close | low | seconds_to_close / 60 |
| `time_frac_15m` | time_geometry | pure_physics, book_aware, reliability | seconds_to_close | low | clip(seconds_to_close / 900, 0, 1) |
| `late_window_lte_180s` | time_geometry | pure_physics, book_aware, reliability | seconds_to_close | low | 1 if seconds_to_close <= 180 and present else 0 |
| `final_avg_effective_horizon_minutes` | final_avg_physics | pure_physics, book_aware, reliability | seconds_to_close | low | if h >= avg: h - 2avg/3 else h^3/(3avg^2), avg=90s |
| `final_avg_variance_compression` | final_avg_physics | pure_physics, book_aware, reliability | seconds_to_close | low | effective final-average horizon / raw horizon, clipped to [0, 1] |
| `final_avg_uncertainty_scale` | final_avg_physics | pure_physics, book_aware, reliability | seconds_to_close | low | sqrt(final_avg_variance_compression) |
| `final_avg_elapsed_window_fraction` | final_avg_physics | pure_physics, book_aware, reliability | seconds_to_close | low | clip((90s - seconds_to_close) / 90s, 0, 1) |
| `final_avg_sigma_proxy_dollars` | final_avg_physics | pure_physics, book_aware, reliability | seconds_to_close, sigma_t_dollars | low | sigma_t_dollars * final_avg_uncertainty_scale |
| `final_avg_d_sigma_proxy` | final_avg_physics | pure_physics, book_aware, reliability | seconds_to_close, sigma_t_dollars, strike, btc_price | low | (strike - btc_price) / final_avg_sigma_proxy_dollars |
| `final_avg_abs_d_sigma_proxy` | final_avg_physics | pure_physics, book_aware, reliability | seconds_to_close, sigma_t_dollars, strike, btc_price | low | abs(final_avg_d_sigma_proxy) |
| `sigma_t_dollars` | v28_derived | pure_physics, book_aware, reliability | sigma_t_dollars | low | float(sigma_t_dollars) |
| `log1p_sigma_t_dollars` | v28_derived | pure_physics, book_aware, reliability | sigma_t_dollars | low | log1p(max(sigma_t_dollars, 0)) |
| `sigma_t_missing` | missingness | pure_physics, book_aware, reliability | sigma_t_dollars | low | 1 if sigma_t_dollars missing else 0 |
| `recross_hazard_score` | boundary_reliability | pure_physics, book_aware, reliability | recross_hazard_score | medium | float(recross_hazard_score) |
| `recross_hazard_missing` | missingness | pure_physics, book_aware, reliability | recross_hazard_score | low | 1 if recross_hazard_score missing else 0 |
| `recross_hazard_high` | boundary_reliability | pure_physics, book_aware, reliability | h6_recross_hazard_high | medium | 1 if h6_recross_hazard_high true else 0 |
| `ask_cents` | book_aware_execution | book_aware | ask_cents | medium | float(ask_cents), missing=>100 |
| `ask_missing` | missingness | book_aware, reliability | ask_cents | low | 1 if ask_cents missing else 0 |
| `ask_frac` | book_aware_execution | book_aware | ask_cents | medium | ask_cents / 100 |
| `edge_cents` | book_aware_execution | book_aware | edge_cents | medium | float(edge_cents) |
| `edge_missing` | missingness | book_aware, reliability | edge_cents | low | 1 if edge_cents missing else 0 |
| `side_is_yes` | row_context | book_aware, reliability | side | low | 1 if side == yes else 0 |
| `source_is_entry` | source_reliability | reliability | source_type | low | 1 if source_type == entry else 0 |
| `source_is_rejected_actionable` | source_reliability | reliability | source_type | low | 1 if source_type == rejected_actionable else 0 |
| `v28_api_replay_available` | v28_api_replay | pure_physics, reliability | api_replay_available | medium | 1 if reconstructed v28 API replay is available for this row |
| `v28_api_replay_p_anchor` | v28_api_replay | pure_physics, book_aware, reliability | replay_p_anchor | medium | clamped replay p_anchor |
| `v28_api_replay_p_static_boundary_field` | v28_api_replay | pure_physics, book_aware, reliability | replay_p_static_boundary_field | medium | clamped replay p_static_boundary_field |
| `v28_api_replay_p_recent_transport` | v28_api_replay | pure_physics, book_aware, reliability | replay_p_recent_transport | medium | clamped replay p_recent_transport |
| `v28_api_replay_p_long_transport` | v28_api_replay | pure_physics, book_aware, reliability | replay_p_long_transport | medium | clamped replay p_long_transport |
| `v28_api_replay_edge_gate` | v28_api_replay | pure_physics, reliability | replay_edge_gate | medium | clamped replay transport edge gate |
| `v28_api_replay_static_gate` | v28_api_replay | pure_physics, reliability | replay_static_gate | medium | clamped replay static boundary gate |
| `log1p_v28_api_replay_transport_recent_n` | v28_api_replay | pure_physics, reliability | replay_transport_recent_n | medium | log1p(replay transport recent sample count) |
| `log1p_v28_api_replay_transport_long_n` | v28_api_replay | pure_physics, reliability | replay_transport_long_n | medium | log1p(replay transport long sample count) |
| `v28_api_replay_minus_logged_p_yes` | v28_api_replay | reliability | replay_minus_logged_v28_p_yes | medium | replay p_yes minus originally logged p_yes |
| `v28_api_replay_abs_p_delta` | v28_api_replay | reliability | replay_minus_logged_v28_p_yes | medium | abs(replay p_yes minus originally logged p_yes) |
| `v28_api_replay_minus_logged_sigma` | v28_api_replay | reliability | replay_minus_logged_sigma_t_dollars | medium | replay sigma_t minus originally logged sigma_t |
| `v28_api_replay_minus_logged_d_sigma` | v28_api_replay | reliability | replay_minus_logged_d_sigma | medium | replay d_sigma minus originally logged d_sigma |
| `d_sigma` | boundary_geometry | pure_physics, book_aware, reliability | d_sigma | low | float(d_sigma) |
| `abs_d_sigma` | boundary_geometry | pure_physics, book_aware, reliability | abs_d_sigma, d_sigma | low | abs_d_sigma if present else abs(d_sigma) |
| `d_sigma_missing` | missingness | pure_physics, book_aware, reliability | d_sigma | low | 1 if d_sigma missing else 0 |
| `boundary_zone_abs_d_lte_1` | boundary_geometry | pure_physics, book_aware, reliability | abs_d_sigma, d_sigma | low | 1 if abs_d_sigma <= 1 else 0 |
| `strike_minus_btc_dollars` | boundary_geometry | pure_physics, book_aware, reliability | strike, btc_price | low | strike - btc_price |
| `strike_distance_dollars_abs` | boundary_geometry | pure_physics, book_aware, reliability | strike, btc_price | low | abs(strike - btc_price) |
| `distance_per_sigma_from_prices` | boundary_geometry | pure_physics, book_aware, reliability | strike, btc_price, sigma_t_dollars | low | (strike - btc_price) / sigma_t_dollars |
| `strike_missing` | missingness | pure_physics, book_aware, reliability | strike | low | 1 if strike missing else 0 |
| `btc_price_missing` | missingness | pure_physics, book_aware, reliability | btc_price | low | 1 if btc_price missing else 0 |
| `arrow` | v28_derived | pure_physics, book_aware, reliability | arrow | low | float(arrow) |
| `arrow_x_d_sigma` | v28_derived | pure_physics, book_aware, reliability | arrow, d_sigma | low | arrow * d_sigma |
| `btc_age_ms` | feed_freshness | book_aware, reliability | btc_age_ms | low | float(btc_age_ms) |
| `book_age_ms` | feed_freshness | book_aware, reliability | book_age_ms | low | float(book_age_ms) |
| `feed_age_ms` | feed_freshness | book_aware, reliability | feed_age_ms | low | float(feed_age_ms) |
| `freshness_max_age_ms` | feed_freshness | book_aware, reliability | btc_age_ms, book_age_ms, feed_age_ms | low | max(btc_age_ms, book_age_ms, feed_age_ms) |
| `log1p_freshness_max_age_ms` | feed_freshness | book_aware, reliability | btc_age_ms, book_age_ms, feed_age_ms | low | log1p(max_age_ms) |
| `btc_age_missing` | missingness | book_aware, reliability | btc_age_ms | low | 1 if btc_age_ms missing else 0 |
| `book_age_missing` | missingness | book_aware, reliability | book_age_ms | low | 1 if book_age_ms missing else 0 |
| `freshness_gt_1000ms` | feed_freshness | book_aware, reliability | btc_age_ms, book_age_ms, feed_age_ms | low | 1 if max_age_ms > 1000 else 0 |
| `book_implied_yes_from_side_ask` | book_aware_execution | book_aware | ask_cents, side | medium | YES ask / 100 for YES side, 1 - NO ask / 100 for NO side |
| `v28_minus_book_implied_yes` | book_aware_execution | book_aware, reliability | v28_p_yes, ask_cents, side | medium | v28_p_yes - book_implied_yes_from_side_ask |
| `v28_book_disagreement_abs` | book_aware_execution | book_aware, reliability | v28_p_yes, ask_cents, side | medium | abs(v28_p_yes - book_implied_yes) |
| `history_bars_log1p` | source_reliability | reliability | history_bars | low | log1p(history_bars) |
| `prior_logged_event_count` | path_memory | pure_physics, book_aware, reliability | prior_logged_event_count | low | count of prior logged rows for this market |
| `log1p_prior_logged_event_count` | path_memory | pure_physics, book_aware, reliability | prior_logged_event_count | low | log1p(prior_logged_event_count) |
| `btc_drift_from_prev_event_dollars` | short_term_drift | pure_physics, book_aware, reliability | btc_drift_from_prev_event_dollars | low | current btc - prior event btc |
| `btc_drift_from_first_event_dollars` | short_term_drift | pure_physics, book_aware, reliability | btc_drift_from_first_event_dollars | low | current btc - first market event btc |
| `prior_btc_path_range_dollars` | realized_vol_regime | pure_physics, book_aware, reliability | prior_btc_path_range_dollars | low | prior max btc - prior min btc |
| `prior_btc_path_range_per_sigma` | realized_vol_regime | pure_physics, book_aware, reliability | prior_btc_path_range_per_sigma | low | prior path range / sigma_t |
| `prior_adverse_path_memory_dollars` | adverse_path_memory | pure_physics, book_aware, reliability | prior_adverse_path_memory_dollars | low | YES: max(0, strike-prior_min_btc); NO: max(0, prior_max_btc-strike) |
| `prior_adverse_path_memory_per_sigma` | adverse_path_memory | pure_physics, book_aware, reliability | prior_adverse_path_memory_per_sigma | low | prior adverse path memory / sigma_t |
| `prior_recross_seen` | recross_hazard | pure_physics, book_aware, reliability | prior_recross_seen | low | 1 if prior min btc <= strike <= prior max btc else 0 |
| `btc_event_dt_seconds` | feed_freshness | book_aware, reliability | btc_event_dt_seconds | low | decision_ts - previous same-market event ts |
| `source_is_logged_approved` | source_reliability | reliability | source_type | low | 1 if source_type == mushroom_v28_approved else 0 |
| `source_is_signal_seen` | source_reliability | reliability | source_type | low | 1 if source_type == signal_seen else 0 |
| `source_is_plan_built` | source_reliability | reliability | source_type | low | 1 if source_type == plan_built else 0 |

## Read

- This feature set adds true logged boundary geometry, strike/BTC distance, arrow, freshness, book-v28 disagreement proxies, and research-only v28 API replay components.
- It remains diagnostic-only because there are no frozen-forward rows.
- Promotion gates must remain closed for any candidate trained on these features.
