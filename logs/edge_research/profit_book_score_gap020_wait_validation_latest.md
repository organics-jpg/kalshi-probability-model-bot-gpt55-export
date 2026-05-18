# Book Score Gap020 Wait Validation

Generated UTC: `20260504_075208Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- The locked candidate requires an early book-margin setup, then waits for a later score_min60_gap020 row.
- Recomputed fresh metrics can drift; strict registered rows are the promotion authority.

## Locked Policy

- Name: `book_score_gap020_wait`
- Wait rule: `book_margin_wait_for_score_min60_gap020_enter_ref_if_seconds_to_close>=480`
- Lock close time: `2026-05-04T02:45:00+00:00`
- Effective entry boundary: `2026-05-04T02:45:00+00:00`
- Lock file: `logs\edge_research\profit_book_score_gap020_wait_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 292/295 | 221/71 | 75.68% | 71.25% | 70.45% | -0.008 | 98.98% | 1295.0c | 6.22% | 68.0c |
| recomputed fresh after lock | 16/16 | 9/7 | 56.25% | 71.69% | 33.18% | -0.385 | 100.00% | -247.0c | -21.53% | 69.0c |
| strict registered fresh | 20/21 | 12/8 | 60.00% | 70.90% | 38.66% | -0.322 | 100.00% | -218.0c | -15.37% | 69.0c |

## Recompute Drift Check

- Compared strict and recomputed rows: 16.
- Mismatched rows: 4; missing recomputed rows: 5.
- `KXBTC15M-26MAY032330-30` strict `2026-05-04T03:18:11.263000+00:00 no 61.0c` vs recomputed `2026-05-04T03:19:11.329000+00:00 no 69.0c`.
- `KXBTC15M-26MAY040130-30` strict `2026-05-04T05:19:06.925000+00:00 no 62.0c` vs recomputed `2026-05-04T05:17:06.838000+00:00 no 66.0c`.
- `KXBTC15M-26MAY040145-45` strict `2026-05-04T05:35:08.515000+00:00 no 69.0c` vs recomputed `2026-05-04T05:31:08.227000+00:00 no 66.0c`.
- `KXBTC15M-26MAY040245-45` strict `2026-05-04T06:33:13.573000+00:00 yes 71.0c` vs recomputed `2026-05-04T06:32:13.465000+00:00 yes 75.0c`.

## Read

- Strict registered fresh sample is not promotion-quality proof.
