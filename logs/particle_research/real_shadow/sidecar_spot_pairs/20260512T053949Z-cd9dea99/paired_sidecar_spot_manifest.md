# Paired Sidecar Spot Capture

Research-only paired capture of one sidecar collection cycle and independent public BTC spot ticks. It does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T05:40:19.194830+00:00`
- Run id: `20260512T053949Z-cd9dea99`
- Collect mode: `public-rest`
- Promotion allowed: `False`
- Paired capture ready: `True`
- Sidecar cycle status: `sidecar_evidence_scored_no_promotable_candidate`
- Sidecar markets selected / packet rows: `1` / `16`
- Sidecar frozen rows / markets: `2614` / `81`
- Spot feed/status/ticks: `coinbase_btcusd_matches` / `stopped` / `68`
- Alignment ready rows: `1` / `1`

## Alignment

| market | decision ts | latest spot before | age ms | ready | issue |
|---|---|---|---:|---|---|
| `KXBTC15M-26MAY120145-45` | `2026-05-12T05:39:50.140000+00:00` | `2026-05-12T05:39:50.011877+00:00` | 128.123 | `True` | `` |

## Read

- `spot_ready_no_future=True` means a locally received independent spot tick existed at or before the sidecar bundle capture timestamp within the configured freshness limit.
- This artifact proves instrumentation coverage only. It is not a probability, EV, PnL, or promotion result.
