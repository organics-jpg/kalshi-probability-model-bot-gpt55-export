# v28 Successor Forward Freeze Preflight

Research-only forward-freeze readiness check. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:30:44Z`
- Preflight status: `blocked`
- Passive rows: `1750`
- Passive markets: `2`
- Open input rows now: `0`
- Registered-before-close rows: `0`
- Freeze-ready rows: `0`
- Freeze-ready markets: `0`
- Forward-collection candidates: `9`
- Forward registry rows: `3126`

## Readiness Blockers

- `insufficient_freeze_ready_markets`
- `insufficient_freeze_ready_rows`
- `market_already_closed_now`
- `missing_btc_state`
- `missing_candidate_prediction`
- `missing_top_book`
- `missing_v28_baseline`
- `row_not_registered_pre_resolution`
- `staging_registration_not_before_close`

## Row Blockers

| blocker | rows |
|---|---:|
| `market_already_closed_now` | 1750 |
| `missing_btc_state` | 1750 |
| `missing_candidate_prediction` | 1750 |
| `missing_top_book` | 128 |
| `missing_v28_baseline` | 1750 |
| `row_not_registered_pre_resolution` | 1750 |
| `staging_registration_not_before_close` | 1750 |

## Blocked Row Sample

| market | side | close | blockers |
|---|---|---|---|
| `KXBTC15M-26MAY110145-45` | `yes` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `no` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `yes` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `no` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `yes` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `no` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `yes` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `no` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `yes` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `no` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `yes` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `no` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `yes` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `no` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `yes` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `no` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `yes` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `no` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `yes` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |
| `KXBTC15M-26MAY110145-45` | `no` | `2026-05-11T05:45:00.000Z` | `market_already_closed_now;row_not_registered_pre_resolution;staging_registration_not_before_close;missing_btc_state;missing_v28_baseline;missing_candidate_prediction` |

## Read

- A row can only freeze when it is still pre-resolution, has market/book/BTC/v28 state, has a frozen candidate prediction, and belongs to a forward-collection candidate manifest.
- The current passive rows are useful staging inputs, but this preflight correctly keeps the frozen registry closed.
