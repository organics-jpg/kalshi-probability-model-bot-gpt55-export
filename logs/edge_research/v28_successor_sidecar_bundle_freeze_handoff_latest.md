# v28 Successor Sidecar Bundle Freeze Handoff

Research-only one-command handoff from sidecar input bundle to packet rows and freeze handoff. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:29:35Z`
- Bundle handoff status: `blocked_non_promotable_bundle_rows`
- Promotion allowed: `False`
- Source input: `generated_template_demo`
- Bundle status: `contract_demo_ready_not_evidence`
- Bundle ready: `True`
- Packet rows: `18`
- Packet markets: `1`
- Simulated packet rows: `18`
- Diagnostic packet rows: `18`
- Freeze handoff status: `blocked_non_promotable_input_rows`
- Frozen prediction rows: `0`
- Registry rows: `0`

## Blockers

- `frozen_registry_below_market_floor`
- `frozen_registry_below_row_floor`
- `input_contains_diagnostic_rows`
- `input_contains_simulated_rows`
- `no_frozen_predictions_from_input`
- `no_preflight_freeze_ready_rows`
- `packet_rows_contain_diagnostic_rows`
- `packet_rows_contain_simulated_rows`

## Read

- Template/demo bundles are intentionally non-promotable.
- Real bundles can produce frozen handoff rows only if captured before close and free of labels, simulation flags, and after-the-fact sources.
- Even successful frozen handoff rows still need post-resolution label join, source contract, forward evidence scoring, and promotion verification.
