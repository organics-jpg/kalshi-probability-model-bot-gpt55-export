# Research Data Pipeline Spec

## Purpose

Define a safe, additive research data pipeline for the Kalshi BTC 15-minute bot that:

- records decision-grade market and execution data
- supports deterministic replay and edge tuning
- powers deeper dashboard research views
- does not slow or destabilize the live bot

This spec is the implementation target for the new research stack.

## Goals

- Capture enough raw data to reconstruct what the bot saw and did.
- Preserve exact event ordering, timestamps, fills, fees, and latency metrics.
- Support replay of entries, exits, false stops, partial fills, and reconnect/stale-book scenarios.
- Make large-scale research queries fast and cheap.
- Integrate with the dashboard without breaking the current live views.
- Keep the live trading path lightweight and reversible.

## Non-Goals

- Do not put a heavy analytical database directly on the live websocket hot path.
- Do not replace the current `logs/`, `stats/`, `score_bot_log.py`, or dashboard workflows in one cutover.
- Do not require cloud infrastructure for the first version.
- Do not implement a semantic vector database as the primary store.

## Principles

1. Live trading writes append-only data only.
2. Heavy normalization and feature generation happen asynchronously.
3. Raw event history is the source of truth.
4. Replay must be event-driven and deterministic.
5. Dashboard research views are additive and must not degrade the current Overview experience.
6. The entire system must be incrementally adoptable and easy to disable.

## High-Level Architecture

### 1. Live Capture Layer

Responsibilities:

- capture websocket market data
- capture private order/fill lifecycle data
- capture bot decision telemetry
- capture sparse orderbook checkpoints
- optionally capture BTC spot context from the existing BTC regime feed or a dedicated spot feed

Output:

- append-only raw event files
- checkpoint files

Constraints:

- no heavy database writes on the decision path
- no blocking analytical transforms on the websocket path

### 2. Normalize Layer

Responsibilities:

- convert raw events into typed structured records
- reconstruct orderbook state from snapshot + delta
- derive implied asks from Kalshi's bids-only book representation
- reconcile fills, order status, and bot trade lifecycle
- partition data for fast scans

Output:

- normalized Parquet datasets

### 3. Feature Layer

Responsibilities:

- generate fixed-interval feature tables for research
- attach BTC context, microstructure features, latency features, and trade labels
- preserve per-market and per-trade join keys

Output:

- feature tables
- labeled trade tables

### 4. Replay Layer

Responsibilities:

- deterministic event-driven playback
- configurable latency and fill assumptions
- rule comparisons for entry, stop, and execution changes

Output:

- replay trade tables
- replay summaries
- rule-comparison artifacts

### 5. Dashboard Research Layer

Responsibilities:

- expose research-only tabs backed by the new data pipeline
- keep current dashboard pages operating from the existing `stats/<tag>` outputs
- surface recorder health, replay comparisons, and microstructure studies

## Storage Recommendation

### First Version

- raw live append logs: existing NDJSON plus new research event sinks
- analytical storage: Parquet
- analytical query engine: DuckDB

### Why

- columnar and efficient for scans
- easy local deployment
- simple Python integration
- good fit for Streamlit-backed research views
- lower operational complexity than ClickHouse for v1

### What Not To Use First

- semantic vector database as the primary store
- live transactional database writes from the bot's hot path
- cloud-only architecture

## Filesystem Layout

Add a new root:

- [research_data](C:/Users/organ/Desktop/kalshi%20btc%20bot%20SCALED/research_data)

Recommended layout:

- `research_data/raw_events/type=<event_type>/day=YYYY-MM-DD/hour=HH/part-*.parquet`
- `research_data/book_checkpoints/day=YYYY-MM-DD/market=<ticker>/part-*.parquet`
- `research_data/features/day=YYYY-MM-DD/market=<ticker>/part-*.parquet`
- `research_data/trade_labels/day=YYYY-MM-DD/part-*.parquet`
- `research_data/replay_runs/run_id=<id>/...`
- `research_data/metadata/markets.parquet`
- `research_data/metadata/schema_version.json`

## Data Sources

### Kalshi Public Data

- `orderbook_delta`
- initial `orderbook_snapshot`
- `ticker`
- `trade`

### Kalshi Private Data

- `fill`
- `user_orders`
- `order_group_updates` if used

### Bot Internal Data

- `signal_seen`
- `filter_blocked`
- `plan_built`
- `order_submit_start`
- `order_submit_success`
- `order_submit_reject`
- `fill_partial`
- `fill_full`
- `exit_signal_seen`
- `exit_plan_built`
- `exit_submit_success`
- `execution_deferred`

### Optional BTC Context

- BTC spot price
- BTC short-horizon returns
- BTC range windows

## Raw Event Schema

One row per received or emitted event.

Required columns:

- `dataset_tag`
- `storage_tag`
- `run_id`
- `connection_id`
- `event_type`
- `channel`
- `market_ticker`
- `sequence_number`
- `exchange_ts`
- `local_recv_ts`
- `local_recv_ns`
- `trust_state`
- `payload_json`
- `source`

Notes:

- `exchange_ts` may be blank if not present.
- `local_recv_ts` is mandatory for replay determinism and feed-age studies.
- `payload_json` should remain available for forensic debugging even after normalization.

## Book Checkpoint Schema

Sparse full-depth checkpoints to accelerate replay.

Columns:

- `dataset_tag`
- `market_ticker`
- `checkpoint_ts`
- `sequence_number`
- `yes_bid_prices`
- `yes_bid_sizes`
- `no_bid_prices`
- `no_bid_sizes`
- `source_event_count`

Checkpoint policy:

- on every websocket snapshot
- on reconnect
- periodically every 30-120 seconds per active market
- optionally at entry and exit decision moments

## Feature Table Schema

One row per fixed interval per market.

Base fields:

- `dataset_tag`
- `market_ticker`
- `ts`
- `seconds_to_close`
- `yes_bid`
- `yes_ask`
- `no_bid`
- `no_ask`
- `spread_yes`
- `spread_no`
- `depth_yes_top1`
- `depth_yes_top3`
- `depth_yes_top5`
- `depth_no_top1`
- `depth_no_top3`
- `depth_no_top5`
- `depth_imbalance`
- `book_age_ms`
- `feed_age_ms`
- `local_reaction_ms`
- `trust_state`

Flow fields:

- `last_trade_price`
- `last_trade_size`
- `last_trade_taker_side`
- `trade_count_5s`
- `trade_count_30s`

Derived microstructure fields:

- `same_side_move_5s`
- `same_side_move_30s`
- `same_side_move_60s`
- `same_side_range_30s`
- `same_side_range_60s`
- `top_of_book_flip_rate`
- `depth_collapse_ratio`
- `book_stale_flag`
- `post_reconnect_flag`

BTC fields:

- `btc_spot`
- `btc_return_30s`
- `btc_return_60s`
- `btc_range_1m`
- `btc_range_5m`
- `btc_range_15m`

## Trade Label Schema

One row per completed trade or settlement record.

Columns:

- `dataset_tag`
- `market_ticker`
- `entry_ts`
- `exit_ts`
- `side`
- `qty`
- `entry_fill_price`
- `exit_fill_price`
- `entry_fee_cents`
- `exit_fee_cents`
- `gross_pnl`
- `net_pnl`
- `outcome`
- `settled_result`
- `hold_duration_s`
- `max_adverse_excursion_cents`
- `max_favorable_excursion_cents`
- `false_stop_proxy`
- `false_stop_settled`
- `feed_age_ms_at_entry`
- `book_age_ms_at_entry`
- `local_reaction_ms_at_entry`
- `submit_latency_ms`
- `auth_prep_ms`
- `http_roundtrip_ms`
- `json_parse_ms`
- `post_reconnect_flag`

## Replay Requirements

Replay must:

- process raw events in deterministic local receive order
- reconstruct books from checkpoints plus deltas
- support configurable latency offsets
- support configurable fill models
- support actual fee modeling
- support alternative stop/entry logic
- emit comparable trade tables

Replay outputs:

- simulated trade rows
- summary metrics
- per-trade decision traces
- rule-comparison tables

## Dashboard Integration

The current dashboard must remain stable.

### Existing Pages

Continue to use:

- `stats/<tag>/trades.csv`
- `stats/<tag>/summary.json`
- `stats/<tag>/market_results.csv`
- `logs/<tag>/bot.log`
- `logs/<tag>/execution_events.ndjson`

### New Research Tab

Add a new top-level view:

- `Research Lab`

Sections:

1. `Replay Compare`
- compare baseline strategy vs candidate rule variants
- show win rate, net pnl, false-stop rate, average hold, slippage

2. `Microstructure`
- inspect pre-entry and pre-exit book conditions
- depth collapse studies
- spread and imbalance distributions
- reconnect/stale-book effects

3. `False Stop Lab`
- analyze false stops by hold duration, depth, BTC regime, and latency
- compare alternative stop delays and panic levels

4. `Feature Explorer`
- compare wins vs losses across selected features
- rank conditions associated with bad outcomes

5. `Data Health`
- recorder freshness
- missing channel detection
- checkpoint lag
- ingestion lag
- schema version

### Dashboard Query Layer

Use DuckDB against Parquet files for the new research views.

Requirements:

- separate cache path from current Overview caches
- lightweight summary queries for first render
- lazy-load heavier comparisons
- keep current Overview refresh cadence independent of research queries

## Implementation Phases

### Phase 1. Recorder Foundation

- add a research recorder module
- write raw events and checkpoints
- do not alter existing scorer/dashboard behavior

Deliverables:

- raw Parquet event sink
- checkpoint Parquet sink
- schema version file

### Phase 2. Normalize and Features

- normalize raw events into research tables
- build first feature tables
- add labeled trade joins

Deliverables:

- feature generation script
- labeled trade table
- DuckDB helper layer

### Phase 3. Replay Engine

- implement deterministic replay
- support configurable latency/fill assumptions
- produce replay comparison outputs

Deliverables:

- replay runner
- replay result schema
- rule-comparison output tables

### Phase 4. Dashboard Research Lab

- add `Research Lab` tab
- expose replay and microstructure views
- expose data health panel

### Phase 5. Edge-Tuning Workflows

- false-stop optimization workflows
- latency regime analysis
- drift monitoring
- feature ranking and avoid-condition analysis

## Operational Safety

- recorder failures must not stop trading
- research writes must be append-only and buffered
- ingestion can lag without affecting live trading
- schema versioning is mandatory
- replay and feature generation must be reproducible

## Success Criteria

- any traded market can be reconstructed from raw events
- replay can reproduce a day of decisions deterministically
- per-trade pre-entry and pre-exit features are queryable
- dashboard can compare rule variants without touching live bot logic
- no measurable degradation to live trade responsiveness

## Recommended First Implementation

Build in this order:

1. `research_data/raw_events`
2. `research_data/book_checkpoints`
3. DuckDB query helpers
4. `Research Lab` dashboard stub

Do not begin with:

- ClickHouse
- a vector database
- a full replay engine before raw capture is stable
