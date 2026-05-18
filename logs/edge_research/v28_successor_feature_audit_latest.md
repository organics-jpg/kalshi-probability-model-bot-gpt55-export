# v28 Successor Feature Audit

Research-only feature artifact for the v28 successor FV pipeline. This script reads the seed dataset and writes model-ready features plus a manifest; it does not touch live bot state or processes.

## Summary

- Created UTC: `2026-05-12T07:29:17Z`
- Builder: `build_v28_successor_features.py`
- Input rows: `research_particle/v28_successor/causal_rows_seed_latest.csv`
- Input row hash: `fb9f4a1a5e09f84839d84adfd317855f8e62ae11cfc1ef87e971a4ff2c884d2b`
- Rows: `795`
- Feature rows: `795`
- Features: `29`
- Feature manifest hash: `a58dc512780c61f24226431e`

## Track Coverage

| track | feature count |
|---|---:|
| book_aware | 27 |
| pure_physics | 20 |
| reliability | 26 |

## Source Rows

| source | rows |
|---|---:|
| entry | 173 |
| rejected_actionable | 622 |

## Leakage Audit

- Status: `pass`
- Target columns are included for scoring joins but are not in the feature manifest.
- P&L/gross, Brier, logloss, settlement, outcome, and win/result columns are excluded from feature columns.
- Book-aware execution features are isolated to the book_aware track.
- All features in this first seed inherit the posthoc source caveat from the seed rows.

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

## Missing Feature Values

| feature | missing values |
|---|---:|
| `v28_logit_yes` | 0 |
| `v28_p_yes_centered` | 0 |
| `v28_abs_logit_yes` | 0 |
| `v28_side_probability` | 0 |
| `seconds_to_close` | 0 |
| `minutes_to_close` | 0 |
| `time_frac_15m` | 0 |
| `late_window_lte_180s` | 0 |
| `final_avg_effective_horizon_minutes` | 0 |
| `final_avg_variance_compression` | 0 |
| `final_avg_uncertainty_scale` | 0 |
| `final_avg_elapsed_window_fraction` | 0 |
| `final_avg_sigma_proxy_dollars` | 0 |
| `final_avg_d_sigma_proxy` | 0 |
| `final_avg_abs_d_sigma_proxy` | 0 |
| `sigma_t_dollars` | 0 |
| `log1p_sigma_t_dollars` | 0 |
| `sigma_t_missing` | 0 |
| `recross_hazard_score` | 0 |
| `recross_hazard_missing` | 0 |
| `recross_hazard_high` | 0 |
| `ask_cents` | 0 |
| `ask_missing` | 0 |
| `ask_frac` | 0 |
| `edge_cents` | 0 |
| `edge_missing` | 0 |
| `side_is_yes` | 0 |
| `source_is_entry` | 0 |
| `source_is_rejected_actionable` | 0 |

## Read

- This feature table is suitable for smoke-test calibration work only; the underlying seed rows remain posthoc diagnostic rows.
- The manifest cleanly separates pure-physics, book-aware, and reliability features.
- No feature names or source columns include settlement/outcome/P&L/Brier/logloss/win/result fields.
