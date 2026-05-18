# Fixed Terminal Locked OOS Run Plan

- schema_version: fixed-terminal-locked-oos-run-plan-v1
- generated_utc: 2026-05-11T18:51:07.367321+00:00
- hypothesis_id: gaussian_vol45_terminal_v1
- evaluation_scope: locked_oos_shadow
- dataset: particle_fixed_terminal_oos_GAUSS45LOCK002
- run_id: GAUSS45LOCK002
- artifact_root: `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002`
- run_seconds: 5400
- checkpoint_interval_seconds: 1
- checkpoint_depth: 5
- independent_spot_feed: coinbase
- independent_spot_max_age_ms: 5000
- baseline_pipeline_annualized_vol: 0.65
- fixed_terminal_annualized_vol: 0.45

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
python -m research_particle.paired_passive_shadow_run --dataset particle_fixed_terminal_oos_GAUSS45LOCK002 --run-id GAUSS45LOCK002 --run-seconds 5400 --checkpoint-interval-seconds 1 --checkpoint-depth 5 --status-interval-seconds 10 --record-independent-spot --independent-spot-feed coinbase --independent-spot-max-age-ms 5000 --require-independent-spot

python -m research_particle.shadow_pipeline --source-type passive_checkpoint --checkpoints "research_data\particle_fixed_terminal_oos_GAUSS45LOCK002\book_checkpoints\**\*.ndjson" --contexts "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\passive_contexts_independent_spot.ndjson" --root "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002" --annualized-vol 0.65 --sample-count 2000 --seed 1 --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5

python -m research_particle.kalshi_market_results --ticker <TICKER_1> --ticker <TICKER_2> --ticker <TICKER_3> --ticker <TICKER_4> --ticker <TICKER_5> --output "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\market_results_full_refresh.json" --issues "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\market_result_issues_full_refresh.json"

python -m research_particle.market_result_labels --candidates "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\candidate_snapshots\candidate_snapshots.ndjson" --market-results "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\market_results_full_refresh.json" --output "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\pipeline_work\label_contexts_full_refresh.ndjson"

python -m research_particle.reports --candidates "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\reports" --stem passive_particle_replay_locked_oos --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5

python -m research_particle.probability_variants --candidates "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\reports" --stem probability_variants_locked_oos --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5

python -m research_particle.fat_tail_particle_diagnostic --run-root "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002" --output-dir "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\reports" --stem fat_tail_particle_locked_oos_diagnostic --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5

python -m research_particle.fixed_terminal_oos --candidates "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\pipeline_work\label_contexts_full_refresh.ndjson" --output-dir "logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\reports" --stem fixed_terminal_oos_locked --hypothesis-id gaussian_vol45_terminal_v1 --evaluation-scope locked_oos_shadow --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5 --gate-min-candidates 1000 --gate-min-markets 5 --gate-min-selected 250
```

## Notes

- This plan is research-only and starts no process by itself.
- The fixed low-vol terminal hypothesis was derived from prior diagnostics and must be treated as a new hypothesis.
- The baseline pipeline remains at annualized vol 0.65 so gaussian_vol45 is compared against the existing static particle baseline.
- Do not edit the hypothesis, fill assumptions, gates, or evaluation scope after collection begins.
- Use the independent spot merged context; contexts without timestamp-available spot are excluded.
- Use all labeled candidates; unresolved-market subsets are not promotion evidence.
- Passing this report only makes gaussian_vol45_terminal_v1 eligible for the broader goal audit.
