# v28 Successor Forward Packet Adapter

Research-only sidecar adapter demo. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:29:31Z`
- Adapter status: `contract_demo_ready`
- Demo rows: `9`
- Demo packet-ready rows: `9`
- Candidate manifests: `9`
- Promotion allowed: `False`

## Missing Groups

| group | rows missing |
|---|---:|
| `identity_and_clock` | 0 |
| `causality` | 0 |
| `market_and_book` | 0 |
| `btc_and_feed` | 0 |
| `v28_baseline` | 0 |
| `candidate_prediction` | 0 |

## Temporal Blockers

| blocker | rows |
|---|---:|

## Read

- The adapter demonstrates the exact sidecar shape future passive collection should emit before close.
- Demo rows are synthetic contract fixtures and must not be promoted or joined as forward evidence.
- Real promotion still requires broad frozen rows captured before settlement and later settled labels.
