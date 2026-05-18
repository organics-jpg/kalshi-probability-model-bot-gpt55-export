# Goal Completion Audit

Generated UTC: `20260505_021859Z`

## Objective Restatement

- Build a BTC 15m Kalshi fair-value/probability model with high accuracy and positive EV.
- Maintain roughly 75-80%+ recurring-market coverage.
- Use strict pre-registered live forward evidence with enough sample size.
- Avoid validation-visible overfit and require cross-split/cross-dataset robustness for new physics priors.
- Do not modify live bot logic, stop the live bot, or place trades.

## Prompt-to-Artifact Checklist

| requirement | evidence artifact | current evidence | status |
|---|---|---|---|
| Strict pre-registered proof | `logs\edge_research\profit_lock_registered_signal_readiness_latest.csv` | strict promotable rows: 0 | fail |
| High recurring-market coverage | `logs\edge_research\profit_lock_market_denominator_audit_latest.csv` | coverage-fail rows: 12; top positive rows checked below | mixed |
| Bayesian confidence | `logs\edge_research\profit_lock_bayesian_ev_monitor_latest.csv` | no row clears readiness because strict promotable rows are 0 | fail |
| Wilson/sample-size proof | `logs\edge_research\profit_lock_sample_size_requirements_latest.csv` | no row clears completion-ready gate | fail |
| Forward registry current | `logs\edge_research\profit_lock_pending_signal_registry_latest.csv` | registry rows: 2973; pending: 5 | pass |
| Overfit controls | robustness reports listed below | no robust scan is promotion evidence without fresh strict validation | fail |
| Live safety | process/error checks in thread | live bot/recorder/collector observed running; no trades submitted by these probes | pass |

## Top Strict Rows

| lock | reg/res/pending | wins/losses | acc | break-even | Wilson low | P(p>BE) | p05 edge | coverage | net | ready |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `kinetic_combo_price_guard` | 100/100/0 | 67/33 | 67.00% | 65.08% | 57.31% | 0.642 | -6.3c | 63.69% | 192.0c | False/False |
| `book_margin` | 103/103/0 | 72/31 | 69.90% | 68.21% | 60.46% | 0.626 | -6.2c | 96.26% | 174.0c | False/False |
| `book_margin_early` | 99/99/0 | 69/30 | 69.70% | 68.24% | 60.05% | 0.602 | -6.6c | 96.12% | 144.0c | False/False |
| `challenger` | 128/128/0 | 87/41 | 67.97% | 66.86% | 59.46% | 0.586 | -6.1c | 64.32% | 142.0c | False/False |
| `touch_overlay` | 136/135/1 | 82/53 | 60.74% | 59.92% | 52.32% | 0.568 | -6.3c | 71.96% | 111.0c | False/False |
| `original` | 136/136/0 | 91/45 | 66.91% | 66.20% | 58.63% | 0.553 | -6.3c | 68.00% | 97.0c | False/False |
| `logit_blend_edge10` | 73/73/0 | 46/27 | 63.01% | 61.88% | 51.55% | 0.564 | -8.5c | 94.81% | 83.0c | False/False |
| `book_margin_gap015` | 88/88/0 | 60/28 | 68.18% | 67.35% | 57.87% | 0.543 | -7.9c | 87.13% | 73.0c | False/False |

## Robustness Reports

| report | exists | read |
|---|---|---|
| `logs\edge_research\market_interval_80coverage_latest.md` | True | diagnostic only |
| `logs\edge_research\cross_dataset_profit_frontier_latest.md` | True | diagnostic only |
| `logs\edge_research\brownian70_candidate_robustness_audit_latest.md` | True | diagnostic only |
| `logs\edge_research\book_brownian_arbitration_audit_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\book_edge_gate_robustness_audit_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\book_cost_score_hole_audit_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\score_physics_guard_audit_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\signed_momentum_exhaustion_guard_audit_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\previous_outcome_state_guard_audit_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\vol_term_structure_guard_audit_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\probability_rolling_online_audit_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\probability_calibration_audit_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\probability_multifeature_logit_audit_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\frontier_candidate_v2_diagnostic_latest.md` | True | diagnostic only |
| `logs\edge_research\book_refmargin_score_switch_robustness_audit_latest.md` | True | diagnostic only |
| `logs\edge_research\book_margin_time_window_stability_scan_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\temporal_side_flip_diagnostic_latest.md` | True | diagnostic only |
| `logs\edge_research\hazard_mean_touch80_robustness_audit_latest.md` | True | diagnostic only |
| `logs\edge_research\hazard_pricecap_granular_frontier_latest.md` | True | diagnostic only |
| `logs\edge_research\hazard_trigger_persistence_frontier_latest.md` | True | diagnostic only |
| `logs\edge_research\impulse_reversal_regime_frontier_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\hazard_causal_threshold_stability_scan_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\hazard_primary_timeband_stability_scan_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\hazard_price_cap_stability_scan_latest.md` | True | rejects promotion under robustness gates |
| `logs\edge_research\logit_blend_threshold_robustness_audit_latest.md` | True | diagnostic only |
| `logs\edge_research\hazard_fallback_robustness_audit_latest.md` | True | diagnostic only |

## Completion Decision

- Not complete: no strict pre-registered row clears the promotion gates.
- Continue collecting forward samples and only lock new candidates after robustness evidence improves.
