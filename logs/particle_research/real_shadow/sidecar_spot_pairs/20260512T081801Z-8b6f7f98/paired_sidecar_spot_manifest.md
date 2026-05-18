# Paired Sidecar Spot Capture

Research-only paired capture of one sidecar collection cycle and independent public BTC spot ticks. It does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T08:18:31.584365+00:00`
- Run id: `20260512T081801Z-8b6f7f98`
- Collect mode: `public-rest`
- Promotion allowed: `False`
- Paired capture ready: `True`
- Sidecar cycle status: `sidecar_cycle_ready_for_external_promotion_verifier`
- Sidecar markets selected / packet rows: `1` / `18`
- Sidecar frozen rows / markets: `3198` / `92`
- Spot feed/status/ticks: `coinbase_btcusd_matches` / `stopped` / `107`
- Alignment ready rows: `1` / `1`

## Alignment

| market | decision ts | latest spot before | age ms | ready | issue |
|---|---|---|---:|---|---|
| `KXBTC15M-26MAY120430-30` | `2026-05-12T08:18:02.544000+00:00` | `2026-05-12T08:18:02.406987+00:00` | 137.013 | `True` | `` |

## Read

- `spot_ready_no_future=True` means a locally received independent spot tick existed at or before the sidecar bundle capture timestamp within the configured freshness limit.
- This artifact proves instrumentation coverage only. It is not a probability, EV, PnL, or promotion result.
