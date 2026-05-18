# Fat-Tail Particle Diagnostic

- run_count: 1
- spec_count: 13
- promotion_safe: False
- conclusion: At least one fixed fat-tail terminal distribution cleared every locked run, but this diagnostic was not predeclared before capture and remains research-only.
- best_by_brier: tail10_scale3_down10bps_vol65
- best_by_pnl: gaussian_vol45

## Summary

| spec | runs | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| gaussian_vol65 | 1 | 48412.0000 | 0.240081 | 0.673717 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| tail05_scale3_vol65 | 1 | 48126.0000 | 0.239726 | 0.672745 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| tail10_scale3_down10bps_vol65 | 1 | 47694.0000 | 0.237196 | 0.666973 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| tail10_scale3_vol65 | 1 | 47641.0000 | 0.239415 | 0.671906 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| tail10_scale5_vol65 | 1 | 47261.0000 | 0.239288 | 0.671612 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| tail20_scale3_vol65 | 1 | 46835.0000 | 0.238922 | 0.670602 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| tail20_scale5_vol65 | 1 | 46769.0000 | 0.238756 | 0.670249 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| gaussian_vol85 | 1 | 46383.0000 | 0.238622 | 0.669456 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| tail20_scale4_down5bps_vol85 | 1 | 44985.0000 | 0.237259 | 0.666706 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| tail20_scale4_up5bps_vol85 | 1 | 44819.0000 | 0.239864 | 0.672133 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| gaussian_vol110 | 1 | 44517.0000 | 0.238699 | 0.669562 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | True |
| gaussian_vol45 | 1 | 49703.0000 | 0.246083 | 0.694486 | 1/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | False |
| tail10_scale3_up10bps_vol65 | 1 | 47043.0000 | 0.241765 | 0.677136 | 1/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | False |

## Runs

| run | spec | candidates | markets | selected | pnl_cents | brier | log_loss | beats_brownian | beats_market | beats_current | ev_rank | top_bucket_pnl | strict |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|
| particle_fixed_terminal_oos_GAUSS45LOCK002 | gaussian_vol45 | 4843 | 7 | 4378 | 49703.0000 | 0.246083 | 0.694486 | False | True | True | 0.117524 | 13.0603 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | gaussian_vol65 | 4843 | 7 | 4582 | 48412.0000 | 0.240081 | 0.673717 | True | True | True | 0.274388 | 19.7622 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | gaussian_vol85 | 4843 | 7 | 4627 | 46383.0000 | 0.238622 | 0.669456 | True | True | True | 0.338113 | 22.8869 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | gaussian_vol110 | 4843 | 7 | 4646 | 44517.0000 | 0.238699 | 0.669562 | True | True | True | 0.380745 | 26.0652 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | tail05_scale3_vol65 | 4843 | 7 | 4589 | 48126.0000 | 0.239726 | 0.672745 | True | True | True | 0.285373 | 20.5822 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | tail10_scale3_vol65 | 4843 | 7 | 4607 | 47641.0000 | 0.239415 | 0.671906 | True | True | True | 0.298918 | 21.1800 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | tail20_scale3_vol65 | 4843 | 7 | 4619 | 46835.0000 | 0.238922 | 0.670602 | True | True | True | 0.319067 | 21.8497 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | tail10_scale5_vol65 | 4843 | 7 | 4604 | 47261.0000 | 0.239288 | 0.671612 | True | True | True | 0.303538 | 21.6400 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | tail20_scale5_vol65 | 4843 | 7 | 4623 | 46769.0000 | 0.238756 | 0.670249 | True | True | True | 0.326444 | 21.9810 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | tail10_scale3_up10bps_vol65 | 4843 | 7 | 4587 | 47043.0000 | 0.241765 | 0.677136 | False | True | True | 0.284609 | 17.2312 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | tail10_scale3_down10bps_vol65 | 4843 | 7 | 4599 | 47694.0000 | 0.237196 | 0.666973 | True | True | True | 0.306708 | 23.1296 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | tail20_scale4_up5bps_vol85 | 4843 | 7 | 4617 | 44819.0000 | 0.239864 | 0.672133 | True | True | True | 0.359476 | 23.4600 | True |
| particle_fixed_terminal_oos_GAUSS45LOCK002 | tail20_scale4_down5bps_vol85 | 4843 | 7 | 4655 | 44985.0000 | 0.237259 | 0.666706 | True | True | True | 0.376894 | 27.6251 | True |

## Run Inputs

| run | rows | markets | candidate_path | label_path |
|---|---:|---:|---|---|
| particle_fixed_terminal_oos_GAUSS45LOCK002 | 4843 | 7 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK002\pipeline_work\label_contexts_full_refresh.ndjson` |
