# Path-Flip Override Frontier

Generated UTC: `20260503_195941Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Keeps v2 as the default high-coverage entry and tests later opposite-side overrides.
- Diagnostic only; a winner still needs a forward lock and strict pre-resolution validation.

## Baseline

- Current v2 baseline: 279.0c, 63.16% accuracy, 99.20% coverage.
- V21 v2 baseline: 1283.0c, 68.04% accuracy, 99.10% coverage.

## Summary

- Policies scanned: 16
- Both-dataset 80% coverage policies: 16
- Both-dataset OOS-positive policies: 16

## Top Rows

| rank | policy | delta current/v21 | overrides current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=none` | 2924.0c/698.0c | 92/80 | 3203.0c/82.59%/99.20% | 1981.0c/79.00%/99.10% | 8.59% |
| 2 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=600; ask_worse<=none` | 2786.0c/626.0c | 88/77 | 3065.0c/81.78%/99.20% | 1909.0c/78.54%/99.10% | 8.09% |
| 3 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=30c` | 2259.0c/626.0c | 80/63 | 2538.0c/77.73%/99.20% | 1909.0c/75.80%/99.10% | 6.84% |
| 4 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=90; delay>=60s; sec_to_close<=600; ask_worse<=none` | 2673.0c/-57.0c | 105/92 | 2952.0c/81.38%/99.20% | 1226.0c/75.34%/99.10% | 8.66% |
| 5 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=660; ask_worse<=none` | 1794.0c/577.0c | 74/53 | 2073.0c/75.30%/99.20% | 1860.0c/74.89%/99.10% | 5.39% |
| 6 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=660; ask_worse<=30c` | 1771.0c/585.0c | 73/47 | 2050.0c/74.90%/99.20% | 1868.0c/73.97%/99.10% | 3.89% |
| 7 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=600; ask_worse<=30c` | 1855.0c/477.0c | 72/59 | 2134.0c/75.30%/99.20% | 1760.0c/74.89%/99.10% | 8.81% |
| 8 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=none` | 2432.0c/-155.0c | 111/98 | 2711.0c/80.57%/99.20% | 1128.0c/75.34%/99.10% | 8.38% |
| 9 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=80; delay>=60s; sec_to_close<=660; ask_worse<=30c` | 1565.0c/322.0c | 96/72 | 1844.0c/74.49%/99.20% | 1605.0c/73.52%/99.10% | 9.63% |
| 10 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=30c` | 1891.0c/-136.0c | 101/82 | 2170.0c/76.52%/99.20% | 1147.0c/72.60%/99.10% | 10.66% |
| 11 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=80; delay>=60s; sec_to_close<=660; ask_worse<=none` | 1588.0c/164.0c | 97/79 | 1867.0c/74.90%/99.20% | 1447.0c/73.97%/99.10% | 11.05% |
| 12 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=90; delay>=60s; sec_to_close<=600; ask_worse<=30c` | 1855.0c/-262.0c | 91/76 | 2134.0c/75.71%/99.20% | 1021.0c/71.69%/99.10% | 11.86% |
| 13 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=80; delay>=60s; sec_to_close<=600; ask_worse<=30c` | 1436.0c/-1.0c | 85/66 | 1715.0c/73.28%/99.20% | 1282.0c/71.69%/99.10% | 11.90% |
| 14 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=600; ask_worse<=30c` | 1202.0c/168.0c | 63/42 | 1481.0c/71.66%/99.20% | 1451.0c/71.69%/99.10% | 4.88% |
| 15 | `base=v2; override=brownian_p_rv_15m>=0.65; ask<=80; delay>=60s; sec_to_close<=600; ask_worse<=none` | 1403.0c/-84.0c | 85/71 | 1682.0c/73.28%/99.20% | 1199.0c/72.15%/99.10% | 9.18% |
| 16 | `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=600; ask_worse<=none` | 1169.0c/25.0c | 63/46 | 1448.0c/71.66%/99.20% | 1308.0c/71.69%/99.10% | 4.88% |

## 14:30 UTC Split Case

| policy | selected side | entry | ask | outcome | win | net | override |
|---|---|---|---:|---|---|---:|---|
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=none` | no | `2026-05-03 14:19:05.141000+00:00` | 82.0c | no | True | 16.0c | True |
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=600; ask_worse<=none` | yes | `2026-05-03 14:16:04.928000+00:00` | 58.0c | no | False | -60.0c | False |
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=30c` | no | `2026-05-03 14:19:05.141000+00:00` | 82.0c | no | True | 16.0c | True |
| `base=v2; override=brownian_p_rv_15m>=0.65; ask<=90; delay>=60s; sec_to_close<=600; ask_worse<=none` | no | `2026-05-03 14:20:05.298000+00:00` | 78.0c | no | True | 20.0c | True |
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=660; ask_worse<=none` | no | `2026-05-03 14:19:50.279000+00:00` | 77.0c | no | True | 21.0c | True |
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=80; delay>=60s; sec_to_close<=660; ask_worse<=30c` | no | `2026-05-03 14:19:50.279000+00:00` | 77.0c | no | True | 21.0c | True |
| `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=600; ask_worse<=30c` | yes | `2026-05-03 14:16:04.928000+00:00` | 58.0c | no | False | -60.0c | False |
| `base=v2; override=brownian_p_rv_15m>=0.65; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=none` | no | `2026-05-03 14:19:05.141000+00:00` | 82.0c | no | True | 16.0c | True |

## Read

- Best diagnostic row: `base=v2; override=brownian_p_rv_15m>=0.70; ask<=90; delay>=60s; sec_to_close<=660; ask_worse<=none` with current/v21 delta 2924.0c/698.0c.
- Important: this scan is an upper-bound diagnostic, not yet a tradable lock. It keeps the early v2 selection when no flip appears, but replaces it with a later opposite-side row when a flip appears. A tradable version must model either waiting cost or exit-and-reverse cost before any forward lock.
