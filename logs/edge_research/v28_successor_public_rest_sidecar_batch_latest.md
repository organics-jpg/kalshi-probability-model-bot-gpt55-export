# v28 Successor Public REST Sidecar Batch

Research-only batch sidecar bundle builder. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-18T20:53:06.000Z`
- Mode: `public_rest`
- Batch status: `batch_bundles_ready_for_freeze`
- Promotion allowed: `False`
- Markets selected: `1`
- Ready bundle files: `1`
- Packet rows: `18`
- Packet markets: `1`

## Markets

| market | close | strike | status | packet rows | output |
|---|---|---:|---|---:|---|
| `KXBTC15M-26MAY181700-00` | `2026-05-18T21:00:00.000Z` | 76917.02 | `input_bundle_ready_for_collection` | 18 | `research_particle/v28_successor/sidecar_input_bundles/20260518T205305790Z_KXBTC15M-26MAY181700-00.json` |

## Read

- Fixture mode is deterministic and diagnostic only.
- Public REST mode is explicit and writes real non-simulated bundles for later pre-close freezing.
- A ready batch still must be frozen before close, labeled after resolution, scored, source-checked, and verifier-approved.
