# V28 Rolling-Vol Transfer Diagnostic

- generated_utc: 2026-05-13T02:11:15+00:00
- promotion_allowed: False
- root_count: 10
- best_by_total_delta: rv600
- best_probability_transfer: v28_80_rv300_20
- conclusion: No rolling-vol transfer cleared the strict diagnostic screen versus v28/current. Best total delta was rv600 at 38929.0c, so keep rolling-vol as a research feature, not a live v28 change.

## Summary

| strategy | family | runs | selected | pnl_cents | delta_vs_current | avg_selected_pnl | brier | log_loss | +delta runs | brier beats | logloss beats | strict? |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| rv600 | rolling_vol | 10 | 26744 | 73567.0 | 38929.0 | 2.7508 | 0.181229 | 0.525901 | 6 | 4 | 5 | False |
| rv300 | rolling_vol | 10 | 26768 | 66909.0 | 32271.0 | 2.4996 | 0.182370 | 0.530731 | 3 | 5 | 5 | False |
| v28_with_rv600_side_agreement_veto | agreement_veto | 10 | 18997 | 56329.0 | 21691.0 | 2.9652 | 0.182412 | 0.533025 | 6 | 0 | 0 | False |
| v28_80_rv300_20 | blend | 10 | 26418 | 51166.0 | 16528.0 | 1.9368 | 0.181877 | 0.530210 | 4 | 6 | 5 | False |
| v28_with_rv300_side_agreement_veto | agreement_veto | 10 | 18310 | 50229.0 | 15591.0 | 2.7433 | 0.182412 | 0.533025 | 5 | 0 | 0 | False |
| v28_80_rv600_20 | blend | 10 | 26535 | 45153.0 | 10515.0 | 1.7016 | 0.181745 | 0.530025 | 5 | 7 | 6 | False |
| v28_90_rv300_10 | blend | 10 | 26715 | 41983.0 | 7345.0 | 1.5715 | 0.182111 | 0.531375 | 4 | 6 | 5 | False |
| v28_95_rv300_05 | blend | 10 | 26696 | 39854.0 | 5216.0 | 1.4929 | 0.182253 | 0.532129 | 6 | 6 | 5 | False |
| v28_90_rv600_10 | blend | 10 | 26659 | 37627.0 | 2989.0 | 1.4114 | 0.182051 | 0.531386 | 5 | 8 | 7 | False |
| v28_95_rv600_05 | blend | 10 | 26704 | 36721.0 | 2083.0 | 1.3751 | 0.182225 | 0.532167 | 5 | 8 | 7 | False |
| current_calibrated_v28 | baseline | 10 | 26808 | 34638.0 | 0.0 | 1.2921 | 0.182412 | 0.533025 | 0 | 0 | 0 | False |

## Roots

- particle_dynamic600_oos_20260511TLOCKEDNEXT2
- particle_dynamic_oos_20260511TLOCKEDNEXT
- particle_fixed_terminal_oos_GAUSS45LOCK001
- particle_fixed_terminal_oos_GAUSS45LOCK002
- particle_fixed_terminal_oos_GAUSS45LOCK003
- particle_residual_blend_oos_RESIDLOCK001
- particle_shadow_forward_20260511T053741Z-long900
- particle_side_consensus_oos_CONSENSUSLOCK001
- particle_side_safety_oos_20260511TLOCKED
- particle_spot_rv_terminal_oos_RVTERMLOCK001
