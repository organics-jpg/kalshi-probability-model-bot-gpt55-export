# Fat-Tail Particle Diagnostic

- run_count: 1
- spec_count: 13
- promotion_safe: False
- conclusion: At least one fixed fat-tail terminal distribution cleared every locked run, but this diagnostic was not predeclared before capture and remains research-only.
- best_by_brier: tail20_scale4_up5bps_vol85
- best_by_pnl: gaussian_vol85

## Summary

| spec | runs | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| gaussian_vol85 | 1 | 50793.0000 | 0.223807 | 0.629968 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| tail20_scale4_up5bps_vol85 | 1 | 50776.0000 | 0.221797 | 0.628864 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| tail10_scale3_vol65 | 1 | 50443.0000 | 0.225913 | 0.631822 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| tail05_scale3_vol65 | 1 | 50436.0000 | 0.226389 | 0.631859 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| gaussian_vol65 | 1 | 50272.0000 | 0.226936 | 0.632014 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| tail10_scale3_up10bps_vol65 | 1 | 50237.0000 | 0.222274 | 0.623236 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| tail20_scale4_down5bps_vol85 | 1 | 50535.0000 | 0.226429 | 0.639071 | 1/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | False |
| gaussian_vol110 | 1 | 50452.0000 | 0.223918 | 0.633876 | 1/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | False |
| tail10_scale5_vol65 | 1 | 50443.0000 | 0.225794 | 0.632180 | 1/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | False |
| tail20_scale5_vol65 | 1 | 50384.0000 | 0.225102 | 0.633046 | 1/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | False |
| tail20_scale3_vol65 | 1 | 50276.0000 | 0.225175 | 0.632096 | 1/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | False |
| tail10_scale3_down10bps_vol65 | 1 | 50269.0000 | 0.229662 | 0.640684 | 1/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | False |
| gaussian_vol45 | 1 | 47330.0000 | 0.239468 | 0.654227 | 1/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | False |

## Runs

| run | spec | candidates | markets | selected | pnl_cents | brier | log_loss | beats_brownian | beats_market | beats_current | ev_rank | top_bucket_pnl | strict |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|
| particle_fixed_terminal_oos_GAUSS45LOCK001 | gaussian_vol45 | 2514 | 4 | 2330 | 47330.0000 | 0.239468 | 0.654227 | False | True | True | 0.112001 | 20.5914 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | gaussian_vol65 | 2514 | 4 | 2422 | 50272.0000 | 0.226936 | 0.632014 | True | True | True | 0.188851 | 21.0906 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | gaussian_vol85 | 2514 | 4 | 2429 | 50793.0000 | 0.223807 | 0.629968 | True | True | True | 0.209017 | 17.9253 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | gaussian_vol110 | 2514 | 4 | 2451 | 50452.0000 | 0.223918 | 0.633876 | False | True | True | 0.226190 | 16.3196 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | tail05_scale3_vol65 | 2514 | 4 | 2423 | 50436.0000 | 0.226389 | 0.631859 | True | True | True | 0.191333 | 21.0191 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | tail10_scale3_vol65 | 2514 | 4 | 2423 | 50443.0000 | 0.225913 | 0.631822 | True | True | True | 0.194906 | 19.9841 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | tail20_scale3_vol65 | 2514 | 4 | 2423 | 50276.0000 | 0.225175 | 0.632096 | False | True | True | 0.201287 | 18.7806 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | tail10_scale5_vol65 | 2514 | 4 | 2423 | 50443.0000 | 0.225794 | 0.632180 | False | True | True | 0.195981 | 19.5978 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | tail20_scale5_vol65 | 2514 | 4 | 2421 | 50384.0000 | 0.225102 | 0.633046 | False | True | True | 0.199517 | 18.1685 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | tail10_scale3_up10bps_vol65 | 2514 | 4 | 2413 | 50237.0000 | 0.222274 | 0.623236 | True | True | True | 0.216842 | 23.6820 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | tail10_scale3_down10bps_vol65 | 2514 | 4 | 2430 | 50269.0000 | 0.229662 | 0.640684 | False | True | True | 0.174088 | 16.4038 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | tail20_scale4_up5bps_vol85 | 2514 | 4 | 2438 | 50776.0000 | 0.221797 | 0.628864 | True | True | True | 0.225440 | 18.6614 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK001 | tail20_scale4_down5bps_vol85 | 2514 | 4 | 2447 | 50535.0000 | 0.226429 | 0.639071 | False | True | True | 0.206490 | 15.8267 | False |

## Run Inputs

| run | rows | markets | candidate_path | label_path |
|---|---:|---:|---|---|
| particle_fixed_terminal_oos_GAUSS45LOCK001 | 2514 | 4 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK001\pipeline_work\label_contexts_full_refresh.ndjson` |
