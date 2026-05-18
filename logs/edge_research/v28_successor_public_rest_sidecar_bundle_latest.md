# v28 Successor Public REST Sidecar Bundle

Research-only one-shot sidecar bundle builder. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:29:31.000Z`
- Mode: `fixture`
- Bundle status: `contract_demo_ready_not_evidence`
- Bundle ready: `True`
- Promotion allowed: `False`
- Market: `KXBTC15M-26MAY111210-100000`
- Decision UTC: `2026-05-11T12:00:00.000Z`
- Close UTC: `2026-05-11T12:10:00.000Z`
- BTC history rows: `240`
- Packet rows materialized: `18`
- Output bundle: `research_particle/v28_successor/public_rest_sidecar_bundle_demo_latest.json`

## Blockers

- None recorded by the bundle contract.

## Read

- Fixture mode is deterministic and diagnostic only.
- Public REST mode writes non-simulated sidecar bundles only when explicitly requested.
- A ready bundle still must be frozen before close, labeled after resolution, scored, source-checked, and verifier-approved.
