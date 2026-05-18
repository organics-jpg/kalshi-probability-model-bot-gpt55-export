# Live v28 Physics Shadow Validator

Generated UTC: `20260502_134812Z`

## Rule

- `ask<=100; block 15m adverse>10 unless v28 cushion>0.5`
- Research-only shadow rule; no orders are submitted.
- Lock file: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\live_v28_physics_shadow_lock.json`
- Fresh evidence starts after source line `3222` / `2026-05-02T05:08:16.423429+00:00`.

## Coverage

- Total shadow rows: 127
- Resolved rows: 127
- Unresolved rows: 0
- Evaluable rows: 127
- Selected rows: 123

## Fresh After Lock

- Fresh rows: 6
- Fresh resolved rows: 6
- Fresh unresolved rows: 0
- Fresh selected rows: 4
- Fresh sample ready: False
- Fresh accuracy gate: True
- Fresh retention gate: False
- Fresh selected sample shortfall: 71 trades / 142 contracts

| fresh set | baseline contracts | baseline acc | shadow contracts | shadow acc | shadow retention |
|---|---:|---:|---:|---:|---:|
| after lock | 10/12 | 83.33% | 8/8 | 100.00% | 66.67% |

## Resolved Accuracy

| split | baseline contracts | baseline acc | shadow contracts | shadow acc | shadow retention |
|---|---:|---:|---:|---:|---:|
| all | 202/251 | 80.48% | 196/243 | 80.66% | 96.81% |
| train | 128/149 | 85.91% | 126/147 | 85.71% | 98.66% |
| validation | 42/50 | 84.00% | 42/50 | 84.00% | 100.00% |
| holdout | 32/52 | 61.54% | 28/46 | 60.87% | 88.46% |

## Completion Read

The shadow rule does not currently satisfy the observed accuracy/retention gate on resolved live v28 fills.
The fresh-after-lock sample does not yet satisfy the configured accuracy/retention/sample gates.

The current v28 resolved holdout is still the limiting evidence source; fresh fills are needed before promotion.
