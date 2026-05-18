# Paired Sidecar Spot Capture

Research-only paired capture of one sidecar collection cycle and independent public BTC spot ticks. It does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T05:47:46.537615+00:00`
- Run id: `20260512T054716Z-d282f3dc`
- Collect mode: `public-rest`
- Promotion allowed: `False`
- Paired capture ready: `True`
- Sidecar cycle status: `sidecar_evidence_scored_no_promotable_candidate`
- Sidecar markets selected / packet rows: `1` / `16`
- Sidecar frozen rows / markets: `2646` / `82`
- Spot feed/status/ticks: `coinbase_btcusd_matches` / `stopped` / `67`
- Alignment ready rows: `1` / `1`

## Alignment

| market | decision ts | latest spot before | age ms | ready | issue |
|---|---|---|---:|---|---|
| `KXBTC15M-26MAY120200-00` | `2026-05-12T05:47:17.512000+00:00` | `2026-05-12T05:47:16.998423+00:00` | 513.577 | `True` | `` |

## Read

- `spot_ready_no_future=True` means a locally received independent spot tick existed at or before the sidecar bundle capture timestamp within the configured freshness limit.
- This artifact proves instrumentation coverage only. It is not a probability, EV, PnL, or promotion result.
