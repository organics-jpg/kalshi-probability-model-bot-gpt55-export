# Paired Sidecar Spot Capture

Research-only paired capture of one sidecar collection cycle and independent public BTC spot ticks. It does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T09:19:29.692848+00:00`
- Run id: `20260512T091859Z-1052e828`
- Collect mode: `public-rest`
- Promotion allowed: `False`
- Paired capture ready: `True`
- Sidecar cycle status: `sidecar_cycle_ready_for_external_promotion_verifier`
- Sidecar markets selected / packet rows: `1` / `18`
- Sidecar frozen rows / markets: `3270` / `96`
- Spot feed/status/ticks: `coinbase_btcusd_matches` / `stopped` / `66`
- Alignment ready rows: `1` / `1`

## Alignment

| market | decision ts | latest spot before | age ms | ready | issue |
|---|---|---|---:|---|---|
| `KXBTC15M-26MAY120530-30` | `2026-05-12T09:19:00.652000+00:00` | `2026-05-12T09:19:00.253504+00:00` | 398.496 | `True` | `` |

## Read

- `spot_ready_no_future=True` means a locally received independent spot tick existed at or before the sidecar bundle capture timestamp within the configured freshness limit.
- This artifact proves instrumentation coverage only. It is not a probability, EV, PnL, or promotion result.
