# Paired Sidecar Spot Capture

Research-only paired capture of one sidecar collection cycle and independent public BTC spot ticks. It does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T04:28:41.838303+00:00`
- Run id: `20260512T042831Z-c2afca25`
- Collect mode: `public-rest`
- Promotion allowed: `False`
- Paired capture ready: `True`
- Sidecar cycle status: `sidecar_evidence_scored_no_promotable_candidate`
- Sidecar markets selected / packet rows: `1` / `14`
- Sidecar frozen rows / markets: `2132` / `76`
- Spot feed/status/ticks: `coinbase_btcusd_matches` / `stopped` / `133`
- Alignment ready rows: `1` / `1`

## Alignment

| market | decision ts | latest spot before | age ms | ready | issue |
|---|---|---|---:|---|---|
| `KXBTC15M-26MAY120030-30` | `2026-05-12T04:28:32.787000+00:00` | `2026-05-12T04:28:32.725231+00:00` | 61.769 | `True` | `` |

## Read

- `spot_ready_no_future=True` means a locally received independent spot tick existed at or before the sidecar bundle capture timestamp within the configured freshness limit.
- This artifact proves instrumentation coverage only. It is not a probability, EV, PnL, or promotion result.
