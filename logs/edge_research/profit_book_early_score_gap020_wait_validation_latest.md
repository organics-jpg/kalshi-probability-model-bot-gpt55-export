# Book Early Score Gap020 Wait Validation

Generated UTC: `20260504_075208Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- The locked candidate requires an early book-margin setup, then waits for a later score_min60_gap020 row.
- Recomputed fresh metrics can drift; strict registered rows are the promotion authority.

## Locked Policy

- Name: `book_early_score_gap020_wait`
- Wait rule: `book_margin_early_wait_for_score_min60_gap020_enter_ref_if_seconds_to_close>=480`
- Lock close time: `2026-05-04T02:00:00+00:00`
- Effective entry boundary: `2026-05-04T02:00:00+00:00`
- Lock file: `logs\edge_research\profit_book_early_score_gap020_wait_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 284/295 | 216/68 | 76.06% | 71.39% | 70.77% | -0.006 | 96.27% | 1325.0c | 6.54% | 68.0c |
| recomputed fresh after lock | 19/19 | 12/7 | 63.16% | 72.58% | 41.04% | -0.315 | 100.00% | -179.0c | -12.98% | 69.0c |
| strict registered fresh | 23/24 | 15/8 | 65.22% | 71.17% | 44.89% | -0.263 | 100.00% | -137.0c | -8.37% | 69.0c |

## Recompute Drift Check

- Compared strict and recomputed rows: 19.
- Mismatched rows: 5; missing recomputed rows: 5.
- `KXBTC15M-26MAY032230-30` strict `2026-05-04T02:18:05.671000+00:00 no 66.0c` vs recomputed `2026-05-04T02:17:05.641000+00:00 no 79.0c`.
- `KXBTC15M-26MAY032330-30` strict `2026-05-04T03:18:11.263000+00:00 no 61.0c` vs recomputed `2026-05-04T03:19:11.329000+00:00 no 69.0c`.
- `KXBTC15M-26MAY040130-30` strict `2026-05-04T05:19:06.925000+00:00 no 62.0c` vs recomputed `2026-05-04T05:17:06.838000+00:00 no 66.0c`.
- `KXBTC15M-26MAY040145-45` strict `2026-05-04T05:35:08.515000+00:00 no 69.0c` vs recomputed `2026-05-04T05:31:08.227000+00:00 no 66.0c`.
- `KXBTC15M-26MAY040245-45` strict `2026-05-04T06:33:13.573000+00:00 yes 71.0c` vs recomputed `2026-05-04T06:32:13.465000+00:00 yes 75.0c`.

## Read

- Strict registered fresh sample is not promotion-quality proof.
