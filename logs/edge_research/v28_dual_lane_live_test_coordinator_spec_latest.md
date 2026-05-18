# v28 Dual-Lane Live-Test Coordinator Spec

Research-only. No orders placed, no live bot stopped, no live bot logic changed.

- Generated UTC: `2026-05-11T03:47:26.004601+00:00`
- Decision: `coordinator_required_before_live_dual_lane`

## Why A Coordinator Is Required

- The current live bot intentionally allows only one DRY_RUN=false process through `state/live_trading.lock`.
- Running two independent bots would corrupt attribution and could make the two exit state machines fight over one account position.
- Dual-lane is still a research scorer/probe family; it needs a real-time decision adapter before it can submit live orders.

## Current Source Controls

| control | present |
|---|---|
| `single_live_lock` | `True` |
| `dry_run_false_strategy_approval` | `True` |
| `strategy_storage_tags` | `True` |
| `execution_events` | `True` |
| `client_order_id_purpose_prefix` | `True` |
| `single_runtime_position_state` | `True` |

## Same-Window Context

- Candidate policy: `post_dual_union_birth_entry_cheap_penalty025_rank_only`
- Candidate W/L/net: `13/3` / `59c ($0.59)`
- Live v28 same-market W/L/net: `7/7` / `240c ($2.40)`
- Candidate minus live: `-181c ($-1.81)`

## Required Architecture

| component | purpose | must not do |
|---|---|---|
| `DualLaneDecisionAdapter` | Emit a real-time entry/exit decision from the frozen dual-lane rules without reading settled outcomes. | Call post-hoc scorer rows that depend on settlement, reconstructed outcomes, or future exits. |
| `LiveStrategyCoordinator` | Run v28 and dual-lane decision adapters in one process behind the existing live lock. | Start a second DRY_RUN=false bot process or bypass state/live_trading.lock. |
| `VirtualStrategyLedger` | Attribute each order, fill, exit, and settlement to v28 or dual-lane using explicit strategy IDs. | Infer attribution only from market ticker after both strategies can trade the same market. |
| `ConflictArbiter` | Decide what happens when both strategies want the same market, same side, opposite side, or different sizes. | Allow two independent state machines to fight over the same account position. |
| `RiskGovernor` | Enforce size=1 initial dual-lane trades, max open exposure, max daily spend/loss, and emergency disable. | Let the test consume the whole account or assume v28 risk controls cover both strategies. |

## Go/No-Go Gates

| gate | required | current |
|---|---|---|
| `live_lock_respected` | One DRY_RUN=false process holds the lock and coordinates both lanes. | `blocked` |
| `dual_lane_realtime_engine` | Dual-lane entry/exit rules run from current market/BTC/orderbook state only. | `blocked` |
| `attribution` | Every order has lane-specific strategy ID/client_order_id and a fill replay can score each lane separately. | `blocked` |
| `risk_cap` | Dual-lane size=1, configured max spend/loss, and operator-visible disable switch. | `blocked` |
| `evidence_context` | Broad dual-lane no longer trails live v28 or is explicitly limited to overlay/risk-control tests. | `blocked` |

## First Safe Milestone

- Name: `paper_coordinator_replay`
- Description: Build the coordinator and run it in DRY_RUN=true/paper mode while the existing live v28 continues trading.

Success criteria:
- Produces two separate ledgers: v28-live-compatible decisions and dual-lane decisions.
- Does not place orders or alter live bot state.
- Matches existing live v28 entries closely enough to prove the coordinator observes the same market stream.
- Shows dual-lane would have generated real-time actionable orders with no future-data dependencies.

## Next Build Steps

- Extract a side-effect-free v28 decision adapter from the current bot path for paper comparison.
- Implement a side-effect-free dual-lane decision adapter from frozen observable rules only.
- Add a coordinator ledger schema with lane, market, side, action, intended_qty, order_id, client_order_id, fill_qty, fill_price, fees, and exit link.
- Run coordinator in paper mode against live market stream before enabling any dual-lane real orders.
- Only after paper coordinator passes attribution/replay checks, add a single-process live flag for dual-lane size=1 under hard spend/loss caps.
