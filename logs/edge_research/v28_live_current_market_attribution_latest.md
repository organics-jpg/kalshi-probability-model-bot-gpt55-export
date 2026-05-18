# v28 Live Current Market Attribution

- Generated UTC: `2026-05-11T03:01:39.326753+00:00`
- Market: `KXBTC15M-26MAY071315-15`
- Entry approvals / entry fill events / exit fill events: `4/4/6`
- Active position: `null`
- FIFO realized gross ex-fees: `15c` on `8` exited contracts; open qty `0`
- Exchange status/result: `finalized/yes`
- Settlement-adjusted gross ex-fees: `15c`

## Current Read

- Latest market is KXBTC15M-26MAY071315-15.
- Same-market repeated entries observed: 4 approved v28 entries.
- 4 entries are p70-adjustable FV evidence, but settlement is required before calibration scoring.
- 3 entries have thin edge <4c; track separately from the stronger p70 rows.
- Exchange result is yes with status finalized; open FIFO lots can be settlement-adjusted for attribution.
- Settlement-adjusted gross includes unexited open lots using the exchange result; this is attribution only and does not mutate live bot state.

## Entries

| # | ts | side | ask | p | edge c | abs d | stc | depth | book age | tags |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 2026-05-07T17:06:27.270122+00:00 | yes | 80 | 0.856612 | 2.161168 | 0.914921 | 512.743000 | 73.000000 | 656.000000 | p70_adjustable, live_v28_confident, thin_edge_lt_4c, deep_geometry, middle_time, older_book_500ms |
| 2 | 2026-05-07T17:09:55.259251+00:00 | yes | 78 | 0.851822 | 3.682248 | 0.877186 | 304.741000 | 6.000000 | 656.000000 | p70_adjustable, live_v28_confident, thin_edge_lt_4c, middle_time, older_book_500ms |
| 3 | 2026-05-07T17:10:51.847892+00:00 | yes | 81 | 0.867042 | 2.204219 | 0.927124 | 248.155000 | 1718.000000 | 234.000000 | p70_adjustable, live_v28_confident, thin_edge_lt_4c, deep_geometry, middle_time, crowded_or_deep_touch |
| 4 | 2026-05-07T17:11:41.155680+00:00 | yes | 77 | 0.857305 | 5.230532 | 0.891592 | 198.844000 | 61.000000 | 547.000000 | p70_adjustable, live_v28_confident, edge_ge_4c, middle_time, older_book_500ms |

## Exits

| ts | side | qty | trigger | reason | p hold | fair drawdown | remaining |
|---|---|---:|---:|---|---:|---:|---:|
| 2026-05-07T17:10:38.687635+00:00 | yes | 2 | 77 | mushroom_v28_probability_reduce_single_shot_visible_depth | None | None | 0 |
| 2026-05-07T17:10:38.826835+00:00 | yes | 1 | 77 | mushroom_v28_probability_reduce_single_shot_visible_depth | None | None | 0 |
| 2026-05-07T17:10:46.691539+00:00 | yes | 1 | 78 | mushroom_v28_probability_reduce_single_shot_visible_depth | None | None | 0 |
| 2026-05-07T17:11:27.679428+00:00 | yes | 1 | 75 | mushroom_v28_probability_reduce_single_shot_visible_depth | None | None | 0 |
| 2026-05-07T17:11:27.768179+00:00 | yes | 1 | 75 | mushroom_v28_probability_reduce_single_shot_visible_depth | None | None | 0 |
| 2026-05-07T17:12:13.683555+00:00 | yes | 2 | 94 | mushroom_v28_exit_value_over_hold_single_shot_visible_depth | None | None | 0 |
