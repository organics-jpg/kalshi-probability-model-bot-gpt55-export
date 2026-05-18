# v28 Successor Sidecar Packet Collector

Research-only collector bridge. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:29:35Z`
- Collector mode: `demo`
- Collector status: `contract_demo_ready_not_evidence`
- Rows: `18`
- Packet-ready rows: `18`
- Markets: `1`
- Candidate manifests: `9`
- Simulated rows: `18`
- Diagnostic rows: `18`
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

- The demo proves the sidecar collector can emit complete YES/NO packet rows at checkpoint time.
- Input-bundle mode lets a passive recorder write market, checkpoint, BTC history, v28 EdgeBatch, and candidate manifest payloads to disk without importing internals.
- Demo, simulated, diagnostic, or after-the-fact rows must not be frozen or promoted.
- Real collection should run during an open market and then run packet validation, preflight, freeze, registry, label join, and forward evidence scoring.
