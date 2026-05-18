# Key Policy Registry/Recompute Audit

Generated UTC: `20260504_155442Z`

## Scope

- Research-only audit; no orders are submitted and no live bot files or processes are touched.
- Compares immutable registered rows with recomputed selections from the latest resolved physics ledger.
- Recompute-only improvement is not promotion evidence; it can reflect later candle/physics availability.

## Summary

| policy | registry W/L/net | recompute W/L/net | common | common net delta | mismatches | side/win | registry-only/recompute-only |
|---|---:|---:|---:|---:|---:|---:|---:|
| `book_margin` | 44/20/-23.0c | 229/96/885.0c | 64 | 17.0c | 264 | 0/0 | 0/261 |
| `score_min60` | 44/20/-263.0c | 244/80/1187.0c | 64 | 183.0c | 275 | 2/2 | 0/260 |
| `book_p80_profit_frontier` | 6/3/-167.0c | 267/45/28.0c | 9 | 0.0c | 303 | 0/0 | 0/303 |
| `book_p80_ask90_frontier` | 5/2/-87.0c | 267/45/110.0c | 7 | 0.0c | 305 | 0/0 | 0/305 |

## Largest Common Deltas

| policy | market | registry | recompute | side | win | delta | reasons |
|---|---|---:|---:|---:|---:|---:|---|
| `score_min60` | `KXBTC15M-26MAY040415-15` | 86.0c/-87.0c | 74.0c/24.0c | no->yes | False->True | 111.0c | entry_dt,side,win,ask,net |
| `score_min60` | `KXBTC15M-26MAY032045-45` | 65.0c/-67.0c | 78.0c/20.0c | yes->no | False->True | 87.0c | entry_dt,side,win,ask,net |
| `score_min60` | `KXBTC15M-26MAY032230-30` | 66.0c/32.0c | 79.0c/19.0c | no->no | True->True | -13.0c | entry_dt,ask,net |
| `book_margin` | `KXBTC15M-26MAY032115-15` | 81.0c/17.0c | 69.0c/29.0c | no->no | True->True | 12.0c | entry_dt,ask,net |
| `score_min60` | `KXBTC15M-26MAY032115-15` | 81.0c/17.0c | 69.0c/29.0c | no->no | True->True | 12.0c | entry_dt,ask,net |
| `score_min60` | `KXBTC15M-26MAY041115-15` | 70.0c/28.0c | 79.0c/19.0c | no->no | True->True | -9.0c | entry_dt,ask,net |
| `score_min60` | `KXBTC15M-26MAY032200-00` | 77.0c/21.0c | 68.0c/30.0c | yes->yes | True->True | 9.0c | entry_dt,ask,net |
| `score_min60` | `KXBTC15M-26MAY032330-30` | 61.0c/37.0c | 69.0c/29.0c | no->no | True->True | -8.0c | entry_dt,ask,net |
| `score_min60` | `KXBTC15M-26MAY041000-00` | 63.0c/35.0c | 70.0c/28.0c | no->no | True->True | -7.0c | entry_dt,ask,net |
| `book_margin` | `KXBTC15M-26MAY040145-45` | 66.0c/-68.0c | 62.0c/-64.0c | no->no | False->False | 4.0c | entry_dt,ask,net |
| `score_min60` | `KXBTC15M-26MAY040130-30` | 62.0c/36.0c | 66.0c/32.0c | no->no | True->True | -4.0c | entry_dt,ask,net |
| `score_min60` | `KXBTC15M-26MAY040245-45` | 71.0c/27.0c | 75.0c/23.0c | yes->yes | True->True | -4.0c | entry_dt,ask,net |
| `score_min60` | `KXBTC15M-26MAY031845-45` | 86.0c/13.0c | 81.0c/17.0c | yes->yes | True->True | 4.0c | entry_dt,ask,net |
| `score_min60` | `KXBTC15M-26MAY031945-45` | 66.0c/-68.0c | 63.0c/-65.0c | yes->yes | False->False | 3.0c | entry_dt,ask,net |
| `score_min60` | `KXBTC15M-26MAY040145-45` | 69.0c/-71.0c | 66.0c/-68.0c | no->no | False->False | 3.0c | entry_dt,ask,net |
| `book_margin` | `KXBTC15M-26MAY040600-00` | 62.0c/36.0c | 61.0c/37.0c | no->no | True->True | 1.0c | entry_dt,ask,net |
| `score_min60` | `KXBTC15M-26MAY040945-45` | 63.0c/-65.0c | 64.0c/-66.0c | yes->yes | False->False | -1.0c | entry_dt,ask,net |
| `score_min60` | `KXBTC15M-26MAY032130-30` | 73.0c/25.0c | 73.0c/25.0c | yes->yes | True->True | 0.0c | entry_dt |

## Read

- Treat recomputed frontier wins as hypothesis generation unless the same policy has matching pre-resolution registry evidence.
- Large common-market deltas indicate timing/physics-state availability, not just sample-size noise.
