# Side Safety OOS Protocol

Updated: 2026-05-11

This protocol predeclares the next side-safety hypothesis before any fresh
shadow/OOS result is inspected. It is research-only and must not change live
trading behavior.

## Hypothesis

`side_safe_yes_only_v1`

Start from the existing particle replay decision rule and the same predeclared
EV/fill assumptions:

- `min_ev_cents=0`
- `min_fill_prob=0.5`
- `counterfactual_fill_policy=threshold`
- `counterfactual_fill_threshold=0.5`
- `no_fill_penalty_cents=0`

Then apply one fixed side-safety overlay:

- keep selected YES decisions
- block selected NO decisions
- do not retune EV thresholds
- do not use market outcome labels before decision time
- do not promote from same-sample diagnostics

## Why This Exists

The full 753-row same-sample forward replay showed selected YES decisions at
`+4193c` and selected NO decisions at `-9069c`. That is enough to justify a
predeclared OOS test, not enough to justify promotion.

## Fresh Locked OOS Gates

A future `locked_oos_shadow` report can pass only if all are true:

- `candidate_count >= 500`
- `market_count >= 4`
- `side_safe_selected_count >= 100`
- `side_safe_total_counterfactual_pnl_cents > 0`
- `side_safe_avg_counterfactual_pnl_cents_per_selected > 0`
- `side_safe_ev_rank_correlation_sign > 0`
- `side_safe_top_ev_bucket_pnl_cents > 0`
- side-safe PnL beats the base particle replay PnL
- denominator is all labeled candidates, not a quiet skipped subset
- the report was run with `--evaluation-scope locked_oos_shadow`

Passing these gates still does not make the strategy live-ready. It only makes
the side-safety hypothesis eligible for the broader particle-system promotion
audit.

## Commands

Same-sample diagnostic on the old 753-row capture:

```powershell
python -m research_particle.side_safety_oos --candidates logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\pipeline_work\label_contexts_full_refresh.ndjson --output-dir logs\particle_research\real_shadow\particle_shadow_forward_20260511T053741Z-long900\reports --stem side_safety_oos_same_sample --evaluation-scope same_sample_diagnostic --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
```

Fresh OOS shadow report, after collecting and labeling a new all-candidate
capture:

```powershell
python -m research_particle.side_safety_oos --candidates <fresh_run>\candidate_snapshots\candidate_snapshots.ndjson --labels <fresh_run>\pipeline_work\label_contexts_full_refresh.ndjson --output-dir <fresh_run>\reports --stem side_safety_oos_locked --evaluation-scope locked_oos_shadow --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
```

## Promotion Blockers

- Any same-sample report is automatically non-promotable.
- Any unresolved market subset is non-promotable.
- Any change to thresholds, side rule, or gates after seeing fresh OOS results
  creates a new hypothesis and requires a new fresh OOS capture.
- Live trading remains untouched until the full goal audit passes.
