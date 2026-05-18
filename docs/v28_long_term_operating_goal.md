# v28 Long-Term Operating Goal

## Mandate

Continuously improve the v28-style BTC 15-minute strategy for durable risk-adjusted ROI. Start from v28, not v55/v60. Improve the whole stack in this order: exits/state handling, entry quality, then FV probability modeling.

Quiet mode is the default: report only when something material changes, breaks, is patched, hits a risk stop, or needs a decision.

## Operating Rules

- Score progress by risk-adjusted ROI: net P&L, account ROI, drawdown, loss clusters, trade count, coverage, and execution quality.
- Keep broad BTC 15m coverage as a soft target, but durable ROI overrides a fixed 80% coverage goal.
- Use v28 as the control baseline: high-confidence entries, IOC execution, fresh BTC/book gates, current v28 exit/state handling, and size/risk settings appropriate to balance.
- Treat old logs as diagnostics only. Promote trading logic from physical argument plus fresh forward evidence, not best historical rows.
- Prefer safe, reversible patches. Live changes must be scoped, observable, and backed by tests or script-level checks.
- Use a medium live-trial risk cap: stop new live entries for review after about 5 net losses or 35-40% trial drawdown, unless the issue is clearly technical.

## Continuous Work Loop

1. Maintain the v28 evidence pipeline for entries, exits, fills, book state, BTC feed state, FV state, and settlement.
2. Track forward registries for FV calibration, exit value, stale-feed events, depth/crowding, model disagreement, recross hazard, and collapse-exit turbulence.
3. Attribute failures as FV error, entry timing error, exit-policy error, execution error, or market-regime error.
4. Improve exits first, especially probability-collapse behavior and exit value versus hold-to-settlement.
5. Improve entries second by identifying physically coherent bad-entry regimes without silently destroying coverage.
6. Improve FV third by measuring calibration before P&L and adding only physics-backed features.

## Current Baseline

- Shadow storage tag: `shadow_mushroom_v28_reactivation_size2`
- Current score status: `logs/edge_research/v28_reactivated_shadow_status_latest.md`
- Current physics registry: `logs/edge_research/v28_forward_physics_registry_latest.md`
- Current operating scorecard: `logs/edge_research/v28_continuous_scorecard_latest.md`

## Promotion Standard

A candidate is useful only if it:

- has a clear market-physics explanation,
- improves risk-adjusted results or calibration on forward evidence,
- does not depend on a tiny historical split,
- preserves enough coverage to matter, unless the ROI improvement justifies narrowing,
- remains reversible and operationally observable.
