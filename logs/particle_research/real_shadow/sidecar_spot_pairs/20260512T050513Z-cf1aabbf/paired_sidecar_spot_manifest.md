# Paired Sidecar Spot Capture

Research-only paired capture of one sidecar collection cycle and independent public BTC spot ticks. It does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T05:05:43.967994+00:00`
- Run id: `20260512T050513Z-cf1aabbf`
- Collect mode: `public-rest`
- Promotion allowed: `False`
- Paired capture ready: `True`
- Sidecar cycle status: `sidecar_evidence_scored_no_promotable_candidate`
- Sidecar markets selected / packet rows: `2` / `32`
- Sidecar frozen rows / markets: `2342` / `79`
- Spot feed/status/ticks: `coinbase_btcusd_matches` / `stopped` / `79`
- Alignment ready rows: `2` / `2`

## Alignment

| market | decision ts | latest spot before | age ms | ready | issue |
|---|---|---|---:|---|---|
| `KXBTC15M-26MAY111210-100000` | `2026-05-12T05:05:43+00:00` | `2026-05-12T05:05:42.801043+00:00` | 198.957 | `True` | `` |
| `KXBTC15M-26MAY111210-100500` | `2026-05-12T05:05:43+00:00` | `2026-05-12T05:05:42.801043+00:00` | 198.957 | `True` | `` |

## Read

- `spot_ready_no_future=True` means a locally received independent spot tick existed at or before the sidecar bundle capture timestamp within the configured freshness limit.
- This artifact proves instrumentation coverage only. It is not a probability, EV, PnL, or promotion result.
