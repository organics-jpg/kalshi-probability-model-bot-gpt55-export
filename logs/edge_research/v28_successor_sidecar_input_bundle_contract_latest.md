# v28 Successor Sidecar Input Bundle Contract

Research-only bundle validator. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:29:34Z`
- Bundle status: `contract_demo_ready_not_evidence`
- Bundle ready: `True`
- Promotion allowed: `False`
- Source input: `generated_template_demo`
- Market: `KXBTC15M-26MAY111210-100000`
- BTC history rows: `66`
- Candidate manifests: `9`
- Forward-collection candidates: `9`
- Simulated: `True`
- Diagnostic only: `True`

## Blockers

| blocker | count |
|---|---:|
| none | 0 |

## Read

- This contract validates the serialized input before packet collection.
- A ready bundle is still not evidence until packet rows are frozen before close and labeled only after resolution.
- Simulated or diagnostic bundles must remain non-promotable.
