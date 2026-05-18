# v28 Dual-Lane Freeze Collection Monitor

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:46:13.723316+00:00`
- Freeze UTC: `2026-05-07T13:00:17.363339+00:00`
- Freeze local time: `2026-05-07T09:00:17.363339-04:00`
- Live baseline: `-256c ($-2.56)`
- Blocker: `none`

## Sample Clock

- Possible 15m windows since freeze: `347`
- Windows remaining to 30-row gate: `0`
- Earliest possible 30-window sample UTC: `2026-05-07T20:30:17.363339+00:00`
- Earliest possible 30-window sample local time: `2026-05-07T16:30:17.363339-04:00`

## Shadow Collection

- Total shadow events: `26023`
- Post-freeze shadow events: `2842`
- Post-freeze reconstructed entry rows: `26`
- Post-freeze distinct markets: `15`
- Post-freeze exit-clock rows: `26`
- Settled post-freeze exit-clock rows: `26`
- Pending post-freeze exit-clock rows: `0`

## Own-Freeze Score Snapshot

| policy | settled | W/L | coverage | net | recon | cushion | live ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `post_dual_union_birth_entry_cheap_penalty025_rank_only` | 14 | 12/2 | 77.77777777777777% | 49c ($0.49) | 14.29% | 0 | `False` | settled_lt_30, full_loss_cushion_lt_3 |
| `post_dual_union_birth_bridge_cheap_penalty025_rank_only` | 14 | 12/2 | 77.77777777777777% | 49c ($0.49) | 14.29% | 0 | `False` | settled_lt_30, full_loss_cushion_lt_3 |

## Recent Post-Freeze Rows

| market | side | entry UTC | exit UTC | status | result | actual | hold | exit reason |
|---|---|---|---|---|---|---:|---:|---|
| `KXBTC15M-26MAY071130-30` | no | `2026-05-07T15:18:39.003964+00:00` | `` | finalized | no | 30c ($0.30) | 30c ($0.30) |  |
| `KXBTC15M-26MAY071145-45` | yes | `2026-05-07T15:31:46.752356+00:00` | `2026-05-07T15:42:14.190856+00:00` | finalized | yes | 44c ($0.44) | 46c ($0.46) | mushroom_v28_exit_value_over_hold |
| `KXBTC15M-26MAY071200-00` | no | `2026-05-07T15:57:45.898203+00:00` | `2026-05-07T15:58:16.718230+00:00` | finalized | no | 42c ($0.42) | 46c ($0.46) | mushroom_v28_exit_value_over_hold |
| `KXBTC15M-26MAY071215-15` | no | `2026-05-07T16:07:13.004846+00:00` | `2026-05-07T16:08:26.386908+00:00` | finalized | no | -16c ($-0.16) | 32c ($0.32) | mushroom_v28_probability_reduce |
| `KXBTC15M-26MAY071215-15` | no | `2026-05-07T16:08:28.013065+00:00` | `2026-05-07T16:08:58.509728+00:00` | finalized | no | 2c ($0.02) | 44c ($0.44) | mushroom_v28_exit_value_over_hold |
| `KXBTC15M-26MAY071215-15` | no | `2026-05-07T16:08:58.574979+00:00` | `2026-05-07T16:09:39.381902+00:00` | finalized | no | -8c ($-0.08) | 40c ($0.40) | mushroom_v28_probability_reduce |
| `KXBTC15M-26MAY071230-30` | yes | `2026-05-07T16:23:06.093545+00:00` | `2026-05-07T16:23:37.942874+00:00` | finalized | yes | -10c ($-0.10) | 46c ($0.46) | mushroom_v28_probability_reduce |
| `KXBTC15M-26MAY071230-30` | yes | `2026-05-07T16:23:59.966329+00:00` | `2026-05-07T16:24:30.935590+00:00` | finalized | yes | -38c ($-0.38) | 32c ($0.32) | mushroom_v28_probability_collapse_full |
| `KXBTC15M-26MAY071230-30` | yes | `2026-05-07T16:24:52.871742+00:00` | `` | finalized | yes | 40c ($0.40) | 40c ($0.40) |  |
| `KXBTC15M-26MAY071315-15` | yes | `2026-05-07T17:06:27.372033+00:00` | `2026-05-07T17:10:38.168558+00:00` | finalized | yes | -6c ($-0.06) | 40c ($0.40) | mushroom_v28_probability_reduce |
| `KXBTC15M-26MAY071315-15` | yes | `2026-05-07T17:10:51.288944+00:00` | `2026-05-07T17:11:27.190018+00:00` | finalized | yes | -14c ($-0.14) | 38c ($0.38) | mushroom_v28_probability_reduce |
| `KXBTC15M-26MAY071315-15` | yes | `2026-05-07T17:11:28.526206+00:00` | `2026-05-07T17:12:12.158487+00:00` | finalized | yes | 32c ($0.32) | 44c ($0.44) | mushroom_v28_exit_value_over_hold |

## Interpretation

- This is a collection monitor, not a strategy scorecard.
- The own-freeze scorecard remains authoritative for live readiness.
- A waiting-for-min-window blocker means evidence cannot be mature yet, even if shadow events are arriving.
