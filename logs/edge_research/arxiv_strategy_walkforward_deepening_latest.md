# arXiv Candidate Walk-Forward Deepening

Research-only. Multiple walk-forward layouts are used to test whether the candidate families are flukes and to find more stable variants worth freezing forward.

- Generated UTC: `2026-05-07T23:22:21.583918+00:00`
- Matched live trades: `632`
- Schedules: `6`

## Fixed Current Params Across Schedules

| family | all replay PnL | W/L | positive schedules | beat-live schedules | min sched PnL | median sched PnL | params |
|---|---:|---:|---:|---:|---:|---:|---|
| consensus_probability_gap | $10.57 | 49/38 (+2 flat) | 6/6 | 6/6 | 464.0c | 502.0c | `{"max_probability_gap": 0.12, "min_edge_cents": 4.0}` |
| depth_decay_fillability | $21.42 | 57/79 | 6/6 | 6/6 | 1,356.0c | 1,388.0c | `{"max_ask_cents": 80.0, "max_book_age_ms": 750.0, "min_depth_ratio": 3.0, "min_seconds_to_close": 600.0}` |
| brownian_fpt_sanity | $27.37 | 146/172 (+7 flat) | 6/6 | 6/6 | 1,341.0c | 1,399.0c | `{"max_abs_d_sigma": 1.1, "min_abs_d_sigma": 0.7, "min_edge_cents": 3.0, "min_seconds_to_close": 120.0}` |
| hybrid_fpt_depth | $15.85 | 77/85 (+1 flat) | 6/6 | 6/6 | 1,209.0c | 1,215.0c | `{"max_abs_d_sigma": 1.1, "max_ask_cents": 83.0, "max_book_age_ms": 750.0, "min_abs_d_sigma": 0.85, "min_depth_ratio": 8.0, "min_edge_cents": 3.0, "min_seconds_to_close": 120.0}` |

## Dynamic Walk-Forward Selection

Each fold selects params using train-only data, then scores the next window. `stable_subsplit` requires positive evidence in at least two train subwindows.

| family | selection | positive runs | beat-live runs | min run PnL | median run PnL | repeated-window PnL sum | median delta vs live |
|---|---|---:|---:|---:|---:|---:|---:|
| consensus_probability_gap | max_train_net | 1/6 | 3/6 | -627.0c | -299.0c | -1,620.0c | 34.0c |
| consensus_probability_gap | stable_subsplit | 3/6 | 3/6 | -656.0c | 217.0c | 672.0c | 179.0c |
| depth_decay_fillability | max_train_net | 5/6 | 6/6 | -187.0c | 345.5c | 2,186.0c | 619.5c |
| depth_decay_fillability | stable_subsplit | 6/6 | 6/6 | 212.0c | 422.0c | 3,347.0c | 923.0c |
| brownian_fpt_sanity | max_train_net | 1/6 | 6/6 | -119.0c | -43.0c | 784.0c | 428.0c |
| brownian_fpt_sanity | stable_subsplit | 4/6 | 6/6 | -485.0c | 127.0c | 1,135.0c | 588.0c |
| hybrid_fpt_depth | max_train_net | 6/6 | 6/6 | 695.0c | 811.0c | 5,873.0c | 1,250.0c |
| hybrid_fpt_depth | stable_subsplit | 6/6 | 6/6 | 354.0c | 600.0c | 4,316.0c | 1,037.5c |

## Best Robust Replay Variants

These leaders are selected with the full retrospective stress set, so treat them as freeze candidates, not proof.

| family | rank | all replay PnL | W/L | positive schedules | beat-live schedules | min sched PnL | median sched PnL | params |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| consensus_probability_gap | 1 | $11.85 | 51/47 (+4 flat) | 6/6 | 6/6 | 674.0c | 712.0c | `{"max_probability_gap": 0.1, "min_edge_cents": 3.0}` |
| consensus_probability_gap | 2 | $9.39 | 39/35 (+2 flat) | 6/6 | 6/6 | 620.0c | 658.0c | `{"max_probability_gap": 0.1, "min_edge_cents": 4.0}` |
| consensus_probability_gap | 3 | $12.90 | 63/53 (+4 flat) | 6/6 | 6/6 | 505.0c | 543.0c | `{"max_probability_gap": 0.12, "min_edge_cents": 3.0}` |
| consensus_probability_gap | 4 | $10.57 | 49/38 (+2 flat) | 6/6 | 6/6 | 464.0c | 502.0c | `{"max_probability_gap": 0.12, "min_edge_cents": 4.0}` |
| consensus_probability_gap | 5 | $7.49 | 38/34 (+4 flat) | 6/6 | 6/6 | 463.0c | 463.0c | `{"max_probability_gap": 0.08, "min_edge_cents": 3.0}` |
| depth_decay_fillability | 1 | $21.02 | 76/91 | 6/6 | 6/6 | 1,470.0c | 1,546.0c | `{"max_ask_cents": 90.0, "max_book_age_ms": 750.0, "min_depth_ratio": 8.0, "min_seconds_to_close": 600.0}` |
| depth_decay_fillability | 2 | $21.04 | 77/97 | 6/6 | 6/6 | 1,390.0c | 1,466.0c | `{"max_ask_cents": 90.0, "max_book_age_ms": 750.0, "min_depth_ratio": 5.0, "min_seconds_to_close": 600.0}` |
| depth_decay_fillability | 3 | $21.52 | 83/105 | 6/6 | 6/6 | 1,384.0c | 1,460.0c | `{"max_ask_cents": 90.0, "max_book_age_ms": 750.0, "min_depth_ratio": 3.0, "min_seconds_to_close": 600.0}` |
| depth_decay_fillability | 4 | $21.28 | 83/107 | 6/6 | 6/6 | 1,384.0c | 1,448.0c | `{"max_ask_cents": 90.0, "max_book_age_ms": 750.0, "min_depth_ratio": 2.0, "min_seconds_to_close": 600.0}` |
| depth_decay_fillability | 5 | $21.42 | 57/79 | 6/6 | 6/6 | 1,356.0c | 1,388.0c | `{"max_ask_cents": 80.0, "max_book_age_ms": 750.0, "min_depth_ratio": 3.0, "min_seconds_to_close": 600.0}` |
| brownian_fpt_sanity | 1 | $26.17 | 141/167 (+7 flat) | 6/6 | 6/6 | 1,341.0c | 1,419.0c | `{"max_abs_d_sigma": 1.1, "min_abs_d_sigma": 0.8, "min_edge_cents": 3.0, "min_seconds_to_close": 120.0}` |
| brownian_fpt_sanity | 2 | $27.37 | 146/172 (+7 flat) | 6/6 | 6/6 | 1,341.0c | 1,399.0c | `{"max_abs_d_sigma": 1.1, "min_abs_d_sigma": 0.7, "min_edge_cents": 3.0, "min_seconds_to_close": 120.0}` |
| brownian_fpt_sanity | 3 | $27.37 | 146/172 (+7 flat) | 6/6 | 6/6 | 1,341.0c | 1,399.0c | `{"max_abs_d_sigma": 1.1, "min_abs_d_sigma": 0.55, "min_edge_cents": 3.0, "min_seconds_to_close": 120.0}` |
| brownian_fpt_sanity | 4 | $25.39 | 145/170 (+7 flat) | 6/6 | 6/6 | 1,201.0c | 1,321.0c | `{"max_abs_d_sigma": 1.1, "min_abs_d_sigma": 0.8, "min_edge_cents": 3.0, "min_seconds_to_close": 60.0}` |
| brownian_fpt_sanity | 5 | $26.59 | 150/175 (+7 flat) | 6/6 | 6/6 | 1,201.0c | 1,301.0c | `{"max_abs_d_sigma": 1.1, "min_abs_d_sigma": 0.7, "min_edge_cents": 3.0, "min_seconds_to_close": 60.0}` |
| hybrid_fpt_depth | 1 | $24.85 | 99/107 (+3 flat) | 6/6 | 6/6 | 1,779.0c | 1,849.0c | `{"max_abs_d_sigma": 1.1, "max_ask_cents": 85.0, "max_book_age_ms": 750.0, "min_abs_d_sigma": 0.8, "min_depth_ratio": 8.0, "min_edge_cents": 3.0, "min_seconds_to_close": 120.0}` |
| hybrid_fpt_depth | 2 | $26.13 | 104/111 (+3 flat) | 6/6 | 6/6 | 1,779.0c | 1,829.0c | `{"max_abs_d_sigma": 1.1, "max_ask_cents": 85.0, "max_book_age_ms": 750.0, "min_abs_d_sigma": 0.7, "min_depth_ratio": 8.0, "min_edge_cents": 3.0, "min_seconds_to_close": 120.0}` |
| hybrid_fpt_depth | 3 | $24.55 | 98/106 (+3 flat) | 6/6 | 6/6 | 1,715.0c | 1,785.0c | `{"max_abs_d_sigma": 1.1, "max_ask_cents": 83.0, "max_book_age_ms": 750.0, "min_abs_d_sigma": 0.8, "min_depth_ratio": 8.0, "min_edge_cents": 3.0, "min_seconds_to_close": 120.0}` |
| hybrid_fpt_depth | 4 | $25.83 | 103/110 (+3 flat) | 6/6 | 6/6 | 1,715.0c | 1,765.0c | `{"max_abs_d_sigma": 1.1, "max_ask_cents": 83.0, "max_book_age_ms": 750.0, "min_abs_d_sigma": 0.7, "min_depth_ratio": 8.0, "min_edge_cents": 3.0, "min_seconds_to_close": 120.0}` |
| hybrid_fpt_depth | 5 | $26.36 | 107/125 (+5 flat) | 6/6 | 6/6 | 1,687.0c | 1,757.0c | `{"max_abs_d_sigma": 1.1, "max_ask_cents": 85.0, "max_book_age_ms": 750.0, "min_abs_d_sigma": 0.8, "min_depth_ratio": 3.0, "min_edge_cents": 3.0, "min_seconds_to_close": 120.0}` |

## Interpretation

- `fixed current` answers whether yesterday's chosen params were a fluke under alternate walk-forward layouts.
- `dynamic` answers whether train-only selection can rediscover useful params without seeing the eval window.
- `robust replay variants` are useful for deciding what to freeze forward next, but they are still retrospective search results.
