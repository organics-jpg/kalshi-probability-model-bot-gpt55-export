# Dynamic Rolling-Vol OOS Protocol

Updated: 2026-05-11

This protocol predeclares the next rolling-vol particle hypothesis before any
fresh shadow/OOS result is inspected. It is research-only and must not change
live trading behavior.

## Hypothesis

Primary hypothesis: `rolling_vol_300s_v1`

Use the existing all-candidate passive particle replay denominator and the same
predeclared EV/fill assumptions:

- `min_ev_cents=0`
- `min_fill_prob=0.5`
- `counterfactual_fill_policy=threshold`
- `counterfactual_fill_threshold=0.5`
- `no_fill_penalty_cents=0`

Replace the fixed 65% annualized volatility terminal probability with the
chronological rolling-vol particle variant:

- lookback: 300 seconds
- fallback annualized volatility: 0.65
- volatility clamp: `[0.20, 2.50]`
- minimum distinct spot observations: 3
- market blend weight: 0.0

The variant must use only spot observations available at or before each
candidate decision timestamp.

## Why This Exists

The fresh locked side-safety OOS capture showed that the same-sample YES-only
side rule failed. On that same fresh capture, the rolling-vol diagnostic family
was the first variant to beat Brownian, market mid, and current calibrated
probability on both Brier/log loss while also producing positive EV ranking and
positive counterfactual PnL. That is enough to justify a new predeclared OOS
test, not enough to justify promotion.

## Fresh Locked OOS Gates

A future `locked_oos_shadow` report can pass only if all are true:

- `candidate_count >= 1000`
- `market_count >= 5`
- `selected_count >= 250`
- total counterfactual PnL is positive
- average PnL per selected candidate is positive
- Brier and log loss beat Brownian
- Brier and log loss beat market mid
- Brier and log loss beat current calibrated probability
- EV rank correlation is positive
- top predicted EV bucket PnL is positive
- dynamic rolling-vol PnL beats static particle replay PnL
- dynamic rolling-vol PnL beats current calibrated PnL
- denominator is all labeled candidates, not a quiet skipped subset
- the report was run with `--evaluation-scope locked_oos_shadow`

Passing these gates still does not make the strategy live-ready. It only makes
the rolling-vol particle hypothesis eligible for the broader particle-system
promotion audit.

## Commands

Same-sample diagnostic on the capture that suggested the hypothesis:

```powershell
python -m research_particle.dynamic_particle_oos --candidates logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\candidate_snapshots\candidate_snapshots.ndjson --labels logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\pipeline_work\label_contexts_full_refresh.ndjson --output-dir logs\particle_research\real_shadow\particle_side_safety_oos_20260511TLOCKED\reports --stem dynamic_particle_oos_same_sample --hypothesis-id rolling_vol_300s_v1 --evaluation-scope same_sample_diagnostic --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
```

Write a fresh locked OOS plan:

```powershell
python -m research_particle.dynamic_particle_locked_oos_plan --hypothesis-id rolling_vol_300s_v1 --dataset particle_dynamic_oos_next_locked --run-id DYNAMIC-OOS-NEXT --stem dynamic_particle_next_locked_plan
```

Fresh OOS shadow report, after collecting and labeling a new all-candidate
capture:

```powershell
python -m research_particle.dynamic_particle_oos --candidates <fresh_run>\candidate_snapshots\candidate_snapshots.ndjson --labels <fresh_run>\pipeline_work\label_contexts_full_refresh.ndjson --output-dir <fresh_run>\reports --stem dynamic_particle_oos_locked --hypothesis-id rolling_vol_300s_v1 --evaluation-scope locked_oos_shadow --min-fill-prob 0.5 --counterfactual-fill-threshold 0.5
```

## Promotion Blockers

- Any same-sample report is automatically non-promotable.
- Any unresolved market subset is non-promotable.
- Any change to lookback, volatility clamp, thresholds, or gates after seeing
  fresh OOS results creates a new hypothesis and requires a new fresh capture.
- Live trading remains untouched until the full goal audit passes.
