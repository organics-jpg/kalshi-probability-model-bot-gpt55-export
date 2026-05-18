# Locked OOS Run Plan

- schema_version: locked-oos-run-plan-v1
- generated_utc: 2026-05-11T06:29:35.240710+00:00
- hypothesis_id: side_safe_yes_only_v1
- evaluation_scope: locked_oos_shadow
- dataset: particle_side_safety_oos_20260511TLOCKED
- run_id: 20260511TLOCKED-SIDESAFE
- artifact_root: `logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED`
- run_seconds: 3900
- checkpoint_interval_seconds: 1
- checkpoint_depth: 5

## Gates

- min_candidate_count: 500
- min_market_count: 4
- min_selected_count: 100
- min_total_pnl_cents: 1.0
- min_avg_pnl_per_selected_cents: 0.01
- require_positive_ev_rank: True
- require_positive_top_ev_bucket: True
- require_beats_base_pnl: True

## Commands

```powershell
python -m research_particle.paired_passive_shadow_run --dataset particle_side_safety_oos_20260511TLOCKED --run-id 20260511TLOCKED-SIDESAFE --run-seconds 3900 --checkpoint-interval-seconds 1 --checkpoint-depth 5 --status-interval-seconds 10

python -m research_particle.shadow_pipeline --source-type passive_checkpoint --checkpoints "research_data\particle_side_safety_oos_20260511TLOCKED\book_checkpoints\**\*.ndjson" --contexts "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\passive_contexts.ndjson" --root "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED" --annualized-vol 0.65 --sample-count 2000 --seed 1 --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5

python -m research_particle.kalshi_market_results --ticker <TICKER_1> --ticker <TICKER_2> --ticker <TICKER_3> --ticker <TICKER_4> --output "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\market_results_full_refresh.json" --issues "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\market_result_issues_full_refresh.json"

python -m research_particle.market_result_labels --candidates "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\candidate_snapshots\candidate_snapshots.ndjson" --market-results "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\market_results_full_refresh.json" --output "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\pipeline_work\label_contexts_full_refresh.ndjson"

python -m research_particle.reports --candidates "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\reports" --stem passive_particle_replay_locked_oos --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5

python -m research_particle.reports --candidates "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\reports" --stem online_calibrated_particle_replay_locked_oos --online-calibrated --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5

python -m research_particle.selection_sweep --candidates "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\reports" --stem passive_particle_selection_sweep_locked_oos --min-ev-grid 0,1,2,3,5,8,10,12,15,20 --min-fill-grid 0,0.25,0.5,0.75,1.0 --counterfactual-fill-threshold 0.5

python -m research_particle.side_failure_analysis --candidates "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\reports" --stem side_failure_locked_oos --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5

python -m research_particle.side_safety_oos --candidates "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\reports" --stem side_safety_oos_locked --evaluation-scope locked_oos_shadow --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5 --gate-min-candidates 500 --gate-min-markets 4 --gate-min-selected 100
```

## Notes

- This plan is research-only and starts no process by itself.
- Do not edit thresholds or gates after collection begins; create a new plan instead.
- Use all labeled candidates; unresolved-market subsets are not promotion evidence.
- Passing side_safety_oos_locked only makes the side-safety hypothesis eligible for the broader goal audit.
