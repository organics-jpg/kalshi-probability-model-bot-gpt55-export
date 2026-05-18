# RV600 Goal Completion Audit

- generated_utc: 2026-05-15T21:22:01+00:00
- goal_complete: False
- best_locked_candidate: rv600_primary_max_3_entries_mid_120_420_ev12
- locked_candidate_count: 5
- status_counts: {'pass': 10, 'partial': 0, 'fail': 3}
- conclusion: RV600 objective is not complete. Retrospective locked candidate rv600_primary_max_3_entries_mid_120_420_ev12 is available, but remaining blockers are: Incoming live markets are moderately validated in shadow mode; Forward-shadow evidence is not only sparse sidecar or fallback-vol artifacts; Forward-shadow PnL is positive and passes the same artifact checks. Current forward-shadow sample is 15 entries, 15 markets, 1 calendar days, 0 weekend days.

## Forward Shadow Sample

- accepted_entries: 15
- distinct_markets: 15
- calendar_days: 1
- weekend_days: 0
- selected_pnl_cents: -155.3
- matched_v28_control_pnl_cents: -148.2
- latest_root_update: 2026-05-15T17:54:56+00:00
- native_candidate_rows: 7584
- sidecar_candidate_rows: 4
- source_quality_note: forward report mixes native and sidecar evidence; completion should rely on native continuous rows

## Checklist

| status | requirement | evidence | next action |
|---|---|---|---|
| pass | Named RV600 variation plan exists and is the source of truth | plan=docs\research\RV600_VARIATION_TEST_PLAN.md exists=True | Restore or write the RV600 variation plan before auditing implementation. |
| pass | Research-only implementation path exists; no live launcher/v28 order logic is required | harness=research_particle\rv600_variation_test.py exists=True; locked_note=docs\research\RV600_LOCKED_CANDIDATES_2026-05-13.md exists=True; audit probe is read/report only | Keep RV600 work in research reports and shadow scoring; do not edit live launchers or order logic. |
| pass | First candidate set from the plan was built and scored | report=logs\particle_research\reports\rv600_variation_test_latest.json phase=first_candidates; variant_count=6; root_count=10 | Run `python -m research_particle.rv600_variation_test --phase first_candidates --write`. |
| pass | Phase 1 grid explored timing, EV, repeated-entry, side/control/regime/micro/price variants | report=logs\particle_research\reports\rv600_variation_grid_latest.json phase=grid; variant_count=3948; root_count=10 | Run the grid phase and inspect rejected high-PnL rows with gate reasons. |
| pass | Locked Phase 2 candidate set contains at most five simple candidates | report=logs\particle_research\reports\rv600_variation_locked_latest.json phase=locked; locked_candidate_count=5; candidates=['rv600_primary_max_3_entries_mid_120_420_ev12', 'rv600_primary_max_3_entries_base_70_420_ev12', 'rv600_primary_risk_cap_200c_mid_120_420_ev12', 'rv600_primary_risk_cap_200c_base_70_420_ev12', 'rv600_primary_max_2_entries_mid_120_420_ev12'] | Freeze at most five simple candidates from the grid before any forward-shadow scoring. |
| pass | Fair repeated-entry accounting is present for all_entries, one_per_side_per_market, and position_capped | accounting_modes=['all_entries', 'one_per_side_per_market', 'position_capped'] | Extend the report to emit all three repeated-entry accounting modes. |
| pass | Best locked candidate is profitable after fees/fills and not only profitable under all_entries | variant=rv600_primary_max_3_entries_mid_120_420_ev12; accounting=position_capped; selected_pnl_cents=1317.0; fill_adjusted_expected_pnl_cents=1042.9523419142793 | Keep the candidate research-only until non-all_entries accounting remains positive. |
| pass | Matched v28/current control is scored on the same accepted timestamps and beaten by at least 20% | selected_pnl_cents=1317.0; matched_v28_control_pnl_cents=1029.0; matched_v28_delta_cents=288.0 | Keep matched timestamp controls in every locked and forward-shadow report. |
| pass | Anti-overfitting gates pass retrospectively: roots/markets, recent window, concentration, added entries | positive_root_rate=0.8; positive_market_rate=0.6153846153846154; max_single_market_pnl_share=0.2034927866362946; last_window_pnl_cents=113.0; avg_added_entry_pnl_cents=16.545454545454547; rejection_reason='' | Reject or simplify any candidate that fails the anti-overfitting gates. |
| fail | Incoming live markets are moderately validated in shadow mode | accepted_entries=15; distinct_markets=15; calendar_days=1; weekend_days=0; source=logs/particle_research/reports/rv600_variation_forward_latest.json; latest_labeled_root_update=2026-05-15T20:33:42+00:00 | Collect/label fresh RV600 locked forward-shadow markets until the plan's sample gates pass. |
| fail | Forward-shadow evidence is not only sparse sidecar or fallback-vol artifacts | native_candidate_rows=7584; native_distinct_markets=23; sidecar_candidate_rows=4; sidecar_distinct_markets=3; source_quality_note=forward report mixes native and sidecar evidence; completion should rely on native continuous rows | Collect native/continuous RV600 forward roots with matching current-control contexts; sparse sidecar snapshots are diagnostic only for completion. |
| fail | Forward-shadow PnL is positive and passes the same artifact checks | selected_pnl_cents=-155.3; matched_v28_control_pnl_cents=-148.2; avg_pnl_per_entry_cents=-10.353333333333333; max_single_market_pnl_share=0.0; last_window_pnl_cents=-6.3 | Do not mark the goal complete until fresh shadow PnL clears all promotion gates. |
| pass | Regression coverage verifies repeated-entry and matched-control accounting | test_file=test_research_particle_synthetic.py mentions_rv600_variation=True | Add or restore the synthetic RV600 accounting regression test. |
