# Research Lab Gauntlet Readiness

The strategy gauntlet must consume Research Lab datasets, not ad hoc strategy logs.

This readiness layer adds the control plane the gauntlet needs before it scores any candidate:

- `metadata/dataset_manifest.json`: provenance, recorder type, source logs, strategy tags, and data-quality flags.
- `metadata/gauntlet_tape_schema.json`: required columns for feature, candidate-decision, fillability, and outcome-label tapes.
- `metadata/ingestion_watchdog_status.json`: raw/checkpoint freshness, latest timestamps, file gaps, and tape counts.
- `metadata/readiness_status.json`: machine-readable preflight status.
- `candidate_specs/gauntlet_candidates.template.json`: frozen-candidate spec template.
- `logs/edge_research/codex_dwell_execution_integrity_research_lab_readiness_<dataset>_*.md`: human-readable audit report.

## Status Meanings

- `PASS`: dataset has raw events, book checkpoints, metadata, feature tape, and gauntlet schema coverage.
- `WARN`: dataset exists but needs pipeline rebuilds, candidate decision tapes, fillability tapes, labels, or freshness review before promotion.
- `FAIL`: dataset is missing raw events or book checkpoints, so it cannot be treated as native passive evidence.

Backfilled datasets can be useful, but they should not be mixed with native passive recording without explicit provenance.

## Recommended Flow

1. Ensure a live or shadow run writes `raw_events/` and `book_checkpoints/`.
2. Run `research_pipeline.py --dataset <dataset>` or `research_ingestor.py --dataset <dataset>`.
3. Run:

```powershell
python .\research_lab_readiness.py --dataset <dataset> --strategy-tag <strategy> --write
```

4. Copy the candidate template into a versioned candidate spec and freeze it.
5. Run gauntlet scoring only after the readiness status is acceptable for the test purpose.

## Anti-Leakage Rule

Candidate decisions may use only fields whose `available_at` timestamp is less than or equal to the decision timestamp. Settlement and PnL fields are labels only.

If a field was reconstructed from bot logs rather than recorded passively, keep that provenance in the dataset manifest.
