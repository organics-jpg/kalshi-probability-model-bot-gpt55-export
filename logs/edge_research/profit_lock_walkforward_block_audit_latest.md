# Profit Lock Walk-Forward Block Audit

Generated UTC: `20260504_035742Z`

## Scope

- Research-only chronological block diagnostic; no orders are submitted and no bot files or live processes are touched.
- Blocks are sequential groups of `20` recurring BTC 15m markets.
- A robust high-coverage candidate should not depend on one favorable time slice.

## Summary

| dataset | policy | blocks | positive blocks | positive+coverage blocks | total net/ROI | coverage | worst block |
|---|---|---:|---:|---:|---:|---:|---:|
| current | `book_margin` | 14 | 9/64.29% | 9/64.29% | 1201.0c/6.37% | 99.29% | -164.0c |
| current | `book_margin_early` | 14 | 10/71.43% | 10/71.43% | 1231.0c/6.71% | 96.43% | -199.0c |
| current | `book_margin_gap015` | 14 | 9/64.29% | 9/64.29% | 1480.0c/8.87% | 88.93% | -133.0c |
| current | `frontier_v2` | 14 | 9/64.29% | 9/64.29% | 370.0c/2.12% | 99.29% | -460.0c |
| current | `score_min60` | 14 | 10/71.43% | 10/71.43% | 1400.0c/7.04% | 98.93% | -197.0c |
| current | `score_min60_gap020` | 14 | 10/71.43% | 10/71.43% | 1567.0c/7.95% | 98.21% | -197.0c |
| current | `v2_wait_score_min60_brownian70_early` | 14 | 10/71.43% | 10/71.43% | 1492.0c/7.54% | 98.93% | -147.0c |
| current | `v2_wait_score_min60_early` | 14 | 10/71.43% | 10/71.43% | 1419.0c/7.14% | 98.93% | -197.0c |
| v21 | `book_margin` | 11 | 7/63.64% | 7/63.64% | 388.0c/2.56% | 99.09% | -332.0c |
| v21 | `book_margin_early` | 11 | 7/63.64% | 7/63.64% | 682.0c/4.74% | 94.09% | -315.0c |
| v21 | `book_margin_gap015` | 11 | 6/54.55% | 6/54.55% | 269.0c/1.82% | 96.82% | -332.0c |
| v21 | `frontier_v2` | 11 | 9/81.82% | 9/81.82% | 1246.0c/9.15% | 99.09% | -124.0c |
| v21 | `score_min60` | 11 | 7/63.64% | 7/63.64% | 497.0c/3.19% | 98.64% | -228.0c |
| v21 | `score_min60_gap020` | 11 | 7/63.64% | 7/63.64% | 497.0c/3.19% | 98.64% | -228.0c |
| v21 | `v2_wait_score_min60_brownian70_early` | 11 | 7/63.64% | 7/63.64% | 718.0c/4.65% | 98.64% | -193.0c |
| v21 | `v2_wait_score_min60_early` | 11 | 7/63.64% | 7/63.64% | 521.0c/3.35% | 98.64% | -228.0c |

## Worst Blocks

| dataset | policy | block | closes UTC | selected/base | wins/losses | net | ROI |
|---|---|---:|---|---:|---:|---:|---:|
| current | `frontier_v2` | 4 | 2026-05-01T22:30:00+00:00 to 2026-05-02T03:15:00+00:00 | 20/20 | 7/13 | -460.0c | -39.66% |
| v21 | `book_margin` | 8 | 2026-05-02T01:45:00+00:00 to 2026-05-02T06:30:00+00:00 | 20/20 | 10/10 | -332.0c | -24.92% |
| v21 | `book_margin_gap015` | 8 | 2026-05-02T01:45:00+00:00 to 2026-05-02T06:30:00+00:00 | 20/20 | 10/10 | -332.0c | -24.92% |
| v21 | `book_margin_early` | 1 | 2026-04-30T14:00:00+00:00 to 2026-04-30T18:45:00+00:00 | 19/20 | 10/9 | -315.0c | -23.95% |
| v21 | `book_margin_gap015` | 1 | 2026-04-30T14:00:00+00:00 to 2026-04-30T18:45:00+00:00 | 19/20 | 10/9 | -306.0c | -23.43% |
| v21 | `book_margin` | 1 | 2026-04-30T14:00:00+00:00 to 2026-04-30T18:45:00+00:00 | 20/20 | 11/9 | -283.0c | -20.46% |
| v21 | `book_margin_early` | 8 | 2026-05-02T01:45:00+00:00 to 2026-05-02T06:30:00+00:00 | 19/20 | 10/9 | -265.0c | -20.95% |
| v21 | `score_min60` | 3 | 2026-05-01T00:00:00+00:00 to 2026-05-01T05:00:00+00:00 | 20/20 | 12/8 | -228.0c | -15.97% |
| v21 | `score_min60_gap020` | 3 | 2026-05-01T00:00:00+00:00 to 2026-05-01T05:00:00+00:00 | 20/20 | 12/8 | -228.0c | -15.97% |
| v21 | `v2_wait_score_min60_early` | 3 | 2026-05-01T00:00:00+00:00 to 2026-05-01T05:00:00+00:00 | 20/20 | 12/8 | -228.0c | -15.97% |
| v21 | `v2_wait_score_min60_early` | 1 | 2026-04-30T14:00:00+00:00 to 2026-04-30T18:45:00+00:00 | 20/20 | 12/8 | -214.0c | -15.13% |
| v21 | `score_min60_gap020` | 1 | 2026-04-30T14:00:00+00:00 to 2026-04-30T18:45:00+00:00 | 20/20 | 12/8 | -214.0c | -15.13% |
| v21 | `score_min60` | 1 | 2026-04-30T14:00:00+00:00 to 2026-04-30T18:45:00+00:00 | 20/20 | 12/8 | -214.0c | -15.13% |
| current | `book_margin_early` | 10 | 2026-05-03T07:00:00+00:00 to 2026-05-03T11:45:00+00:00 | 19/20 | 11/8 | -199.0c | -15.32% |
| current | `score_min60_gap020` | 0 | 2026-05-01T02:30:00+00:00 to 2026-05-01T07:15:00+00:00 | 20/20 | 12/8 | -197.0c | -14.10% |
| current | `score_min60` | 0 | 2026-05-01T02:30:00+00:00 to 2026-05-01T07:15:00+00:00 | 20/20 | 12/8 | -197.0c | -14.10% |
| current | `v2_wait_score_min60_early` | 0 | 2026-05-01T02:30:00+00:00 to 2026-05-01T07:15:00+00:00 | 20/20 | 12/8 | -197.0c | -14.10% |
| v21 | `score_min60` | 8 | 2026-05-02T01:45:00+00:00 to 2026-05-02T06:30:00+00:00 | 20/20 | 12/8 | -193.0c | -13.85% |
| v21 | `score_min60_gap020` | 8 | 2026-05-02T01:45:00+00:00 to 2026-05-02T06:30:00+00:00 | 20/20 | 12/8 | -193.0c | -13.85% |
| v21 | `v2_wait_score_min60_early` | 8 | 2026-05-02T01:45:00+00:00 to 2026-05-02T06:30:00+00:00 | 20/20 | 12/8 | -193.0c | -13.85% |

## Read

- `book_margin` min positive-block rate/min coverage/worst block: 63.64%/99.09%/-332.0c.
- `book_margin_early` min positive-block rate/min coverage/worst block: 63.64%/94.09%/-315.0c.
- `book_margin_gap015` min positive-block rate/min coverage/worst block: 54.55%/88.93%/-332.0c.
- `frontier_v2` min positive-block rate/min coverage/worst block: 64.29%/99.09%/-460.0c.
- `score_min60` min positive-block rate/min coverage/worst block: 63.64%/98.64%/-228.0c.
- `score_min60_gap020` min positive-block rate/min coverage/worst block: 63.64%/98.21%/-228.0c.
- `v2_wait_score_min60_brownian70_early` min positive-block rate/min coverage/worst block: 63.64%/98.64%/-193.0c.
- `v2_wait_score_min60_early` min positive-block rate/min coverage/worst block: 63.64%/98.64%/-228.0c.
- Block stability is diagnostic only; strict pre-registered live evidence remains the promotion gate.
