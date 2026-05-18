# v28 Feature-Gate Live Gate Rejection Audit

Research-only. No live bot logic changes, no process control, no orders.

- Generated UTC: `2026-05-07T18:22:37.349478+00:00`
- Strategy/storage: `mushroom_v28_feature_gate_raw05_recross60_abs085_ask65_size1_live` / `live_mushroom_v28_feature_gate_ask65_size1`
- Event path: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\live_mushroom_v28_feature_gate_ask65_size1\execution_events.ndjson`
- Events / decisions / feature rows: `153` / `149` / `149`
- Reasons: `{'edge_below_floor': 66, 'feature_gate': 38, 'book_stale': 16, 'btc_stale': 10, 'risk_or_depth': 10, 'time_window': 8, 'ask_too_high': 1}`
- Gate pass counts: `{'balance_ok': 143, 'btc_ok': 139, 'book_ok': 131, 'risk_ok': 131, 'recross_ok': 75, 'model_price_ok': 60, 'raw_edge_ok': 30, 'ask_ok': 25, 'abs_d_ok': 10}`
- Gate pass rates pct: `{'raw_edge_ok': 20.13422818791946, 'recross_ok': 50.33557046979866, 'abs_d_ok': 6.7114093959731544, 'ask_ok': 16.778523489932887, 'feature_gate_pass': 0.0, 'model_price_ok': 40.26845637583892, 'book_ok': 87.91946308724832, 'btc_ok': 93.28859060402685, 'risk_ok': 87.91946308724832, 'balance_ok': 95.97315436241611}`
- Feature ranges: `{'raw_edge_prob_min_median_max': [-0.247732, 0.011484, 0.237732], 'ask_prob_min_median_max': [0.0, 0.45, 1.0], 'abs_d_min_median_max': [0.002512, 0.203708, 3.938213], 'recross_min_median_max': [0.00033, 0.532047, 1.447477]}`
- Blocker notes: `zero_feature_gate_passes_observed, raw_edge_is_primary_or_secondary_bottleneck, abs_d_boundary_geometry_filters_many_rows, ask_floor_filters_cheap_or_mid_contracts`

## Interpretation

- This report is observational; counterfactual pass counts do not imply fills or profitability.
- If no-ask has many passes but ask65 has zero, the ask floor is the live coverage bottleneck.
- If no-ask also has zero passes, the current market simply did not show the raw-edge plus boundary geometry setup.

## Counterfactual Pass Counts

| variant | ask min | pass count | sides | markets |
|---|---:|---:|---|---|
| `raw05_recross60_abs085_no_ask` | None | 3 | `{'no': 3}` | `['KXBTC15M-26MAY071415-15']` |
| `raw05_recross60_abs085_ask55` | 0.55 | 0 | `{}` | `[]` |
| `raw05_recross60_abs085_ask60` | 0.6 | 0 | `{}` | `[]` |
| `raw05_recross60_abs085_ask65` | 0.65 | 0 | `{}` | `[]` |
| `raw05_recross60_abs085_ask70` | 0.7 | 0 | `{}` | `[]` |
| `frontier_raw03_recross60_abs85_ask35` | 0.35 | 0 | `{}` | `[]` |
| `frontier_raw03_recross60_abs85_ask45` | 0.45 | 0 | `{}` | `[]` |
| `frontier_raw03_recross60_abs85_ask55` | 0.55 | 0 | `{}` | `[]` |

## Top Near Misses

| ts | market | side | reason | ask | raw edge | abs d | recross | p side | edge c |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| `2026-05-07T18:13:44.414844+00:00` | `KXBTC15M-26MAY071415-15` | `no` | `book_stale` | 0.23 | 0.237732 | 0.087323 | 0.117696 | 0.467732 | 21.773218 |
| `2026-05-07T18:13:43.917742+00:00` | `KXBTC15M-26MAY071415-15` | `no` | `feature_gate` | 0.25 | 0.236203 | 0.042283 | 0.123923 | 0.486203 | 21.620344 |
| `2026-05-07T18:13:50.012976+00:00` | `KXBTC15M-26MAY071415-15` | `no` | `time_window` | 0.1 | 0.236031 | 0.410289 | 0.078914 | 0.336031 | 22.603142 |
| `2026-05-07T18:12:43.920930+00:00` | `KXBTC15M-26MAY071415-15` | `no` | `feature_gate` | 0.21 | 0.140269 | 0.379383 | 0.158575 | 0.350269 | 12.026896 |
| `2026-05-07T18:13:16.070634+00:00` | `KXBTC15M-26MAY071415-15` | `no` | `risk_or_depth` | 0.37 | 0.130159 | 0.010392 | 0.174765 | 0.500159 | 11.015918 |
| `2026-05-07T18:08:23.769795+00:00` | `KXBTC15M-26MAY071415-15` | `no` | `risk_or_depth` | 0.14 | 0.126298 | 0.620982 | 0.362052 | 0.266298 | 11.629837 |
| `2026-05-07T18:13:23.915438+00:00` | `KXBTC15M-26MAY071415-15` | `no` | `feature_gate` | 0.33 | 0.122554 | 0.125678 | 0.143988 | 0.452554 | 10.25538 |
| `2026-05-07T18:13:16.419647+00:00` | `KXBTC15M-26MAY071415-15` | `no` | `book_stale` | 0.38 | 0.120152 | 0.010409 | 0.174178 | 0.500152 | 10.015209 |
| `2026-05-07T18:12:38.466312+00:00` | `KXBTC15M-26MAY071415-15` | `no` | `risk_or_depth` | 0.29 | 0.11319 | 0.249614 | 0.187768 | 0.40319 | 9.319038 |
| `2026-05-07T18:09:34.610080+00:00` | `KXBTC15M-26MAY071415-15` | `no` | `risk_or_depth` | 0.19 | 0.108662 | 0.519642 | 0.328535 | 0.298662 | 8.866229 |
| `2026-05-07T18:14:10.024325+00:00` | `KXBTC15M-26MAY071415-15` | `no` | `time_window` | 0.01 | 0.102747 | 1.168573 | 0.026362 | 0.112747 | 9.274723 |
| `2026-05-07T18:12:23.911574+00:00` | `KXBTC15M-26MAY071415-15` | `no` | `feature_gate` | 0.39 | 0.09779 | 0.029462 | 0.258028 | 0.48779 | 7.778961 |
