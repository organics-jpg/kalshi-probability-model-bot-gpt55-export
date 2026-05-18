# v28 Successor Sidecar Collection Cycle

Research-only one-cycle runner for broad sidecar forward evidence. It does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-18T20:50:16Z`
- Cycle status: `sidecar_cycle_ready_for_external_promotion_verifier`
- Collect mode: `public_rest`
- Promotion allowed: `False`
- Sidecar frozen rows / markets: `16896` / `196`
- Sidecar joined rows / markets: `16860` / `195`
- Sidecar clean rows / markets: `16860` / `195`
- Sidecar promotable candidates: `1`

## Blockers

- None recorded by this cycle.

## Next Actions

- Continue to the source contract and promotion verifier.

## Steps

| step | status |
|---|---|
| `public_rest_sidecar_batch` | `batch_bundles_ready_for_freeze` |
| `sidecar_bundle_batch_handoff` | `frozen_batch_handoff_ready_for_settlement_labels` |
| `sidecar_bundle_batch_settlement_labels` | `settlement_labels_available` |
| `sidecar_bundle_batch_label_join` | `joined_batch_labels_available` |
| `sidecar_batch_evidence_score` | `scored_sidecar_batch_evidence` |
| `source_contract` | `promotion_grade` |
| `forward_source_readiness` | `blocked_missing_freeze_ready_sources` |
| `goal_completion_audit` | `complete` |

## Read

- Default collection mode is `none`; it refreshes existing bundle evidence without a new public API capture.
- Use `--collect-mode public-rest --write` only during an explicit pre-close collection attempt.
- This runner keeps sidecar evidence non-canonical and non-promoting by design.
