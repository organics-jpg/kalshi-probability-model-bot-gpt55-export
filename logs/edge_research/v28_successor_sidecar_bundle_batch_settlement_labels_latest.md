# v28 Successor Sidecar Batch Settlement Labels

Research-only label fetch for sidecar batch frozen rows. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-18T20:50:16.000Z`
- Label fetch status: `settlement_labels_available`
- Promotion allowed: `False`
- Frozen rows: `16896`
- Frozen markets: `196`
- Label rows: `195`
- Label markets: `195`
- Fetched label rows this run: `195`
- Preserved existing label rows: `195`

## Blockers

- `market_not_closed`: `1`

## Read

- The fetcher refuses to label markets before their frozen close time.
- Labels are written to a sidecar batch file, not the canonical promotion ledger.
- A label row still needs label-join validation, source contract, evidence scoring, and promotion verification.
