# OU Mispricing Strategy Test Verdict

Generated: 2026-05-14

## Idea

Option #1 treats Kalshi probability mispricing as the OU state:

`z = Kalshi YES mid - Brownian fair YES`

The strategy enters when the market is meaningfully cheap/rich versus fair value, then uses the OU simulation to pick PT/SL/max-hold exits. This is a new strategy hypothesis, not a paper-exact Carr/Lopez de Prado replication.

## Refreshed Main Tape Results

Input tape:

- Events: `logs/live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live/execution_events.ndjson`
- Market results: `stats/mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api/market_results.csv`
- Snapshots after sampling/filtering: 13,712
- Markets observed: 213

| Variant | Entry gates | Trades | Net PnL | Win rate | Avg/trade | Notes |
|---|---|---:|---:|---:|---:|---|
| Default | z>=4c, raw edge>=1.5c, sim EV>=1c, loss prob<=0.58, spread<=6c | 139 | +$12.15 | 53.24% | +8.74c | Broadest coverage |
| Strict | z>=6c, raw edge>=3c, sim EV>=2c, loss prob<=0.52, spread<=4c | 115 | +$8.49 | 51.30% | +7.38c | Still positive, less coverage |
| Very strict | z>=8c, raw edge>=4c, sim EV>=3c, loss prob<=0.48, spread<=3c | 98 | +$13.76 | 58.16% | +14.04c | Best risk/quality profile |

## Time Split

| Variant | Q1 | Q2 | Q3 | Q4 |
|---|---:|---:|---:|---:|
| Default | +$3.19 | +$2.48 | +$5.64 | +$0.84 |
| Strict | +$1.75 | +$4.16 | +$4.11 | -$1.53 |
| Very strict | +$2.05 | +$1.75 | +$6.26 | +$3.70 |

## Secondary Tape Sanity Check

Input tape:

- Events: `logs/live_mushroom_v28_common_clock_phi_reward_memory_size2_live/execution_events.ndjson`
- Market results: `stats/mushroom_v28_common_clock_phi_reward_memory_size2_live/market_results.csv`
- Markets observed: 20

| Variant | Trades | Net PnL | Win rate | Avg/trade |
|---|---:|---:|---:|---:|
| Default | 14 | +$0.71 | 50.00% | +5.07c |
| Strict | 14 | +$1.11 | 50.00% | +7.93c |

## Diagnostics

- The edge is not coming from the old live entries. This is a new entry rule over Kalshi mispricing residuals.
- The current main tape result is strongest under the very strict gate, which is a good sign: higher selectivity improved average PnL instead of merely reducing sample.
- The result is heavily NO-side driven on the main tape. Very strict produced +$11.84 on NO trades and +$1.92 on YES trades.
- Take-profit exits were strongly positive, settlement exits were also positive, and max-hold exits were mildly negative.
- The secondary tape is positive but too small to prove robustness.

## Verdict

This is worth forward shadowing as a standalone strategy candidate.

The best current candidate is the very strict configuration, not the broad default. It has the best PnL, win rate, average trade, and all four chronological quarters are positive on the refreshed main tape.

This is still not ready for live trading. It needs pre-registered forward shadow evidence on fresh BTC15M markets, plus stricter fillability checks before it can be considered tradable.

## Recommended Forward Shadow Candidate

Use the very strict gate:

- `entry_z_min = 8`
- `min_raw_edge_cents = 4`
- `min_sim_ev_cents = 3`
- `max_loss_prob = 0.48`
- `max_spread_cents = 3`
- `pt_values = 3,5,8,12,18,25`
- `sl_values = 4,8,12,20,35,55`
- `hold_values = 30,60,120,240,480`

Forward validation should report:

- accepted entries
- would-fill price and spread
- shadow exits
- realized/settled PnL after fees
- side split
- quarter/day split
- comparison against no-trade and current live baseline

## Forward Shadow Started

A very-strict research-only shadow was started after the backtest refresh.

- PID: 28268
- Status: `logs/particle_research/ou_mispricing_forward_shadow_very_strict/status.json`
- Decisions: `logs/particle_research/ou_mispricing_forward_shadow_very_strict/decisions.ndjson`
- Current status at startup check: `research_only=true`, `places_orders=false`, `events_written=0`, `open_positions=0`
- Caveat: the source execution log was stale at offset 282748900, so this shadow will stay quiet until fresh snapshots appear.
