# Particle Shadow Run Preflight

Generated UTC: `2026-05-13T11:56:27.681592+00:00`
Dataset: `particle_shadow_readonly`
Artifact root: `logs\particle_research\real_shadow\particle_shadow_readonly`

## Readiness

- ready_to_collect: `True`
- ready_to_pipeline: `True`
- env_file_exists: `True`
- api_key_present: `True`
- private_key_path_present: `True`
- private_key_file_exists: `True`
- passive_recorder_exists: `True`
- context_tailer_exists: `True`
- paired_runner_exists: `True`
- checkpoint_file_count: `1`
- checkpoint_row_count: `72`
- context_row_count: `60`
- market_results_row_count: `1`

## Commands

```powershell
python research_native_passive_ws_recorder.py --dataset particle_shadow_readonly --strategy-tag particle_shadow_readonly --bot-tag particle_shadow_readonly --checkpoint-interval-seconds 1 --checkpoint-depth 5

python -m research_particle.v28_context_tailer --input "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live\execution_events.ndjson" --output "logs\particle_research\real_shadow\particle_shadow_readonly\passive_contexts.ndjson" --issues "logs\particle_research\real_shadow\particle_shadow_readonly\passive_context_issues.ndjson" --status "logs\particle_research\real_shadow\particle_shadow_readonly\passive_context_tailer_status.json" --follow --start-at-end --seed-last-contexts --append-ok

python -m research_particle.paired_passive_shadow_run --run-seconds 900 --checkpoint-interval-seconds 1 --checkpoint-depth 5 --record-independent-spot --independent-spot-feed coinbase --independent-spot-max-age-ms 5000

python -m research_particle.shadow_pipeline --source-type passive_checkpoint --checkpoints "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\research_data\particle_shadow_readonly\book_checkpoints\**\*.ndjson" --contexts "logs\particle_research\real_shadow\particle_shadow_readonly\passive_contexts.ndjson" --market-results "logs\particle_research\real_shadow\particle_shadow_readonly\market_results.json" --root "logs\particle_research\real_shadow\particle_shadow_readonly" --annualized-vol 0.65 --sample-count 2000 --seed 1 --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5

python -m research_particle.reports --candidates "logs\particle_research\real_shadow\particle_shadow_readonly\candidate_snapshots\candidate_snapshots.ndjson" --labels "logs\particle_research\real_shadow\particle_shadow_readonly\settlement_labels\settlement_labels.ndjson" --output-dir "logs\particle_research\real_shadow\particle_shadow_readonly\reports" --stem online_calibrated_particle_replay --online-calibrated --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
```

## Notes

- Pipeline prerequisites are present; run the command template with a fresh artifact root.
