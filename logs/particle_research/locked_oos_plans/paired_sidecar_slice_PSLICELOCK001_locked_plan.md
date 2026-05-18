# Paired Sidecar Slice Locked Shadow Plan

- schema_version: paired-sidecar-slice-locked-plan-v1
- generated_utc: `2026-05-12T14:44:16+00:00`
- hypothesis_id: `blend_v28_w20_time_gt_600s_v1`
- evaluation_scope: `locked_forward_shadow`
- run_id: `PSLICELOCK001`
- locked_after_utc: `2026-05-12T14:44:16+00:00`
- model: `blend_v28_online_lr010_w20`
- slice: `time_to_close_band=600s_plus`
- fee_cents: `1.5`
- assumed_fill_probability: `1.0`
- no_fill_penalty_cents: `0.0`
- baseline_models: `v28, market_side_ask, candle_brownian`
- selection_source_json: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\particle_research\reports\paired_sidecar_blend_failure_analysis_latest.json`
- selection_source_sha256: `41654819807d7e5628f580d6765c61be90638affce5c730482daf4d4a70429ff`

## Gates

- min_fresh_candidate_rows: 200
- min_fresh_markets: 20
- min_slice_rows: 100
- min_slice_markets: 15
- min_selected_count: 50
- min_selected_pnl_cents: 1.0
- min_avg_pnl_per_selected_cents: 0.01
- min_positive_selected_market_share: 0.6
- min_positive_top_ev_market_share: 0.6
- top_ev_fraction: 0.2
- require_positive_ev_rank: True
- require_positive_top_ev_bucket: True
- require_beats_baseline_brier: True
- require_beats_baseline_logloss: True
- require_beats_baseline_selected_pnl: False

## Commands

```powershell
python -m research_particle.paired_sidecar_spot_capture --collect-mode public-rest --spot-feed coinbase --spot-run-seconds 15 --spot-warmup-seconds 1 --spot-max-age-ms 2000 --timeout-seconds 10 --max-markets 80
python -m research_particle.paired_sidecar_spot_refresh --fetch-labels --write
python -m research_particle.paired_sidecar_online_calibration --write
python -m research_particle.paired_sidecar_blend_failure_analysis --write
python -m research_particle.paired_sidecar_slice_oos --plan-json "C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\particle_research\locked_oos_plans\paired_sidecar_slice_PSLICELOCK001_locked_plan.json" --stem paired_sidecar_slice_oos_latest --write
```

## Notes

- This plan is research-only and starts no process by itself.
- The model and slice were selected from a post-hoc diagnostic; all rows at or before locked_after_utc are excluded from promotion gates.
- Do not edit model, slice, fee/fill assumptions, baselines, gates, or evaluation_scope after this plan is written.
- The evaluator recomputes fee-adjusted EV and PnL from p_yes, side, ask, and the predeclared assumptions.
- Fresh paired sidecar captures must remain public REST plus independent public spot; no live bot orders, thresholds, secrets, or processes are touched.
- Passing the slice OOS report is still research evidence only; live trading remains untouched until the broader goal audit clears.
