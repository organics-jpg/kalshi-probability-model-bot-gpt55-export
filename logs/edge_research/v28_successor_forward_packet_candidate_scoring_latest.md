# v28 Successor Forward Packet Candidate Scoring

Research-only scorer for frozen collection candidates on packet-shaped rows. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:29:31Z`
- Packet rows: `1506`
- Collection candidates: `9`
- Prediction rows: `13554`
- Freeze-eligible prediction rows: `0`
- Promotion-allowed rows: `0`

## Status Counts

| status | rows |
|---|---:|
| `diagnostic_scored_not_freeze_ready` | 13554 |

## Blockers

| blocker | rows |
|---|---:|
| `incomplete_input_packet:btc_and_feed,v28_baseline` | 13554 |
| `packet_not_registered_before_close` | 5994 |
| `temporal_blockers:is_recomputed_after_resolution_true` | 5994 |

## Read

- The scorer proves frozen simple candidate manifests can be applied to packet rows.
- Current predictions are diagnostic because packet rows are incomplete and/or already closed.
- Freeze and promotion remain blocked until rows are complete, pre-resolution registered, broad enough, and later settled.
