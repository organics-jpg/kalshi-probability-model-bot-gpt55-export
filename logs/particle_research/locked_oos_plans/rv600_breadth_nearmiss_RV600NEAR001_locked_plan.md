# RV600NEAR001 Locked Forward Diagnostic Plan

- generated_utc: `2026-05-15T04:53:47Z`
- research_only: `True`
- variant: `rv600_primary_side_flip_only_broad_70_600_ev4`
- probability_mode: `rv600_primary`
- window: `T-600s` to `T-70s`
- min_ev_cents: `4`
- entry_rule: `side_flip_only`
- max_entries_per_market: `2`
- primary_accounting_mode: `position_capped`

## Why This Candidate

This is a simple three-gate RV600 candidate from the existing locked candidate
set. On the current 22-root diagnostic sample, `one_per_side_per_market` and
`position_capped` are equivalent because side-flip-only prevents repeated
same-side replay inflation.

Prior diagnostic metrics:

- accepted_entries: `41`
- selected_pnl_cents: `+339c`
- matched_v28_delta_cents: `+218c`
- avg_pnl_per_entry_cents: `8.2683c`
- positive_root_rate: `0.6364`
- positive_market_rate: `0.6071`
- max_single_market_pnl_share: `0.1799`
- last_window_pnl_cents: `+27c`
- rejection_reason: `avg_entry_below_10c`

## Pre-Registration

Only evidence after `2026-05-15T04:53:47Z` counts as forward evidence for this
plan. Prior evidence can explain why the candidate was frozen, but cannot
promote the candidate or complete the goal.

Do not tune this candidate using future outcomes. Score the frozen variant
against matched v28 at the same accepted timestamps.

## Forward Gates

- selected PnL after fees/fills must be positive
- selected PnL must beat matched v28 by at least `20%`
- average PnL per entry must be at least `10c`
- average PnL per market must be positive
- positive root and market rates must both be at least `60%`
- last 20 accepted entries must be positive
- no single market may contribute more than `25%` of total PnL
- fill-adjusted PnL must remain positive
- target sample: `100` accepted entries, `40` distinct markets, `10` calendar
  days, and `2` weekend sessions

## Guardrails

- Research-only: no live trades.
- Do not change live v28 order logic.
- Do not restart the live bot.
- Use offline matched-v28 replay from passive checkpoints and independent spot.
- Do not call `update_goal` unless the objective audit is green on future-only
  evidence.
