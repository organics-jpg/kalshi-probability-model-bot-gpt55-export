# Paired Sidecar Spot Capture

Research-only paired capture of one sidecar collection cycle and independent public BTC spot ticks. It does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T18:49:17.764015+00:00`
- Run id: `20260512T184902Z-0d41a88e`
- Collect mode: `public-rest`
- Promotion allowed: `False`
- Paired capture ready: `True`
- Sidecar cycle status: `sidecar_cycle_ready_for_external_promotion_verifier`
- Sidecar markets selected / packet rows: `1` / `18`
- Sidecar frozen rows / markets: `3792` / `125`
- Spot feed/status/ticks: `coinbase_btcusd_matches` / `stopped` / `185`
- Alignment ready rows: `1` / `1`

## Alignment

| market | decision ts | latest spot before | age ms | ready | issue |
|---|---|---|---:|---|---|
| `KXBTC15M-26MAY121500-00` | `2026-05-12T18:49:03.735000+00:00` | `2026-05-12T18:49:02.956470+00:00` | 778.530 | `True` | `` |

## Read

- `spot_ready_no_future=True` means a locally received independent spot tick existed at or before the sidecar bundle capture timestamp within the configured freshness limit.
- This artifact proves instrumentation coverage only. It is not a probability, EV, PnL, or promotion result.
