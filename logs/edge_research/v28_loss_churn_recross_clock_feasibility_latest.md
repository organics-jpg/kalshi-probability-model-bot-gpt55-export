# v28 Loss-Churn Recross Clock Feasibility

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T16:56:11.035222+00:00`
- Rule: `recross_ge_045`
- Known / selected rows: `167` / `15`
- Replay delta / candidate net: `574c ($5.74)` / `1393c ($13.93)`
- Replay harmful / new losses: `0` / `0`
- Blockers: `research_only, not_frozen_forward, full_denominator_replay_not_shadow_clock, selected_decisions_lt_30, scorecard_missing_exit_ts_for_exit_clock, some_selected_rows_have_no_exit_event`

## Read

- recross_ge_045 is observable in the current scorecard at row/entry scope.
- The current scorecard does not provide an exit_ts field, so a strict exit watch needs a separate exit-event clock or an existing exit-clock join source.
- Do not treat this as a frozen candidate until a pre-registered clock writes post-freeze rows.

## Field Availability

| field | known present | selected present |
|---|---:|---:|
| `entry_ts` | 167 | 15 |
| `market` | 167 | 15 |
| `side` | 167 | 15 |
| `recross_hazard_score` | 167 | 15 |
| `h6_recross_hazard_high` | 167 | 15 |
| `exit_cents` | 140 | 10 |
| `exit_reason` | 140 | 10 |
| `actual_gross_cents` | 167 | 15 |
| `hold_gross_cents` | 167 | 15 |
| `exit_ts` | 0 | 0 |
