# v28 Successor Logged Event Dataset Audit

Research-only dataset built from recorded v28 execution-event outputs with posthoc seed labels attached by market. Live bot state, orders, thresholds, and processes were not touched.

## Summary

- Generated UTC: `2026-05-12T07:29:16Z`
- Rows: `1745`
- Markets: `118`
- Avg YES Brier: `0.14567028417757133`
- Pre-resolution rows by event clock: `1745`
- Forward-promotion rows: `0`
- Leakage status: `pass_for_logged_event_diagnostic_not_promotion`

## Source Labels

- Seed rows read: `795`
- Labeled markets: `176`
- Conflicting label markets: `0`

## Missing Counts

| field | missing rows |
|---|---:|
| `strike` | 0 |
| `decision_ts_utc` | 0 |
| `btc_price` | 0 |
| `book_age_ms` | 0 |
| `d_sigma` | 0 |
| `arrow` | 0 |
| `prior_logged_event_count` | 0 |
| `prior_adverse_path_memory_dollars` | 0 |
| `y_yes_win` | 0 |

## By Event Type

| event type | rows |
|---|---:|
| `mushroom_v28_approved` | 450 |
| `signal_seen` | 450 |
| `plan_built` | 395 |
| `fill_full` | 251 |
| `execution_deferred` | 197 |
| `fill_partial` | 2 |

## Read

- This dataset is richer than the calibration seed for strike, d_sigma, arrow, BTC price, and freshness features.
- It is still diagnostic-only because labels come from the posthoc seed label lookup and no rows are frozen forward registry rows.
- It should be used to develop feature plumbing and sanity checks, not to promote a live candidate.

## Outputs

- Logged rows CSV: `research_particle/v28_successor/causal_rows_logged_events_latest.csv`
- Logged rows JSON: `research_particle/v28_successor/causal_rows_logged_events_latest.json`
