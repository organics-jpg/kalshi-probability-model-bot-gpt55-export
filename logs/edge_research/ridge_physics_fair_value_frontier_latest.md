# Ridge Physics Fair-Value Frontier

Generated UTC: `20260504_124446Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Fits one ridge-logistic fair-value model using only train-split side rows from current+v21.
- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.

## Diagnostics

- Current markets: 313
- V21 markets: 221
- Candidate policies: 226
- Strict pass rows: 0
- Train rows/markets: 25450/319
- Train logloss/Brier: 0.4456/0.1495

## Model Coefficients

- `intercept`: 0.0048
- `logit_book`: 1.3266
- `logit_brownian15`: 0.7206
- `logit_drift5`: 0.1522
- `margin_sigma`: 0.7154
- `long_path_z`: -0.1296

## Top Rows

| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | median ask current/v21 | min block+ | worst block |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ridge_physics_fv; p>=0.6; fee_edge>=-2c; ask<=98; sec>=120` | False | 1433.0c | 948.0c | 88.89% | 462.0c/971.0c | 69.74%/73.53% | 65.0c/64.5c | 0.6875 | -318.0c |
| `ridge_physics_fv; p>=0.6; fee_edge>=-2c; ask<=95; sec>=120` | False | 1428.0c | 947.0c | 86.67% | 463.0c/965.0c | 69.64%/73.00% | 65.0c/64.0c | 0.6875 | -318.0c |
| `ridge_physics_fv; p>=0.6; fee_edge>=-2c; ask<=90; sec>=120` | False | 1499.0c | 935.0c | 86.67% | 454.0c/1045.0c | 69.33%/72.96% | 65.0c/64.0c | 0.6875 | -318.0c |
| `ridge_physics_fv; p>=0.6; fee_edge>=-2c; ask<=98; sec>=300` | False | 1310.0c | 896.0c | 86.67% | 409.0c/901.0c | 69.44%/73.00% | 65.0c/64.0c | 0.6875 | -318.0c |
| `ridge_physics_fv; p>=0.6; fee_edge>=-2c; ask<=95; sec>=300` | False | 1306.0c | 895.0c | 84.44% | 411.0c/895.0c | 69.44%/72.45% | 65.0c/64.0c | 0.6875 | -318.0c |
| `ridge_physics_fv; p>=0.6; fee_edge>=-2c; ask<=90; sec>=300` | False | 1381.0c | 887.0c | 84.44% | 402.0c/979.0c | 69.13%/72.54% | 65.0c/64.0c | 0.6875 | -318.0c |
| `choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0` | False | 1474.0c | 844.0c | 97.78% | 1049.0c/425.0c | 71.06%/71.23% | 64.0c/66.0c | 0.6250 | -332.0c |
| `ridge_physics_fv; p>=0.575; fee_edge>=-2c; ask<=98; sec>=120` | False | 812.0c | -154.0c | 88.89% | -205.0c/1017.0c | 65.57%/71.09% | 62.0c/61.0c | 0.6875 | -559.0c |
| `ridge_physics_fv; p>=0.575; fee_edge>=-2c; ask<=95; sec>=120` | False | 807.0c | -155.0c | 86.67% | -204.0c/1011.0c | 65.46%/70.53% | 62.0c/61.0c | 0.6875 | -559.0c |
| `ridge_physics_fv; p>=0.575; fee_edge>=-2c; ask<=90; sec>=120` | False | 878.0c | -167.0c | 86.67% | -213.0c/1091.0c | 65.12%/70.44% | 62.0c/61.0c | 0.6875 | -559.0c |
| `ridge_physics_fv; p>=0.575; fee_edge>=-2c; ask<=98; sec>=300` | False | 788.0c | -206.0c | 86.67% | -199.0c/987.0c | 65.45%/70.87% | 62.0c/61.0c | 0.6875 | -559.0c |
| `ridge_physics_fv; p>=0.575; fee_edge>=-2c; ask<=95; sec>=300` | False | 784.0c | -207.0c | 84.44% | -197.0c/981.0c | 65.45%/70.30% | 62.0c/61.0c | 0.6875 | -559.0c |
| `ridge_physics_fv; p>=0.575; fee_edge>=-2c; ask<=90; sec>=300` | False | 859.0c | -215.0c | 84.44% | -206.0c/1065.0c | 65.10%/70.35% | 62.0c/61.0c | 0.6875 | -559.0c |
| `ridge_physics_fv; p>=0.55; fee_edge>=-2c; ask<=98; sec>=300` | False | 76.0c | -281.0c | 93.33% | -1099.0c/1175.0c | 60.26%/68.69% | 60.0c/60.0c | 0.5000 | -444.0c |
| `ridge_physics_fv; p>=0.55; fee_edge>=-2c; ask<=95; sec>=300` | False | 76.0c | -282.0c | 91.11% | -1097.0c/1173.0c | 60.26%/68.40% | 60.0c/60.0c | 0.5000 | -444.0c |
| `ridge_physics_fv; p>=0.55; fee_edge>=-2c; ask<=90; sec>=300` | False | 155.0c | -286.0c | 91.11% | -1102.0c/1257.0c | 60.00%/68.42% | 60.0c/59.0c | 0.5000 | -444.0c |
| `ridge_physics_fv; p>=0.525; fee_edge>=-2c; ask<=98; sec>=300` | False | 135.0c | -293.0c | 97.73% | -1040.0c/1175.0c | 58.20%/66.36% | 57.0c/57.0c | 0.5000 | -489.0c |
| `ridge_physics_fv; p>=0.55; fee_edge>=-2c; ask<=98; sec>=120` | False | 90.0c | -293.0c | 95.56% | -1028.0c/1118.0c | 60.52%/68.37% | 60.0c/60.0c | 0.5000 | -444.0c |
| `ridge_physics_fv; p>=0.525; fee_edge>=-2c; ask<=98; sec>=120` | False | 82.0c | -293.0c | 97.78% | -1040.0c/1122.0c | 58.20%/66.06% | 57.0c/57.0c | 0.5000 | -489.0c |
| `ridge_physics_fv; p>=0.525; fee_edge>=-2c; ask<=95; sec>=300` | False | 136.0c | -294.0c | 95.56% | -1038.0c/1174.0c | 58.20%/66.20% | 57.0c/57.0c | 0.5000 | -489.0c |
| `ridge_physics_fv; p>=0.55; fee_edge>=-2c; ask<=95; sec>=120` | False | 90.0c | -294.0c | 93.33% | -1026.0c/1116.0c | 60.52%/68.08% | 60.0c/60.0c | 0.5000 | -444.0c |
| `ridge_physics_fv; p>=0.525; fee_edge>=-2c; ask<=95; sec>=120` | False | 83.0c | -294.0c | 95.56% | -1038.0c/1121.0c | 58.20%/65.90% | 57.0c/57.0c | 0.5000 | -489.0c |
| `ridge_physics_fv; p>=0.525; fee_edge>=-2c; ask<=90; sec>=300` | False | 215.0c | -298.0c | 95.45% | -1043.0c/1258.0c | 57.93%/66.20% | 57.0c/57.0c | 0.5000 | -489.0c |
| `ridge_physics_fv; p>=0.55; fee_edge>=-2c; ask<=90; sec>=120` | False | 169.0c | -298.0c | 93.33% | -1031.0c/1200.0c | 60.26%/68.10% | 60.0c/59.0c | 0.5000 | -444.0c |
| `ridge_physics_fv; p>=0.525; fee_edge>=-2c; ask<=90; sec>=120` | False | 162.0c | -298.0c | 95.56% | -1043.0c/1205.0c | 57.93%/65.89% | 57.0c/56.5c | 0.5000 | -489.0c |
| `ridge_physics_fv; p>=0.55; fee_edge>=-2c; ask<=95; sec>=600` | False | 142.0c | -334.0c | 84.44% | -997.0c/1139.0c | 60.07%/68.37% | 60.0c/59.5c | 0.5000 | -444.0c |
| `ridge_physics_fv; p>=0.55; fee_edge>=-2c; ask<=98; sec>=600` | False | 142.0c | -334.0c | 84.44% | -997.0c/1139.0c | 60.07%/68.37% | 60.0c/59.5c | 0.5000 | -444.0c |
| `ridge_physics_fv; p>=0.55; fee_edge>=-2c; ask<=90; sec>=600` | False | 121.0c | -338.0c | 84.44% | -1006.0c/1127.0c | 59.79%/68.04% | 60.0c/59.0c | 0.5000 | -444.0c |
| `ridge_physics_fv; p>=0.525; fee_edge>=-2c; ask<=95; sec>=600` | False | 221.0c | -339.0c | 88.89% | -898.0c/1119.0c | 58.22%/65.70% | 57.0c/56.0c | 0.5000 | -489.0c |
| `ridge_physics_fv; p>=0.525; fee_edge>=-2c; ask<=98; sec>=600` | False | 221.0c | -339.0c | 88.89% | -898.0c/1119.0c | 58.22%/65.70% | 57.0c/56.0c | 0.5000 | -489.0c |

## Read

- No ridge-calibrated fair-value policy clears the strict gate.
