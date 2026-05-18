# RV600REV001 Locked Forward Plan

- generated_utc: `2026-05-15T07:10:45Z`
- research_only: `true`
- plan_id: `RV600REV001`
- variant: `rv600_primary_same_side_ev_step_3c_base_70_420_ev2`
- forward_evidence_starts_after_utc: `2026-05-15T07:10:45Z`

## Candidate

- probability_mode: `rv600_primary`
- timing window: `70s` to `420s` before close
- min EV: `2c`
- entry rule: `same_side_ev_step_3c`
- max entries per market: `3`
- primary accounting mode: `position_capped`
- required accounting modes:
  - `all_entries`
  - `one_per_side_per_market`
  - `position_capped`

## Why Frozen

After the 25th bounded root, this became the simplest current support row with
no local summary rejection under fair repeated-entry accounting:

- entries: `63`
- markets: `28`
- selected PnL: `+1198c`
- matched-v28 delta: `+542c`
- average PnL per entry: `19.0159c`
- positive root rate: `0.6000`
- positive market rate: `0.6071`
- max single-market PnL share: `0.2362`
- last-window PnL: `+28c`
- rejection: none

This is not a promotion. The current grid is still rejected by broader
anti-overfitting checks:

- PBO: `pbo_rejects_current_grid`, `pbo=0.5449`
- root-bootstrap reality check: `reality_check_rejects_current_grid`,
  mean p-value `0.2498`, studentized p-value `0.2278`
- stability selection: `stability_selection_rescue_failed`

## Forward Gates

Future evidence only counts after `2026-05-15T07:10:45Z`.

- selected PnL after fees/fills must be positive
- matched-v28 edge must be at least `20%`
- average PnL per entry must be at least `10c`
- average PnL per market must be positive
- positive root rate must be at least `60%`
- positive market rate must be at least `60%`
- last 20 accepted entries must be positive
- no single market may contribute more than `25%` of total PnL
- fill-adjusted PnL must be positive
- target sample: `100` accepted entries, `40` markets, `10` calendar days,
  and `2` weekend sessions

## Guardrails

- Research-only: no live trades.
- Do not change live v28 order logic.
- Do not restart the live bot.
- Do not tune this candidate using future outcomes.
- Do not complete the goal unless the full objective audit is green on
  future-only evidence.
