# v28 Successor Sidecar Bundle Batch Handoff

Research-only batch handoff for broad sidecar bundle collection. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-18T20:53:05Z`
- Batch handoff status: `frozen_batch_handoff_ready_for_settlement_labels`
- Promotion allowed: `False`
- Bundle directory: `research_particle/v28_successor/sidecar_input_bundles`
- Input bundle files: `1056`
- Ready bundle files: `1055`
- Packet rows: `16914`
- Packet markets: `196`
- Frozen prediction rows: `16914`
- Registry rows: `16914`
- Registry markets: `196`

## Blockers

- `bundle_blocker:market_not_btc15m_boundary`

## Bundle Status Counts

| status | files |
|---|---:|
| `blocked` | 1 |
| `input_bundle_ready_for_collection` | 1055 |

## Read

- Drop real pre-close sidecar input bundle JSON files into the bundle directory, then rerun this handoff.
- The CLI preserves valid existing frozen batch rows by default so post-close refreshes cannot erase pre-close evidence.
- Empty, simulated, diagnostic, after-the-fact, or label-contaminated batches remain non-promotable.
- Even successful frozen batch rows still need post-resolution label join, source contract, forward evidence scoring, and promotion verification.
