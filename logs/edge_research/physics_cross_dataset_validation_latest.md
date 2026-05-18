# Physics Cross-Dataset Validation

Generated UTC: `20260502_044936Z`

## Scope

- Fixed rules are taken from the `live_90_70` physics-prior scan; this script does not run a broad rule search.
- Independent validation excludes `live_90_70` from the pooled independent view.
- Only resolved settlement rows are included; exited-before-settlement rows are excluded.

## Coverage

- Feature rows: 829
- Contracts: 6604
- Metadata missing after load/fetch: 3
- coinbase_cache: C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\coinbase_btc_usd_1m_cache.parquet
- candle_rows: 62750
- candle_start: 2026-03-14T00:54:59.999000+00:00
- candle_end: 2026-04-26T14:48:59.999000+00:00

### Skips

| dataset | missing metadata | missing strike | missing close | missing spot | missing horizon |
|---|---:|---:|---:|---:|---:|
| live_90_70 | 0 | 1 | 0 | 0 | 0 |
| entry_90_stop_78 | 0 | 2 | 0 | 0 | 0 |
| live_90_78 | 0 | 0 | 0 | 0 | 0 |
| live_87_77_67 | 0 | 0 | 0 | 0 | 0 |
| live_90_truffle_exit_size2 | 0 | 0 | 0 | 0 | 0 |
| live_liquidity_dwell_size2 | 0 | 0 | 0 | 0 | 0 |

## Results

### `entry_90_stop_78`

Baseline: 160/160 contracts (100.00%), trades 80/80 (100.00%).

| rule | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.5` | 152 | 100.00% | 95.00% | 76 | 100.00% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.75` | 140 | 100.00% | 87.50% | 70 | 100.00% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>1.0` | 140 | 100.00% | 87.50% | 70 | 100.00% |
| `ask<=100; margin/rv30>=0.5` | 126 | 100.00% | 78.75% | 63 | 100.00% |
| `ask<=100; margin/rv60>=0.5` | 120 | 100.00% | 75.00% | 60 | 100.00% |
| `ask<=100; margin/rv15>=0.5` | 136 | 100.00% | 85.00% | 68 | 100.00% |
| `ask<=100; Phi(margin/rv15)>=0.7` | 132 | 100.00% | 82.50% | 66 | 100.00% |
| `ask<=100; Phi(margin/rv30)>=0.7` | 124 | 100.00% | 77.50% | 62 | 100.00% |

### `live_87_77_67`

Baseline: 91/141 contracts (64.54%), trades 7/9 (77.78%).

| rule | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.5` | 141 | 64.54% | 100.00% | 9 | 77.78% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.75` | 141 | 64.54% | 100.00% | 9 | 77.78% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>1.0` | 141 | 64.54% | 100.00% | 9 | 77.78% |
| `ask<=100; margin/rv30>=0.5` | 121 | 58.68% | 85.82% | 8 | 75.00% |
| `ask<=100; margin/rv60>=0.5` | 121 | 58.68% | 85.82% | 8 | 75.00% |
| `ask<=100; margin/rv15>=0.5` | 141 | 64.54% | 100.00% | 9 | 77.78% |
| `ask<=100; Phi(margin/rv15)>=0.7` | 141 | 64.54% | 100.00% | 9 | 77.78% |
| `ask<=100; Phi(margin/rv30)>=0.7` | 121 | 58.68% | 85.82% | 8 | 75.00% |

### `live_90_70`

Baseline: 4903/4983 contracts (98.39%), trades 501/509 (98.43%).

| rule | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.5` | 4682 | 98.29% | 93.96% | 478 | 98.33% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.75` | 4410 | 98.41% | 88.50% | 450 | 98.44% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>1.0` | 4290 | 98.37% | 86.09% | 438 | 98.40% |
| `ask<=100; margin/rv30>=0.5` | 4040 | 98.27% | 81.08% | 413 | 98.31% |
| `ask<=100; margin/rv60>=0.5` | 3880 | 98.20% | 77.86% | 397 | 98.24% |
| `ask<=100; margin/rv15>=0.5` | 4060 | 98.28% | 81.48% | 415 | 98.31% |
| `ask<=100; Phi(margin/rv15)>=0.7` | 3950 | 98.23% | 79.27% | 404 | 98.27% |
| `ask<=100; Phi(margin/rv30)>=0.7` | 3950 | 98.23% | 79.27% | 404 | 98.27% |

### `live_90_78`

Baseline: 1174/1174 contracts (100.00%), trades 163/163 (100.00%).

| rule | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.5` | 1092 | 100.00% | 93.02% | 150 | 100.00% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.75` | 1070 | 100.00% | 91.14% | 145 | 100.00% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>1.0` | 1025 | 100.00% | 87.31% | 142 | 100.00% |
| `ask<=100; margin/rv30>=0.5` | 896 | 100.00% | 76.32% | 119 | 100.00% |
| `ask<=100; margin/rv60>=0.5` | 863 | 100.00% | 73.51% | 114 | 100.00% |
| `ask<=100; margin/rv15>=0.5` | 936 | 100.00% | 79.73% | 126 | 100.00% |
| `ask<=100; Phi(margin/rv15)>=0.7` | 936 | 100.00% | 79.73% | 126 | 100.00% |
| `ask<=100; Phi(margin/rv30)>=0.7` | 876 | 100.00% | 74.62% | 115 | 100.00% |

### `live_90_truffle_exit_size2`

Baseline: 112/126 contracts (88.89%), trades 56/63 (88.89%).

| rule | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.5` | 112 | 89.29% | 88.89% | 56 | 89.29% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.75` | 104 | 88.46% | 82.54% | 52 | 88.46% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>1.0` | 104 | 88.46% | 82.54% | 52 | 88.46% |
| `ask<=100; margin/rv30>=0.5` | 86 | 90.70% | 68.25% | 43 | 90.70% |
| `ask<=100; margin/rv60>=0.5` | 86 | 88.37% | 68.25% | 43 | 88.37% |
| `ask<=100; margin/rv15>=0.5` | 94 | 89.36% | 74.60% | 47 | 89.36% |
| `ask<=100; Phi(margin/rv15)>=0.7` | 90 | 91.11% | 71.43% | 45 | 91.11% |
| `ask<=100; Phi(margin/rv30)>=0.7` | 84 | 90.48% | 66.67% | 42 | 90.48% |

### `live_liquidity_dwell_size2`

Baseline: 8/20 contracts (40.00%), trades 2/5 (40.00%).

| rule | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.5` | 20 | 40.00% | 100.00% | 5 | 40.00% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.75` | 20 | 40.00% | 100.00% | 5 | 40.00% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>1.0` | 20 | 40.00% | 100.00% | 5 | 40.00% |
| `ask<=100; margin/rv30>=0.5` | 12 | 33.33% | 60.00% | 3 | 33.33% |
| `ask<=100; margin/rv60>=0.5` | 12 | 33.33% | 60.00% | 3 | 33.33% |
| `ask<=100; margin/rv15>=0.5` | 16 | 25.00% | 80.00% | 4 | 25.00% |
| `ask<=100; Phi(margin/rv15)>=0.7` | 16 | 25.00% | 80.00% | 4 | 25.00% |
| `ask<=100; Phi(margin/rv30)>=0.7` | 12 | 33.33% | 60.00% | 3 | 33.33% |

### `pooled_independent_ex_live_90_70`

Baseline: 1545/1621 contracts (95.31%), trades 308/320 (96.25%).

| rule | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.5` | 1517 | 95.12% | 93.58% | 296 | 96.28% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.75` | 1475 | 94.98% | 90.99% | 281 | 96.09% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>1.0` | 1430 | 94.83% | 88.22% | 278 | 96.04% |
| `ask<=100; margin/rv30>=0.5` | 1241 | 94.68% | 76.56% | 236 | 96.61% |
| `ask<=100; margin/rv60>=0.5` | 1202 | 94.34% | 74.15% | 228 | 96.05% |
| `ask<=100; margin/rv15>=0.5` | 1323 | 94.56% | 81.62% | 254 | 96.06% |
| `ask<=100; Phi(margin/rv15)>=0.7` | 1315 | 94.68% | 81.12% | 250 | 96.40% |
| `ask<=100; Phi(margin/rv30)>=0.7` | 1217 | 94.58% | 75.08% | 230 | 96.52% |

### `pooled_all`

Baseline: 6448/6604 contracts (97.64%), trades 809/829 (97.59%).

| rule | contracts | contract acc | contract ret | trades | trade acc |
|---|---:|---:|---:|---:|---:|
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.5` | 6199 | 97.52% | 93.87% | 774 | 97.55% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>0.75` | 5885 | 97.55% | 89.11% | 731 | 97.54% |
| `ask<=100; block 15m adverse>10 unless v28 cushion>1.0` | 5720 | 97.48% | 86.61% | 716 | 97.49% |
| `ask<=100; margin/rv30>=0.5` | 5281 | 97.42% | 79.97% | 649 | 97.69% |
| `ask<=100; margin/rv60>=0.5` | 5082 | 97.28% | 76.95% | 625 | 97.44% |
| `ask<=100; margin/rv15>=0.5` | 5383 | 97.36% | 81.51% | 669 | 97.46% |
| `ask<=100; Phi(margin/rv15)>=0.7` | 5265 | 97.34% | 79.72% | 654 | 97.55% |
| `ask<=100; Phi(margin/rv30)>=0.7` | 5167 | 97.37% | 78.24% | 634 | 97.63% |

## Completion Read

The pooled independent set supports a fixed physics rule at the requested accuracy/volume/sample gates.
