# Kinetic Fresh Failure Attribution

Generated UTC: `20260503_100353Z`

## Scope

- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.
- Uses only pre-registered kinetic-family signals and bot quote paths.
- Post-loss explanations are diagnostics only; they do not update any lock.

## Fresh Kinetic Registry State

| lock | resolved | wins/losses | net P&L |
|---|---:|---:|---:|
| `kinetic_guard` | 29 | 23/6 | 344.0c |
| `kinetic_price_guard` | 27 | 19/8 | 167.0c |
| `kinetic_touch` | 30 | 22/8 | 215.0c |

## Loss Rows

| lock | market | entry | side | ask | outcome | book | brownian15 | adverse15 | touch_loss15 | kinetic | net |
|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| `kinetic_guard` | `KXBTC15M-26MAY022345-45` | `2026-05-03 03:30:48.459000+00:00` | no | 52.0c | yes | 0.515 | 0.681 | 0.0c | 0.639 | 0.591 | -54.0c |
| `kinetic_price_guard` | `KXBTC15M-26MAY022345-45` | `2026-05-03 03:30:48.459000+00:00` | no | 52.0c | yes | 0.515 | 0.681 | 0.0c | 0.639 | 0.591 | -54.0c |
| `kinetic_touch` | `KXBTC15M-26MAY022345-45` | `2026-05-03 03:30:48.459000+00:00` | no | 52.0c | yes | 0.515 | 0.681 | 0.0c | 0.639 | 0.591 | -54.0c |
| `kinetic_guard` | `KXBTC15M-26MAY030330-30` | `2026-05-03 07:17:10.413000+00:00` | no | 61.0c | yes | 0.605 | 0.553 | 0.0c | 0.894 | 0.608 | -63.0c |
| `kinetic_price_guard` | `KXBTC15M-26MAY030330-30` | `2026-05-03 07:17:10.413000+00:00` | no | 61.0c | yes | 0.605 | 0.553 | 0.0c | 0.894 | 0.608 | -63.0c |
| `kinetic_touch` | `KXBTC15M-26MAY030330-30` | `2026-05-03 07:17:10.413000+00:00` | no | 61.0c | yes | 0.605 | 0.553 | 0.0c | 0.894 | 0.608 | -63.0c |
| `kinetic_guard` | `KXBTC15M-26MAY030430-30` | `2026-05-03 08:16:00.800000+00:00` | yes | 65.0c | no | 0.645 | 0.607 | 0.0c | 0.786 | 0.647 | -67.0c |
| `kinetic_price_guard` | `KXBTC15M-26MAY030430-30` | `2026-05-03 08:16:00.800000+00:00` | yes | 65.0c | no | 0.645 | 0.607 | 0.0c | 0.786 | 0.647 | -67.0c |
| `kinetic_touch` | `KXBTC15M-26MAY030430-30` | `2026-05-03 08:16:00.800000+00:00` | yes | 65.0c | no | 0.645 | 0.607 | 0.0c | 0.786 | 0.647 | -67.0c |
| `kinetic_guard` | `KXBTC15M-26MAY030445-45` | `2026-05-03 08:34:02.927000+00:00` | no | 66.0c | yes | 0.655 | 0.668 | 0.0c | 0.665 | 0.676 | -68.0c |
| `kinetic_price_guard` | `KXBTC15M-26MAY030445-45` | `2026-05-03 08:34:02.927000+00:00` | no | 66.0c | yes | 0.655 | 0.668 | 0.0c | 0.665 | 0.676 | -68.0c |
| `kinetic_touch` | `KXBTC15M-26MAY030445-45` | `2026-05-03 08:34:02.927000+00:00` | no | 66.0c | yes | 0.655 | 0.668 | 0.0c | 0.665 | 0.676 | -68.0c |
| `kinetic_price_guard` | `KXBTC15M-26MAY030500-00` | `2026-05-03 08:49:04.453000+00:00` | yes | 59.0c | no | 0.585 | 0.593 | 0.0c | 0.814 | 0.564 | -61.0c |
| `kinetic_touch` | `KXBTC15M-26MAY030500-00` | `2026-05-03 08:49:04.453000+00:00` | yes | 59.0c | no | 0.585 | 0.593 | 0.0c | 0.814 | 0.564 | -61.0c |
| `kinetic_guard` | `KXBTC15M-26MAY030515-15` | `2026-05-03 09:00:35.435000+00:00` | no | 54.0c | yes | 0.530 | 0.659 | 0.0c | 0.681 | 0.641 | -56.0c |
| `kinetic_price_guard` | `KXBTC15M-26MAY030515-15` | `2026-05-03 09:00:35.435000+00:00` | no | 54.0c | yes | 0.530 | 0.659 | 0.0c | 0.681 | 0.641 | -56.0c |
| `kinetic_touch` | `KXBTC15M-26MAY030515-15` | `2026-05-03 09:00:35.435000+00:00` | no | 54.0c | yes | 0.530 | 0.659 | 0.0c | 0.681 | 0.641 | -56.0c |
| `kinetic_price_guard` | `KXBTC15M-26MAY030545-45` | `2026-05-03 09:34:38.805000+00:00` | no | 66.0c | yes | 0.655 | 0.694 | 69.7c | 0.613 | 0.657 | -68.0c |
| `kinetic_touch` | `KXBTC15M-26MAY030545-45` | `2026-05-03 09:32:08.508000+00:00` | no | 73.0c | yes | 0.725 | 0.605 | 87.5c | 0.791 | 0.610 | -75.0c |
| `kinetic_guard` | `KXBTC15M-26MAY030600-00` | `2026-05-03 09:46:09.804000+00:00` | no | 71.0c | yes | 0.705 | 0.604 | 0.0c | 0.793 | 0.675 | -73.0c |
| `kinetic_price_guard` | `KXBTC15M-26MAY030600-00` | `2026-05-03 09:48:09.938000+00:00` | no | 63.0c | yes | 0.620 | 0.612 | 29.5c | 0.777 | 0.583 | -65.0c |
| `kinetic_touch` | `KXBTC15M-26MAY030600-00` | `2026-05-03 09:46:09.804000+00:00` | no | 71.0c | yes | 0.705 | 0.604 | 0.0c | 0.793 | 0.675 | -73.0c |

## Feature Means

| feature | wins mean | losses mean | loss - win |
|---|---:|---:|---:|
| `ask_cents` | 64.781 | 61.636 | -3.145 |
| `book_p_side` | 0.641 | 0.610 | -0.031 |
| `brownian_p_rv_15m` | 0.634 | 0.628 | -0.006 |
| `brownian_p_rv_30m` | 0.630 | 0.618 | -0.013 |
| `margin_per_rv_sigma_15m` | 0.346 | 0.328 | -0.019 |
| `adverse_move_15m` | 9.289 | 8.484 | -0.805 |
| `touch_loss_rv_15m` | 0.732 | 0.745 | 0.013 |
| `kinetic_touch_score_15` | 0.635 | 0.628 | -0.007 |
| `seconds_to_close` | 737.935 | 773.642 | 35.708 |

## Quote Path Checkpoints

### `KXBTC15M-26MAY022345-45`

- Quote count after entry: 56
- Side mid at entry/min/max after entry: 48.5c / 0.0c / 48.5c
- Opposite side max after entry: 100.0c

| offset sec | timestamp | YES mid | NO mid | chosen side mid | opposite mid |
|---:|---|---:|---:|---:|---:|
| 0 | `2026-05-03 03:31:03+00:00` | 51.5c | 48.5c | 48.5c | 51.5c |
| 60 | `2026-05-03 03:32:03+00:00` | 66.0c | 34.0c | 34.0c | 66.0c |
| 180 | `2026-05-03 03:34:03+00:00` | 83.5c | 16.5c | 16.5c | 83.5c |
| 300 | `2026-05-03 03:36:03+00:00` | 92.0c | 8.0c | 8.0c | 92.0c |
| 600 | `2026-05-03 03:40:49+00:00` | 96.5c | 3.5c | 3.5c | 96.5c |
| 840 | `2026-05-03 03:44:49+00:00` | 100.0c | 0.0c | 0.0c | 100.0c |

### `KXBTC15M-26MAY030330-30`

- Quote count after entry: 51
- Side mid at entry/min/max after entry: 60.0c / 0.0c / 60.5c
- Opposite side max after entry: 100.0c

| offset sec | timestamp | YES mid | NO mid | chosen side mid | opposite mid |
|---:|---|---:|---:|---:|---:|
| 0 | `2026-05-03 07:17:25+00:00` | 40.0c | 60.0c | 60.0c | 40.0c |
| 60 | `2026-05-03 07:18:25+00:00` | 51.0c | 49.0c | 49.0c | 51.0c |
| 180 | `2026-05-03 07:20:25+00:00` | 44.5c | 55.5c | 55.5c | 44.5c |
| 300 | `2026-05-03 07:22:25+00:00` | 78.5c | 21.5c | 21.5c | 78.5c |
| 600 | `2026-05-03 07:27:11+00:00` | 99.0c | 1.0c | 1.0c | 99.0c |

### `KXBTC15M-26MAY030430-30`

- Quote count after entry: 55
- Side mid at entry/min/max after entry: 64.5c / 0.0c / 75.5c
- Opposite side max after entry: 100.0c

| offset sec | timestamp | YES mid | NO mid | chosen side mid | opposite mid |
|---:|---|---:|---:|---:|---:|
| 0 | `2026-05-03 08:16:15+00:00` | 64.5c | 35.5c | 64.5c | 35.5c |
| 60 | `2026-05-03 08:17:15+00:00` | 72.0c | 28.0c | 72.0c | 28.0c |
| 180 | `2026-05-03 08:19:01+00:00` | 66.5c | 33.5c | 66.5c | 33.5c |
| 300 | `2026-05-03 08:21:01+00:00` | 65.5c | 34.5c | 65.5c | 34.5c |
| 600 | `2026-05-03 08:26:01+00:00` | 48.0c | 52.0c | 48.0c | 52.0c |

### `KXBTC15M-26MAY030445-45`

- Quote count after entry: 43
- Side mid at entry/min/max after entry: 70.5c / 0.0c / 79.5c
- Opposite side max after entry: 100.0c

| offset sec | timestamp | YES mid | NO mid | chosen side mid | opposite mid |
|---:|---|---:|---:|---:|---:|
| 0 | `2026-05-03 08:34:17+00:00` | 29.5c | 70.5c | 70.5c | 29.5c |
| 60 | `2026-05-03 08:35:03+00:00` | 20.5c | 79.5c | 79.5c | 20.5c |
| 180 | `2026-05-03 08:37:03+00:00` | 49.0c | 51.0c | 51.0c | 49.0c |
| 300 | `2026-05-03 08:39:03+00:00` | 62.5c | 37.5c | 37.5c | 62.5c |
| 600 | `2026-05-03 08:44:03+00:00` | 97.0c | 3.0c | 3.0c | 97.0c |

### `KXBTC15M-26MAY030515-15`

- Quote count after entry: 57
- Side mid at entry/min/max after entry: 52.5c / 0.5c / 78.5c
- Opposite side max after entry: 99.5c

| offset sec | timestamp | YES mid | NO mid | chosen side mid | opposite mid |
|---:|---|---:|---:|---:|---:|
| 0 | `2026-05-03 09:00:50+00:00` | 47.5c | 52.5c | 52.5c | 47.5c |
| 60 | `2026-05-03 09:01:50+00:00` | 35.5c | 64.5c | 64.5c | 35.5c |
| 180 | `2026-05-03 09:03:50+00:00` | 37.5c | 62.5c | 62.5c | 37.5c |
| 300 | `2026-05-03 09:05:50+00:00` | 39.5c | 60.5c | 60.5c | 39.5c |
| 600 | `2026-05-03 09:10:36+00:00` | 93.5c | 6.5c | 6.5c | 93.5c |
| 840 | `2026-05-03 09:14:36+00:00` | 96.5c | 3.5c | 3.5c | 96.5c |

### `KXBTC15M-26MAY030600-00`

- Quote count after entry: 55
- Side mid at entry/min/max after entry: 71.5c / 0.5c / 78.5c
- Opposite side max after entry: 99.5c

| offset sec | timestamp | YES mid | NO mid | chosen side mid | opposite mid |
|---:|---|---:|---:|---:|---:|
| 0 | `2026-05-03 09:46:24+00:00` | 28.5c | 71.5c | 71.5c | 28.5c |
| 60 | `2026-05-03 09:47:24+00:00` | 25.5c | 74.5c | 74.5c | 25.5c |
| 180 | `2026-05-03 09:49:10+00:00` | 39.5c | 60.5c | 60.5c | 39.5c |
| 300 | `2026-05-03 09:51:10+00:00` | 46.5c | 53.5c | 53.5c | 46.5c |
| 600 | `2026-05-03 09:56:10+00:00` | 74.5c | 25.5c | 25.5c | 74.5c |

### `KXBTC15M-26MAY030500-00`

- Quote count after entry: 43
- Side mid at entry/min/max after entry: 50.0c / 0.0c / 63.5c
- Opposite side max after entry: 100.0c

| offset sec | timestamp | YES mid | NO mid | chosen side mid | opposite mid |
|---:|---|---:|---:|---:|---:|
| 0 | `2026-05-03 08:49:19+00:00` | 50.0c | 50.0c | 50.0c | 50.0c |
| 60 | `2026-05-03 08:50:19+00:00` | 59.5c | 40.5c | 59.5c | 40.5c |
| 180 | `2026-05-03 08:52:19+00:00` | 37.5c | 62.5c | 37.5c | 62.5c |
| 300 | `2026-05-03 08:54:19+00:00` | 21.5c | 78.5c | 21.5c | 78.5c |
| 600 | `2026-05-03 08:59:05+00:00` | 0.0c | 100.0c | 0.0c | 100.0c |

### `KXBTC15M-26MAY030545-45`

- Quote count after entry: 41
- Side mid at entry/min/max after entry: 49.5c / 0.0c / 53.5c
- Opposite side max after entry: 100.0c

| offset sec | timestamp | YES mid | NO mid | chosen side mid | opposite mid |
|---:|---|---:|---:|---:|---:|
| 0 | `2026-05-03 09:34:53+00:00` | 50.5c | 49.5c | 49.5c | 50.5c |
| 60 | `2026-05-03 09:35:53+00:00` | 62.5c | 37.5c | 37.5c | 62.5c |
| 180 | `2026-05-03 09:37:39+00:00` | 63.5c | 36.5c | 36.5c | 63.5c |
| 300 | `2026-05-03 09:39:39+00:00` | 97.5c | 2.5c | 2.5c | 97.5c |
| 600 | `2026-05-03 09:44:39+00:00` | 100.0c | 0.0c | 0.0c | 100.0c |

### `KXBTC15M-26MAY030600-00`

- Quote count after entry: 47
- Side mid at entry/min/max after entry: 58.0c / 0.5c / 68.0c
- Opposite side max after entry: 99.5c

| offset sec | timestamp | YES mid | NO mid | chosen side mid | opposite mid |
|---:|---|---:|---:|---:|---:|
| 0 | `2026-05-03 09:48:24+00:00` | 42.0c | 58.0c | 58.0c | 42.0c |
| 60 | `2026-05-03 09:49:10+00:00` | 39.5c | 60.5c | 60.5c | 39.5c |
| 180 | `2026-05-03 09:51:10+00:00` | 46.5c | 53.5c | 53.5c | 46.5c |
| 300 | `2026-05-03 09:53:10+00:00` | 63.5c | 36.5c | 36.5c | 63.5c |
| 600 | `2026-05-03 09:58:10+00:00` | 84.5c | 15.5c | 15.5c | 84.5c |

### `KXBTC15M-26MAY030545-45`

- Quote count after entry: 51
- Side mid at entry/min/max after entry: 71.5c / 0.0c / 84.5c
- Opposite side max after entry: 100.0c

| offset sec | timestamp | YES mid | NO mid | chosen side mid | opposite mid |
|---:|---|---:|---:|---:|---:|
| 0 | `2026-05-03 09:32:23+00:00` | 28.5c | 71.5c | 71.5c | 28.5c |
| 60 | `2026-05-03 09:33:23+00:00` | 18.5c | 81.5c | 81.5c | 18.5c |
| 180 | `2026-05-03 09:35:23+00:00` | 60.5c | 39.5c | 39.5c | 60.5c |
| 300 | `2026-05-03 09:37:23+00:00` | 65.0c | 35.0c | 35.0c | 65.0c |
| 600 | `2026-05-03 09:42:09+00:00` | 95.0c | 5.0c | 5.0c | 95.0c |

## Read

- The latest loss is a live-path failure: the selected side was cheap and physically plausible at entry, but the order book flipped rapidly and stayed flipped.
- A book-floor repair would have avoided this loss, but separate cross-split diagnostics show that book floors are not yet stable enough to promote without their own future lock.
