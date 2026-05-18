# v28 Exit Reduce Loss-Control Actionability

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:13:40.890722+00:00`

## Interpretation

- This report does not create or promote an exit rule; it classifies which diagnostic separators are usable at decision time.
- Best separator overall is best_post_exit_hold_mark_cents ge 44.0 and is hindsight-only.
- Best observable separator is entry_seconds_to_close le 536.526, selected W/L 11/0, delta 583.0c.
- Best observable separator is already covered by frozen watch v28_frozen_exit_reduce_observable_loss_control_watch_latest.json; current depth opportunity would-suppress rows 8.
- Side-geometry opportunity remains too strict so far: rejected base candidates 7 for -36.0c.

## Observable Separators

| feature | dir | threshold | selected | W/L | delta c | excluded helpful/harmful | actionability | frozen watch |
|---|---|---:|---:|---:|---:|---:|---|---|
| entry_seconds_to_close | le | 536.526000 | 11 | 11/0 | 583.000000 | 9/5 | observable_at_exit | v28_frozen_exit_reduce_observable_loss_control_watch_latest.json |
| entry_seconds_to_close | le | 519.475000 | 10 | 10/0 | 537.000000 | 10/5 | observable_at_exit | v28_frozen_exit_reduce_observable_loss_control_watch_latest.json |
| entry_seconds_to_close | le | 518.045000 | 9 | 9/0 | 475.000000 | 11/5 | observable_at_exit | v28_frozen_exit_reduce_observable_loss_control_watch_latest.json |
| entry_p_side | le | 0.855912 | 8 | 8/0 | 435.000000 | 12/5 | observable_at_exit |  |
| entry_book_age_ms | le | 266.000000 | 8 | 8/0 | 419.000000 | 12/5 | observable_at_exit | v28_frozen_exit_reduce_observable_loss_control_watch_latest.json |
| entry_seconds_to_close | le | 512.735000 | 8 | 8/0 | 415.000000 | 12/5 | observable_at_exit | v28_frozen_exit_reduce_observable_loss_control_watch_latest.json |
| entry_p_side | le | 0.855860 | 7 | 7/0 | 387.000000 | 13/5 | observable_at_exit |  |
| entry_seconds_to_close | le | 471.760000 | 7 | 7/0 | 369.000000 | 13/5 | observable_at_exit | v28_frozen_exit_reduce_observable_loss_control_watch_latest.json |
| exit_d_sigma | le | -0.665824 | 7 | 7/0 | 356.000000 | 13/5 | observable_at_exit |  |
| exit_fair_drawdown_cents | le | -1.645773 | 6 | 6/0 | 355.000000 | 14/5 | observable_at_exit | v28_frozen_exit_reduce_loss_control_refinement_latest.json |
| entry_volshock | ge | 0.673097 | 6 | 6/0 | 339.000000 | 14/5 | observable_at_exit | v28_frozen_exit_reduce_observable_loss_control_watch_latest.json |
| entry_p_side | le | 0.852499 | 6 | 6/0 | 327.000000 | 14/5 | observable_at_exit |  |

## Hindsight-Only Separators

| feature | dir | threshold | selected | W/L | delta c | excluded helpful/harmful | actionability | frozen watch |
|---|---|---:|---:|---:|---:|---:|---|---|
| best_post_exit_hold_mark_cents | ge | 44.000000 | 11 | 11/0 | 603.000000 | 9/5 | hindsight_post_exit |  |
| best_post_exit_hold_mark_cents | ge | 48.000000 | 7 | 7/0 | 391.000000 | 13/5 | hindsight_post_exit |  |
| post_exit_points | ge | 29.000000 | 6 | 6/0 | 355.000000 | 14/5 | hindsight_post_exit |  |
| best_post_exit_hold_mark_cents | ge | 50.000000 | 6 | 6/0 | 343.000000 | 14/5 | hindsight_post_exit |  |
| best_post_exit_hold_mark_cents | ge | 52.000000 | 5 | 5/0 | 283.000000 | 15/5 | hindsight_post_exit |  |

## Observable Separators Needing A Separate Freeze

| feature | dir | threshold | selected | W/L | delta c | excluded helpful/harmful | actionability | frozen watch |
|---|---|---:|---:|---:|---:|---:|---|---|
| entry_p_side | le | 0.855912 | 8 | 8/0 | 435.000000 | 12/5 | observable_at_exit |  |
| entry_p_side | le | 0.855860 | 7 | 7/0 | 387.000000 | 13/5 | observable_at_exit |  |
| exit_d_sigma | le | -0.665824 | 7 | 7/0 | 356.000000 | 13/5 | observable_at_exit |  |
| entry_p_side | le | 0.852499 | 6 | 6/0 | 327.000000 | 14/5 | observable_at_exit |  |
| exit_d_sigma | le | -0.669434 | 6 | 6/0 | 300.000000 | 14/5 | observable_at_exit |  |
| entry_cents | le | 74.000000 | 5 | 5/0 | 281.000000 | 15/5 | observable_at_exit |  |
| entry_p_side | le | 0.851825 | 5 | 5/0 | 273.000000 | 15/5 | observable_at_exit |  |
| exit_btc_age_ms | ge | 532.000000 | 5 | 5/0 | 248.000000 | 15/5 | observable_at_exit |  |
