# v28 Successor Forward Registry

Research-only frozen-prediction registry scaffold. It does not touch live bot state, orders, thresholds, or processes.

## Summary

- Generated UTC: `2026-05-18T20:51:42Z`
- Registry status: `active`
- Registry rows: `16896`
- Registry markets: `196`
- Feature rows eligible for forward promotion: `0`
- Candidate manifests: `10`
- Forward-collection candidates: `9`
- Passive staging rows: `1750`
- Passive staging registered before close: `0`
- Forward-freeze preflight status: `blocked`
- Freeze-ready rows: `0`
- Frozen prediction rows: `16896`
- Packet-ready rows: `0`
- Promotion ready: `True`

## Inputs

- Frozen forward predictions: `research_particle/v28_successor/frozen_forward_predictions_latest.csv`
- Features: `research_particle/v28_successor/features_latest.csv`
- Candidate predictions: `research_particle/v28_successor/candidate_predictions_latest.csv`
- Candidate manifests: `research_particle/v28_successor/candidate_manifests_latest.json`

## Blockers

- settled label join and forward evidence scoring are still required before promotion.

## Read

- This file is the handoff point for future pre-resolution predictions.
- The current run correctly registers zero predictions because every current row is diagnostic/posthoc.
- Promotion remains impossible until rows are frozen before settlement and later scored after settlement.

## Outputs

- Registry CSV: `research_particle/v28_successor/forward_registry_latest.csv`
- Registry JSON: `research_particle/v28_successor/forward_registry_latest.json`
