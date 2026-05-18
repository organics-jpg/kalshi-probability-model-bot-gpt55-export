# Dynamic Particle Locked OOS Run Plan

- schema_version: dynamic-particle-locked-oos-run-plan-v1
- generated_utc: 2026-05-11T09:28:43.251725+00:00
- hypothesis_id: rolling_vol_600s_v1
- evaluation_scope: locked_oos_shadow
- dataset: particle_dynamic600_oos_20260511TLOCKEDNEXT2
- run_id: 20260511TLOCKEDNEXT2-DYN600
- artifact_root: `logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2`
- run_seconds: 3900
- checkpoint_interval_seconds: 1
- checkpoint_depth: 5

## Gates

- min_candidate_count: 1000
- min_market_count: 5
- min_selected_count: 250
- min_total_pnl_cents: 1.0
- min_avg_pnl_per_selected_cents: 0.01
- require_positive_ev_rank: True
- require_positive_top_ev_bucket: True
- require_beats_brownian_probability: True
- require_beats_market_probability: True
- require_beats_current_probability: True
- require_beats_static_particle_pnl: True
- require_beats_current_calibrated_pnl: True

## Commands

```powershell
python -m research_particle.paired_passive_shadow_run --dataset particle_dynamic600_oos_20260511TLOCKEDNEXT2 --run-id 20260511TLOCKEDNEXT2-DYN600 --run-seconds 3900 --checkpoint-interval-seconds 1 --checkpoint-depth 5 --status-interval-seconds 10

python -m research_particle.shadow_pipeline --source-type passive_checkpoint --checkpoints "research_data\particle_dynamic600_oos_20260511TLOCKEDNEXT2\book_checkpoints\**\*.ndjson" --contexts "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\passive_contexts.ndjson" --root "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2" --annualized-vol 0.65 --sample-count 2000 --seed 1 --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5

python -m research_particle.kalshi_market_results --ticker <TICKER_1> --ticker <TICKER_2> --ticker <TICKER_3> --ticker <TICKER_4> --ticker <TICKER_5> --output "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\market_results_full_refresh.json" --issues "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\market_result_issues_full_refresh.json"

python -m research_particle.market_result_labels --candidates "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\candidate_snapshots\candidate_snapshots.ndjson" --market-results "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\market_results_full_refresh.json" --output "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\pipeline_work\label_contexts_full_refresh.ndjson"

python -m research_particle.reports --candidates "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\reports" --stem passive_particle_replay_locked_oos --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5

python -m research_particle.probability_variants --candidates "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\reports" --stem probability_variants_locked_oos --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5

python -m research_particle.dynamic_particle_replay --candidates "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\reports" --stem dynamic_particle_locked_oos_diagnostic --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5

python -m research_particle.dynamic_particle_oos --candidates "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_dynamic600_oos_20260511TLOCKEDNEXT2\reports" --stem dynamic_particle_oos_locked --hypothesis-id rolling_vol_600s_v1 --evaluation-scope locked_oos_shadow --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5 --gate-min-candidates 1000 --gate-min-markets 5 --gate-min-selected 250
```

## Notes

- This plan is research-only and starts no process by itself.
- The dynamic hypothesis, gates, and evaluation scope must be fixed before collection begins.
- Do not use this plan to relabel or promote the capture that inspired the hypothesis.
- Use all labeled candidates; unresolved-market subsets are not promotion evidence.
- Passing this report only makes the dynamic-vol particle variant eligible for the broader goal audit.
