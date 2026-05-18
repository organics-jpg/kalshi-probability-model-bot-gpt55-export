# Book Margin Delayed Adverse100 Brownian55 Locked Policy Validation

Generated UTC: `20260504_075204Z`

## Scope

- Research-only validation; no orders are submitted and no bot files or live processes are touched.
- Reads an existing forward lock and evaluates the current resolved heartbeat ledger.
- Recomputed fresh metrics can drift when Brownian/RV features are refreshed; strict registered rows are the promotion authority.

## Locked Policy

- Name: `book_margin_delayed_adv100_brownian55`
- Label: `choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; delayed until adverse_move_15m<=100 and brownian_p_rv_15m>=0.55`
- Lock close time: `2026-05-04T04:15:00+00:00`
- Effective entry boundary: `2026-05-04T04:15:00+00:00`
- Lock file: `logs\edge_research\profit_book_margin_delayed_adv100_brownian55_lock.json`

## Metrics

| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all current ledger | 293/295 | 217/76 | 74.06% | 69.19% | 68.75% | -0.004 | 99.32% | 1428.0c | 7.04% | 65.0c |
| recomputed fresh after lock | 10/10 | 5/5 | 50.00% | 69.50% | 23.66% | -0.458 | 100.00% | -195.0c | -28.06% | 67.0c |
| strict registered fresh | 14/15 | 8/6 | 57.14% | 69.93% | 32.59% | -0.373 | 100.00% | -179.0c | -18.28% | 67.0c |

## Recompute Drift Check

- Compared strict and recomputed rows: 10.
- Mismatched rows: 2; missing recomputed rows: 5.
- `KXBTC15M-26MAY040145-45` strict `2026-05-04T05:31:08.227000+00:00 no 66.0c` vs recomputed `2026-05-04T05:30:53.210000+00:00 no 62.0c`.
- `KXBTC15M-26MAY040245-45` strict `2026-05-04T06:35:13.704000+00:00 yes 68.0c` vs recomputed `2026-05-04T06:33:13.573000+00:00 yes 71.0c`.

## Read

- Strict registered fresh sample is not promotion-quality proof.
- Recomputed fresh rows diverge from pre-registered rows; strict registered rows are the promotion authority.
