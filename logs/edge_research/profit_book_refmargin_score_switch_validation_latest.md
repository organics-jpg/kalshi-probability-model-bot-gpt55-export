# Book Reference-Margin Score Switch Forward Validation

Generated UTC: `20260504_075215Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Locked rule: use book_margin, but switch to score_min60_gap020 when the reference margin per RV sigma is <=0.5.
- This is forward-test evidence only; the regime-switch scan is not promotion evidence.

## Lock

- Label: `book_margin_switch_to_score_min60_gap020_if_reference_margin_per_rv_sigma_15m<=0.5`
- Effective entry boundary: `2026-05-04T04:30:00+00:00`
- Lock file: `logs\edge_research\profit_book_refmargin_score_switch_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 292/295 | 221/71 | 75.68% | 71.46% | 70.45% | -0.010 | 98.98% | 1233.0c | 5.91% | 68.0c |
| recomputed fresh after lock | 9/9 | 6/3 | 66.67% | 71.00% | 35.42% | -0.356 | 100.00% | -39.0c | -6.10% | 69.0c |
| strict registered fresh | 13/14 | 9/4 | 69.23% | 70.62% | 42.37% | -0.282 | 100.00% | -18.0c | -1.96% | 69.0c |

## Recompute Drift Check

- Compared strict and recomputed rows: 9.
- Mismatched rows: 3; missing recomputed rows: 5.
- `KXBTC15M-26MAY040130-30` strict `2026-05-04T05:19:06.925000+00:00 no 62.0c` vs recomputed `2026-05-04T05:17:06.838000+00:00 no 66.0c`.
- `KXBTC15M-26MAY040145-45` strict `2026-05-04T05:35:08.515000+00:00 no 69.0c` vs recomputed `2026-05-04T05:31:08.227000+00:00 no 66.0c`.
- `KXBTC15M-26MAY040245-45` strict `2026-05-04T06:33:13.573000+00:00 yes 71.0c` vs recomputed `2026-05-04T06:32:13.465000+00:00 yes 75.0c`.

## Read

- Strict registered fresh sample is not promotion-quality proof.
- The physical hypothesis is book-pressure fragility when the later score reference has weak RV-scaled margin.
