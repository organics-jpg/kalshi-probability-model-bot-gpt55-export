# Research Lab Recording Requirement

Effective 2026-04-26, all new strategy research, shadow candidates, live bot runs, and market observation sessions must be recorded in the Research Lab dataset format.

This is a data-integrity requirement. Do not create a new standalone dataset, ledger, or replay source for strategy promotion unless it is either:

- recorded directly under `research_data/<dataset_tag>/`; or
- explicitly derived from a Research Lab dataset and labeled with its `source_dataset_tag`.

## Required Dataset Shape

Every new live or shadow dataset must have, at minimum:

- `research_data/<dataset_tag>/raw_events/`
- `research_data/<dataset_tag>/book_checkpoints/`
- `research_data/<dataset_tag>/metadata/`

Pipeline-derived folders should be produced by `research_pipeline.py` or a compatible successor:

- `normalized_events/`
- `features/`
- `trade_labels/`
- `replay_runs/`

## Required Metadata Labels

Each dataset must be traceable enough to compare backtests, forward-shadow runs, and live behavior without guessing. Metadata should include:

- `dataset_tag`
- `schema_version`
- `recorder_version`
- `feature_set_version`
- `recorder_type`: `native_passive`, `live_bot_attached`, `shadow`, or `backfill`
- `strategy_tags`
- `live_bot_run_tag`
- `source_dataset_tag` when derived from another Research Lab dataset
- `source_log_paths` when backfilled from logs
- `started_at_utc`
- `ended_at_utc`
- `market_tickers`
- `market_selection_reason`
- `records_raw_market_feed`: boolean
- `records_book_checkpoints`: boolean
- `records_strategy_decisions`: boolean
- `records_execution_events`: boolean
- `records_settlement_labels`: boolean
- `data_quality_flags`

## Backfill Rule

Backfilled datasets are allowed as a stopgap, but they must be labeled as `recorder_type=backfill` and must not be treated as equivalent to native passive recording. If a field was reconstructed from bot logs or execution telemetry rather than recorded from the market stream, that provenance must be visible in metadata.

## Promotion Rule

No new strategy should be promoted from research to live, and no new live market/run should be treated as clean evidence, unless there is a current Research Lab dataset covering the relevant market stream.

Reports under `logs/edge_research/` are still allowed, but they should be analysis artifacts derived from Research Lab datasets, not independent sources of truth.

## Readiness Gate

Before a dataset is used for gauntlet scoring, run:

```powershell
python .\research_lab_readiness.py --dataset <dataset_tag> --strategy-tag <strategy_tag> --write
```

The readiness gate writes:

- `research_data/<dataset_tag>/metadata/dataset_manifest.json`
- `research_data/<dataset_tag>/metadata/gauntlet_tape_schema.json`
- `research_data/<dataset_tag>/metadata/ingestion_watchdog_status.json`
- `research_data/<dataset_tag>/metadata/readiness_status.json`
- `research_data/<dataset_tag>/candidate_specs/gauntlet_candidates.template.json`

The gauntlet should refuse native-live promotion evidence when readiness is `FAIL`. `WARN` can be used for research exploration, but the warning reason must be carried into the report.
