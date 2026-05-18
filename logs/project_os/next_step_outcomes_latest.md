# Research OS Next-Step Outcomes

- generated_at_utc: 2026-05-18T18:32:03Z
- registry_generated_at_utc: 2026-05-18T18:32:03Z
- research_only: True

Scope: local atlas/evidence review only. No live bot, order, threshold, secret, or state change is implied.

| Node | Kind | Family | Status | Completion | Outcome | Next Action |
|---|---|---|---|---|---|---|
| RESIDLOCK001 | candidate | rv600 | blocked | completed | local_gate_review_completed_negative_or_nonpositive | Archive residual-blend-as-is; fresh locked OOS failed hard, so do not collect more rows without a new predeclared blocker mechanism. |
| RV600NEAR001 | candidate | rv600 | blocked | completed | local_gate_review_completed | Keep frozen diagnostic, not promotable; positive P&L is too thin/concentrated and still fails sample, breadth, and matched-v28 gates. |
| RV600REV001 | candidate | rv600 | blocked | completed | local_gate_review_completed_negative_or_nonpositive | Archive or park this revision unless a newly predeclared RV600 mechanism changes the trade set; current forward economics are negative. |
| CONSENSUSLOCK001 | candidate | v28_successor | blocked | completed | local_gate_review_completed | Do not rerun unchanged; redesign the candidate to address positive_top_ev_bucket before more rows. |
| GAUSS45LOCK001 | candidate | v28_successor | blocked | completed | local_gate_review_completed | Block for insufficient markets plus benchmark failures; collect fresh locked OOS only after the mechanism changes. |
| GAUSS45LOCK002 | candidate | v28_successor | blocked | completed | local_gate_review_completed | Keep as near-miss only; require Brownian-probability improvement before any more collection. |
| GAUSS45LOCK003 | candidate | v28_successor | blocked | completed | local_gate_review_completed_negative_or_nonpositive | Archive or redesign this candidate; local OOS/forward evidence is nonpositive and failed beats_current_probability, beats_market_probability, beats_static_particle_pnl, positive_avg_pnl. |
| PSLICELOCK001 | candidate | v28_successor | blocked | completed | local_slice_oos_review_completed | Repair slice calibration and positive-market-share gates before collecting more rows. |
| PSLICELOCK002 | candidate | v28_successor | blocked | completed | local_slice_oos_review_completed | Repair slice calibration and positive-market-share gates before collecting more rows. |
| PSLICELOCK003 | candidate | v28_successor | blocked | completed | local_slice_oos_review_completed | Repair slice calibration and positive-market-share gates before collecting more rows. |
| PSLICELOCK004 | candidate | v28_successor | blocked | completed | local_slice_oos_review_completed | Block or archive this slice unless redesigned; current local OOS is negative or underpowered after fees. |
| PSLICELOCK005 | candidate | v28_successor | blocked | completed | local_slice_oos_review_completed | Block or archive this slice unless redesigned; current local OOS is negative or underpowered after fees. |
| RVTERMLOCK001 | candidate | v28_successor | blocked | completed | local_gate_review_completed | Do not rerun unchanged; redesign the candidate to address beats_current_calibrated_pnl, beats_current_probability, beats_market_probability, positive_ev_rank before more rows. |
| dynamic_particle600_next_locked_plan | candidate | v28_successor | blocked | completed | local_gate_review_completed | Do not rerun unchanged; redesign the candidate to address beats_current_calibrated_pnl, beats_current_probability, beats_market_probability, beats_static_particle_pnl before more rows. |
| dynamic_particle_next_locked_plan | candidate | v28_successor | blocked | completed | local_gate_review_completed | Do not rerun unchanged; redesign the candidate to address beats_current_calibrated_pnl before more rows. |
| side_safety_oos_next_locked_plan | candidate | v28_successor | blocked | completed | local_gate_review_completed_negative_or_nonpositive | Archive or redesign this candidate; local OOS/forward evidence is nonpositive and failed beats_base_pnl, positive_avg_pnl, positive_top_ev_bucket, positive_total_pnl. |
| Dashboard Ui | family | dashboard_ui | archived | completed | support_tooling | Keep out of strategy ranking; link only as provenance, dashboard, or infrastructure support. |
| Infrastructure | family | infrastructure | active | completed | support_tooling | Keep out of strategy ranking; link only as provenance, dashboard, or infrastructure support. |
| Legacy Live | family | legacy_live | worth_watching | completed | baseline_or_live_reference | Keep as baseline/stat reference unless one artifact is explicitly wrapped as a frozen candidate with forward validation criteria. |
| Live V28 | family | live_v28 | worth_watching | completed | baseline_or_live_reference | Keep as baseline/stat reference unless one artifact is explicitly wrapped as a frozen candidate with forward validation criteria. |
| Ninety Touch | family | ninety_touch | diagnostic_only | completed | archive_or_unscoped | Do not score as a strategy family until a named candidate and evidence chain exist. |
| Ou Mispricing | family | ou_mispricing | diagnostic_only | completed | diagnostic_or_unowned_evidence | Either freeze the strongest artifact as a named candidate with forward gates, or archive the family as diagnostic/support evidence. |
| Particle Sim | family | particle_sim | diagnostic_only | completed | diagnostic_or_unowned_evidence | Either freeze the strongest artifact as a named candidate with forward gates, or archive the family as diagnostic/support evidence. |
| Research Os | family | research_os | unknown | completed | support_tooling | Keep out of strategy ranking; link only as provenance, dashboard, or infrastructure support. |
| Rv600 | family | rv600 | blocked | completed | blocked_candidate_family | Stop sibling variants until the changed assumption is explicit; repair breadth, average entries, root/market positivity, and matched-v28 comparison before more collection. |
| Strategy Research | family | strategy_research | unknown | completed | baseline_or_live_reference | Keep as baseline/stat reference unless one artifact is explicitly wrapped as a frozen candidate with forward validation criteria. |
| Truffle | family | truffle | unknown | completed | baseline_or_live_reference | Keep as baseline/stat reference unless one artifact is explicitly wrapped as a frozen candidate with forward validation criteria. |
| V28 Successor | family | v28_successor | blocked | completed | blocked_candidate_family | Freeze sibling runs; classify OOS gate failures, then only test a pre-registered variant with a changed blocker mechanism and stats reconciliation. |
