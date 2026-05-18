# Current Live Strategy OU Exit Overlay Verdict

Generated: 2026-05-14

## Setup

This is a research-only projection. It does not change live bot logic, stop the bot, or place orders.

The test keeps the current live strategy entries fixed and replaces only the exit governor with a Carr-inspired OU profit-taking/stop-loss mesh. Inputs were refreshed through `score_bot_log.py` with Kalshi API accounting before the overlay was rerun.

- Live strategy: `mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live`
- Entries: 95
- Completed round trips from scorer: 86
- Kalshi API accounting: authenticated, 95 entry rows matched, 86 realized exit rows matched
- Overlay usable trades: 95 of 95
- Actual API-reconciled net PnL on overlay trade set: -$7.83

## Projection

| Variant | Same-slice actual PnL | OU-simulation walk-forward PnL | Delta vs actual | Historical-grid walk-forward PnL | Best full-sample grid |
|---|---:|---:|---:|---:|---:|
| Main, 1c slippage, 30s min hold | -$6.60 | -$8.4755 | -$1.8755 | -$7.99 | -$2.79 |
| No slippage sensitivity | -$6.60 | -$6.5590 | +$0.0410 | -$7.33 | -$1.95 |
| No minimum hold sensitivity | -$6.60 | -$10.0500 | -$3.4500 | -$7.99 | -$2.98 |

## Verdict

We can apply this idea as an exit overlay, but the current evidence says not to deploy it.

The paper-style OU simulated selector does not produce a profitable projection on the current live strategy entries. In the realistic main run it performs worse than the actual live exits. Even the hindsight full-sample grid is still negative after the refreshed API accounting, so this is not merely a walk-forward penalty.

The only near-neutral result is the no-slippage OU sensitivity, which lands at -$6.559 versus -$6.60 same-slice actual. That is not a tradable edge; it says friction assumptions can move a few cents, not that the exit governor is profitable.

## Artifacts

- Main report: `docs/research/CURRENT_LIVE_CARR_INSPIRED_EXIT_OVERLAY_BACKTEST.md`
- Main JSON: `logs/particle_research/reports/current_live_carr_inspired_exit_overlay_backtest.json`
- No-slippage JSON: `logs/particle_research/reports/current_live_carr_inspired_exit_overlay_no_slippage.json`
- No-min-hold JSON: `logs/particle_research/reports/current_live_carr_inspired_exit_overlay_no_min_hold.json`
