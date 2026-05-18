# Path-Flip Switch-Cost Check

Generated UTC: `20260503_200704Z`

## Scope

- Research-only check; no orders are submitted and no bot files or live processes are touched.
- Charges an early v2 entry, exit at contemporaneous bid, and late opposite-side entry when an override appears.
- This is closer to tradable managed P&L than the replacement-only flip diagnostic.

## Baseline

- Current v2 held-to-settlement baseline: 279.0c
- V21 v2 held-to-settlement baseline: 1283.0c

## Summary

- Policies scanned: 16
- Both-dataset 80% coverage policies: 16
- Both-dataset switch-cost OOS-positive policies: 0

## Top Rows

| rank | policy | switch delta current/v21 | overrides current/v21 | switch net current/v21 | OOS ROI floor |
|---:|---|---:|---:|---:|---:|
| 1 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=660; ask_worse<=30c` | -716.0c/-1086.0c | 73/47 | -437.0c/197.0c | -11.72% |
| 2 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=660; ask_worse<=none` | -750.0c/-1262.0c | 74/53 | -471.0c/21.0c | -10.93% |
| 3 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=600; ask_worse<=30c` | -990.0c/-1350.0c | 63/42 | -711.0c/-67.0c | -10.82% |
| 4 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=30c` | -718.0c/-1836.0c | 80/63 | -439.0c/-553.0c | -10.94% |
| 5 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=600; ask_worse<=none` | -1056.0c/-1600.0c | 63/46 | -777.0c/-317.0c | -10.82% |
| 6 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=600; ask_worse<=30c` | -888.0c/-1878.0c | 72/59 | -609.0c/-595.0c | -9.60% |
| 7 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=none` | -654.0c/-2346.0c | 92/80 | -375.0c/-1063.0c | -11.45% |
| 8 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=600; ask_worse<=none` | -738.0c/-2378.0c | 88/77 | -459.0c/-1095.0c | -8.87% |
| 9 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=80; delay>=60s; sec_to_close<=600; ask_worse<=30c` | -1416.0c/-2276.0c | 85/66 | -1137.0c/-993.0c | -7.15% |
| 10 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=80; delay>=60s; sec_to_close<=660; ask_worse<=30c` | -1566.0c/-2144.0c | 96/72 | -1287.0c/-861.0c | -7.73% |
| 11 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=80; delay>=60s; sec_to_close<=600; ask_worse<=none` | -1482.0c/-2484.0c | 85/71 | -1203.0c/-1201.0c | -7.15% |
| 12 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=80; delay>=60s; sec_to_close<=660; ask_worse<=none` | -1600.0c/-2480.0c | 97/79 | -1321.0c/-1197.0c | -7.03% |
| 13 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=90; delay>=60s; sec_to_close<=600; ask_worse<=30c` | -1400.0c/-3070.0c | 91/76 | -1121.0c/-1787.0c | -6.38% |
| 14 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=90; delay>=60s; sec_to_close<=600; ask_worse<=none` | -1250.0c/-3444.0c | 105/92 | -971.0c/-2161.0c | -12.29% |
| 15 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=30c` | -1622.0c/-3128.0c | 101/82 | -1343.0c/-1845.0c | -7.13% |
| 16 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=none` | -1580.0c/-3688.0c | 111/98 | -1301.0c/-2405.0c | -12.63% |

## 14:30 UTC Split Case

| policy | final side | ask | final net | switch net | override |
|---|---|---:|---:|---:|---|
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=660; ask_worse<=30c` | no | 77.0c | 21.0c | -18.0c | True |
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=660; ask_worse<=none` | no | 77.0c | 21.0c | -18.0c | True |
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=600; ask_worse<=30c` | yes | 58.0c | -60.0c | -60.0c | False |
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=30c` | no | 82.0c | 16.0c | -28.0c | True |
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=600; ask_worse<=none` | yes | 58.0c | -60.0c | -60.0c | False |
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=600; ask_worse<=30c` | yes | 58.0c | -60.0c | -60.0c | False |
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=none` | no | 82.0c | 16.0c | -28.0c | True |
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=600; ask_worse<=none` | yes | 58.0c | -60.0c | -60.0c | False |

## Read

- Best switch-cost row: `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=660; ask_worse<=30c` with current/v21 delta -716.0c/-1086.0c.
- Switch costs break the apparent edge; do not lock the flip override.
