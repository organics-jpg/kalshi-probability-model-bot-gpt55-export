# Paired Sidecar Spot Capture

Research-only paired capture of one sidecar collection cycle and independent public BTC spot ticks. It does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T19:06:51.130008+00:00`
- Run id: `20260512T190636Z-de79eb7f`
- Collect mode: `public-rest`
- Promotion allowed: `False`
- Paired capture ready: `True`
- Sidecar cycle status: `sidecar_cycle_ready_for_external_promotion_verifier`
- Sidecar markets selected / packet rows: `1` / `18`
- Sidecar frozen rows / markets: `3810` / `126`
- Spot feed/status/ticks: `coinbase_btcusd_matches` / `stopped` / `126`
- Alignment ready rows: `1` / `1`

## Alignment

| market | decision ts | latest spot before | age ms | ready | issue |
|---|---|---|---:|---|---|
| `KXBTC15M-26MAY121515-15` | `2026-05-12T19:06:37.096000+00:00` | `2026-05-12T19:06:36.778924+00:00` | 317.076 | `True` | `` |

## Read

- `spot_ready_no_future=True` means a locally received independent spot tick existed at or before the sidecar bundle capture timestamp within the configured freshness limit.
- This artifact proves instrumentation coverage only. It is not a probability, EV, PnL, or promotion result.
