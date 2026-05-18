# v28 Exit Loss-Guard Threshold Margin Stress

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T11:39:23.116380+00:00`

## Interpretation

- Research-only margin stress; it replays stricter thresholds on already-frozen strict rows.
- This is not a new candidate freeze and does not change any live or watch logic.
- If small threshold moves erase most recovery, the branch should keep collecting before any child-freeze discussion.

## book_gap_loss_guard

- Freeze UTC: `2026-05-06T21:29:32.710906+00:00`
- Best by delta: `as_frozen`
- First positive clean conservative: `value_p86_reduce_p79`

| variant | suppressed | helpful | harmful | net c | delta c | suppression delta c | dropped base | cushion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `as_frozen` | 8 | 8 | 0 | 22.00 | 76.00 | 76.00 | 0 | 0 |
| `value_p86_reduce_p79` | 8 | 8 | 0 | 22.00 | 76.00 | 76.00 | 0 | 0 |
| `value_p88_reduce_p79` | 7 | 7 | 0 | 0.00 | 54.00 | 54.00 | 1 | 0 |
| `value_p90_reduce_p79` | 5 | 5 | 0 | -34.00 | 20.00 | 20.00 | 3 | 0 |
| `value_p85_reduce_p80` | 8 | 8 | 0 | 22.00 | 76.00 | 76.00 | 0 | 0 |
| `value_p88_reduce_p80` | 7 | 7 | 0 | 0.00 | 54.00 | 54.00 | 1 | 0 |
| `gap_positive_2pct` | 8 | 8 | 0 | 22.00 | 76.00 | 76.00 | 0 | 0 |

## book_gap_loss_guard_v3

- Freeze UTC: `2026-05-07T01:01:45.501061+00:00`
- Best by delta: `as_frozen`
- First positive clean conservative: `extreme_p96`

| variant | suppressed | helpful | harmful | net c | delta c | suppression delta c | dropped base | cushion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `as_frozen` | 2 | 2 | 0 | 108.00 | 24.00 | 24.00 | 0 | 1 |
| `extreme_p96` | 2 | 2 | 0 | 108.00 | 24.00 | 24.00 | 0 | 1 |
| `extreme_p97` | 2 | 2 | 0 | 108.00 | 24.00 | 24.00 | 0 | 1 |
| `shallow_drawdown_0` | 1 | 1 | 0 | 86.00 | 2.00 | 2.00 | 1 | 0 |
| `value_p88_extreme_p96` | 1 | 1 | 0 | 86.00 | 2.00 | 2.00 | 1 | 0 |
