# Paired Sidecar Spot Capture

Research-only paired capture of one sidecar collection cycle and independent public BTC spot ticks. It does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T06:05:56.529035+00:00`
- Run id: `20260512T060526Z-549f3a8f`
- Collect mode: `public-rest`
- Promotion allowed: `False`
- Paired capture ready: `True`
- Sidecar cycle status: `sidecar_evidence_scored_no_promotable_candidate`
- Sidecar markets selected / packet rows: `1` / `16`
- Sidecar frozen rows / markets: `2790` / `83`
- Spot feed/status/ticks: `coinbase_btcusd_matches` / `stopped` / `421`
- Alignment ready rows: `1` / `1`

## Alignment

| market | decision ts | latest spot before | age ms | ready | issue |
|---|---|---|---:|---|---|
| `KXBTC15M-26MAY120215-15` | `2026-05-12T06:05:27.498000+00:00` | `2026-05-12T06:05:27.433959+00:00` | 64.041 | `True` | `` |

## Read

- `spot_ready_no_future=True` means a locally received independent spot tick existed at or before the sidecar bundle capture timestamp within the configured freshness limit.
- This artifact proves instrumentation coverage only. It is not a probability, EV, PnL, or promotion result.
