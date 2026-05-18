# Paired Sidecar Spot Capture

Research-only paired capture of one sidecar collection cycle and independent public BTC spot ticks. It does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T04:36:08.955746+00:00`
- Run id: `20260512T043558Z-57f05abf`
- Collect mode: `public-rest`
- Promotion allowed: `False`
- Paired capture ready: `False`
- Sidecar cycle status: `sidecar_evidence_scored_no_promotable_candidate`
- Sidecar markets selected / packet rows: `1` / `14`
- Sidecar frozen rows / markets: `2160` / `77`
- Spot feed/status/ticks: `coinbase_btcusd_matches` / `stopped` / `35`
- Alignment ready rows: `0` / `1`

## Alignment

| market | decision ts | latest spot before | age ms | ready | issue |
|---|---|---|---:|---|---|
| `KXBTC15M-26MAY120045-45` | `2026-05-12T04:33:57.501000+00:00` | `` |  | `False` | `no_independent_spot_tick_at_or_before_sidecar_capture` |

## Read

- `spot_ready_no_future=True` means a locally received independent spot tick existed at or before the sidecar bundle capture timestamp within the configured freshness limit.
- This artifact proves instrumentation coverage only. It is not a probability, EV, PnL, or promotion result.
