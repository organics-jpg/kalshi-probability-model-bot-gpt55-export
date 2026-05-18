# V2 Tradeable Veto Scan

Generated UTC: `20260503_222034Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Tests one-feature abstention rules on top of v2 while preserving >=80% coverage.
- This is diagnostic; any winner needs a forward lock and strict pre-resolution validation.

## Baseline

- Current v2 baseline: 291.0c
- V21 v2 baseline: 1283.0c

## Summary

- Rules scanned: 75
- Both-dataset 80% coverage rules: 26
- Both-dataset OOS-positive rules: 0

## Top Rows

| rank | rule | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |
|---:|---|---:|---:|---:|---:|
| 1 | `adverse_move_15m<=75` | 277.0c/211.0c | 568.0c/64.04%/87.69% | 1494.0c/70.00%/85.97% | -17.30% |
| 2 | `adverse_move_15m<=100` | 132.0c/121.0c | 423.0c/63.56%/95.00% | 1404.0c/68.93%/93.21% | -19.25% |
| 3 | `none>=0` | 0.0c/0.0c | 291.0c/63.18%/99.23% | 1283.0c/68.04%/99.10% | -14.00% |
| 4 | `seconds_to_close>=240` | 0.0c/0.0c | 291.0c/63.18%/99.23% | 1283.0c/68.04%/99.10% | -14.00% |
| 5 | `seconds_to_close>=300` | 0.0c/0.0c | 291.0c/63.18%/99.23% | 1283.0c/68.04%/99.10% | -14.00% |
| 6 | `brownian_p_rv_15m>=0.55` | 0.0c/0.0c | 291.0c/63.18%/99.23% | 1283.0c/68.04%/99.10% | -14.00% |
| 7 | `touch_loss_rv_15m<=1` | 0.0c/0.0c | 291.0c/63.18%/99.23% | 1283.0c/68.04%/99.10% | -14.00% |
| 8 | `touch_loss_rv_15m<=1.25` | 0.0c/0.0c | 291.0c/63.18%/99.23% | 1283.0c/68.04%/99.10% | -14.00% |
| 9 | `spread_cents<=4` | 0.0c/0.0c | 291.0c/63.18%/99.23% | 1283.0c/68.04%/99.10% | -14.00% |
| 10 | `spread_cents<=5` | 0.0c/0.0c | 291.0c/63.18%/99.23% | 1283.0c/68.04%/99.10% | -14.00% |
| 11 | `ask_cents<=90` | 0.0c/-7.0c | 291.0c/63.18%/99.23% | 1276.0c/67.89%/98.64% | -14.00% |
| 12 | `ask_cents<=85` | 0.0c/-17.0c | 291.0c/63.18%/99.23% | 1266.0c/67.74%/98.19% | -14.00% |
| 13 | `spread_cents<=3` | 0.0c/-42.0c | 291.0c/63.18%/99.23% | 1241.0c/67.89%/98.64% | -14.00% |
| 14 | `ask_cents<=80` | 36.0c/-79.0c | 327.0c/62.99%/97.69% | 1204.0c/67.14%/96.38% | -14.91% |
| 15 | `ask_cents<=75` | -49.0c/6.0c | 242.0c/62.04%/94.23% | 1289.0c/67.15%/93.67% | -17.08% |
| 16 | `seconds_to_close>=360` | -28.0c/-27.0c | 263.0c/63.04%/98.85% | 1256.0c/67.89%/98.64% | -14.00% |
| 17 | `ask_cents<=70` | -111.0c/-53.0c | 180.0c/61.04%/88.85% | 1230.0c/66.32%/87.33% | -16.35% |
| 18 | `seconds_to_close>=420` | -113.0c/-63.0c | 178.0c/62.75%/98.08% | 1220.0c/67.74%/98.19% | -14.00% |
| 19 | `seconds_to_close>=480` | -113.0c/-63.0c | 178.0c/62.75%/98.08% | 1220.0c/67.74%/98.19% | -14.00% |
| 20 | `seconds_to_close>=540` | -113.0c/-63.0c | 178.0c/62.75%/98.08% | 1220.0c/67.74%/98.19% | -14.00% |

## Read

- Best veto row: `adverse_move_15m<=75` with current/v21 delta 277.0c/211.0c.
- No veto improves v2 robustly enough to lock.
