# RV600 Sidecar Shadow Root

Research-only derived RV600 input root built from paired sidecar/independent-spot diagnostics.

## Summary

- generated_utc: `2026-05-13T12:02:21+00:00`
- input_root: `logs\particle_research\real_shadow\sidecar_spot_pairs`
- output_root: `logs\particle_research\real_shadow\rv600_sidecar_spot_pairs_forward`
- min_decision_ts_utc: `2026-05-13T05:37:07+00:00`
- diagnostic_files: `83`
- enriched_files: `87`
- candidate_rows_written: `4`
- label_rows_written: `3`
- distinct_markets: `3`

## Guardrails

- one RV600 snapshot is written per market and decision timestamp
- duplicate sidecar model-candidate rows are skipped to avoid replay inflation
- by default only post-lock decisions are written
- this converter writes research artifacts only; it does not touch live bot state or orders

## Skips

- duplicate_snapshot_rows_skipped: `68`
- pre_min_decision_rows_skipped: `1410`
- missing_label_rows_skipped: `0`
- independent_spot_rows_skipped: `0`
- malformed_rows_skipped: `0`
- fetched_label_rows: `4`
