# v28 Dual-Lane Own-Freeze Watch

Research-only. No live bot changes or orders.

- Generated UTC: `2026-05-11T03:46:12.127187+00:00`
- Freeze UTC: `2026-05-07T13:00:17.363339+00:00`
- Freeze local time: `2026-05-07T09:00:17.363339-04:00`
- Live baseline: `-255.99c`
- Possible 15m windows since freeze: `347`
- Windows remaining to 30-row sample gate: `0`
- Earliest possible 30-window sample UTC: `2026-05-07T20:30:17.363339+00:00`
- Earliest possible 30-window sample local time: `2026-05-07T16:30:17.363339-04:00`
- Pre-sample short-circuit: `False`
- Manual force replay: `False`

## Interpretation

- Research-only own-freeze dual-lane watch; no live bot changes or orders.
- This is the frozen-forward birth for the top-component parent-fill repair plus continuous cheap-side penalty union.
- Best own-freeze union has 14 settled, W/L 12/2, net 49.0c, coverage 77.77777777777777%, source share 0.14285714285714285, blockers ['settled_lt_30', 'full_loss_cushion_lt_3'].

## Live-Ready Requirements

- Settled own-freeze rows: `>= 30`
- Coverage: `75.0%` to `90.0%`
- Reconstructed/rejected share: `<= 35.0%`
- Full-loss cushion: `>= 3`
- Net PnL must beat refreshed live baseline: `>-255.99c`
- Evidence must be strict post-freeze only: `true`

## Diagnostic Reference

| context | primary | sidecar | settled | W/L | coverage | net | recon | cushion | sidecar add | shared | blockers |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| best diagnostic | `rescue_drop15_exit_clock_rows_only` | `post_penalty_birth_entry_cheap_penalty025_rank_only` | 83 | 68/15 | 82.18% | 1842c ($18.43) | 21.69% | 18 | 177c ($1.77) | 27 | needs_own_frozen_forward_birth, live_ready_false |
| best strict/post context | `post_feature_freeze_entry_quarter_midprice_boundary` | `post_penalty_birth_entry_cheap_penalty025_rank_only` | 65 | 51/13 | 84.42% | 464c ($4.64) | 33.85% | 4 | 83c ($0.83) | 33 | needs_own_frozen_forward_birth, live_ready_false |

## Own-Freeze Unions

| rank | sidecar | settled | W/L | coverage | net | recon | cushion | sidecar add | shared | live ready | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `post_dual_union_birth_entry_cheap_penalty025_rank_only` | 14 | 12/2 | 77.78% | 49c ($0.49) | 14.29% | 0 | 0c ($0.00) | 0 | `False` | settled_lt_30, full_loss_cushion_lt_3 |
| 2 | `post_dual_union_birth_bridge_cheap_penalty025_rank_only` | 14 | 12/2 | 77.78% | 49c ($0.49) | 14.29% | 0 | 0c ($0.00) | 0 | `False` | settled_lt_30, full_loss_cushion_lt_3 |
