# arXiv Priority Tests

Research-only priority tests from the latest Truffle synthesis. These are retrospective diagnostics over recorded v28 data, not live-trading changes.

- Generated UTC: `2026-05-08T02:16:29.977386+00:00`
- Matched trades: `619`

## Probability Calibration

| model | window | rows | Brier | log loss |
|---|---|---:|---:|---:|
| raw_v28 | all | 618 | 0.1846 | 0.5838 |
| raw_v28 | first_400 | 400 | 0.1961 | 0.6205 |
| raw_v28 | rows_201_400 | 200 | 0.2087 | 0.6576 |
| raw_v28 | rows_401_600 | 199 | 0.1776 | 0.5538 |
| raw_v28 | last_232 | 218 | 0.1634 | 0.5164 |
| brownian_terminal | all | 618 | 0.1738 | 0.5336 |
| brownian_terminal | first_400 | 400 | 0.1846 | 0.5613 |
| brownian_terminal | rows_201_400 | 200 | 0.1979 | 0.5955 |
| brownian_terminal | rows_401_600 | 199 | 0.1658 | 0.5113 |
| brownian_terminal | last_232 | 218 | 0.1540 | 0.4829 |
| fixed_iso_train200_apply201_600 | rows_201_400 | 200 | 0.1954 | 0.6929 |
| fixed_iso_train200_apply201_600 | rows_201_600 | 399 | 0.1806 | 0.6015 |
| fixed_iso_train200_apply201_600 | rows_401_600 | 199 | 0.1657 | 0.5097 |
| rolling_iso_w30 | first_400 | 370 | 0.2165 | 1.0851 |
| rolling_iso_w50 | first_400 | 350 | 0.2003 | 0.7785 |
| rolling_iso_w80 | first_400 | 320 | 0.2075 | 0.7798 |
| rolling_iso_w120 | first_400 | 280 | 0.1988 | 0.6690 |
| aci_bias_eta_0p01 | first_400 | 400 | 0.1830 | 0.5559 |
| aci_bias_eta_0p03 | first_400 | 400 | 0.1823 | 0.5556 |
| aci_bias_eta_0p05 | first_400 | 400 | 0.1826 | 0.5641 |
| aci_bias_eta_0p08 | first_400 | 400 | 0.1819 | 0.6141 |

- Best first-400 calibration candidate: `aci_bias_eta_0p08`.
- Promotion gate Brier < `0.165` and log loss < `0.50`: `False`.

## ACI Coverage

| model | eta | coverage | first-400 coverage | all Brier | passes ACI gate |
|---|---:|---:|---:|---:|---|
| aci_bias_eta_0p01 | 0.01 | 85.9% | 83.2% | 0.1744 | True |
| aci_bias_eta_0p03 | 0.03 | 89.2% | 87.8% | 0.1732 | True |
| aci_bias_eta_0p05 | 0.05 | 89.6% | 88.8% | 0.1727 | True |
| aci_bias_eta_0p08 | 0.08 | 90.0% | 89.2% | 0.1696 | True |

## E-Process

- Robust hybrid selected entries: `204`.
- First-200 selected entries: `67`.
- Last-100 selected entries: `39`.
- Pass gate: `False`.

| lambda | full max | first-200 max | last-100 max | last-100 cross |
|---:|---:|---:|---:|---|
| 0.02 | 1.25 | 1.07 | 1.05 | None |
| 0.05 | 1.73 | 1.18 | 1.12 | None |
| 0.1 | 2.85 | 1.37 | 1.24 | None |
| 0.2 | 6.83 | 1.80 | 1.45 | None |
| 0.35 | 18.31 | 2.52 | 1.67 | None |

## S-CRC Target Risk

- Baseline robust hybrid: `$22.77` from `204` rows, avg `11.2c`.

| score | accepted | W/L | PnL | avg/entry | accepted share | pass |
|---|---:|---:|---:|---:|---:|---|
| edge28_cents | 289 | 120/161 (+8 flat) | $-5.40 | -1.9c | 46.7% | False |
| depth_ratio | 254 | 103/147 (+4 flat) | $-6.76 | -2.7c | 41.0% | False |
| brownian_terminal_p_side | 235 | 99/131 (+5 flat) | $0.92 | 0.4c | 38.0% | True |
| absd_band_quality | 370 | 149/214 (+7 flat) | $-6.37 | -1.7c | 59.8% | False |
| hybrid_manual_score | 136 | 64/70 (+2 flat) | $16.69 | 12.3c | 22.0% | False |

## Fill Model

- Rows: `999`; train `799`; last-test `200`.
- Depth-only AUC: `0.612`.
- Extended logistic AUC: `0.549`; improvement `-0.063`.
- Precision at 50% recall: `72.0%`.
- Pass gate: `False`.

## Post-Fill Adverse Selection

- Rows with cached 5m BTC return: `0`.
- BTC cache range: `2026-03-14 00:55:00+00:00` to `2026-05-01 00:15:00+00:00`.
- Trade entry range: `2026-04-30 22:17:02` to `2026-05-07 13:11:41`.
- Median signed 5m return: `0.00` dollars.
- Depth vs signed 5m return Spearman: `0.000`.
- Ask vs signed 5m return Spearman: `0.000`.

## Shadow Registry

- Schema markdown: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_forward_shadow_registry_schema_latest.md`.
- Schema CSV: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_forward_shadow_registry_columns_latest.csv`.

## Read

- Probability calibration is the immediate lane only if it beats Brownian and clears the strict first-400 gate.
- The e-process is still the hardest promotion blocker because it asks for last-100 evidence without first-200 false discovery.
- The fill model is only promotable if it beats the depth-ratio baseline by more than 0.05 AUC on the chronological last 200 submits.
- The schema files are a forward-shadow registry blueprint, not a live-bot integration.
