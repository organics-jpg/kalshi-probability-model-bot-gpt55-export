# Fat-Tail Particle Diagnostic

- run_count: 1
- spec_count: 13
- promotion_safe: False
- conclusion: No fixed fat-tail/jump-mixture terminal distribution clears strict locked-run gates.
- best_by_brier: gaussian_vol45
- best_by_pnl: gaussian_vol65

## Summary

| spec | runs | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| gaussian_vol65 | 1 | -6229.0000 | 0.191099 | 0.566604 | 0/1 | 1/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | False |
| tail05_scale3_vol65 | 1 | -6545.0000 | 0.192395 | 0.569919 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | False |
| tail10_scale3_down10bps_vol65 | 1 | -6884.0000 | 0.195900 | 0.577800 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | False |
| tail10_scale5_vol65 | 1 | -6954.0000 | 0.194321 | 0.574764 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | False |
| tail20_scale3_vol65 | 1 | -7095.0000 | 0.196522 | 0.580121 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | False |
| tail10_scale3_vol65 | 1 | -7136.0000 | 0.193731 | 0.573277 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | False |
| gaussian_vol45 | 1 | -7258.0000 | 0.178926 | 0.533517 | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | False |
| tail20_scale5_vol65 | 1 | -7418.0000 | 0.197781 | 0.583178 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | False |
| tail10_scale3_up10bps_vol65 | 1 | -7697.0000 | 0.191712 | 0.569054 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | False |
| gaussian_vol85 | 1 | -8228.0000 | 0.200461 | 0.589260 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | False |
| tail20_scale4_up5bps_vol85 | 1 | -8283.0000 | 0.204980 | 0.599932 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | False |
| tail20_scale4_down5bps_vol85 | 1 | -8418.0000 | 0.207536 | 0.605162 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | False |
| gaussian_vol110 | 1 | -8822.0000 | 0.209008 | 0.608598 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | False |

## Runs

| run | spec | candidates | markets | selected | pnl_cents | brier | log_loss | beats_brownian | beats_market | beats_current | ev_rank | top_bucket_pnl | strict |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|
| particle_fixed_terminal_oos_GAUSS45LOCK003 | gaussian_vol45 | 4405 | 6 | 4221 | -7258.0000 | 0.178926 | 0.533517 | True | False | False | -0.031596 | -14.1824 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | gaussian_vol65 | 4405 | 6 | 4227 | -6229.0000 | 0.191099 | 0.566604 | True | False | False | 0.066722 | -12.0717 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | gaussian_vol85 | 4405 | 6 | 4219 | -8228.0000 | 0.200461 | 0.589260 | False | False | False | 0.146661 | -10.1842 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | gaussian_vol110 | 4405 | 6 | 4210 | -8822.0000 | 0.209008 | 0.608598 | False | False | False | 0.213301 | -6.3530 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | tail05_scale3_vol65 | 4405 | 6 | 4220 | -6545.0000 | 0.192395 | 0.569919 | False | False | False | 0.076599 | -11.8984 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | tail10_scale3_vol65 | 4405 | 6 | 4231 | -7136.0000 | 0.193731 | 0.573277 | False | False | False | 0.094709 | -11.6189 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | tail20_scale3_vol65 | 4405 | 6 | 4223 | -7095.0000 | 0.196522 | 0.580121 | False | False | False | 0.114123 | -11.1661 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | tail10_scale5_vol65 | 4405 | 6 | 4226 | -6954.0000 | 0.194321 | 0.574764 | False | False | False | 0.097071 | -11.5091 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | tail20_scale5_vol65 | 4405 | 6 | 4220 | -7418.0000 | 0.197781 | 0.583178 | False | False | False | 0.126367 | -10.7967 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | tail10_scale3_up10bps_vol65 | 4405 | 6 | 4182 | -7697.0000 | 0.191712 | 0.569054 | False | False | False | 0.096476 | -11.3984 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | tail10_scale3_down10bps_vol65 | 4405 | 6 | 4246 | -6884.0000 | 0.195900 | 0.577800 | False | False | False | 0.084903 | -11.8648 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | tail20_scale4_up5bps_vol85 | 4405 | 6 | 4197 | -8283.0000 | 0.204980 | 0.599932 | False | False | False | 0.193572 | -7.3575 | False |
| particle_fixed_terminal_oos_GAUSS45LOCK003 | tail20_scale4_down5bps_vol85 | 4405 | 6 | 4223 | -8418.0000 | 0.207536 | 0.605162 | False | False | False | 0.193078 | -7.4129 | False |

## Run Inputs

| run | rows | markets | candidate_path | label_path |
|---|---:|---:|---|---|
| particle_fixed_terminal_oos_GAUSS45LOCK003 | 4405 | 6 | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK003\candidate_snapshots\candidate_snapshots.ndjson` | `logs\particle_research\real_shadow\particle_fixed_terminal_oos_GAUSS45LOCK003\pipeline_work\label_contexts_full_refresh.ndjson` |
