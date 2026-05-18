# v28 Feature-Gate Side-Displacement Guard

Research-only settled-row replay. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T11:31:58.142648+00:00`
- Candidate source UTC: `2026-05-07T11:17:29.409489+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Live baseline: `821c`

## Interpretation

- Research-only same-market side-displacement guard scan; no live bot changes or orders.
- The guard is observable: when a cheap selected side conflicts with a same-market opposite side that passes the ask65 core, prefer the high-ask side.
- The broad any-ask65 replacement is not attractive because it includes the known 67c ask false-positive loser.
- The narrower ask>=85 over cheap/sub50 guards improve source quality and some PnL, but they still do not solve broad coverage or live-baseline gates.

## post_feature_freeze_entry

- Future denominator: `57`

| rank | policy | entries | settled replay | W/L | coverage | net | delta live | replay recon | cushion | replacements | repl delta |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `raw03_recross70_abs075_ask85_over_cheap10_priority` | 42 | 42 | 28/11 | 73.68% | 357c | -464c | 0.357 | 3 | 4 | 51c |
| 2 | `raw03_recross70_abs075_ask85_over_sub50_priority` | 42 | 42 | 28/11 | 73.68% | 357c | -464c | 0.357 | 3 | 4 | 51c |
| 3 | `raw05_recross60_abs085_ask85_over_cheap10_priority` | 36 | 36 | 26/8 | 63.16% | 350c | -471c | 0.250 | 3 | 4 | 51c |
| 4 | `raw05_recross60_abs085_ask85_over_sub50_priority` | 36 | 36 | 26/8 | 63.16% | 350c | -471c | 0.250 | 3 | 4 | 51c |
| 5 | `raw03_recross70_abs075_control` | 42 | 42 | 25/15 | 73.68% | 306c | -515c | 0.452 | 3 | 0 | 0c |
| 6 | `raw05_recross60_abs085_control` | 36 | 36 | 23/12 | 63.16% | 299c | -522c | 0.361 | 2 | 0 | 0c |
| 7 | `raw03_recross70_abs075_ask65_any_conflict_priority` | 42 | 42 | 27/12 | 73.68% | 230c | -591c | 0.357 | 2 | 5 | -76c |
| 8 | `raw05_recross60_abs085_ask65_any_conflict_priority` | 36 | 36 | 25/9 | 63.16% | 223c | -598c | 0.250 | 2 | 5 | -76c |

### Best Policy Replacements: `raw03_recross70_abs075_ask85_over_cheap10_priority`

| market | old side | old ask | old net | new side | new ask | new net | delta |
|---|---|---:|---:|---|---:|---:|---:|
| `KXBTC15M-26MAY061415-15` | `yes` | 0.020 | -3c | `no` | 0.880 | 10c | 13c |
| `KXBTC15M-26MAY061830-30` | `yes` | 0.050 | -6c | `no` | 0.890 | 0c | 6c |
| `KXBTC15M-26MAY062245-45` | `no` | 0.040 | -5c | `yes` | 0.860 | 13c | 18c |
| `KXBTC15M-26MAY062300-00` | `no` | 0.010 | -2c | `yes` | 0.870 | 12c | 14c |

## post_feature_freeze_bridge

- Future denominator: `58`

| rank | policy | entries | settled replay | W/L | coverage | net | delta live | replay recon | cushion | replacements | repl delta |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `raw05_recross60_abs085_ask85_over_cheap10_priority` | 36 | 36 | 28/8 | 62.07% | 375c | -446c | 0.250 | 3 | 4 | 60c |
| 2 | `raw05_recross60_abs085_ask85_over_sub50_priority` | 36 | 36 | 28/8 | 62.07% | 375c | -446c | 0.250 | 3 | 4 | 60c |
| 3 | `raw05_recross60_abs085_control` | 36 | 36 | 24/12 | 62.07% | 315c | -506c | 0.361 | 3 | 0 | 0c |
| 4 | `raw03_recross70_abs075_ask85_over_cheap10_priority` | 42 | 42 | 30/12 | 72.41% | 314c | -507c | 0.357 | 3 | 4 | 60c |
| 5 | `raw03_recross70_abs075_ask85_over_sub50_priority` | 42 | 42 | 30/12 | 72.41% | 314c | -507c | 0.357 | 3 | 4 | 60c |
| 6 | `raw03_recross70_abs075_control` | 42 | 42 | 26/16 | 72.41% | 254c | -567c | 0.452 | 2 | 0 | 0c |
| 7 | `raw05_recross60_abs085_ask65_any_conflict_priority` | 36 | 36 | 27/9 | 62.07% | 248c | -573c | 0.250 | 2 | 5 | -67c |
| 8 | `raw03_recross70_abs075_ask65_any_conflict_priority` | 42 | 42 | 29/13 | 72.41% | 187c | -634c | 0.357 | 1 | 5 | -67c |

### Best Policy Replacements: `raw05_recross60_abs085_ask85_over_cheap10_priority`

| market | old side | old ask | old net | new side | new ask | new net | delta |
|---|---|---:|---:|---|---:|---:|---:|
| `KXBTC15M-26MAY061415-15` | `yes` | 0.020 | -3c | `no` | 0.880 | 10c | 13c |
| `KXBTC15M-26MAY061830-30` | `yes` | 0.050 | -6c | `no` | 0.890 | 9c | 15c |
| `KXBTC15M-26MAY062245-45` | `no` | 0.040 | -5c | `yes` | 0.860 | 13c | 18c |
| `KXBTC15M-26MAY062300-00` | `no` | 0.010 | -2c | `yes` | 0.870 | 12c | 14c |
